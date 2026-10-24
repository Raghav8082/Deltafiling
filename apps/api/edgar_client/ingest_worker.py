import asyncio
import json
import time
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from config.database import AsyncSessionLocal
    from models.company import Company
    from models.filings import Filings
    from edgar_client.client import get_json, get_text
    from edgar_client.storage import save_text
except ModuleNotFoundError:
    from apps.api.config.database import AsyncSessionLocal
    from apps.api.models.company import Company
    from apps.api.models.filings import Filings
    from apps.api.edgar_client.client import get_json, get_text
    from apps.api.edgar_client.storage import save_text

_facts_cache = {}   # one XBRL download per company per run


async def claim_filing(session: AsyncSession) -> Filings | None:
    """Pick one 'detected' filing and mark it 'fetching' so no one else takes it."""
    stmt = (
        select(Filings)
        .where(Filings.status == "detected")
        .order_by(Filings.filing_date.desc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    res = await session.execute(stmt)
    filing = res.scalar_one_or_none()
    if filing:
        filing.status = "fetching"
        filing.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await session.commit()
    return filing


def filing_url(cik: str, accession: str, document: str) -> str:
    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{int(cik)}/{accession.replace('-', '')}/{document}"
    )


async def process(session: AsyncSession, filing: Filings):
    company = await session.get(Company, filing.company_id)
    if not company:
        raise ValueError(f"Company ID {filing.company_id} not found")

    # 1. Download HTML and XBRL facts
    html = get_text(
        filing_url(company.cik, filing.accession_number, filing.primary_document)
    )
    if company.cik not in _facts_cache:
        _facts_cache[company.cik] = get_json(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{company.cik}.json"
        )

    # 2. Save files locally
    html_path = save_text(
        f"filings/{company.cik}/{filing.accession_number}/{filing.primary_document}",
        html,
    )
    xbrl_path = save_text(
        f"facts/{company.cik}.json", json.dumps(_facts_cache[company.cik])
    )

    # 3. Update the database
    filing.raw_html_path = html_path
    filing.xbrl_path = xbrl_path
    filing.status = "fetched"
    filing.error = None
    filing.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()


async def run(limit: int | None = None):
    count = 0
    async with AsyncSessionLocal() as session:
        while True:
            filing = await claim_filing(session)
            if filing is None:
                print("No more detected filings.")
                break
            try:
                await process(session, filing)
                count += 1
                print(f"Fetched {filing.accession_number} ({filing.form_type})")
            except Exception as e:
                await session.rollback()
                filing.status = "failed"
                filing.error = str(e)[:500]
                filing.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                await session.commit()
                print(f"FAILED {filing.accession_number}: {e}")

            if limit and count >= limit:
                print(f"Reached batch limit of {limit} filings.")
                break


if __name__ == "__main__":
    asyncio.run(run())
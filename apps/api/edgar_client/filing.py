import asyncio
from datetime import date
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict

try:
    from config.database import AsyncSessionLocal
    from edgar_client.client import get_json
    from models.company import Company
    from models.filings import Filings
except ModuleNotFoundError:
    from apps.api.config.database import AsyncSessionLocal
    from apps.api.edgar_client.client import get_json
    from apps.api.models.company import Company
    from apps.api.models.filings import Filings



WANTED_FORMS = {"10-K", "10-Q"}
BASE = "https://data.sec.gov/submissions/"


def _rows_from_block(block: dict, company_id) -> list[dict]:
    rows = []
    for acc, form, fdate, rdate, doc in zip(
        block["accessionNumber"],
        block["form"],
        block["filingDate"],
        block["reportDate"],
        block["primaryDocument"],
    ):
        if form not in WANTED_FORMS:
            continue
        rows.append({
            "company_id": company_id,
            "accession_number": acc,
            "form_type": form,
            "filing_date": date.fromisoformat(fdate),
            "report_date": date.fromisoformat(rdate) if rdate else date.fromisoformat(fdate),
            "primary_document": doc,
            "status": "detected",
        })
    return rows


def _limit_per_form(rows: list[dict], n_10k: int, n_10q: int) -> list[dict]:
    limits = {"10-K": n_10k, "10-Q": n_10q}
    rows = sorted(rows, key=lambda r: r["filing_date"], reverse=True)
    counts = defaultdict(int)
    kept = []
    for r in rows:
        if counts[r["form_type"]] < limits[r["form_type"]]:
            kept.append(r)
            counts[r["form_type"]] += 1
    return kept

async def fetch_filings(session: AsyncSession, ticker: str, include_older: bool = False , n_10k=3, n_10q=4) -> int:
    res = await session.execute(
        select(Company).where(Company.ticker == ticker.upper())
    )
    company = res.scalar_one_or_none()
    if company is None:
        raise ValueError(f"Ticker {ticker} not found in companies table")

    data = get_json(f"{BASE}CIK{company.cik}.json")
    rows = _rows_from_block(data["filings"]["recent"], company.id)

    if include_older:
        for f in data["filings"].get("files", []):
            older = get_json(BASE + f["name"])
            rows += _rows_from_block(older, company.id)
            rows = _limit_per_form(rows, n_10k, n_10q)   

    if rows:
        stmt = insert(Filings).values(rows).on_conflict_do_nothing(
            index_elements=[Filings.accession_number]
        )
        await session.execute(stmt)
        await session.commit()
    return len(rows)


# --- TEST TRIGGER BLOCK ---
async def main():
    async with AsyncSessionLocal() as session:
        # Test with AAPL (already in DB)
        count = await fetch_filings(session, "MSFT")
        print(f"Successfully loaded {count} filings for MSFT")

        # Verify query from database
        res = await session.execute(
            select(Filings).limit(3)
        )
        filings = res.scalars().all()
        for f in filings:
            print(f"Stored Filing: {f.form_type} on {f.filing_date} (Accession: {f.accession_number})")

if __name__ == "__main__":
    asyncio.run(main())

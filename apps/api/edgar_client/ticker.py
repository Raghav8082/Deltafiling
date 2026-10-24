import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

try:
    from config.database import AsyncSessionLocal
    from edgar_client.client import get_json
    from models.company import Company
except ModuleNotFoundError:
    from apps.api.config.database import AsyncSessionLocal
    from apps.api.edgar_client.client import get_json
    from apps.api.models.company import Company

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

async def load_companies(session: AsyncSession, chunk_size: int = 1000) -> int:
    raw = get_json(TICKERS_URL)

   
    by_cik = {}
    for entry in raw.values():
        cik = str(entry["cik_str"]).zfill(10)
        by_cik.setdefault(cik, {
            "cik": cik,
            "ticker": entry["ticker"],
            "company_name": entry["title"],
        })
    rows = list(by_cik.values())

    # Insert in chunks; update the row if the CIK already exists
    for i in range(0, len(rows), chunk_size):
        stmt = insert(Company).values(rows[i:i + chunk_size])
        stmt = stmt.on_conflict_do_update(
            index_elements=[Company.cik],
            set_={"ticker": stmt.excluded.ticker, "company_name": stmt.excluded.company_name},
        )
        await session.execute(stmt)

    await session.commit()
    return len(rows)



# async def main():
#     async with AsyncSessionLocal() as session:
#         count = await load_companies(session)
#         print(f"{count} companies loaded")
#         res = await session.execute(select(Company).where(Company.ticker == "AAPL"))
#         apple = res.scalar_one()
#         print(f"Verified Apple: CIK={apple.cik}, Name={apple.company_name}")
# if __name__ == "__main__":
#     asyncio.run(main())
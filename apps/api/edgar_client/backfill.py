import asyncio
import argparse
from sqlalchemy import select, func

try:
    from config.database import AsyncSessionLocal
    from models.company import Company
    from edgar_client.ticker import load_companies
    from edgar_client.filing import fetch_filings
except ModuleNotFoundError:
    from apps.api.config.database import AsyncSessionLocal
    from apps.api.models.company import Company
    from apps.api.edgar_client.ticker import load_companies
    from apps.api.edgar_client.filing import fetch_filings


async def run_backfill(tickers: list[str]):
    async with AsyncSessionLocal() as session:
        # Step 2 runs only if the companies table is empty
        count = await session.scalar(select(func.count()).select_from(Company))
        if count == 0:
            print("Loading company list...")
            loaded = await load_companies(session)
            print(f"{loaded} companies loaded")

        for ticker in tickers:
            try:
                n = await fetch_filings(session, ticker)
                print(f"{ticker}: {n} filings found")
            except Exception as e:
                await session.rollback()
                print(f"{ticker}: FAILED ({e})")


def main():
    parser = argparse.ArgumentParser(description="Backfill recent filings")
    parser.add_argument("tickers", nargs="+", help="e.g. AAPL MSFT TSLA")
    args = parser.parse_args()

    asyncio.run(run_backfill(args.tickers))


if __name__ == "__main__":
    main()
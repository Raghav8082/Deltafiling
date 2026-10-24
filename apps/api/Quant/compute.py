from pathlib import Path

from .extraction import get_flow, get_flow_prior, get_instant, load_facts
from .math import (
    debt_to_equity,
    free_cash_flow,
    gross_margin,
    operating_margin,
    receivables_to_revenue,
    revenue_growth,
)


REVENUE = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
]
COST_OF_REVENUE = [
    "CostOfRevenue",
    "CostOfGoodsAndServicesSold",
    "CostOfGoodsSold",
    "CostOfServices",
]
OPERATING_INCOME = ["OperatingIncomeLoss"]
NET_INCOME       = ["NetIncomeLoss", "ProfitLoss"]
OP_CASH_FLOW     = ["NetCashProvidedByUsedInOperatingActivities"]
CAPEX            = ["PaymentsToAcquirePropertyPlantAndEquipment",
                    "PaymentsToAcquireProductiveAssets"]
RECEIVABLES      = ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"]
LONG_TERM_DEBT   = ["LongTermDebtNoncurrent", "LongTermDebt"]
SHORT_TERM_DEBT  = ["DebtCurrent", "LongTermDebtCurrent", "ShortTermBorrowings"]
EQUITY           = ["StockholdersEquity"]


def compute_annual(facts, accn, end):
    rev    = get_flow(facts, REVENUE, accn, end, 350, 380)
    prior  = get_flow_prior(facts, REVENUE, accn, end, 350, 380)
    cost   = get_flow(facts, COST_OF_REVENUE, accn, end, 350, 380)
    opinc  = get_flow(facts, OPERATING_INCOME, accn, end, 350, 380)
    ocf    = get_flow(facts, OP_CASH_FLOW, accn, end, 350, 380)
    capex  = get_flow(facts, CAPEX, accn, end, 350, 380)
    recv   = get_instant(facts, RECEIVABLES, accn, end)
    ltd    = get_instant(facts, LONG_TERM_DEBT, accn, end)
    std    = get_instant(facts, SHORT_TERM_DEBT, accn, end)
    equity = get_instant(facts, EQUITY, accn, end)

    v = lambda x: x["value"] if x else None
    total_debt = (v(ltd) or 0) + (v(std) or 0) if (ltd or std) else None

    return {
        "gross_margin": gross_margin(v(rev), v(cost)),
        "operating_margin": operating_margin(v(opinc), v(rev)),
        "revenue_growth": revenue_growth(v(rev), v(prior)),
        "free_cash_flow": free_cash_flow(v(ocf), v(capex)),
        "debt_to_equity": debt_to_equity(total_debt, v(equity)),
        "receivables_to_revenue": receivables_to_revenue(v(recv), v(rev)),
    }

if __name__ == "__main__":
    facts_path = Path(__file__).resolve().parents[1] / "data" / "facts" / "0000320193.json"
    facts = load_facts(facts_path)
    print(compute_annual(facts, "0000320193-23-000106", "2023-09-30"))
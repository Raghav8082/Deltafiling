def safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b

def gross_margin(revenue, cost):
    if revenue is None or cost is None:
        return None
    return safe_div(revenue - cost, revenue)

def operating_margin(op_income, revenue):
    return safe_div(op_income, revenue)

def revenue_growth(revenue, prior_revenue):
    if revenue is None or prior_revenue is None:
        return None
    return safe_div(revenue - prior_revenue, prior_revenue)

def free_cash_flow(op_cash_flow, capex):
    if op_cash_flow is None or capex is None:
        return None
    return op_cash_flow - capex

def debt_to_equity(total_debt, equity):
    return safe_div(total_debt, equity)

def receivables_to_revenue(receivables, revenue):
    return safe_div(receivables, revenue)
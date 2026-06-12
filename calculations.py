def calc_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard reducing balance EMI formula."""
    r = annual_rate / 100 / 12
    n = tenure_months
    if r == 0:
        return round(principal / n, 2)
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return round(emi, 2)


def calc_risk_score(credit_score: int, emi_ratio: float,
                    existing_loans: int, employment: str) -> int:
    """
    Returns approval probability 0–100.
    Weights: credit score 35, EMI ratio 30, existing loans 20, employment 15
    """
    score = 0

    # Credit score (35 pts)
    if credit_score >= 750:   score += 35
    elif credit_score >= 700: score += 25
    elif credit_score >= 650: score += 15
    else:                     score += 5

    # EMI/Income ratio (30 pts)
    if emi_ratio < 30:   score += 30
    elif emi_ratio < 40: score += 20
    elif emi_ratio < 50: score += 10
    else:                score += 0

    # Existing loans (20 pts)
    if existing_loans == 0:   score += 20
    elif existing_loans == 1: score += 12
    elif existing_loans == 2: score += 5
    else:                     score += 0

    # Employment type (15 pts)
    if employment in ["Government", "Salaried"]: score += 15
    else:                                         score += 8

    return min(score, 100)
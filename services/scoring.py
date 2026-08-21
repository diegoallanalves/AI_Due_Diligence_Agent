def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def growth_score(revenue_growth, customer_growth, retention):
    return round(clamp(clamp(revenue_growth*3)*0.35 + clamp(customer_growth*3)*0.25 + retention*0.40),1)

def financial_score(gross_margin, ebitda_margin, recurring_revenue):
    return round(clamp(gross_margin*0.35 + clamp(ebitda_margin*2.5)*0.35 + recurring_revenue*0.30),1)

def technology_score(data_quality, automation, cloud_maturity, ai_readiness):
    return round(clamp(data_quality*0.30 + automation*0.25 + cloud_maturity*0.20 + ai_readiness*0.25),1)

def risk_score(regulatory, concentration, security, operational):
    return round(clamp(regulatory*0.30 + concentration*0.20 + security*0.25 + operational*0.25),1)

def investment_score(growth, financial, technology, risk):
    return round(clamp(growth*0.30 + financial*0.30 + technology*0.25 + (100-risk)*0.15),1)

def verdict(score):
    if score >= 78: return "Strong opportunity", "Proceed to deeper diligence"
    if score >= 65: return "Attractive with conditions", "Proceed, but validate key risks"
    if score >= 52: return "Mixed case", "Investigate before proceeding"
    return "High concern", "Do not proceed without major improvements"

def identify_opportunities(manual_ops, support_cost, data_quality, automation, complaints, revenue, ebitda_margin):
    out=[]
    if manual_ops>=55:
        out.append({"name":"Operations automation","impact":"High","reason":"A large share of operational work remains manual.","pilot":"AI-assisted exception triage with human approval."})
    if complaints>=5000 or support_cost>=3_000_000:
        out.append({"name":"Customer service AI","impact":"High","reason":"Customer-service volume/cost indicates a potential automation opportunity.","pilot":"AI support assistant with controlled escalation to human agents."})
    if data_quality>=75 and automation<65:
        out.append({"name":"AI-enabled workflow layer","impact":"Medium","reason":"Data is usable, but workflow automation maturity is still limited.","pilot":"Connect trusted enterprise data to AI-assisted workflows."})
    if ebitda_margin<20:
        out.append({"name":"Margin improvement","impact":"High","reason":"EBITDA margin suggests operational efficiency could materially affect value.","pilot":"Target high-cost repetitive workflows first and measure cost-to-serve reduction."})
    if revenue>=100_000_000 and data_quality>=80:
        out.append({"name":"AI product / data monetisation","impact":"Medium","reason":"Scale and data quality may support new AI-enabled customer products.","pilot":"Test one premium AI insight or decision-support product."})
    if not out:
        out.append({"name":"Targeted process discovery","impact":"Low","reason":"Current data does not show an obvious large AI opportunity.","pilot":"Run process discovery before investing in AI."})
    return out

def estimate_value(manual_ops, annual_operating_cost, automation_potential):
    addressable=annual_operating_cost*(manual_ops/100)
    theoretical=addressable*(automation_potential/100)
    return {"Addressable cost":addressable,"Conservative":theoretical*0.35,"Base":theoretical*0.55,"Aggressive":theoretical*0.75}

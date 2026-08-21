import json, os
from dotenv import load_dotenv
load_dotenv()

def local_summary(company, scores, risks, opportunities, value):
    inv=scores["Investment"]; risk=scores["Risk"]
    if inv>=78 and risk<60: rec="Proceed to deeper diligence."
    elif inv>=65: rec="Proceed with conditions and validate the highest risks."
    elif inv>=52: rec="Keep investigating before making an investment decision."
    else: rec="Do not proceed unless major risks or performance issues improve."
    biggest=max(risks,key=risks.get); top=opportunities[0]
    return {
      "recommendation":rec,
      "investment_view":f"{company} scores {inv}/100 on the current diligence model with an overall risk score of {risk}/100.",
      "biggest_risk":f"{biggest} is currently the largest diligence concern ({risks[biggest]}/100).",
      "ai_opportunity":f"{top['name']}: {top['reason']} Suggested pilot: {top['pilot']}",
      "value_creation":f"The Base scenario estimates approximately ${value['Base']:,.0f} of annual operational value if assumptions are validated.",
      "next_step":"Validate assumptions with management and operational data, test the highest-value opportunity in a controlled pilot, and update the investment case using measured results."
    }

def llm_summary(payload, fallback):
    key=os.getenv("OPENAI_API_KEY")
    if not key: return fallback, False
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        system="""You are an AI due-diligence and value-creation analyst for financial-services investments.
Use only supplied data. Do not invent facts. Treat scenarios as estimates, not forecasts.
Return strict JSON with keys: recommendation, investment_view, biggest_risk, ai_opportunity, value_creation, next_step."""
        r=client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),
            temperature=0.2,
            messages=[{"role":"system","content":system},{"role":"user","content":json.dumps(payload)}],
            response_format={"type":"json_object"}
        )
        return json.loads(r.choices[0].message.content), True
    except Exception:
        return fallback, False

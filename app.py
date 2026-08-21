import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from services.scoring import growth_score, financial_score, technology_score, risk_score, investment_score, verdict
from services.value_creation import identify_opportunities, estimate_value
from services.agent import local_summary, llm_summary

st.set_page_config(page_title="AI Due Diligence Agent", page_icon="◈", layout="wide")
st.title("AI Due Diligence & Value Creation Agent")
st.caption("Assess a financial-services company, surface risks, identify AI opportunities and build a value-creation thesis.")

with st.expander("How to use this app", expanded=True):
    st.markdown("""
**1. Choose a sample company** or use Custom.  
**2. Adjust the assumptions in the sidebar.**  
**3. Click `Run Due Diligence`.**  
**4. Review the investment score, risks, AI opportunities and value scenarios.**  
**5. Challenge the assumptions — these are scenarios, not forecasts.**
""")

sample_df=pd.read_csv("data/sample_companies.csv")
with st.sidebar:
    st.header("Company assumptions")
    sample=st.selectbox("Start from a sample company",["Custom"]+sample_df.company.tolist())
    if sample!="Custom":
        defaults=sample_df[sample_df.company==sample].iloc[0].to_dict()
    else:
        defaults={"company":"Example FinTech","sector":"Banking & Payments","revenue_m":125,"revenue_growth_pct":18,"customer_growth_pct":16,"retention_pct":92,"gross_margin_pct":61,"ebitda_margin_pct":14,"recurring_revenue_pct":83,"data_quality":79,"automation":42,"cloud_maturity":74,"ai_readiness":67,"manual_ops_pct":64,"annual_operating_cost_m":38,"annual_support_cost_m":5.1,"complaints":8100,"regulatory_risk":78,"customer_concentration_risk":55,"cybersecurity_risk":48,"operational_risk":68}
    company=st.text_input("Company",value=str(defaults["company"]))
    sector=st.selectbox("Sector",["Banking & Payments","Insurance","Wealth Management","Capital Markets","Financial Data","Fintech"])
    st.subheader("Growth")
    revenue_m=st.number_input("Annual revenue (USD millions)",1.0,5000.0,float(defaults["revenue_m"]))
    revenue_growth=st.slider("Revenue growth %",-20,60,int(defaults["revenue_growth_pct"]))
    customer_growth=st.slider("Customer growth %",-20,60,int(defaults["customer_growth_pct"]))
    retention=st.slider("Customer retention %",0,100,int(defaults["retention_pct"]))
    st.subheader("Financial quality")
    gross_margin=st.slider("Gross margin %",0,100,int(defaults["gross_margin_pct"]))
    ebitda_margin=st.slider("EBITDA margin %",-20,60,int(defaults["ebitda_margin_pct"]))
    recurring_revenue=st.slider("Recurring revenue %",0,100,int(defaults["recurring_revenue_pct"]))
    st.subheader("Technology & operations")
    data_quality=st.slider("Data quality",0,100,int(defaults["data_quality"]))
    automation=st.slider("Automation maturity",0,100,int(defaults["automation"]))
    cloud_maturity=st.slider("Cloud maturity",0,100,int(defaults["cloud_maturity"]))
    ai_readiness=st.slider("AI readiness",0,100,int(defaults["ai_readiness"]))
    manual_ops=st.slider("Manual operations %",0,100,int(defaults["manual_ops_pct"]))
    annual_operating_cost_m=st.number_input("Annual operating cost (USD millions)",0.1,1000.0,float(defaults["annual_operating_cost_m"]))
    annual_support_cost_m=st.number_input("Annual customer-support cost (USD millions)",0.0,500.0,float(defaults["annual_support_cost_m"]))
    complaints=st.number_input("Annual complaints",0,1_000_000,int(defaults["complaints"]),step=100)
    st.subheader("Risks")
    regulatory=st.slider("Regulatory risk",0,100,int(defaults["regulatory_risk"]))
    concentration=st.slider("Customer concentration risk",0,100,int(defaults["customer_concentration_risk"]))
    cybersecurity=st.slider("Cybersecurity risk",0,100,int(defaults["cybersecurity_risk"]))
    operational=st.slider("Operational risk",0,100,int(defaults["operational_risk"]))
    st.subheader("Value-creation assumption")
    automation_potential=st.slider("Potential reduction of addressable manual work %",0,80,35)

if st.button("Run Due Diligence",type="primary",use_container_width=True):
    growth=growth_score(revenue_growth,customer_growth,retention)
    financial=financial_score(gross_margin,ebitda_margin,recurring_revenue)
    technology=technology_score(data_quality,automation,cloud_maturity,ai_readiness)
    risk=risk_score(regulatory,concentration,cybersecurity,operational)
    invest=investment_score(growth,financial,technology,risk)
    label,action=verdict(invest)
    risks={"Regulatory risk":regulatory,"Customer concentration":concentration,"Cybersecurity":cybersecurity,"Operational risk":operational}
    opportunities=identify_opportunities(manual_ops,annual_support_cost_m*1_000_000,data_quality,automation,complaints,revenue_m*1_000_000,ebitda_margin)
    value=estimate_value(manual_ops,annual_operating_cost_m*1_000_000,automation_potential)
    scores={"Growth":growth,"Financial":financial,"Technology":technology,"Risk":risk,"Investment":invest}
    fallback=local_summary(company,scores,risks,opportunities,value)
    summary,used_llm=llm_summary({"company":company,"sector":sector,"scores":scores,"risks":risks,"opportunities":opportunities,"value_creation_scenarios":value},fallback)

    st.divider(); st.subheader("Investment snapshot")
    a,b,c,d=st.columns(4)
    a.metric("Investment score",f"{invest}/100"); b.metric("Risk score",f"{risk}/100"); c.metric("Revenue growth",f"{revenue_growth}%"); d.metric("EBITDA margin",f"{ebitda_margin}%")
    st.info(f"**{label}** — {action}")

    left,right=st.columns(2)
    with left:
        score_df=pd.DataFrame({"Dimension":["Growth","Financial","Technology","Risk-adjusted"],"Score":[growth,financial,technology,100-risk]})
        fig=px.bar(score_df,x="Dimension",y="Score",text="Score",range_y=[0,100],title="Due-diligence scorecard")
        fig.update_traces(textposition="outside"); st.plotly_chart(fig,use_container_width=True)
    with right:
        risk_df=pd.DataFrame({"Risk":list(risks.keys()),"Score":list(risks.values())})
        fig=px.bar(risk_df,x="Score",y="Risk",orientation="h",text="Score",range_x=[0,110],title="Risk heatmap")
        fig.update_traces(textposition="outside",cliponaxis=False); st.plotly_chart(fig,use_container_width=True)

    st.subheader("Growth vs risk position")
    position_df=sample_df.copy()
    position_df["Risk"]=position_df.apply(lambda r:risk_score(r["regulatory_risk"],r["customer_concentration_risk"],r["cybersecurity_risk"],r["operational_risk"]),axis=1)
    position_df["Investment"]=position_df.apply(lambda r:investment_score(growth_score(r["revenue_growth_pct"],r["customer_growth_pct"],r["retention_pct"]),financial_score(r["gross_margin_pct"],r["ebitda_margin_pct"],r["recurring_revenue_pct"]),technology_score(r["data_quality"],r["automation"],r["cloud_maturity"],r["ai_readiness"]),risk_score(r["regulatory_risk"],r["customer_concentration_risk"],r["cybersecurity_risk"],r["operational_risk"])),axis=1)
    current=pd.DataFrame([{"company":company,"revenue_growth_pct":revenue_growth,"Risk":risk,"Investment":invest,"revenue_m":revenue_m}])
    plot_df=pd.concat([position_df[["company","revenue_growth_pct","Risk","Investment","revenue_m"]],current],ignore_index=True)
    fig=px.scatter(plot_df,x="Risk",y="Investment",size="revenue_m",text="company",hover_name="company",title="Investment attractiveness vs risk",labels={"Risk":"Risk score (lower is better)","Investment":"Investment score"},size_max=55)
    fig.add_vline(x=60,line_dash="dash"); fig.add_hline(y=65,line_dash="dash"); fig.update_traces(textposition="top center"); st.plotly_chart(fig,use_container_width=True)

    st.subheader("AI value-creation opportunities")
    st.dataframe(pd.DataFrame(opportunities)[["name","impact","reason","pilot"]],use_container_width=True,hide_index=True)

    st.subheader("Operational value-creation scenarios")
    value_df=pd.DataFrame({"Scenario":["Conservative","Base","Aggressive"],"Annual value":[value["Conservative"],value["Base"],value["Aggressive"]]})
    c1,c2=st.columns(2)
    with c1:
        fig=px.bar(value_df,x="Scenario",y="Annual value",text_auto=".3s",title="Estimated annual operational value")
        fig.update_layout(yaxis_title="USD",xaxis_title=""); st.plotly_chart(fig,use_container_width=True)
    with c2:
        prof=pd.DataFrame({"Area":["Growth","Financial","Technology","Risk-adjusted"],"Score":[growth,financial,technology,100-risk]})
        fig=px.line(prof,x="Area",y="Score",markers=True,text="Score",title="Company profile")
        fig.update_traces(textposition="top center"); fig.update_yaxes(range=[0,100]); st.plotly_chart(fig,use_container_width=True)

    st.subheader("AI Due Diligence Agent")
    st.caption("LLM (Large Language Model) mode enabled" if used_llm else "Deterministic local analysis mode")
    st.markdown("### Recommendation"); st.write(summary["recommendation"])
    x,y=st.columns(2)
    with x:
        st.markdown("### Investment view"); st.write(summary["investment_view"])
        st.markdown("### Biggest risk"); st.write(summary["biggest_risk"])
        st.markdown("### AI opportunity"); st.write(summary["ai_opportunity"])
    with y:
        st.markdown("### Value creation"); st.write(summary["value_creation"])
        st.markdown("### Next diligence step"); st.write(summary["next_step"])

    st.subheader("Suggested diligence roadmap")
    roadmap=pd.DataFrame({"Stage":["1. Validate metrics","2. Test key risks","3. Process discovery","4. AI pilot","5. Investment thesis update"],"Question":["Are management KPIs and unit economics supported by source data?","Which risk could materially change the investment case?","Where is cost, friction or manual work actually created?","Can one narrow AI use case produce measurable value?","How do measured results change the value-creation plan?"]})
    st.dataframe(roadmap,use_container_width=True,hide_index=True)

st.divider()
st.caption("All companies, figures and outputs are synthetic scenario data. This prototype is for demonstration only and is not investment, legal or financial advice.")

import streamlit as st
import pandas as pd
import plotly.express as px
from db import fetch_all

st.markdown("## ⚠️ Risk Analysis")
st.caption("Delinquency watchlist and portfolio risk breakdown")
st.divider()

# ── Risk KPIs ────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("High Risk Loans",   "187",   delta="-3 from last week",  delta_color="inverse")
m2.metric("Medium Risk",       "642",   delta="+12 from last week", delta_color="inverse")
m3.metric("Low Risk",          "3,018", delta="+109 from last week")
m4.metric("Avg Credit Score",  "714",   delta="+12 pts this quarter")

st.divider()

# ── Delinquency table ────────────────────────────────────────
st.markdown("#### 🔴 Delinquency Watchlist")
st.caption("Loans overdue by more than 15 days with credit score below 650")

try:
    delinquent = fetch_all("""
        SELECT
            l.loan_id,
            b.full_name,
            l.outstanding_balance,
            DATEDIFF(CURDATE(), l.last_payment_date) AS overdue_days,
            b.credit_score,
            ROUND((l.outstanding_balance / b.annual_income) * 10, 1) AS risk_score
        FROM loans l
        JOIN loan_applications la ON l.application_id = la.application_id
        JOIN borrowers b ON la.borrower_id = b.borrower_id
        WHERE DATEDIFF(CURDATE(), l.last_payment_date) > 15
          AND b.credit_score < 650
        ORDER BY risk_score DESC
        LIMIT 20
    """)

    if delinquent:
        df = pd.DataFrame(delinquent)
        df["outstanding_balance"] = df["outstanding_balance"].apply(lambda x: f"₹{x:,.0f}")
        def action(score):
            if score >= 7: return "🔴 Escalate"
            if score >= 5: return "🟡 Follow Up"
            return "🟢 Monitor"
        df["Action"] = df["risk_score"].apply(action)
        df.rename(columns={
            "loan_id":             "Loan ID",
            "full_name":           "Borrower",
            "outstanding_balance": "Outstanding",
            "overdue_days":        "Overdue Days",
            "credit_score":        "Credit Score",
            "risk_score":          "Risk Score",
        }, inplace=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("No delinquent loans found.")

except Exception as e:
    st.info("DB not connected — showing sample data.")
    sample = {
        "Loan ID":     ["#LN-3891","#LN-3744","#LN-3621","#LN-3580"],
        "Borrower":    ["Manoj Verma","Pooja Gupta","Suresh Babu","Anita Desai"],
        "Outstanding": ["₹4,20,000","₹1,80,000","₹8,90,000","₹2,30,000"],
        "Overdue Days":[62, 31, 45, 18],
        "Credit Score":[548, 602, 571, 638],
        "Risk Score":  [8.9, 6.2, 7.8, 4.5],
        "Action":      ["🔴 Escalate","🟡 Follow Up","🔴 Escalate","🟢 Monitor"],
    }
    st.dataframe(pd.DataFrame(sample), use_container_width=True, hide_index=True)

st.divider()

# ── Risk distribution chart ──────────────────────────────────
st.markdown("#### Risk Distribution by Loan Type")

try:
    risk_data = fetch_all("""
        SELECT
            la.loan_purpose,
            SUM(CASE WHEN b.credit_score >= 700 THEN 1 ELSE 0 END) AS low_risk,
            SUM(CASE WHEN b.credit_score BETWEEN 600 AND 699 THEN 1 ELSE 0 END) AS medium_risk,
            SUM(CASE WHEN b.credit_score < 600 THEN 1 ELSE 0 END) AS high_risk
        FROM loan_applications la
        JOIN borrowers b ON la.borrower_id = b.borrower_id
        WHERE la.status = 'approved'
        GROUP BY la.loan_purpose
    """)
    if risk_data:
        df_risk = pd.DataFrame(risk_data)
        df_melt = df_risk.melt(id_vars="loan_purpose", var_name="Risk Level", value_name="Count")
        fig = px.bar(df_melt, x="loan_purpose", y="Count", color="Risk Level",
                     barmode="stack",
                     color_discrete_map={"low_risk":"#4ab86a","medium_risk":"#c9a227","high_risk":"#e05050"})
        fig.update_layout(plot_bgcolor="#111820", paper_bgcolor="#111820",
                          font_color="#8aa8c0", xaxis_title="", yaxis_title="Loans",
                          margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No approved loan data available.")
except:
    sample_risk = pd.DataFrame({
        "Loan Type":   ["Home","Personal","Vehicle","Education","Business"],
        "Low Risk":    [320, 180, 140, 95, 88],
        "Medium Risk": [85,  110, 60,  40, 45],
        "High Risk":   [20,  55,  18,  12, 22],
    })
    fig = px.bar(sample_risk.melt(id_vars="Loan Type", var_name="Risk", value_name="Count"),
                 x="Loan Type", y="Count", color="Risk", barmode="stack",
                 color_discrete_map={"Low Risk":"#4ab86a","Medium Risk":"#c9a227","High Risk":"#e05050"})
    fig.update_layout(plot_bgcolor="#111820", paper_bgcolor="#111820",
                      font_color="#8aa8c0", margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── SQL query showcase ───────────────────────────────────────
if st.session_state.role == "admin":
    st.markdown("#### 🛠️ Raw SQL — Delinquency Detection Query")
    st.code("""
SELECT
    l.loan_id,
    b.full_name,
    l.outstanding_balance,
    DATEDIFF(CURDATE(), l.last_payment_date) AS overdue_days,
    b.credit_score,
    ROUND((l.outstanding_balance / b.annual_income) * 10, 1) AS risk_score
FROM loans l
JOIN loan_applications la ON l.application_id = la.application_id
JOIN borrowers b ON la.borrower_id = b.borrower_id
WHERE DATEDIFF(CURDATE(), l.last_payment_date) > 15
  AND b.credit_score < 650
ORDER BY risk_score DESC;
    """, language="sql")
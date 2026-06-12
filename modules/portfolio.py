import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db import fetch_all

st.markdown("## 📊 Loan Portfolio")
st.caption("Portfolio-wide metrics and application history")
st.divider()

# ── KPI cards ───────────────────────────────────────────────
try:
    summary = fetch_all("""
        SELECT
            COUNT(*) AS total_apps,
            SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) AS approved,
            SUM(CASE WHEN status='rejected' THEN 1 ELSE 0 END) AS rejected,
            SUM(CASE WHEN status='review'   THEN 1 ELSE 0 END) AS review,
            SUM(CASE WHEN status='approved' THEN loan_amount ELSE 0 END) AS total_disbursed
        FROM loan_applications
    """)
    row = summary[0] if summary else {}
except:
    row = {}

total       = row.get("total_apps", 0)       or 0
approved    = row.get("approved", 0)          or 0
rejected    = row.get("rejected", 0)          or 0
review      = row.get("review", 0)            or 0
disbursed   = row.get("total_disbursed", 0)   or 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Applications", total)
m2.metric("Approved",  approved, delta=f"{round(approved/total*100,1)}% approval rate" if total else "0%")
m3.metric("Rejected",  rejected)
m4.metric(
    "Total Disbursed",
    f"₹{float(disbursed)/1e7:.2f}Cr" if disbursed else "₹0"
)
st.divider()

# ── Charts ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Disbursement by Loan Type")
    try:
        type_data = fetch_all("""
            SELECT loan_purpose, COUNT(*) as count, SUM(loan_amount) as total
            FROM loan_applications WHERE status='approved'
            GROUP BY loan_purpose
        """)
        if type_data:
            df_type = pd.DataFrame(type_data)
            fig = px.bar(df_type, x="loan_purpose", y="total",
                         color="loan_purpose",
                         color_discrete_sequence=["#c9a227","#378add","#1d9e75","#4ab86a","#8a6add"])
            fig.update_layout(
                plot_bgcolor="#111820", paper_bgcolor="#111820",
                font_color="#8aa8c0", showlegend=False,
                xaxis_title="", yaxis_title="Amount (₹)",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No approved loans yet.")
    except Exception as e:
        st.info("Showing sample data — connect DB to see live data.")
        df_sample = pd.DataFrame({
            "loan_purpose": ["Home Loan","Personal Loan","Vehicle Loan","Education Loan","Business Loan"],
            "total": [18400000, 8200000, 6700000, 4100000, 5200000]
        })
        fig = px.bar(df_sample, x="loan_purpose", y="total",
                     color="loan_purpose",
                     color_discrete_sequence=["#c9a227","#378add","#1d9e75","#4ab86a","#8a6add"])
        fig.update_layout(plot_bgcolor="#111820", paper_bgcolor="#111820",
                          font_color="#8aa8c0", showlegend=False,
                          margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Application Status Distribution")
    labels = ["Approved", "Rejected", "Review", "Pending"]
    values = [approved, rejected, review, max(0, total - approved - rejected - review)]
    fig2 = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.65,
        marker_colors=["#4ab86a", "#e05050", "#c9a227", "#378add"]
    )])
    fig2.update_layout(
        plot_bgcolor="#111820", paper_bgcolor="#111820",
        font_color="#8aa8c0", showlegend=True,
        legend=dict(font=dict(color="#8aa8c0")),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Applications table ───────────────────────────────────────
st.markdown("#### Recent Applications")

try:
    apps = fetch_all("""
        SELECT
            la.application_id,
            b.full_name,
            la.loan_amount,
            la.loan_purpose,
            b.credit_score,
            la.interest_rate,
            la.tenure_months,
            la.status,
            la.approval_probability,
            la.applied_at
        FROM loan_applications la
        JOIN borrowers b ON la.borrower_id = b.borrower_id
        ORDER BY la.applied_at DESC
        LIMIT 50
    """)
    if apps:
        df = pd.DataFrame(apps)
        df["loan_amount"] = df["loan_amount"].apply(lambda x: f"₹{x:,.0f}")
        df["approval_probability"] = df["approval_probability"].apply(lambda x: f"{x}%")
        df.rename(columns={
            "application_id":     "App ID",
            "full_name":          "Applicant",
            "loan_amount":        "Amount",
            "loan_purpose":       "Type",
            "credit_score":       "Credit Score",
            "interest_rate":      "Rate %",
            "tenure_months":      "Tenure",
            "status":             "Status",
            "approval_probability": "Probability",
            "applied_at":         "Applied On"
        }, inplace=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No applications in database yet.")
except Exception as e:
    st.info("DB not connected — showing sample data.")
    sample = {
        "App ID":      ["#LN-4421","#LN-4420","#LN-4419","#LN-4418"],
        "Applicant":   ["Ravi Kumar","Priya Sharma","Amit Patel","Sneha Rao"],
        "Amount":      ["₹8,50,000","₹2,00,000","₹15,00,000","₹5,50,000"],
        "Type":        ["Home Loan","Personal Loan","Business Loan","Vehicle Loan"],
        "Credit Score":[780, 610, 740, 695],
        "Status":      ["approved","rejected","review","approved"],
    }
    st.dataframe(pd.DataFrame(sample), use_container_width=True, hide_index=True)
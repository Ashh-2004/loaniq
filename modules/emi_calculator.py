import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from calculations import calc_emi

st.markdown("## 🧮 EMI Calculator")
st.caption("Calculate monthly instalments and generate amortization schedule")
st.divider()

col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown("#### Loan Parameters")
    principal     = st.number_input("Principal Amount (₹)", min_value=10000, max_value=10000000, value=500000, step=10000)
    annual_rate   = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=30.0, value=10.5, step=0.1)
    tenure_months = st.number_input("Tenure (months)", min_value=1, max_value=360, value=36)
    processing_fee_pct = st.number_input("Processing Fee (%)", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
    calculate = st.button("Calculate EMI", use_container_width=True)

with col2:
    emi           = calc_emi(principal, annual_rate, tenure_months)
    total_payment = round(emi * tenure_months)
    total_interest = total_payment - principal
    processing_fee = round(principal * processing_fee_pct / 100)
    total_cost    = total_payment + processing_fee

    st.markdown("#### Results")
    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly EMI",    f"₹{emi:,.0f}")
    m2.metric("Total Payment",  f"₹{total_cost:,.0f}")
    m3.metric("Total Interest", f"₹{total_interest:,.0f}")

    interest_pct  = round(total_interest / principal * 100, 1)
    principal_pct = round(100 - interest_pct, 1)

    st.markdown(f"**Principal: {principal_pct}% &nbsp;|&nbsp; Interest: {interest_pct}%**")
    st.progress(principal_pct / 100)

    # Donut chart
    fig = go.Figure(data=[go.Pie(
        labels=["Principal", "Interest", "Processing Fee"],
        values=[principal, total_interest, processing_fee],
        hole=0.60,
        marker_colors=["#c9a227", "#e08030", "#378add"]
    )])
    fig.update_layout(
        plot_bgcolor="#111820", paper_bgcolor="#111820",
        font_color="#8aa8c0", showlegend=True,
        legend=dict(font=dict(color="#8aa8c0")),
        margin=dict(l=10, r=10, t=10, b=10),
        height=220
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Amortization schedule ────────────────────────────────────
st.markdown("#### Amortization Schedule")

show_all = st.checkbox("Show full schedule", value=False)
r = annual_rate / 100 / 12
rows = []
balance = principal

for i in range(1, tenure_months + 1):
    interest_comp  = round(balance * r, 2)
    principal_comp = round(emi - interest_comp, 2)
    closing        = max(0, round(balance - principal_comp, 2))
    rows.append({
        "Month":           i,
        "Opening Balance": f"₹{balance:,.0f}",
        "EMI":             f"₹{emi:,.0f}",
        "Principal":       f"₹{principal_comp:,.0f}",
        "Interest":        f"₹{interest_comp:,.0f}",
        "Closing Balance": f"₹{closing:,.0f}",
    })
    balance = closing
    if balance <= 0:
        break

df = pd.DataFrame(rows)
display_df = df if show_all else df.head(12)
st.dataframe(display_df, use_container_width=True, hide_index=True)

if not show_all and tenure_months > 12:
    st.caption(f"Showing 12 of {tenure_months} months. Check 'Show full schedule' to see all.")

# ── Download ─────────────────────────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Schedule as CSV",
    data=csv,
    file_name="emi_schedule.csv",
    mime="text/csv",
    use_container_width=True
)
import streamlit as st
import pandas as pd
from db import fetch_all, execute
from calculations import calc_emi, calc_risk_score

st.markdown("## 📋 Loan Application")
st.caption("Submit and analyse a new loan application")
st.divider()

# ── Form ────────────────────────────────────────────────────
with st.form("loan_form"):
    st.markdown("#### Applicant Profile")
    col1, col2 = st.columns(2)
    with col1:
        name         = st.text_input("Full Name")
        loan_amount  = st.number_input("Loan Amount (₹)", min_value=10000, max_value=10000000, value=500000, step=10000)
        annual_income = st.number_input("Annual Income (₹)", min_value=100000, max_value=10000000, value=800000, step=10000)
        employment   = st.selectbox("Employment Type", ["Salaried", "Self-Employed", "Business", "Government"])

    with col2:
        purpose      = st.selectbox("Loan Purpose", ["Home Loan", "Personal Loan", "Education Loan", "Vehicle Loan", "Business Loan"])
        existing     = st.selectbox("Existing Loans", [0, 1, 2, 3])
        property_area = st.selectbox("Property Area", ["Urban", "Semi-Urban", "Rural"])
        email        = st.text_input("Email (optional)")

    st.markdown("#### Loan Parameters")
    col3, col4 = st.columns(2)
    with col3:
        credit_score = st.slider("Credit Score", 300, 900, 720)
        tenure       = st.slider("Tenure (months)", 6, 240, 36, step=6)
    with col4:
        interest_rate = st.slider("Interest Rate (%)", 6.0, 24.0, 10.5, step=0.5)
        age           = st.slider("Applicant Age", 18, 70, 30)

    submitted = st.form_submit_button("🔍 Analyse Loan Application", use_container_width=True)

# ── Analysis ────────────────────────────────────────────────
if submitted:
    if not name:
        st.warning("Please enter applicant name.")
        st.stop()

    emi          = calc_emi(loan_amount, interest_rate, tenure)
    monthly_inc  = round(annual_income / 12)
    emi_ratio    = round((emi / monthly_inc) * 100, 1)
    risk_score   = calc_risk_score(credit_score, emi_ratio, existing, employment)
    total_pay    = emi * tenure
    total_int    = total_pay - loan_amount

    st.divider()
    st.markdown("#### 📊 Financial Analysis")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly EMI",     f"₹{emi:,.0f}")
    m2.metric("Monthly Income",  f"₹{monthly_inc:,.0f}")
    m3.metric("EMI / Income",    f"{emi_ratio}%")
    m4.metric("Total Interest",  f"₹{total_int:,.0f}")

    st.markdown(f"**Approval Probability: {risk_score}%**")
    bar_color = "green" if risk_score >= 70 else "orange" if risk_score >= 45 else "red"
    st.progress(risk_score / 100)

    if risk_score >= 70:
        st.success(f"✅ Loan Approved — Confidence: {risk_score}%")
        status = "approved"
        st.info("Strong credit profile with manageable EMI-to-income ratio. Recommend standard processing with documentation verification.")
    elif risk_score >= 45:
        st.warning(f"⚠️ Manual Review Required — Score: {risk_score}%")
        status = "review"
        st.info("Borderline application. Additional collateral or guarantor recommended. Senior officer review required before disbursement.")
    else:
        st.error(f"❌ Loan Rejected — Risk Score: {risk_score}%")
        status = "rejected"
        st.info("High risk indicators detected. Reapply after 6 months with improved credit score (680+) or reduced loan amount.")

    # ── Save to DB ───────────────────────────────────────────
    st.divider()
    if st.session_state.role in ["admin", "officer"]:
        if st.button("💾 Save Application to Database", use_container_width=True):
            try:
                # Insert borrower
                execute("""
                    INSERT INTO borrowers
                        (full_name, email, credit_score, annual_income,
                         employment_type, property_area, existing_loans)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, email, credit_score, annual_income,
                      employment, property_area, existing))

                # Get borrower_id
                rows = fetch_all(
                    "SELECT borrower_id FROM borrowers WHERE full_name=%s ORDER BY borrower_id DESC LIMIT 1",
                    (name,)
                )
                borrower_id = rows[0]["borrower_id"]

                # Insert application
                execute("""
                    INSERT INTO loan_applications
                        (borrower_id, reviewed_by, loan_amount, loan_purpose,
                         interest_rate, tenure_months, status, approval_probability)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (borrower_id, None, loan_amount, purpose,
                      interest_rate, tenure, status, risk_score))

                st.success("Application saved successfully!")
            except Exception as e:
                st.error(f"DB Error: {e}")
    else:
        st.caption("🔒 Viewer role cannot save applications.")

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Expiry Strategy Tool", layout="centered")

st.title("Expiry Strategy Tool with Auto Lot Size")

if 'data' not in st.session_state:
    st.session_state.data = {}

index_name = st.selectbox("Select Index", ["NIFTY", "SENSEX"])
expiry_date = st.date_input("Expiry Date", datetime.today())
spot_price = st.number_input("Spot Price (Index Closing at 9:30 AM)", min_value=0, value=st.session_state.data.get('spot_price', 0))
vix = st.number_input("India VIX (Closing at 9:30 AM)", min_value=0.0, value=st.session_state.data.get('vix', 0.0))
capital = st.number_input("Your Capital (₹)", min_value=0, value=st.session_state.data.get('capital', 0))
premium = st.number_input("Sell Side Premium (CE/PE)", min_value=0.0, value=st.session_state.data.get('premium', 0.0))
notes = st.text_area("Notes (Optional)", value=st.session_state.data.get('notes', ''))

st.session_state.data.update({
    'spot_price': spot_price,
    'vix': vix,
    'capital': capital,
    'premium': premium,
    'notes': notes
})

st.markdown("---")

if st.button("Calculate"):
    lot_size = 50 if index_name == "NIFTY" else 15
    range_pct = vix / 19.1
    upper_level = spot_price * (1 + range_pct / 100)
    lower_level = spot_price * (1 - range_pct / 100)

    st.success(f"Upper Level: {round(upper_level, 2)} | Lower Level: {round(lower_level, 2)}")

    if premium >= 30:
        hedge = "Buy hedge around ₹5"
    elif 10 <= premium < 30:
        hedge = "Buy hedge around ₹2-₹3"
    elif premium < 10:
        hedge = "Buy hedge around ₹1-₹2"
    st.info(f"Hedge Suggestion: {hedge}")

    est_roi = (premium * 2 * lot_size) / capital * 100
    st.metric("Estimated ROI %", f"{round(est_roi, 2)}%")

    df = pd.DataFrame([{
        "Index": index_name,
        "Expiry Date": expiry_date,
        "Spot Price": spot_price,
        "VIX": vix,
        "Upper Level": round(upper_level, 2),
        "Lower Level": round(lower_level, 2),
        "Premium": premium,
        "Hedge": hedge,
        "Lot Size": lot_size,
        "Notes": notes,
        "Estimated ROI %": f"{round(est_roi, 2)}%"
    }])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="expiry_strategy.csv", mime="text/csv")

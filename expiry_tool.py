import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Expiry Strategy Tool", layout="centered")

st.title("Expiry Strategy Tool with Auto Lot Size")

# Function to calculate nearest strike price
def calculate_nearest_strike(level, index_name):
    if index_name == "NIFTY":
        interval = 50
    elif index_name == "SENSEX":
        interval = 100

    # For Upper Level (CE): Round up to the nearest interval
    if level == "upper":
        strike = spot_price * (1 + range_pct / 100)
        nearest_strike = ((strike // interval) + 1) * interval
        return f"{int(nearest_strike)} CE"

    # For Lower Level (PE): Round down to the nearest interval
    elif level == "lower":
        strike = spot_price * (1 - range_pct / 100)
        nearest_strike = (strike // interval) * interval
        return f"{int(nearest_strike)} PE"

# Initialize session state for data and saved results
if 'data' not in st.session_state:
    st.session_state.data = {}

if 'saved_results' not in st.session_state:
    st.session_state.saved_results = []

# Input fields
index_name = st.selectbox("Select Index", ["NIFTY", "SENSEX"])
expiry_date = st.date_input("Expiry Date", datetime.today())
spot_price = st.number_input("Spot Price (Index Closing at 9:30 AM)", min_value=0, value=st.session_state.data.get('spot_price', 0))
vix = st.number_input("India VIX (Closing at 9:30 AM)", min_value=0.0, value=st.session_state.data.get('vix', 0.0))
capital = st.number_input("Your Capital (₹)", min_value=0, value=st.session_state.data.get('capital', 0))
notes = st.text_area("Notes (Optional)", value=st.session_state.data.get('notes', ''))

# Update session state with current inputs
st.session_state.data.update({
    'spot_price': spot_price,
    'vix': vix,
    'capital': capital,
    'notes': notes
})

st.markdown("---")

# Calculate button
if st.button("Calculate"):
    lot_size = 50 if index_name == "NIFTY" else 15
    range_pct = vix / 19.1

    # Calculate Upper and Lower Levels
    upper_level = spot_price * (1 + range_pct / 100)
    lower_level = spot_price * (1 - range_pct / 100)

    # Calculate Nearest Strike Prices
    upper_strike = calculate_nearest_strike("upper", index_name)
    lower_strike = calculate_nearest_strike("lower", index_name)

    # Display Results
    st.success(f"Upper Level: {round(upper_level, 2)} | Sell: {upper_strike}")
    st.success(f"Lower Level: {round(lower_level, 2)} | Sell: {lower_strike}")

    # Hedge Suggestion (based on VIX)
    if vix >= 30:
        hedge = "Buy hedge around ₹5"
    elif 10 <= vix < 30:
        hedge = "Buy hedge around ₹2-₹3"
    elif vix < 10:
        hedge = "Buy hedge around ₹1-₹2"
    st.info(f"Hedge Suggestion: {hedge}")

    # Create a result dictionary
    result = {
        "Index": index_name,
        "Expiry Date": expiry_date,
        "Spot Price": spot_price,
        "VIX": vix,
        "Upper Level": round(upper_level, 2),
        "Upper Strike": upper_strike,
        "Lower Level": round(lower_level, 2),
        "Lower Strike": lower_strike,
        "Hedge": hedge,
        "Lot Size": lot_size,
        "Notes": notes
    }

    # Save the result to session state
    st.session_state.saved_results.append(result)

    # Display saved results
    st.subheader("Saved Results")
    saved_df = pd.DataFrame(st.session_state.saved_results)
    st.dataframe(saved_df)

    # Download CSV button
    csv = saved_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download All Results as CSV", data=csv, file_name="all_expiry_strategies.csv", mime="text/csv")
import os
import datetime
import pandas as pd
import streamlit as st

FILE_NAME = "Unit.csv"

COLUMNS = [
    "Date",
    "Name",
    "Starting_Units",
    "Ending_Units",
    "Consumed_Units",
    "Unit_Price",
    "Total_Price",
]

# 1. Load or Initialize DataFrame safely
if os.path.exists(FILE_NAME):
    try:
        df = pd.read_csv(FILE_NAME)
        # Clean up any potential unnamed index columns created by old glitches
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    except Exception:
        df = pd.DataFrame(columns=COLUMNS)
    
    # FIXED: Reindex ensures exactly the right columns exist once, without duplicating them
    df = df.reindex(columns=COLUMNS)
    
    # Remove corrupt blank records safely
    df = df.dropna(subset=["Name"])
    df["Name"] = df["Name"].astype(str)
    df = df[df["Name"].str.strip() != ""]
else:
    df = pd.DataFrame(columns=COLUMNS)

st.title("⚡ Electricity Unit Calculator of Turbine!")
st.markdown("---")

# 2. Input Form
with st.form("calculator_form", clear_on_submit=False):

    date_input = st.date_input("Select Date:", datetime.date.today())
    formatted_date = date_input.strftime("%d-%m-%Y")

    name = st.text_input("Name:", key="input_name")
    starting_unit = st.number_input("Starting Units:", min_value=0, value=0, step=1, key="input_start")
    ending_unit = st.number_input("Ending Units:", min_value=0, value=0, step=1, key="input_end")
    unit_price = st.number_input("Unit Price:", min_value=0, value=0, step=1, key="input_unit_price")

    submit_button = st.form_submit_button("Calculate & Save Data!")

if submit_button:

    if not name or not name.strip() or name.lower() == "none":
        st.error("❌ Please enter a valid Name before saving.")

    elif ending_unit < starting_unit:
        st.error("❌ Ending Units cannot be less than Starting Units!")

    elif ending_unit == 0:
        st.error("❌ Enter Ending Units! (Cannot be 0)")

    elif unit_price == 0:
        st.error("❌ Enter Unit Price! (Price cannot be 0)")

    else:
        consumed_units = int(ending_unit - starting_unit)
        total_cost = int(consumed_units * unit_price)

        new_row = {
            "Date": str(formatted_date),
            "Name": str(name.strip()),
            "Starting_Units": int(starting_unit),
            "Ending_Units": int(ending_unit),
            "Consumed_Units": consumed_units,
            "Unit_Price": int(unit_price),
            "Total_Price": total_cost,
        }

        # Safe index-based appending to ensure no column duplication
        df.loc[len(df)] = new_row
        df.to_csv(FILE_NAME, index=False)
        st.rerun()

st.markdown("---")

# 3. Personalized Data Search Feature
st.subheader("🔍 Look Up Specific User Data")

if not df.empty:
    df["Name"] = df["Name"].astype(str)
    unique_names = sorted(df["Name"].unique())
    search_name = st.selectbox("Select a name to view personalized history:", ["Show All Records"] + unique_names)

    if search_name != "Show All Records":
        user_df = df[df["Name"] == search_name]
        user_total_units = user_df["Consumed_Units"].sum()
        user_total_spent = user_df["Total_Price"].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f"Total Units Consumed by {search_name}", value=f"{user_total_units:,} kWh")
        with col2:
            st.metric(label=f"Total Bill Amount", value=f"Rs. {user_total_spent:,}")
            
        st.dataframe(user_df)
    else:
        st.info("Displaying the full list of recent entries below.")
        st.dataframe(df.tail(10)) 
else:
    st.info("No records found yet. Input data above to start!")

# 4. Database Tools Sidebar
if not df.empty:
    st.sidebar.markdown("### 🛠️ Database Tools")
    if st.sidebar.button("🗑️ Delete Last Entry"):
        df = df.drop(df.index[-1])
        df.to_csv(FILE_NAME, index=False)
        st.rerun()

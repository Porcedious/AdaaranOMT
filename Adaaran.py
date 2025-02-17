import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

# Title
st.title("🏨 Multi-Resort Rate Calculator")
st.subheader("Easily calculate rates for multiple resorts based on contracts")

# Resort Contracts Data
resorts_data = {
    "Heritance Aarah": {
        "room_rates": {
            "Beach Villa": [978, 953, 771, 797],
            "Ocean Villa": [1041, 1024, 853, 879],
            "Sunset Pool Beach Villa": [1104, 1095, 926, 951],
            "Overwater Ocean Suite": [1504, 1490, 1287, 1387]
        },
        "seasons": [
            ("2025-02-01", "2025-03-31"),
            ("2025-04-01", "2025-04-30"),
            ("2025-05-01", "2025-07-31"),
            ("2025-08-01", "2025-10-31")
        ],
        "extra_charges": {"adult": [265, 285, 337, 330], "child": [133, 143, 168, 165], "green_tax": 12},
        "min_stay": 3,
        "extra_night_charge": 150
    },
    "Adaaran Select Hudhuranfushi": {
        "room_rates": {
            "Garden Villa": [503, 427, 345, 390, 396],
            "Beach Villa": [555, 491, 409, 456, 460],
            "Deluxe Beach Villa": [587, 530, 447, 495, 499],
            "Sunset Beach Villa": [608, 556, 460, 508, 512],
            "Sunrise Ocean Villa": [691, 637, 582, 589, 604],
            "Sunset Ocean Villa": [712, 661, 602, 607, 623]
        },
        "seasons": [
            ("2025-02-01", "2025-03-31"),
            ("2025-04-01", "2025-04-30"),
            ("2025-05-01", "2025-07-31"),
            ("2025-08-01", "2025-09-30"),
            ("2025-10-01", "2025-10-31")
        ],
        "extra_charges": {"adult": [180, 182], "child": [90, 92], "green_tax": 12},
        "min_stay": 2,
        "extra_night_charge": 50
    },
    "Adaaran Prestige Vadoo": {
        "room_rates": {
            "Overwater Villa": [887, 845, 770, 658],
            "Sunrise Water Villa with Private Pool & Jacuzzi": [919, 875, 800, 689],
            "Sunset Water Villa with Private Pool & Jacuzzi": [1013, 965, 900, 740],
            "Honeymoon Water Villa with Private Pool & Jacuzzi": [1059, 1009, 950, 842]
        },
        "seasons": [
            ("2025-02-01", "2025-02-28"),
            ("2025-03-01", "2025-03-31"),
            ("2025-04-01", "2025-04-30"),
            ("2025-05-01", "2025-10-31")
        ],
        "extra_charges": {"adult": [315, 300, 306, 295], "green_tax": 12},
        "min_stay": 3,
        "adult_only": True
    }
}

# Resort Selection
resort_choice = st.selectbox("🏝 Select Resort", list(resorts_data.keys()))
resort_info = resorts_data[resort_choice]

# Display warning if resort is adult-only
if resort_info.get("adult_only", False):
    st.warning("⚠️ This is an ADULT-ONLY resort. Children are not allowed.")

# Display minimum stay requirements
st.info(f"ℹ️ Minimum Stay Requirement: {resort_info['min_stay']} nights for {resort_choice}.")

# Option to split room categories
split_rooms = st.checkbox("🔄 Split Room Categories?")
num_stays = 2 if split_rooms else 1

# Guest Details
st.subheader("👨‍👩‍👧‍👦 Number of Guests")
num_adults = st.number_input("Number of Adults", min_value=1, value=2)
num_children = st.number_input("Number of Children", min_value=0, value=0 if not resort_info.get("adult_only", False) else 0, disabled=resort_info.get("adult_only", False))

# Check-in Details
st.subheader("📅 Booking Details")
check_in_date = st.date_input("Check-in Date", value=datetime.today().date())
num_rooms = st.number_input("🛏 Number of Rooms", min_value=1, value=1)

stay_details = []
total_nights = 0
for i in range(num_stays):
    st.subheader(f"🏡 Stay {i+1} Details")
    room_type = st.selectbox(f"Choose Room Type for Stay {i+1}", list(resort_info['room_rates'].keys()), key=f"room_type_{i}")
    num_nights = st.number_input(f"🌙 Number of Nights for Stay {i+1}", min_value=1, value=1, key=f"num_nights_{i}")
    total_nights += num_nights
    
    if i == 0:
        stay_check_in_date = check_in_date
    else:
        stay_check_in_date = stay_details[i-1]["check_in_date"] + timedelta(days=stay_details[i-1]["num_nights"])
    
    stay_details.append({"room_type": room_type, "num_nights": num_nights, "check_in_date": stay_check_in_date})
    st.write(f"📅 Check-in Date for Stay {i+1}: {stay_check_in_date.strftime('%Y-%m-%d')}")

# Validate minimum stay requirement
if total_nights < resort_info["min_stay"]:
    st.error(f"⛔ Minimum stay for {resort_choice} is {resort_info['min_stay']} nights. Please adjust your booking.")
else:
    # Price Calculation
    if st.button("💰 Calculate Cost"):
        total_cost = 0
        for stay in stay_details:
            season_index = next((index for index, (start, end) in enumerate(resort_info['seasons']) if datetime.strptime(start, "%Y-%m-%d").date() <= stay['check_in_date'] <= datetime.strptime(end, "%Y-%m-%d").date()), None)
            
            if season_index is None:
                st.error("Error: No valid season found for selected dates.")
                continue
            
            base_rate = resort_info['room_rates'][stay['room_type']][season_index] * stay['num_nights'] * num_rooms
            extra_adult_cost = max(0, num_adults - 2) * resort_info['extra_charges']['adult'][season_index] * stay['num_nights'] * num_rooms if num_adults > 2 else 0
            extra_child_cost = num_children * resort_info['extra_charges'].get('child', [0]*4)[season_index] * stay['num_nights'] * num_rooms
            green_tax_cost = (num_adults + num_children) * resort_info['extra_charges']['green_tax'] * stay['num_nights']
            extra_night_charge = resort_info.get("extra_night_charge", 0) * num_rooms * stay['num_nights']
            total_cost += base_rate + extra_adult_cost + extra_child_cost + green_tax_cost + extra_night_charge
        
        st.success(f"💵 Total Cost for {resort_choice}: ${total_cost}")

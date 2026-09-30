
import math
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# SMART MALL PARKING SYSTEM
# ============================================================

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "parking_system.db"

PARKING_SLOTS = [
    ("A-1-001", 50), ("A-1-002", 60), ("A-1-003", 70),
    ("B-1-001", 30), ("B-1-002", 20), ("B-1-003", 40),
    ("C-1-001", 80), ("C-1-002", 90), ("C-1-003", 70),
]

SHAPES = [
    "Rectangle", "Square", "Circle",
    "Triangle", "Trapezium", "Ellipse"
]

# ============================================================
# DATABASE
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS parked_vehicles (
                slot TEXT PRIMARY KEY,
                vehicle_number TEXT NOT NULL UNIQUE,
                vehicle_type TEXT NOT NULL
                    CHECK(vehicle_type IN ('Car', 'Bike')),
                entry_time TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS parking_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_number TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                slot TEXT NOT NULL,
                event_type TEXT NOT NULL
                    CHECK(event_type IN ('ENTRY', 'EXIT')),
                event_time TEXT NOT NULL
            )
        """)
        conn.commit()


def load_parked_vehicles():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT slot, vehicle_number, vehicle_type, entry_time
            FROM parked_vehicles
            ORDER BY slot
        """).fetchall()

    return {
        row["slot"]: {
            "vehicle_number": row["vehicle_number"],
            "vehicle_type": row["vehicle_type"],
            "entry_time": row["entry_time"],
        }
        for row in rows
    }


def get_history():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                event_time AS Time,
                event_type AS Event,
                vehicle_number AS 'Vehicle Number',
                vehicle_type AS 'Vehicle Type',
                slot AS Slot
            FROM parking_events
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


# ============================================================
# VEHICLE MANAGEMENT
# ============================================================

def recommend_slot(available_slots, vehicle_type):
    """Choose a deterministic available slot."""
    if not available_slots:
        return None

    return min(
        available_slots,
        key=lambda item: (item[1], item[0])
    )[0]


def record_entry(vehicle_number, vehicle_type, slot):
    now = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_connection() as conn:
        if slot not in {s[0] for s in PARKING_SLOTS}:
            raise ValueError("Parking slot does not exist.")

        conn.execute("""
            INSERT INTO parked_vehicles
            (slot, vehicle_number, vehicle_type, entry_time)
            VALUES (?, ?, ?, ?)
        """, (slot, vehicle_number, vehicle_type, now))

        conn.execute("""
            INSERT INTO parking_events
            (vehicle_number, vehicle_type, slot,
             event_type, event_time)
            VALUES (?, ?, ?, 'ENTRY', ?)
        """, (vehicle_number, vehicle_type, slot, now))

        conn.commit()


def record_exit(vehicle_number):
    now = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_connection() as conn:
        row = conn.execute("""
            SELECT slot, vehicle_type
            FROM parked_vehicles
            WHERE vehicle_number = ?
        """, (vehicle_number,)).fetchone()

        if row is None:
            return None

        conn.execute("""
            DELETE FROM parked_vehicles
            WHERE vehicle_number = ?
        """, (vehicle_number,))

        conn.execute("""
            INSERT INTO parking_events
            (vehicle_number, vehicle_type, slot,
             event_type, event_time)
            VALUES (?, ?, ?, 'EXIT', ?)
        """, (
            vehicle_number,
            row["vehicle_type"],
            row["slot"],
            now
        ))

        conn.commit()
        return row["slot"]


# ============================================================
# AREA CONVERSION
# ============================================================

def convert_to_sqft(value, unit):
    value = float(value)

    if not math.isfinite(value) or value < 0:
        raise ValueError(
            "Area must be a finite, non-negative number."
        )

    conversions = {
        "Acres": 43560.0,
        "Square Feet": 1.0,
        "Square Meters": 10.7639104167,
    }

    if unit not in conversions:
        raise ValueError(f"Unsupported area unit: {unit}")

    return value * conversions[unit]


# ============================================================
# PARKING CAPACITY CALCULATOR
# ============================================================

def calculate_parking_capacity(
    parking_area,
    floors=1,
    zones=1,
    road_percentage=20.0,
    ramp_percentage=5.0,
    entrance_percentage=5.0,
    car_space=180.0,
    bike_space=30.0,
):
    values = [
        parking_area,
        road_percentage,
        ramp_percentage,
        entrance_percentage,
        car_space,
        bike_space,
    ]

    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("All numeric inputs must be finite.")

    parking_area = max(0.0, float(parking_area))
    floors = max(1, int(floors))
    zones = max(1, int(zones))

    road_percentage = max(0.0, float(road_percentage))
    ramp_percentage = max(0.0, float(ramp_percentage))
    entrance_percentage = max(0.0, float(entrance_percentage))

    car_space = max(0.0, float(car_space))
    bike_space = max(0.0, float(bike_space))

    non_parking = (
        road_percentage
        + ramp_percentage
        + entrance_percentage
    )

    if non_parking > 100:
        raise ValueError(
            "Road, ramp, and entrance percentages "
            "cannot total more than 100%."
        )

    gross = parking_area * floors

    usable = gross * (1.0 - non_parking / 100.0)

    car_area = usable * 0.85
    bike_area = usable * 0.15

    cars = (
        math.floor(car_area / car_space)
        if car_space > 0 else 0
    )

    bikes = (
        math.floor(bike_area / bike_space)
        if bike_space > 0 else 0
    )

    return {
        "gross_area_sqft": round(gross, 2),
        "usable_area_sqft": round(usable, 2),
        "car_allocated_area_sqft": round(car_area, 2),
        "bike_allocated_area_sqft": round(bike_area, 2),
        "total_car_slots": cars,
        "total_bike_slots": bikes,
        "total_capacity": cars + bikes,
        "zones": zones,
        "floors": floors,
    }


# ============================================================
# 3D PARKING VISUALIZATION
# ============================================================

def create_parking_3d(parked_vehicles, selected_shape):
    free_x, free_y, free_z, free_text = [], [], [], []
    occupied_x, occupied_y, occupied_z = [], [], []
    occupied_text = []

    for i, (slot, _) in enumerate(PARKING_SLOTS):
        x = float(i % 3) * 3.0
        y = float(i // 3) * 3.0
        z = 0.0

        if slot in parked_vehicles:
            vehicle = parked_vehicles[slot]

            occupied_x.append(x)
            occupied_y.append(y)
            occupied_z.append(z)
            occupied_text.append(
                f"{slot}<br>{vehicle['vehicle_number']} "
                f"({vehicle['vehicle_type']})"
            )
        else:
            free_x.append(x)
            free_y.append(y)
            free_z.append(z)
            free_text.append(f"{slot}<br>Available")

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=free_x,
        y=free_y,
        z=free_z,
        mode="markers+text",
        text=[
            slot for slot, _ in PARKING_SLOTS
            if slot not in parked_vehicles
        ],
        textposition="top center",
        name="Available",
        marker=dict(
            size=9,
            color="#22c55e",
            symbol="square"
        ),
        hovertext=free_text,
        hoverinfo="text",
    ))

    fig.add_trace(go.Scatter3d(
        x=occupied_x,
        y=occupied_y,
        z=occupied_z,
        mode="markers+text",
        text=[
            slot for slot, _ in PARKING_SLOTS
            if slot in parked_vehicles
        ],
        textposition="top center",
        name="Occupied",
        marker=dict(
            size=9,
            color="#ef4444",
            symbol="square"
        ),
        hovertext=occupied_text,
        hoverinfo="text",
    ))

    fig.update_layout(
        title=(
            f"Parking layout — {selected_shape} "
            "boundary (schematic)"
        ),
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Floor",
            zaxis=dict(
                range=[-1, 2],
                tickvals=[0],
                ticktext=["Ground"]
            ),
        ),
        height=560,
        margin=dict(l=0, r=0, t=55, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )

    return fig


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart Mall Parking System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_database()

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"

if "selected_shape" not in st.session_state:
    st.session_state.selected_shape = "Rectangle"


# ============================================================
# CUSTOM CSS AND HEADER
# ============================================================

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

.hero-header {
    background: linear-gradient(
        135deg,
        rgba(15,23,42,.97),
        rgba(30,41,59,.97)
    );
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 20px;
    padding: 24px 36px;
    margin-bottom: 22px;
}

.hero-title {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff !important;
    text-shadow: 0 2px 12px rgba(56, 189, 248, 0.45);
    margin: 0;
}

div.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    min-height: 42px;
}
</style>

<div class="hero-header">
    <h1 class="hero-title">
        🚗 Smart Mall Parking System
    </h1>
    <p style="color:#cbd5e1;margin:6px 0 0 0;">
        Enterprise Real-Time Management &amp;
        ADSA Analytics Platform
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# NAVIGATION
# ============================================================

pages = [
    "🏠 Home",
    "🚘 Vehicle Entry",
    "🚪 Vehicle Exit",
    "🚙 Parked Vehicles",
    "📊 Analytics",
    "📐 Parking Area",
    "🏗️ 3D Parking",
    "ℹ️ About",
]

nav_cols = st.columns(len(pages))

for idx, page_name in enumerate(pages):
    with nav_cols[idx]:
        if st.button(
            page_name,
            key=f"navbar_button_{idx}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.current_page == page_name
                else "secondary"
            ),
        ):
            st.session_state.current_page = page_name
            st.rerun()

st.divider()

page = st.session_state.current_page

parked = load_parked_vehicles()

available_slots = [
    slot for slot in PARKING_SLOTS
    if slot[0] not in parked
]

total_slots = len(PARKING_SLOTS)
occupied_slots = len(parked)
available_count = len(available_slots)

occupancy_percentage = (
    occupied_slots / total_slots * 100
    if total_slots else 0
)


# ============================================================
# PAGE 1 — HOME
# ============================================================

if page == "🏠 Home":
    st.subheader("📌 System Dashboard Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Slots", total_slots)
    c2.metric("Available", available_count)
    c3.metric("Occupied", occupied_slots)
    c4.metric("Occupancy", f"{occupancy_percentage:.1f}%")

    st.divider()
    st.subheader("⚡ Core Capabilities")

    f1, f2, f3 = st.columns(3)

    f1.info(
        "🚘 **Vehicle Entry**\n\n"
        "Find and assign an available parking slot."
    )

    f2.info(
        "🚪 **Vehicle Exit**\n\n"
        "Process checkout and free the assigned slot."
    )

    f3.info(
        "📊 **Analytics**\n\n"
        "Review parking events and occupancy."
    )


# ============================================================
# PAGE 2 — VEHICLE ENTRY
# ============================================================

elif page == "🚘 Vehicle Entry":
    st.title("🚘 Vehicle Entry")

    with st.form("vehicle_entry_form"):
        v_num = st.text_input(
            "Enter Vehicle Number",
            placeholder="e.g. AP39AB1234"
        )

        v_type = st.selectbox(
            "Select Vehicle Type",
            ["Car", "Bike"]
        )

        submitted = st.form_submit_button(
            "🔍 Find Recommended Slot",
            use_container_width=True
        )

    if submitted:
        normalized = v_num.strip().upper()

        if not normalized:
            st.warning("Please enter a vehicle number.")

        elif any(
            v["vehicle_number"] == normalized
            for v in parked.values()
        ):
            st.warning("This vehicle is already parked.")

        elif not available_slots:
            st.error("No parking slots currently available.")

        else:
            slot = recommend_slot(available_slots, v_type)

            st.session_state.recommended_slot = slot
            st.session_state.recommended_vehicle = normalized
            st.session_state.recommended_type = v_type

    if st.session_state.get("recommended_slot"):
        slot = st.session_state.recommended_slot
        veh = st.session_state.recommended_vehicle
        typ = st.session_state.recommended_type

        current = load_parked_vehicles()

        if (
            slot in current
            or any(
                v["vehicle_number"] == veh
                for v in current.values()
            )
        ):
            st.warning(
                "The recommendation is no longer available. "
                "Please search again."
            )

            for key in (
                "recommended_slot",
                "recommended_vehicle",
                "recommended_type"
            ):
                st.session_state.pop(key, None)

        else:
            st.info(
                f"Assigning slot **{slot}** to **{veh}** ({typ})."
            )

            if st.button(
                "✅ Confirm Park Vehicle",
                key="btn_confirm_park",
                use_container_width=True
            ):
                try:
                    record_entry(veh, typ, slot)

                    st.success(
                        f"Vehicle {veh} successfully parked in {slot}."
                    )

                    for key in (
                        "recommended_slot",
                        "recommended_vehicle",
                        "recommended_type"
                    ):
                        st.session_state.pop(key, None)

                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error(
                        "The vehicle or slot was assigned in "
                        "another action. Refresh and try again."
                    )

                except Exception as err:
                    st.error(f"Could not park vehicle: {err}")


# ============================================================
# PAGE 3 — VEHICLE EXIT
# ============================================================

elif page == "🚪 Vehicle Exit":
    st.title("🚪 Vehicle Exit")

    with st.form("vehicle_exit_form"):
        exit_num = st.text_input(
            "Vehicle Number to Exit",
            placeholder="e.g. AP39AB1234"
        )

        submitted = st.form_submit_button(
            "🚗 Process Exit",
            use_container_width=True
        )

    if submitted:
        target = exit_num.strip().upper()

        if not target:
            st.warning("Please enter a vehicle number.")

        else:
            try:
                found_slot = record_exit(target)

                if found_slot:
                    st.success(
                        f"Vehicle {target} removed from slot {found_slot}."
                    )
                    st.rerun()

                else:
                    st.error(
                        f"Vehicle {target} not found in the parked list."
                    )

            except Exception as err:
                st.error(f"Could not process vehicle exit: {err}")


# ============================================================
# PAGE 4 — PARKED VEHICLES
# ============================================================

elif page == "🚙 Parked Vehicles":
    st.title("🚙 Currently Parked Vehicles")

    parked = load_parked_vehicles()

    if not parked:
        st.info("No vehicles currently parked.")

    else:
        df = pd.DataFrame([
            {
                "Slot": slot,
                "Vehicle Number": v["vehicle_number"],
                "Type": v["vehicle_type"],
                "Entry Time": v["entry_time"],
            }
            for slot, v in parked.items()
        ])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# PAGE 5 — ANALYTICS
# ============================================================

elif page == "📊 Analytics":
    st.title("📊 Parking Analytics")

    parked = load_parked_vehicles()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Slots", len(PARKING_SLOTS))
    c2.metric("Currently Occupied", len(parked))
    c3.metric(
        "Occupancy",
        f"{len(parked) / len(PARKING_SLOTS) * 100:.1f}%"
    )

    history = get_history()

    if history:
        st.subheader("Parking Event History")

        history_df = pd.DataFrame(history)

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        counts = (
            history_df.groupby("Event")
            .size()
            .reindex(["ENTRY", "EXIT"], fill_value=0)
        )

        st.bar_chart(counts)

    else:
        st.info("No parking history recorded yet.")


# ============================================================
# PAGE 6 — PARKING AREA
# ============================================================

elif page == "📐 Parking Area":
    st.title("📐 Parking Area Planner")

    st.write(
        "Estimate parking capacity from a land area "
        "and allocation assumptions."
    )

    c1, c2 = st.columns(2)

    with c1:
        area_val = st.number_input(
            "Land Area Size",
            min_value=0.1,
            value=2.0,
            step=0.1
        )

        area_unit = st.selectbox(
            "Unit",
            ["Acres", "Square Feet", "Square Meters"]
        )

        shape = st.selectbox(
            "Parking Geometry Shape",
            SHAPES,
            key="area_shape"
        )

        floors = st.number_input(
            "Number of Parking Floors",
            min_value=1,
            value=1,
            step=1
        )

        zones = st.number_input(
            "Number of Parking Zones",
            min_value=1,
            value=1,
            step=1
        )

    with c2:
        st.subheader("📐 Area Allocation")

        road = st.number_input(
            "Road / Circulation %",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0
        )

        ramp = st.number_input(
            "Ramp %",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=1.0
        )

        entrance = st.number_input(
            "Entrance %",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=1.0
        )

        st.subheader("🚗 Vehicle Space Requirements")

        car_space = st.number_input(
            "Space Required Per Car (sq ft)",
            min_value=1.0,
            value=180.0,
            step=5.0
        )

        bike_space = st.number_input(
            "Space Required Per Bike (sq ft)",
            min_value=1.0,
            value=30.0,
            step=5.0
        )

    st.caption(
        f"Selected geometry: {shape}. "
        "Capacity is an estimate; geometry does not alter "
        "the area-only calculation."
    )

    if st.button(
        "📊 Calculate Layout",
        key="btn_calc_layout",
        use_container_width=True,
        type="primary"
    ):
        try:
            sqft = convert_to_sqft(area_val, area_unit)

            result = calculate_parking_capacity(
                sqft,
                floors,
                zones,
                road,
                ramp,
                entrance,
                car_space,
                bike_space
            )

            st.success(
                "Parking layout calculated successfully!"
            )

            st.subheader("📊 Parking Capacity")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total Area", f"{sqft:,.2f} sq ft")
            c2.metric(
                "Usable Area",
                f"{result['usable_area_sqft']:,.2f} sq ft"
            )
            c3.metric("Car Slots", result["total_car_slots"])
            c4.metric("Bike Slots", result["total_bike_slots"])

            c1, c2, c3 = st.columns(3)

            c1.metric("Total Capacity", result["total_capacity"])
            c2.metric("Parking Floors", result["floors"])
            c3.metric("Parking Zones", result["zones"])

            details = [
                ("Total Gross Area",
                 f"{result['gross_area_sqft']:,.2f} sq ft"),
                ("Usable Parking Area",
                 f"{result['usable_area_sqft']:,.2f} sq ft"),
                ("Car Allocated Area",
                 f"{result['car_allocated_area_sqft']:,.2f} sq ft"),
                ("Bike Allocated Area",
                 f"{result['bike_allocated_area_sqft']:,.2f} sq ft"),
                ("Car Parking Slots", result["total_car_slots"]),
                ("Bike Parking Slots", result["total_bike_slots"]),
                ("Total Parking Capacity", result["total_capacity"]),
                ("Parking Floors", result["floors"]),
                ("Parking Zones", result["zones"]),
            ]

            st.subheader("📋 Detailed Calculation")

            st.dataframe(
                pd.DataFrame(
                    details,
                    columns=["Parameter", "Value"]
                ),
                use_container_width=True,
                hide_index=True
            )

        except Exception as err:
            st.error(f"Unable to calculate parking capacity: {err}")


# ============================================================
# PAGE 7 — 3D PARKING
# ============================================================

elif page == "🏗️ 3D Parking":
    st.title("🏗️ 3D Parking Visualization")

    current_shape = st.session_state.get(
        "selected_shape", "Rectangle"
    )

    selected_shape = st.selectbox(
        "Select Geometric Boundary Shape",
        SHAPES,
        index=(
            SHAPES.index(current_shape)
            if current_shape in SHAPES else 0
        ),
    )

    st.session_state.selected_shape = selected_shape

    st.plotly_chart(
        create_parking_3d(
            load_parked_vehicles(),
            selected_shape
        ),
        use_container_width=True
    )


# ============================================================
# PAGE 8 — ABOUT
# ============================================================

elif page == "ℹ️ About":
    st.title("ℹ️ About System")

    st.write(
        "Smart Mall Parking System powered by Python, "
        "Streamlit, Pandas, SQLite, and Plotly."
    )

    st.divider()
    st.subheader("🛠️ Technologies")

    st.markdown(
        "- Python\n"
        "- Streamlit\n"
        "- Pandas\n"
        "- SQLite local database\n"
        "- Plotly 3D visualization"
    )

    st.divider()
    st.subheader("🚗 Parking System Features")

    st.markdown(
        "- Vehicle entry and exit management\n"
        "- Automatic slot recommendation\n"
        "- Persistent parking history\n"
        "- Parking analytics\n"
        "- Parking capacity calculator\n"
        "- Multiple floor and zone inputs\n"
        "- Schematic 3D parking visualization"
    )
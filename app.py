import streamlit as st

st.set_page_config(page_title="Fiber Techno-Economic Analysis", layout="wide")

st.title("Techno-Economic Fiber Production Analysis")

# --- Sidebar Section Navigation ---
section = st.sidebar.selectbox(
    "Choose a Section",
    [
        "Production Capacity",
        "Solution Preparation",
        "Extruder",
        "Spinning",
        "Stretching",
        "Drying",
        "Raw Materials",
        "Economic Summary"
    ]
)

# ---- Section: Production Capacity ----
if section == "Production Capacity":
    st.header("Production Capacity")

    # Inputs (editable)
    annual_production_ton = st.number_input("Annual Production (tons/year)", min_value=1, value=250)
    operational_days = st.number_input("Operational Days per Year", min_value=1, max_value=366, value=300)
    dpf = st.number_input("Filament Linear Density (dpf)", min_value=0.01, value=3.1)
    take_up_speed = st.number_input("Take-up Speed (m/min)", min_value=1, value=100)
    spinnerets = st.number_input("Number of Spinnerets", min_value=1, value=50)
    holes_per_spinneret = st.number_input("Holes Per Spinneret", min_value=1, value=360)

    # Calculations
    operational_minutes = operational_days * 24 * 60
    annual_production_kg = annual_production_ton * 1000
    annual_production_g = annual_production_kg * 1000
    g_per_min = annual_production_g / operational_minutes
    g_per_m = dpf / 9000
    filament_m_per_min = g_per_min / g_per_m
    n_filaments_needed = filament_m_per_min / take_up_speed
    n_spinneret_holes = spinnerets * holes_per_spinneret

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Dry Fiber Output (g/min)", round(g_per_min, 2))
        st.metric("Filament Linear Density (g/m)", g_per_m)
        st.metric("Filament Linear Density (dpf)", dpf)
        st.metric("Operational Time (min/year)", operational_minutes)
    with col2:
        st.metric("Total Filament Output (m/min)", int(filament_m_per_min))
        st.metric("Take-up Speed (m/min)", take_up_speed)
        st.metric("Filaments Needed", int(n_filaments_needed))
        st.metric("Design Filaments (Spinneret Holes)", n_spinneret_holes)

    st.info(
        f"**Design Used:** {spinnerets} spinnerets × {holes_per_spinneret} holes = "
        f"{n_spinneret_holes:,} filaments (compare to {int(n_filaments_needed):,} minimum needed)\n"
        "To reach higher annual output, run additional production trains in parallel."
    )

    st.caption("Change any parameter above to see live updates.")

# ---- Section: Solution Preparation ----
elif section == "Solution Preparation":
    st.header("Solution Preparation")
    st.write("Section under construction. Add your calculation logic and inputs here!")

# ---- Section: Extruder ----
elif section == "Extruder":
    st.header("Extruder")
    st.write("Section under construction. Add your calculation logic and inputs here!")

# ---- Section: Spinning ----
elif section == "Spinning":
    st.header("Spinning")
    st.write("Section under construction. Add your calculation logic and inputs here!")

# ---- Section: Stretching ----
elif section == "Stretching":
    st.header("Stretching")
    st.write("Section under construction. Add your calculation logic and inputs here!")

# ---- Section: Drying ----
elif section == "Drying":
    st.header("Drying")
    st.write("Section under construction. Add your calculation logic and inputs here!")

# ---- Section: Raw Materials ----
elif section == "Raw Materials":
    st.header("Raw Materials")
    st.write("Section under construction. Add your calculation logic and inputs here!")

# ---- Section: Economic Summary ----
elif section == "Economic Summary":
    st.header("Economic Summary")
    st.write("Section under construction. Add your calculation logic and summary outputs here!")

# ---------- END ----------

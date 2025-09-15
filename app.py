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
        "Fiber Property",
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
    
    # Polymer Solution Preparation code block
    polymer_wt_frac = st.number_input("Polymer Weight Fraction in Solution (g/g)", min_value=0.001, max_value=1.0, value=0.1, step=0.01)
    dry_fiber_g_per_min = st.number_input("Dry Fiber Output (g/min)", min_value=1.0, value=5787.04, step=1.0)
    solution_density = st.number_input("Polymer Solution Density (g/cc)", min_value=0.5, max_value=2.0, value=0.9, step=0.01)
    spinnerets = st.number_input("Number of Spinnerets", min_value=1, value=50, step=1)
    holes_per_spinneret = st.number_input("Holes Per Spinneret", min_value=1, value=360, step=1)

    solution_g_per_min = dry_fiber_g_per_min / polymer_wt_frac
    solution_cc_per_min = solution_g_per_min / solution_density
    total_holes = spinnerets * holes_per_spinneret
    solution_cc_per_min_per_hole = solution_cc_per_min / total_holes
    solution_g_per_min_per_hole = solution_g_per_min / total_holes

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Solution polymer flow (g/min)", round(solution_g_per_min, 2))
        st.metric("Solution flow rate (cc/min)", round(solution_cc_per_min, 2))
    with col2:
        st.metric("Solution flow per hole (cc/min/hole)", round(solution_cc_per_min_per_hole, 4))
        st.metric("Solution flow per hole (g/min/hole)", round(solution_g_per_min_per_hole, 4))

    st.caption(
        f"These values are based on a polymer weight fraction of {polymer_wt_frac}, a solution density of {solution_density} g/cc, and a total of {total_holes} spinning holes."
    )
# ---- Section: Extruder ----
elif section == "Extruder":
    st.header("Extruder")
    st.write("Section under construction. Add your calculation logic and inputs here!")

# ---- Section: Spinning ----
elif section == "Spinning":
    st.header("Spinning Calculations")

    import math

    # --- Core Spinning Inputs ---
    spinneret_hole_diameter_cm = st.number_input("Spinneret Hole Diameter (cm)", min_value=0.001, value=0.03, step=0.001)
    holes_per_spinneret = st.number_input("Holes per Spinneret", min_value=1, value=360, step=1)
    spinnerets = st.number_input("Number of Spinnerets", min_value=1, value=50, step=1)
    solution_cc_per_min = st.number_input("Total Solution Flow Rate (cc/min)", min_value=0.01, value=6430.04, step=0.01)
    take_up_speed = st.number_input("Take-up Speed (m/min)", min_value=0.01, value=100.0, step=1.0)

    # --- Battery/Yarn Inputs ---
    spinnerets_per_battery = st.number_input("Spinnerets per Battery", min_value=1, value=10, step=1)
    filaments_per_yarn = st.number_input("Filaments per Yarn", min_value=1, value=720, step=1)

    # --- Calculations ---
    spinneret_hole_radius_cm = spinneret_hole_diameter_cm / 2
    hole_cross_section_cm2 = math.pi * spinneret_hole_radius_cm ** 2
    total_holes = spinnerets * holes_per_spinneret

    # Battery/group calculations
    num_batteries = math.ceil(spinnerets / spinnerets_per_battery)
    battery_flow_cc_per_min = solution_cc_per_min / num_batteries if num_batteries else 0  # cc/min per battery

    # Per spinneret, per yarn
    filaments_per_spinneret = holes_per_spinneret
    spinnerets_per_yarn = filaments_per_yarn // filaments_per_spinneret if filaments_per_spinneret else 0

    # Volumetric flow per hole and spinneret
    vol_flow_per_hole_cc_min = solution_cc_per_min / total_holes if total_holes else 0
    vol_flow_per_spinneret_cc_min = solution_cc_per_min / spinnerets if spinnerets else 0

    # Velocity leaving spinneret (m/min)
    hole_cross_section_m2 = hole_cross_section_cm2 * 1e-4
    vol_flow_per_hole_m3_min = vol_flow_per_hole_cc_min * 1e-6
    vel_leaving_spinneret_m_min = vol_flow_per_hole_m3_min / hole_cross_section_m2 if hole_cross_section_m2 else 0

    # Draw ratio and fiber at TU
    solution_draw_ratio = take_up_speed / vel_leaving_spinneret_m_min if vel_leaving_spinneret_m_min else 0
    fiber_cross_section_cm2_TU = hole_cross_section_cm2 / solution_draw_ratio if solution_draw_ratio else 0
    fiber_diameter_cm = math.sqrt(fiber_cross_section_cm2_TU * 4 / math.pi) if fiber_cross_section_cm2_TU else 0
    fiber_diameter_um = fiber_diameter_cm * 10000

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Holes", total_holes)
        st.metric("Hole Cross Section (cm²)", round(hole_cross_section_cm2, 6))
        st.metric("Volumetric Flow per Hole (cc/min)", round(vol_flow_per_hole_cc_min, 6))
        st.metric("Volumetric Flow per Spinneret (cc/min)", round(vol_flow_per_spinneret_cc_min, 3))
        st.metric("Num. Batteries Needed", num_batteries)
        st.metric("Battery Flow Rate (L/min)", round(battery_flow_cc_per_min/1000, 2))
    with col2:
        st.metric("Velocity Leaving Spinneret (m/min)", round(vel_leaving_spinneret_m_min, 3))
        st.metric("Solution Draw Ratio", round(solution_draw_ratio, 3))
        st.metric("Fiber Cross Section at TU (cm²)", round(fiber_cross_section_cm2_TU, 6))
        st.metric("Fiber Diameter at TU (μm, no shrinkage)", round(fiber_diameter_um, 4))
        st.metric("Spinneret/Yarn", spinnerets_per_yarn)
        st.metric("Filaments per Yarn", filaments_per_yarn)

    st.caption(
        f"{num_batteries} batteries, each feeding {spinnerets_per_battery} spinnerets ({battery_flow_cc_per_min/1000:.2f} L/min per battery). "
        f"For {filaments_per_yarn} filaments/yarn, you need {spinnerets_per_yarn} spinnerets per yarn."
    )


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

# ---- Section: Fiber Property ----
elif section == "Fiber Property":
    st.header("Fiber Property Calculations")

    # Editable Inputs
    filament_diameter_um = st.number_input("Filament Diameter (μm)", min_value=1.0, value=22.08, step=0.01)
    filament_density = st.number_input("Density of PE (g/cc)", min_value=0.1, value=0.9, step=0.01)
    dpf = st.number_input("Denier Per Filament (dpf)", min_value=0.01, value=3.1, step=0.01)

    # Calculations
    filament_diameter_cm = filament_diameter_um / 10000  # μm → cm
    filament_crosssection_cm2 = 3.1416 * (filament_diameter_cm/2)**2  # A = πr^2

    # Filament g/1m: volume per length (cm^2 × 100 cm = cm^3) × density
    filament_g_per_m = filament_crosssection_cm2 * 100 * filament_density  # g/m

    # Cross-check with dpf:
    # 1 dpf = 1 g / 9000 m; dpf for this filament: filament_g_per_m * 9000
    calculated_dpf = filament_g_per_m * 9000

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Filament Diameter (μm)", filament_diameter_um)
        st.metric("Filament Cross-section (cm²)", filament_crosssection_cm2)
        st.metric("Filament Linear Density (g/m)", filament_g_per_m)
    with col2:
        st.metric("Cross-check dpf from g/m", calculated_dpf)
        st.metric("Input Denier Per Filament", dpf)

    st.caption(
        "Calculation uses filament diameter to compute cross-sectional area and linear density, "
        "and cross-checks measured dpf (g/9000m) against calculated value from geometry and density.")


# ---- Section: Economic Summary ----
elif section == "Economic Summary":
    st.header("Economic Summary")
    st.write("Section under construction. Add your calculation logic and summary outputs here!")

# ---------- END ----------

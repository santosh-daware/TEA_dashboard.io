import streamlit as st
import math
import pandas as pd
import altair as alt

st.set_page_config(page_title="Fiber Techno-Economic Analysis", layout="wide")

st.title("Techno-Economic Fiber Production Analysis")

# Use compact navigation with radio buttons
sections = [
    "Production Capacity", "Solution Preparation", "Extruder", "Spinning",
    "Stretching & Solvent Removal", "Drying", "Raw Materials", 
    "Fiber Property", "Economic Summary"
]

# Create a compact navigation
selected_section = st.radio("Navigate to Section:", sections, horizontal=True)

st.markdown("---")

# Add a schematic image (replace with your actual image path)
col1, col2 = st.columns([2, 1])
with col1:
    st.image("https://via.placeholder.com/800x400?text=Fiber+Production+Process+Schematic", 
             use_container_width=True, caption="Fiber Production Process Schematic")

# ---- Section: Production Capacity ----
if selected_section == "Production Capacity":
    st.header("Production Capacity")

    col1, col2 = st.columns(2)
    with col1:
        annual_production_ton = st.number_input("Annual Production (tons/year)", min_value=1, value=250)
        operational_days = st.number_input("Operational Days per Year", min_value=1, max_value=366, value=300)
        dpf = st.number_input("Filament Linear Density (dpf)", min_value=0.01, value=3.1)
    with col2:
        take_up_speed = st.number_input("Take-up Speed (m/min)", min_value=1, value=100)
        spinnerets = st.number_input("Number of Spinnerets", min_value=1, value=50)
        holes_per_spinneret = st.number_input("Holes Per Spinneret", min_value=1, value=360)

    # Calculations
    operational_minutes = operational_days * 24 * 60
    annual_production_g = annual_production_ton * 1000 * 1000
    g_per_min = annual_production_g / operational_minutes
    g_per_m = dpf / 9000
    filament_m_per_min = g_per_min / g_per_m
    n_filaments_needed = filament_m_per_min / take_up_speed
    n_spinneret_holes = spinnerets * holes_per_spinneret

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Dry Fiber Output (g/min)", round(g_per_min, 2))
        st.metric("Filament Linear Density (g/m)", round(g_per_m, 6))
        st.metric("Total Filament Output (m/min)", int(filament_m_per_min))
    with col2:
        st.metric("Filaments Needed", int(n_filaments_needed))
        st.metric("Design Filaments (Spinneret Holes)", n_spinneret_holes)
        st.metric("Utilization (%)", round((n_filaments_needed / n_spinneret_holes) * 100, 1))

# ---- Section: Solution Preparation ----
elif selected_section == "Solution Preparation":
    st.header("Solution Preparation")
    
    col1, col2 = st.columns(2)
    with col1:
        polymer_wt_frac = st.number_input("Polymer Weight Fraction", min_value=0.001, max_value=1.0, value=0.1, step=0.01)
        dry_fiber_g_per_min = st.number_input("Dry Fiber Output (g/min)", min_value=1.0, value=5787.04, step=1.0)
    with col2:
        solution_density = st.number_input("Solution Density (g/cc)", min_value=0.5, max_value=2.0, value=0.9, step=0.01)
        total_holes = st.number_input("Total Spinneret Holes", min_value=1, value=18000, step=1)

    solution_g_per_min = dry_fiber_g_per_min / polymer_wt_frac
    solution_cc_per_min = solution_g_per_min / solution_density
    solution_cc_per_min_per_hole = solution_cc_per_min / total_holes
    solution_g_per_min_per_hole = solution_g_per_min / total_holes

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Solution Flow (g/min)", round(solution_g_per_min, 2))
        st.metric("Solution Flow (cc/min)", round(solution_cc_per_min, 2))
    with col2:
        st.metric("Flow per Hole (cc/min)", round(solution_cc_per_min_per_hole, 4))
        st.metric("Flow per Hole (g/min)", round(solution_g_per_min_per_hole, 4))

# ---- Section: Extruder ----
elif selected_section == "Extruder":
    st.header("Extruder Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        screw_diameter = st.number_input("Screw Diameter (mm)", min_value=10, value=60, step=5)
        l_d_ratio = st.number_input("L/D Ratio", min_value=10, value=40, step=1)
        motor_power = st.number_input("Motor Power (kW)", min_value=1, value=200, step=10)
    with col2:
        max_rpm = st.number_input("Maximum RPM", min_value=10, value=300, step=10)
        throughput = st.number_input("Throughput (kg/h)", min_value=1, value=500, step=10)
        specific_energy = st.number_input("Specific Energy (kWh/kg)", min_value=0.1, value=0.15, step=0.01)
    
    st.metric("Screw Length (mm)", screw_diameter * l_d_ratio)
    st.metric("Energy Consumption (kW)", round(throughput * specific_energy, 1))

# ---- Section: Spinning ----
elif selected_section == "Spinning":
    st.header("Spinning Calculations")

    col1, col2 = st.columns(2)
    with col1:
        spinneret_hole_diameter = st.number_input("Hole Diameter (mm)", min_value=0.01, value=0.3, step=0.01)
        total_holes = st.number_input("Total Holes", min_value=1, value=18000, step=1)
        solution_cc_per_min = st.number_input("Solution Flow Rate (cc/min)", min_value=0.01, value=6430.04, step=0.01)
    with col2:
        take_up_speed = st.number_input("Take-up Speed (m/min)", min_value=0.01, value=100.0, step=1.0)
        spinnerets_per_battery = st.number_input("Spinnerets per Battery", min_value=1, value=10, step=1)
        filaments_per_yarn = st.number_input("Filaments per Yarn", min_value=1, value=720, step=1)

    # Calculations
    spinneret_hole_radius_cm = spinneret_hole_diameter / 20  # mm to cm, then radius
    hole_cross_section_cm2 = math.pi * spinneret_hole_radius_cm ** 2
    vol_flow_per_hole_cc_min = solution_cc_per_min / total_holes
    hole_cross_section_m2 = hole_cross_section_cm2 * 1e-4
    vol_flow_per_hole_m3_min = vol_flow_per_hole_cc_min * 1e-6
    vel_leaving_spinneret_m_min = vol_flow_per_hole_m3_min / hole_cross_section_m2 if hole_cross_section_m2 else 0
    solution_draw_ratio = take_up_speed / vel_leaving_spinneret_m_min if vel_leaving_spinneret_m_min else 0
    
    num_batteries = math.ceil(total_holes / (spinnerets_per_battery * (total_holes / 360))) if 'holes_per_spinneret' in st.session_state else 1
    battery_flow_cc_per_min = solution_cc_per_min / num_batteries if num_batteries else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Hole Cross Section (cm²)", round(hole_cross_section_cm2, 6))
        st.metric("Velocity at Spinneret (m/min)", round(vel_leaving_spinneret_m_min, 3))
        st.metric("Solution Draw Ratio", round(solution_draw_ratio, 3))
    with col2:
        st.metric("Num. Batteries Needed", num_batteries)
        st.metric("Battery Flow Rate (L/min)", round(battery_flow_cc_per_min/1000, 2))
        st.metric("Filaments per Yarn", filaments_per_yarn)

# ---- Section: Stretching & Solvent Removal ----
elif selected_section == "Stretching & Solvent Removal":
    st.header("Stretching & Solvent Removal")

    col1, col2 = st.columns(2)
    with col1:
        draw_ratio = st.number_input("Draw Ratio (ASF → Final)", min_value=0.1, value=9.33, step=0.01)
        asf_g_per_min = st.number_input("ASF Output (g/min)", min_value=0.01, value=643.0, step=1.0)
        solvent_removed_g_per_min = st.number_input("Solvent Removed (g/min)", min_value=1.0, value=5208.33, step=1.0)
    with col2:
        vel_tu_shrunk = st.number_input("Take-Up Speed (m/min)", min_value=0.1, value=150.0, step=1.0)
        solvent_conc_exit = st.number_input("Solvent Conc. at Exit (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        electricity_cost = st.number_input("Electricity Cost ($/kWh)", min_value=0.01, value=0.15, step=0.01)

    hexane_required_kg_min = solvent_removed_g_per_min / 1000
    hexane_required_kg_hr = hexane_required_kg_min * 60
    power_hexane_evap_kw = hexane_required_kg_hr * 0.5  # Simplified calculation
    annual_solvent_heat_cost = power_hexane_evap_kw * 7200 * electricity_cost  # 7200 operational hours

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Draw Ratio", draw_ratio)
        st.metric("Solvent Removed (kg/min)", round(hexane_required_kg_min, 2))
        st.metric("Hexane Required (kg/hr)", round(hexane_required_kg_hr, 2))
    with col2:
        st.metric("Evaporation Power (kW)", round(power_hexane_evap_kw, 1))
        st.metric("Annual Solvent Heat Cost ($)", round(annual_solvent_heat_cost, 0))

# ---- Section: Drying ----
elif selected_section == "Drying":
    st.header("Drying Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        drying_temperature = st.number_input("Drying Temperature (°C)", min_value=20, value=120, step=5)
        residence_time = st.number_input("Residence Time (min)", min_value=0.1, value=5.0, step=0.5)
        air_flow_rate = st.number_input("Air Flow Rate (m³/min)", min_value=1, value=100, step=10)
    with col2:
        initial_moisture = st.number_input("Initial Moisture (%)", min_value=0.0, value=20.0, step=1.0)
        final_moisture = st.number_input("Final Moisture (%)", min_value=0.0, value=1.0, step=0.1)
        energy_consumption = st.number_input("Energy Consumption (kWh/kg water)", min_value=0.1, value=1.2, step=0.1)
    
    water_removed = (initial_moisture - final_moisture) / 100 * 5787.04 / 1000
    drying_energy = water_removed * energy_consumption
    
    st.metric("Water Removed (kg/h)", round(water_removed * 60, 2))
    st.metric("Drying Energy (kW)", round(drying_energy, 2))

# ---- Section: Raw Materials ----
elif selected_section == "Raw Materials":
    st.header("Raw Materials Usage & Cost")
    
    col1, col2 = st.columns(2)
    with col1:
        uhmwpe_use_ton = st.number_input("UHMWPE Usage (T/yr)", min_value=1.0, value=250.0)
        solvent_makeup_ton = st.number_input("Makeup Solvent (T/yr)", min_value=0.0, value=67.5)
        additives_kg_yr = st.number_input("Additives (kg/yr)", min_value=0.0, value=2500.0)
    with col2:
        uhmwpe_cost = st.number_input("UHMWPE Cost ($/kg)", min_value=0.1, value=2.0)
        solvent_cost = st.number_input("Solvent Cost ($/kg)", min_value=0.1, value=2.0)
        additive_cost = st.number_input("Additive Cost ($/kg)", min_value=0.1, value=20.0)
    
    material_costs = (
        (uhmwpe_use_ton * 1000 * uhmwpe_cost) +
        (solvent_makeup_ton * 1000 * solvent_cost) +
        (additives_kg_yr * additive_cost)
    )
    
    st.metric("Total Material Cost ($/yr)", round(material_costs, 2))
    st.metric("Material Cost per kg Fiber ($/kg)", round(material_costs / (uhmwpe_use_ton * 1000), 2))

# ---- Section: Fiber Property ----
elif selected_section == "Fiber Property":
    st.header("Fiber Property Calculations")
    
    col1, col2 = st.columns(2)
    with col1:
        filament_diameter = st.number_input("Filament Diameter (μm)", min_value=1.0, value=22.08, step=0.01)
        filament_density = st.number_input("Density (g/cc)", min_value=0.1, value=0.9, step=0.01)
    with col2:
        dpf = st.number_input("Denier Per Filament (dpf)", min_value=0.01, value=3.1, step=0.01)
        tenacity = st.number_input("Tenacity (g/denier)", min_value=0.1, value=35.0, step=0.1)
    
    filament_diameter_cm = filament_diameter / 10000
    filament_crosssection = 3.1416 * (filament_diameter_cm/2)**2
    filament_g_per_m = filament_crosssection * 100 * filament_density
    calculated_dpf = filament_g_per_m * 9000
    tensile_strength = tenacity * dpf * 0.0882  # Convert to N/tex
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Filament Cross-section (cm²)", round(filament_crosssection, 8))
        st.metric("Calculated Linear Density (g/m)", round(filament_g_per_m, 6))
    with col2:
        st.metric("Calculated dpf", round(calculated_dpf, 2))
        st.metric("Tensile Strength (N/tex)", round(tensile_strength, 1))

# ---- Section: Economic Summary ----
elif selected_section == "Economic Summary":
    st.header("Profitability & Cost Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        capex_total = st.number_input("Total Capex ($)", min_value=1.0, value=915000.0)
        labor_cost = st.number_input("Labor Cost ($/yr)", min_value=0.0, value=200000.0)
        utility_cost = st.number_input("Utility Cost ($/yr)", min_value=0.0, value=50000.0)
    with col2:
        fiber_price = st.number_input("Fiber Selling Price ($/kg)", min_value=0.01, value=15.0, step=0.1)
        annual_production = st.number_input("Annual Production (tons)", min_value=1.0, value=250.0)
        maintenance_cost = st.number_input("Maintenance Cost ($/yr)", min_value=0.0, value=75000.0)
    with col3:
        material_cost_per_kg = st.number_input("Material Cost ($/kg)", min_value=0.01, value=2.5, step=0.1)
        depreciation_years = st.number_input("Depreciation Period (years)", min_value=1, value=10)
        other_costs = st.number_input("Other Costs ($/yr)", min_value=0.0, value=50000.0)
    
    # Calculate costs
    material_cost = annual_production * 1000 * material_cost_per_kg
    depreciation_cost = capex_total / depreciation_years
    total_annual_costs = material_cost + labor_cost + utility_cost + maintenance_cost + other_costs + depreciation_cost
    annual_revenue = annual_production * 1000 * fiber_price
    annual_profit = annual_revenue - total_annual_costs
    roi = annual_profit / capex_total * 100 if capex_total else 0
    
    # Create cost breakdown for pie chart
    cost_data = pd.DataFrame({
        'Category': ['Materials', 'Labor', 'Utilities', 'Maintenance', 'Other Costs', 'Depreciation'],
        'Amount': [material_cost, labor_cost, utility_cost, maintenance_cost, other_costs, depreciation_cost]
    })
    
    # Create pie chart using Altair
    pie_chart = alt.Chart(cost_data).mark_arc().encode(
        theta=alt.Theta(field="Amount", type="quantitative"),
        color=alt.Color(field="Category", type="nominal", 
                       scale=alt.Scale(scheme='category10')),
        tooltip=['Category', 'Amount']
    ).properties(
        width=400,
        height=400,
        title='Annual Cost Distribution'
    )
    
    # Display results
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Annual Revenue ($)", f"{annual_revenue:,.2f}")
        st.metric("Annual Costs ($)", f"{total_annual_costs:,.2f}")
        st.metric("Annual Profit ($)", f"{annual_profit:,.2f}")
        st.metric("ROI (%)", f"{roi:.1f}")
        st.metric("Payback Period (years)", f"{capex_total / annual_profit:.1f}" if annual_profit > 0 else "N/A")
        st.metric("Break-even Price ($/kg)", f"{total_annual_costs / (annual_production * 1000):.2f}")
    
    with col2:
        st.altair_chart(pie_chart, use_container_width=True)

st.markdown("---")
st.caption("Fiber Production Techno-Economic Analysis Tool v1.0")

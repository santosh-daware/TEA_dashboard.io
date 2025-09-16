import streamlit as st
import math
import pandas as pd
import altair as alt

st.set_page_config(page_title="Fiber Techno-Economic Analysis", layout="wide")
st.title("Techno-Economic Fiber Production Analysis")

sections = [
    "Production Capacity", "Solution Preparation", "Extruder", "Spinning",
    "Stretching & Solvent Removal", "Drying", "Raw Materials", 
    "Fiber Property", "Economic Summary"
]
selected_section = st.radio("Navigate to Section:", sections, horizontal=True)
st.markdown("---")

if 'dpf' not in st.session_state:
    st.session_state.dpf = 3.1
if 'filament_g_per_m' not in st.session_state:
    st.session_state.filament_g_per_m = st.session_state.dpf / 9000

# ---- GLOBAL (SESSION) DEFAULTS FOR TOP VISUALS ----
defaults = {
    "annual_production": 250,
    "fiber_price": 15.0,
    "capex_total": 915000.0,
    "depreciation_years": 10,
    "material_cost_per_kg": 2.5,
    "labor_cost": 200000.0,
    "utility_cost": 50000.0,
    "maintenance_cost": 75000.0,
    "other_costs": 50000.0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---- TOP-LEVEL ECONOMICS CALCULATIONS & PIE CHART ----
annual_production = st.session_state.annual_production
fiber_price = st.session_state.fiber_price
capex_total = st.session_state.capex_total
depreciation_years = st.session_state.depreciation_years
material_cost_per_kg = st.session_state.material_cost_per_kg
labor_cost = st.session_state.labor_cost
utility_cost = st.session_state.utility_cost
maintenance_cost = st.session_state.maintenance_cost
other_costs = st.session_state.other_costs

material_cost = annual_production * 1000 * material_cost_per_kg
depreciation_cost = capex_total / depreciation_years
total_annual_costs = material_cost + labor_cost + utility_cost + maintenance_cost + other_costs + depreciation_cost
annual_revenue = annual_production * 1000 * fiber_price
annual_profit = annual_revenue - total_annual_costs
roi = (annual_profit / capex_total * 100) if capex_total else 0
payback_period = capex_total / annual_profit if annual_profit > 0 else float('inf')
break_even = total_annual_costs / (annual_production * 1000) if annual_production > 0 else 0

cost_data = pd.DataFrame({
    'Category': ['Materials', 'Labor', 'Utilities', 'Maintenance', 'Other Costs', 'Depreciation'],
    'Amount': [material_cost, labor_cost, utility_cost, maintenance_cost, other_costs, depreciation_cost]
})
pie_chart = alt.Chart(cost_data).mark_arc().encode(
    theta=alt.Theta(field="Amount", type="quantitative"),
    color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme='category10')),
    tooltip=['Category', 'Amount']
).properties(width=200, height=200, title='Annual Cost Distribution')

colA, colB = st.columns([1.2, 1])
with colA:
    st.image(
        "https://via.placeholder.com/800x400?text=Fiber+Production+Process+Schematic", 
        use_container_width=True, caption="Fiber Production Process Schematic"
    )
with colB:
    st.altair_chart(pie_chart, use_container_width=True)
    
    # --- Custom two-column, reduced font metrics ---
    metric_style = """
    <style>
    .small-metric {
        font-size: 0.95rem;
        color: #495162;
        font-weight: 500;
        margin-bottom: 0.18em;
        letter-spacing: 0.01em;
    }
    .small-value {
        font-size: 1.17rem;
        color: #034078;
        font-weight: 700;
        margin-bottom: 0.8em;
    }
    </style>
    """
    st.markdown(metric_style, unsafe_allow_html=True)

    mcol1, mcol2 = st.columns(2)
    with mcol1:
        st.markdown('<div class="small-metric">Annual Revenue ($)</div>'
                    f'<div class="small-value">{annual_revenue:,.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-metric">Annual Profit ($)</div>'
                    f'<div class="small-value">{annual_profit:,.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-metric">Payback Period (years)</div>'
                    f'<div class="small-value">{payback_period:.1f}</div>', unsafe_allow_html=True)
    with mcol2:
        st.markdown('<div class="small-metric">Annual Costs ($)</div>'
                    f'<div class="small-value">{total_annual_costs:,.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-metric">ROI (%)</div>'
                    f'<div class="small-value">{roi:.1f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-metric">Break-even Price ($/kg)</div>'
                    f'<div class="small-value">{break_even:.2f}</div>', unsafe_allow_html=True)

st.markdown("---")


# ---- MAIN APP SECTIONS ----

if selected_section == "Production Capacity":
    st.header("Production Capacity")
    col1, col2 = st.columns(2)

    # -- GLOBAL SYNC for dpf and filament g/m --
    with col1:
        annual_production_ton = st.number_input(
            "Annual Production (tons/year)",
            min_value=1,
            value=int(st.session_state.annual_production)
        )
        operational_days = st.number_input(
            "Operational Days per Year",
            min_value=1, max_value=366,
            value=300
        )
        # Synchronized dpf input
        new_dpf = st.number_input(
            "Denier Per Filament (dpf)",
            min_value=0.01,
            value=float(st.session_state.dpf),
            step=0.01,
            key="prodcap_dpf"
        )
        if new_dpf != st.session_state.dpf:
            st.session_state.dpf = new_dpf
            st.session_state.filament_g_per_m = new_dpf / 9000

        new_filament_g_per_m = st.number_input(
            "Filament Linear Density (g/m)",
            min_value=0.00001,
            value=float(st.session_state.filament_g_per_m),
            step=0.00001,
            format="%.5f",
            key="prodcap_gpm"
        )
        # If changed directly, sync dpf!
        if abs(new_filament_g_per_m - st.session_state.filament_g_per_m) > 1e-8:
            st.session_state.filament_g_per_m = new_filament_g_per_m
            st.session_state.dpf = new_filament_g_per_m * 9000

    with col2:
        take_up_speed = st.number_input(
            "Take-up Speed (m/min)",
            min_value=1,
            value=100
        )
        spinnerets = st.number_input(
            "Number of Spinnerets",
            min_value=1,
            value=50
        )
        holes_per_spinneret = st.number_input(
            "Holes Per Spinneret",
            min_value=1,
            value=360
        )

    # --- CALCULATIONS (using session_state for dpf and filament g/m) ---
    operational_minutes = operational_days * 24 * 60
    annual_production_g = annual_production_ton * 1000 * 1000
    g_per_min = annual_production_g / operational_minutes
    g_per_m = st.session_state.filament_g_per_m  # always use session_state value now!
    filament_m_per_min = g_per_min / g_per_m if g_per_m else 0
    n_filaments_needed = filament_m_per_min / take_up_speed if take_up_speed else 0
    n_spinneret_holes = spinnerets * holes_per_spinneret
    utilization = (n_filaments_needed / n_spinneret_holes) * 100 if n_spinneret_holes else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Dry Fiber Output (g/min)", round(g_per_min, 2))
        st.metric("Filament Linear Density (g/m)", round(g_per_m, 6))
        st.metric("Total Filament Output (m/min)", int(filament_m_per_min))
    with col2:
        st.metric("Filaments Needed", int(n_filaments_needed))
        st.metric("Design Filaments (Spinneret Holes)", n_spinneret_holes)
        st.metric("Utilization (%)", round(utilization, 1))

    # -- Make annual production available to other sections --
    st.session_state.annual_production = annual_production_ton


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

elif selected_section == "Extruder":
    st.header("Extruder Parameters")
    col1, col2 = st.columns(2)
    with col1:
        screw_diameter = st.number_input("Screw Diameter (mm)", min_value=10, value=60, step=5)
        l_d_ratio = st.number_input("L/D Ratio", min_value=10, value=40, step=1)
        motor_power = st.number_input("Motor Power (kW)", min_value=1, value=200, step=10)
        extruder_energy_cost = st.number_input("Extruder Energy/Utility Cost ($/yr)", min_value=0.0, value=float(st.session_state.utility_cost))
    with col2:
        max_rpm = st.number_input("Maximum RPM", min_value=10, value=300, step=10)
        throughput = st.number_input("Throughput (kg/h)", min_value=1, value=500, step=10)
        specific_energy = st.number_input("Specific Energy (kWh/kg)", min_value=0.1, value=0.15, step=0.01)
    st.metric("Screw Length (mm)", screw_diameter * l_d_ratio)
    st.metric("Energy Consumption (kW)", round(throughput * specific_energy, 1))
    st.session_state.utility_cost = extruder_energy_cost

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
    spinneret_hole_radius_cm = spinneret_hole_diameter / 20
    hole_cross_section_cm2 = math.pi * spinneret_hole_radius_cm ** 2
    vol_flow_per_hole_cc_min = solution_cc_per_min / total_holes
    hole_cross_section_m2 = hole_cross_section_cm2 * 1e-4
    vol_flow_per_hole_m3_min = vol_flow_per_hole_cc_min * 1e-6
    vel_leaving_spinneret_m_min = vol_flow_per_hole_m3_min / hole_cross_section_m2 if hole_cross_section_m2 else 0
    solution_draw_ratio = take_up_speed / vel_leaving_spinneret_m_min if vel_leaving_spinneret_m_min else 0
    num_batteries = math.ceil(total_holes / (spinnerets_per_battery * (total_holes / 360))) if spinnerets_per_battery > 0 else 1
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
    power_hexane_evap_kw = hexane_required_kg_hr * 0.5  # Placeholder/simple formula!
    annual_solvent_heat_cost = power_hexane_evap_kw * 7200 * electricity_cost
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Draw Ratio", draw_ratio)
        st.metric("Solvent Removed (kg/min)", round(hexane_required_kg_min, 2))
        st.metric("Hexane Required (kg/hr)", round(hexane_required_kg_hr, 2))
    with col2:
        st.metric("Evaporation Power (kW)", round(power_hexane_evap_kw, 1))
        st.metric("Annual Solvent Heat Cost ($)", round(annual_solvent_heat_cost, 0))

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
    tensile_strength = tenacity * dpf * 0.0882
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Filament Cross-section (cm²)", round(filament_crosssection, 8))
        st.metric("Calculated Linear Density (g/m)", round(filament_g_per_m, 6))
    with col2:
        st.metric("Calculated dpf", round(calculated_dpf, 2))
        st.metric("Tensile Strength (N/tex)", round(tensile_strength, 1))


elif selected_section == "Economic Summary":
    st.header("Profitability & Cost Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_capex = st.number_input("Total Capex ($)", min_value=1.0, value=float(capex_total))
        new_labor = st.number_input("Labor Cost ($/yr)", min_value=0.0, value=float(labor_cost))
        new_utility = st.number_input("Utility Cost ($/yr)", min_value=0.0, value=float(utility_cost))
    with col2:
        new_fiber_price = st.number_input("Fiber Selling Price ($/kg)", min_value=0.01, value=float(fiber_price), step=0.1)
        new_annual_prod = st.number_input("Annual Production (tons)", min_value=1.0, value=float(annual_production))
        new_maintenance = st.number_input("Maintenance Cost ($/yr)", min_value=0.0, value=float(maintenance_cost))
    with col3:
        new_material_cost_kg = st.number_input("Material Cost ($/kg)", min_value=0.01, value=float(material_cost_per_kg), step=0.1)
        new_deprec_yrs = st.number_input("Depreciation Period (years)", min_value=1, value=int(depreciation_years))
        new_other_costs = st.number_input("Other Costs ($/yr)", min_value=0.0, value=float(other_costs))
    st.session_state.capex_total = new_capex
    st.session_state.labor_cost = new_labor
    st.session_state.utility_cost = new_utility
    st.session_state.fiber_price = new_fiber_price
    st.session_state.annual_production = new_annual_prod
    st.session_state.maintenance_cost = new_maintenance
    st.session_state.material_cost_per_kg = new_material_cost_kg
    st.session_state.depreciation_years = new_deprec_yrs
    st.session_state.other_costs = new_other_costs
    st.write("Scroll to the top to see updated schematic and cost breakdown pie chart!")

st.caption("Fiber Production Techno-Economic Analysis Tool v1.0")

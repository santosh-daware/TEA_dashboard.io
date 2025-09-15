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

# -- Default state for top-level visuals (modify to link inputs globally) --
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

# -- Top-level calculations for cost pie and summary visuals --
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
).properties(width=400, height=400, title='Annual Cost Distribution')

# ==== SHOW SCHEMATIC + COST PIE ALWAYS AT TOP ====
colA, colB = st.columns([2, 1])
with colA:
    st.image(
        "https://via.placeholder.com/800x400?text=Fiber+Production+Process+Schematic", 
        use_container_width=True, caption="Fiber Production Process Schematic"
    )
with colB:
    st.altair_chart(pie_chart, use_container_width=True)
    st.metric("Annual Revenue ($)", f"{annual_revenue:,.2f}")
    st.metric("Annual Costs ($)", f"{total_annual_costs:,.2f}")
    st.metric("Annual Profit ($)", f"{annual_profit:,.2f}")
    st.metric("ROI (%)", f"{roi:.1f}")
    st.metric("Payback Period (years)", f"{payback_period:.1f}" if payback_period != float('inf') else "N/A")
    st.metric("Break-even Price ($/kg)", f"{break_even:.2f}")
st.markdown("---")

# ==== APP SECTIONS ====
if selected_section == "Production Capacity":
    st.header("Production Capacity")
    col1, col2 = st.columns(2)
    with col1:
        annual_production_ton = st.number_input("Annual Production (tons/year)", min_value=1, value=int(st.session_state.annual_production))
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
    # Sync annual production to global state so visuals update!
    st.session_state.annual_production = annual_production_ton

# ---- Add other sections here ----

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
    # Sync to state for top-level visuals!
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

# ---- Add your other process sections similarly, following this pattern ----

st.caption("Fiber Production Techno-Economic Analysis Tool v1.0")

import streamlit as st
import math
import pandas as pd
import altair as alt

st.set_page_config(page_title="Fiber Techno-Economic Analysis", layout="wide")
st.title("Techno-Economic Fiber Production Analysis")

sections = [
    "Design Inputs", "Production Capacity", "Solution Preparation", "Spinning",
    "Fiber Property", "Extruder", "Drying", "Raw Materials", "Economic Summary"
]
selected_section = st.radio("Navigate to Section:", sections, horizontal=True)
st.markdown("---")

# ------- UNIVERSAL INPUTS (design parameters) --------
default_params = {
    "annual_production": 250,
    "operational_days": 300,
    "dpf": 3.1,
    "filament_diameter_um": 22.08,
    "filament_density": 0.9,
    "take_up_speed": 100.0,
    "spinnerets": 50,
    "holes_per_spinneret": 360,
    "polymer_wt_frac": 0.1,
    "solution_density": 0.9,
    "material_cost_per_kg": 2.5,
    "solvent_cost_per_kg": 2.0,
    "additive_cost_per_kg": 20.0,
    "additives_kg_yr": 2500,
    "makeup_solvent_ton": 67.5,
    "uhmwpe_use_ton": 250,
    "maintenance_cost": 75000.0,
    "labor_cost": 200000.0,
    "other_costs": 50000.0,
    "capex_total": 915000.0,
    "depreciation_years": 10,
    "fiber_price": 15.0,
    "extruder_power_kw": 200,
    "drying_oven_power_kw": 80,
    "electricity_price": 0.15,
}
for k, v in default_params.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Major flows and calculations
st.session_state['total_holes'] = int(st.session_state['spinnerets']) * int(st.session_state['holes_per_spinneret'])
st.session_state['annual_production_g'] = st.session_state['annual_production'] * 1000 * 1000
st.session_state['annual_production_kg'] = st.session_state['annual_production'] * 1000
st.session_state['operational_minutes'] = st.session_state['operational_days'] * 24 * 60
st.session_state['operational_hours'] = st.session_state['operational_days'] * 24

if st.session_state['operational_minutes'] > 0:
    st.session_state['dry_fiber_g_per_min'] = st.session_state['annual_production_g'] / st.session_state['operational_minutes']
else:
    st.session_state['dry_fiber_g_per_min'] = 0

st.session_state['filament_g_per_m'] = st.session_state['dpf'] / 9000

if st.session_state['polymer_wt_frac'] > 0 and st.session_state['solution_density'] > 0:
    st.session_state['solution_g_per_min'] = st.session_state['dry_fiber_g_per_min'] / st.session_state['polymer_wt_frac']
    st.session_state['solution_cc_per_min'] = st.session_state['solution_g_per_min'] / st.session_state['solution_density']
else:
    st.session_state['solution_g_per_min'] = 0
    st.session_state['solution_cc_per_min'] = 0

if st.session_state['total_holes'] > 0:
    st.session_state['solution_cc_per_min_per_hole'] = st.session_state['solution_cc_per_min'] / st.session_state['total_holes']
else:
    st.session_state['solution_cc_per_min_per_hole'] = 0

# -- Utility/Energy Costs: Only Extruder and Drying Oven --
st.session_state['extruder_utility_cost'] = (
    st.session_state['extruder_power_kw'] *
    st.session_state['operational_hours'] *
    st.session_state['electricity_price']
)
st.session_state['drying_utility_cost'] = (
    st.session_state['drying_oven_power_kw'] *
    st.session_state['operational_hours'] *
    st.session_state['electricity_price']
)
st.session_state['total_utility_cost'] = (
    st.session_state['extruder_utility_cost'] +
    st.session_state['drying_utility_cost']
)

# ---------- TOP: Pie Chart & Metrics -------------
annual_production = st.session_state.annual_production
fiber_price = st.session_state.fiber_price
capex_total = st.session_state.capex_total
depreciation_years = st.session_state.depreciation_years
material_cost_per_kg = st.session_state.material_cost_per_kg
labor_cost = st.session_state.labor_cost
total_utility_cost = st.session_state['total_utility_cost']
maintenance_cost = st.session_state.maintenance_cost
other_costs = st.session_state.other_costs
additive_cost_per_kg = st.session_state.additive_cost_per_kg
solvent_cost_per_kg = st.session_state.solvent_cost_per_kg

material_cost = st.session_state.uhmwpe_use_ton * 1000 * material_cost_per_kg
solvent_cost = st.session_state.makeup_solvent_ton * 1000 * solvent_cost_per_kg
additive_cost = st.session_state.additives_kg_yr * additive_cost_per_kg
total_materials_cost = material_cost + solvent_cost + additive_cost

depreciation_cost = capex_total / depreciation_years
total_annual_costs = (
    total_materials_cost + labor_cost + total_utility_cost
    + maintenance_cost + other_costs + depreciation_cost
)
annual_revenue = annual_production * 1000 * fiber_price
annual_profit = annual_revenue - total_annual_costs
roi = (annual_profit / capex_total * 100) if capex_total else 0
payback_period = capex_total / annual_profit if annual_profit > 0 else float('inf')
break_even = total_annual_costs / (annual_production * 1000) if annual_production > 0 else 0

cost_data = pd.DataFrame({
    'Category': [
        'UHMWPE', 'Solvent', 'Additives', 'Labor',
        'Extruder Energy', 'Drying Energy',
        'Maintenance', 'Other', 'Depreciation'
    ],
    'Amount': [
        material_cost, solvent_cost, additive_cost, labor_cost,
        st.session_state['extruder_utility_cost'],
        st.session_state['drying_utility_cost'],
        maintenance_cost, other_costs, depreciation_cost
    ]
})
pie_chart = alt.Chart(cost_data).mark_arc().encode(
    theta=alt.Theta(field="Amount", type="quantitative"),
    color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme='tableau20')),
    tooltip=['Category', 'Amount']
).properties(width=350, height=350, title='Annual Cost Distribution')

colA, colB = st.columns([1.3, 1])
with colA:
    st.image(
        "Flow_chart.png",
        width=800,
        caption="Fiber Production Process Schematic"
    )
with colB:
    st.altair_chart(pie_chart, use_container_width=True)
    metric_style = """
    <style>
    .small-metric { font-size: 0.92rem; color: #495162; font-weight: 500; margin-bottom: 0.2em; letter-spacing: 0.01em;}
    .small-value { font-size: 1.15rem; color: #034078; font-weight: 700; margin-bottom: 1em; }
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

if selected_section == "Design Inputs":
    st.header("Universal Fiber Line Design Inputs")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['annual_production'] = st.number_input(
            "Annual Production Target (tons/year)", min_value=1.0, value=float(st.session_state['annual_production'])
        )
        st.session_state['operational_days'] = st.number_input(
            "Operational Days per Year", min_value=1, max_value=366, value=int(st.session_state['operational_days'])
        )
        st.session_state['dpf'] = st.number_input(
            "Denier Per Filament (dpf)", min_value=0.01, value=float(st.session_state['dpf']), step=0.01
        )
        st.session_state['filament_diameter_um'] = st.number_input(
            "Filament Diameter (μm)", min_value=1.0, value=float(st.session_state['filament_diameter_um']), step=0.01
        )
        st.session_state['extruder_power_kw'] = st.number_input(
            "Extruder Power (kW)", min_value=1.0, value=float(st.session_state['extruder_power_kw']), step=1.0
        )
    with col2:
        st.session_state['filament_density'] = st.number_input(
            "Filament Density (g/cc)", min_value=0.1, value=float(st.session_state['filament_density']), step=0.01
        )
        st.session_state['take_up_speed'] = st.number_input(
            "Take-up Speed (m/min)", min_value=1.0, value=float(st.session_state['take_up_speed']), step=1.0
        )
        st.session_state['spinnerets'] = st.number_input(
            "Number of Spinnerets", min_value=1, value=int(st.session_state['spinnerets']), step=1
        )
        st.session_state['holes_per_spinneret'] = st.number_input(
            "Holes Per Spinneret", min_value=1, value=int(st.session_state['holes_per_spinneret']), step=1
        )
        st.session_state['polymer_wt_frac'] = st.number_input(
            "Polymer Weight Fraction (g/g)", min_value=0.001, max_value=1.0, value=float(st.session_state['polymer_wt_frac']), step=0.01
        )
        st.session_state['solution_density'] = st.number_input(
            "Solution Density (g/cc)", min_value=0.5, max_value=2.0, value=float(st.session_state['solution_density']), step=0.01
        )
        st.session_state['drying_oven_power_kw'] = st.number_input(
            "Drying Oven Power (kW)", min_value=1.0, value=float(st.session_state['drying_oven_power_kw']), step=1.0
        )
        st.session_state['electricity_price'] = st.number_input(
            "Electricity Price ($/kWh)", min_value=0.01, value=float(st.session_state['electricity_price']), step=0.01
        )

elif selected_section == "Production Capacity":
    st.header("Production Capacity (calculated values only)")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Filament Linear Density (g/m)", round(st.session_state['filament_g_per_m'], 6), "from dpf")
        st.metric("Dry Fiber Output (g/min)", round(st.session_state['dry_fiber_g_per_min'], 2))
    with col2:
        st.metric("Total Filament Output (m/min)", 
                  int(st.session_state['dry_fiber_g_per_min'] / st.session_state['filament_g_per_m']) if st.session_state['filament_g_per_m'] else 0)
        st.metric("Total Spinneret Holes", int(st.session_state['total_holes']))
    st.metric("Take-up Speed (m/min)", st.session_state['take_up_speed'])

elif selected_section == "Solution Preparation":
    st.header("Solution Preparation (auto-calculated from design)")
    st.metric("Solution Flow (g/min)", round(st.session_state['solution_g_per_min'], 2))
    st.metric("Solution Flow (cc/min)", round(st.session_state['solution_cc_per_min'], 2))
    st.metric("Flow per Hole (cc/min)", round(st.session_state['solution_cc_per_min_per_hole'], 6))

elif selected_section == "Spinning":
    st.header("Spinning Section (auto-calculated)")
    st.metric("Total Spinneret Holes", st.session_state['total_holes'])
    st.metric("Take-up Speed (m/min)", st.session_state['take_up_speed'])
    st.metric("Solution Flow per Hole (cc/min/hole)", round(st.session_state['solution_cc_per_min_per_hole'], 6))

elif selected_section == "Fiber Property":
    st.header("Fiber Property Calculations (from design)")
    filament_diameter_cm = st.session_state['filament_diameter_um'] / 10000
    filament_density = st.session_state['filament_density']
    filament_crosssection = math.pi * (filament_diameter_cm/2)**2
    calc_filament_g_per_m = filament_crosssection * 100 * filament_density
    calc_dpf = calc_filament_g_per_m * 9000
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Filament Cross-section (cm²)", round(filament_crosssection, 8))
        st.metric("Calculated Linear Density (g/m)", round(calc_filament_g_per_m, 6))
    with col2:
        st.metric("dpf from geom.", round(calc_dpf, 2))
        st.metric("Design dpf", round(st.session_state['dpf'], 2))

elif selected_section == "Extruder":
    st.header("Extruder Parameters (energy-driven, auto-integrated)")
    st.metric("Extruder Power (kW)", st.session_state['extruder_power_kw'])
    st.metric("Operational Hours per Year", st.session_state['operational_hours'])
    st.metric("Electricity Price ($/kWh)", st.session_state['electricity_price'])
    st.metric("Extruder Utility Cost ($/yr)", round(st.session_state['extruder_utility_cost'], 2))

elif selected_section == "Drying":
    st.header("Drying Oven Energy")
    st.metric("Drying Oven Power (kW)", st.session_state['drying_oven_power_kw'])
    st.metric("Operational Hours per Year", st.session_state['operational_hours'])
    st.metric("Electricity Price ($/kWh)", st.session_state['electricity_price'])
    st.metric("Drying Utility Cost ($/yr)", round(st.session_state['drying_utility_cost'], 2))

elif selected_section == "Raw Materials":
    st.header("Raw Materials & Ingredients (auto from universal values)")
    st.metric("UHMWPE Usage (T/yr)", st.session_state['uhmwpe_use_ton'])
    st.metric("Solvent Makeup (T/yr)", st.session_state['makeup_solvent_ton'])
    st.metric("Additives (kg/yr)", st.session_state['additives_kg_yr'])
    st.metric("Material Cost ($/kg)", st.session_state['material_cost_per_kg'])
    st.metric("Total Material Cost ($/yr)", round(total_materials_cost, 2))

elif selected_section == "Economic Summary":
    st.header("Profitability & Cost Summary (extruder and drying utility included)")
    st.metric("Annual Costs ($)", f"{total_annual_costs:,.2f}")
    st.metric("Annual Revenue ($)", f"{annual_revenue:,.2f}")
    st.metric("Annual Profit ($)", f"{annual_profit:,.2f}")
    st.metric("ROI (%)", f"{roi:.1f}")
    st.metric("Payback Period (years)", f"{payback_period:.1f}")



)

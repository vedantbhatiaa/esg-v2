"""
ESG KPI Calculations — TIP ESG Platform V2
Exact port of formula_engine.py from the Streamlit app.
Field names match what Entry.vue submits and data_loader.py stores.
"""

# ── Emission factors (T.CO₂ per GJ LHV) — from formula_engine.py
EF = {
    "nat_gas_gj":        0.0561,   # Natural Gas
    "coal_gj":           0.0961,   # Coal
    "propane_gj":        0.0631,   # Propane
    "fuel_oil_gj":       0.0774,   # Fuel Oil
    "diesel_gj":         0.0741,   # Diesel
    "petrol_gj":         0.0693,   # Petrol
    "biomass_gj":        0.0,      # Biomass (biogenic, excluded)
    "waste_tires_gj":    0.0475,   # Waste tires (already in GJ via HV)
    "lpg_gj":            0.0561,   # LPG
    "other_fuel_gj":     0.0719,   # Other
}

WASTE_TIRE_HV       = 36.23   # GJ per metric tonne of waste tires
SCOPE2_ELEC_EF      = 0.125   # T.CO₂/GJ = 0.45 T.CO₂/MWh ÷ 3.6 (EU avg, from formula_engine.py)
GJ_TO_MWH           = 1 / 3.6


def _f(data: dict, key: str, default: float = 0.0) -> float:
    """Safe float extraction."""
    try:
        return float(data.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def calculate_all_kpis(data: dict) -> dict:
    """
    Master KPI calculation — exact port of formula_engine.calculate().
    Accepts the field names used by Entry.vue form and data_loader._COL_MAP.
    """
    production = max(_f(data, "production_t"), 1)

    # ── Electricity
    renew_elec    = _f(data, "renew_elec_gj")
    nonrenew_elec = _f(data, "nonrenew_elec_gj")
    self_gen      = _f(data, "self_gen_elec_gj")
    total_elec    = renew_elec + nonrenew_elec + self_gen

    # ── Steam & sold
    purchased_steam  = _f(data, "purchased_steam_gj")
    sold_elec        = _f(data, "sold_elec_gj")
    sold_steam       = _f(data, "sold_steam_gj")

    # ── Fuels
    nat_gas     = _f(data, "nat_gas_gj")
    coal        = _f(data, "coal_gj")
    propane     = _f(data, "propane_gj")
    fuel_oil    = _f(data, "fuel_oil_gj")
    diesel      = _f(data, "diesel_gj")
    petrol      = _f(data, "petrol_gj")
    biomass     = _f(data, "biomass_gj")
    lpg         = _f(data, "lpg_gj")
    other_fuel  = _f(data, "other_fuel_gj")

    # Waste tires: input may be in metric tonnes → convert to GJ
    waste_tires_t  = _f(data, "waste_tires_t")
    waste_tires_gj = _f(data, "waste_tires_gj") or (waste_tires_t * WASTE_TIRE_HV)

    # ── Total energy (GJ)
    total_energy = (
        total_elec + purchased_steam
        + nat_gas + coal + propane + fuel_oil + diesel
        + petrol + biomass + waste_tires_gj + lpg + other_fuel
        - sold_elec - sold_steam
    )

    # ── CO₂ Scope 1 (direct combustion)
    scope1 = (
        nat_gas   * EF["nat_gas_gj"]
        + coal      * EF["coal_gj"]
        + propane   * EF["propane_gj"]
        + fuel_oil  * EF["fuel_oil_gj"]
        + diesel    * EF["diesel_gj"]
        + petrol    * EF["petrol_gj"]
        + biomass   * EF["biomass_gj"]
        + waste_tires_gj * EF["waste_tires_gj"]
        + lpg       * EF["lpg_gj"]
        + other_fuel* EF["other_fuel_gj"]
    )

    # ── CO₂ Scope 2 (purchased energy)
    # nonrenew_elec is in GJ; convert to MWh then × 0.45 T.CO₂/MWh
    scope2_elec  = (nonrenew_elec * GJ_TO_MWH) * (SCOPE2_ELEC_EF / GJ_TO_MWH)  # = nonrenew_elec * 0.125
    scope2_steam = _f(data, "co2_scope2_steam")   # company-provided T.CO₂
    scope2       = scope2_elec + scope2_steam
    total_co2    = scope1 + scope2

    # ── Water
    water        = _f(data, "total_water_m3")

    # ── Waste
    waste_total    = _f(data, "waste_total_t")
    waste_recovery = _f(data, "waste_recovered_t")

    # ── ISO 14001
    iso_total     = int(_f(data, "total_sites"))
    iso_certified = int(_f(data, "iso_sites"))

    # ── KPI ratios
    def sdiv(a, b): return round(a / b, 4) if b else 0.0

    energy_kpi         = sdiv(total_energy, production)
    co2_kpi            = sdiv(total_co2, production)
    water_kpi          = sdiv(water, production)
    renewable_share    = sdiv(renew_elec + self_gen, max(total_elec, 1)) * 100
    waste_recovery_pct = sdiv(waste_recovery, waste_total) * 100 if waste_total > 0 else 0.0
    iso_certified_pct  = sdiv(iso_certified, iso_total) * 100 if iso_total > 0 else 0.0

    return {
        # Totals
        "total_energy_gj":      round(total_energy, 2),
        "total_elec_gj":        round(total_elec, 2),
        "scope1_co2_t":         round(scope1, 2),
        "scope2_co2_t":         round(scope2, 2),
        "total_co2_t":          round(total_co2, 2),
        "total_water_m3":       round(water, 2),
        "waste_total_t":        round(waste_total, 2),
        "waste_recovered_t":    round(waste_recovery, 2),
        "production_t":         round(production, 2),
        # KPIs
        "energy_kpi":           round(energy_kpi, 4),
        "co2_kpi":              round(co2_kpi, 6),
        "water_kpi":            round(water_kpi, 4),
        "renewable_share_pct":  round(renewable_share, 2),
        "waste_recovery_pct":   round(waste_recovery_pct, 2),
        "iso_certified_pct":    round(iso_certified_pct, 2),
    }


def calculate_yoy_change(current_val: float, prior_val: float) -> dict:
    """Returns YoY change % and direction."""
    if not prior_val or prior_val == 0:
        return {"pct": None, "direction": "neutral"}
    pct = round(((current_val - prior_val) / abs(prior_val)) * 100, 1)
    return {"pct": pct, "direction": "down" if pct < 0 else "up" if pct > 0 else "neutral"}


def calculate_yoy_all(current_kpis: dict, prior_kpis: dict) -> dict:
    """YoY delta for all KPIs."""
    fields = [
        "energy_kpi", "co2_kpi", "water_kpi",
        "renewable_share_pct", "waste_recovery_pct", "iso_certified_pct",
        "total_energy_gj", "total_co2_t", "total_water_m3",
    ]
    return {f: calculate_yoy_change(current_kpis.get(f, 0), prior_kpis.get(f, 0)) for f in fields}
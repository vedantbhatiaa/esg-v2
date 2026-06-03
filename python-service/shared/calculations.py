"""
ESG KPI Calculations
Extracted from original Streamlit app.py
All formulas unchanged - this is the same logic, just importable.
"""


def calculate_all_kpis(data: dict) -> dict:
    """
    Master KPI calculation function.
    Takes raw form data dict, returns all computed KPIs.
    """
    prod = float(data.get("production_volume", 1))

    # ── Energy totals ──────────────────────────────────────────────
    renew_elec   = float(data.get("renew_elec_purchased", 0))
    nonrenew_elec = float(data.get("nonrenew_elec", 0))
    self_gen     = float(data.get("self_gen_renew", 0))
    steam        = float(data.get("purchased_steam", 0))
    nat_gas      = float(data.get("nat_gas", 0))
    lpg          = float(data.get("lpg", 0))
    coal         = float(data.get("coal", 0))
    fuel_oil     = float(data.get("fuel_oil", 0))
    diesel       = float(data.get("diesel", 0))
    petrol       = float(data.get("petrol", 0))
    biomass      = float(data.get("biomass", 0))
    waste_tires  = float(data.get("waste_tires", 0))
    lpg2         = float(data.get("lpg2", 0))
    other_fuel   = float(data.get("other_fuel", 0))

    total_elec      = renew_elec + nonrenew_elec + self_gen
    total_fossil    = nat_gas + lpg + coal + fuel_oil + diesel + petrol + biomass + waste_tires + lpg2 + other_fuel
    total_energy    = total_elec + steam + total_fossil

    # ── CO2 ────────────────────────────────────────────────────────
    # Scope 1: from direct combustion (calculated from fuel emission factors)
    # Scope 2: from purchased electricity + purchased steam
    scope2_elec  = nonrenew_elec * 0.0000647  # tCO2/GJ avg grid factor
    scope2_steam = float(data.get("co2_scope2_steam", 0))
    scope2_total = scope2_elec + scope2_steam

    # Scope 1 from fuels (IPCC 2006 factors, GJ LHV basis)
    scope1_nat_gas  = nat_gas  * 0.0000561
    scope1_lpg      = (lpg + lpg2) * 0.0000631
    scope1_coal     = coal     * 0.0000946
    scope1_fuel_oil = fuel_oil * 0.0000772
    scope1_diesel   = diesel   * 0.0000741
    scope1_petrol   = petrol   * 0.0000693
    scope1_total    = scope1_nat_gas + scope1_lpg + scope1_coal + scope1_fuel_oil + scope1_diesel + scope1_petrol

    total_co2 = scope1_total + scope2_total

    # ── Water ──────────────────────────────────────────────────────
    water = float(data.get("water_withdrawals", 0))

    # ── Waste ──────────────────────────────────────────────────────
    waste_total    = float(data.get("waste_total", 0))
    waste_recovery = float(data.get("waste_recovery", 0))

    # ── ISO ────────────────────────────────────────────────────────
    iso_total     = int(data.get("iso_total_sites", 0))
    iso_certified = int(data.get("iso_certified_sites", 0))

    # ── KPI ratios ─────────────────────────────────────────────────
    energy_kpi       = round(total_energy / prod, 2)      if prod > 0 else 0
    co2_kpi          = round(total_co2 / prod, 4)         if prod > 0 else 0
    water_kpi        = round(water / prod, 2)             if prod > 0 else 0
    renewable_share  = round(renew_elec / total_elec * 100, 1) if total_elec > 0 else 0
    waste_recovery_rate = round(waste_recovery / waste_total * 100, 1) if waste_total > 0 else 0
    iso_pct          = round(iso_certified / iso_total * 100, 1) if iso_total > 0 else 0

    return {
        # Raw totals
        "total_energy_gj":      round(total_energy, 0),
        "total_elec_gj":        round(total_elec, 0),
        "total_fossil_gj":      round(total_fossil, 0),
        "total_co2_t":          round(total_co2, 0),
        "scope1_co2_t":         round(scope1_total, 0),
        "scope2_co2_t":         round(scope2_total, 0),
        "total_water_m3":       round(water, 0),
        "total_waste_t":        round(waste_total, 0),
        "waste_recovered_t":    round(waste_recovery, 0),
        "production_t":         round(prod, 0),
        # KPIs
        "energy_kpi":           energy_kpi,
        "co2_kpi":              co2_kpi,
        "water_kpi":            water_kpi,
        "renewable_share_pct":  renewable_share,
        "waste_recovery_pct":   waste_recovery_rate,
        "iso_certified_pct":    iso_pct,
    }


def calculate_yoy_change(current_val: float, prior_val: float) -> dict:
    """Returns YoY change % and direction."""
    if prior_val == 0:
        return {"pct": None, "direction": "neutral"}
    pct = round(((current_val - prior_val) / abs(prior_val)) * 100, 1)
    direction = "down" if pct < 0 else "up" if pct > 0 else "neutral"
    return {"pct": pct, "direction": direction}


def calculate_yoy_all(current_kpis: dict, prior_kpis: dict) -> dict:
    """YoY delta for all KPIs."""
    fields = [
        "energy_kpi", "co2_kpi", "water_kpi",
        "renewable_share_pct", "waste_recovery_pct", "iso_certified_pct",
        "total_energy_gj", "total_co2_t", "total_water_m3",
    ]
    result = {}
    for f in fields:
        result[f] = calculate_yoy_change(
            current_kpis.get(f, 0),
            prior_kpis.get(f, 0)
        )
    return result

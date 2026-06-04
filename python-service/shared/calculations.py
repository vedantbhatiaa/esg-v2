"""
calculations.py — TIP ESG Platform V2
Exact port of formula_engine.py from Streamlit.
Field names match TemplateInputs (production, nat_gas, water_withdrawals etc).
"""

# Emission factors (T.CO2 per GJ LHV) - exact from formula_engine.py
EF = {
    "nat_gas":          0.0561,
    "coal_sub":         0.0961,
    "propane":          0.0631,
    "fuel_oil_heavy_a": 0.0774,
    "diesel":           0.0741,
    "petrol":           0.0693,
    "biomass":          0.0,
    "waste_tires_gj":   0.0475,
    "lpg":              0.0561,
    "other_fuels":      0.0719,
}

WASTE_TIRE_HV        = 36.23    # GJ per metric tonne
SCOPE2_ELEC_EF       = 0.45     # T.CO2/MWh (EU average)
GJ_TO_MWH            = 1 / 3.6

def _f(data, key, d=0.0):
    try: return float(data.get(key, d) or d)
    except: return d

def calculate_all_kpis(data: dict) -> dict:
    """
    Exact port of formula_engine.calculate().
    data: uses Streamlit TemplateInputs field names.
    Returns: dict with co2_kpi, energy_kpi, water_kpi etc.
    """
    prod    = max(_f(data,"production"), 1)

    # Electricity
    renew   = _f(data,"renew_elec_purchased")
    nonrenew= _f(data,"nonrenew_elec_purchased")
    self_gen= _f(data,"self_gen_elec")
    total_elec = renew + nonrenew + self_gen

    # Steam & sold
    steam   = _f(data,"purchased_steam")
    sold_e  = _f(data,"sold_electricity")
    sold_s  = _f(data,"sold_steam")

    # Fuels (input in GJ LHV except waste_tires_mt in metric T)
    nat_gas = _f(data,"nat_gas")
    coal    = _f(data,"coal_sub")
    prop    = _f(data,"propane")
    fo      = _f(data,"fuel_oil_heavy_a")
    diesel  = _f(data,"diesel")
    petrol  = _f(data,"petrol")
    biomass = _f(data,"biomass")
    lpg     = _f(data,"lpg")
    other   = _f(data,"other_fuels")

    # Waste tires: metric T → GJ
    wt_mt   = _f(data,"waste_tires_mt")
    wt_gj   = wt_mt * WASTE_TIRE_HV

    # Total energy (GJ)
    total_energy = (
        total_elec + steam
        + nat_gas + coal + prop + fo + diesel + petrol
        + biomass + wt_gj + lpg + other
        - sold_e - sold_s
    )

    # CO2 Scope 1 (direct combustion)
    scope1 = (
        nat_gas * EF["nat_gas"]
        + coal   * EF["coal_sub"]
        + prop   * EF["propane"]
        + fo     * EF["fuel_oil_heavy_a"]
        + diesel * EF["diesel"]
        + petrol * EF["petrol"]
        + biomass* EF["biomass"]
        + wt_gj  * EF["waste_tires_gj"]
        + lpg    * EF["lpg"]
        + other  * EF["other_fuels"]
    )

    # CO2 Scope 2 (purchased electricity + steam)
    # nonrenew in GJ → MWh → T.CO2
    scope2_elec  = (nonrenew * GJ_TO_MWH) * SCOPE2_ELEC_EF
    scope2_steam = _f(data,"co2_scope2_steam")
    scope2       = scope2_elec + scope2_steam
    total_co2    = scope1 + scope2

    # Water
    water = _f(data,"water_withdrawals")

    # Waste
    waste_total    = _f(data,"waste_total")
    waste_recovery = _f(data,"waste_recovery")

    # ISO
    iso_total = int(_f(data,"total_sites"))
    iso_cert  = int(_f(data,"iso_sites"))

    def sdiv(a,b): return round(a/b,6) if b else 0.0

    renew_share    = sdiv(renew+self_gen, max(total_elec,1)) * 100
    waste_recov_pct= sdiv(waste_recovery, waste_total) * 100 if waste_total>0 else 0.0
    iso_pct        = sdiv(iso_cert, iso_total) * 100 if iso_total>0 else 0.0

    return {
        # Same names as TemplateOutputs fields used in Streamlit
        "total_electricity":  round(total_elec,2),
        "waste_tires_gj":     round(wt_gj,2),
        "total_energy":       round(total_energy,2),
        "energy_kpi":         round(sdiv(total_energy,prod),4),
        "co2_nat_gas":        round(nat_gas*EF["nat_gas"],2),
        "co2_coal":           round(coal*EF["coal_sub"],2),
        "co2_propane":        round(prop*EF["propane"],2),
        "co2_fuel_oil":       round(fo*EF["fuel_oil_heavy_a"],2),
        "co2_diesel":         round(diesel*EF["diesel"],2),
        "co2_petrol":         round(petrol*EF["petrol"],2),
        "co2_biomass":        round(biomass*EF["biomass"],2),
        "co2_waste_tires":    round(wt_gj*EF["waste_tires_gj"],2),
        "co2_lpg":            round(lpg*EF["lpg"],2),
        "co2_other":          round(other*EF["other_fuels"],2),
        "scope1":             round(scope1,2),
        "scope2":             round(scope2,2),
        "total_co2":          round(total_co2,2),
        "co2_kpi":            round(sdiv(total_co2,prod),6),
        "water_kpi":          round(sdiv(water,prod),4),
        "waste_elimination":  round(waste_total-waste_recovery,2),
        "waste_recov_pct":    round(waste_recov_pct,2),
        "pct_certified":      round(sdiv(iso_cert,iso_total),4),
        "renew_share_pct":    round(renew_share,2),
        "iso_pct":            round(iso_pct,2),
    }

def calculate_yoy(current, prior):
    if not prior or prior==0: return {"pct":None,"direction":"neutral"}
    pct = round(((current-prior)/abs(prior))*100,1)
    return {"pct":pct,"direction":"down" if pct<0 else "up" if pct>0 else "neutral"}

def calculate_yoy_all(cur_kpis, prior_kpis):
    fields=["energy_kpi","co2_kpi","water_kpi","renew_share_pct","waste_recov_pct","total_energy","total_co2"]
    return {f:calculate_yoy(cur_kpis.get(f,0),prior_kpis.get(f,0)) for f in fields}
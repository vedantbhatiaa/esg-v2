"""
ESG Data Verification & Flag Rules
Replicates the verification logic from the original Streamlit app.
"""

WARNING_THRESHOLD = 15   # % YoY change triggers warning
ERROR_THRESHOLD   = 30   # % YoY change triggers error


def check_yoy_flags(current: dict, prior: dict) -> list:
    """
    Checks all KPIs for YoY anomalies.
    Returns list of flag dicts with severity, field, and detail.
    """
    flags = []

    kpi_labels = {
        "energy_kpi":          "Energy Intensity (GJ/T)",
        "co2_kpi":             "CO2 Intensity (T.CO2/T)",
        "water_kpi":           "Water Intensity (m3/T)",
        "renewable_share_pct": "Renewable Electricity Share (%)",
        "waste_recovery_pct":  "Waste Recovery Rate (%)",
        "total_energy_gj":     "Total Energy (GJ)",
        "total_co2_t":         "Total CO2 (T)",
        "total_water_m3":      "Total Water Withdrawals (m3)",
    }

    for field, label in kpi_labels.items():
        curr_val  = current.get(field)
        prior_val = prior.get(field)

        if curr_val is None or prior_val is None or prior_val == 0:
            continue

        pct_change = ((curr_val - prior_val) / abs(prior_val)) * 100

        if abs(pct_change) > ERROR_THRESHOLD:
            flags.append({
                "field":      field,
                "label":      label,
                "severity":   "error",
                "pct_change": round(pct_change, 1),
                "current":    curr_val,
                "prior":      prior_val,
                "threshold":  ERROR_THRESHOLD,
                "message":    f"{label} changed {pct_change:+.1f}% YoY — exceeds ±{ERROR_THRESHOLD}% error threshold",
            })
        elif abs(pct_change) > WARNING_THRESHOLD:
            flags.append({
                "field":      field,
                "label":      label,
                "severity":   "warning",
                "pct_change": round(pct_change, 1),
                "current":    curr_val,
                "prior":      prior_val,
                "threshold":  WARNING_THRESHOLD,
                "message":    f"{label} changed {pct_change:+.1f}% YoY — exceeds ±{WARNING_THRESHOLD}% warning threshold",
            })

    # ── Logical checks ─────────────────────────────────────────────
    iso_cert  = current.get("_raw_iso_certified", 0)
    iso_total = current.get("_raw_iso_total", 0)
    if iso_total > 0 and iso_cert > iso_total:
        flags.append({
            "field":    "iso_sites",
            "label":    "ISO 14001 Sites",
            "severity": "error",
            "message":  f"Certified sites ({iso_cert}) exceeds total sites ({iso_total}) — logical impossibility",
            "current":  iso_cert,
            "prior":    iso_total,
        })

    renew_share = current.get("renewable_share_pct", 0)
    if renew_share > 100:
        flags.append({
            "field":    "renewable_share_pct",
            "label":    "Renewable Share",
            "severity": "error",
            "message":  f"Renewable share ({renew_share}%) exceeds 100% — check electricity inputs",
        })

    waste_rate = current.get("waste_recovery_pct", 0)
    if waste_rate > 100:
        flags.append({
            "field":    "waste_recovery_pct",
            "label":    "Waste Recovery Rate",
            "severity": "error",
            "message":  f"Waste recovery rate ({waste_rate}%) exceeds 100% — check waste inputs",
        })

    return flags


def get_submission_status(flags: list) -> str:
    """Returns 'error', 'warning', or 'ok'."""
    severities = [f["severity"] for f in flags]
    if "error" in severities:
        return "error"
    if "warning" in severities:
        return "warning"
    return "ok"

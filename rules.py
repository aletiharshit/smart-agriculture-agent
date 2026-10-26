"""
Rule-Based Reasoning Engine for Smart Agriculture Agent
Provides transparent, deterministic IF-THEN expert rules grounded in verified
agronomic guidelines for Rice, Wheat, Maize, Cotton, and Tomato across 4 growth stages.
"""

from typing import Dict, Any, List, Optional, Tuple

# Agronomic thresholds based on standard agricultural extension guidelines
CROP_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "Rice": {
        "description": "Semi-aquatic cereal crop requiring elevated moisture regimes, especially during vegetative tillering and panicle development.",
        "temp_min": 20.0,
        "temp_max": 34.0,
        "stages": {
            "Germination / Seedling": {"moisture_min": 55.0, "moisture_max": 75.0},
            "Vegetative": {"moisture_min": 70.0, "moisture_max": 90.0},
            "Flowering / Reproductive": {"moisture_min": 75.0, "moisture_max": 92.0},
            "Maturity / Harvest": {"moisture_min": 35.0, "moisture_max": 55.0},
        },
        "critical_stage": "Flowering / Reproductive",
        "drought_sensitivity": "Very High",
        "drainage_note": "Drain standing water 10-14 days before harvest to facilitate uniform grain maturation."
    },
    "Wheat": {
        "description": "Temperate cool-season cereal sensitive to waterlogging and terminal heat stress during grain filling.",
        "temp_min": 12.0,
        "temp_max": 26.0,
        "stages": {
            "Germination / Seedling": {"moisture_min": 45.0, "moisture_max": 60.0},
            "Vegetative": {"moisture_min": 50.0, "moisture_max": 65.0},
            "Flowering / Reproductive": {"moisture_min": 55.0, "moisture_max": 70.0},
            "Maturity / Harvest": {"moisture_min": 30.0, "moisture_max": 48.0},
        },
        "critical_stage": "Flowering / Reproductive",
        "drought_sensitivity": "Medium-High",
        "drainage_note": "Highly susceptible to root rot if soil moisture exceeds 75% for more than 24 hours."
    },
    "Maize": {
        "description": "C4 cereal with moderate water requirements, exceptionally vulnerable to drought during tasseling and silking.",
        "temp_min": 18.0,
        "temp_max": 33.0,
        "stages": {
            "Germination / Seedling": {"moisture_min": 50.0, "moisture_max": 65.0},
            "Vegetative": {"moisture_min": 55.0, "moisture_max": 72.0},
            "Flowering / Reproductive": {"moisture_min": 60.0, "moisture_max": 78.0},
            "Maturity / Harvest": {"moisture_min": 35.0, "moisture_max": 52.0},
        },
        "critical_stage": "Flowering / Reproductive",
        "drought_sensitivity": "High during silking",
        "drainage_note": "Adequate aeration is essential; waterlogging impairs nitrogen assimilation."
    },
    "Cotton": {
        "description": "Deep-rooted warm-season fiber crop requiring balanced irrigation; sensitive to boll shedding under both moisture deficit and excess.",
        "temp_min": 21.0,
        "temp_max": 35.0,
        "stages": {
            "Germination / Seedling": {"moisture_min": 40.0, "moisture_max": 55.0},
            "Vegetative": {"moisture_min": 48.0, "moisture_max": 65.0},
            "Flowering / Reproductive": {"moisture_min": 55.0, "moisture_max": 72.0},
            "Maturity / Harvest": {"moisture_min": 30.0, "moisture_max": 48.0},
        },
        "critical_stage": "Flowering / Reproductive",
        "drought_sensitivity": "Medium",
        "drainage_note": "Excess moisture during boll opening promotes boll rot and compromises lint quality."
    },
    "Tomato": {
        "description": "High-value solanaceous vegetable requiring consistent moisture to prevent blossom-end rot and fruit cracking.",
        "temp_min": 18.0,
        "temp_max": 29.0,
        "stages": {
            "Germination / Seedling": {"moisture_min": 55.0, "moisture_max": 70.0},
            "Vegetative": {"moisture_min": 60.0, "moisture_max": 75.0},
            "Flowering / Reproductive": {"moisture_min": 65.0, "moisture_max": 80.0},
            "Maturity / Harvest": {"moisture_min": 45.0, "moisture_max": 62.0},
        },
        "critical_stage": "Flowering / Reproductive",
        "drought_sensitivity": "High",
        "drainage_note": "Moisture fluctuations cause calcium uptake failure leading to blossom-end rot."
    }
}


def evaluate_conditions(
    crop_type: str,
    growth_stage: str,
    soil_moisture: float,
    temperature: float
) -> Dict[str, Any]:
    """
    Executes deterministic IF-THEN agronomic rules.
    Compares real observed field values with crop-specific threshold boundaries.
    
    Returns a comprehensive advisory dictionary containing:
    - status: 'Optimal' | 'Needs Attention' | 'Critical Action Required'
    - status_color: Hex color code matching nature-inspired palette
    - status_badge: Descriptive text label
    - action_title: Concise headline recommendation
    - moisture_state: 'Deficit' | 'Optimal' | 'Excess'
    - temp_state: 'Cold Stress' | 'Optimal' | 'Heat Stress'
    - reasoning: Detailed agronomic explanation
    - practical_steps: Actionable bullet list for field implementation
    - optimal_moisture_range: Tuple (min, max)
    - optimal_temp_range: Tuple (min, max)
    """
    crop_info = CROP_THRESHOLDS.get(crop_type, CROP_THRESHOLDS["Maize"])
    stage_info = crop_info["stages"].get(
        growth_stage,
        {"moisture_min": 50.0, "moisture_max": 70.0}
    )

    opt_m_min = stage_info["moisture_min"]
    opt_m_max = stage_info["moisture_max"]
    opt_t_min = crop_info["temp_min"]
    opt_t_max = crop_info["temp_max"]

    moisture_diff = 0.0
    moisture_state = "Optimal"
    moisture_severity = "normal"  # normal, mild, critical

    # --- Rule Evaluation: Soil Moisture ---
    if soil_moisture < opt_m_min:
        moisture_state = "Deficit"
        moisture_diff = opt_m_min - soil_moisture
        if moisture_diff > 15.0 or (growth_stage == crop_info["critical_stage"] and moisture_diff > 8.0):
            moisture_severity = "critical"
        else:
            moisture_severity = "mild"
    elif soil_moisture > opt_m_max:
        moisture_state = "Excess"
        moisture_diff = soil_moisture - opt_m_max
        if moisture_diff > 15.0:
            moisture_severity = "critical"
        else:
            moisture_severity = "mild"
    else:
        moisture_state = "Optimal"
        moisture_severity = "normal"

    # --- Rule Evaluation: Ambient Temperature ---
    temp_state = "Optimal"
    temp_severity = "normal"

    if temperature < opt_t_min:
        temp_state = "Cold Stress"
        if (opt_t_min - temperature) > 6.0:
            temp_severity = "critical"
        else:
            temp_severity = "mild"
    elif temperature > opt_t_max:
        temp_state = "Heat Stress"
        if (temperature - opt_t_max) > 5.0 or (growth_stage == crop_info["critical_stage"] and (temperature - opt_t_max) > 3.0):
            temp_severity = "critical"
        else:
            temp_severity = "mild"
    else:
        temp_state = "Optimal"
        temp_severity = "normal"

    # --- Synthesis & Priority Status Determination ---
    practical_steps: List[str] = []
    reasoning_points: List[str] = []

    # Priority 1: Critical Condition
    if moisture_severity == "critical" or temp_severity == "critical":
        status = "Critical Action Required"
        status_color = "#b91c1c"  # Deep red / crimson
        status_badge = "Urgent Attention Needed"
    # Priority 2: Needs Attention
    elif moisture_severity == "mild" or temp_severity == "mild":
        status = "Needs Attention"
        status_color = "#d97706"  # Earthy Amber / Ochre
        status_badge = "Advisory Alert"
    # Priority 3: Optimal Conditions
    else:
        status = "Optimal"
        status_color = "#2d6a4f"  # Forest green
        status_badge = "Field Conditions Balanced"

    # --- Action Headline & Diagnostic Reasoning ---
    action_title = ""

    # Soil Moisture Diagnostic & Guidance
    if moisture_state == "Deficit":
        if moisture_severity == "critical":
            action_title = "Immediate Deep Irrigation Required"
            reasoning_points.append(
                f"Severe soil moisture deficit: Observed {soil_moisture:.1f}% is {moisture_diff:.1f}% below the required minimum of {opt_m_min:.1f}% for {crop_type} at the {growth_stage} stage."
            )
            if growth_stage == crop_info["critical_stage"]:
                reasoning_points.append(
                    f"CRITICAL WARNING: The {growth_stage} phase is the highest-sensitivity reproductive window. Prolonged water stress will cause irreversible yield reduction."
                )
            practical_steps.append(f"Initiate deep irrigation immediately: target 35–45 mm application via drip or furrow system.")
            practical_steps.append("Check root zone at 15–20 cm depth before and after irrigation to confirm moisture penetration.")
        else:
            action_title = "Schedule Supplementary Irrigation"
            reasoning_points.append(
                f"Mild moisture deficit: Observed {soil_moisture:.1f}% is slightly below the target range ({opt_m_min:.0f}%–{opt_m_max:.0f}%)."
            )
            practical_steps.append(f"Schedule light supplemental irrigation (20–25 mm) during early morning or late evening hours to minimize evaporative loss.")
            practical_steps.append("Re-inspect soil moisture sensors within 12 hours.")

    elif moisture_state == "Excess":
        if moisture_severity == "critical":
            action_title = "Waterlogging Danger: Cease Irrigation & Drain Furrows"
            reasoning_points.append(
                f"Critical saturation: Observed moisture ({soil_moisture:.1f}%) exceeds the safe upper bound ({opt_m_max:.1f}%) by {moisture_diff:.1f}%. Anaerobic root zone conditions threaten root asphyxiation and damping-off pathogens."
            )
            practical_steps.append("Immediately suspend all scheduled irrigation cycles.")
            practical_steps.append("Inspect drainage trenches and furrow outlets; clear blockages to evacuate standing surface water.")
            practical_steps.append("Monitor for fungal symptoms (e.g., Phytophthora or root rot) once drainage recedes.")
        else:
            action_title = "Moisture Elevated: Pause Irrigation"
            reasoning_points.append(
                f"Moisture reading ({soil_moisture:.1f}%) is moderately above the optimal ceiling ({opt_m_max:.1f}%). Root oxygenation remains adequate but further watering is counterproductive."
            )
            practical_steps.append("Withhold irrigation until soil naturally dries back into the optimal range.")
            practical_steps.append("Ensure field soil surface has adequate air circulation.")

    else:
        # Moisture is optimal
        if temp_state == "Optimal":
            action_title = "Conditions Ideal: Maintain Current Field Regimen"
            reasoning_points.append(
                f"Soil moisture ({soil_moisture:.1f}%) is in the optimal agronomic band ({opt_m_min:.0f}%–{opt_m_max:.0f}%) for {crop_type} during {growth_stage}."
            )
            practical_steps.append("Continue standard baseline irrigation schedule.")
            practical_steps.append("Conduct routine visual scout for pests and nutrient leaf symptoms.")
        else:
            action_title = "Moisture Optimal: Manage Ambient Temperature Stress"
            reasoning_points.append(
                f"Soil moisture ({soil_moisture:.1f}%) is balanced within the optimal {opt_m_min:.0f}%–{opt_m_max:.0f}% range."
            )

    # Temperature Diagnostic & Guidance
    if temp_state == "Heat Stress":
        reasoning_points.append(
            f"Thermal stress alert: Current temperature ({temperature:.1f}°C) exceeds the optimal threshold ceiling ({opt_t_max:.1f}°C) for {crop_type}."
        )
        if growth_stage == "Flowering / Reproductive":
            reasoning_points.append(
                "High temperature during flowering accelerates pollen desiccation and reduces fruit/grain set."
            )
        practical_steps.append("Apply organic straw mulch (5–8 cm depth) across exposed beds to lower soil temperature and conserve root moisture.")
        if crop_type in ["Tomato", "Cotton"]:
            practical_steps.append("If feasible, deploy 35% shade netting or overhead micro-sprinklers for evaporative canopy cooling during peak solar hours (12:00 PM – 3:30 PM).")
    elif temp_state == "Cold Stress":
        reasoning_points.append(
            f"Low temperature alert: Observed temperature ({temperature:.1f}°C) is below the growth threshold ({opt_t_min:.1f}°C) for {crop_type}."
        )
        practical_steps.append("Minimize cold damage: Avoid late-evening overhead sprinkling.")
        practical_steps.append("Deploy row covers or low plastic tunnels if temperature is forecast to drop further.")
    else:
        reasoning_points.append(
            f"Ambient temperature ({temperature:.1f}°C) is within the safe metabolic range ({opt_t_min:.0f}°C–{opt_t_max:.0f}°C)."
        )

    # Growth stage specific notes
    if growth_stage == "Maturity / Harvest":
        practical_steps.append(crop_info["drainage_note"])

    # Combine reasoning into structured narrative
    reasoning_text = " • ".join(reasoning_points)

    return {
        "status": status,
        "status_color": status_color,
        "status_badge": status_badge,
        "action_title": action_title,
        "moisture_state": moisture_state,
        "temp_state": temp_state,
        "reasoning": reasoning_text,
        "practical_steps": practical_steps,
        "optimal_moisture_range": (opt_m_min, opt_m_max),
        "optimal_temp_range": (opt_t_min, opt_t_max),
        "crop_description": crop_info["description"],
        "crop_context": crop_info["description"]
    }


def get_optimal_moisture_band(crop: str, stage: str = "Vegetative") -> Tuple[float, float]:
    """Returns (min_moisture, max_moisture) for the specified crop and growth stage."""
    crop_info = CROP_THRESHOLDS.get(crop, CROP_THRESHOLDS.get("Tomato", {}))
    stages = crop_info.get("stages", {})
    stage_info = stages.get(stage, next(iter(stages.values()), {"moisture_min": 50.0, "moisture_max": 75.0}))
    return (float(stage_info["moisture_min"]), float(stage_info["moisture_max"]))


def get_safe_temp_range(crop: str) -> Tuple[float, float]:
    """Returns (min_temp, max_temp) for the specified crop."""
    crop_info = CROP_THRESHOLDS.get(crop, CROP_THRESHOLDS.get("Tomato", {}))
    return (float(crop_info.get("temp_min", 18.0)), float(crop_info.get("temp_max", 32.0)))


def evaluate_moisture_condition(arg1, arg2="Vegetative", arg3=50.0, **kwargs) -> Dict[str, Any]:
    """
    Evaluates hydration status against optimal crop threshold band.
    Flexible signature: accepts (crop, stage, soil_moisture) or (soil_moisture, crop, stage) or kwargs.
    Used for focused irrigation management.
    """
    if isinstance(arg1, (int, float)):
        soil_moisture = float(arg1)
        crop = str(arg2)
        stage = str(arg3) if isinstance(arg3, str) else "Vegetative"
    else:
        crop = str(arg1)
        stage = str(arg2) if isinstance(arg2, str) else "Vegetative"
        soil_moisture = float(arg3) if isinstance(arg3, (int, float)) else 50.0

    crop = kwargs.get("crop", crop)
    stage = kwargs.get("stage", kwargs.get("growth_stage", stage))
    soil_moisture = float(kwargs.get("soil_moisture", kwargs.get("moisture", soil_moisture)))

    opt_min, opt_max = get_optimal_moisture_band(crop, stage)
    if soil_moisture < opt_min - 15.0:
        return {
            "status": "Critical",
            "moisture_state": "Severe Deficit",
            "action_title": f"Critical Deficit: Soil moisture ({soil_moisture:.1f}%) is far below safe minimum ({opt_min:.0f}%). Immediate irrigation required.",
            "reasoning": f"Root zone hydration is severely depleted for {crop}. Hydraulic tension is restricting stomatal conductance and causing wilting.",
            "optimal_band": (opt_min, opt_max)
        }
    elif soil_moisture < opt_min:
        return {
            "status": "Warning",
            "moisture_state": "Deficit",
            "action_title": f"Moisture Depleted: Current moisture ({soil_moisture:.1f}%) is below optimal ({opt_min:.0f}%–{opt_max:.0f}%). Schedule irrigation.",
            "reasoning": f"Transpirational demand exceeds current soil moisture availability for {crop} at {stage} stage.",
            "optimal_band": (opt_min, opt_max)
        }
    elif soil_moisture > opt_max + 15.0:
        return {
            "status": "Critical",
            "moisture_state": "Waterlogging Hazard",
            "action_title": f"Saturation Alert: Moisture ({soil_moisture:.1f}%) exceeds upper bound ({opt_max:.0f}%). Suspend watering & inspect drainage.",
            "reasoning": f"Saturated root zone deprives roots of oxygen, risking anaerobic rot and Pythium infection.",
            "optimal_band": (opt_min, opt_max)
        }
    elif soil_moisture > opt_max:
        return {
            "status": "Warning",
            "moisture_state": "Excess",
            "action_title": f"Moisture Elevated: Current reading ({soil_moisture:.1f}%) is above target ceiling ({opt_max:.0f}%). Pause irrigation.",
            "reasoning": f"Soil has surplus water; further irrigation is wasteful and may leach nutrients.",
            "optimal_band": (opt_min, opt_max)
        }
    else:
        return {
            "status": "Optimal",
            "moisture_state": "Optimal",
            "action_title": f"Moisture Balanced: Reading ({soil_moisture:.1f}%) is within optimal band ({opt_min:.0f}%–{opt_max:.0f}%). Maintain regimen.",
            "reasoning": f"Root zone hydration is balanced for {crop} during {stage}. Stomata and nutrient uptake function optimally.",
            "optimal_band": (opt_min, opt_max)
        }


def evaluate_all_rules(
    crop: str,
    growth_stage: str,
    soil_moisture: float,
    temperature: float,
    leaf_wetness_hours: float = 0.0,
    symptoms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Comprehensive rule-based agronomic evaluation encompassing soil moisture,
    ambient temperature, leaf wetness duration, and observed symptoms.
    """
    res = evaluate_conditions(
        crop_type=crop,
        growth_stage=growth_stage,
        soil_moisture=float(soil_moisture),
        temperature=float(temperature)
    )

    reasoning_points = res["reasoning"].split(" • ") if isinstance(res["reasoning"], str) else list(res["reasoning"])
    practical_steps = list(res.get("practical_steps", []))
    status = res.get("status", "Optimal")

    # Evaluate leaf wetness
    if leaf_wetness_hours >= 6.0:
        reasoning_points.append(
            f"Extended leaf wetness ({leaf_wetness_hours:.1f} hours) dramatically increases foliar fungal infection probability (Blight / Downy Mildew)."
        )
        practical_steps.append("Avoid overhead sprinkling; inspect underside of canopy for early sporulation.")
        if status == "Optimal":
            status = "Warning"

    # Evaluate visual symptoms
    if symptoms:
        symptom_str = ", ".join(symptoms)
        reasoning_points.append(f"Visual anomalies reported: {symptom_str}.")
        for s in symptoms:
            s_lower = s.lower()
            if "wilt" in s_lower:
                practical_steps.append("Check vascular bundles near stem base for bacterial or fungal discoloration.")
            elif "yellow" in s_lower:
                practical_steps.append("Assess leaf age: lower leaf chlorosis indicates nitrogen/magnesium deficiency; upper leaf chlorosis suggests iron/sulfur deficit.")
            elif "mildew" in s_lower or "spot" in s_lower:
                practical_steps.append("Isolate infected leaves and apply prophylactic copper or sulfur formulation as appropriate.")
            elif "chew" in s_lower or "curl" in s_lower:
                practical_steps.append("Scout for sucking pests (aphids/thrips) on leaf undersides and deploy yellow sticky traps.")
        if status == "Optimal":
            status = "Warning"

    res["status"] = status
    res["reasoning"] = reasoning_points
    res["practical_steps"] = practical_steps
    return res


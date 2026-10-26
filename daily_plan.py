"""
Daily Farming Plan Generator for Smart Agriculture Agent.
Synthesizes real-time meteorological forecasts, soil hydration status,
crop growth stage, and risk alerts into an actionable, prioritized daily checklist.
Explains the clear agronomic rationale behind every recommended action.
"""

from typing import Dict, Any, List, Optional


def generate_daily_plan(
    crop_type: Optional[str] = None,
    growth_stage: str = "Vegetative",
    weather: Optional[Dict[str, Any]] = None,
    latest_reading: Optional[Dict[str, Any]] = None,
    top_threats: Optional[List[Dict[str, Any]]] = None,
    crop: Optional[str] = None,
    risks: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> Dict[str, List[Dict[str, str]]]:
    """
    Generates a structured daily operational checklist categorized both:
    - Chronologically: 'morning_tasks', 'afternoon_tasks', 'evening_tasks'
    - Priority-wise: 'urgent', 'routine', 'scout'
    """
    active_crop = crop or crop_type or "Tomato"
    weather = weather or {}
    latest_reading = latest_reading or {}
    threats = risks if risks is not None else (top_threats or [])

    rain_prob = weather.get("rain_prob_today", 15.0)
    temp = weather.get("temperature", 28.0)
    moisture = latest_reading.get("soil_moisture", 50.0)
    status = latest_reading.get("status", "Optimal")

    morning_tasks: List[Dict[str, str]] = []
    afternoon_tasks: List[Dict[str, str]] = []
    evening_tasks: List[Dict[str, str]] = []
    urgent: List[Dict[str, str]] = []
    routine: List[Dict[str, str]] = []
    scout: List[Dict[str, str]] = []

    # 1. Rain & Irrigation
    if rain_prob >= 50.0:
        drain_task = {
            "time": "06:00 – 08:00 AM",
            "task": "Inspect Furrows & Drainage Swales Before Rain Inundation",
            "reason": f"Forecast indicates {rain_prob:.0f}% rain probability today. Evacuate debris from outlets to prevent root zone saturation.",
            "impact": "Prevents anaerobic root asphyxiation and standing water accumulation."
        }
        morning_tasks.append(drain_task)
        urgent.append(drain_task)

        withhold_task = {
            "time": "All Day",
            "task": "Withhold Scheduled Irrigation Cycles",
            "reason": "Expected rainfall will replenish root hydration naturally. Avoid leaching soil nutrients.",
            "impact": "Conserves water and prevents fertilizer run-off."
        }
        morning_tasks.append(withhold_task)
        urgent.append(withhold_task)
    elif moisture < 45.0:
        irrig_task = {
            "time": "05:30 – 08:30 AM",
            "task": f"Initiate Deep Irrigation Cycle for {active_crop}",
            "reason": f"Observed soil moisture ({moisture:.1f}%) indicates deficit. Irrigate during early hours to minimize evaporative loss.",
            "impact": "Restores hydraulic conductivity into root zone without midday leaf scorching."
        }
        morning_tasks.append(irrig_task)
        urgent.append(irrig_task)
    elif moisture > 80.0:
        drain_task = {
            "time": "07:00 – 10:00 AM",
            "task": "Drain Surface Standing Water and Aerate Field Soil",
            "reason": f"Soil moisture ({moisture:.1f}%) exceeds physiological ceiling. Aeration is critical for nutrient uptake.",
            "impact": "Restores root oxygenation and discourages soil-borne damping-off pathogens."
        }
        morning_tasks.append(drain_task)
        urgent.append(drain_task)

    # 2. Disease & Pest Scouting (Morning)
    if threats:
        high_threats = [t for t in threats if t.get("risk_level") == "High Risk"]
        target = high_threats[0] if high_threats else threats[0]
        scout_task = {
            "time": "06:30 – 08:30 AM",
            "task": f"Field Scouting Focus: {target.get('threat_name', 'Foliar Pathogens')}",
            "reason": f"Diagnostic model indicates {target.get('risk_level', 'elevated risk')} under current microclimate. Inspect 20 random plants.",
            "impact": f"Early detection prevents exponential pest spread. Look for: {target.get('early_signs', 'foliar lesions')}"
        }
        morning_tasks.append(scout_task)
        scout.append(scout_task)

    # Ensure morning has a routine task if still empty
    if not morning_tasks:
        default_morning = {
            "time": "07:00 – 09:00 AM",
            "task": f"Morning Field Walk & Canopy Inspection for {active_crop}",
            "reason": "Conditions are stable. Morning walk ensures uniform vegetative growth and absence of overnight insect damage.",
            "impact": "Maintains continuous agronomic oversight across all field parcels."
        }
        morning_tasks.append(default_morning)
        routine.append(default_morning)

    # 3. Afternoon Operations (12:00 - 15:30)
    if temp >= 34.0:
        mulch_task = {
            "time": "12:00 – 02:00 PM",
            "task": "Apply 5–8 cm Organic Straw Mulch Across Exposed Beds",
            "reason": f"Daytime heat expected at {temp:.1f}°C. Mulch acts as a thermal buffer, lowering soil temperature by 3–5°C.",
            "impact": "Protects delicate root hairs and cuts soil surface evaporation by up to 40%."
        }
        afternoon_tasks.append(mulch_task)
        routine.append(mulch_task)

    if growth_stage == "Maturity / Harvest":
        harvest_task = {
            "time": "01:00 – 03:00 PM",
            "task": "Sample Grain/Fruit Maturity and Terminate Late Irrigation",
            "reason": "Ceasing irrigation prior to harvest triggers uniform grain ripening and prevents harvest mold.",
            "impact": "Enhances crop dry matter, reduces drying cost, and improves storage longevity."
        }
        afternoon_tasks.append(harvest_task)
        routine.append(harvest_task)

    if not afternoon_tasks:
        default_afternoon = {
            "time": "01:00 – 03:00 PM",
            "task": "Microclimate & Soil Temperature Assessment",
            "reason": f"Ambient temperature is {temp:.1f}°C. Monitor canopy transpiration and ensure shade nets or drip lines operate smoothly.",
            "impact": "Prevents midday heat shock and preserves vegetative vigor."
        }
        afternoon_tasks.append(default_afternoon)
        routine.append(default_afternoon)

    # 4. Evening Operations (16:30 - 19:00)
    if growth_stage == "Germination / Seedling":
        gap_task = {
            "time": "04:30 – 06:00 PM",
            "task": "Seedling Thinning and Gap-Filling",
            "reason": "Fill empty patches with healthy nursery seedlings during cooler afternoon hours to avoid transplant shock.",
            "impact": "Guarantees optimal canopy closure and target plant population per acre."
        }
        evening_tasks.append(gap_task)
        routine.append(gap_task)
    elif growth_stage == "Vegetative":
        weed_task = {
            "time": "05:00 – 06:30 PM",
            "task": "Light Inter-Cultivation & Weed Eradication",
            "reason": "Eliminates root competition for nutrients and loosens upper soil crust for night aeration.",
            "impact": "Accelerates tillering, branching, and vegetative leaf area index."
        }
        evening_tasks.append(weed_task)
        routine.append(weed_task)
    elif growth_stage == "Flowering / Reproductive":
        flower_task = {
            "time": "05:00 – 06:30 PM",
            "task": "Verify Root-Zone Hydration & Flower Retention",
            "reason": "Flowering is the highest-sensitivity physiological window. Avoid sudden moisture swings.",
            "impact": "Maximizes pollen viability, flower retention, and fruit/grain setting percentage."
        }
        evening_tasks.append(flower_task)
        urgent.append(flower_task)

    drip_task = {
        "time": "05:30 – 06:45 PM",
        "task": "Inspect Irrigation Drippers / Furrow Outlets",
        "reason": "Clogged emitters or broken furrows cause localized drought and localized waterlogging.",
        "impact": "Ensures uniform water delivery across the entire planted acreage."
    }
    evening_tasks.append(drip_task)
    scout.append(drip_task)

    return {
        "morning_tasks": morning_tasks,
        "afternoon_tasks": afternoon_tasks,
        "evening_tasks": evening_tasks,
        "urgent": urgent,
        "routine": routine,
        "scout": scout
    }


# Backward-compatible alias
generate_daily_farming_plan = generate_daily_plan

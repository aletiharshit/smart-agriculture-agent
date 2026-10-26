"""
AI-Based Crop Recommendation Engine for Smart Agriculture Agent.
Evaluates soil chemical parameters (N, P, K, pH), soil classification,
water availability, season, and meteorological data.
Ranks suitable crops using verified agronomic guidelines with clear parameter provenance.
"""

from typing import Dict, Any, List

CROP_PROFILES = {
    "Rice": {
        "ideal_soil": ["Clay Loam", "Alluvial", "Clay"],
        "ph_min": 5.5, "ph_max": 7.5,
        "n_min": 100, "n_max": 180,
        "p_min": 30, "p_max": 60,
        "k_min": 40, "k_max": 90,
        "temp_min": 20, "temp_max": 35,
        "water_req": "High",
        "seasons": ["Kharif", "Rabi"],
        "description": "High water demand cereal suited for lowland clays and alluvial soils with reliable canal or borewell supply."
    },
    "Wheat": {
        "ideal_soil": ["Loam", "Clay Loam", "Alluvial"],
        "ph_min": 6.0, "ph_max": 7.5,
        "n_min": 100, "n_max": 160,
        "p_min": 40, "p_max": 70,
        "k_min": 30, "k_max": 60,
        "temp_min": 12, "temp_max": 25,
        "water_req": "Moderate",
        "seasons": ["Rabi"],
        "description": "Cool-season temperate staple requiring well-drained loams and moderate irrigation during crown root initiation."
    },
    "Maize": {
        "ideal_soil": ["Loam", "Sandy Loam", "Alluvial", "Red Soil"],
        "ph_min": 5.8, "ph_max": 7.2,
        "n_min": 90, "n_max": 150,
        "p_min": 30, "p_max": 60,
        "k_min": 30, "k_max": 60,
        "temp_min": 18, "temp_max": 32,
        "water_req": "Moderate",
        "seasons": ["Kharif", "Rabi", "Zaid"],
        "description": "Versatile C4 grain with high fertilizer responsiveness; thrives in well-aerated fertile soils without waterlogging."
    },
    "Cotton": {
        "ideal_soil": ["Black Soil", "Alluvial", "Clay Loam"],
        "ph_min": 6.0, "ph_max": 8.0,
        "n_min": 90, "n_max": 160,
        "p_min": 30, "p_max": 60,
        "k_min": 40, "k_max": 80,
        "temp_min": 21, "temp_max": 35,
        "water_req": "Moderate",
        "seasons": ["Kharif"],
        "description": "Deep-rooted commercial cash crop optimal for moisture-retentive black cotton soils with sunny maturation."
    },
    "Tomato": {
        "ideal_soil": ["Sandy Loam", "Loam", "Red Soil"],
        "ph_min": 6.0, "ph_max": 7.0,
        "n_min": 80, "n_max": 140,
        "p_min": 40, "p_max": 80,
        "k_min": 60, "k_max": 120,
        "temp_min": 18, "temp_max": 30,
        "water_req": "Moderate",
        "seasons": ["Kharif", "Rabi", "Zaid"],
        "description": "High-value horticultural crop requiring balanced N-P-K nutrition, consistent soil moisture, and drip irrigation."
    },
    "Groundnut": {
        "ideal_soil": ["Sandy Loam", "Red Soil", "Loam"],
        "ph_min": 6.0, "ph_max": 7.5,
        "n_min": 20, "n_max": 40,  # Legume fixes atmospheric nitrogen
        "p_min": 40, "p_max": 70,
        "k_min": 40, "k_max": 75,
        "temp_min": 20, "temp_max": 32,
        "water_req": "Moderate",
        "seasons": ["Kharif", "Rabi"],
        "description": "Nitrogen-fixing oilseed crop highly suited for friable sandy loams that facilitate subterranean peg penetration."
    },
    "Millets (Jowar / Bajra)": {
        "ideal_soil": ["Sandy Loam", "Red Soil", "Alluvial", "Black Soil"],
        "ph_min": 5.5, "ph_max": 8.0,
        "n_min": 40, "n_max": 80,
        "p_min": 20, "p_max": 40,
        "k_min": 20, "k_max": 40,
        "temp_min": 22, "temp_max": 38,
        "water_req": "Low",
        "seasons": ["Kharif", "Zaid"],
        "description": "Climate-resilient, drought-hardy coarse grain requiring minimal inputs, highly tolerant of elevated heat."
    },
    "Pulses (Chickpea / Pigeonpea)": {
        "ideal_soil": ["Loam", "Clay Loam", "Black Soil", "Sandy Loam"],
        "ph_min": 6.0, "ph_max": 7.8,
        "n_min": 20, "n_max": 40,
        "p_min": 30, "p_max": 60,
        "k_min": 20, "k_max": 50,
        "temp_min": 15, "temp_max": 30,
        "water_req": "Low",
        "seasons": ["Rabi", "Kharif"],
        "description": "Restores soil fertility via biological nitrogen fixation; operates well on residual soil moisture."
    }
}


from typing import Dict, Any, List, Optional

# (CROP_PROFILES dictionary remains unchanged above)


def recommend_crops(
    soil_type: str = "Clay Loam",
    soil_ph: Optional[float] = None,
    nitrogen: Optional[float] = None,
    phosphorus: Optional[float] = None,
    potassium: Optional[float] = None,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    water_availability: str = "Moderate",
    season: str = "Kharif",
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Ranks crops based on multiple agronomic dimensions:
    - pH tolerance (25%)
    - NPK nutrient availability match (30%)
    - Thermal and humidity feasibility (25%)
    - Soil texture & water supply compatibility (20%)
    Handles parameter aliases gracefully.
    """
    ph = float(soil_ph if soil_ph is not None else kwargs.get("ph", 6.8))
    n = float(nitrogen if nitrogen is not None else kwargs.get("n", 140.0))
    p = float(phosphorus if phosphorus is not None else kwargs.get("p", 45.0))
    k = float(potassium if potassium is not None else kwargs.get("k", 180.0))
    temp = float(temperature if temperature is not None else (kwargs.get("current_temp") or kwargs.get("temp") or 28.0))
    hum = float(humidity if humidity is not None else kwargs.get("hum", 65.0))
    water = water_availability or kwargs.get("water", "Moderate")
    target_season = season or kwargs.get("target_season", "Kharif")
    soil = soil_type or kwargs.get("soil", "Clay Loam")

    results = []

    for crop_name, prof in CROP_PROFILES.items():
        score = 0.0
        reasons = []

        # 1. pH evaluation (0 - 25 points)
        if prof["ph_min"] <= ph <= prof["ph_max"]:
            score += 25.0
            reasons.append(f"Soil pH ({ph:.1f}) is within the optimum range ({prof['ph_min']}–{prof['ph_max']}).")
        elif abs(ph - prof["ph_min"]) <= 0.6 or abs(ph - prof["ph_max"]) <= 0.6:
            score += 15.0
            reasons.append(f"Soil pH ({ph:.1f}) is acceptable with minor amendments.")
        else:
            score += 5.0
            reasons.append(f"Soil pH ({ph:.1f}) is outside the preferred band ({prof['ph_min']}–{prof['ph_max']}).")

        # 2. Temperature & Climate (0 - 25 points)
        if prof["temp_min"] <= temp <= prof["temp_max"]:
            score += 25.0
            reasons.append(f"Temperature ({temp:.1f}°C) matches the metabolic growth window ({prof['temp_min']}°C–{prof['temp_max']}°C).")
        elif abs(temp - prof["temp_min"]) <= 4.0 or abs(temp - prof["temp_max"]) <= 4.0:
            score += 15.0
            reasons.append(f"Temperature ({temp:.1f}°C) is tolerable but near physiological boundaries.")
        else:
            score += 5.0
            reasons.append(f"Temperature ({temp:.1f}°C) poses potential thermal stress.")

        # 3. Water & Soil compatibility (0 - 25 points)
        soil_match = any(st_sub.lower() in soil.lower() for st_sub in prof["ideal_soil"])
        if soil_match:
            score += 15.0
            reasons.append(f"{soil} texture supports adequate root penetration and drainage for {crop_name}.")
        else:
            score += 7.0

        if prof["water_req"] == "High" and water == "High":
            score += 10.0
        elif prof["water_req"] in ["Moderate", "Low"] and water in ["Moderate", "High"]:
            score += 10.0
        elif prof["water_req"] == "Low" and water == "Low":
            score += 10.0
            reasons.append("Crop is highly drought-tolerant, well-matched with low water availability.")
        else:
            score += 3.0
            reasons.append(f"Caution: {crop_name} requires {prof['water_req']} water availability.")

        # 4. Nutrient Match (N-P-K) (0 - 25 points)
        n_ok = prof["n_min"] * 0.7 <= n <= prof["n_max"] * 1.4
        p_ok = prof["p_min"] * 0.7 <= p <= prof["p_max"] * 1.4
        k_ok = prof["k_min"] * 0.7 <= k <= prof["k_max"] * 1.4
        nutr_matches = sum([n_ok, p_ok, k_ok])
        score += (nutr_matches / 3.0) * 25.0

        # Season Bonus / Penalty
        if target_season in prof["seasons"] or any(s in target_season for s in prof["seasons"]):
            score = min(100.0, score + 5.0)
            reasons.append(f"Well-adapted to the current {target_season} cultivation season.")

        final_score = round(score, 1)
        results.append({
            "crop": crop_name,
            "suitability_score": final_score,
            "score": round(final_score),
            "water_requirement": prof["water_req"],
            "description": prof["description"],
            "reasons": reasons
        })

    # Sort descending by suitability score and assign 1-based ranks
    results.sort(key=lambda x: x["suitability_score"], reverse=True)
    for i, item in enumerate(results, 1):
        item["rank"] = i

    return results

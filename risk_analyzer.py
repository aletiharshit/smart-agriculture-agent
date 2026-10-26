"""
Crop Risk and Pest/Disease Diagnostic Analyzer for Smart Agriculture Agent.
Analyzes microclimate parameters, growth stage, and farmer-observed symptoms.
Produces scientific risk vulnerability estimates, warning signs, and preventive measures.
Does not claim laboratory confirmation.
"""

from typing import Dict, Any, List, Optional

DISEASE_PEST_KNOWLEDGE = {
    "Rice": [
        {
            "name": "Rice Blast (Fungal - Magnaporthe oryzae)",
            "temp_range": (20.0, 29.0),
            "humidity_min": 85.0,
            "stages": ["Vegetative", "Flowering / Reproductive"],
            "symptom_keywords": ["spindle", "spots", "lesions", "brown patch", "drying leaves"],
            "early_signs": "Diamond- or spindle-shaped lesions with grayish centers and brown borders on leaves and nodes.",
            "preventive_measures": [
                "Avoid excessive split applications of Nitrogen fertilizer.",
                "Ensure balanced Potash (K) nutrition to thicken epidermal cell walls.",
                "Maintain optimal field drainage; avoid prolonged stagnant water during humid spells.",
                "If threshold incidence exceeds 5% leaves, apply recommended bio-fungicide (Trichoderma viride) or targeted triazole spray."
            ]
        },
        {
            "name": "Brown Planthopper (Insect Pest - Nilaparvata lugens)",
            "temp_range": (25.0, 33.0),
            "humidity_min": 75.0,
            "stages": ["Vegetative", "Flowering / Reproductive"],
            "symptom_keywords": ["yellowing", "drying", "hopperburn", "wilting", "base of plant"],
            "early_signs": "Circular patches of yellowing drying hills ('hopper burn'); tiny brown insects visible at plant base near water level.",
            "preventive_measures": [
                "Practice alternate wetting and drying (AWD) irrigation to break insect multiplication cycles.",
                "Open 'alleyways' (30 cm paths every 2–3 meters) to increase sunlight penetration and air circulation.",
                "Conserve natural predators such as spiders and mirid bugs; avoid prophylactic broad-spectrum insecticide sprays."
            ]
        }
    ],
    "Wheat": [
        {
            "name": "Stripe / Yellow Rust (Fungal - Puccinia striiformis)",
            "temp_range": (10.0, 22.0),
            "humidity_min": 75.0,
            "stages": ["Vegetative", "Flowering / Reproductive"],
            "symptom_keywords": ["yellow", "pustules", "stripes", "powder", "rust"],
            "early_signs": "Linear stripes of bright yellow powdery pustules running parallel to leaf veins.",
            "preventive_measures": [
                "Scout early in morning when sunlight reveals bright yellow powdery stripes.",
                "Avoid late sowing to bypass optimal spore germination temperature windows.",
                "Deploy resistant regional cultivars and apply propiconazole 25% EC at first appearance of focal foci."
            ]
        },
        {
            "name": "Wheat Aphids (Rhopalosiphum padi)",
            "temp_range": (15.0, 26.0),
            "humidity_min": 40.0,
            "stages": ["Flowering / Reproductive", "Maturity / Harvest"],
            "symptom_keywords": ["curled", "sticky", "sap", "cluster", "aphid"],
            "early_signs": "Clusters of small greenish insects congregating under leaves and earheads with shiny sticky honeydew.",
            "preventive_measures": [
                "Spray 5% neem seed kernel extract (NSKE) as early deterrent.",
                "Conserve ladybird beetles and syrphid fly larvae."
            ]
        }
    ],
    "Maize": [
        {
            "name": "Fall Armyworm (Spodoptera frugiperda)",
            "temp_range": (20.0, 35.0),
            "humidity_min": 50.0,
            "stages": ["Germination / Seedling", "Vegetative"],
            "symptom_keywords": ["holes", "frass", "ragged", "caterpillar", "whorl"],
            "early_signs": "Pin-holes in young leaves, sawdust-like larval fecal frass deposited inside central whorls.",
            "preventive_measures": [
                "Apply dry sand mixed with neem cake into whorls during early vegetative phase.",
                "Deploy pheromone traps at 5 traps/acre for real-time adult male moth flight monitoring.",
                "Apply Bacillus thuringiensis (Bt) formulation or emamectin benzoate if whorl damage exceeds 10%."
            ]
        }
    ],
    "Cotton": [
        {
            "name": "Pink Bollworm (Pectinophora gossypiella)",
            "temp_range": (24.0, 35.0),
            "humidity_min": 60.0,
            "stages": ["Flowering / Reproductive", "Maturity / Harvest"],
            "symptom_keywords": ["rosette", "flower", "boll", "exit hole", "shedding"],
            "early_signs": "Twisted 'rosette' flowers that fail to open normally; tiny pin-prick entrance holes on young developing bolls.",
            "preventive_measures": [
                "Install delta pheromone traps (5 traps per acre) from 45 days after sowing.",
                "Collect and safely dispose of shed squares, buds, and fallen rosette flowers daily.",
                "Release Trichogramma bactrae egg parasitoid wasps at weekly intervals."
            ]
        },
        {
            "name": "Cotton Leaf Curl Virus & Whitefly Complex",
            "temp_range": (26.0, 36.0),
            "humidity_min": 55.0,
            "stages": ["Vegetative", "Flowering / Reproductive"],
            "symptom_keywords": ["curling", "thick veins", "cupping", "whitefly", "stunted"],
            "early_signs": "Upward or downward leaf curling, vein thickening, and enations (leaf-like outgrowths) on leaf undersides.",
            "preventive_measures": [
                "Install yellow sticky traps (15–20 per acre) slightly above the canopy to trap whitefly vectors.",
                "Eradicate weed hosts (Abutilon, Xanthium) along field borders.",
                "Spray insecticidal soap or neem oil (1500 ppm) to control early nymphal whitefly populations."
            ]
        }
    ],
    "Tomato": [
        {
            "name": "Early Blight (Alternaria solani)",
            "temp_range": (22.0, 32.0),
            "humidity_min": 75.0,
            "stages": ["Vegetative", "Flowering / Reproductive", "Maturity / Harvest"],
            "symptom_keywords": ["target", "concentric", "lower leaves", "brown spots", "yellow halo"],
            "early_signs": "Dark brown circular spots with characteristic concentric 'target-board' rings and surrounding yellow chlorotic halos.",
            "preventive_measures": [
                "Prune bottom 15–20 cm of foliage to prevent soil splash-borne spore contact during irrigation.",
                "Mulch beds with clean straw to create a physical barrier against soil-dwelling fungal spores.",
                "Drip irrigate rather than overhead sprinkle to keep tomato foliage dry."
            ]
        },
        {
            "name": "Blossom End Rot (Physiological Calcium Disorder)",
            "temp_range": (27.0, 38.0),
            "humidity_min": 30.0,
            "stages": ["Flowering / Reproductive", "Maturity / Harvest"],
            "symptom_keywords": ["bottom", "black patch", "sunken", "calcium", "fruit rot"],
            "early_signs": "Water-soaked dark sunken leathery patch developing at blossom end of green ripening tomato fruits.",
            "preventive_measures": [
                "Maintain uniform soil moisture; avoid severe dry-wet soil moisture fluctuations.",
                "Apply foliar calcium nitrate (0.5%) spray during early fruit set.",
                "Mulch to buffer root zone temperature and conserve volumetric soil moisture."
            ]
        }
    ]
}


def analyze_crop_risks(
    crop_type: str = "",
    growth_stage: str = "Vegetative",
    temperature: float = 25.0,
    humidity: float = 60.0,
    soil_moisture: float = 60.0,
    observed_symptoms: str = "",
    crop: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates scientific risk likelihood (High, Moderate, Low)
    by combining environmental thresholds with farmer-reported symptoms.
    Supports either `crop_type` or `crop` parameter.
    """
    selected_crop = crop if crop is not None else crop_type
    crop_threats = DISEASE_PEST_KNOWLEDGE.get(selected_crop, [])
    analyzed_threats = []
    symptoms_lower = (observed_symptoms or "").lower()

    for threat in crop_threats:
        risk_score = 0
        factors_matched = []

        # 1. Growth Stage Match
        if growth_stage in threat["stages"]:
            risk_score += 30
            factors_matched.append(f"Active growth stage ({growth_stage}) is vulnerable.")

        # 2. Temperature Threshold Match
        t_min, t_max = threat["temp_range"]
        if t_min <= temperature <= t_max:
            risk_score += 25
            factors_matched.append(f"Temperature ({temperature:.1f}°C) matches pathogen/pest proliferation window ({t_min}°C–{t_max}°C).")
        elif abs(temperature - t_min) <= 3.0 or abs(temperature - t_max) <= 3.0:
            risk_score += 15

        # 3. Humidity / Soil Moisture Match
        if humidity >= threat["humidity_min"] or soil_moisture >= threat["humidity_min"]:
            risk_score += 25
            factors_matched.append(f"Atmospheric humidity ({humidity:.0f}%) / soil moisture facilitates spore germination/pest shelter.")
        elif humidity >= (threat["humidity_min"] - 15):
            risk_score += 10

        # 4. Symptom Correlation
        symptom_hit = any(keyword in symptoms_lower for keyword in threat["symptom_keywords"])
        if symptom_hit:
            risk_score += 20
            factors_matched.append("Entered field symptoms match early diagnostic patterns.")

        # Determine Risk Classification
        if risk_score >= 65:
            risk_level = "High Risk"
            badge_color = "#b91c1c"
        elif risk_score >= 40:
            risk_level = "Moderate Risk"
            badge_color = "#d97706"
        else:
            risk_level = "Low Risk"
            badge_color = "#2d6a4f"

        analyzed_threats.append({
            "threat_name": threat["name"],
            "risk_name": threat["name"],
            "name": threat["name"],
            "risk_level": risk_level,
            "severity": risk_level,
            "badge_color": badge_color,
            "risk_score": min(100, risk_score),
            "score": min(100, risk_score),
            "early_signs": threat["early_signs"],
            "factors_matched": factors_matched,
            "preventive_measures": threat["preventive_measures"],
            "mitigations": threat["preventive_measures"]
        })

    # Sort threats so highest risk appears on top
    analyzed_threats.sort(key=lambda x: x["risk_score"], reverse=True)
    return analyzed_threats

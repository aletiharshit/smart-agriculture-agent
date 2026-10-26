# -*- coding: utf-8 -*-
"""
Multilingual Agricultural Assistant & Knowledge Engine for Smart Agriculture Agent.
Provides structured, rule-based agronomic advisory across 14 Indian languages:
English, Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, Gujarati,
Punjabi, Odia, Urdu, Assamese, and Sanskrit.

Integrates:
- Deterministic crop thresholds from rules.py
- Crop recommendation engine from crop_recommender.py
- Crop disease and pest diagnostic models from risk_analyzer.py
- Daily checklist synthesizer from daily_plan.py
- Real-time Open-Meteo meteorological data from weather_service.py
- Strict farmer privacy and data provenance tracking
"""

from typing import Dict, Any, Optional, List, Tuple
import re
import datetime
from translations import t, SUPPORTED_LANGUAGES

# ==============================================================================
# 1. 15 COMMON FARMER QUESTIONS REGISTRY
# ==============================================================================
COMMON_QUESTIONS: List[Dict[str, str]] = [
    # 💧 Category 1: Irrigation & Water Management
    {
        "id": "q1",
        "category_key": "asst_cat_irrigation",
        "chip_key": "q1_chip",
        "full_key": "q1_full",
        "intent": "irrigation_today"
    },
    {
        "id": "q6",
        "category_key": "asst_cat_irrigation",
        "chip_key": "q6_chip",
        "full_key": "q6_full",
        "intent": "low_soil_moisture"
    },
    {
        "id": "q7",
        "category_key": "asst_cat_irrigation",
        "chip_key": "q7_chip",
        "full_key": "q7_full",
        "intent": "reduce_water_waste"
    },

    # 🌱 Category 2: Soil Health & Nutrition
    {
        "id": "q2",
        "category_key": "asst_cat_soil",
        "chip_key": "q2_chip",
        "full_key": "q2_full",
        "intent": "soil_fertility"
    },
    {
        "id": "q11",
        "category_key": "asst_cat_soil",
        "chip_key": "q11_chip",
        "full_key": "q11_full",
        "intent": "nutrient_deficiencies"
    },
    {
        "id": "q12",
        "category_key": "asst_cat_soil",
        "chip_key": "q12_chip",
        "full_key": "q12_full",
        "intent": "interpret_analysis"
    },

    # 🌾 Category 3: Crop Selection & Planning
    {
        "id": "q3",
        "category_key": "asst_cat_crop",
        "chip_key": "q3_chip",
        "full_key": "q3_full",
        "intent": "crop_suitability"
    },
    {
        "id": "q14",
        "category_key": "asst_cat_crop",
        "chip_key": "q14_chip",
        "full_key": "q14_full",
        "intent": "crop_selection_info"
    },
    {
        "id": "q15",
        "category_key": "asst_cat_crop",
        "chip_key": "q15_chip",
        "full_key": "q15_full",
        "intent": "next_season_prep"
    },

    # 🛡️ Category 4: Pest & Disease Protection
    {
        "id": "q4",
        "category_key": "asst_cat_pest",
        "chip_key": "q4_chip",
        "full_key": "q4_full",
        "intent": "crop_diseases"
    },
    {
        "id": "q5",
        "category_key": "asst_cat_pest",
        "chip_key": "q5_chip",
        "full_key": "q5_full",
        "intent": "disease_early_signs"
    },
    {
        "id": "q13",
        "category_key": "asst_cat_pest",
        "chip_key": "q13_chip",
        "full_key": "q13_full",
        "intent": "pest_resistance"
    },

    # 📅 Category 5: Daily Operations & Growth
    {
        "id": "q8",
        "category_key": "asst_cat_daily",
        "chip_key": "q8_chip",
        "full_key": "q8_full",
        "intent": "daily_priorities"
    },
    {
        "id": "q9",
        "category_key": "asst_cat_daily",
        "chip_key": "q9_chip",
        "full_key": "q9_full",
        "intent": "growth_stage_care"
    },
    {
        "id": "q10",
        "category_key": "asst_cat_daily",
        "chip_key": "q10_chip",
        "full_key": "q10_full",
        "intent": "heavy_rain_action"
    }
]

# Mapping from question ID to intent
QID_TO_INTENT = {q["id"]: q["intent"] for q in COMMON_QUESTIONS}


# ==============================================================================
# 2. MULTILINGUAL INTENT KEYWORD CATALOG
# ==============================================================================
INTENT_KEYWORDS: Dict[str, List[str]] = {
    "irrigation_today": [
        # English
        "irrigate today", "irrigate my crop today", "how much should i irrigate",
        "when should i irrigate", "when should i irrigate my field", "irrigate my field", "irrigate", "irrigation",
        "water my crop", "should i water", "watering today", "irrigation timing",
        "when should i water", "how much water", "irrigation schedule", "water my field", "watering",
        # Telugu
        "ఎంత నీరు", "నీరు పెట్టాలి", "నీటిપారుదల", "ఈరోజు ఎంత నీరు", "నీరు కావాలా",
        # Hindi
        "कितना पानी", "सिंचाई कब", "सिंचाई आज", "पानी देना चाहिए", "कब पानी दें",
        # Tamil
        "எவ்வளவு தண்ணீர்", "பாசனம்", "தண்ணீர் பாய்ச்ச", "இன்று தண்ணீர்",
        # Kannada
        "ಎಷ್ಟು ನೀರು", "ಯಾವಾಗ ನೀರು", "ನೀರಾವರಿ", "ಇಂದು ನೀರು",
        # Malayalam
        "എത്ര വെള്ളം", "നനയ്ക്കണം", "ജലസேചനം", "ഇന്ന് നനയ്ക്കണോ",
        # Bengali
        "কতটুকু সেচ", "পানি দেওয়া", "সেচ দেওয়া", "আজকে পানি",
        # Marathi
        "किती पाणी", "सिंचन कधी", "पाणी द्यावे", "आज पाणी",
        # Gujarati
        "કેટલું પાણી", "પિયત આપવું", "પાણી આપવું", "આજે પિયત",
        # Punjabi
        "ਕਿੰਨਾ ਪਾਣੀ", "ਸਿੰਚਾਈ ਕਦੋਂ", "ਪਾਣੀ ਦੇਣਾ", "ਅੱਜ ਪਾਣੀ",
        # Odia
        "କେତେ ଜଳସେଚନ", "ପାଣି ଦେବା", "ଜଳସେଚନ କେତେ",
        # Urdu
        "کتنا پانی", "آبپاشی کب", "پانی دینا چاہیے", "آج آبپاشی",
        # Assamese
        "কিমান জলসিঞ্চন", "পানী দিয়া", "আজি পানী"
    ],
    "low_soil_moisture": [
        # English
        "moisture is too low", "soil moisture is low", "soil is dry", "dry soil",
        "the soil moisture is low. should i water my crop", "soil moisture is low. should i water",
        "ground is dry", "plants wilting", "drought stress", "dry ground", "lack of moisture",
        # Telugu
        "తేమ తక్కువ", "నేల ఎండిപോ", "భੂమి పొడిగా", "తేమ కొರత", "ఎండిపోయింది",
        # Hindi
        "नमी बहुत कम", "मिट्टी सूखी", "नमी कम है", "सूखा पड़ रहा है", "सूखी मिट्टी", "सूखी", "सूखा", "नमी कम",
        # Tamil
        "ஈரப்பதம் குறைவு", "மண் வறண்டு", "வறட்சி",
        # Kannada
        "ತೇವಾಂಶ ಕಡಿಮೆ", "ಒಣ ಮಣ್ಣು", "ತೇವಾಂಶ ಕೊರತೆ",
        # Malayalam
        "ഈർപ്പം കുറവ്", "വരണ്ട മണ്ണ്", "വരൾച്ച",
        # Bengali
        "আর্দ্রতা খুব কম", "মাটি শুকিয়ে", "খরা",
        # Marathi
        "ओलावा खूप कमी", "माती सुकली", "ओलावा कमी",
        # Gujarati
        "ભેજ ઓછો", "જમીન સુકાઈ", "ભેજની કમી",
        # Punjabi
        "ਨਮੀ ਬਹੁਤ ਘੱਟ", "ਮਿੱਟੀ ਸੁੱਕੀ", "ਨਮੀ ਦੀ ਘਾਟ",
        # Odia
        "ଆର୍ଦ୍ରତା ବହୁତ କମ୍", "ମାଟି ଶୁଖିଲା",
        # Urdu
        "نمی بہت کم", "خشک مٹی", "خشکی",
        # Assamese
        "আৰ্দ্ৰতা অতি কম", "মাটি শুকান"
    ],
    "reduce_water_waste": [
        # English
        "reduce water wastage", "reduce water waste", "save water", "water conservation",
        "water wastage", "efficient irrigation", "drip efficiency", "prevent water runoff",
        # Telugu
        "నీటి వృధા", "నీటి ఆదా", "నీరు ఆదా", "వృధా తగ్గించు",
        # Hindi
        "पानी की बर्बादी", "जल संरक्षण", "पानी बचाएं", "पानी की बचत",
        # Tamil
        "நீர் வீணாவதை", "நீர் சேமிப்பு", "நீர் விரயம்",
        # Kannada
        "ನೀರಿನ ಪೋಲು", "ನೀರು ಉಳಿಸಿ", "ವ್ಯರ್ಥವಾಗದಂತೆ",
        # Malayalam
        "ജലം പാഴാകുന്നത്", "ജല സംരക്ഷണം", "വെള്ളം ലാഭിക്കുക",
        # Bengali
        "পানির অপচয়", "পানি সংরক্ষণ", "অপচয় রোধ",
        # Marathi
        "पाण्याचा अपव्यय", "पाणी बचत", "पाणी वाया",
        # Gujarati
        "પાણીનો બગાડ", "પાણીની બચત", "બગાડ અટકાવવો",
        # Punjabi
        "ਪਾਣੀ ਦੀ ਬਰਬਾਦੀ", "ਪਾਣੀ ਦੀ ਬਚਤ",
        # Odia
        "ଜଳ ଅପଚୟ", "ପାଣି ସଂରକ୍ଷଣ",
        # Urdu
        "پانی کا ضیاع", "پانی کی بچت", "پانی ضائع",
        # Assamese
        "পানীৰ অপচয়", "পানী সংৰক্ষণ"
    ],
    "soil_fertility": [
        # English
        "improve my soil fertility", "improve soil fertility", "soil fertility", "make soil fertile",
        "soil organic matter", "compost", "fym", "soil health", "enrich soil",
        # Telugu
        "నేల సారవంతం", "సారవంతాన్ని", "భూሚ బలం", "సేంద్రీయ ఎరువు", "మట్టి బలం",
        # Hindi
        "मिट्टी की उर्वरता", "उर्वरता कैसे सुधारें", "उपजाऊ बनाएं", "जैविक खाद", "गोबर की खाद",
        # Tamil
        "மண் வளம்", "மண் வளத்தை", "இயற்கை உரம்",
        # Kannada
        "ಮಣ್ಣಿನ ಫಲವತ್ತತೆ", "ಫಲವತ್ತತೆಯನ್ನು", "ಸಾವಯವ ಗೊಬ್ಬರ",
        # Malayalam
        "മണ്ണിന്റെ ഫലഭൂയിഷ്ഠത", "ഫലഭൂയിഷ്ഠത", "ജൈവവളം",
        # Bengali
        "মাটির উর্বরতা", "উর্বরতা বৃদ্ধি", "জৈব সার",
        # Marathi
        "जमिनीची सुपीकता", "सुपीकता कशी वाढवावी", "सेंद्रिय खत",
        # Gujarati
        "જમીનની ફળદ્રુપતા", "ફળદ્રુપતા કેવી રીતે વધારવી", "સેન્દ્રિય ખાતર",
        # Punjabi
        "ਮਿੱਟੀ ਦੀ ਉਪਜਾਊ ਸ਼ਕਤੀ", "ਉਪਜਾਊ ਸ਼ਕਤੀ", "ਦੇਸੀ ਰੂੜੀ",
        # Odia
        "ମାଟିର ଉର୍ବରତା", "ଉର୍ବରତା ବୃଦ୍ଧି", "ଜୈବିକ ଖତ",
        # Urdu
        "مٹی کی زرخیزی", "زرخیزی کیسے بڑھائیں", "نامیاتی کھاد",
        # Assamese
        "মাটিৰ উৰ্বৰতা", "উৰ্বৰতা বৃদ্ধি", "জৈৱিক সাৰ"
    ],
    "nutrient_deficiencies": [
        # English
        "identify nutrient deficiencies", "nutrient deficiency", "lack of fertilizer",
        "yellow leaves", "purple leaves", "deficiency symptoms", "nitrogen deficiency",
        "zinc deficiency", "chlorosis",
        # Telugu
        "పోషకాల లోపాలు", "పోషక లోపం", "పసుపు ఆకులు", "ఎరువుల లోపం",
        # Hindi
        "पोषक तत्वों की कमी", "पोषक तत्व कमी", "पीली पत्तियां", "खाद की कमी",
        # Tamil
        "ஊட்டச்சத்து குறைபாடு", "தழைச்சத்து குறைபாடு", "மஞ்சள் இலைகள்",
        # Kannada
        "ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ", "ಪೋಷಕಾಂಶ ಕೊರತೆ", "ಹಳದಿ ಎಲೆ",
        # Malayalam
        "പോഷകക്കുറവ്", "ഇല മഞ്ഞളിപ്പ്", "വളക്കുറവ്",
        # Bengali
        "পুষ্টির ঘাটতি", "পুষ্টি ঘাটতি", "হলুদ পাতা",
        # Marathi
        "पोषक घटकांची कमतरता", "अन्नद्रव्यांची कमतरता", "पिवळी पाने",
        # Gujarati
        "પોષક તત્વોની ઉણપ", "તત્વોની ખામી", "પીળા પાંદડા",
        # Punjabi
        "ਪੋਸ਼ਕ ਤੱਤਾਂ ਦੀ ਘਾਟ", "ਖੁਰਾਕੀ ਤੱਤਾਂ ਦੀ ਕਮੀ", "ਪੀਲੇ ਪੱਤੇ",
        # Odia
        "ପୋଷକ ତତ୍ତ୍ୱର ଅଭାବ", "ହଳଦିଆ ପତ୍ର",
        # Urdu
        "غذائی اجزاء کی کمی", "پیلے پتے", "کھاد کی کمی",
        # Assamese
        "পুষ্টিহীনতা", "হালধীয়া পাত"
    ],
    "interpret_analysis": [
        # English
        "interpret my farm analysis results", "interpret analysis results", "farm analysis results",
        "soil test results", "soil report", "how to read soil test", "what does ph mean",
        "npk report", "soil health card meaning",
        # Telugu
        "విశ్లేషణ ఫలితాలు", "ఫలితాలను ఎలా అర్థం", "సాయిల్ రిపోర్ట్", "నేల పరీక్ష ఫలితం",
        # Hindi
        "विश्लेषण रिपोर्ट", "मिट्टी परीक्षण रिपोर्ट", "विश्लेषण परिणाम", "मृदा रिपोर्ट कैसे समझें",
        # Tamil
        "பகுப்பாய்வு முடிவுகள்", "மண் பரிசோதனை அறிக்கை",
        # Kannada
        "ವಿಶ್ಲೇಷಣಾ ಫಲಿತಾಂಶ", "ಮಣ್ಣು ಪರೀಕ್ಷೆ ವರದಿ",
        # Malayalam
        "വിശകലന ഫലങ്ങൾ", "മണ്ണ് പരിശോധനാ റിപ്പോർട്ട്",
        # Bengali
        "বিশ্লেষণ ফলাফল", "মাটি পরীক্ষার রিপোর্ট",
        # Marathi
        "विश्लेषण अहवाल", "माती चाचणी अहवाल",
        # Gujarati
        "વિશ્લેષણ અહેવાલ", "જમીન ચકાસણી અહેવાલ",
        # Punjabi
        "ਵਿਸ਼ਲੇਸ਼ਣ ਰਿਪੋਰਟ", "ਮਿੱਟੀ ਟੈਸਟ ਰਿਪੋਰਟ",
        # Odia
        "ବିଶ୍ଳେଷଣ ଫଳାଫଳ", "ମାଟି ପରୀକ୍ଷା ରିପୋର୍ଟ",
        # Urdu
        "تجزیاتی رپورٹ", "مٹی ٹیسٹ کی رپورٹ",
        # Assamese
        "বিশ্লেষণৰ ফলাফল", "মাটি পৰীক্ষাৰ ফলাফল"
    ],
    "crop_suitability": [
        # English
        "which crop is suitable", "crop is suitable for my soil and climate", "what crop should i grow",
        "suitable crop", "crop suitability", "which crop to plant", "best crop for my land",
        "crop recommendation", "recommend a crop",
        # Telugu
        "ఏ పంట అనుకూలం", "అనుకూలమైన పంట", "ఏ పంట వేయాలి", "నా నేలకు ఏ పంట",
        # Hindi
        "कौन सी फसल उपयुक्त", "कौन सी फसल बोएं", "उपयुक्त फसल", "मेरी मिट्टी के लिए फसल",
        # Tamil
        "எந்த பயிர் ஏற்றது", "உகந்த பயிர்", "என்ன பயிர் நடலாம்",
        # Kannada
        "ಯಾವ ಬೆಳೆ ಸೂಕ್ತ", "ಸೂಕ್ತವಾದ ಬೆಳೆ", "ಯಾವ ಬೆಳೆ ಬೆಳೆಯಬೇಕು",
        # Malayalam
        "ഏത് വിള അനുയോജ്യം", "അനുയോജ്യമായ വിള", "ഏത് വിള കൃഷി ചെയ്യണം",
        # Bengali
        "কোন ফসল উপযুক্ত", "উপযুক্ত ফসল", "কোন ফসল লাগাব",
        # Marathi
        "कोणते पीक योग्य", "योग्य पीक कोणते", "कोणते पीक घ्यावे",
        # Gujarati
        "કયો પાક અનુકૂળ", "યોગ્ય પાક કયો", "કયો પાક વાવવો",
        # Punjabi
        "ਕਿਹੜੀ ਫਸਲ ਢੁਕਵੀਂ", "ਢੁਕਵੀਂ ਫਸਲ", "ਕਿਹੜੀ ਫਸਲ ਬੀਜੀਏ",
        # Odia
        "କେଉଁ ଫସଲ ଉପଯୁକ୍ତ", "ଉପଯୁକ୍ତ ଫସଲ", "କେଉଁ ଫସଲ ଲଗାଇବି",
        # Urdu
        "کون سی فصل موزوں", "موزوں فصل", "کون سی فصل لگائیں",
        # Assamese
        "কোনটো শস্য উপযুক্ত", "উপযুক্ত শস্য"
    ],
    "crop_selection_info": [
        # English
        "what information do i need before selecting a crop", "before selecting a crop",
        "crop selection checklist", "information needed to choose crop", "factors to consider before planting",
        # Telugu
        "పంటను ఎంచుకోవడానికి ముందు", "ఏ సమాచారం అవసరం", "పంట ఎంపిక చెక్‌లిస్ట్",
        # Hindi
        "फसल चुनने से पहले", "किन जानकारियों की आवश्यकता", "फसल चयन से पूर्व",
        # Tamil
        "பயிரைத் தேர்ந்தெடுப்பதற்கு முன்", "என்ன தகவல்கள் தேவை",
        # Kannada
        "ಬೆಳೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡುವ ಮೊದಲು", "ಯಾವ ಮಾಹಿತಿ ಬೇಕು",
        # Malayalam
        "വിള തിരഞ്ഞെടുക്കുന്നതിന് മുൻപ്", "എന്തെല്ലാം കാര്യങ്ങൾ അറിയണം",
        # Bengali
        "ফসল নির্বাচনের আগে", "কী তথ্য জানা প্রয়োজন",
        # Marathi
        "पीक निवडण्यापूर्वी", "कोणती माहिती आवश्यक",
        # Gujarati
        "પાક પસંદ કરતા પહેલા", "કઈ માહિતી જોઈએ",
        # Punjabi
        "ਫਸਲ ਚੁਣਨ ਤੋਂ ਪਹਿਲਾਂ", "ਕਿਹੜੀ ਜਾਣਕਾਰੀ ਚਾਹੀਦੀ",
        # Odia
        "ଫସଲ ବାଛିବା ପୂର୍ବରୁ", "କେଉଁ ସୂଚନା ଆବଶ୍ୟକ",
        # Urdu
        "فصل منتخب کرنے سے پہلے", "کن معلومات کی ضرورت",
        # Assamese
        "শস্য নিৰ্বাচনৰ আগতে", "কি তথ্যৰ প্ৰয়োজন"
    ],
    "next_season_prep": [
        # English
        "prepare my farm for the next growing season", "prepare farm for next season",
        "next growing season", "summer plowing", "pre-season land preparation",
        "prepare field for next crop", "field preparation",
        # Telugu
        "తదుపరి సాగు కాలం", "పొలాన్ని సిద్ధం", "తదుపరి సీజన్", "వేసవి దుక్కి",
        # Hindi
        "अगले सीजन के लिए", "खेत को कैसे तैयार करें", "गर्मी की जुताई", "खेत की तैयारी",
        # Tamil
        "அடுத்த சாகுபடி பருவம்", "பண்ணையை தயார்", "அடுத்த பருவம்",
        # Kannada
        "ಮುಂದಿನ ಋತುವಿಗಾಗಿ", "ಹೊಲವನ್ನು ಸಿದ್ಧಪಡಿಸುವುದು", "ಮುಂದಿನ ಹಂಗಾಮು",
        # Malayalam
        "അടുത്ത കൃഷി സീസൺ", "കൃഷിയിടം ഒരുക്കുക",
        # Bengali
        "পরবর্তী মৌসুমের জন্য", "জমি প্রস্তুত", "পরবর্তী মরশুম",
        # Marathi
        "पुढील हंगामासाठी", "शेत कसे तयार करावे", "उन्हाळी नांगरणी",
        # Gujarati
        "આગામી સીઝન માટે", "ખેતર કેવી રીતે તૈયાર કરવું", "ઉનાળુ ખેડ",
        # Punjabi
        "ਅਗਲੇ ਸੀਜ਼ਨ ਲਈ", "ਖੇਤ ਕਿਵੇਂ ਤਿਆਰ ਕਰਨਾ",
        # Odia
        "ପରବର୍ତ୍ତୀ ଋତୁ ପାଇଁ", "ଜମି ପ୍ରସ୍ତୁତ",
        # Urdu
        "اگلے سیزن کے لیے", "کھیت کو کیسے تیار کریں", "گرمیوں کی جوتائی",
        # Assamese
        "পৰৱৰ্তী বতৰৰ বাবে", "পাম কেনেকৈ প্ৰস্তুত"
    ],
    "crop_diseases": [
        # English
        "common diseases affecting my crop", "diseases affecting my crop", "crop diseases",
        "common pests", "fungus on crop", "blight", "rust", "blast", "wilt", "borer",
        # Telugu
        "సాధారణ తెగుళ్లు", "వ్యాధులు ఏమిటి", "పంట తెగుళ్లు", "పంట వ్యాధులు",
        # Hindi
        "सामान्य रोग कौन से हैं", "फसल के रोग", "कीट व रोग", "प्रमुख बीमारियां",
        # Tamil
        "பொதுவான நோய்கள்", "பயிர் நோய்கள்", "தாக்கும் நோய்கள்",
        # Kannada
        "ಸಾಮಾನ್ಯ ರೋಗಗಳು", "ಬೆಳೆ ರೋಗಗಳು", "ಬಾಧಿಸುವ ರೋಗಗಳು",
        # Malayalam
        "സാധാരണ രോഗങ്ങൾ", "വിള രോഗങ്ങൾ", "പ്രധാന രോഗങ്ങൾ",
        # Bengali
        "সাধারণ কোন রোগগুলো", "ফসলের রোগ", "প্রধান রোগবালাই",
        # Marathi
        "सामान्य रोग कोणते", "पिकावरील रोग", "मुख्य रोग",
        # Gujarati
        "સામાન્ય રોગો કયા", "પાકના રોગો", "મુખ્ય જીવાતો",
        # Punjabi
        "ਮੁੱਖ ਬਿਮਾਰੀਆਂ ਕਿਹੜੀਆਂ", "ਫਸਲ ਦੀਆਂ ਬਿਮਾਰੀਆਂ",
        # Odia
        "ସାଧାରଣ ରୋଗଗୁଡ଼ିକ", "ଫସଲ ରୋଗ",
        # Urdu
        "عام بیماریاں کون سی", "فصل کی بیماریاں",
        # Assamese
        "সাধাৰণ ৰোগসমূহ", "শস্যৰ ৰোগ"
    ],
    "disease_early_signs": [
        # English
        "identify early signs of crop disease", "early signs of crop disease", "early symptoms",
        "how to spot disease early", "early signs", "disease detection", "scouting signs",
        # Telugu
        "ప్రారంభ సంకేతాలు", "లక్షణాలను ఎలా గుర్తించాలి", "వ్యాధి లక్షణాలు", "తెగులు గుర్తింపు",
        # Hindi
        "शुरुआती लक्षणों को कैसे पहचानें", "रोग के शुरुआती लक्षण", "प्रारंभिक लक्षण",
        # Tamil
        "ஆரம்ப அறிகுறிகள்", "நோயின் ஆரம்ப அறிகுறிகள்",
        # Kannada
        "ಆರಂಭಿಕ ಲಕ್ಷಣಗಳು", "ರೋಗದ ஆரம்ப ಲಕ್ಷಣ",
        # Malayalam
        "ആദ്യ ലക്ഷണങ്ങൾ", "പ്രാരംഭ രോഗ ലക്ഷണങ്ങൾ",
        # Bengali
        "প্রাথমিক লক্ষণ কীভাবে শনাক্ত", "রোগের প্রাথমিক লক্ষণ",
        # Marathi
        "सुरुवातीची लक्षणे कशी ओळखावीत", "रोगाची सुरुवातीची लक्षणे",
        # Gujarati
        "પ્રારંભિક લક્ષણો કેવી રીતે ઓળખવા", "રોગના શરૂઆતના લક્ષણો",
        # Punjabi
        "ਸ਼ੁਰੂਆਤੀ ਲੱਛਣਾਂ ਦੀ ਪਛਾਣ", "ਬਿਮਾਰੀ ਦੇ ਲੱਛਣ",
        # Odia
        "ପ୍ରାରମ୍ଭିକ ଲକ୍ଷଣ କିପରି ଚିହ୍ନଟ", "ରୋଗର ଲକ୍ଷଣ",
        # Urdu
        "ابتدائی علامات کی شناخت", "بیماری کی ابتدائی علامات",
        # Assamese
        "প্ৰাৰম্ভিক লক্ষণ কেনেকৈ চিনাক্ত"
    ],
    "pest_resistance": [
        # English
        "improve my crop's resistance to pests", "resistance to pests", "pest resistance",
        "boost plant immunity", "prevent insect attacks", "ipm", "natural pest control",
        "control pests", "pest control", "pests", "pest", "insects", "insect", "neem oil", "organic pest",
        # Telugu
        "తెగుళ్లను తట్టుకునే శక్తి", "నిరోధకత పెంపు", "రోగ నిరోధక శక్తి", "పురుగుల నివారణ", "పురుగుల మందు", "పురుగులు",
        # Hindi
        "कीटों के प्रति प्रतिरोधक क्षमता", "रोग प्रतिरोधक क्षमता कैसे बढ़ाएं", "कीट प्रतिरोधी", "कीट नियंत्रण", "कीट", "नीम तेल",
        # Tamil
        "பூச்சிகளை எதிர்க்கும் திறன்", "நோய் எதிர்ப்பு திறன்",
        # Kannada
        "ಕೀಟಗಳನ್ನು ತಡೆದುಕೊಳ್ಳುವ ಶಕ್ತಿ", "ರೋಗ ನಿರೋಧಕ ಶಕ್ತಿ",
        # Malayalam
        "കീടപ്രതിരോധശേഷി", "രോഗപ്രതിരോധശേഷി",
        # Bengali
        "রোগ ও পোকা প্রতিরোধ ক্ষমতা", "প্রতিরোধ ক্ষমতা বৃদ্ধি",
        # Marathi
        "कीड प्रतिकारशक्ती कशी वाढवावी", "रोगप्रतिकારशक्ती",
        # Gujarati
        "જીવાત સામે પ્રતિકારક શક્તિ", "રોગ પ્રતિકારક શક્તિ",
        # Punjabi
        "ਕੀੜਿਆਂ ਵਿਰੁੱਧ ਲੜਨ ਦੀ ਸਮਰੱਥਾ", "ਰੋਗ ਪ੍ਰਤੀਰੋਧਕ ਸ਼ਕਤੀ",
        # Odia
        "ରୋଗ ପ୍ରତିରୋଧକ ଶକ୍ତି", "ପୋକ ପ୍ରତିରୋଧକ",
        # Urdu
        "کیڑوں کے خلاف مدافعت", "قوت مدافعت کیسے بڑھائیں",
        # Assamese
        "কীট প্ৰতিৰোধ ক্ষমতা", "ৰোগ প্ৰতিৰোধ"
    ],
    "daily_priorities": [
        # English
        "farming activities should i prioritize today", "prioritize today", "activities today",
        "today's farming plan", "what to do today", "daily tasks", "today's priorities",
        # Telugu
        "ఈరోజు ఏ పనులకు ప్రాధాన్యత", "నేటి పనులు", "ఈరోజు చేయవలసిన పనులు",
        # Hindi
        "किन कृषि कार्यों को प्राथमिकता दें", "आज के प्राथमिक कार्य", "आज क्या करें",
        # Tamil
        "எந்த பணிகளுக்கு முன்னுரிமை", "இன்றைய முக்கிய பணிகள்",
        # Kannada
        "ಯಾವ ಕೆಲಸಗಳಿಗೆ ಆದ್ಯತೆ", "ಇಂದಿನ ಮುಖ್ಯ ಕೆಲಸಗಳು",
        # Malayalam
        "ഏതെല്ലാം ജോലികൾക്ക് മുൻഗണന", "ഇന്നത്തെ മുൻഗണനകൾ",
        # Bengali
        "কোন কাজকে অগ্রাধিকার", "আজকের করণীয় কাজ",
        # Marathi
        "कोणत्या कामांना प्राधान्य द्यावे", "आजची महत्त्वाची कामे",
        # Gujarati
        "કયા કાર્યોને પ્રાથમિકતા આપવી", "આજના મુખ્ય કાર્યો",
        # Punjabi
        "ਕਿਹੜੇ ਕੰਮਾਂ ਨੂੰ ਪਹਿਲ ਦੇਣੀ", "ਅੱਜ ਦੇ ਮੁੱਖ ਕੰਮ",
        # Odia
        "କେଉଁ କାର୍ଯ୍ୟକୁ ଅଗ୍ରାଧିକାର", "ଆଜିର ପ୍ରମୁଖ କାର୍ଯ୍ୟ",
        # Urdu
        "کن زرعی کاموں کو ترجیح دیں", "آج کے ترجیحی کام",
        # Assamese
        "কোনবোৰ কামক অগ্ৰাধিকাৰ", "আজিৰ প্ৰধান কাম"
    ],
    "growth_stage_care": [
        # English
        "improve crop growth during the current growth stage", "current growth stage",
        "growth stage care", "tillering stage", "flowering stage", "vegetative care",
        "seedling care", "stage management",
        # Telugu
        "ప్రస్తుత పెరుగుదల దశ", "దశలో పంట ఎదుగుదల", "పూత దశ సంరక్షణ", "శాఖీయ దశ",
        # Hindi
        "वर्तमान वृद्धि अवस्था", "वृद्धि अवस्था में फसल की बढ़वार", "फूल आने की अवस्था", "कल्ले फूटने पर",
        # Tamil
        "வளர்ச்சி பருவத்தில்", "பருவ மேலாண்மை", "பூக்கும் பருவம்",
        # Kannada
        "ಬೆಳವಣಿಗೆಯ ಹಂತದಲ್ಲಿ", "ಹಂತದ ನಿರ್ವಹಣೆ", "ಹೂ ಬಿಡುವ ಹಂತ",
        # Malayalam
        "വളർച്ചാ ഘട്ടത്തിൽ", "ഘട്ട പരിചരണം", "പൂക്കുന്ന സമയം",
        # Bengali
        "বৃদ্ধির পর্যায়ে", "বর্তমান পর্যায় পরিচর্যা",
        # Marathi
        "वाढीच्या अवस्थेत", "अवस्था व्यवस्थापन", "फुलोरा अवस्था",
        # Gujarati
        "વિકાસના તબક્કે", "વૃદ્ધિ તબક્કાની સંભાળ",
        # Punjabi
        "ਵਾਧੇ ਦੇ ਪੜਾਅ ਦੌਰਾਨ", "ਫਸਲ ਵਾਧਾ ਸੰਭਾਲ",
        # Odia
        "ବୃଦ୍ଧି ପର୍ଯ୍ୟାୟରେ", "ପର୍ଯ୍ୟାୟ ଯତ୍ନ",
        # Urdu
        "نشوونما کے مرحلے میں", "مرحلے کی دیکھ بھال",
        # Assamese
        "বৃদ্ধিৰ পৰ্যায়ত", "বৃদ্ধি পৰ্যায়ৰ যত্ন"
    ],
    "heavy_rain_action": [
        # English
        "when heavy rain is expected", "heavy rain expected", "heavy rain", "rain coming",
        "rain precaution", "storm care", "waterlogging care", "flood in field",
        # Telugu
        "భారీ వర్షం", "వర్షం పడే అవకాశం", "వాన జాగ్రత్తలు", "ముంపు నివారణ",
        # Hindi
        "भारी बारिश की संभावना", "भारी बारिश", "बारिश से बचाव", "जलभराव से बचाव",
        # Tamil
        "கனமழை எதிர்பார்க்கப்படும் போது", "கனமழை முன்னெச்சரிக்கை", "மழை பாதுகாப்பு",
        # Kannada
        "ಭಾರೀ ಮಳೆಯ ಮುನ್ಸೂಚನೆ", "ಭಾರೀ ಮಳೆ", "ಮಳೆಯಿಂದ ರಕ್ಷಣೆ",
        # Malayalam
        "ശക്തമായ മഴ പ്രതീക്ഷിക്കുമ്പോൾ", "കനത്ത മഴ മുൻകരുതൽ",
        # Bengali
        "ভারী বৃষ্টির পূর্বাভাস", "ভারী বৃষ্টি", "বৃষ্টির সতর্কতা",
        # Marathi
        "मुसळधार पावसाची शक्यता", "मुसळधार पाऊस काळजी",
        # Gujarati
        "ભારે વરસાદની શક્યતા", "ભારે વરસાદથી બચાવ",
        # Punjabi
        "ਭਾਰੀ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ", "ਭਾਰੀ ਮੀਂਹ ਸਾਵਧਾਨੀ",
        # Odia
        "ପ୍ରବଳ ବର୍ଷା ସମ୍ଭାବନା", "ପ୍ରବଳ ବର୍ଷା ସତର୍କତା",
        # Urdu
        "شدید بارش کی پیش گوئی", "تیز بارش سے بچاؤ", "شدید بارش",
        # Assamese
        "প্ৰবল বৰষুণৰ সম্ভাৱনা", "প্ৰবল বৰষুণৰ সাৱধানতা"
    ]
}


# ==============================================================================
# 3. INTENT DETECTION ENGINE
# ==============================================================================
def detect_intent(query: str, question_id: Optional[str] = None) -> str:
    """
    Identifies the farmer's agronomic intent from direct button clicks,
    exact question strings, or natural conversational queries across 14 languages.
    """
    # 1. Direct Question ID match (from button clicks)
    if question_id and question_id in QID_TO_INTENT:
        return QID_TO_INTENT[question_id]

    q_clean = query.strip().lower()
    if not q_clean:
        return "general_help"

    # 2. Exact match against COMMON_QUESTIONS full questions or chips across all languages
    for q in COMMON_QUESTIONS:
        full_key = q["full_key"]
        chip_key = q["chip_key"]
        # Check against English and all supported languages
        for lang_code in SUPPORTED_LANGUAGES.keys():
            full_txt = t(full_key, lang=lang_code).lower()
            chip_txt = t(chip_key, lang=lang_code).lower()
            if q_clean == full_txt or q_clean == chip_txt:
                return q["intent"]
            # Substring match if full question text is contained
            if len(full_txt) > 8 and full_txt in q_clean:
                return q["intent"]

    # 3. Keyword and semantic pattern match
    best_intent = "general_help"
    max_score = 0

    for intent, kws in INTENT_KEYWORDS.items():
        score = 0
        for kw in kws:
            kw_clean = kw.lower()
            if kw_clean in q_clean:
                # Longer phrases get higher weight
                score += len(kw_clean.split()) * 2 + 1
        if score > max_score:
            max_score = score
            best_intent = intent

    return best_intent


# ==============================================================================
# 4. STRUCTURED DATA PROVENANCE HELPER
# ==============================================================================
def _build_provenance_block(
    lang: str,
    crop: str,
    stage: str,
    moisture: Optional[float],
    temp: Optional[float],
    rain_prob: Optional[float],
    weather_source: str,
    system: str
) -> str:
    """Formats honest data provenance clearly distinguishing live readings and estimates."""
    weather_label = f"{temp:.1f}°C, {rain_prob:.0f}% Rain Chance ({weather_source})" if temp is not None else "Regional Climate Benchmark"
    moisture_str = f"{moisture:.1f}% (Observed)" if moisture is not None else "Not Recorded Today (Using Crop Rules)"

    if lang == "te":
        return (
            f"• **పంట & దశ:** {crop} ({stage})\n"
            f"• **క్షేత్ర తేమ:** {moisture_str}\n"
            f"• **వాతావరణం:** {weather_label}\n"
            f"• **నీటిపారుదల వ్యవస్థ:** {system}"
        )
    elif lang == "hi":
        return (
            f"• **फसल व अवस्था:** {crop} ({stage})\n"
            f"• **मिट्टी की नमी:** {moisture_str}\n"
            f"• **मौसम:** {weather_label}\n"
            f"• **सिंचाई प्रणाली:** {system}"
        )
    elif lang == "ta":
        return (
            f"• **பயிர் & பருவம்:** {crop} ({stage})\n"
            f"• **மண் ஈரப்பதம்:** {moisture_str}\n"
            f"• **வானிலை:** {weather_label}\n"
            f"• **பாசன முறை:** {system}"
        )
    elif lang == "kn":
        return (
            f"• **ಬೆಳೆ & ಹಂತ:** {crop} ({stage})\n"
            f"• **ಮಣ್ಣಿನ ತೇವಾಂಶ:** {moisture_str}\n"
            f"• **ಹವಾಮಾನ:** {weather_label}\n"
            f"• **ನೀರಾವರಿ:** {system}"
        )
    elif lang == "ml":
        return (
            f"• **വിള & ഘട്ടം:** {crop} ({stage})\n"
            f"• **മണ്ണിലെ ഈർപ്പം:** {moisture_str}\n"
            f"• **കാലാവസ്ഥ:** {weather_label}\n"
            f"• **ജലസേಚനം:** {system}"
        )
    elif lang == "bn":
        return (
            f"• **ফসল ও পর্যায়:** {crop} ({stage})\n"
            f"• **মাটির আর্দ্রতা:** {moisture_str}\n"
            f"• **আবহাওয়া:** {weather_label}\n"
            f"• **সেচ ব্যবস্থা:** {system}"
        )
    elif lang == "mr":
        return (
            f"• **पीक व अवस्था:** {crop} ({stage})\n"
            f"• **मातीतील ओलावा:** {moisture_str}\n"
            f"• **हवामान:** {weather_label}\n"
            f"• **सिंचन पद्धत:** {system}"
        )
    elif lang == "gu":
        return (
            f"• **પાક અને તબક્કો:** {crop} ({stage})\n"
            f"• **જમીનનો ભેજ:** {moisture_str}\n"
            f"• **હવામાન:** {weather_label}\n"
            f"• **પિયત પદ્ધતિ:** {system}"
        )
    elif lang == "pa":
        return (
            f"• **ਫਸਲ ਅਤੇ ਪੜਾਅ:** {crop} ({stage})\n"
            f"• **ਮਿੱਟੀ ਦੀ ਨਮੀ:** {moisture_str}\n"
            f"• **ਮੌਸਮ:** {weather_label}\n"
            f"• **ਸਿੰਚਾਈ ਪ੍ਰਣਾਲੀ:** {system}"
        )
    elif lang == "or":
        return (
            f"• **ଫସଲ ଓ ପର୍ଯ୍ୟାୟ:** {crop} ({stage})\n"
            f"• **ମାଟିର ଆର୍ଦ୍ରତା:** {moisture_str}\n"
            f"• **ପାଣିପାଗ:** {weather_label}\n"
            f"• **ଜଳସେଚନ ପଦ୍ଧତି:** {system}"
        )
    elif lang == "ur":
        return (
            f"• **فصل اور مرحلہ:** {crop} ({stage})\n"
            f"• **مٹی کی نمی:** {moisture_str}\n"
            f"• **موسم:** {weather_label}\n"
            f"• **آبپاشی کا نظام:** {system}"
        )
    elif lang == "as":
        return (
            f"• **শস্য আৰু পৰ্যায়:** {crop} ({stage})\n"
            f"• **মাটিৰ আৰ্দ্ৰতা:** {moisture_str}\n"
            f"• **বতৰ:** {weather_label}\n"
            f"• **জলসিঞ্চন ব্যৱস্থা:** {system}"
        )
    elif lang == "sa":
        return (
            f"• **सस्यं दशा च:** {crop} ({stage})\n"
            f"• **मृत्तिकाया आर्द्रता:** {moisture_str}\n"
            f"• **ऋतुवृत्तान्तः:** {weather_label}\n"
            f"• **सेचनपद्धतिः:** {system}"
        )
    else:
        return (
            f"• **Crop & Growth Stage:** {crop} ({stage})\n"
            f"• **Soil Hydration Status:** {moisture_str}\n"
            f"• **Atmospheric Conditions:** {weather_label}\n"
            f"• **Irrigation Infrastructure:** {system}"
        )


# ==============================================================================
# 5. AGRONOMIC KNOWLEDGE BASE & RESPONSE GENERATOR
# ==============================================================================
def generate_response(
    intent: str,
    lang: str,
    farm_context: Dict[str, Any],
    latest_reading: Optional[Dict[str, Any]],
    weather_data: Optional[Dict[str, Any]]
) -> str:
    """
    Constructs a deterministic, professional, structured agricultural response:
    1. Direct Answer
    2. Farm Context & Data Used (distinguishing live, manual, and rule thresholds)
    3. Scientific Agronomic Reasoning
    4. Practical Next Steps
    5. Operational Directive
    """
    active_lang = lang if lang in SUPPORTED_LANGUAGES else "en"

    # Extract farm context
    crop = (farm_context or {}).get("primary_crop") or (latest_reading or {}).get("crop_type") or "General Crop"
    soil = (farm_context or {}).get("soil_type", "Loam")
    system = (farm_context or {}).get("irrigation_system", "Drip")
    district = (farm_context or {}).get("location_district", "Farm Parcel")
    stage = (latest_reading or {}).get("growth_stage", "Vegetative")

    moisture = (latest_reading or {}).get("soil_moisture") if latest_reading else None
    temp = (weather_data or {}).get("temperature") if weather_data else ((latest_reading or {}).get("temperature") if latest_reading else 28.0)
    rain_prob = (weather_data or {}).get("rain_prob_today", 15.0) if weather_data else 15.0
    w_source = (weather_data or {}).get("source_label", "Open-Meteo Live") if weather_data else "Benchmark Standard"

    # Section Headings
    h_direct = t("lbl_direct_answer", active_lang)
    h_context = t("lbl_farm_context", active_lang)
    h_reasoning = t("lbl_reasoning", active_lang)
    h_steps = t("lbl_next_steps", active_lang)
    h_notice = t("lbl_field_notice", active_lang)

    provenance = _build_provenance_block(
        active_lang, crop, stage, moisture, temp, rain_prob, w_source, system
    )

    # -------------------------------------------------------------------------
    # INTENT 1: irrigation_today (Q1)
    # -------------------------------------------------------------------------
    if intent == "irrigation_today":
        if rain_prob >= 50.0:
            direct = {
                "en": f"💧 **Withhold scheduled irrigation today.** Rain probability is high ({rain_prob:.0f}%). Let natural precipitation recharge root moisture and prevent waterlogging.",
                "te": f"💧 **ఈరోజు షెడ్యూల్ చేసిన నీటిపారుదలను నిలిపివేయండి.** వర్షం పడే అవకాశం ఎక్కువగా ఉంది ({rain_prob:.0f}%). సహజ వర్షపాతం వల్ల నేలలో తేమ పెరుగుతుంది మరియు నీరు నిలవకుండా కాపాడుతుంది.",
                "hi": f"💧 **आज निर्धारित सिंचाई स्थगित रखें।** बारिश की संभावना अधिक है ({rain_prob:.0f}%)। प्राकृतिक वर्षा से जड़ क्षेत्र में नमी आएगी और जलभराव से बचाव होगा।",
            }.get(active_lang, f"💧 **Withhold scheduled irrigation today.** Rain probability is high ({rain_prob:.0f}%). Natural rainfall will replenish soil moisture.")
        elif moisture is not None and moisture < 50.0:
            direct = {
                "en": f"💧 **Initiate active irrigation today.** Soil moisture is currently {moisture:.1f}%, which is below the optimal threshold for {crop} ({stage}). Run your {system} system during the early morning hours.",
                "te": f"💧 **ఈరోజు నీటిపారుదల ప్రారంభించండి.** నేలలో తేమ ప్రస్తుతం {moisture:.1f}% మాత్రమే ఉంది, ఇది {crop} ({stage}) దశకు అవసరమైన దానికంటే తక్కువ. ఉదయాన్నే మీ {system} ద్వారా నీరు పెట్టండి.",
                "hi": f"💧 **आज सिंचाई अवश्य करें।** वर्तमान मिट्टी की नमी {moisture:.1f}% है, जो {crop} ({stage}) के लिए निर्धारित सीमा से कम है। सुबह के समय {system} से पानी दें।",
            }.get(active_lang, f"💧 **Initiate irrigation today.** Soil moisture is {moisture:.1f}%, below target for {crop}. Irrigate during early morning.")
        elif moisture is not None and moisture >= 75.0:
            direct = {
                "en": f"💧 **No irrigation needed today.** Observed soil moisture is optimal ({moisture:.1f}%) for {crop}. Excess watering risks root asphyxiation and fungal collar rot.",
                "te": f"💧 **ఈరోజు నీరు పెట్టవలసిన అవసరం లేదు.** {crop} కోసం నేలలో తేమ ({moisture:.1f}%) అనుకూలంగా ఉంది. ఎక్కువ నీరు పెడితే వేరుకుళ్లు తెగులు వచ్చే ప్రమాదం ఉంది.",
                "hi": f"💧 **आज सिंचाई की आवश्यकता नहीं है।** मिट्टी में पर्याप्त नमी ({moisture:.1f}%) उपलब्ध है। अधिक पानी देने से जड़ गलन रोग का खतरा रहता है।",
            }.get(active_lang, f"💧 **No irrigation needed today.** Soil moisture is optimal ({moisture:.1f}%) for {crop}.")
        else:
            direct = {
                "en": f"💧 **Apply moderate irrigation based on crop stage.** For {crop} in {stage} stage, maintain steady root hydration. Early morning application (05:30–08:30 AM) maximizes water efficiency.",
                "te": f"💧 **పంట దశను బట్టి మితమైన నీరు పెట్టండి.** {crop} ({stage}) దశలో స్థిరమైన తేమ అవసరం. ఉదయం (05:30–08:30) నీరు పెట్టడం వల్ల ఆవిరి నష్టం తగ్గుతుంది.",
                "hi": f"💧 **फसल अवस्था अनुसार संतुलित सिंचाई करें।** {crop} ({stage}) के लिए जड़ क्षेत्र में नमी बनाए रखें। सुबह 05:30 से 08:30 के बीच सिंचाई करें।",
            }.get(active_lang, f"💧 **Apply balanced irrigation for {crop} ({stage}).** Irrigate early morning.")

        reasoning = {
            "en": f"• Water requirements peak during reproductive tillering and flowering phases.\n• Evaporative loss peaks above 30°C; early morning application reduces evapotranspiration loss by up to 35%.\n• Consistent moisture prevents blossom-end rot and hydraulic stress.",
            "te": f"• పూత మరియు గింజ పాలుపోసుకునే దశలో నీటి అవసరం అత్యధికంగా ఉంటుంది.\n• ఎండ తీవ్రత పెరిగే కొద్దీ ఆవిరి నష్టం 35% వరకు పెరుగుతుంది, కాబట్టి ఉదయాన్నే నీరు పెట్టడం శ్రేయస్కరం.\n• సమానమైన తేమ ఉండటం వల్ల కాయల నాణ్యత పెరుగుతుంది.",
            "hi": f"• फूल आने और दाना भरने की अवस्था में फसल को सबसे अधिक पानी की आवश्यकता होती है।\n• दोपहर की धूप में वाष्पीकरण से 35% पानी नष्ट होता है, अतः सुबह सिंचाई सर्वोत्तम है।\n• नियमित नमी से फल फटने और फूल झड़ने की समस्या नहीं होती।"
        }.get(active_lang, f"• Critical watering stage: early morning reduces evaporation loss by 35%.\n• Maintain uniform root hydration.")

        steps = {
            "en": f"1. Inspect furrow outlets and ensure {system} drippers/nozzles are unclogged.\n2. If rain occurs today, shut off secondary valves immediately.\n3. Verify topsoil moisture at 10–15 cm root depth using a soil auger or probe.",
            "te": f"1. మీ {system} డ్రిప్పర్లు లేదా పైపులలో పూడిక లేకుండా తనిఖీ చేయండి.\n2. ఒకవేళ వర్షం పడితే నీటిపారుదల మోటారును వెంటనే ఆపివేయండి.\n3. వేరు వ్యవస్థ వద్ద (10-15 సెం.మీ లోతులో) తేమను పరిశీలించండి.",
            "hi": f"1. अपनी {system} ड्रिप या नोजल की जांच करें कि कोई रुकावट न हो।\n2. यदि बारिश हो तो तुरंत सिंचाई पंप बंद कर दें।\n3. जड़ क्षेत्र में 10-15 सेमी गहराई पर नमी की जांच करें।"
        }.get(active_lang, f"1. Check {system} system nozzles.\n2. Withhold if rain starts.\n3. Check moisture at 10-15 cm depth.")

        notice = "Deterministic calculation using crop thresholds from rules.py and live weather forecast."

    # -------------------------------------------------------------------------
    # INTENT 2: low_soil_moisture (Q6)
    # -------------------------------------------------------------------------
    elif intent == "low_soil_moisture":
        direct = {
            "en": f"⚠️ **Immediate corrective watering protocol required.** Soil moisture deficit causes stomatal closure, reduced photosynthesis, and flower abortion in {crop}.",
            "te": f"⚠️ **తక్షణమే తేమ సంరక్షణ చర్యలు చేపట్టండి.** నేలలో తేమ తగ్గడం వల్ల {crop} లో ఆకులు వాడిపోవడం, కిరణజన్య సంయోగక్రియ మందగించడం మరియు పూత రాలడం జరుగుతుంది.",
            "hi": f"⚠️ **तत्काल सुधारात्मक सिंचाई की आवश्यकता है।** मिट्टी में नमी की कमी से {crop} में पत्तियां मुरझाने लगती हैं और फूल झड़ने का खतरा बढ़ जाता है।"
        }.get(active_lang, f"⚠️ **Immediate corrective watering protocol required.** Soil moisture deficit causes plant stress.")

        reasoning = {
            "en": f"• Dry soil shrinks and creates root fissures, shearing delicate root hairs.\n• High ambient temperature coupled with dry soil induces severe wilting and leaf drop.\n• Rapid flood irrigation on extremely dry cracked clay causes root shock; gradual drip irrigation is ideal.",
            "te": f"• నేల ఎండిపోయి నెర్రెలు బారినప్పుడు వేర్లకు గాలి తగిలి దెబ్బతింటాయి.\n• ఎండిన నేలపై ఒకేసారి ఎక్కువ నీరు పారగడితే మొక్కలు షాక్‌కు గురవుతాయి; డ్రిప్ ద్వారా నెమ్మదిగా తడపడం శ్రేయస్కరం.\n• గడ్డి లేదా ఆకులతో మల్చింగ్ చేయడం వల్ల తేమ ఆవిరి కాకుండా ఉంటుంది.",
            "hi": f"• अत्यधिक सूखी मिट्टी में दरारें पड़ने से बारीक जड़ें टूट जाती हैं।\n• सूखी जमीन पर अचानक भारी पानी भरने के बजाय ड्रिप से धीरे-धीरे पानी देना बेहतर होता है।\n• जैविक मल्चिंग करने से मिट्टी की नमी लंबे समय तक बनी रहती है।"
        }.get(active_lang, f"• Avoid flooding cracked soil; apply gradual watering via drip.\n• Mulch to conserve root zone moisture.")

        steps = {
            "en": f"1. Run a 45–60 minute gradual drip cycle during early morning or late afternoon.\n2. Apply a 5–7 cm layer of crop residue/straw mulch along crop rows to suppress evaporative loss.\n3. Avoid heavy chemical fertilizer top-dressing until soil moisture returns to 60%.",
            "te": f"1. ఉదయం లేదా సాయంత్రం వేళల్లో 45–60 నిమిషాలు డ్రిప్ ద్వారా నీరు పెట్టండి.\n2. తేమ ఆవిరి కాకుండా సాళ్ల మధ్య ఎండుగడ్డి లేదా ఆకులతో 5-7 సెం.మీ మల్చింగ్ చేయండి.\n3. నేలలో తేమ 60% కి చేరే వరకు రసాయన ఎరువులు వేయవద్దు.",
            "hi": f"1. सुबह या शाम के समय 45-60 मिनट तक ड्रिप से हल्की सिंचाई करें।\n2. क्यारियों के बीच पुआल या सूखी घास की 5-7 सेमी मल्चिंग बिछाएं।\n3. जब तक मिट्टी में नमी सामान्य न हो जाए, तब तक रासायनिक खाद न डालें।"
        }.get(active_lang, f"1. Irrigate gradually for 45-60 mins.\n2. Apply organic mulch.\n3. Defer chemical fertilizers until hydrated.")

        notice = "Advisory grounded in moisture regime rules. No sensor hardware claimed unless logged."

    # -------------------------------------------------------------------------
    # INTENT 3: reduce_water_waste (Q7)
    # -------------------------------------------------------------------------
    elif intent == "reduce_water_waste":
        direct = {
            "en": f"🔄 **Adopt Precision Micro-Irrigation & Evaporation Shields.** You can reduce farm water consumption by 30–45% without sacrificing yield.",
            "te": f"🔄 **బిందు సేద్యం (డ్రిప్) మరియు నీటి సంరక్షణ పద్ధతులను పాటించండి.** పంట దిగుబడి తగ్గకుండానే నీటి వినియోగాన్ని 30–45% వరకు ఆదా చేయవచ్చు.",
            "hi": f"🔄 **सूक्ष्म सिंचाई (ड्रिप) और जल संरक्षण तकनीक अपनाएं।** आप बिना पैदावार घटाए पानी की खपत 30-45% तक कम कर सकते हैं।"
        }.get(active_lang, f"🔄 **Adopt precision micro-irrigation.** Conserve 30-45% water without yield reduction.")

        reasoning = {
            "en": f"• Midday furrow irrigation loses over 40% of applied water to solar evaporation and deep seepage.\n• Drip systems apply water directly to the root zone at low pressure, minimizing weed growth in furrows.\n• For Rice, Alternate Wetting and Drying (AWD) saves up to 30% water and reduces methane emissions.",
            "te": f"• మధ్యాహ్నం వేళల్లో నీరు పారగడితే 40% కంటే ఎక్కువ నీరు ఆవిరి రూపంలో వృధా అవుతుంది.\n• డ్రిప్ విధానంలో నీరు నేరుగా వేర్ల వద్దకే అందుతుంది, కలుపు మొక్కల పెరుగుదల తగ్గుతుంది.\n• వరిలో 'ఆరుతడి - తడి' (AWD) పద్ధతి ద్వారా 30% నీరు ఆదా అవుతుంది.",
            "hi": f"• दोपहर में खुली सिंचाई करने से 40% से अधिक पानी वाष्पीकरण से बर्बाद हो जाता है।\n• ड्रिप सिंचाई से पानी सीधे जड़ों तक पहुंचता है और खरपतवार नहीं पनपते।\n• धान में 'वैकल्पिक गीला और सूखा' (AWD) पद्धति से 30% पानी की बचत होती है।"
        }.get(active_lang, f"• Avoid midday watering.\n• Use drip or AWD in paddy.\n• Mulching prevents soil moisture loss.")

        steps = {
            "en": f"1. Schedule all irrigation exclusively between 05:30–08:30 AM.\n2. Clean inline drip filters and acid-flush emitters once every season to clear mineral deposits.\n3. Implement organic straw mulching to lock in soil humidity.",
            "te": f"1. నీటిపారుదల సమయాన్ని ఉదయం 05:30 నుండి 08:30 మధ్య మాత్రమే కేటాయించండి.\n2. డ్రిప్ ఫిల్టర్లను క్రమం తప్పకుండా శుభ્રం చేయండి.\n3. పొలంలో తేమ ఆవిరి కాకుండా సేంద్రీయ మల్చింగ్ ఉపయోగించండి.",
            "hi": f"1. सिंचाई का समय केवल सुबह 05:30 से 08:30 बजे के बीच रखें।\n2. ड्रिप पाइप और फिल्टर की नियमित सफाई करें।\n3. खेत में पुआल से मल्चिंग करें ताकि जमीन की नमी बची रहे।"
        }.get(active_lang, f"1. Irrigate only 05:30-08:30 AM.\n2. Clean drip filters regularly.\n3. Apply straw mulch.")

        notice = "Water efficiency directives based on Indian Council of Agricultural Research (ICAR) benchmarks."

    # -------------------------------------------------------------------------
    # INTENT 4: soil_fertility (Q2)
    # -------------------------------------------------------------------------
    elif intent == "soil_fertility":
        direct = {
            "en": f"🌱 **Build Organic Biomass & Adopt Soil Health Card N-P-K Balancing.** Healthy soil biology increases fertilizer use efficiency by over 30%.",
            "te": f"🌱 **సేంద్రీయ కర్బనాన్ని పెంచండి మరియు సమతుల్య ఎరువులను వాడండి.** నేలలో సేంద్రీయ పదార్థం పెరిగితే ఎరువుల సామర్థ్యం 30% కంటే ఎక్కువ పెరుగుతుంది.",
            "hi": f"🌱 **जैविक खाद बढ़ाएं और संतुलित N-P-K पोषण अपनाएं।** मिट्टी में जीवांश कार्बन बढ़ने से उर्वरकों की कार्यক্ষমતા 30% बढ़ जाती है।"
        }.get(active_lang, f"🌱 **Enhance soil organic carbon and balanced nutrition.**")

        reasoning = {
            "en": f"• Chemical fertilizers without organic manure degrade beneficial microbial communities and cause soil compaction.\n• Optimum soil organic carbon (>0.75%) dramatically enhances soil cation exchange capacity (CEC) and moisture retention.\n• Balanced pH (6.5–7.5) prevents phosphorus and micronutrient fixation.",
            "te": f"• పశువుల ఎరువు లేకుండా కేవలం రసాయన ఎరువులు మాత్రమే వాడితే నేల గట్టిపడి పోషక సామర్థ్యం తగ్గుతుంది.\n• నేలలో సేంద్రీయ కర్బనం (>0.75%) ఉంటే నీటిని నిల్వ ఉంచే శక్తి మరియు పోషక లభ్యత పెరుగుతుంది.\n• సరైన pH (6.5–7.5) ఉన్నప్పుడు మాత్రమే మొక్కలు భాస్వరం మరియు సూక్ష్మ పోషకాలను గ్రహించగలవు.",
            "hi": f"• बिना गोबर की खाद के केवल रासायनिक खाद डालने से मिट्टी कठोर हो जाती है।\n• मृदा जीवांश कार्बन (>0.75%) होने से मिट्टी में नमी और पोषक तत्व सोखने की क्षमता बढ़ती है।\n• संतुलित pH (6.5–7.5) होने पर ही पौधे फास्फोरस व सूक्ष्म तत्व ग्रहण कर पाते हैं।"
        }.get(active_lang, f"• Organic carbon increases nutrient absorption.\n• Balance chemical and organic fertilizers.")

        steps = {
            "en": f"1. Incorporate 2–3 tons of well-decomposed Farm Yard Manure (FYM) or vermicompost per acre before final plowing.\n2. Cultivate green manure crops (Dhaincha / Sunhemp) for 45 days and incorporate before flowering.\n3. Split Urea application into 3 equal doses (Basal, Vegetative, Flowering) rather than a single heavy dose.",
            "te": f"1. ఆఖరి దుక్కిలో ఎకరానికి 2–3 టన్నుల పశువుల ఎరువు లేదా వర్మీ కంపోస్ట్ వేయండి.\n2. పచ్చిరొట్ట ఎరువులైన జనుము లేదా జీలుగును 45 రోజులు పెంచి పూతకు ముందే కలియదున్నండి.\n3. యూరియాను ఒకేసారి వేయకుండా మూడు సమ భాగాలుగా విభజించి వేయండి.",
            "hi": f"1. अंतिम जुताई के समय प्रति एकड़ 2-3 टन सड़ी हुई गोबर की खाद या वर्मीकम्पोस्ट मिलाएं।\n2. हरी खाद (ढैंचा या सनई) को 45 दिन उगाकर फूल आने से पहले खेत में जोत दें।\n3. यूरिया कभी भी एक बार में न डालें, इसे 3 बराबर किस्तों में बांटकर दें।"
        }.get(active_lang, f"1. Apply 2-3 tons FYM/acre.\n2. Grow green manure (Dhaincha).\n3. Split nitrogen into 3 doses.")

        notice = "Grounded in agronomic soil testing standards and crop profile parameters."

    # -------------------------------------------------------------------------
    # INTENT 5: nutrient_deficiencies (Q11)
    # -------------------------------------------------------------------------
    elif intent == "nutrient_deficiencies":
        direct = {
            "en": f"🔍 **Perform Canopy Diagnostic by Leaf Position.** Mobile nutrients (N, P, K, Mg) show symptoms on older lower leaves first; immobile elements (Fe, Zn, Ca) show on young upper foliage first.",
            "te": f"🔍 **ఆకుల స్థానాన్ని బట్టి పోషక లోపాలను గుర్తించండి.** నత్రజని, భాస్వరం, పొటాష్ లోపాలు పాత అడుగు ఆకులపై కనిపిస్తాయి; జింక్, ఇనుము లోపాలు లేత పై ఆకులపై కనిపిస్తాయి.",
            "hi": f"🔍 **पत्तियों की स्थिति देखकर पोषक तत्वों की पहचान करें।** नाइट्रोजन, फास्फोरस, पोटाश की कमी पुरानी निचली पत्तियों पर दिखती है; जबकि जिंक व लोहे की कमी नई ऊपरी पत्तियों पर दिखती है।"
        }.get(active_lang, f"🔍 **Identify deficiency by leaf location:** Lower leaves = N, P, K; Upper leaves = Fe, Zn, Ca.")

        reasoning = {
            "en": f"• **Nitrogen (N):** General uniform yellowing (chlorosis) starting from tips of oldest lower leaves along midrib.\n• **Phosphorus (P):** Purplish-bronze discoloration on dark green leaves with stunted root proliferation.\n• **Potassium (K):** Marginal scorching and browning along outer leaf edges resembling burn damage.\n• **Zinc (Zn):** Bleached white/yellow bands on either side of leaf midrib in cereals.",
            "te": f"• **నత్రజని (N):** అడుగున ఉన్న పాత ఆకులు మొదట లేత పసుపు రంగులోకి మారి ఎండిపోతాయి.\n• **భాస్వరం (P):** ఆకులు ముదురు ఆకుపచ్చగా ఉండి అంచులు ఊదా/ఎరుపు రంగులోకి మారతాయి, వేర్లు బలహీనపడతాయి.\n• **పొటాష్ (K):** ఆకుల అంచులు కాలినట్లుగా గోధుమ రంగులోకి మారతాయి.\n• **జింక్ (Zn):** ఆకుల ఈనెల మధ్య భాగం పసుపు లేదా తెల్లటి చారలుగా మారుతుంది.",
            "hi": f"• **नाइट्रोजन (N):** निचली पुरानी पत्तियां सिरे से पीली पड़ने लगती हैं।\n• **फास्फोरस (P):** पत्तियां बैंगनी या गहरे कांस्य रंग की हो जाती हैं और जड़ें कमजोर रहती हैं।\n• **पोटाश (K):** पत्तियों के बाहरी किनारे जले हुए जैसे भूरे हो जाते हैं।\n• **जिंक (Zn):** नई पत्तियों की नसों के बीच का भाग सफेद या पीला हो जाता है।"
        }.get(active_lang, f"• N = Older leaves yellow.\n• P = Purple leaves.\n• K = Leaf edges scorched.\n• Zn = Interveinal chlorosis.")

        steps = {
            "en": f"1. Inspect 10 consecutive plants in 3 field sectors early in the morning.\n2. For acute Nitrogen deficiency, top-dress Urea (25–30 kg/acre) before scheduled watering.\n3. For Zinc deficiency, apply foliar spray of Zinc Sulphate (0.5% + 0.25% lime) on foliage.",
            "te": f"1. ఉదయాన్నే పొలంలో 10 మొక్కల ఆకులను క్షుణ్ణంగా పరిశీలించండి.\n2. నత్రజని లోపానికి తడి ఆరిన తర్వాత ఎకరానికి 25-30 కిలోల యూరియా వేయండి.\n3. జింక్ లోపం ఉంటే లీటరు నీటికి 5 గ్రాముల జింక్ సల్ఫేట్ కలిపి పిచికారీ చేయండి.",
            "hi": f"1. खेत में सुबह के समय पौधों की ऊपरी व निचली पत्तियों की जांच करें।\n2. नाइट्रोजन की कमी होने पर सिंचाई से पहले यूरिया (25-30 किग्रा/एकड़) दें।\n3. जिंक की कमी के लिए जिंक सल्फेट (0.5%) का पर्णीय छिड़काव करें।"
        }.get(active_lang, f"1. Inspect upper vs lower leaves.\n2. Top-dress Urea for N.\n3. Spray Zinc Sulphate for micronutrients.")

        notice = "Visual diagnostic guide. Cross-verify with certified Soil Health Card laboratory testing."

    # -------------------------------------------------------------------------
    # INTENT 6: interpret_analysis (Q12)
    # -------------------------------------------------------------------------
    elif intent == "interpret_analysis":
        n_val = (farm_context or {}).get("nitrogen", 120.0)
        p_val = (farm_context or {}).get("phosphorus", 35.0)
        k_val = (farm_context or {}).get("potassium", 55.0)
        ph_val = (farm_context or {}).get("soil_ph", 6.8)

        direct = {
            "en": f"📊 **Your Soil Health Rating:** pH = {ph_val:.1f} (Neutral/Ideal), Available N = {n_val:.0f} kg/ha, P = {p_val:.0f} kg/ha, K = {k_val:.0f} kg/ha. Soil chemical parameters are calibrated for agronomic scheduling.",
            "te": f"📊 **మీ నేల ఆరోగ్య రేటింగ్:** pH = {ph_val:.1f} (అనుకూలమైనది), లభ్యమయ్యే నత్రజని = {n_val:.0f} కిలో/హెక్టారు, భాస్వరం = {p_val:.0f} కిలో/హెక్టారు, పొటాష్ = {k_val:.0f} కిలో/హెక్టారు.",
            "hi": f"📊 **आपकी मिट्टी की जांच रिपोर्ट:** pH = {ph_val:.1f} (सामान्य/आदर्श), उपलब्ध नाइट्रोजन = {n_val:.0f} किग्रा/हेक्टेयर, फास्फोरस = {p_val:.0f} किग्रा/हेक्टेयर, पोटाश = {k_val:.0f} किग्रा/हेक्टेयर।"
        }.get(active_lang, f"📊 **Soil Health Rating:** pH = {ph_val:.1f}, N = {n_val:.0f}, P = {p_val:.0f}, K = {k_val:.0f} kg/ha.")

        reasoning = {
            "en": f"• **Soil pH Benchmarks:** 6.5–7.5 is optimal; <6.0 locks Phosphorus and requires agricultural lime; >8.0 causes Iron/Zinc lockout and requires Gypsum.\n• **Nitrogen (N):** <140 kg/ha is Low; 140–280 kg/ha is Medium; >280 kg/ha is High.\n• **Phosphorus (P):** <10 kg/ha is Low; 10–25 kg/ha is Medium; >25 kg/ha is High.\n• **Potassium (K):** <110 kg/ha is Low; 110–280 kg/ha is Medium; >280 kg/ha is High.",
            "te": f"• **pH ప్రమాణాలు:** 6.5–7.5 అనుకూలం; 6.0 కంటే తక్కువైతే ఆమ్ల నేల (సున్నం వేయాలి); 8.0 కంటే ఎక్కువైతే క్షార నేల (జిప్సం వేయాలి).\n• **నత్రజని (N):** 140 కంటే తక్కువైతే తక్కువ; 140–280 మధ్యస్థం; 280 కంటే ఎక్కువైతే అధికం.\n• **భాస్వరం (P):** 10 కంటే తక్కువైతే తక్కువ; 10–25 మధ్యస్థం; 25 కంటే ఎక్కువైతే అధికం.\n• **పొటాష్ (K):** 110 కంటే తక్కువైతే తక్కువ; 110–280 మధ్యస్థం; 280 కంటే ఎక్కువైతే అధికం.",
            "hi": f"• **pH मान:** 6.5-7.5 सर्वोत्तम है; 6.0 से कम अम्लीय (चूना डालें); 8.0 से अधिक क्षारीय (जिप्सम डालें)।\n• **नाइट्रोजन (N):** <140 कम; 140-280 मध्यम; >280 अधिक।\n• **फास्फोरस (P):** <10 कम; 10-25 मध्यम; >25 अधिक।\n• **पोटाश (K):** <110 कम; 110-280 मध्यम; >280 अधिक।"
        }.get(active_lang, f"• pH 6.5-7.5 optimal.\n• N: <140 Low, 140-280 Medium.\n• P: <10 Low, 10-25 Medium.\n• K: <110 Low, 110-280 Medium.")

        steps = {
            "en": f"1. If soil test N is Low, split urea into 3 applications rather than applying extra all at once.\n2. Always apply 100% Phosphorus at sowing time as a basal dose.\n3. Test soil every 2 years after harvest of the main crop.",
            "te": f"1. నత్రజని తక్కువగా ఉంటే యూరియాను మూడు దఫాలుగా వేయండి.\n2. భాస్వరం ఎరువులను విత్తే సమయంలోనే మొదట్లోనే వేయండి.\n3. ప్రతి రెండు సంవత్సరాలకు ఒకసారి పంట కోత తర్వాత నేల పరీక్ష చేయించండి.",
            "hi": f"1. यदि नाइट्रोजन कम है तो यूरिया को तीन बार में दें।\n2. फास्फोरस की पूरी मात्रा बुवाई के समय ही बेसल डोज के रूप में दें।\n3. हर दो साल में मुख्य फसल की कटाई के बाद मिट्टी की जांच अवश्य कराएं।"
        }.get(active_lang, f"1. Split urea doses if N is low.\n2. Apply P as basal application.\n3. Re-test soil every 2 years.")

        notice = "Derived from farmer profile records stored in SQLite database."

    # -------------------------------------------------------------------------
    # INTENT 7: crop_suitability (Q3)
    # -------------------------------------------------------------------------
    elif intent == "crop_suitability":
        direct = {
            "en": f"🌾 **Top Agro-Climatic Crop Matches for Your Farm:** For {soil} soil with current temperatures ({temp:.1f}°C), evaluated crops are ranked in your Crop Recommendations tab.",
            "te": f"🌾 **మీ నేల మరియు శీతోష్ణస్థితికి సరిపోయే పంటలు:** {soil} నేల మరియు ప్రస్తుత ఉష్ణోగ్రత ({temp:.1f}°C) ఆధారంగా సిఫార్సు చేసిన పంటల వివరాలు క್ರಾಪ್ రికమెండేషన్స్ ట్యాబ్‌లో అందుబాటులో ఉన్నాయి.",
            "hi": f"🌾 **आपकी मिट्टी और जलवायु के लिए उपयुक्त फसलें:** {soil} मिट्टी और वर्तमान तापमान ({temp:.1f}°C) के आधार पर अनुशंसित फसलों की सूची फसल अनुशंसा टैब में उपलब्ध है।"
        }.get(active_lang, f"🌾 **Top Crop Matches:** Evaluated based on {soil} soil and temperature ({temp:.1f}°C).")

        reasoning = {
            "en": f"• **Clay Loam / Black Soil:** High moisture retention; optimal for Rice (Kharif), Cotton (Summer), and Wheat (Rabi).\n• **Sandy Loam / Red Soil:** Rapid drainage; optimal for Maize, Groundnut, Tomato, and Millets.\n• **Water Availability:** If canal/borewell water is abundant, Rice/Sugarcane/Tomato yield maximum returns; under moderate/scarce water, Maize/Millets conserve resource.",
            "te": f"• **నల్లరేగడి / బంకమన్ను నేలలు:** ఎక్కువ తేమను నిల్వ ఉంచుతాయి; వరి, పత్తి, గోధుమ పంటలకు అనుకూలం.\n• **ఎర్ర నేలలు / ఇసుక నేలలు:** తేలికపాటి నేలలు; మొక్కజొన్న, వేరుశనగ, టమోటా మరియు చిరుధాನ್ಯాలకు అనుకూలం.\n• **నీటి లభ్యత:** నీరు పుష్కలంగా ఉంటే వరి, టమోటా సాగు చేయవచ్చు; నీరు తక్కువగా ఉంటే మొక్కజొన్న లేదా చిరుధాన్యాలు ఉత్తమం.",
            "hi": f"• **काली व दोमट मिट्टी:** अधिक नमी सोखती है; धान, कपास और गेहूं के लिए सर्वोत्तम।\n• **बलुई दोमट व लाल मिट्टी:** अच्छा जल निकास; मक्का, मूंगफली, टमाटर और मोटे अनाज के लिए उत्तम।\n• **पानी की उपलब्धता:** पानी पर्याप्त हो तो धान/टमाटर लगाएं; सीमित पानी में मक्का या बाजरा चुनें।"
        }.get(active_lang, f"• Heavy soils = Rice/Cotton.\n• Sandy loams = Maize/Groundnut/Tomato.\n• Match crop to available irrigation water.")

        steps = {
            "en": f"1. Navigate to the 🌱 **Crop Recommendations** section on your sidebar for specific ranking scores.\n2. Verify local seed variety certification (e.g., hybrid vs open-pollinated) before buying.\n3. Plan crop rotation with leguminous pulses (Gram / Greengram) to break pest cycles.",
            "te": f"1. మరింత సమాచారం కోసం సైడ్‌బార్‌లోని 🌱 **పంట సిఫార్సులు** విభాగాన్ని చూడండి.\n2. విత్తనాలు కొనేటప్పుడు ధృవీకరించబడిన హైబ్రిడ్ లేదా నాణ్యమైన విత్తనాలను ఎంచుకోండి.\n3. నేల సారాన్ని పెంచడానికి పప్పుధాన్యాల పంటలతో పంట మార్పిడి చేయండి.",
            "hi": f"1. विस्तृत स्कोर देखने के लिए साइडबार में 🌱 **फसल अनुशंसाएं** सेक्शन खोलें।\n2. प्रमाणित बीज ही खरीदें और बुवाई से पहले बीजोपचार अवश्य करें।\n3. दलहनी फसलों के साथ फसल चक्र अपनाएं ताकि मिट्टी की ताकत बढ़े।"
        }.get(active_lang, f"1. Check Crop Recommendations tab.\n2. Source certified seed varieties.\n3. Practice crop rotation with legumes.")

        notice = "Deterministic ranking powered by crop_recommender.py agronomic guidelines."

    # -------------------------------------------------------------------------
    # INTENT 8: crop_selection_info (Q14)
    # -------------------------------------------------------------------------
    elif intent == "crop_selection_info":
        direct = {
            "en": f"📋 **5 Core Parameters Required Before Selecting a Crop:** 1. Soil Texture & Depth, 2. Peak-Season Water Security, 3. Thermal Window (°C), 4. Historical Pest Pressure, and 5. Local Market Mandi Liquidity.",
            "te": f"📋 **పంటను ఎంచుకోవడానికి ముందు కావలసిన 5 ముఖ్యమైన అంశాలు:** 1. నేల రకం మరియు లోతు, 2. కీలక దశల్లో నీటి లభ్యత, 3. వాతావరణ ఉష్ణోగ్రత, 4. మునుపటి పంటల్లో తెగుళ్ల చరిత్ర, 5. స్థానిక మార్కెట్ ధరలు మరియు డిమాండ్.",
            "hi": f"📋 **फसल चुनने से पहले 5 प्रमुख आवश्यक जानकारियां:** 1. मिट्टी की बनावट व गहराई, 2. सिंचाई पानी की उपलब्धता, 3. मौसमी तापमान दायरा, 4. पिछले कीट-रोगों का इतिहास, 5. स्थानीय मंडी भाव व मांग।"
        }.get(active_lang, f"📋 **5 Core Crop Selection Factors:** Soil type, water security, temperature, pest history, and market demand.")

        reasoning = {
            "en": f"• Planting high-water crops (Paddy/Sugarcane) in porous sand or water-stressed borewells leads to terminal drought failure.\n• Planting cool-season crops (Wheat) during high nighttime temperatures causes floral sterility and empty grains.\n• Monocropping the same botanical family consecutive seasons multiplies soil-borne fungal pathogens.",
            "te": f"• నీటి ఎద్దడి ఉన్న ప్రాంతాల్లో ఎక్కువ నీరు అవసరమయ్యే పంటలు వేస్తే చివరి దశలో తీవ్ర నష్టం వస్తుంది.\n• రాత్రి ఉష్ణోగ్రతలు ఎక్కువగా ఉన్నప్పుడు గోధుమ వంటి పంటలు వేస్తే గింజ సరిగ్గా కట్టదు.\n• ప్రతి ఏటా ఒకే రకమైన పంట వేస్తే నేలలో తెగుళ్లు మరియు పురుగులు స్థిరపడిపోతాయి.",
            "hi": f"• पानी की कमी वाले इलाकों में धान जैसी फसलें लगाने से फसल सूखने का खतरा रहता है।\n• अधिक रात के तापमान में गेहूं बोने से दाना कमजोर बनता है।\n• लगातार एक ही कुल की फसल लगाने से मिट्टी जनित रोग बढ़ जाते हैं।"
        }.get(active_lang, f"• Match crop water demand to seasonal borewell discharge.\n• Rotate botanical families.")

        steps = {
            "en": f"1. Audit your borewell recharge yield during dry pre-monsoon months.\n2. Review your Soil Health Card for pH and micronutrient deficiencies.\n3. Consult your nearest Krishi Vigyan Kendra (KVK) or Agriculture Officer for regional pest alerts.",
            "te": f"1. ఎండాకాలంలో మీ బోరుబావి నీటి లభ్యతను అంచనా వేయండి.\n2. మీ నేల ఆరోగ్య కార్డులోని pH మరియు పోషక లోపాలను పరిశీలించండి.\n3. స్థానిక కృషి విజ్ఞాన కేంద్రం (KVK) లేదా వ్యవసాయ అధికారిని సంప్రదించండి.",
            "hi": f"1. गर्मियों में अपने नलकूप के पानी की क्षमता का सही आकलन करें।\n2. मृदा स्वास्थ्य कार्ड से pH और सूक्ष्म पोषक तत्वों की स्थिति जांचें।\n3. निकटतम कृषि विज्ञान केंद्र (KVK) से उन्नत किस्मों की जानकारी लें।"
        }.get(active_lang, f"1. Assess borewell yield.\n2. Check soil pH and NPK.\n3. Consult local KVK.")

        notice = "Checklist based on ICAR Good Agricultural Practices (GAP)."

    # -------------------------------------------------------------------------
    # INTENT 9: next_season_prep (Q15)
    # -------------------------------------------------------------------------
    elif intent == "next_season_prep":
        direct = {
            "en": f"🚜 **Execute Deep Summer Plowing & Pre-Season Sanitation.** Deep tillage (20–25 cm) destroys weed rhizomes, breaks hardpan soil layers, and exposes dormant insect pupae to solar heat.",
            "te": f"🚜 **వేసవి లోతు దుక్కులు మరియు పొలం పారిశుధ్యం చేపట్టండి.** 20–25 సెం.మీ లోతు దుక్కి చేయడం వల్ల నేలలో దాగి ఉన్న పురుగుల గుడ్లు, కోశస్థ దశలు మరియు కలుపు విత్తనాలు ఎండ తీవ్రతకు నశిస్తాయి.",
            "hi": f"🚜 **गहरी ग्रीष्मकालीन जुताई और खेत की सफाई करें।** 20-25 सेमी गहरी जुताई करने से खरपतवार की जड़ें नष्ट होती हैं और मिट्टी में छिपे कीटों के अंडे व प्यूपा धूप से खत्म हो जाते हैं।"
        }.get(active_lang, f"🚜 **Execute deep summer plowing (20-25 cm).** Eliminates weed seeds and dormant pest pupae.")

        reasoning = {
            "en": f"• Solar heating of turned soil (solarization) reduces fungal spore populations by up to 60%.\n• Laser land leveling saves 20–25% irrigation water by preventing high and low spots.\n• Clearing bunds and swales eliminates alternate weed hosts for aphids and hoppers.",
            "te": f"• ఎండకు నేలను ఆరబెట్టడం వల్ల నేలలోని శిలీంధ్రాల బీజాలు 60% వరకు నశిస్తాయి.\n• లేజర్ లెವೆਲర్ ద్వారా పొలాన్ని సమానం చేయడం వల్ల 20–25% నీరు ఆదా అవుతుంది.\n• గట్లపై ఉన్న కలుపు మొక్కలను తొలగిస్తే పురుగులు మరియు తెగుళ్లు వ్యాపించకుండా ఉంటాయి.",
            "hi": f"• तेज धूप से मिट्टी तपने पर हानिकारक फफूंद 60% तक नष्ट हो जाती है।\n• लेजर लैंड लेवलर से खेत समतल करने पर 20-25% पानी की बचत होती है।\n• मेड़ों की सफाई करने से कीटों को छिपने की जगह नहीं मिलती।"
        }.get(active_lang, f"• Soil solarization reduces soil-borne fungus.\n• Laser leveling saves 20% water.")

        steps = {
            "en": f"1. Deep plow across the slope immediately after the previous crop harvest.\n2. Laser-level the field parcel to ensure uniform water distribution.\n3. Incorporate green manure crop or farmyard manure 3 weeks prior to sowing.",
            "te": f"1. పంట కోత పూర్తయిన వెంటనే వాలుకు అಡ್ಡంగా లోతు దుక్కి చేయండి.\n2. నీరు సమానంగా అందడానికి పొలాన్ని లేజర్ లెವೆలర్‌తో చదును చేయండి.\n3. విత్తడానికి 3 వారాల ముందే పచ్చిరొట్ట ఎరువు లేదా పశువుల ఎరువును నేలలో కలియదున్నండి.",
            "hi": f"1. पिछली फसल कटाई के तुरंत बाद ढलान के विपरीत गहरी जुताई करें।\n2. खेत को लेजर लेवलर से समतल कराएं।\n3. बुवाई से 3 सप्ताह पहले गोबर की खाद या हरी खाद मिट्टी में मिलाएं।"
        }.get(active_lang, f"1. Deep plow immediately post-harvest.\n2. Laser level field.\n3. Incorporate FYM 3 weeks before sowing.")

        notice = "Agronomic pre-season protocol."

    # -------------------------------------------------------------------------
    # INTENT 10: crop_diseases (Q4)
    # -------------------------------------------------------------------------
    elif intent == "crop_diseases":
        direct = {
            "en": f"🛡️ **Major Pathological & Insect Threats for {crop}:** Grounded in scientific risk modeling for your active parcel, common threats include blast/rust/blight and sucking insects.",
            "te": f"🛡️ **{crop} పంటకు సోకే ప్రధాన తెగుళ్లు మరియు వ్యాధులు:** మీ పంట కోసం పరిశీలించగా, సాధారణంగా వచ్చే శిలీంధ్ర తెగుళ్లు, ఎండు తెగులు మరియు రసం పీల్చే పురుగులు ప్రధాన ముప్పుగా ఉంటాయి.",
            "hi": f"🛡️ **{crop} के प्रमुख रोग एवं कीट:** आपकी फसल के लिए प्रमुख खतरों में ब्लास्ट/झੁਲसा/रस्ट फफूंद और रस चूसक कीट शामिल हैं।"
        }.get(active_lang, f"🛡️ **Major threats for {crop}:** Fungal blights, leaf spots, and sucking pests.")

        reasoning = {
            "en": f"• High humidity (>80%) combined with moderate temperatures (20–28°C) triggers rapid fungal spore germination.\n• Excessive succulent growth caused by over-application of Nitrogen attracts sucking pests (aphids, planthoppers).\n• Poor field drainage exacerbates root rot (Rhizoctonia) and damping-off.",
            "te": f"• గాలిలో తేమ 80% కంటే ఎక్కువగా ఉండి ఉష్ణోగ్రత 20–28°C మధ్య ఉన్నప్పుడు శిలీంధ్ర వ్యాధులు వేగంగా వ్యాపిస్తాయి.\n• ఎక్కువ మోతాదులో నత్రజని (యూరియా) వాడితే ఆకులు మెత్తగా మారి రసం పీల్చే పురుగులు ఎక్కువగా ఆశిస్తాయి.\n• పొలంలో నీరు నిలిచి ఉంటే వేరుకుళ్లు తెగులు తీవ్రమవుతుంది.",
            "hi": f"• अधिक आर्द्रता (>80%) और मध्यम तापमान में फफूंद के जीवाणु तेजी से पनपते हैं।\n• अत्यधिक यूरिया डालने से पत्तियां कोमल हो जाती हैं, जिससे रस चूसक कीटों का हमला बढ़ता है।\n• खेत में जलभराव रहने से जड़ गलन रोग फैलता है।"
        }.get(active_lang, f"• High humidity (>80%) promotes fungal blast/blight.\n• Excess urea attracts sucking pests.")

        steps = {
            "en": f"1. Scout 20 random plants early in the morning, focusing on the undersides of leaves.\n2. Maintain balanced Potash (K) fertilization to strengthen plant cell walls against penetration.\n3. Install 5 pheromone traps per acre for early insect monitoring.",
            "te": f"1. ఉదయాన్నే 20 మొక్కల ఆకుల అడుగు భాగాన్ని పరిశీలించండి.\n2. మొక్కలకు తెగుళ్లను తట్టుకునే శక్తిని ఇవ్వడానికి తగినంత పొటాష్ ఎరువును వేయండి.\n3. పురుగుల ఉనికిని గుర్తించడానికి ఎకరానికి 5 లింగాకర్షక బుట్టలను అమర్చండి.",
            "hi": f"1. सुबह के समय 20 पौधों की पत्तियों के नीचे कीटों और धब्बों की जांच करें।\n2. पोटाश खाद का संतुलित उपयोग करें ताकि पौधों की कोशिकाएं मजबूत रहें।\n3. कीटों की निगरानी के लिए प्रति एकड़ 5 फेरोमोन ट्रैप लगाएं।"
        }.get(active_lang, f"1. Scout 20 plants early morning.\n2. Apply balanced Potash.\n3. Deploy 5 pheromone traps/acre.")

        notice = "Derived from disease knowledge base in risk_analyzer.py."

    # -------------------------------------------------------------------------
    # INTENT 11: disease_early_signs (Q5)
    # -------------------------------------------------------------------------
    elif intent == "disease_early_signs":
        direct = {
            "en": f"🔎 **Key Early Warning Signs in Field Scouting:** Catching lesions and insect colonies at <5% threshold prevents economic yield loss.",
            "te": f"🔎 **పంట వ్యాధుల ప్రారంభ హెచ్చరిక సంకేతాలు:** తెగుళ్లు 5% కంటే తక్కువగా ఉన్నప్పుడే గుర్తిస్తే పంట నష్టాన్ని పూర్తిగా నివారించవచ్చు.",
            "hi": f"🔎 **खेत में रोग के शुरुआती लक्षण:** आर्थिक नुकसान स्तर (5% से कम) पर ही पहचान कर समय रहते रोकथाम करें।"
        }.get(active_lang, f"🔎 **Early Warning Signs:** Inspect lower leaves and margins for initial lesions and nymphs.")

        reasoning = {
            "en": f"• Fungal spores produce tiny water-soaked pinhead spots before expanding into necrotic dead lesions.\n• Sucking pests (thrips, aphids, whiteflies) congregate in leaf curls and secrete sticky shiny honeydew.\n• Wilting during cool morning hours indicates subterranean root damage or vascular blockage.",
            "te": f"• శిలీంధ్ర తెగుళ్లు వచ్చినప్పుడు మొదట ఆకులపై చిన్న నీటి మచ్చలు ఏర్పడి క్రమంగా పెద్ద మచ్చలుగా మారుతాయి.\n• రసం పీల్చే పురుగులు ఆకుల అడుగున చేరి రసాన్ని పీల్చడం వల్ల ఆకులు ముడుచుకుపోతాయి మరియు జిగురు పదార్థం కనిపిస్తుంది.\n• ఉదయం పూట కూడా మొక్కలు వాడిపోయి ఉంటే వేరు వ్యవస్థ దెబ్బతిన్నట్లు గుర్తించాలి.",
            "hi": f"• फफूंद के हमले पर पत्तियों पर पहले छोटे पानी जैसे धब्बे बनते हैं, जो बाद में सूखकर भूरे हो जाते हैं।\n• रस चूसक कीट पत्तियों की निचली सतह पर चिपककर रस चूसते हैं और चिपचिपा पदार्थ छोड़ते हैं।\n• सुबह के ठंडे समय भी यदि पौधे मुरझाए दिखें, तो यह जड़ में खराबी का संकेत है।"
        }.get(active_lang, f"• Fungal spots start as water-soaked lesions.\n• Sucking insects hide in leaf folds.\n• Morning wilting indicates root rot.")

        steps = {
            "en": f"1. Walk an 'X' or 'W' pattern across your parcel during early morning light.\n2. Check lower leaf axils, collars, and growing tips.\n3. If honeydew or tiny nymphs appear, spray 5% Neem Seed Kernel Extract (NSKE) or Neem Oil (1500 ppm).",
            "te": f"1. ఉదయం వేళల్లో పొలంలో 'W' ఆకారంలో నడుస్తూ మొక్కలను పరిశీలించండి.\n2. ఆకుల అడుగు భాగం, కాండం మరియు లేత చిగుళ్లను గమనించండి.\n3. రసం పీల్చే పురుగులు కనిపిస్తే వేప నూనె (1500 ppm) లేదా 5% వేప గింజల కషాయం పిచికారీ చేయండి.",
            "hi": f"1. सुबह के समय खेत में घूमकर पत्तियों के नीचे और तने के पास जांच करें।\n2. पत्तियों के मुड़ने या सफेद मक्खी दिखने पर तुरंत ध्यान दें।\n3. शुरुआती रोकथाम के लिए 5% नीम का अर्क या नीम तेल (1500 ppm) का छिड़काव करें।"
        }.get(active_lang, f"1. Walk W-pattern early morning.\n2. Inspect lower leaf surfaces.\n3. Spray 1500 ppm Neem Oil at first sign.")

        notice = "Scouting protocol. Does not claim computer vision or camera access."

    # -------------------------------------------------------------------------
    # INTENT 12: pest_resistance (Q13)
    # -------------------------------------------------------------------------
    elif intent == "pest_resistance":
        direct = {
            "en": f"🌿 **Strengthen Plant Biomechanics & Biological Resistance.** Resilient crops naturally repel insect piercing and fungal hyphae penetration.",
            "te": f"🌿 **మొక్కల సహజ రక్షణ వ్యవస్థను బలోపేతం చేయండి.** దృఢమైన కణజాలం ఉన్న మొక్కలు పురుగుల దాడిని మరియు తెగుళ్లను సులభంగా తట్టుకోగలవు.",
            "hi": f"🌿 **पौधों की प्राकृतिक रोग प्रतिरोधक क्षमता बढ़ाएं।** मजबूत कोशिका भित्ति वाले पौधे कीटों और फफूंद के संक्रमण को आसानी से रोक लेते हैं।"
        }.get(active_lang, f"🌿 **Boost plant natural immunity:** Balanced potassium, silica, and biological controls.")

        reasoning = {
            "en": f"• Adequate Potassium (K) thickens outer epidermal cell walls, physically impeding insect stylet penetration.\n• Excess Nitrogen creates soft, succulent foliage with elevated free amino acids that attract caterpillars and aphids.\n• Bio-agents like Trichoderma viride colonize the rhizosphere, shielding roots against pathogenic fungi.",
            "te": f"• తగినంత పొటాష్ ఎరువు వేయడం వల్ల మొక్కల కణాల గోడలు దృఢంగా మారి పురుగులు రసం పీల్చలేవు.\n• ఎక్కువ యూరియా వేస్తే ఆకులు మెత్తగా మారి పురుగులను ఎక్కువగా ఆకర్షిస్తాయి.\n• ట్రైకోడెర్మా విరిడే వంటి జీవ శిలీంధ్రాలు వేర్ల వద్ద రక్షణ కవచంలా పనిచేసి వేరుకుళ్లు రాకుండా కాపాడతాయి.",
            "hi": f"• पर्याप्त पोटाश देने से पौधों की बाहरी परत मोटी होती है, जिससे कीड़े रस नहीं चूस पाते।\n• अत्यधिक यूरिया से पत्तियां अत्यधिक कोमल बनती हैं, जो इल्लियों और माहू को आकर्षित करती हैं।\n• ट्राइकोडर्मा विरिडी का प्रयोग करने से जड़ें फफूंद जनित रोगों से सुरक्षित रहती हैं।"
        }.get(active_lang, f"• Potassium strengthens cell walls.\n• Excess N makes plants soft and vulnerable.\n• Deploy bio-agents like Trichoderma.")

        steps = {
            "en": f"1. Never exceed recommended Nitrogen doses; always apply balanced Potash (MOP).\n2. Deploy beneficial biocontrol agents (Beauveria bassiana for insects, Trichoderma for soil fungi).\n3. Plant trap crops (e.g., Marigold around Tomato/Cotton) to lure bollworms away from main crops.",
            "te": f"1. సిఫార్సు చేసిన మోతాదు కంటే ఎక్కువ యూరియా వేయకండి; పొటాష్ తప్పనిసరిగా వేయండి.\n2. జీవ నియంత్రణ కోసం ట్రైకోడెర్మా మరియు బవేరియా ബാസിയానా వాడండి.\n3. ప్రధాన పంట చుట్టూ బంతి మొక్కలను ఎర పంటగా నాటడం వల్ల పురుగుల ఉధృతి తగ్గుతుంది.",
            "hi": f"1. यूरिया संतुलित मात्रा में ही दें और पोटाश का पूरा उपयोग करें।\n2. जैविक फफूंदनाशी (ट्राइकोडर्मा) से बीजोपचार व मृदा उपचार करें।\n3. मुख्य फसल (टमाटर/कपास) के चारों ओर गेंदा (मैरीगोल्ड) की ट्रैप क्रॉप लगाएं।"
        }.get(active_lang, f"1. Balance N with Potash.\n2. Use Trichoderma and Beauveria.\n3. Plant marigold trap crops on borders.")

        notice = "Integrated Pest Management (IPM) guidelines."

    # -------------------------------------------------------------------------
    # INTENT 13: daily_priorities (Q8)
    # -------------------------------------------------------------------------
    elif intent == "daily_priorities":
        direct = {
            "en": f"📅 **Daily Action Priorities for {crop} ({stage}):** Synthesized checklist categorized into Urgent, Routine, and Scouting operations for today's weather conditions.",
            "te": f"📅 **ఈరోజు {crop} ({stage}) కోసం ప్రాధాన్యతా పనులు:** నేటి వాతావరణం మరియు పొలం పరిస్థితిని బట్టి తక్షణ, సాధారణ మరియు పరిశీలన పనుల జాబితా.",
            "hi": f"📅 **आज के प्राथमिकता कार्य ({crop} - {stage}):** आज के मौसम और खेत की स्थिति अनुसार आवश्यक, सामान्य व निगरानी कार्यों की कार्यसूची।"
        }.get(active_lang, f"📅 **Today's Priorities for {crop} ({stage}):** Urgent, routine, and scouting operations.")

        reasoning = {
            "en": f"• Operational priorities depend strictly on weather forecasts (rain probability {rain_prob:.0f}%) and soil moisture.\n• High humidity requires deferring pesticide sprays until morning dew dries.\n• Regular early morning scouting detects pest hotspots before economic damage thresholds are crossed.",
            "te": f"• రోజువారీ పనులు వాతావరణం (వర్షం అవకాశం {rain_prob:.0f}%) మరియు నేలలో తేమపై ఆధారపడి ఉంటాయి.\n• ఆకులపై మంచు ఉన్నప్పుడు రసాయనాలు పిచికారీ చేయవద్దు, మంచు ఆరిన తర్వాతే చేయాలి.\n• ఉదయం పూట పొలాన్ని పరిశీలించడం వల్ల తెగుళ్లను ప్రారంభంలోనే అరికట్టవచ్చు.",
            "hi": f"• आज के कार्य मौसम पूर्वानुमान (बारिश की संभावना {rain_prob:.0f}%) पर निर्भर करते हैं।\n• सुबह ओस सूखने के बाद ही कीटनाशक या खाद का छिड़काव करें।\n• सुबह के समय खेत का चक्कर लगाने से कीटों का प्रकोप तुरंत पता चल जाता है।"
        }.get(active_lang, f"• Tasks aligned to weather (rain chance {rain_prob:.0f}%).\n• Spray only after dew evaporates.")

        steps = {
            "en": f"1. **Morning (06:00–08:30 AM):** Inspect furrows, check irrigation drippers, and scout 20 random plants.\n2. **Midday (11:00 AM–02:00 PM):** Check irrigation secondary valves; avoid midday pesticide spraying.\n3. **Late Afternoon (04:00–06:00 PM):** Perform scheduled foliar sprays or nutrient application in calm wind.",
            "te": f"1. **ఉదయం (06:00–08:30):** కాలువలు, డ్రిప్ లైన్లను తనిఖీ చేయండి మరియు 20 మొక్కల ఆకులను పరిశీలించండి.\n2. **మధ్యాహ్నం (11:00–02:00):** ఎండ తీవ్రంగా ఉన్నప్పుడు మందులు పిచికారీ చేయవద్దు.\n3. **సాయంత్రం (04:00–06:00):** గాలి వేగం తక్కువగా ఉన్నప్పుడు అవసరమైన పిచికారీ పనులు పూర్తి చేయండి.",
            "hi": f"1. **सुबह (06:00-08:30):** नालियों और सिंचाई प्रणाली की जांच करें, 20 पौधों का निरीक्षण करें।\n2. **दोपहर (11:00-02:00):** तेज धूप में कोई भी कीटनाशक छिड़काव न करें।\n3. **शाम (04:00-06:00):** शांत मौसम में आवश्यक पोषक तत्वों या दवा का छिड़काव करें।"
        }.get(active_lang, f"1. Morning: Scout and irrigate.\n2. Midday: Avoid chemical spraying.\n3. Evening: Apply foliar nutrients.")

        notice = "Synchronized with daily_plan.py operations schedule."

    # -------------------------------------------------------------------------
    # INTENT 14: growth_stage_care (Q9)
    # -------------------------------------------------------------------------
    elif intent == "growth_stage_care":
        direct = {
            "en": f"📈 **Growth Management Directives for {crop} ({stage}):** Each physiological phase has distinct hydraulic and nutritional demands.",
            "te": f"📈 **{crop} ({stage}) దశలో పంట పెరుగుదల యాజమాన్యం:** పంట ప్రతి పెరుగుదల దశలోనూ నీరు మరియు పోషకాల అవసరాలు వేర్వేరుగా ఉంటాయి.",
            "hi": f"📈 **{crop} ({stage}) अवस्था के लिए विकास प्रबंधन:** फसल की प्रत्येक वृद्धि अवस्था में पानी और पोषक तत्वों की विशेष आवश्यकता होती है।"
        }.get(active_lang, f"📈 **Growth Stage Management for {crop} ({stage}):** Nutrient and irrigation alignment.")

        reasoning = {
            "en": f"• **Vegetative Phase:** High Nitrogen demand for chlorophyll synthesis and leafy canopy expansion.\n• **Flowering / Reproductive Phase:** Peak water demand and elevated Potassium/Phosphorus need for pollination and boll/grain filling.\n• **Maturity / Harvest Phase:** Water stress should be avoided until 10–14 days before harvest, when drainage promotes ripening.",
            "te": f"• **శాఖీయ / పెరుగుదల దశ:** ఆకులు మరియు కొమ్మలు బాగా పెరగడానికి నత్రజని ఎక్కువగా అవసరం.\n• **పూత మరియు పిందె దశ:** నీటి అవసరం అత్యధికంగా ఉంటుంది; గింజ బరువుకు పొటాష్, భాస్వరం చాలా ముఖ్యం.\n• **కోత దశ:** కోతకు 10-14 రోజుల ముందు నీటిని నిలిపివేయడం వల్ల పంట సమానంగా పక్వానికి వస్తుంది.",
            "hi": f"• **वानस्पतिक वृद्धि अवस्था:** पौधों की बढ़वार और हरियाली के लिए नाइट्रोजन की अधिक आवश्यकता होती है।\n• **फूल और दाना बनने की अवस्था:** पानी की सबसे नाजुक अवस्था; फास्फोरस व पोटाश से दाना चमकदार बनता है।\n• **पकाव अवस्था:** कटाई से 10-14 दिन पहले पानी बंद करने से दाना समान रूप से पकता है।"
        }.get(active_lang, f"• Vegetative = Nitrogen.\n• Flowering = Peak water & Potash.\n• Maturity = Stop water 10-14 days prior to harvest.")

        steps = {
            "en": f"1. Check soil moisture and prevent moisture stress during flowering/pollination.\n2. Apply the final top-dress split dose of Potassium (MOP) to maximize grain weight and fruit size.\n3. Monitor for stage-specific pests (e.g., bollworms in cotton flowering; planthoppers in rice tillering).",
            "te": f"1. పూత దశలో నేలలో తేమ తగ్గకుండా జాగ్రత్త వహించండి.\n2. గింజ పరిమాణం మరియు నాణ్యత పెరగడానికి పొటాష్ (MOP) ఎరువును వేయండి.\n3. ఈ దశలో వచ్చే పురుగుల (వరిలో దోమ, పత్తిలో కాయతొలుచు పురుగు) పట్ల అప్రమత్తంగా ఉండండి.",
            "hi": f"1. फूल आने के समय खेत में नमी की कमी बिल्कुल न होने दें।\n2. दाने की चमक और वजन बढ़ाने के लिए पोटाश (MOP) की खुराक दें।\n3. इस अवस्था में लगने वाले विशिष्ट कीटों (इल्ली/माहू) की नियमित निगरानी करें।"
        }.get(active_lang, f"1. Guard moisture at flowering.\n2. Apply final Potash split.\n3. Watch for stage pests.")

        notice = "Derived from rules.py CROP_THRESHOLDS."

    # -------------------------------------------------------------------------
    # INTENT 15: heavy_rain_action (Q10)
    # -------------------------------------------------------------------------
    elif intent == "heavy_rain_action":
        direct = {
            "en": f"🌧️ **Emergency Heavy Rain Protection & Drainage Protocol:** Immediate actions to prevent root waterlogging, fungal damping-off, and fertilizer wash-off.",
            "te": f"🌧️ **భారీ వర్షం అత్యవసర రక్షణ మరియు నీటి నిష్క్రమణ చర్యలు:** పొలంలో నీరు నిల్వ ఉండకుండా, వేరుకుళ్లు రాకుండా మరియు ఎరువులు కొట్టుకుపోకుండా తీసుకోవలసిన జాగ్రత్తలు.",
            "hi": f"🌧️ **भारी बारिश से सुरक्षा एवं जल निकासी प्रोटोकॉल:** खेत में पानी भरने, जड़ गलन और खाद बहने से रोकने के लिए तुरंत कदम उठाएं।"
        }.get(active_lang, f"🌧️ **Heavy Rain Safeguards:** Clear drainage outlets, stop irrigation, and defer spraying.")

        reasoning = {
            "en": f"• Waterlogged soil depletes oxygen within 24 hours, causing root asphyxiation and nitrogen denitrification.\n• Saturated soil conditions combined with high humidity accelerate fungal root rot (Pythium / Phytophthora).\n• Applying fertilizers or chemical sprays before heavy rain results in 80% product wash-off into waterways.",
            "te": f"• పొలంలో 24 గంటలకు మించి నీరు నిలిచి ఉంటే వేర్లకు ఆక్సిజన్ అందక వేర్లు కుళ్ళిపోతాయి.\n• నీరు నిలవడం వల్ల నేలలోని నత్రజని ఆవిరైపోతుంది మరియు శిలీంధ్ర వ్యాధులు వేగంగా వ్యాపిస్తాయి.\n• వర్షానికి ముందు ఎరువులు లేదా మందులు వేస్తే అవన్నీ నీటిలో కొట్టుకుపోయి వృధా అవుతాయి.",
            "hi": f"• खेत में 24 घंटे से अधिक पानी भरा रहने पर जड़ों को ऑक्सीजन नहीं मिलती और फसल पीली पड़ने लगती है।\n• जलभराव और नमी से फफूंद जनित जड़ गलन रोग बहुत तेजी से फैलता है।\n• बारिश से पहले खाद या दवा का छिड़काव करने से सब बहकर नष्ट हो जाता है।"
        }.get(active_lang, f"• Standing water causes root asphyxiation within 24 hours.\n• Defer spraying to prevent 80% chemical wash-off.")

        steps = {
            "en": f"1. **Pre-Rain:** Immediately clear field drainage swales, bund outlets, and furrow exits.\n2. **Withhold:** Suspend all scheduled irrigation and fertilizer top-dressing until weather clears.\n3. **Post-Rain:** Drain all standing water within 24 hours and apply a prophylactic copper oxychloride/bio-fungicide drench.",
            "te": f"1. **వర్షానికి ముందు:** పొలం గట్ల వద్ద ఉన్న నీటి కాలువలను మరియు తూములను వెంటనే శుభ్రం చేసి నీరు బయటకు పోయేలా చూడండి.\n2. **నిలిపివేయండి:** వర్షం తగ్గే వరకు నీరు పెట్టడం మరియు ఎరువులు వేయడం పూర్తిగా ఆపండి.\n3. **వర్షం తగ్గిన తర్వాత:** నిలిచిన నీటిని 24 గంటల్లో బయటకు పంపించి, వేరుకుళ్లు రాకుండా కాపర్ ఆక్సిక్లోరైడ్ లేదా ట్రైకోడెర్మా పిచికారీ చేయండి.",
            "hi": f"1. **बारिश से पहले:** खेत की मेड़ों के निकास और जल निकासी नालियों को तुरंत साफ करें।\n2. **स्थगित रखें:** बारिश रुकने तक सभी सिंचाई और खाद डालने के काम पूरी तरह बंद रखें।\n3. **बारिश के बाद:** 24 घंटे के अंदर खेत से अतिरिक्त पानी बाहर निकालें और फफूंद से बचाव के लिए कॉपर ऑक्सीक्लोराइड का छिड़काव करें।"
        }.get(active_lang, f"1. Clear drainage channels immediately.\n2. Stop all irrigation & fertilizer.\n3. Evacuate water within 24 hours post-rain.")

        notice = "Precautionary weather advisory from weather_service.py."

    # -------------------------------------------------------------------------
    # GENERAL / UNRECOGNIZED QUERY FALLBACK
    # -------------------------------------------------------------------------
    else:
        direct = {
            "en": f"🌾 **Agricultural Decision Support Advisory for {crop} ({stage}):** Your query touches on general farming operations.",
            "te": f"🌾 **{crop} ({stage}) కోసం వ్యవసాయ సలహా:** మీ ప్రశ్న సాధారణ వ్యవసాయ నిర్వహణకు సంబంధించినది.",
            "hi": f"🌾 **{crop} ({stage}) के लिए कृषि परामर्श:** आपका प्रश्न सामान्य कृषि प्रबंधन से संबंधित है।"
        }.get(active_lang, f"🌾 **Agricultural Advisory for {crop} ({stage}):** General farm guidance.")

        reasoning = {
            "en": f"• As a transparent rule-based assistant, I evaluate crop thresholds, soil moisture, live weather forecasts, and disease models.\n• I can answer specific questions on today's irrigation, soil fertility, pest resistance, disease identification, crop selection, and heavy rain care.",
            "te": f"• ఈ వ్యవస్థ పారదర్శక నిబంధనల ఆధారంగా మీ పంట అవసరాలు, నేల తేమ, వాతావరణ సమాచారం మరియు తెగుళ్ల ప్రమాదాన్ని విశ్లేషిస్తుంది.\n• నీటిపారుదల, నేల సారవంతం, తెగుళ్ల నివారణ, ఎరువుల యాజమాన్యం మరియు వర్షపు జాగ్రత్తలపై మీరు నిర్దిష్ట ప్రశ్నలు అడగవచ్చు.",
            "hi": f"• यह प्रणाली पारदर्शी कृषि नियमों, मिट्टी की नमी, मौसम पूर्वानुमान और कीट जोखिम का विश्लेषण करती है।\n• आप सिंचाई समय, मिट्टी की उर्वरता, कीट नियंत्रण, खाद प्रबंधन और बारिश से बचाव पर प्रश्न पूछ सकते हैं।"
        }.get(active_lang, f"• Rule-based advisory evaluates crop thresholds, moisture, and weather.")

        steps = {
            "en": f"1. Select one of the 15 Common Questions above for instant tailored analysis.\n2. Or specify your query: e.g., 'When should I irrigate my crop?' or 'How to treat yellow leaves?'.\n3. Make sure your Farm Profile and Field Monitoring readings are up to date.",
            "te": f"1. తక్షణ సమాధానం కోసం పైన ఉన్న 15 సాధారణ ప్రశ్నలలో ఒకదానిని ఎంచుకోండి.\n2. లేదా 'ఈరోజు ఎంత నీరు పెట్టాలి?' లేదా 'పసుపు ఆకులను ఎలా నివారించాలి?' వంటి ప్రశ్నలు అడగండి.\n3. మీ వ్యవసాయ ప్రొఫైల్ మరియు క్షేత్ర పరిశీలన వివరాలను ఎప్పటికప్పుడు నమోదు చేసుకోండి.",
            "hi": f"1. तुरंत सटीक सलाह के लिए ऊपर दिए गए 15 सामान्य प्रश्नों में से कोई एक चुनें।\n2. या स्पष्ट प्रश्न पूछें, जैसे: 'फसल में पानी कब दें?' या 'पीली पत्तियों का उपचार क्या है?'।\n3. अपनी खेत प्रोफ़ाइल और निगरानी रीडिंग अपडेट रखें।"
        }.get(active_lang, f"1. Choose from the 15 Common Questions above.\n2. Or ask specifically about irrigation, soil fertility, pests, or weather.")

        notice = "Transparent rule-based agronomic assistant. No external AI APIs or paid tokens used."

    # Assemble complete formatted markdown response
    response_parts = [
        f"### {h_direct}",
        direct,
        "",
        f"#### {h_context}",
        provenance,
        "",
        f"#### {h_reasoning}",
        reasoning,
        "",
        f"#### {h_steps}",
        steps,
        "",
        f"> ℹ️ *{h_notice}: {notice}*"
    ]

    return "\n".join(response_parts)


# ==============================================================================
# 6. PUBLIC QUERY INTERFACE
# ==============================================================================
def answer_query(
    query: str,
    lang: str = "en",
    farm_context: Optional[Dict[str, Any]] = None,
    latest_reading: Optional[Dict[str, Any]] = None,
    weather_data: Optional[Dict[str, Any]] = None,
    question_id: Optional[str] = None
) -> str:
    """
    Main entry point for answering farmer questions.
    Accepts both common question button clicks (via question_id) and free-text queries.
    Seamlessly executes intent classification, farm data synthesis, and multilingual response generation.
    """
    if not query.strip() and not question_id:
        return t("asst_validation_empty", lang)

    # 1. Identify intent
    intent = detect_intent(query, question_id)

    # 2. Synthesize structured answer
    try:
        return generate_response(
            intent=intent,
            lang=lang,
            farm_context=farm_context or {},
            latest_reading=latest_reading,
            weather_data=weather_data
        )
    except Exception as e:
        import logging
        logging.exception(f"Assistant generation error: {e}")
        err_msg = t("asst_error_general", lang)
        return f"⚠️ {err_msg}\n\nPlease try rephrasing your question or select one of the Common Questions above."

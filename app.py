"""
Smart Agriculture Agent - Decision Support System
A modern agtech Streamlit dashboard utilizing SQLite persistence and
deterministic, rule-based agronomic reasoning for sustainable farming.
"""

import streamlit as st
import pandas as pd
import datetime
import logging
from typing import Dict, Any

# Domain & Data Layer Modules
import database
import rules

# Configure logging for graceful technical tracing
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="Smart Agriculture Agent",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize SQLite database
database.init_db()

# ==============================================================================
# Navigation State Management
# ==============================================================================
NAV_PAGES = [
    "📊 Dashboard",
    "🌾 Farm Monitoring",
    "🤖 AI Farm Advisor",
    "📈 Analytics",
    "📜 Analysis History"
]

# Initialize pending navigation state
if "pending_nav" not in st.session_state:
    st.session_state["pending_nav"] = None

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = NAV_PAGES[0]

# Process any queued navigation request BEFORE instantiating the sidebar widget
if st.session_state["pending_nav"] is not None:
    st.session_state["nav_page"] = st.session_state["pending_nav"]
    st.session_state["sidebar_nav_selection"] = st.session_state["pending_nav"]
    st.session_state["pending_nav"] = None
elif "sidebar_nav_selection" not in st.session_state:
    st.session_state["sidebar_nav_selection"] = st.session_state["nav_page"]

def set_page(page_name: str):
    """
    Safely queues a navigation page change.
    Does NOT assign directly to 'sidebar_nav_selection' while a widget
    with that key is already instantiated in the current execution cycle.
    """
    st.session_state["pending_nav"] = page_name
    st.session_state["nav_page"] = page_name

def on_sidebar_nav_change():
    """Callback when user directly interacts with the sidebar radio."""
    st.session_state["nav_page"] = st.session_state["sidebar_nav_selection"]

# ==============================================================================
# Nature-Inspired High-Contrast CSS Styling
# ==============================================================================
st.markdown("""
<style>
    /* Google Typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Overall App Background & Text */
    .stApp {
        background-color: #f6faf6;
        color: #1e293b;
    }

    /* Glossy Forest-Green Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #133926 0%, #1b4332 50%, #24573f 100%) !important;
        color: #ffffff !important;
        box-shadow: 4px 0 20px rgba(19, 57, 38, 0.15);
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: #f1f8f3 !important;
    }

    /* Sidebar Radio Button Styling */
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        display: none;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 12px;
        padding: 0.65rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        cursor: pointer;
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.92rem;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.18);
        border-color: #74c69d;
        transform: translateX(3px);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%) !important;
        border: 1px solid #95d5b2 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        color: #ffffff !important;
    }

    /* App Header Banner */
    .app-header-container {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 60%, #40916c 100%);
        color: #ffffff;
        padding: 1.5rem 1.8rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px -4px rgba(27, 67, 50, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .app-header-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .app-logo-badge {
        background: rgba(255, 255, 255, 0.18);
        width: 52px;
        height: 52px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .app-header-title {
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff !important;
        line-height: 1.2;
    }

    .app-header-sub {
        font-size: 0.9rem;
        color: #d8f3dc;
        margin: 0.2rem 0 0 0;
        font-weight: 400;
    }

    .app-status-badge {
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.35);
        color: #ffffff;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.4rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(27, 67, 50, 0.3) !important;
        background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%) !important;
    }

    /* Streamlit Metric Container Styling */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e1ece4;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 10px rgba(27, 67, 50, 0.04);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #52796f !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        color: #1b4332 !important;
    }

    /* Friendly Empty State Box */
    .clean-empty-state {
        background: #ffffff;
        border: 2px dashed #b7e4c7;
        border-radius: 16px;
        padding: 2.5rem 1.8rem;
        text-align: center;
        margin: 1.2rem 0;
    }

    .clean-empty-state-icon {
        font-size: 2.8rem;
        margin-bottom: 0.6rem;
    }

    .clean-empty-state-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1b4332;
        margin-bottom: 0.3rem;
    }

    .clean-empty-state-desc {
        font-size: 0.92rem;
        color: #64748b;
        max-width: 520px;
        margin: 0 auto 1.2rem auto;
        line-height: 1.5;
    }

    /* Scoped High-Contrast Styling for Warning / Advisory Alert Boxes */
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]),
    .stApp div[data-testid="stAlert"]:has([data-testid*="warning"]),
    .stApp div.stAlert:has([data-testid*="Warning"]),
    .stApp [data-testid="stAlertContainer"]:has([data-testid*="Warning"]),
    .stApp [data-testid*="stAlertContentWarning"],
    [data-testid*="stAlertContentWarning"] {
        background-color: #fef9c3 !important; /* Crisp, light warm yellow */
        border: 1.5px solid #d97706 !important; /* Earthy amber border */
        border-radius: 12px !important;
        opacity: 1 !important;
    }

    /* Force all text, markdown containers, headings, and labels to dark forest green */
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) *,
    .stApp div[data-testid="stAlert"]:has([data-testid*="warning"]) *,
    .stApp [data-testid="stAlertContainer"]:has([data-testid*="Warning"]) *,
    .stApp [data-testid*="stAlertContentWarning"],
    .stApp [data-testid*="stAlertContentWarning"] *,
    [data-testid*="stAlertContentWarning"],
    [data-testid*="stAlertContentWarning"] * {
        color: #143525 !important; /* High-contrast dark forest green */
        opacity: 1 !important;
    }

    /* Explicit overrides for all nested typography */
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) h1,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) h2,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) h3,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) h4,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) p,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) span,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) strong,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) em,
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) div,
    .stApp [data-testid*="stAlertContentWarning"] h1,
    .stApp [data-testid*="stAlertContentWarning"] h2,
    .stApp [data-testid*="stAlertContentWarning"] h3,
    .stApp [data-testid*="stAlertContentWarning"] h4,
    .stApp [data-testid*="stAlertContentWarning"] p,
    .stApp [data-testid*="stAlertContentWarning"] span,
    .stApp [data-testid*="stAlertContentWarning"] strong,
    .stApp [data-testid*="stAlertContentWarning"] em,
    .stApp [data-testid*="stAlertContentWarning"] div,
    [data-testid*="stAlertContentWarning"] h3,
    [data-testid*="stAlertContentWarning"] p,
    [data-testid*="stAlertContentWarning"] strong {
        color: #143525 !important; /* Explicit deep forest green */
        opacity: 1 !important;
    }

    /* Headings inside warning: bold and crisp */
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) h3,
    .stApp [data-testid*="stAlertContentWarning"] h3,
    [data-testid*="stAlertContentWarning"] h3 {
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.35rem !important;
        color: #143525 !important;
    }

    /* Paragraph and body text inside warning */
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) p,
    .stApp [data-testid*="stAlertContentWarning"] p,
    [data-testid*="stAlertContentWarning"] p {
        color: #1b4332 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) strong,
    .stApp [data-testid*="stAlertContentWarning"] strong,
    [data-testid*="stAlertContentWarning"] strong {
        color: #0f291e !important;
        font-weight: 700 !important;
    }

    /* Alert icon styling */
    .stApp div[data-testid="stAlert"]:has([data-testid*="Warning"]) [data-testid="stAlertDynamicIcon"],
    .stApp [data-testid*="stAlertContentWarning"] [data-testid="stAlertDynamicIcon"],
    [data-testid*="stAlertContentWarning"] [data-testid="stAlertDynamicIcon"] {
        color: #b45309 !important;
        opacity: 1 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR - Navigation & Farm Station Profile
# ==============================================================================
with st.sidebar:
    # Sidebar Header / Logo
    st.markdown("""
    <div style="padding: 0.5rem 0 1.2rem 0; text-align: center;">
        <div style="background: rgba(255, 255, 255, 0.15); width: 56px; height: 56px; border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; font-size: 2rem; border: 1px solid rgba(255, 255, 255, 0.25); margin-bottom: 0.6rem;">🌱</div>
        <h2 style="font-size: 1.3rem; font-weight: 800; margin: 0; color: #ffffff; letter-spacing: -0.01em;">Smart Agriculture</h2>
        <p style="font-size: 0.8rem; color: #b7e4c7; margin: 0.2rem 0 0 0;">Intelligent Decision Agent</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #95d5b2; font-weight: 700; margin-bottom: 0.4rem;'>Main Navigation</p>", unsafe_allow_html=True)
    
    # Controlled Navigation Radio linked to session state
    st.radio(
        "Navigation",
        options=NAV_PAGES,
        key="sidebar_nav_selection",
        on_change=on_sidebar_nav_change
    )

    st.markdown("---")

    # Station Metadata
    latest_reading_meta = database.get_latest_reading()
    st.markdown("<p style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #95d5b2; font-weight: 700; margin-bottom: 0.4rem;'>Station Status</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 0.8rem; border: 1px solid rgba(255, 255, 255, 0.12); font-size: 0.82rem; line-height: 1.5;">
        <div>📡 <strong>Status:</strong> Active & Connected</div>
        <div>⚙️ <strong>Engine:</strong> Rule-Based (IF–THEN)</div>
        <div>🗄️ <strong>Database:</strong> SQLite Verified</div>
    </div>
    """, unsafe_allow_html=True)

    if latest_reading_meta:
        st.caption(f"Last Logged: {latest_reading_meta['timestamp']}")
    else:
        st.caption("No historical records logged yet.")


# ==============================================================================
# Persistent App Header
# ==============================================================================
st.markdown("""
<div class="app-header-container">
    <div class="app-header-left">
        <div class="app-logo-badge">🌱</div>
        <div>
            <h1 class="app-header-title">Smart Agriculture Agent</h1>
            <p class="app-header-sub">Intelligent Agronomic Decisions for Sustainable Crop Yields</p>
        </div>
    </div>
    <div class="app-status-badge">
        <span>🛡️</span>
        <span>Rule-Based Advisory System</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: DASHBOARD
# ==============================================================================
if st.session_state["nav_page"] == "📊 Dashboard":
    st.markdown("## 📊 Farm Overview Dashboard")
    st.markdown("Monitor real-time field state and recent agronomic telemetry.")

    latest_reading = database.get_latest_reading()

    # Top CTA Bar - Starts a new analysis by navigating to Farm Monitoring
    dash_top_col1, dash_top_col2 = st.columns([3, 1])
    with dash_top_col1:
        st.caption("Review your most recent field observations or start a new telemetry analysis.")
    with dash_top_col2:
        st.button(
            "➕ Start New Farm Analysis",
            on_click=set_page,
            args=("🌾 Farm Monitoring",),
            use_container_width=True
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if latest_reading is None:
        # High-contrast friendly empty state
        st.markdown("""
        <div class="clean-empty-state">
            <div class="clean-empty-state-icon">🌱</div>
            <div class="clean-empty-state-title">No Field Readings Recorded Yet</div>
            <div class="clean-empty-state-desc">
                The SQLite database currently holds no historical observations. 
                Record your field's soil moisture and temperature to generate baseline recommendations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            st.button(
                "🚀 Record First Field Observation",
                on_click=set_page,
                args=("🌾 Farm Monitoring",),
                use_container_width=True
            )
    else:
        # Consistent metric cards using Streamlit native primitives
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            st.metric(
                label="💧 Soil Moisture",
                value=f"{latest_reading['soil_moisture']:.1f}%",
                help="Volumetric moisture level in top root zone."
            )
        with m_col2:
            st.metric(
                label="🌡️ Temperature",
                value=f"{latest_reading['temperature']:.1f}°C",
                help="Ambient temperature at crop canopy level."
            )
        with m_col3:
            st.metric(
                label="🌾 Monitored Crop",
                value=latest_reading["crop_type"],
                delta=latest_reading["growth_stage"],
                delta_color="off"
            )
        with m_col4:
            st.metric(
                label="🛡️ Advisory State",
                value=latest_reading["status"],
                delta=latest_reading["action_title"],
                delta_color="normal" if latest_reading["status"] == "Optimal" else "inverse"
            )

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Overview Detail Box
        with st.container(border=True):
            st.markdown("### 📋 Latest Advisory Summary")
            
            status_val = latest_reading["status"]
            if status_val == "Optimal":
                st.success(f"**{latest_reading['action_title']}**", icon="✅")
            elif status_val == "Needs Attention":
                st.warning(f"**{latest_reading['action_title']}**", icon="⚠️")
            else:
                st.error(f"**{latest_reading['action_title']}**", icon="🚨")

            st.markdown(f"**Agronomic Reasoning:** {latest_reading['reasoning']}")
            
            st.markdown("---")
            act_col1, act_col2 = st.columns([1, 1])
            with act_col1:
                st.button(
                    "🔍 View Complete AI Advisor Report",
                    on_click=set_page,
                    args=("🤖 AI Farm Advisor",),
                    use_container_width=True
                )
            with act_col2:
                st.button(
                    "📈 Explore Telemetry Analytics",
                    on_click=set_page,
                    args=("📈 Analytics",),
                    use_container_width=True
                )


# ==============================================================================
# VIEW 2: FARM MONITORING FORM & ON-PAGE ANALYSIS REPORT
# ==============================================================================
elif st.session_state["nav_page"] == "🌾 Farm Monitoring":
    st.markdown("## 🌾 Farm Monitoring & Observation Input")
    st.markdown("Configure current field environmental parameters to evaluate crop hydration, temperature stress, and irrigation needs.")

    with st.container(border=True):
        st.markdown("### 📋 Crop & Environmental Parameters")
        st.caption("Ensure readings reflect verified sensor measurements or calibrated field observations.")

        crop_options = ["Rice", "Wheat", "Maize", "Cotton", "Tomato"]
        stage_options = [
            "Germination / Seedling",
            "Vegetative",
            "Flowering / Reproductive",
            "Maturity / Harvest"
        ]

        f_col1, f_col2 = st.columns(2)

        with f_col1:
            crop_type = st.selectbox(
                "🌾 Select Crop Cultivated",
                options=crop_options,
                index=crop_options.index(st.session_state.get("selected_crop", "Tomato")),
                help="Select the crop currently cultivated in the field parcel."
            )

            growth_stage = st.selectbox(
                "🌱 Active Growth Stage",
                options=stage_options,
                index=stage_options.index(st.session_state.get("selected_stage", "Vegetative")),
                help="Select the physiological development stage of your crop."
            )

        with f_col2:
            soil_moisture = st.slider(
                "💧 Soil Moisture Level (%)",
                min_value=0,
                max_value=100,
                value=int(st.session_state.get("selected_moisture", 45)),
                step=1,
                help="Volumetric water content of the top 20cm root zone. Optimal values vary by crop."
            )

            temperature = st.slider(
                "🌡️ Ambient Air Temperature (°C)",
                min_value=0,
                max_value=50,
                value=int(st.session_state.get("selected_temp", 28)),
                step=1,
                help="Ambient air temperature measured at field canopy level."
            )

        # High-contrast parameter review banner
        st.info(
            f"**Field Observation Summary:** Crop: **{crop_type}** | Stage: **{growth_stage}** | "
            f"Moisture: **{soil_moisture}%** | Temperature: **{temperature}°C**",
            icon="ℹ️"
        )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        analyze_btn = st.button("🌱 Analyze Farm Conditions", use_container_width=True)

        # Process form submission on button click
        if analyze_btn:
            try:
                with st.spinner("Analyzing parameters through agronomic IF–THEN rule matrix..."):
                    # Execute deterministic rule reasoning
                    advisory = rules.evaluate_conditions(
                        crop_type=crop_type,
                        growth_stage=growth_stage,
                        soil_moisture=float(soil_moisture),
                        temperature=float(temperature)
                    )

                    # Persist record in SQLite (only on explicit button click to avoid duplicates)
                    steps_joined = "\n".join(f"• {step}" for step in advisory["practical_steps"])
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    database.save_reading(
                        crop_type=crop_type,
                        growth_stage=growth_stage,
                        soil_moisture=float(soil_moisture),
                        temperature=float(temperature),
                        status=advisory["status"],
                        action_title=advisory["action_title"],
                        reasoning=advisory["reasoning"],
                        practical_steps=steps_joined,
                        timestamp=timestamp_str
                    )

                    # Store in session state for on-page display and persistent retention
                    st.session_state["latest_advisory"] = advisory
                    st.session_state["latest_inputs"] = {
                        "crop": crop_type,
                        "stage": growth_stage,
                        "moisture": float(soil_moisture),
                        "temp": float(temperature),
                        "timestamp": timestamp_str
                    }

            except Exception as e:
                logging.exception("Error executing farm analysis")
                st.error(
                    "An unexpected error occurred during rule evaluation. "
                    "Please check your input values and try again. (Details logged safely)."
                )

    # --------------------------------------------------------------------------
    # CHANGE 2: Display latest analysis directly below the form button
    # --------------------------------------------------------------------------
    if "latest_advisory" in st.session_state and "latest_inputs" in st.session_state:
        adv = st.session_state["latest_advisory"]
        inp = st.session_state["latest_inputs"]
        opt_m = adv["optimal_moisture_range"]
        opt_t = adv["optimal_temp_range"]

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("## 📋 Your Farm Analysis")
            st.caption(f"Analysis generated on {inp['timestamp']} based on submitted field measurements.")

            # Status Indicator Banner
            if adv["status"] == "Optimal":
                st.success(f"### 🟢 {adv['action_title']}\n**Status:** Field Conditions Balanced & Optimal", icon="✅")
            elif adv["status"] == "Needs Attention":
                st.warning(f"### 🟡 {adv['action_title']}\n**Status:** Advisory Alert — Attention Recommended", icon="⚠️")
            else:
                st.error(f"### 🔴 {adv['action_title']}\n**Status:** Urgent Action Required — Physiological Stress Detected", icon="🚨")

            st.markdown("---")

            # Section 1: Current Farm Conditions
            st.markdown("### 1. Current Farm Conditions")
            with st.container(border=True):
                st.markdown(f"- 💧 **Soil Moisture:** `{inp['moisture']:.1f}%`")
                st.markdown(f"- 🌡️ **Ambient Temperature:** `{inp['temp']:.1f}°C`")
                st.markdown(f"- 🌾 **Crop Type:** `{inp['crop']}`")
                st.markdown(f"- 🌱 **Growth Stage:** `{inp['stage']}`")

            # Section 2: Overall Assessment
            st.markdown("### 2. Overall Assessment")
            with st.container(border=True):
                if adv["status"] == "Optimal":
                    assessment_text = (
                        f"The submitted soil moisture of **{inp['moisture']:.1f}%** and ambient temperature of **{inp['temp']:.1f}°C** "
                        f"are balanced within optimal physiological boundaries for **{inp['crop']}** at the **{inp['stage']}** stage. "
                        f"Root respiration and hydration are well-maintained. "
                        f"**Rule-Based Recommendation:** *{adv['action_title']}*."
                    )
                elif adv["moisture_state"] == "Deficit":
                    assessment_text = (
                        f"The submitted soil moisture of **{inp['moisture']:.1f}%** indicates an active root-zone moisture deficit for **{inp['crop']}** "
                        f"during the **{inp['stage']}** phase. Combined with an ambient temperature of **{inp['temp']:.1f}°C** ({adv['temp_state'].lower()}), "
                        f"plants are prone to transpiration stress and reduced vegetative/reproductive development. "
                        f"**Rule-Based Recommendation:** *{adv['action_title']}*."
                    )
                elif adv["moisture_state"] == "Excess":
                    assessment_text = (
                        f"The submitted soil moisture of **{inp['moisture']:.1f}%** indicates excessive root-zone saturation for **{inp['crop']}** "
                        f"at the **{inp['stage']}** phase. Anaerobic conditions in the root zone restrict oxygen uptake. "
                        f"**Rule-Based Recommendation:** *{adv['action_title']}*."
                    )
                else:
                    assessment_text = (
                        f"While soil moisture is recorded at **{inp['moisture']:.1f}%**, the field is experiencing **{adv['temp_state'].lower()}** "
                        f"with an ambient reading of **{inp['temp']:.1f}°C** for **{inp['crop']}** ({inp['stage']}). "
                        f"**Rule-Based Recommendation:** *{adv['action_title']}*."
                    )
                st.markdown(assessment_text)

            # Section 3: Why This Recommendation?
            st.markdown("### 3. Why This Recommendation?")
            with st.container(border=True):
                st.markdown("**Triggered Agronomic Rules & Logic:**")
                st.markdown(f"{adv['reasoning']}")
                st.markdown(
                    f"> **Rule Threshold Comparison:** Observed moisture of `{inp['moisture']:.1f}%` was evaluated against "
                    f"the configured threshold band (`{opt_m[0]:.0f}%–{opt_m[1]:.0f}%`), and observed temperature of `{inp['temp']:.1f}°C` "
                    f"against the configured thermal band (`{opt_t[0]:.0f}°C–{opt_t[1]:.0f}°C`)."
                )

            # Section 4: Recommended Actions
            st.markdown("### 4. Recommended Actions")
            with st.container(border=True):
                st.markdown("**Practical Operational Steps:**")
                for idx, step in enumerate(adv["practical_steps"], 1):
                    st.markdown(f"**{idx}.** {step}")
                
                st.markdown("---")
                st.markdown("**Relevant Agricultural Cautions:**")
                if adv["moisture_state"] == "Excess":
                    st.markdown("⚠️ *Waterlogging Caution: Withhold further watering until root-zone aeration is re-established. Standing surface water increases susceptibility to damping-off and root pathogens.*")
                elif adv["moisture_state"] == "Deficit":
                    st.markdown("⚠️ *Water Deficit Caution: Avoid high-evaporation watering during direct noon sunlight. Apply irrigation during early morning hours for optimal infiltration.*")
                if adv["temp_state"] == "Heat Stress":
                    st.markdown("⚠️ *Thermal Stress Caution: Elevated temperatures accelerate crop transpiration; apply organic mulch across bare soil to preserve root-zone moisture.*")
                elif adv["temp_state"] == "Cold Stress":
                    st.markdown("⚠️ *Cold Stress Caution: Chilling slows metabolic water absorption; do not over-irrigate during persistent low temperatures.*")

            # Section 5: Target Conditions
            st.markdown("### 5. Target Conditions")
            with st.container(border=True):
                st.markdown(f"- **Configured Decision Threshold for Soil Moisture:** `{opt_m[0]:.0f}% – {opt_m[1]:.0f}%`")
                st.markdown(f"- **Configured Decision Threshold for Air Temperature:** `{opt_t[0]:.0f}°C – {opt_t[1]:.0f}°C`")
                st.markdown(f"- **Crop Reference Profile:** {adv.get('crop_description', 'Standard agronomic extension guideline.')}")
                st.markdown("---")
                st.caption(
                    "📌 **Decision Thresholds vs. Scientifically Validated Targets:** "
                    f"The numeric target ranges shown above represent the application's explicitly configured decision thresholds for {inp['crop']} "
                    f"during the {inp['stage']} stage, derived from agricultural extension benchmarks. "
                    "Decision thresholds serve as operational evaluation rules and should not be treated as universal laboratory-validated agronomic targets. "
                    "Actual optimal targets must be verified against site-specific soil physical properties (e.g., sandy loam vs. heavy clay), "
                    "organic matter percentage, irrigation infrastructure, and local microclimate."
                )

            # Section 6: Important Note
            st.markdown("### 6. Important Note")
            st.info(
                "🛡️ **System Transparency Notice:** This agricultural report is generated exclusively using the field readings you entered "
                "and deterministic IF–THEN rule evaluation. The system has no direct connection to live in-ground IoT sensors, automated weather APIs, "
                "or black-box machine-learning models. It is designed as a transparent decision-support tool. For commercial cultivation, "
                "always cross-verify with local agricultural extension specialists.",
                icon="ℹ️"
            )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.button(
                "🔍 Open Full Advisory in AI Farm Advisor Tab",
                on_click=set_page,
                args=("🤖 AI Farm Advisor",),
                use_container_width=True
            )


# ==============================================================================
# VIEW 3: AI FARM ADVISOR (SINGLE-COLUMN VERTICAL LAYOUT)
# ==============================================================================
elif st.session_state["nav_page"] == "🤖 AI Farm Advisor":
    st.markdown("## 🤖 AI Farm Decision Advisor")
    st.markdown("Comprehensive single-column agricultural decision support based on deterministic agronomic rules.")

    # Check if an analysis exists in session state or recover from database
    adv = st.session_state.get("latest_advisory")
    inp = st.session_state.get("latest_inputs")

    if adv is None:
        latest_db = database.get_latest_reading()
        if latest_db:
            adv = rules.evaluate_conditions(
                crop_type=latest_db["crop_type"],
                growth_stage=latest_db["growth_stage"],
                soil_moisture=latest_db["soil_moisture"],
                temperature=latest_db["temperature"]
            )
            inp = {
                "crop": latest_db["crop_type"],
                "stage": latest_db["growth_stage"],
                "moisture": latest_db["soil_moisture"],
                "temp": latest_db["temperature"],
                "timestamp": latest_db["timestamp"]
            }

    if adv is None or inp is None:
        st.markdown("""
        <div class="clean-empty-state">
            <div class="clean-empty-state-icon">🌾</div>
            <div class="clean-empty-state-title">No Farm Analysis Generated Yet</div>
            <div class="clean-empty-state-desc">
                No active advisory is available to display. Navigate to <strong>Farm Monitoring</strong> 
                to configure your field parameters and generate actionable agricultural advice.
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            st.button(
                "🌾 Go to Farm Monitoring",
                on_click=set_page,
                args=("🌾 Farm Monitoring",),
                use_container_width=True
            )
    else:
        # Full-width Single Column Layout (No 2-column split)
        opt_m = adv["optimal_moisture_range"]
        opt_t = adv["optimal_temp_range"]

        # Primary Status Banner
        status_text = adv["status"]
        if status_text == "Optimal":
            st.success(f"### 🟢 {adv['action_title']}\n**Current Evaluation:** Field Conditions Balanced & Optimal", icon="✅")
        elif status_text == "Needs Attention":
            st.warning(f"### 🟡 {adv['action_title']}\n**Current Evaluation:** Advisory Alert — Attention Recommended", icon="⚠️")
        else:
            st.error(f"### 🔴 {adv['action_title']}\n**Current Evaluation:** Urgent Action Required — Physiological Stress Detected", icon="🚨")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # A. Current Farm Conditions
        # ----------------------------------------------------------------------
        st.markdown("### A. Current Farm Conditions")
        with st.container(border=True):
            st.markdown(f"- 💧 **Soil Moisture:** `{inp['moisture']:.1f}%`")
            st.markdown(f"- 🌡️ **Ambient Temperature:** `{inp['temp']:.1f}°C`")
            st.markdown(f"- 🌾 **Cultivated Crop:** `{inp['crop']}`")
            st.markdown(f"- 🌱 **Growth Phase:** `{inp['stage']}`")
            st.markdown(f"- 🕒 **Telemetry Timestamp:** `{inp['timestamp']}`")
            st.caption("Values reflect verified field inputs evaluated by the rule engine.")

        # ----------------------------------------------------------------------
        # B. Current Status
        # ----------------------------------------------------------------------
        st.markdown("### B. Current Status")
        with st.container(border=True):
            st.markdown(f"- **Advisory Classification:** `{adv['status']}` ({adv['status_badge']})")
            st.markdown(f"- **Moisture State Diagnostic:** `{adv['moisture_state']}`")
            st.markdown(f"- **Thermal State Diagnostic:** `{adv['temp_state']}`")
            st.markdown("---")
            st.markdown(f"**Agronomic Meaning:** {adv['reasoning']}")

        # ----------------------------------------------------------------------
        # C. Target Conditions
        # ----------------------------------------------------------------------
        st.markdown("### C. Target Conditions")
        with st.container(border=True):
            st.markdown(f"- **Configured Target Moisture Range:** `{opt_m[0]:.0f}% – {opt_m[1]:.0f}%`")
            st.markdown(f"- **Configured Safe Temperature Range:** `{opt_t[0]:.0f}°C – {opt_t[1]:.0f}°C`")
            st.markdown(f"- **Desirable Physiological State:** {adv.get('crop_description', 'Optimal vegetative balance and metabolic activity.')}")
            st.markdown("---")
            st.caption(
                "📌 **Decision Thresholds vs. Validated Agricultural Targets:** "
                f"The target conditions displayed above are the system's explicitly configured decision thresholds for {inp['crop']} "
                f"during the {inp['stage']} stage. They represent agronomic rule baselines rather than universally validated laboratory targets. "
                "Because optimal root-zone hydration varies with soil composition (sand vs. clay), salinity, and local climate, "
                "these configured thresholds should be verified against site-specific field tests rather than treated as universal agricultural absolutes."
            )

        # ----------------------------------------------------------------------
        # D. Recommended Operations & Practical Steps
        # ----------------------------------------------------------------------
        st.markdown("### D. Recommended Actions & Next Steps")
        with st.container(border=True):
            st.markdown("**Actionable Field Directives:**")
            for idx, step in enumerate(adv["practical_steps"], 1):
                st.markdown(f"**{idx}.** {step}")

            st.markdown("---")
            st.markdown("**Operational Cautions:**")
            if adv["moisture_state"] == "Excess":
                st.markdown("⚠️ *Drainage Caution: Check furrow outlets and drainage swales to evacuate standing surface water.*")
            elif adv["moisture_state"] == "Deficit":
                st.markdown("⚠️ *Irrigation Caution: Avoid high-evaporation noon hours. Irrigate in early morning to maximize soil penetration.*")
            if adv["temp_state"] == "Heat Stress":
                st.markdown("⚠️ *Heat Caution: High solar radiation causes rapid soil moisture depletion; inspect canopy turgidity daily.*")
            elif adv["temp_state"] == "Cold Stress":
                st.markdown("⚠️ *Cold Caution: Low temperatures slow root water uptake; avoid over-watering.*")

        # ----------------------------------------------------------------------
        # E. Important System Notes & Limitations
        # ----------------------------------------------------------------------
        st.markdown("### E. Important Notes & System Transparency")
        st.info(
            "🛡️ **System Transparency Notice:** This agricultural report is generated exclusively using the field readings you entered "
            "and deterministic IF–THEN rule evaluation. The system has no direct connection to live in-ground IoT sensors, automated weather APIs, "
            "or black-box machine-learning models. It is designed as a transparent decision-support tool. For commercial cultivation, "
            "always cross-verify with local agricultural extension specialists.",
            icon="ℹ️"
        )

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Single-column navigation buttons
        st.button(
            "➕ Start New Farm Analysis",
            on_click=set_page,
            args=("🌾 Farm Monitoring",),
            use_container_width=True
        )

        st.button(
            "📈 View Historical Telemetry Analytics",
            on_click=set_page,
            args=("📈 Analytics",),
            use_container_width=True
        )


# ==============================================================================
# VIEW 4: ANALYTICS
# ==============================================================================
elif st.session_state["nav_page"] == "📈 Analytics":
    st.markdown("## 📈 Field Environmental Analytics")
    st.markdown("Analyze historical telemetry patterns and observation trends logged in SQLite (`smart_agri.db`).")

    df_hist = database.get_history(limit=100)

    if df_hist.empty:
        st.markdown("""
        <div class="clean-empty-state">
            <div class="clean-empty-state-icon">📈</div>
            <div class="clean-empty-state-title">No Historical Telemetry Found</div>
            <div class="clean-empty-state-desc">
                There are currently no observations stored in SQLite. 
                Complete a field assessment in <strong>Farm Monitoring</strong> to generate analytical charts.
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            st.button(
                "🌾 Go to Farm Monitoring",
                on_click=set_page,
                args=("🌾 Farm Monitoring",),
                use_container_width=True
            )
    else:
        # Overview summary stats
        stat1, stat2, stat3, stat4 = st.columns(4)
        with stat1:
            st.metric("Total Observations", len(df_hist))
        with stat2:
            avg_m = df_hist["Soil Moisture (%)"].mean()
            st.metric("Average Moisture", f"{avg_m:.1f}%")
        with stat3:
            avg_t = df_hist["Temperature (°C)"].mean()
            st.metric("Average Temperature", f"{avg_t:.1f}°C")
        with stat4:
            opt_cnt = len(df_hist[df_hist["Status"] == "Optimal"])
            opt_pct = (opt_cnt / len(df_hist)) * 100
            st.metric("Optimal Condition Rate", f"{opt_pct:.0f}%")

        st.markdown("---")

        # Time-series charts (chronological order)
        df_chart = df_hist.copy().iloc[::-1].reset_index(drop=True)

        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            with st.container(border=True):
                st.markdown("#### 💧 Soil Moisture Over Time (%)")
                st.line_chart(
                    data=df_chart.set_index("Timestamp")[["Soil Moisture (%)"]],
                    color="#0284c7"
                )

        with ch_col2:
            with st.container(border=True):
                st.markdown("#### 🌡️ Temperature Over Time (°C)")
                st.line_chart(
                    data=df_chart.set_index("Timestamp")[["Temperature (°C)"]],
                    color="#d97706"
                )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        dist_col1, dist_col2 = st.columns(2)
        with dist_col1:
            with st.container(border=True):
                st.markdown("#### 🌾 Observations by Crop Type")
                st.bar_chart(df_hist["Crop"].value_counts(), color="#2d6a4f")

        with dist_col2:
            with st.container(border=True):
                st.markdown("#### 🛡️ Advisory Status Distribution")
                st.bar_chart(df_hist["Status"].value_counts(), color="#52b788")


# ==============================================================================
# VIEW 5: ANALYSIS HISTORY
# ==============================================================================
elif st.session_state["nav_page"] == "📜 Analysis History":
    st.markdown("## 📜 Telemetry History & Audit Log")
    st.markdown("Review, filter, and export verified records stored in the SQLite database (`smart_agri.db`).")

    df_hist = database.get_history(limit=100)

    if df_hist.empty:
        st.markdown("""
        <div class="clean-empty-state">
            <div class="clean-empty-state-icon">📋</div>
            <div class="clean-empty-state-title">No Database Records Available</div>
            <div class="clean-empty-state-desc">
                The SQLite audit table is currently empty. 
                Perform a farm analysis to start populating your historical telemetry log.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Action Toolbar
        tb_col1, tb_col2 = st.columns([1, 1])
        with tb_col1:
            csv_data = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Telemetry as CSV",
                data=csv_data,
                file_name=f"smart_agri_telemetry_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with tb_col2:
            with st.expander("⚠️ Classroom Demo Reset Options"):
                st.caption("Erase all records in SQLite for a clean demonstration.")
                confirm_reset = st.checkbox("Confirm database reset")
                if st.button("Clear SQLite Audit Log", disabled=not confirm_reset):
                    database.clear_history()
                    if "latest_advisory" in st.session_state:
                        del st.session_state["latest_advisory"]
                    if "latest_inputs" in st.session_state:
                        del st.session_state["latest_inputs"]
                    st.success("All SQLite records cleared successfully.")
                    st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Tabular Display
        st.dataframe(
            df_hist,
            use_container_width=True,
            hide_index=True
        )

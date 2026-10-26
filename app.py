"""
Smart Agriculture Agent - Decision Support System
A modern agtech Streamlit application featuring multi-tenant farmer authentication,
multilingual localization (14 Indian languages), live Open-Meteo weather integration,
precision irrigation guidance, AI crop suitability recommender, crop disease/pest risk analyzer,
daily farming plans, multilingual assistant, and deterministic IF-THEN agronomic rule reasoning.
"""

import streamlit as st
import pandas as pd
import datetime
import logging
from typing import Dict, Any, Optional
import streamlit.components.v1 as components

# Domain & Data Layer Modules
import database
import rules
import auth
import translations
from translations import t
import weather_service
import crop_recommender
import risk_analyzer
import daily_plan
import assistant

# Configure logging (strict privacy: zero passwords or sensitive data logged)
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

# Initialize database schema and migrations
database.init_db()

# 13 Standardized Navigation Page Keys (Stable Internal Keys)
NAV_PAGE_KEYS = [
    "nav_dashboard",
    "nav_profile",
    "nav_weather",
    "nav_crop_recommend",
    "nav_monitoring",
    "nav_advisor",
    "nav_irrigation",
    "nav_risk_analyzer",
    "nav_daily_plan",
    "nav_analytics",
    "nav_history",
    "nav_assistant",
    "nav_settings"
]

# ==============================================================================
# Session State Initialization
# ==============================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "farmer" not in st.session_state:
    st.session_state["farmer"] = None

if "language" not in st.session_state:
    st.session_state["language"] = "en"

if "active_view" not in st.session_state:
    st.session_state["active_view"] = "nav_dashboard"

if "sidebar_nav_radio" not in st.session_state:
    st.session_state["sidebar_nav_radio"] = "nav_dashboard"

if "asst_messages" not in st.session_state:
    st.session_state["asst_messages"] = []

if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"

def set_page(page_name: str):
    """Safely queues a navigation page change (accepts key or translated label)."""
    target = page_name
    for k in NAV_PAGE_KEYS:
        if page_name == k or page_name == t(k):
            target = k
            break
    st.session_state["active_view"] = target
    st.session_state["sidebar_nav_radio"] = target

def logout():
    """Clears authenticated session safely while retaining public language preference."""
    saved_lang = st.session_state.get("language", "en")
    st.session_state["authenticated"] = False
    st.session_state["farmer"] = None
    st.session_state["active_view"] = "nav_dashboard"
    st.session_state["auth_mode"] = "login"
    st.session_state["language"] = saved_lang
    if "login_page_language_select" in st.session_state:
        del st.session_state["login_page_language_select"]
    if "sidebar_lang_selector" in st.session_state:
        del st.session_state["sidebar_lang_selector"]
    if "user_lang_synced" in st.session_state:
        del st.session_state["user_lang_synced"]
    if "asst_messages" in st.session_state:
        st.session_state["asst_messages"] = []
    if "latest_advisory" in st.session_state:
        del st.session_state["latest_advisory"]
    if "latest_inputs" in st.session_state:
        del st.session_state["latest_inputs"]
    try:
        st.session_state["sidebar_nav_radio"] = "nav_dashboard"
    except Exception:
        pass
    st.rerun()


# ==============================================================================
# High-Contrast Accessible Styling & RTL Support
# ==============================================================================
st.markdown("""
<style>
    /* Google Fonts for clean legibility across Indian scripts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Application Canvas */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Headings: Dark Forest Green on Light Backgrounds */
    h1, h2, h3, h4, h5, h6 {
        color: #1b4332 !important;
        font-weight: 700 !important;
    }

    /* Scoped typography for main content canvas (avoids trampling dark-green elements) */
    div[data-testid="stMainBlockContainer"] p,
    div[data-testid="stMainBlockContainer"] li,
    div[data-testid="stMainBlockContainer"] label:not(button label),
    section.main p,
    section.main label {
        color: #1e293b;
    }

    /* ==========================================================================
       SIDEBAR & NAVIGATION STYLING (GREEN BACKGROUND: LIGHT TEXT REQUIRED)
       ========================================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #133926 0%, #1b4332 50%, #204e38 100%) !important;
        color: #ffffff !important;
        box-shadow: 4px 0 20px rgba(19, 57, 38, 0.12);
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] > div label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not(div[data-baseweb="select"] *):not(div[data-baseweb="input"] *),
    section[data-testid="stSidebar"] caption,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p {
        color: #f1f8f3 !important;
    }

    /* Inside sidebar inputs and selectbox: preserve crisp dark text on white container */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] div[data-baseweb="input"] * {
        color: #0f172a !important;
    }

    /* Sidebar Radio Navigation Options - Scoped strictly to sidebar */
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        display: none;
    }

    /* Unselected / Default Sidebar Radio Item */
    section[data-testid="stSidebar"] div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-baseweb="radio"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
    section[data-testid="stSidebar"] .stRadio label {
        background: rgba(255, 255, 255, 0.09) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: 10px !important;
        padding: 0.55rem 0.85rem !important;
        margin-bottom: 0.35rem !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label *,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label *,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-baseweb="radio"] *,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label *,
    section[data-testid="stSidebar"] .stRadio label *,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] span,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Hover State for Sidebar Radio */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-baseweb="radio"]:hover,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover,
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255, 255, 255, 0.22) !important;
        border-color: #86efac !important;
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover *,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover *,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-baseweb="radio"]:hover *,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover *,
    section[data-testid="stSidebar"] .stRadio label:hover * {
        color: #ffffff !important;
    }

    /* Selected / Active Navigation Item */
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked),
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-baseweb="radio"]:has(input:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked),
    section[data-testid="stSidebar"] .stRadio label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(135deg, #2d6a4f 0%, #40916c 100%) !important;
        border: 1.5px solid #a7f3d0 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25) !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] *,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] *,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) *,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) *,
    section[data-testid="stSidebar"] div[role="radiogroup"] [data-baseweb="radio"]:has(input:checked) *,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] *,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) *,
    section[data-testid="stSidebar"] .stRadio label[data-checked="true"] *,
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Radio button indicators (circles / svgs) inside sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] + div,
    section[data-testid="stSidebar"] [data-baseweb="radio"] input[type="radio"] + div {
        border-color: #a7f3d0 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"]:checked + div,
    section[data-testid="stSidebar"] [data-baseweb="radio"] input[type="radio"]:checked + div {
        background-color: #52b788 !important;
        border-color: #ffffff !important;
    }

    /* Sidebar Secondary / Logout Button */
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"],
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.4) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] *,
    section[data-testid="stSidebar"] .stButton > button * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover,
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        border-color: #86efac !important;
    }

    /* ==========================================================================
       TOP BRAND HEADER BANNER
       ========================================================================== */
    .app-header-container {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 60%, #388e63 100%);
        color: #ffffff;
        padding: 1.25rem 1.6rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 16px rgba(27, 67, 50, 0.15);
    }

    .app-header-container * {
        color: #ffffff !important;
    }

    /* ==========================================================================
       METRIC CARDS & CONTAINERS (WEATHER & DASHBOARD)
       ========================================================================== */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-top: 3.5px solid #2d6a4f !important;
        border-radius: 12px !important;
        padding: 0.85rem 1rem !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    }

    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] *,
    div[data-testid="stMetricValue"] > div {
        color: #1b4332 !important;
        font-weight: 800 !important;
        font-size: 1.3rem !important;
        line-height: 1.25 !important;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] label,
    div[data-testid="stMetricLabel"] span {
        font-size: 0.88rem !important;
        color: #475569 !important;
        font-weight: 600 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        line-height: 1.35 !important;
    }

    .dash-metric-card {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-top: 3.5px solid #2d6a4f;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        min-height: 104px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .dash-metric-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(45, 106, 79, 0.08);
    }

    .dash-metric-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #475569 !important;
        margin-bottom: 0.35rem;
        line-height: 1.35;
        white-space: normal;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    .dash-metric-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: #1b4332 !important;
        line-height: 1.25;
        word-break: break-word;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border: 1.5px solid #e2e8f0 !important;
        background-color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        padding: 0.85rem !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] li,
    div[data-testid="stVerticalBlockBorderWrapper"] span:not(button *) {
        color: #0f172a !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] strong,
    div[data-testid="stVerticalBlockBorderWrapper"] b {
        color: #1b4332 !important;
    }

    /* ==========================================================================
       BUTTON CONTRAST (PRIMARY, SECONDARY & DISABLED)
       ========================================================================== */
    /* Primary buttons (Dark green gradient with crisp white text) */
    button[data-testid="baseButton-primary"],
    button[data-testid="stBaseButton-primary"],
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button,
    div[data-testid="stDownloadButton"] > button,
    .stDownloadButton > button,
    .stDownloadButton a {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%) !important;
        color: #ffffff !important;
        border: 1.5px solid #1b4332 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.62rem 1.25rem !important;
        box-shadow: 0 3px 8px rgba(27, 67, 50, 0.22) !important;
        transition: all 0.2s ease !important;
    }

    button[data-testid="baseButton-primary"] *,
    button[data-testid="stBaseButton-primary"] *,
    .stButton > button[kind="primary"] *,
    .stFormSubmitButton > button *,
    div[data-testid="stDownloadButton"] > button *,
    .stDownloadButton > button *,
    .stDownloadButton a * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    .stDownloadButton > button:hover,
    .stDownloadButton a:hover {
        background: linear-gradient(135deg, #245840 0%, #388e63 100%) !important;
        border-color: #52b788 !important;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(27, 67, 50, 0.32) !important;
    }

    /* Common Questions Preset Buttons in AI Assistant - Opposite High Contrast (Dark Green with Crisp White Text) */
    div[class*="st-key-cq_btn"] button,
    div[class*="st-key-cq_btn"] button[data-testid="stBaseButton-secondary"],
    div[class*="st-key-cq_btn"] button[data-testid="baseButton-secondary"],
    div[class*="st-key-cq_btn"] button[data-testid="stBaseButton-primary"],
    div[class*="st-key-cq_btn"] button[data-testid="baseButton-primary"],
    div[data-testid="stExpander"] div[class*="st-key-cq_btn"] button {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%) !important;
        color: #ffffff !important;
        border: 1.5px solid #143525 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1rem !important;
        box-shadow: 0 3px 8px rgba(27, 67, 50, 0.22) !important;
        transition: all 0.2s ease !important;
    }

    div[class*="st-key-cq_btn"] button *,
    div[class*="st-key-cq_btn"] button p,
    div[class*="st-key-cq_btn"] button span,
    div[class*="st-key-cq_btn"] button div,
    div[data-testid="stExpander"] div[class*="st-key-cq_btn"] button * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    div[class*="st-key-cq_btn"] button:hover,
    div[class*="st-key-cq_btn"] button:hover *,
    div[class*="st-key-cq_btn"] button:hover p,
    div[class*="st-key-cq_btn"] button:hover span,
    div[data-testid="stExpander"] div[class*="st-key-cq_btn"] button:hover {
        background: linear-gradient(135deg, #245840 0%, #388e63 100%) !important;
        border-color: #52b788 !important;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(27, 67, 50, 0.32) !important;
    }

    /* Secondary buttons (Clean white background, green border, dark green text) */
    button[data-testid="baseButton-secondary"],
    button[data-testid="stBaseButton-secondary"],
    .stButton > button[kind="secondary"],
    .stButton > button:not([data-testid="baseButton-primary"]):not([data-testid="stBaseButton-primary"]):not([kind="primary"]) {
        background: #ffffff !important;
        color: #1b4332 !important;
        border: 2px solid #86efac !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.62rem 1.25rem !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }

    button[data-testid="baseButton-secondary"] *,
    button[data-testid="stBaseButton-secondary"] *,
    button[data-testid="baseButton-secondary"] p,
    button[data-testid="stBaseButton-secondary"] p,
    button[data-testid="baseButton-secondary"] span,
    button[data-testid="stBaseButton-secondary"] span,
    button[data-testid="baseButton-secondary"] div,
    button[data-testid="stBaseButton-secondary"] div,
    .stButton > button[kind="secondary"] *,
    .stButton > button[kind="secondary"] p,
    .stButton > button:not([data-testid="baseButton-primary"]):not([data-testid="stBaseButton-primary"]):not([kind="primary"]) *,
    .stButton > button:not([data-testid="baseButton-primary"]):not([data-testid="stBaseButton-primary"]):not([kind="primary"]) p {
        color: #1b4332 !important;
        font-weight: 700 !important;
    }

    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([data-testid="baseButton-primary"]):not([data-testid="stBaseButton-primary"]):not([kind="primary"]):hover {
        background: #f0fdf4 !important;
        border-color: #2d6a4f !important;
        color: #143525 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(27, 67, 50, 0.15) !important;
    }

    button[data-testid="baseButton-secondary"]:hover *,
    button[data-testid="stBaseButton-secondary"]:hover *,
    .stButton > button[kind="secondary"]:hover *,
    .stButton > button:not([data-testid="baseButton-primary"]):not([data-testid="stBaseButton-primary"]):not([kind="primary"]):hover * {
        color: #143525 !important;
    }

    /* Disabled Button State (Readable muted contrast) */
    button:disabled,
    button[disabled] {
        background: #f1f5f9 !important;
        color: #94a3b8 !important;
        border: 1.5px solid #cbd5e1 !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
        transform: none !important;
    }

    button:disabled *,
    button[disabled] * {
        color: #94a3b8 !important;
    }

    /* ==========================================================================
       DROPDOWNS, SELECT BOXES & POPOVERS (ACCESSIBLE CONTRAST)
       ========================================================================== */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
    }

    div[data-baseweb="select"] * {
        color: #0f172a !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12) !important;
    }

    li[role="option"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        padding: 0.6rem 1rem !important;
    }

    li[role="option"] * {
        color: #0f172a !important;
    }

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #f0fdf4 !important;
        color: #166534 !important;
    }

    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"] * {
        color: #166534 !important;
        font-weight: 700 !important;
    }

    /* MultiSelect Tags */
    div[data-baseweb="tag"] {
        background-color: #dcfce7 !important;
        border: 1px solid #86efac !important;
        border-radius: 6px !important;
        padding: 2px 8px !important;
    }

    div[data-baseweb="tag"] * {
        color: #14532d !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="tag"] span[role="button"] {
        color: #166534 !important;
    }

    /* ==========================================================================
       FORM INPUTS (TEXT, NUMBER, TEXTAREA & AI ASSISTANT INPUT)
       ========================================================================== */
    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {
        font-weight: 700 !important;
        color: #1e293b !important;
        font-size: 0.92rem !important;
        margin-bottom: 0.25rem !important;
    }

    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #2d6a4f !important;
        box-shadow: 0 0 0 2px rgba(45, 106, 79, 0.2) !important;
    }

    div[data-baseweb="input"] input,
    input[data-testid="stTextInput"],
    div[data-testid="stTextInput"] input,
    textarea {
        color: #0f172a !important;
        background-color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="input"] input::placeholder,
    div[data-testid="stTextInput"] input::placeholder,
    input::placeholder,
    textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #64748b !important;
    }

    div[data-testid="stNumberInput"] button {
        color: #0f172a !important;
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
    }

    div[data-testid="stNumberInput"] button * {
        color: #0f172a !important;
    }

    /* ==========================================================================
       TABS STYLING
       ========================================================================== */
    div[data-baseweb="tab-list"] {
        background: #f1f5f9 !important;
        padding: 6px !important;
        border-radius: 12px !important;
        gap: 8px !important;
        border: 1.5px solid #cbd5e1 !important;
        margin-bottom: 1rem !important;
    }

    button[data-baseweb="tab"] {
        border-radius: 9px !important;
        padding: 0.65rem 1.3rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        background: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        transition: all 0.2s ease !important;
        flex: 1 !important;
        text-align: center !important;
        justify-content: center !important;
    }

    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span {
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #1e293b !important;
    }

    button[data-baseweb="tab"]:hover {
        background: #f0fdf4 !important;
        border-color: #86efac !important;
    }

    button[data-baseweb="tab"]:hover p,
    button[data-baseweb="tab"]:hover span {
        color: #1b4332 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%) !important;
        border-color: #1b4332 !important;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.25) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span {
        color: #ffffff !important;
    }

    div[data-baseweb="tab-highlight"],
    div[data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ==========================================================================
       EXPANDERS
       ========================================================================== */
    div[data-testid="stExpander"] {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        background-color: #ffffff !important;
    }

    div[data-testid="stExpander"] details summary {
        color: #1b4332 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1rem !important;
    }

    div[data-testid="stExpander"] details summary p,
    div[data-testid="stExpander"] details summary span {
        color: #1b4332 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stExpander"] details summary svg {
        fill: #1b4332 !important;
    }

    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 0.8rem 1rem !important;
        color: #0f172a !important;
    }

    /* ==========================================================================
       SLIDERS & CONTROLS
       ========================================================================== */
    div[data-testid="stSlider"] div[data-testid="stTickBarMin"],
    div[data-testid="stSlider"] div[data-testid="stTickBarMax"] {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
    }

    div[data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #1b4332 !important;
        font-weight: 700 !important;
    }

    /* Checkboxes & Radios in Main Content (Strictly scoped so sidebar is unaffected!) */
    div[data-testid="stMainBlockContainer"] div[data-testid="stCheckbox"] label span,
    div[data-testid="stMainBlockContainer"] div[data-testid="stCheckbox"] label p,
    section.main div[data-testid="stCheckbox"] label span,
    section.main div[data-testid="stCheckbox"] label p {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] label span,
    div[data-testid="stMainBlockContainer"] div[data-testid="stRadio"] label p,
    section.main div[data-testid="stRadio"] label span,
    section.main div[data-testid="stRadio"] label p {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* ==========================================================================
       INLINE CODE & BADGES
       ========================================================================== */
    code {
        color: #1e293b !important;
        background-color: #f1f5f9 !important;
        padding: 0.15rem 0.4rem !important;
        border-radius: 5px !important;
        font-size: 0.88em !important;
        border: 1px solid #cbd5e1 !important;
    }

    section[data-testid="stSidebar"] code {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    /* Captions in Main Body vs Sidebar */
    caption,
    .stCaption,
    div[data-testid="stCaptionContainer"],
    div[data-testid="stCaptionContainer"] p {
        color: #475569 !important;
        font-size: 0.88rem !important;
    }

    section[data-testid="stSidebar"] caption,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p {
        color: #b7e4c7 !important;
    }

    /* ==========================================================================
       ALERTS (HIGH CONTRAST ALL 4 STATES)
       ========================================================================== */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        padding: 0.9rem 1.1rem !important;
    }

    /* SUCCESS */
    div[data-testid="stAlert"]:has([data-testid*="Success"]),
    div[data-testid="stAlert"]:has([data-testid*="success"]) {
        background-color: #f0fdf4 !important;
        border: 1.5px solid #22c55e !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Success"]) *,
    div[data-testid="stAlert"]:has([data-testid*="success"]) * {
        color: #14532d !important;
        font-weight: 600 !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Success"]) code {
        color: #14532d !important;
        background-color: #dcfce7 !important;
        border: 1px solid #bbf7d0 !important;
    }

    /* ERROR */
    div[data-testid="stAlert"]:has([data-testid*="Error"]),
    div[data-testid="stAlert"]:has([data-testid*="error"]) {
        background-color: #fef2f2 !important;
        border: 1.5px solid #ef4444 !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Error"]) *,
    div[data-testid="stAlert"]:has([data-testid*="error"]) * {
        color: #7f1d1d !important;
        font-weight: 600 !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Error"]) code {
        color: #7f1d1d !important;
        background-color: #fee2e2 !important;
        border: 1px solid #fecaca !important;
    }

    /* WARNING */
    div[data-testid="stAlert"]:has([data-testid*="Warning"]),
    div[data-testid="stAlert"]:has([data-testid*="warning"]),
    .stAlert[data-baseweb="notification"]:has([data-testid*="Warning"]) {
        background-color: #fffbeb !important;
        border: 1.5px solid #f59e0b !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Warning"]) *,
    div[data-testid="stAlert"]:has([data-testid*="warning"]) * {
        color: #78350f !important;
        font-weight: 600 !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Warning"]) code {
        color: #78350f !important;
        background-color: #fef3c7 !important;
        border: 1px solid #fde68a !important;
    }

    /* INFO */
    div[data-testid="stAlert"]:has([data-testid*="Info"]),
    div[data-testid="stAlert"]:has([data-testid*="info"]) {
        background-color: #f0f9ff !important;
        border: 1.5px solid #38bdf8 !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Info"]) *,
    div[data-testid="stAlert"]:has([data-testid*="info"]) * {
        color: #0c4a6e !important;
        font-weight: 600 !important;
    }
    div[data-testid="stAlert"]:has([data-testid*="Info"]) code {
        color: #0c4a6e !important;
        background-color: #e0f2fe !important;
        border: 1px solid #bae6fd !important;
    }

    /* ==========================================================================
       DATAFRAMES, TABLES & AUDIT HISTORY
       ========================================================================== */
    table, div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    table {
        border-collapse: collapse !important;
        width: 100% !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* Table column headers: Forest green background with crisp white text */
    th, thead tr th, table thead th, thead th {
        background-color: #1b4332 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 0.65rem 0.9rem !important;
        border: 1px solid #143525 !important;
        font-size: 0.9rem !important;
        text-align: left !important;
    }

    th *, thead tr th *, table thead th *, thead th * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Table body cells: White/light background with dark text */
    td, tbody tr td, table tbody td, tbody td {
        background-color: #ffffff !important;
        color: #0f172a !important;
        padding: 0.6rem 0.9rem !important;
        border: 1px solid #e2e8f0 !important;
        font-size: 0.88rem !important;
    }

    td *, tbody tr td *, table tbody td *, tbody td * {
        color: #0f172a !important;
    }

    tbody tr:nth-of-type(even) td {
        background-color: #f8fafc !important;
    }

    tbody tr:hover td {
        background-color: #f0fdf4 !important;
    }

    /* Streamlit native dataframe container */
    div[data-testid="stDataFrame"] {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Column headers inside Dataframe (high-contrast white on dark green) */
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #1b4332 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    div[data-testid="stDataFrame"] div[role="columnheader"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Data cells inside Dataframe (high-contrast dark text on white/light) */
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    div[data-testid="stDataFrame"] div[role="gridcell"] * {
        color: #0f172a !important;
    }

    .clean-empty-state {
        background: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 14px;
        padding: 2.2rem 1.8rem;
        text-align: center;
        margin: 1.2rem 0;
    }

    .clean-empty-state-icon { font-size: 2.6rem; margin-bottom: 0.5rem; }
    .clean-empty-state-title { font-size: 1.15rem; font-weight: 700; color: #1b4332 !important; margin-bottom: 0.3rem; }
    .clean-empty-state-desc { font-size: 0.92rem; color: #475569 !important; max-width: 520px; margin: 0 auto 1.2rem auto; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# RTL support for Urdu
if st.session_state.get("language") == "ur":
    st.markdown("""
    <style>
        .stApp, div[data-testid="stMarkdownContainer"], p, span, label, h1, h2, h3, h4, h5, h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        section[data-testid="stSidebar"] {
            direction: ltr !important;
            text-align: left !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# Helper Function: Readable Field Assessment Presentation
# ==============================================================================
def render_field_assessment(
    adv: Dict[str, Any],
    inp: Optional[Dict[str, Any]] = None,
    section_title: Optional[str] = None,
    show_metrics: bool = True
):
    """
    Renders an accessible, beautifully formatted field assessment using native
    Streamlit containers, metrics, alerts, and structured markdown.
    """
    if not isinstance(adv, dict):
        st.info("Field assessment data is currently unavailable.")
        return

    sec_title = section_title or t("lbl_generated_assessment")
    st.markdown(f"### {sec_title}")

    status = adv.get("status", "Normal")
    action_title = adv.get("action_title", "Monitor field conditions")

    if status == "Optimal":
        st.success(f"**{t('status_optimal')}:** {action_title}", icon="✅")
    elif status in ["Advisory", "Warning", "Needs Attention"]:
        st.warning(f"**{t('status_advisory')}:** {action_title}", icon="⚠️")
    else:
        st.error(f"**{t('status_critical')}:** {action_title}", icon="🚨")

    if show_metrics:
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            m_val = inp.get("moisture") if inp else None
            try:
                st.metric(t("lbl_soil_moisture"), f"{float(m_val):.1f}%" if m_val is not None else "N/A")
            except (ValueError, TypeError):
                st.metric(t("lbl_soil_moisture"), "N/A")
        with m_col2:
            t_val = inp.get("temp") if inp else None
            try:
                st.metric(t("lbl_temperature"), f"{float(t_val):.1f}°C" if t_val is not None else "N/A")
            except (ValueError, TypeError):
                st.metric(t("lbl_temperature"), "N/A")
        with m_col3:
            m_state = adv.get("moisture_state", "Normal")
            st.metric(t("lbl_moisture_regime"), str(m_state))
        with m_col4:
            t_state = adv.get("temp_state", "Normal")
            st.metric(t("lbl_thermal_status"), str(t_state))

    st.markdown(f"#### 🔍 {t('lbl_diagnostic_findings')}")
    reasons = adv.get("reasoning", [])
    if isinstance(reasons, list):
        for pt in reasons:
            if pt and isinstance(pt, str):
                st.markdown(f"- {pt.strip(' •')}")
    elif isinstance(reasons, str) and reasons:
        clean_pts = [p.strip(" •") for p in (reasons.split("\n") if "\n" in reasons else reasons.split(" • ")) if p.strip(" •")]
        for p in clean_pts:
            st.markdown(f"- {p}")

    steps = adv.get("practical_steps", [])
    if steps:
        st.markdown(f"#### 🎯 {t('lbl_recommended_steps')}")
        if isinstance(steps, list):
            for idx, step in enumerate(steps, 1):
                if step and isinstance(step, str):
                    st.markdown(f"**{idx}.** {step.strip(' •')}")
        elif isinstance(steps, str):
            step_items = [s.strip(" •|") for s in (steps.replace("|", "\n").split("\n")) if s.strip(" •|")]
            for idx, step in enumerate(step_items, 1):
                st.markdown(f"**{idx}.** {step}")

    crop_desc = adv.get("crop_context") or adv.get("crop_description", "")
    if crop_desc:
        st.caption(f"🌾 **{t('lbl_agronomic_context')}:** {crop_desc}")


# ==============================================================================
# Top Brand Header Banner (Visible Across All Pages)
# ==============================================================================
active_code = st.session_state.get("language", "en")
st.markdown(f"""
<div class="app-header-container">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
        <div>
            <div style="font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.6rem;">
                <span>🌱</span> {t('app_title')}
            </div>
            <div style="font-size: 0.95rem; opacity: 0.92; margin-top: 0.2rem; font-weight: 500;">
                {t('app_subtitle')}
            </div>
        </div>
        <div style="background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 10px; padding: 0.45rem 0.9rem; font-size: 0.85rem; font-weight: 600;">
            🌐 {translations.SUPPORTED_LANGUAGES.get(active_code, 'English')}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# AUTHENTICATION SCREEN (IF NOT LOGGED IN)
# ==============================================================================
if not st.session_state.get("authenticated", False) or not st.session_state.get("farmer"):
    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])

    with auth_col2:
        # Language Selector on Welcome Screen
        lang_codes = list(translations.SUPPORTED_LANGUAGES.keys())
        login_lang = st.selectbox(
            "🌐 Select Language / భాషను ఎంచుకోండి / भाषा चुनें",
            options=lang_codes,
            format_func=lambda code: translations.SUPPORTED_LANGUAGES[code],
            index=lang_codes.index(active_code) if active_code in lang_codes else 0,
            key="login_page_language_select"
        )
        if login_lang != active_code:
            st.session_state["language"] = login_lang
            st.rerun()

        st.markdown(f"""
        <div style="background: #ffffff; border: 1.5px solid #86efac; border-radius: 16px; padding: 1.8rem; box-shadow: 0 10px 25px rgba(27, 67, 50, 0.08); margin-top: 1rem;">
            <div style="text-align: center; margin-bottom: 1.2rem;">
                <span style="font-size: 2.8rem;">🌾</span>
                <h3 style="color: #1b4332; margin: 0.4rem 0 0.2rem 0; font-weight: 800;">{t('welcome_title', default='Welcome to Smart Agriculture Agent 🌱')}</h3>
                <p style="color: #475569; font-size: 0.92rem; margin: 0;">{t('welcome_desc', default='Your intelligent farming assistant helps you monitor field conditions, understand crop risks, plan irrigation, and make informed farming decisions.')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        current_auth_mode = st.session_state.get("auth_mode", "login")

        # Prominent, High-Contrast Segmented Selector (Login vs Create Account)
        nav_col_login, nav_col_reg = st.columns(2, gap="medium")
        with nav_col_login:
            is_login_active = (current_auth_mode == "login")
            if st.button(
                f"🔐 {t('tab_login')}",
                key="btn_auth_tab_login",
                type="primary" if is_login_active else "secondary",
                use_container_width=True
            ):
                st.session_state["auth_mode"] = "login"
                st.rerun()

        with nav_col_reg:
            is_reg_active = (current_auth_mode == "register")
            if st.button(
                f"📝 {t('tab_register')}",
                key="btn_auth_tab_register",
                type="primary" if is_reg_active else "secondary",
                use_container_width=True
            ):
                st.session_state["auth_mode"] = "register"
                st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # LOGIN VIEW
        # ----------------------------------------------------------------------
        if current_auth_mode == "login":
            with st.container(border=True):
                st.markdown(f"### 🔐 {t('tab_login')}")
                st.caption(t("login_desc"))
                with st.form("login_form", clear_on_submit=False):
                    phone_in = st.text_input(
                        t("lbl_phone"),
                        placeholder="e.g. 9876543210",
                        help="Enter your 10-digit mobile number.",
                        key="login_phone"
                    )
                    pwd_in = st.text_input(
                        t("lbl_password"),
                        type="password",
                        placeholder="••••••••",
                        help="Enter your secure account password.",
                        key="login_pwd"
                    )
                    login_btn = st.form_submit_button(t("btn_login"), use_container_width=True)

                if login_btn:
                    if not phone_in.strip() or not pwd_in.strip():
                        st.error(t("msg_auth_missing_fields"))
                    elif not auth.validate_phone_number(phone_in):
                        st.error(t("auth_err_phone"))
                    else:
                        authenticated_farmer = database.authenticate_farmer(phone_in, pwd_in)
                        if authenticated_farmer:
                            st.session_state["authenticated"] = True
                            st.session_state["farmer"] = authenticated_farmer
                            # Restore saved farmer language preference
                            fav_lang = authenticated_farmer.get("preferred_language")
                            if fav_lang and fav_lang in translations.SUPPORTED_LANGUAGES:
                                st.session_state["language"] = fav_lang
                            st.success(f"{t('auth_success_login')} {authenticated_farmer['full_name']}!")
                            st.rerun()
                        else:
                            st.error(t("auth_err_creds"))

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; color: #475569; font-size: 0.92rem; font-weight: 500; margin-bottom: 0.5rem;'>{t('reg_desc')}</div>", unsafe_allow_html=True)
                if st.button(f"✨ {t('tab_register')}", key="btn_switch_to_register_footer", type="secondary", use_container_width=True):
                    st.session_state["auth_mode"] = "register"
                    st.rerun()

        # ----------------------------------------------------------------------
        # REGISTRATION VIEW
        # ----------------------------------------------------------------------
        else:
            with st.container(border=True):
                st.markdown(f"### 📝 {t('tab_register')}")
                st.caption(t("reg_desc"))
                with st.form("register_form", clear_on_submit=False):
                    reg_name = st.text_input(t("lbl_full_name"), placeholder="e.g. Ramesh Patel", key="reg_full_name")
                    reg_phone = st.text_input(t("lbl_phone"), placeholder="e.g. 9876543210", key="reg_phone")
                    reg_pwd = st.text_input(t("lbl_password"), type="password", placeholder="At least 6 characters", key="reg_pwd")
                    reg_pwd2 = st.text_input(t("lbl_confirm_password"), type="password", placeholder="Repeat password", key="reg_pwd2")
                    reg_lang = st.selectbox(
                        t("lbl_pref_lang"),
                        options=lang_codes,
                        format_func=lambda code: translations.SUPPORTED_LANGUAGES[code],
                        index=lang_codes.index(active_code) if active_code in lang_codes else 0,
                        key="reg_pref_lang"
                    )
                    reg_btn = st.form_submit_button(t("btn_register"), use_container_width=True)

                if reg_btn:
                    if not reg_name.strip() or not reg_phone.strip() or not reg_pwd.strip():
                        st.error(t("msg_auth_missing_fields"))
                    elif len(reg_pwd) < 6:
                        st.error(t("auth_err_pwd_short"))
                    elif reg_pwd != reg_pwd2:
                        st.error(t("auth_err_pwd_mismatch"))
                    elif not auth.validate_phone_number(reg_phone):
                        st.error(t("auth_err_phone"))
                    else:
                        success, msg, new_farmer = database.create_farmer(
                            full_name=reg_name,
                            phone_number=reg_phone,
                            password=reg_pwd,
                            preferred_language=reg_lang
                        )
                        if success:
                            st.success(f"{t('auth_success_registered')} Please sign in with your credentials.")
                            st.session_state["auth_mode"] = "login"
                            st.rerun()
                        else:
                            st.error(f"Registration failed: {msg}")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; color: #475569; font-size: 0.92rem; font-weight: 500; margin-bottom: 0.5rem;'>Already have an account? / ఇప్పటికే ఖాతా ఉందా?</div>", unsafe_allow_html=True)
                if st.button(f"👉 {t('tab_login')}", key="btn_switch_to_login_footer", type="secondary", use_container_width=True):
                    st.session_state["auth_mode"] = "login"
                    st.rerun()

        st.stop()


# ==============================================================================
# AUTHENTICATED USER CONTEXT
# ==============================================================================
farmer = st.session_state.get("farmer")
if not farmer:
    st.stop()
farmer_id = farmer["id"]
farmer_profile = database.get_farmer_profile(farmer_id) or {}

# Synchronize preferred language from profile on initial load
if "user_lang_synced" not in st.session_state:
    prof_lang = farmer.get("preferred_language") or farmer_profile.get("preferred_language")
    if prof_lang and prof_lang in translations.SUPPORTED_LANGUAGES:
        st.session_state["language"] = prof_lang
    st.session_state["user_lang_synced"] = True

# Fetch isolated telemetry and weather
latest_reading = database.get_latest_reading(farmer_id=farmer_id)
weather_data = weather_service.get_weather_forecast(
    latitude=farmer_profile.get("latitude", 16.3067),
    longitude=farmer_profile.get("longitude", 80.4365),
    district_name=farmer_profile.get("location_district", "Local Farm")
)


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 0.4rem 0 0.8rem 0; text-align: center;">
        <div style="background: rgba(255, 255, 255, 0.15); width: 48px; height: 48px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.8rem; border: 1px solid rgba(255, 255, 255, 0.25); margin-bottom: 0.4rem;">🌱</div>
        <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: -0.01em; color: #ffffff;">{t('app_title')}</div>
        <div style="font-size: 0.72rem; color: #b7e4c7; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">{t('lbl_authenticated_mode', default='Farmer Session')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Farmer Account Card
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; padding: 0.85rem; margin-bottom: 1rem;">
        <div style="font-size: 0.72rem; text-transform: uppercase; color: #b7e4c7; font-weight: 700;">{t('lbl_welcome_farmer')}</div>
        <div style="font-size: 1.05rem; font-weight: 800; color: #ffffff; margin: 0.2rem 0;">👨‍🌾 {farmer['full_name']}</div>
        <div style="font-size: 0.8rem; color: #d8f3dc;">📱 {farmer['phone_number']}</div>
        <div style="font-size: 0.75rem; color: #a7f3d0; margin-top: 0.25rem;">📍 {farmer_profile.get('location_district', 'Local Station')} | {farmer_profile.get('farm_size_acres', 2.0)} ac</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Language Switcher inside Sidebar
    active_code = st.session_state.get("language", "en")
    lang_opts = list(translations.SUPPORTED_LANGUAGES.keys())
    sidebar_lang = st.selectbox(
        "🌐 Language / భాష",
        options=lang_opts,
        format_func=lambda code: translations.SUPPORTED_LANGUAGES[code],
        index=lang_opts.index(active_code) if active_code in lang_opts else 0,
        key="sidebar_lang_selector"
    )
    if sidebar_lang != active_code:
        st.session_state["language"] = sidebar_lang
        database.update_farmer_language(farmer_id, sidebar_lang)
        st.rerun()

    st.markdown("---")
    st.markdown("<p style='font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #95d5b2; font-weight: 700; margin-bottom: 0.3rem;'>Navigation</p>", unsafe_allow_html=True)

    # Ensure current navigation value in session state is valid
    nav_val = st.session_state.get("sidebar_nav_radio")
    if nav_val not in NAV_PAGE_KEYS:
        nav_val = st.session_state.get("active_view", "nav_dashboard")
        if nav_val not in NAV_PAGE_KEYS:
            nav_val = "nav_dashboard"
        st.session_state["sidebar_nav_radio"] = nav_val

    selected_view = st.radio(
        "Navigation",
        options=NAV_PAGE_KEYS,
        format_func=lambda k, lang=active_code: t(k, lang=lang),
        key="sidebar_nav_radio"
    )
    st.session_state["active_view"] = selected_view


    st.markdown("---")
    if st.button(f"🚪 {t('btn_logout')}", use_container_width=True, key="sidebar_logout_btn", on_click=logout):
        logout()

active_view = st.session_state.get("active_view", "nav_dashboard")


# ==============================================================================
# VIEW 1: DASHBOARD / OVERVIEW
# ==============================================================================
if active_view == "nav_dashboard":
    st.markdown(f"## {t('nav_dashboard')}")
    st.caption(t("dash_caption", default="Monitor your farm details, field conditions, and agricultural insights in one place."))

    farm_acres_val = f"{farmer_profile.get('farm_size_acres', 3.0)} Acres"
    soil_type_val = str(farmer_profile.get("soil_type") or "Clay Loam")
    water_avail_val = str(farmer_profile.get("water_availability") or "Moderate")
    primary_crop_val = str(farmer_profile.get("primary_crop") or "Rice")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="dash-metric-card">
            <div class="dash-metric-title">{t("lbl_total_area", default=t("lbl_farm_size", default="Total Farm Area (Acres)"))}</div>
            <div class="dash-metric-value">{farm_acres_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="dash-metric-card">
            <div class="dash-metric-title">{t("lbl_soil_type", default="Dominant Soil Classification")}</div>
            <div class="dash-metric-value">{soil_type_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="dash-metric-card">
            <div class="dash-metric-title">{t("lbl_water_avail", default="Field Water Availability Level")}</div>
            <div class="dash-metric-value">{water_avail_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="dash-metric-card">
            <div class="dash-metric-title">{t("lbl_primary_crop", default="Primary Cultivated Crop")}</div>
            <div class="dash-metric-value">{primary_crop_val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown(f"### ⛅ {t('weather_title')}")
            st.markdown(f"**{t('lbl_temperature', default='Temperature')}:** `{weather_data['temperature']:.1f}°C` | **{t('lbl_humidity', default='Humidity')}:** `{weather_data['humidity']:.0f}%`")
            st.markdown(f"**{t('lbl_location', default='Location')}:** `{weather_data['location_name']}` | **{t('lbl_precipitation', default='Precipitation')}:** `{weather_data['rain_prob_today']:.0f}%`")
            st.caption(f"Source: {weather_data['source_label']}")
            st.button(f"🔍 {t('btn_quick_view')} {t('weather_title')}", on_click=set_page, args=("nav_weather",), use_container_width=True)

        with st.container(border=True):
            st.markdown(f"### 💧 {t('irrigation_title')}")
            if latest_reading:
                st.markdown(f"**{t('lbl_soil_moisture', default='Soil Moisture')}:** `{latest_reading['soil_moisture']:.1f}%` ({latest_reading['status']})")
                st.markdown(f"**{t('lbl_current_action', default='Current Action')}:** `{latest_reading['action_title']}`")
                st.markdown(f"**{t('lbl_diagnostic_findings', default='Diagnostic Findings')}:** {latest_reading['reasoning']}")
            else:
                st.info(t("irrigation_no_data"))
            st.button(f"💧 {t('btn_quick_view')} {t('irrigation_title')}", on_click=set_page, args=("nav_irrigation",), use_container_width=True)

    with col_b:
        with st.container(border=True):
            st.markdown(f"### 📋 {t('plan_title')}")
            st.markdown(t("dash_plan_summary", default="Chronological morning, afternoon, and evening tasks synthesized for current conditions."))
            st.button(f"📋 {t('btn_quick_view')} {t('plan_title')}", on_click=set_page, args=("nav_daily_plan",), use_container_width=True)

        with st.container(border=True):
            st.markdown(f"### 🌾 {t('crop_rec_title')} & {t('risk_title')}")
            st.markdown(t("dash_crop_rec_summary", default="Evaluate crop suitability from soil nutrients, or inspect disease & pest risks."))
            rc1, rc2 = st.columns(2)
            with rc1:
                st.button(f"🌾 {t('nav_crop_recommend')}", on_click=set_page, args=("nav_crop_recommend",), use_container_width=True)
            with rc2:
                st.button(f"🛡️ {t('nav_risk_analyzer')}", on_click=set_page, args=("nav_risk_analyzer",), use_container_width=True)


# ==============================================================================
# VIEW 2: FARM PROFILE
# ==============================================================================
elif active_view == "nav_profile":
    st.markdown(f"## {t('profile_title')}")
    st.markdown(t("profile_desc"))

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            farm_name_val = st.text_input(
                t("lbl_farm_name"),
                value=farmer_profile.get("farm_name", f"{farmer['full_name']}'s Farm"),
                help="Descriptive name for your agricultural parcel or holding."
            )
            district_val = st.text_input(
                t("lbl_district"),
                value=farmer_profile.get("location_district", "Guntur, Andhra Pradesh"),
                help="Village, District, and State where your farm is located."
            )
            size_val = st.number_input(
                t("lbl_farm_size"),
                min_value=0.1, max_value=500.0,
                value=float(farmer_profile.get("farm_size_acres", 3.0)),
                step=0.5,
                help="Total cultivated field area measured in standard acres."
            )
            soil_options = ["Clay Loam", "Sandy Loam", "Black Soil", "Red Soil", "Alluvial", "Clay", "Loam"]
            curr_soil = farmer_profile.get("soil_type", "Clay Loam")
            soil_val = st.selectbox(
                t("lbl_soil_type"),
                options=soil_options,
                index=soil_options.index(curr_soil) if curr_soil in soil_options else 0,
                help="Soil texture determines moisture retention and nutrient capacity."
            )

        with col2:
            crop_options = ["Rice", "Wheat", "Maize", "Cotton", "Tomato"]
            curr_crop = farmer_profile.get("primary_crop", "Tomato")
            crop_val = st.selectbox(
                t("lbl_primary_crop"),
                options=crop_options,
                index=crop_options.index(curr_crop) if curr_crop in crop_options else 4,
                help="Dominant crop cultivated in the active parcel."
            )
            irrig_options = ["Drip Irrigation", "Furrow / Basin", "Sprinkler", "Canal / Flood", "Rainfed"]
            curr_irrig = farmer_profile.get("irrigation_system", "Drip Irrigation")
            irrig_val = st.selectbox(
                t("lbl_irrigation_type"),
                options=irrig_options,
                index=irrig_options.index(curr_irrig) if curr_irrig in irrig_options else 0,
                help="Installed water application infrastructure."
            )
            water_options = ["High (Canal / Reliable Borewell)", "Moderate (Scheduled Borewell / Shared Supply)", "Low (Rainfed / Water Scarcity)"]
            curr_water = farmer_profile.get("water_availability", "Moderate")
            water_val = st.selectbox(
                t("lbl_water_avail"),
                options=["High", "Moderate", "Low"],
                index=1 if curr_water == "Moderate" else (0 if curr_water == "High" else 2),
                help="Security and volume of available irrigation sources."
            )
            ph_val = st.number_input(
                t("lbl_soil_ph"),
                min_value=4.0, max_value=9.5,
                value=float(farmer_profile.get("soil_ph", 6.8)),
                step=0.1,
                help="Soil reaction from Soil Health Card test (Neutral is 6.5-7.2)."
            )

        st.markdown("---")
        st.markdown("#### 🧪 Soil Health Card Nutrients (Available Macronutrients)")
        n1, n2, n3 = st.columns(3)
        with n1:
            n_val = st.number_input(
                t("lbl_nitrogen"),
                min_value=0.0, max_value=500.0,
                value=float(farmer_profile.get("nitrogen", 140.0)),
                step=5.0,
                help="Available Nitrogen from soil lab report (kg/ha)."
            )
        with n2:
            p_val = st.number_input(
                t("lbl_phosphorus"),
                min_value=0.0, max_value=300.0,
                value=float(farmer_profile.get("phosphorus", 45.0)),
                step=2.0,
                help="Available Phosphorus (P2O5) (kg/ha)."
            )
        with n3:
            k_val = st.number_input(
                t("lbl_potassium"),
                min_value=0.0, max_value=500.0,
                value=float(farmer_profile.get("potassium", 180.0)),
                step=5.0,
                help="Available Potassium (K2O) (kg/ha)."
            )

        save_btn = st.form_submit_button(t("btn_save_profile"), use_container_width=True)

        if save_btn:
            database.upsert_farmer_profile(
                farmer_id=farmer_id,
                farm_name=farm_name_val,
                location_district=district_val,
                farm_size_acres=size_val,
                soil_type=soil_val,
                primary_crop=crop_val,
                irrigation_system=irrig_val,
                water_availability=water_val,
                soil_ph=ph_val,
                nitrogen=n_val,
                phosphorus=p_val,
                potassium=k_val,
                latitude=farmer_profile.get("latitude", 16.3067),
                longitude=farmer_profile.get("longitude", 80.4365)
            )
            st.success(t("msg_profile_saved"))
            st.rerun()


# ==============================================================================
# VIEW 3: WEATHER
# ==============================================================================
elif active_view == "nav_weather":
    st.markdown(f"## {t('weather_title')}")
    st.markdown(t("weather_desc"))

    if not weather_data.get("fallback", False):
        st.info(f"📡 **{weather_data['source_label']}** for `{weather_data['location_name']}`. (100% Free, Zero API Keys Required).", icon="ℹ️")
    else:
        st.warning(f"⚠️ **{weather_data['source_label']}**", icon="⚠️")

    w1, w2, w3, w4 = st.columns(4)
    with w1:
        st.metric(t("lbl_temperature"), f"{weather_data['temperature']:.1f}°C")
    with w2:
        st.metric(t("lbl_humidity"), f"{weather_data['humidity']:.0f}%")
    with w3:
        st.metric(t("lbl_wind"), f"{weather_data['wind_speed']:.1f} km/h")
    with w4:
        st.metric(t("lbl_precipitation"), f"{weather_data['rain_prob_today']:.0f}%")

    st.markdown("---")
    st.markdown("### 📅 7-Day Agricultural Forecast Trend")
    dates = weather_data.get("daily_dates", [])
    t_max = weather_data.get("daily_temp_max", [])
    t_min = weather_data.get("daily_temp_min", [])
    rain_p = weather_data.get("daily_rain_prob", [])

    if dates and len(dates) == len(t_max) == len(t_min) == len(rain_p):
        df_forecast = pd.DataFrame({
            "Date": dates,
            "Max Temp (°C)": t_max,
            "Min Temp (°C)": t_min,
            "Rain Probability (%)": rain_p
        })
        wch1, wch2 = st.columns(2)
        with wch1:
            st.markdown("#### 🌡️ Temperature Trajectory (7-Day)")
            st.line_chart(df_forecast.set_index("Date")[["Max Temp (°C)", "Min Temp (°C)"]])
        with wch2:
            st.markdown("#### 🌧️ Precipitation Probability (7-Day)")
            st.bar_chart(df_forecast.set_index("Date")["Rain Probability (%)"])

        with st.expander("📊 View Detailed 7-Day Numerical Table", expanded=False):
            st.dataframe(df_forecast, use_container_width=True, hide_index=True)
    else:
        st.info("7-day meteorological forecast data is temporarily unavailable. Please check your network connection or try refreshing.")


# ==============================================================================
# VIEW 4: CROP RECOMMENDATIONS
# ==============================================================================
elif active_view == "nav_crop_recommend":
    st.markdown(f"## {t('crop_rec_title')}")
    st.markdown(t("crop_rec_desc"))

    with st.container(border=True):
        st.markdown("### 📋 Active Evaluation Parameters")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.markdown(f"- **Soil Type:** `{farmer_profile.get('soil_type', 'Clay Loam')}`")
            st.markdown(f"- **Soil pH:** `{farmer_profile.get('soil_ph', 6.8):.1f}`")
        with p2:
            st.markdown(f"- **Nitrogen (N):** `{farmer_profile.get('nitrogen', 140.0):.0f} kg/ha`")
            st.markdown(f"- **Phosphorus (P):** `{farmer_profile.get('phosphorus', 45.0):.0f} kg/ha`")
        with p3:
            st.markdown(f"- **Potassium (K):** `{farmer_profile.get('potassium', 180.0):.0f} kg/ha`")
            st.markdown(f"- **Temperature:** `{weather_data['temperature']:.1f}°C` (Live)")
        with p4:
            rec_season = st.selectbox(
                "📅 Target Planting Season",
                options=["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)"],
                index=0
            )
            rec_water = st.selectbox(
                "💧 Available Water Supply",
                options=["High", "Moderate", "Low"],
                index=0 if farmer_profile.get("water_availability") == "High" else (2 if farmer_profile.get("water_availability") == "Low" else 1),
                help="Water source security for this parcel."
            )

    ranked_crops = crop_recommender.recommend_crops(
        soil_type=farmer_profile.get("soil_type", "Clay Loam"),
        soil_ph=float(farmer_profile.get("soil_ph", 6.8)),
        nitrogen=float(farmer_profile.get("nitrogen", 140.0)),
        phosphorus=float(farmer_profile.get("phosphorus", 45.0)),
        potassium=float(farmer_profile.get("potassium", 180.0)),
        temperature=float(weather_data["temperature"]),
        humidity=float(weather_data["humidity"]),
        water_availability=rec_water,
        season=rec_season
    )

    st.markdown("### 🏆 Agronomic Crop Suitability Ranking")
    if ranked_crops:
        df_crop_scores = pd.DataFrame([
            {"Crop": item["crop"], "Suitability Score": item["score"]}
            for item in ranked_crops
        ]).set_index("Crop")
        st.bar_chart(df_crop_scores)

        for item in ranked_crops:
            with st.container(border=True):
                r_col1, r_col2 = st.columns([4, 1])
                with r_col1:
                    idx = item['rank']
                    st.markdown(f"#### **{idx}. {item['crop']}** (Water Need: `{item['water_requirement']}`)")
                    st.markdown(f"*{item['description']}*")
                    st.markdown("**Agronomic Matching Factors:**")
                    for reason in item["reasons"]:
                        st.markdown(f"• {reason}")
                with r_col2:
                    st.metric("Suitability Score", f"{item['score']}/100")
    else:
        st.info("No crop recommendations available for the selected parameters. Adjust your soil or water settings.")


# ==============================================================================
# VIEW 5: FIELD MONITORING (SENSORS & OBSERVATIONS)
# ==============================================================================
elif active_view == "nav_monitoring":
    st.markdown(f"## {t('nav_monitoring')}")
    st.markdown("Input field sensor measurements or calibrated observations to execute deterministic agronomic rules.")

    with st.container(border=True):
        st.markdown("### 📋 Field Sensor & Observation Form")
        st.caption("All submitted readings are stored strictly under your private farmer account.")

        crop_list = ["Rice", "Wheat", "Maize", "Cotton", "Tomato"]
        growth_stages = ["Vegetative", "Flowering", "Fruiting / Grain Fill", "Maturity"]

        fm_col1, fm_col2 = st.columns(2)
        with fm_col1:
            def_crop = farmer_profile.get("primary_crop", "Tomato")
            f_crop = st.selectbox(
                "🌾 Cultivated Crop Type",
                options=crop_list,
                index=crop_list.index(def_crop) if def_crop in crop_list else 4,
                key="fm_crop_select"
            )
            f_stage = st.selectbox(
                "🌱 Current Growth Stage",
                options=growth_stages,
                index=0,
                key="fm_stage_select"
            )
            f_moisture = st.slider(
                "💧 Soil Moisture Level (%)",
                min_value=5.0, max_value=95.0,
                value=float(latest_reading["soil_moisture"]) if latest_reading else 50.0,
                step=1.0,
                help="Calibrated volumetric water content percentage."
            )

        with fm_col2:
            f_temp = st.slider(
                "🌡️ Ambient Field Temperature (°C)",
                min_value=5.0, max_value=50.0,
                value=float(weather_data["temperature"]),
                step=0.5,
                help="Air temperature at canopy height."
            )
            f_symptoms = st.multiselect(
                "🔍 Observed Field Symptoms (Optional)",
                options=[
                    "Wilting leaves", "Yellowing foliage", "White powdery mildew spots",
                    "Dark water-soaked lesions", "Leaf curling", "Chewed leaf margins"
                ],
                default=[]
            )

        st.info(f"**Submitted Field Summary:** Crop: **{f_crop}** | Stage: **{f_stage}** | Soil Moisture: **{f_moisture}%** | Ambient Temp: **{f_temp}°C**", icon="ℹ️")

        analyze_btn = st.button("🌱 Analyze Farm Conditions & Save Log", use_container_width=True)

        if analyze_btn:
            try:
                advisory_res = rules.evaluate_all_rules(
                    crop=f_crop,
                    growth_stage=f_stage,
                    soil_moisture=f_moisture,
                    temperature=f_temp,
                    leaf_wetness_hours=0.0,
                    symptoms=f_symptoms
                )
                now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                record_id = database.save_reading(
                    farmer_id=farmer_id,
                    crop_type=f_crop,
                    growth_stage=f_stage,
                    soil_moisture=f_moisture,
                    temperature=f_temp,
                    status=advisory_res["status"],
                    action_title=advisory_res["action_title"],
                    reasoning="\n".join(advisory_res["reasoning"]) if isinstance(advisory_res["reasoning"], list) else str(advisory_res["reasoning"]),
                    practical_steps=" | ".join(advisory_res["practical_steps"]) if isinstance(advisory_res["practical_steps"], list) else str(advisory_res["practical_steps"]),
                    timestamp=now_ts
                )

                st.session_state["latest_advisory"] = advisory_res
                st.session_state["latest_inputs"] = {
                    "crop": f_crop, "stage": f_stage, "moisture": f_moisture,
                    "temp": f_temp, "symptoms": f_symptoms, "timestamp": now_ts
                }

                st.success("Field reading analyzed and saved to your private audit log!")
                st.rerun()

            except Exception as e:
                logging.exception(f"Rule evaluation error: {e}")
                st.error(f"Error during rule evaluation: {e}")


    if "latest_advisory" in st.session_state:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        render_field_assessment(
            st.session_state["latest_advisory"],
            st.session_state.get("latest_inputs")
        )


# ==============================================================================
# VIEW 6: AI FARM ADVISOR
# ==============================================================================
elif active_view == "nav_advisor":
    st.markdown(f"## {t('nav_advisor')}")
    st.caption("Comprehensive single-column agricultural decision report grounded in transparent IF-THEN rules.")

    try:
        adv_data = st.session_state.get("latest_advisory")
        inp_data = st.session_state.get("latest_inputs")

        if not adv_data and latest_reading:
            c_name = latest_reading.get("crop_type") or latest_reading.get("crop") or farmer_profile.get("primary_crop", "Tomato")
            s_name = latest_reading.get("growth_stage", "Vegetative")
            m_val = float(latest_reading.get("soil_moisture") or 50.0)
            t_val = float(latest_reading.get("temperature") or weather_data.get("temperature", 28.0))

            try:
                adv_data = rules.evaluate_all_rules(
                    crop=c_name,
                    growth_stage=s_name,
                    soil_moisture=m_val,
                    temperature=t_val,
                    leaf_wetness_hours=0.0,
                    symptoms=[]
                )
            except Exception as ex_eval:
                logging.exception(f"Rule re-evaluation failed: {ex_eval}")
                r_raw = str(latest_reading.get("reasoning") or "")
                s_raw = str(latest_reading.get("practical_steps") or "")
                r_list = [r.strip(" •") for r in (r_raw.split("\n") if "\n" in r_raw else r_raw.split(" • ")) if r.strip(" •")]
                s_list = [s.strip(" •|") for s in (s_raw.split("\n") if "\n" in s_raw else s_raw.split(" | ")) if s.strip(" •|")]
                adv_data = {
                    "status": latest_reading.get("status", "Normal"),
                    "action_title": latest_reading.get("action_title", "Farm Advisory"),
                    "moisture_state": "Evaluated",
                    "temp_state": "Evaluated",
                    "reasoning": r_list or [r_raw],
                    "practical_steps": s_list or [s_raw],
                    "crop_context": f"Logged for {c_name} ({s_name})"
                }

            inp_data = {
                "crop": c_name,
                "stage": s_name,
                "moisture": m_val,
                "temp": t_val,
                "timestamp": latest_reading.get("timestamp", "Recent")
            }

        if not adv_data and not latest_reading:
            # Baseline profile-driven guidance if no field reading recorded yet
            p_crop = farmer_profile.get("primary_crop", "Tomato")
            p_temp = float(weather_data.get("temperature", 28.0))
            opt_band = rules.get_optimal_moisture_band(p_crop, "Vegetative")
            baseline_moisture = (opt_band[0] + opt_band[1]) / 2.0

            st.info("💡 **Baseline Profile Advisory:** Showing baseline guidance for your cultivated crop based on current meteorological conditions. Record specific sensor measurements in **Field Monitoring** for custom field diagnostics.", icon="ℹ️")

            try:
                adv_data = rules.evaluate_all_rules(
                    crop=p_crop,
                    growth_stage="Vegetative",
                    soil_moisture=baseline_moisture,
                    temperature=p_temp,
                    leaf_wetness_hours=0.0,
                    symptoms=[]
                )
                inp_data = {
                    "crop": p_crop,
                    "stage": "Vegetative",
                    "moisture": baseline_moisture,
                    "temp": p_temp,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            except Exception:
                pass

        if not adv_data:
            st.markdown(f"""
            <div class="clean-empty-state">
                <div class="clean-empty-state-icon">📡</div>
                <div class="clean-empty-state-title">No Field Observations Recorded Yet</div>
                <div class="clean-empty-state-desc">To generate a transparent agronomic advisory, please record your field sensor readings or visual observations.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button(f"👉 {t('nav_monitoring')}", on_click=set_page, args=("nav_monitoring",), use_container_width=True)
        else:
            render_field_assessment(
                adv=adv_data,
                inp=inp_data,
                section_title="📋 Grounded Agronomic Decision Report"
            )

            with st.container(border=True):
                st.markdown("### 🔬 Decision Logic & Parameter Audit")
                inp = inp_data or {}
                crop_name = inp.get("crop") or farmer_profile.get("primary_crop", "Tomato")
                stage_name = inp.get("stage", "Vegetative")

                opt_m = rules.get_optimal_moisture_band(crop_name, stage_name)
                opt_t = rules.get_safe_temp_range(crop_name)

                m_disp = f"{float(inp['moisture']):.1f}%" if inp.get("moisture") is not None else "N/A"
                t_disp = f"{float(inp['temp']):.1f}°C" if inp.get("temp") is not None else "N/A"

                st.markdown("### A. Recorded Farm Conditions")
                st.markdown(f"- 💧 **Soil Moisture:** `{m_disp}`")
                st.markdown(f"- 🌡️ **Ambient Air Temperature:** `{t_disp}`")
                st.markdown(f"- 🌾 **Cultivated Crop:** `{crop_name}`")
                st.markdown(f"- 🌱 **Growth Phase:** `{stage_name}`")
                st.markdown(f"- 🕒 **Observation Timestamp:** `{inp.get('timestamp', 'Recent')}`")

                st.markdown("---")
                st.markdown("### B. Configured Agronomic Decision Thresholds")
                st.markdown(f"- **Target Soil Moisture Range:** `{opt_m[0]:.0f}% – {opt_m[1]:.0f}%`")
                st.markdown(f"- **Configured Safe Temperature Range:** `{opt_t[0]:.0f}°C – {opt_t[1]:.0f}°C`")

                st.markdown("---")
                st.info("🛡️ **System Transparency Notice:** This report is generated strictly from the values you entered using transparent deterministic rules. It does not replace site-specific soil testing.", icon="ℹ️")

    except Exception as e:
        logging.exception(f"Unexpected error in AI Farm Advisor view: {e}")
        st.error("An unexpected error occurred while preparing your farm advisory. Please check your field monitoring records.", icon="⚠️")


# ==============================================================================
# VIEW 7: SMART IRRIGATION GUIDANCE
# ==============================================================================
elif active_view == "nav_irrigation":
    st.markdown(f"## {t('irrigation_title')}")
    st.markdown(t("irrigation_desc"))

    crop = farmer_profile.get("primary_crop", "Tomato")
    soil = farmer_profile.get("soil_type", "Clay Loam")
    irrig_sys = farmer_profile.get("irrigation_system", "Drip Irrigation")

    with st.container(border=True):
        st.markdown(f"### 📋 Current Irrigation Infrastructure: **{crop}** on **{soil}**")
        st.caption(f"Installed System: **{irrig_sys}**")

        opt_m = rules.get_optimal_moisture_band(crop, "Vegetative")

        if latest_reading:
            m_curr = latest_reading["soil_moisture"]
            eval_res = rules.evaluate_moisture_condition(crop, "Vegetative", m_curr)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Observed Moisture (%)", f"{m_curr:.1f}%")
            with m2:
                st.metric("Target Band (%)", f"{opt_m[0]:.0f}% – {opt_m[1]:.0f}%")
            with m3:
                st.metric("Hydration Status", eval_res["moisture_state"])

            st.markdown("#### 💧 Moisture Level vs. Target Agronomic Thresholds")
            df_irr_chart = pd.DataFrame({
                "Parameter": ["Current Observed", "Target Min", "Target Max"],
                "Moisture (%)": [m_curr, opt_m[0], opt_m[1]]
            }).set_index("Parameter")
            st.bar_chart(df_irr_chart)

            st.markdown("---")
            if eval_res["status"] == "Optimal":
                st.success(f"**Optimal Moisture Balance:** {eval_res['action_title']}", icon="✅")
            elif eval_res["status"] == "Warning":
                st.warning(f"**Water Stress Alert:** {eval_res['action_title']}", icon="⚠️")
            else:
                st.error(f"**Severe Deficit Alert:** {eval_res['action_title']}", icon="🚨")

            st.markdown(f"**Agronomic Guidance:** {eval_res['reasoning']}")
        else:
            st.info("No soil moisture recorded yet. Enter a reading in Field Monitoring to evaluate irrigation run-times.")
            st.button(f"👉 {t('nav_monitoring')}", on_click=set_page, args=("nav_monitoring",), use_container_width=True)


# ==============================================================================
# VIEW 8: CROP DISEASE & PEST RISK
# ==============================================================================
elif active_view == "nav_risk_analyzer":
    st.markdown(f"## {t('risk_title')}")
    st.markdown(t("risk_desc"))
    st.warning(t("risk_disclaimer"), icon="⚠️")

    crop = farmer_profile.get("primary_crop", "Tomato")
    stage = latest_reading.get("growth_stage", "Vegetative") if latest_reading else "Vegetative"
    moisture = latest_reading.get("soil_moisture", 60.0) if latest_reading else 60.0

    threats = risk_analyzer.analyze_crop_risks(
        crop_type=crop,
        growth_stage=stage,
        temperature=weather_data["temperature"],
        humidity=weather_data["humidity"],
        soil_moisture=moisture
    )

    st.markdown(f"### 🔍 Detected Environmental Risk Correlations for **{crop}**")
    if not threats:
        st.success("✅ No elevated disease or insect risks detected under current microclimate conditions.", icon="✅")
    else:
        df_threats = pd.DataFrame([
            {"Threat": t["threat_name"], "Risk Score": t["risk_score"]}
            for t in threats
        ]).set_index("Threat")
        st.markdown("#### 🛡️ Microclimate Risk Severity Comparison")
        st.bar_chart(df_threats)

        for threat in threats:
            with st.container(border=True):
                st.markdown(f"### 🛡️ {threat['threat_name']}")
                st.markdown(f"**Early Warning Signs:** {threat['early_signs']}")
                st.markdown(f"**Contributing Conditions:** {' • '.join(threat['factors_matched'])}")
                st.markdown("**Recommended Preventive Actions:**")
                for measure in threat["preventive_measures"]:
                    st.markdown(f"• {measure}")
                st.caption(f"Risk Score: {threat['risk_score']}/100")


# ==============================================================================
# VIEW 9: DAILY FARMING PLAN
# ==============================================================================
elif active_view == "nav_daily_plan":
    st.markdown(f"## {t('plan_title')}")
    st.markdown(t("plan_desc"))

    crop = farmer_profile.get("primary_crop", "Tomato")
    stage = latest_reading.get("growth_stage", "Vegetative") if latest_reading else "Vegetative"
    latest_r = latest_reading or {"soil_moisture": 55.0, "status": "Optimal"}
    threats = risk_analyzer.analyze_crop_risks(crop, stage, weather_data["temperature"], weather_data["humidity"], latest_r.get("soil_moisture", 55.0))

    plan = daily_plan.generate_daily_farming_plan(
        crop=crop,
        growth_stage=stage,
        weather=weather_data,
        latest_reading=latest_r,
        risks=threats
    )

    with st.container(border=True):
        st.markdown("### 🌅 Morning Routine (06:00 - 10:00)")
        for idx, task in enumerate(plan["morning_tasks"], 1):
            st.markdown(f"**{idx}. [{task['time']}] {task['task']}**")
            st.markdown(f"📖 **Agronomic Rationale:** {task['reason']}")
            st.caption(f"🎯 **Expected Outcome:** {task['impact']}")

    with st.container(border=True):
        st.markdown("### ☀️ Afternoon Routine (12:00 - 15:30)")
        for idx, task in enumerate(plan["afternoon_tasks"], 1):
            st.markdown(f"**{idx}. [{task['time']}] {task['task']}**")
            st.markdown(f"📖 **Agronomic Rationale:** {task['reason']}")
            st.caption(f"🎯 **Expected Outcome:** {task['impact']}")

    with st.container(border=True):
        st.markdown("### 🌇 Evening Routine (16:30 - 19:00)")
        for idx, task in enumerate(plan["evening_tasks"], 1):
            st.markdown(f"**{idx}. [{task['time']}] {task['task']}**")
            st.markdown(f"📖 **Agronomic Rationale:** {task['reason']}")
            st.caption(f"🎯 **Expected Outcome:** {task['impact']}")


# ==============================================================================
# VIEW 10: ANALYTICS
# ==============================================================================
elif active_view == "nav_analytics":
    st.markdown(f"## {t('nav_analytics')}")
    st.caption("Chronological telemetry patterns logged for your private farm records.")

    df_hist = database.get_history(farmer_id=farmer_id, limit=100)

    if df_hist.empty:
        st.markdown(f"""
        <div class="clean-empty-state">
            <div class="clean-empty-state-icon">📈</div>
            <div class="clean-empty-state-title">No Telemetry Recorded Yet</div>
            <div class="clean-empty-state-desc">Analytics will dynamically display trends in moisture, temperature, and advisory compliance once readings are saved.</div>
        </div>
        """, unsafe_allow_html=True)
        st.button(f"👉 {t('nav_monitoring')}", on_click=set_page, args=("nav_monitoring",), use_container_width=True)
    else:
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric(t("lbl_total_obs"), len(df_hist))
        with s2:
            st.metric(t("lbl_avg_moisture"), f"{df_hist['Soil Moisture (%)'].mean():.1f}%")
        with s3:
            st.metric(t("lbl_avg_temp"), f"{df_hist['Temperature (°C)'].mean():.1f}°C")
        with s4:
            opt_count = len(df_hist[df_hist['Status'] == 'Optimal'])
            st.metric(t("lbl_optimal_rate"), f"{(opt_count / len(df_hist)) * 100:.0f}%")

        st.markdown("---")
        df_plot = df_hist.sort_values("Timestamp")
        moisture_col = next((c for c in df_plot.columns if "Moisture" in c), "Soil Moisture (%)")
        temp_col = next((c for c in df_plot.columns if "Temperature" in c), "Temperature (°C)")

        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown(f"#### 💧 {t('lbl_soil_moisture')} (%)")
            if len(df_plot) > 1:
                st.line_chart(df_plot.set_index("Timestamp")[moisture_col])
            else:
                st.bar_chart(df_plot.set_index("Timestamp")[moisture_col])
        with ch2:
            st.markdown(f"#### 🌡️ {t('lbl_temperature')} (°C)")
            if len(df_plot) > 1:
                st.line_chart(df_plot.set_index("Timestamp")[temp_col])
            else:
                st.bar_chart(df_plot.set_index("Timestamp")[temp_col])


# ==============================================================================
# VIEW 11: FARM HISTORY & AUDIT
# ==============================================================================
elif active_view == "nav_history":
    st.markdown(f"## {t('nav_history')}")
    st.caption(f"Historical telemetry records strictly belonging to farmer **{farmer['full_name']}** (Phone: {farmer['phone_number']}).")

    df_hist = database.get_history(farmer_id=farmer_id, limit=200)

    if df_hist.empty:
        st.markdown(f"""
        <div class="clean-empty-state">
            <div class="clean-empty-state-icon">📂</div>
            <div class="clean-empty-state-title">No Audit Records Available</div>
            <div class="clean-empty-state-desc">Every time you submit sensor observations in Field Monitoring, a tamper-proof timestamped audit entry is logged here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        csv_data = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 {t('btn_download_csv')}",
            data=csv_data,
            file_name=f"farmer_{farmer_id}_telemetry_log.csv",
            mime="text/csv",
            key="download_csv_btn"
        )
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        with st.expander("📈 Quick Telemetry Trends Preview", expanded=False):
            df_hist_plot = df_hist.sort_values("Timestamp")
            m_col = next((c for c in df_hist_plot.columns if "Moisture" in c), "Soil Moisture (%)")
            t_col = next((c for c in df_hist_plot.columns if "Temperature" in c), "Temperature (°C)")
            hc1, hc2 = st.columns(2)
            with hc1:
                st.caption(f"💧 {t('lbl_soil_moisture')} (%)")
                if len(df_hist_plot) > 1:
                    st.line_chart(df_hist_plot.set_index("Timestamp")[m_col])
                else:
                    st.bar_chart(df_hist_plot.set_index("Timestamp")[m_col])
            with hc2:
                st.caption(f"🌡️ {t('lbl_temperature')} (°C)")
                if len(df_hist_plot) > 1:
                    st.line_chart(df_hist_plot.set_index("Timestamp")[t_col])
                else:
                    st.bar_chart(df_hist_plot.set_index("Timestamp")[t_col])

        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        with st.expander("⚠️ Danger Zone: Clear Historical Records"):
            confirm_clear = st.checkbox("I confirm that I want to delete my farm telemetry records permanently.")
            if st.button("Permanently Clear My Records", disabled=not confirm_clear, key="btn_clear_hist"):
                database.clear_history(farmer_id=farmer_id)
                if "latest_advisory" in st.session_state:
                    del st.session_state["latest_advisory"]
                if "latest_inputs" in st.session_state:
                    del st.session_state["latest_inputs"]
                st.success("Your private telemetry records have been cleared.")
                st.rerun()


# ==============================================================================
# VIEW 12: ASSISTANT (COMMON QUESTIONS & MULTILINGUAL ADVISORY)
# ==============================================================================
elif active_view == "nav_assistant":
    st.markdown(f"## {t('asst_title')}")
    st.markdown(t("asst_desc"))

    # Browser Voice API Notice
    st.info(
        f"🎙️ **{t('asst_voice_info')}:** "
        f"{t('asst_voice_prompt')} {t('asst_voice_listening')}",
        icon="ℹ️"
    )

    components.html("""
    <div style="font-family: sans-serif; background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
            <span style="font-weight: 700; color: #166534; font-size: 0.95rem;">🎙️ Browser Speech-to-Text</span>
            <button id="voiceBtn" onclick="toggleDictation()" style="background: #16a34a; color: white; border: none; padding: 6px 14px; border-radius: 8px; font-weight: 700; cursor: pointer;">🎤 Start Voice Dictation</button>
        </div>
        <p id="speechStatus" style="font-size: 0.82rem; color: #15803d; margin: 6px 0 0 0;">Click to speak your question in your preferred language.</p>
    </div>
    <script>
        let recognizing = false;
        let recognition = null;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-IN';

            recognition.onstart = function() {
                recognizing = true;
                document.getElementById('voiceBtn').innerText = '🛑 Listening...';
                document.getElementById('speechStatus').innerText = 'Listening to your microphone... Speak clearly now.';
            };
            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                document.getElementById('speechStatus').innerText = 'Heard: "' + text + '" (Copy and paste into question box below)';
            };
            recognition.onerror = function(event) {
                document.getElementById('speechStatus').innerText = 'Microphone notice: ' + event.error;
                recognizing = false;
                document.getElementById('voiceBtn').innerText = '🎤 Start Voice Dictation';
            };
            recognition.onend = function() {
                recognizing = false;
                document.getElementById('voiceBtn').innerText = '🎤 Start Voice Dictation';
            };
        } else {
            document.getElementById('voiceBtn').disabled = true;
            document.getElementById('speechStatus').innerText = 'Web Speech API is not supported in this browser. Please type below.';
        }

        function toggleDictation() {
            if (!recognition) return;
            if (recognizing) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }
    </script>
    """, height=95)

    # Unified Question Processor
    def ask_assistant_core(query_text: str, qid: Optional[str] = None):
        """Unified processing pipeline for both Common Questions and typed queries."""
        if not query_text.strip() and not qid:
            st.warning(t("asst_validation_empty"))
            return

        curr_lang = st.session_state.get("language", "en")
        logging.info(f"[ASSISTANT DIAGNOSTIC] Question received: '{query_text}' | QID: {qid} | Language: {curr_lang}")

        # Add User Message to session history
        st.session_state["asst_messages"].append({
            "role": "user",
            "text": query_text,
            "qid": qid,
            "time": datetime.datetime.now().strftime("%H:%M")
        })

        # Generate Answer
        try:
            with st.spinner(t("asst_thinking_spinner")):
                logging.info(f"[ASSISTANT DIAGNOSTIC] Invoking assistant.answer_query for QID={qid}...")
                ans = assistant.answer_query(
                    query=query_text,
                    lang=curr_lang,
                    farm_context=farmer_profile or {},
                    latest_reading=latest_reading,
                    weather_data=weather_data,
                    question_id=qid
                )
                logging.info(f"[ASSISTANT DIAGNOSTIC] Answer returned ({len(ans)} characters)")
                st.session_state["asst_messages"].append({
                    "role": "assistant",
                    "text": ans,
                    "qid": qid,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
        except Exception as ex:
            logging.exception(f"[ASSISTANT EXCEPTION] Error generating response: {ex}")
            err_notice = t("asst_error_general")
            st.session_state["asst_messages"].append({
                "role": "assistant",
                "text": f"⚠️ {err_notice}",
                "qid": qid,
                "time": datetime.datetime.now().strftime("%H:%M")
            })

    # Categorized Common Questions Section
    st.markdown("---")
    st.markdown(f"### 💡 {t('asst_common_questions')}")
    st.caption("Click any preset agricultural question to receive instant tailored agronomic guidance.")

    # 5 Agricultural Categories
    categories = [
        ("asst_cat_irrigation", "💧"),
        ("asst_cat_soil", "🌱"),
        ("asst_cat_crop", "🌾"),
        ("asst_cat_pest", "🛡️"),
        ("asst_cat_daily", "📅")
    ]

    for cat_key, icon in categories:
        cat_qs = [q for q in assistant.COMMON_QUESTIONS if q["category_key"] == cat_key]
        raw_cat_title = t(cat_key)
        cat_title = raw_cat_title if raw_cat_title.startswith(icon) else f"{icon} {raw_cat_title}"
        with st.expander(cat_title, expanded=(cat_key == "asst_cat_irrigation")):
            cols = st.columns(len(cat_qs))
            for idx, q in enumerate(cat_qs):
                with cols[idx]:
                    chip_label = t(q["chip_key"])
                    full_q = t(q["full_key"])
                    if st.button(
                        chip_label,
                        key=f"cq_btn_{q['id']}",
                        type="primary",
                        use_container_width=True,
                        help=full_q
                    ):
                        ask_assistant_core(query_text=full_q, qid=q["id"])
                        st.rerun()

    # Input Form for Typed Questions
    st.markdown("---")
    with st.form("assistant_query_form", clear_on_submit=True):
        st.markdown(f"**💬 {t('asst_input_label')}**")
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            typed_query = st.text_input(
                "query",
                label_visibility="collapsed",
                placeholder=t("asst_input_placeholder"),
                help=t("asst_input_help"),
                key="asst_typed_query"
            )
        with col_btn:
            submit_btn = st.form_submit_button(t("asst_send_btn"), use_container_width=True)

        if submit_btn and typed_query.strip():
            ask_assistant_core(query_text=typed_query.strip(), qid=None)
            st.rerun()

    # Conversation History Display
    st.markdown("---")
    ch_col1, ch_col2 = st.columns([4, 1])
    with ch_col1:
        st.markdown(f"### 💬 {t('asst_chat_history')}")
    with ch_col2:
        if st.session_state["asst_messages"]:
            if st.button(f"🗑️ {t('asst_clear_btn')}", key="clear_chat_history_btn", use_container_width=True):
                st.session_state["asst_messages"] = []
                st.rerun()

    if not st.session_state["asst_messages"]:
        st.info(f"💡 {t('asst_empty_chat')}")
    else:
        for msg in reversed(st.session_state["asst_messages"]):
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background: #e2e8f0; border-radius: 12px; padding: 10px 14px; margin: 8px 0; max-width: 85%; margin-left: auto; color: #0f172a; border-left: 4px solid #16a34a; box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 700;">👨‍🌾 {farmer['full_name']} • {msg['time']}</div>
                    <div style="font-size: 0.95rem; font-weight: 600; margin-top: 4px; color: #0f172a !important;">{msg['text']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.container(border=True):
                    st.markdown(f"<div style='font-weight: 800; color: #1b4332; font-size: 0.95rem; margin-bottom: 4px;'>🤖 {t('asst_title')} <span style='font-size: 0.75rem; color: #475569; font-weight: 600;'>({msg['time']})</span></div>", unsafe_allow_html=True)
                    st.markdown(msg["text"])


# ==============================================================================
# VIEW 13: SETTINGS / LANGUAGE
# ==============================================================================
elif active_view == "nav_settings":
    st.markdown(f"## {t('settings_title')}")
    st.markdown(t("settings_desc"))

    with st.container(border=True):
        st.markdown("### 🌐 Interface Language Configuration")
        st.caption("Select your preferred language. All navigation items, buttons, and form labels will update immediately.")

        lang_codes = list(translations.SUPPORTED_LANGUAGES.keys())
        active_code = st.session_state.get("language", "en")

        new_lang = st.selectbox(
            "Interface Language / भाषा चयन",
            options=lang_codes,
            format_func=lambda code: f"{translations.SUPPORTED_LANGUAGES[code]} — {translations.TRANSLATION_STATUS[code]}",
            index=lang_codes.index(active_code) if active_code in lang_codes else 0,
            help="Choose your preferred language from the 14 supported Indian languages.",
            key="settings_lang_select"
        )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button(t("settings_save_btn"), use_container_width=True, key="save_lang_btn"):
            st.session_state["language"] = new_lang
            database.update_farmer_language(farmer_id, new_lang)
            st.success(t("settings_saved"))
            st.rerun()

    # Translation Coverage Report Expander
    with st.expander("📊 Translation Coverage Report", expanded=False):
        cov_report = translations.get_translation_coverage_report()
        st.markdown(f"**Total Registered UI String Keys:** `{cov_report['total_keys']}`")
        st.markdown(f"**Total Supported Languages:** `{cov_report['total_languages']}` | **Complete Coverage:** `{len(cov_report['complete_languages'])}`")
        df_cov = pd.DataFrame(cov_report["details"])
        st.dataframe(df_cov, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.markdown("### 👤 Farmer Account Overview")
        st.markdown(f"- **Full Name:** `{farmer['full_name']}`")
        st.markdown(f"- **Mobile Number:** `{farmer['phone_number']}`")
        st.markdown(f"- **Farmer ID:** `{farmer['id']}` (Private multi-tenant partition)")
        st.markdown(f"- **Active Language:** `{translations.SUPPORTED_LANGUAGES.get(st.session_state.get('language', 'en'))}`")
        st.markdown(f"- **Database Engine:** `SQLite (smart_agri.db)` — Isolated Audit History")

        st.markdown("---")
        if st.button("🚪 Log Out of My Account", key="settings_logout_btn", on_click=logout):
            logout()
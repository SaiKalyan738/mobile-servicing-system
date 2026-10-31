import os
import html as _html

import requests
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

STATUSES = [
    "Received",
    "Diagnosis",
    "Repair in Progress",
    "Ready for Collection",
    "Collected",
]

# Presentation-only styles: icon, text colour, badge background
STATUS_STYLES = {
    "Received": ("📥", "#93c5fd", "#14305a"),
    "Diagnosis": ("🔍", "#c4b5fd", "#2e2457"),
    "Repair in Progress": ("🛠️", "#fcd34d", "#4a3410"),
    "Ready for Collection": ("✅", "#6ee7b7", "#0f3d30"),
    "Collected": ("📦", "#cbd5e1", "#263244"),
}
DEFAULT_STYLE = ("•", "#cbd5e1", "#263244")

NAV_ICONS = {
    "Dashboard": "📊",
    "Track Repair": "🔎",
    "New Request": "➕",
    "Update Status": "🔄",
}

PAGES = list(NAV_ICONS)

PAGE_META = {
    "Dashboard": (
        "SERVICE OPERATIONS",
        "MobileCare Portal",
        "One place to manage repairs, track progress, and keep every service request moving.",
    ),
    "Track Repair": (
        "LIVE TRACKING",
        "Track your repair",
        "Follow your device from drop-off to collection with a clear, step-by-step view.",
    ),
    "New Request": (
        "INTAKE DESK",
        "Register a new repair",
        "Capture the case, the device and the fault in under a minute.",
    ),
    "Update Status": (
        "WORKSHOP CONTROL",
        "Update repair progress",
        "Move a request through the pipeline and keep every customer informed.",
    ),
}

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="MobileCare | Service Portal",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "### MobileCare\nRepair management and tracking portal.",
    },
)

# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --primary: #60a5fa;
        --accent: #22d3ee;
        --background: #0b1120;
        --card: #151f32;
        --border: #293750;
        --muted: #9aaac2;
    }

    /* ---------- App background ---------- */
    .stApp {
        background:
            radial-gradient(900px 520px at 6% -6%, rgba(59, 130, 246, .26), transparent 62%),
            radial-gradient(800px 520px at 102% 8%, rgba(6, 182, 212, .20), transparent 60%),
            radial-gradient(700px 500px at 50% 110%, rgba(99, 102, 241, .16), transparent 60%),
            linear-gradient(135deg, rgba(7, 13, 27, .95), rgba(10, 22, 42, .93)),
            url('https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=2200&q=85');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
        color: #eaf2ff;
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }

    ::selection { background: rgba(96, 165, 250, .35); }
    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: #0b1220; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(#3b82f6, #06b6d4);
        border-radius: 20px;
    }

    [data-testid="stHeader"] { background: transparent; }
    footer { visibility: hidden; }

    /* ---------- Text colours (safe on any base theme) ---------- */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li { color: #dbe7f7; }
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #f1f5f9;
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        letter-spacing: -.4px;
    }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: #cfe0f5 !important;
        font-weight: 600;
    }
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p { color: #9aaac2 !important; }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(13, 25, 44, .97), rgba(8, 16, 30, .985)),
            url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=70');
        background-size: cover;
        background-position: center;
        border-right: 1px solid rgba(96, 165, 250, .22);
        box-shadow: 8px 0 35px rgba(0, 0, 0, .22);
    }
    [data-testid="stSidebar"] * { color: #e5edf9; }

    .side-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 2px 2px;
    }
    .side-logo {
        width: 46px; height: 46px;
        border-radius: 14px;
        display: grid; place-items: center;
        font-size: 24px;
        background: linear-gradient(135deg, #2563eb, #06b6d4);
        box-shadow: 0 8px 22px rgba(37, 99, 235, .4);
    }
    .side-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -.6px;
        background: linear-gradient(90deg, #ffffff, #7dd3fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
    }
    .side-sub {
        font-size: 10px;
        letter-spacing: 1.8px;
        font-weight: 700;
        color: #7dd3fc;
        -webkit-text-fill-color: #7dd3fc;
        margin-top: 3px;
    }

    [data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 11px 14px;
        border-radius: 12px;
        border: 1px solid transparent;
        cursor: pointer;
        transition: background .2s ease, transform .2s ease, border-color .2s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display: none; }
    [data-testid="stSidebar"] [role="radiogroup"] label p { font-weight: 600; font-size: 15px; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(96, 165, 250, .13);
        border-color: rgba(96, 165, 250, .3);
        transform: translateX(4px);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(110deg, rgba(37, 99, 235, .55), rgba(8, 145, 178, .4));
        border-color: rgba(125, 211, 252, .55);
        box-shadow: 0 8px 20px rgba(37, 99, 235, .25);
    }

    /* ---------- Top bar ---------- */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 12px 18px;
        margin-bottom: 16px;
        border-radius: 16px;
        background: rgba(15, 27, 46, .72);
        border: 1px solid rgba(125, 160, 199, .22);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 10px 28px rgba(0, 0, 0, .18);
        animation: fade-up .5s ease both;
    }
    .tb-brand {
        display: flex; align-items: center; gap: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700; font-size: 18px; letter-spacing: -.4px; color: #fff;
    }
    .tb-logo {
        width: 34px; height: 34px; border-radius: 10px;
        display: grid; place-items: center; font-size: 18px;
        background: linear-gradient(135deg, #2563eb, #06b6d4);
    }
    .tb-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
    .tb-crumb {
        padding: 6px 12px; border-radius: 999px; font-size: 12px; font-weight: 700;
        color: #bfdbfe; background: rgba(59, 130, 246, .14);
        border: 1px solid rgba(96, 165, 250, .3);
    }
    .tb-live {
        padding: 6px 12px; border-radius: 999px; font-size: 12px; font-weight: 700;
        border: 1px solid; white-space: nowrap;
    }
    .tb-live.ok   { color: #6ee7b7; background: rgba(16, 185, 129, .12); border-color: rgba(52, 211, 153, .35); }
    .tb-live.warn { color: #fcd34d; background: rgba(245, 158, 11, .12); border-color: rgba(251, 191, 36, .35); }
    .tb-live.off  { color: #fca5a5; background: rgba(239, 68, 68, .12); border-color: rgba(248, 113, 113, .35); }
    .tb-live.ok::first-letter { animation: blink 1.8s ease-in-out infinite; }

    /* ---------- Hero ---------- */
    .hero {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(105deg, rgba(8, 20, 40, .96) 0%, rgba(16, 54, 91, .88) 55%, rgba(8, 145, 178, .72) 100%),
            url('https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1800&q=85');
        background-size: cover;
        background-position: center 43%;
        border: 1px solid rgba(125, 211, 252, .38);
        border-radius: 26px;
        padding: clamp(28px, 4vw, 48px);
        margin: 4px 0 30px 0;
        box-shadow: 0 22px 55px rgba(0, 0, 0, .3), inset 0 1px rgba(255,255,255,.08);
        animation: fade-up .65s ease both;
    }
    .hero:before {
        content: "";
        position: absolute; inset: 0;
        background: linear-gradient(115deg, transparent 35%, rgba(255,255,255,.07) 50%, transparent 65%);
        transform: translateX(-100%);
        animation: sheen 6s ease-in-out infinite;
        pointer-events: none;
    }
    .hero .eyebrow, .hero h1, .stApp .hero p, .hero .chips { position: relative; z-index: 1; }
    .hero h1 {
        color: #ffffff;
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-size: clamp(27px, 4vw, 42px);
        font-weight: 700;
        margin: 5px 0 10px 0;
        letter-spacing: -1.4px;
        text-shadow: 0 4px 24px rgba(0, 0, 0, .18);
    }
    .stApp .hero p {
        color: #d9eafe;
        font-size: 15px;
        line-height: 1.8;
        max-width: 650px;
        margin-bottom: 0;
    }
    .eyebrow {
        color: #93c5fd;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 11px;
        font-weight: 800;
    }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
    .chip {
        padding: 7px 13px; border-radius: 999px; font-size: 12px; font-weight: 600;
        color: #e0f2fe; background: rgba(255, 255, 255, .09);
        border: 1px solid rgba(255, 255, 255, .2);
        backdrop-filter: blur(6px);
        transition: transform .2s ease, background .2s ease;
    }
    .chip:hover { transform: translateY(-2px); background: rgba(255, 255, 255, .17); }

    @keyframes fade-up {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes sheen { 0%, 55% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
    @keyframes float { 0%, 100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-12px) rotate(6deg); } }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: .3; } }
    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(34, 211, 238, .55); }
        70%  { box-shadow: 0 0 0 12px rgba(34, 211, 238, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0); }
    }

    .section-label {
        color: #f1f5f9;
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-size: 22px;
        font-weight: 700;
        margin: 18px 0 16px 0;
        display: flex; align-items: center; gap: 12px;
    }
    .section-label:before {
        content: "";
        width: 5px; height: 22px; border-radius: 4px;
        background: linear-gradient(180deg, #60a5fa, #22d3ee);
    }

    /* ---------- Cards ---------- */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(var(--min, 160px), 1fr));
        gap: 14px;
        margin-bottom: 8px;
    }
    .info-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(145deg, rgba(25, 43, 67, .94), rgba(13, 25, 43, .96));
        border: 1px solid rgba(125, 160, 199, .22);
        border-radius: 18px;
        padding: 20px 20px 18px 22px;
        min-height: 116px;
        box-shadow: 0 8px 22px rgba(0, 0, 0, .14);
        transition: transform 220ms ease, border-color 220ms ease,
                    box-shadow 220ms ease, background 220ms ease;
        animation: fade-up .55s ease both;
    }
    .info-card:before {
        content: "";
        position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
        background: var(--accent, #60a5fa);
        opacity: .9;
    }
    .info-card:after {
        content: "";
        position: absolute;
        width: 110px; height: 110px;
        right: -42px; bottom: -54px;
        border-radius: 50%;
        background: var(--accent, #60a5fa);
        opacity: .10;
        transition: transform 250ms ease, opacity 250ms ease;
    }
    .info-card:hover {
        transform: translateY(-6px);
        border-color: var(--accent, #60a5fa);
        background: linear-gradient(145deg, rgba(30, 54, 84, .98), rgba(15, 31, 53, .98));
        box-shadow: 0 18px 34px rgba(0, 0, 0, .3);
    }
    .info-card:hover:after { transform: scale(1.6); opacity: .16; }
    .card-icon {
        position: absolute; right: 16px; top: 14px;
        width: 36px; height: 36px; border-radius: 11px;
        display: grid; place-items: center; font-size: 18px;
        background: rgba(255, 255, 255, .07);
        border: 1px solid rgba(255, 255, 255, .1);
        transition: transform .25s ease;
    }
    .info-card:hover .card-icon { transform: rotate(-8deg) scale(1.12); }
    .card-label {
        color: #a8b8ce;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: .6px;
        margin-bottom: 12px;
        padding-right: 44px;
    }
    .card-value {
        color: #f8fafc;
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-size: 30px;
        font-weight: 700;
        overflow-wrap: anywhere;
        position: relative; z-index: 1;
    }
    .card-bar {
        margin-top: 14px; height: 5px; border-radius: 5px;
        background: rgba(255, 255, 255, .08); overflow: hidden;
        position: relative; z-index: 1;
    }
    .card-bar span {
        display: block; height: 100%; border-radius: 5px;
        background: var(--accent, #60a5fa);
        transition: width .6s ease;
    }
    .small-note { color: #9aaac2; font-size: 12px; }

    /* ---------- Status badge, details, tracker ---------- */
    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: 999px;
        font-size: 12px; font-weight: 700; border: 1px solid;
        white-space: nowrap;
    }
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px; margin: 10px 0 6px;
    }
    .detail {
        background: linear-gradient(145deg, rgba(25, 43, 67, .85), rgba(13, 25, 43, .9));
        border: 1px solid rgba(125, 160, 199, .22);
        border-radius: 14px;
        padding: 14px 16px;
        transition: transform .2s ease, border-color .2s ease;
    }
    .detail:hover { transform: translateY(-3px); border-color: rgba(96, 165, 250, .7); }
    .detail .k {
        font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
        color: #8fa3bf; font-weight: 700;
    }
    .detail .v { font-size: 15px; font-weight: 600; color: #f1f5f9; margin-top: 7px; overflow-wrap: anywhere; }

    .tracker {
        background: rgba(17, 31, 51, .66);
        border: 1px solid rgba(125, 160, 199, .2);
        border-radius: 18px;
        padding: 20px 16px 8px;
        margin: 14px 0 8px;
    }
    .tracker-title {
        font-size: 12px; letter-spacing: 1.5px; font-weight: 800;
        color: #7dd3fc; margin: 0 0 18px 6px;
    }
    .stepper { display: flex; }
    .step { flex: 1; position: relative; text-align: center; padding: 0 6px 14px; }
    .step .dot {
        width: 36px; height: 36px; margin: 0 auto 10px;
        border-radius: 50%; display: grid; place-items: center;
        font-size: 15px; font-weight: 800;
        background: #142238; border: 2px solid #33476a; color: #7f93b0;
        position: relative; z-index: 1;
        transition: transform .2s ease;
    }
    .step:hover .dot { transform: scale(1.12); }
    .step:not(:last-child):after {
        content: ""; position: absolute;
        top: 17px; left: calc(50% + 22px); width: calc(100% - 44px);
        height: 3px; border-radius: 3px; background: #2a3b58;
    }
    .step.done .dot {
        background: linear-gradient(135deg, #2563eb, #06b6d4);
        border-color: #7dd3fc; color: #fff;
    }
    .step.done:not(:last-child):after { background: linear-gradient(90deg, #3b82f6, #22d3ee); }
    .step.current .dot {
        background: linear-gradient(135deg, #0ea5e9, #22d3ee);
        border-color: #cffafe; color: #04121f;
        animation: pulse 1.8s infinite;
    }
    .step-label { font-size: 12px; font-weight: 600; color: #8fa3bf; line-height: 1.3; }
    .step.done .step-label, .step.current .step-label { color: #e6f0ff; }

    /* ---------- Buttons ---------- */
    div.stButton > button,
    div.stFormSubmitButton > button,
    [data-testid="stFormSubmitButton"] > button {
        position: relative;
        overflow: hidden;
        background: linear-gradient(115deg, #2563eb 0%, #087ea4 100%);
        color: #fff;
        border: 1px solid rgba(125, 211, 252, .55);
        border-radius: 12px;
        font-weight: 750;
        letter-spacing: .2px;
        min-height: 46px;
        padding: 0 22px;
        box-shadow: 0 7px 18px rgba(37, 99, 235, .25);
        transition: transform 180ms ease, filter 180ms ease, box-shadow 180ms ease;
    }
    div.stButton > button:before,
    div.stFormSubmitButton > button:before,
    [data-testid="stFormSubmitButton"] > button:before {
        content: "";
        position: absolute; top: 0; left: -80%;
        width: 60%; height: 100%;
        background: linear-gradient(100deg, transparent, rgba(255,255,255,.35), transparent);
        transform: skewX(-20deg);
        transition: left .6s ease;
    }
    div.stButton > button:hover:before,
    div.stFormSubmitButton > button:hover:before,
    [data-testid="stFormSubmitButton"] > button:hover:before { left: 130%; }
    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        color: #fff;
        filter: brightness(1.12);
        transform: translateY(-3px);
        border-color: #bae6fd;
        box-shadow: 0 14px 28px rgba(14, 165, 233, .35);
    }
    div.stButton > button:active,
    div.stFormSubmitButton > button:active,
    [data-testid="stFormSubmitButton"] > button:active { transform: translateY(0) scale(.98); }
    div.stButton > button p,
    div.stFormSubmitButton > button p,
    [data-testid="stFormSubmitButton"] > button p { color: #fff; position: relative; z-index: 1; }

    /* ---------- Inputs, tables, forms ---------- */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        background: rgba(17, 28, 46, .92);
        border-color: #344761;
        border-radius: 12px;
        transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
    }
    div[data-baseweb="input"] > div:hover,
    div[data-baseweb="textarea"] > div:hover,
    div[data-baseweb="select"] > div:hover { border-color: #5b84bf; }
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #60a5fa;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, .22);
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] * { color: #eaf2ff; -webkit-text-fill-color: #eaf2ff; }
    ::placeholder { color: #7f93b0 !important; -webkit-text-fill-color: #7f93b0 !important; opacity: 1; }

    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"] { background: #111c2e !important; }
    div[data-baseweb="popover"] li { color: #eaf2ff; }
    div[data-baseweb="popover"] li:hover { background: rgba(96, 165, 250, .18) !important; }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(125, 160, 199, .22);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0, 0, 0, .18);
    }
    div[data-testid="stForm"] {
        background: rgba(17, 31, 51, .62);
        border: 1px solid rgba(125, 160, 199, .2);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, .16);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: border-color .25s ease, box-shadow .25s ease;
    }
    div[data-testid="stForm"]:hover {
        border-color: rgba(96, 165, 250, .45);
        box-shadow: 0 16px 36px rgba(0, 0, 0, .24);
    }
    div[data-testid="stAlert"] { border-radius: 12px; border: 1px solid rgba(125, 160, 199, .2); }
    [data-testid="stCode"] pre, div[data-testid="stCode"] {
        border-radius: 12px;
        border: 1px solid rgba(125, 160, 199, .22);
    }
    [data-testid="stMetric"] {
        background: #151f32; border: 1px solid #293750;
        border-radius: 15px; padding: 15px;
    }
    [data-testid="stMetricLabel"] { color: #b8c7dc; }
    [data-testid="stMetricValue"] { color: #f8fafc; }
    hr { border-color: #293750; }

    /* ---------- Footer ---------- */
    .footer-panel {
        margin-top: 34px;
        border: 1px solid rgba(96, 165, 250, .22);
        border-radius: 22px;
        background:
            linear-gradient(110deg, rgba(14, 26, 44, .95), rgba(11, 38, 58, .9)),
            url('https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=70');
        background-size: cover;
        box-shadow: 0 10px 28px rgba(0,0,0,.18);
        overflow: hidden;
    }
    .footer-top {
        display: grid;
        grid-template-columns: 1.6fr 1fr 1fr;
        gap: 26px;
        padding: 28px 30px;
    }
    .footer-brand {
        color: #eaf4ff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 19px; font-weight: 700; letter-spacing: -.4px;
    }
    .footer-copy { color: #9eb2cc; font-size: 13px; line-height: 1.75; margin-top: 8px; }
    .footer-h { color: #7dd3fc; font-size: 11px; font-weight: 800; letter-spacing: 1.6px; margin-bottom: 12px; }
    .footer-link {
        display: block; color: #c9d8ee; font-size: 13px; padding: 4px 0;
        transition: color .2s ease, transform .2s ease;
    }
    .footer-link:hover { color: #67e8f9; transform: translateX(5px); }
    .footer-pill {
        display: inline-block;
        border: 1px solid rgba(103, 232, 249, .25);
        border-radius: 999px;
        color: #a5f3fc;
        background: rgba(8, 145, 178, .12);
        padding: 7px 12px;
        font-size: 11px; font-weight: 700; letter-spacing: .4px;
        margin-top: 14px;
    }
    .footer-bottom {
        display: flex; flex-wrap: wrap; gap: 8px;
        justify-content: space-between; align-items: center;
        padding: 14px 30px;
        border-top: 1px solid rgba(125, 160, 199, .18);
        background: rgba(5, 12, 24, .35);
        color: #8fa3bf; font-size: 12px;
    }

    /* ---------- Tablet / mobile ---------- */
    @media (min-width: 769px) {
        .main .block-container { padding-left: 2.5rem; padding-right: 2.5rem; }
        .hero { min-height: 220px; display: flex; flex-direction: column; justify-content: center; }
    }

    @media (max-width: 900px) {
        .footer-top { grid-template-columns: 1fr 1fr; }
        .footer-top > div:first-child { grid-column: 1 / -1; }
    }

    @media (max-width: 768px) {
        .stApp { background-attachment: scroll; }
        .main .block-container { padding: .8rem .85rem 1.5rem .85rem; width: 100%; }
        .topbar { padding: 10px 12px; border-radius: 14px; }
        .tb-brand { font-size: 16px; }
        .tb-crumb { display: none; }
        .hero { border-radius: 19px; padding: 25px 20px; margin-bottom: 20px; }
        .hero h1 { font-size: clamp(25px, 7vw, 34px); line-height: 1.15; }
        .stApp .hero p { font-size: 14px; max-width: 100%; }
        .eyebrow { font-size: 10px; letter-spacing: 1.5px; }
        .chip { font-size: 11px; padding: 6px 11px; }
        .section-label { font-size: 19px; margin: 12px 0 13px; }
        .card-grid { gap: 10px; }
        .info-card { padding: 15px 14px 14px 17px; min-height: 96px; border-radius: 15px; }
        .card-icon { width: 30px; height: 30px; font-size: 15px; right: 10px; top: 10px; }
        .card-label { font-size: 10px; margin-bottom: 9px; padding-right: 34px; }
        .card-value { font-size: clamp(22px, 6vw, 26px); }
        div[data-testid="stForm"] { padding: 15px; border-radius: 15px; }
        div.stButton > button, div.stFormSubmitButton > button,
        [data-testid="stFormSubmitButton"] > button {
            min-height: 48px; width: 100%; white-space: normal;
        }
        div[data-testid="stDataFrame"] { overflow-x: auto; }

        /* vertical tracker */
        .stepper { flex-direction: column; }
        .step { display: flex; align-items: center; gap: 14px; text-align: left; padding: 0 0 18px; }
        .step .dot { margin: 0; flex: 0 0 36px; }
        .step:not(:last-child):after { top: 36px; left: 17px; width: 3px; height: calc(100% - 36px); }
        .step-label { font-size: 14px; }

        .footer-panel { border-radius: 16px; }
        .footer-top { grid-template-columns: 1fr; padding: 22px 18px; gap: 20px; }
        .footer-bottom { padding: 12px 18px; flex-direction: column; align-items: flex-start; }
    }

    @media (max-width: 480px) {
        .main .block-container { padding-left: .65rem; padding-right: .65rem; }
        .hero { padding: 22px 16px; }
        div[data-testid="stDataFrame"] [role="grid"] { min-width: 620px; }
    }

    /* =====================================================
       V2 POLISH LAYER (CSS only)
       ===================================================== */

    /* ---- Living background: slowly drifting colour mesh ---- */
    .stApp {
        background-size: 140% 140%, 140% 140%, 140% 140%, cover, cover;
        background-repeat: no-repeat;
        animation: mesh 26s ease-in-out infinite alternate;
    }
    @keyframes mesh {
        0%   { background-position: 0% 0%, 100% 0%, 50% 100%, center, center; }
        100% { background-position: 100% 90%, 0% 60%, 20% 0%, center, center; }
    }
    @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
    @keyframes flow { from { background-position: 0% 0; } to { background-position: 200% 0; } }
    @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
    .main .block-container { animation: fade-in .6s ease both; }

    hr {
        border: 0 !important;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(125, 211, 252, .4), transparent);
    }

    /* ---- Accessibility: visible keyboard focus ---- */
    button:focus-visible, input:focus-visible, textarea:focus-visible,
    [role="radio"]:focus-visible, label:focus-visible {
        outline: 2px solid #67e8f9 !important;
        outline-offset: 2px;
    }
    input:-webkit-autofill {
        -webkit-box-shadow: 0 0 0 1000px #111c2e inset !important;
        -webkit-text-fill-color: #eaf2ff !important;
    }

    /* ---- Top bar ---- */
    .topbar {
        position: relative;
        box-shadow: inset 0 1px rgba(255, 255, 255, .08), 0 12px 30px rgba(0, 0, 0, .2);
    }
    .topbar:after {
        content: "";
        position: absolute; left: 22px; right: 22px; bottom: -1px; height: 1px;
        background: linear-gradient(90deg, transparent, #22d3ee, #60a5fa, transparent);
    }
    .tb-logo { box-shadow: 0 6px 16px rgba(37, 99, 235, .45); transition: transform .3s ease; }
    .tb-brand:hover .tb-logo { transform: rotate(-10deg) scale(1.1); }

    /* ---- Hero: dot grid + gradient headline + glow ---- */
    .hero {
        background-image:
            radial-gradient(rgba(255, 255, 255, .10) 1px, transparent 1.3px),
            linear-gradient(105deg, rgba(8, 20, 40, .96) 0%, rgba(16, 54, 91, .88) 55%, rgba(8, 145, 178, .72) 100%),
            url('https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1800&q=85');
        background-size: 24px 24px, auto, cover;
        background-position: 0 0, center, center 43%;
        background-repeat: repeat, no-repeat, no-repeat;
        box-shadow: 0 22px 55px rgba(0, 0, 0, .32), 0 0 70px -12px rgba(34, 211, 238, .28),
                    inset 0 1px rgba(255, 255, 255, .1);
    }
    .hero h1 {
        width: fit-content;
        max-width: 100%;
        background: linear-gradient(90deg, #ffffff 0%, #bae6fd 55%, #67e8f9 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
    }
    .chip { cursor: default; }
    .chip:hover { box-shadow: 0 8px 20px rgba(14, 165, 233, .3); border-color: rgba(186, 230, 253, .6); }

    /* ---- Section headings ---- */
    .section-label:after {
        content: "";
        flex: 1; height: 1px;
        background: linear-gradient(90deg, rgba(125, 160, 199, .4), transparent);
    }

    /* ---- Cards: glass, accent glow, animated meters ---- */
    .info-card {
        background:
            linear-gradient(180deg, rgba(255, 255, 255, .06), rgba(255, 255, 255, 0) 45%),
            linear-gradient(145deg, rgba(25, 43, 67, .9), rgba(13, 25, 43, .94));
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        box-shadow: inset 0 1px rgba(255, 255, 255, .07), 0 10px 24px rgba(0, 0, 0, .18);
    }
    .info-card:hover {
        background:
            linear-gradient(180deg, rgba(255, 255, 255, .09), rgba(255, 255, 255, 0) 50%),
            linear-gradient(145deg, rgba(30, 54, 84, .98), rgba(15, 31, 53, .98));
        box-shadow: 0 24px 44px -12px color-mix(in srgb, var(--accent, #60a5fa) 55%, transparent),
                    0 0 0 1px color-mix(in srgb, var(--accent, #60a5fa) 55%, transparent);
    }
    .card-icon {
        background: color-mix(in srgb, var(--accent, #60a5fa) 18%, transparent);
        border-color: color-mix(in srgb, var(--accent, #60a5fa) 45%, transparent);
    }
    .card-value { text-shadow: 0 0 28px color-mix(in srgb, var(--accent, #60a5fa) 40%, transparent); }
    .card-bar { height: 6px; }
    .card-bar span {
        background: linear-gradient(90deg, var(--accent, #60a5fa),
                    color-mix(in srgb, var(--accent, #60a5fa) 45%, white));
        box-shadow: 0 0 12px color-mix(in srgb, var(--accent, #60a5fa) 70%, transparent);
        transform-origin: left center;
        animation: grow 1s cubic-bezier(.2, .8, .2, 1) both;
    }

    /* ---- Status badge, detail cards, tracker ---- */
    .badge { box-shadow: 0 0 16px -4px currentColor; }
    .detail { position: relative; overflow: hidden; cursor: default; }
    .detail:before {
        content: "";
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #3b82f6, #22d3ee);
        opacity: .65; transition: opacity .2s ease;
    }
    .detail:hover { box-shadow: 0 14px 28px rgba(0, 0, 0, .28), 0 0 24px -8px rgba(34, 211, 238, .5); }
    .detail:hover:before { opacity: 1; }

    .tracker {
        background: linear-gradient(180deg, rgba(34, 211, 238, .06), rgba(17, 31, 51, .66) 40%);
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        box-shadow: inset 0 1px rgba(255, 255, 255, .06), 0 12px 30px rgba(0, 0, 0, .18);
    }
    .step:not(.done):not(.current) .dot { border-style: dashed; }
    .step.done .dot { box-shadow: 0 0 0 4px rgba(34, 211, 238, .12), 0 6px 16px rgba(37, 99, 235, .4); }
    .step.done:not(:last-child):after {
        background: linear-gradient(90deg, #3b82f6, #22d3ee, #3b82f6);
        background-size: 200% 100%;
        animation: flow 3s linear infinite;
    }

    /* ---- Sidebar polish ---- */
    [data-testid="stSidebar"] [role="radiogroup"] label { position: relative; }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked):before {
        content: "";
        position: absolute; left: -1px; top: 22%; bottom: 22%; width: 4px;
        border-radius: 4px;
        background: #22d3ee;
        box-shadow: 0 0 12px #22d3ee;
    }
    .side-logo { transition: transform .3s ease; }
    .side-brand:hover .side-logo { transform: rotate(-8deg) scale(1.08); }

    /* ---- Buttons: animated primary + ghost secondary ---- */
    div.stFormSubmitButton > button,
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(110deg, #2563eb, #06b6d4, #6366f1, #2563eb);
        background-size: 300% 100%;
        animation: flow 9s linear infinite;
        border-radius: 14px;
        letter-spacing: .5px;
        box-shadow: inset 0 1px rgba(255, 255, 255, .25), 0 10px 24px rgba(37, 99, 235, .35);
    }
    div.stButton > button[data-testid="stBaseButton-secondary"] {
        background: rgba(96, 165, 250, .10);
        border: 1px solid rgba(125, 211, 252, .5);
        box-shadow: none;
        border-radius: 14px;
        -webkit-backdrop-filter: blur(8px);
        backdrop-filter: blur(8px);
    }
    div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: linear-gradient(115deg, #2563eb, #087ea4);
        box-shadow: 0 14px 28px rgba(14, 165, 233, .35);
    }

    /* ---- Inputs ---- */
    [data-testid="stWidgetLabel"] p {
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #9fc3ee !important;
    }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { min-height: 48px; }
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { font-size: 15px; }

    /* ---- Alerts: coloured accent edge ---- */
    div[data-testid="stAlert"] [data-baseweb="notification"],
    div[data-testid="stAlert"] > div {
        border-radius: 14px;
        border-left: 4px solid #60a5fa;
        -webkit-backdrop-filter: blur(8px);
        backdrop-filter: blur(8px);
    }
    div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-baseweb="notification"] { border-left-color: #34d399; }
    div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-baseweb="notification"] { border-left-color: #fbbf24; }
    div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-baseweb="notification"] { border-left-color: #f87171; }

    div[data-testid="stDataFrame"] { transition: box-shadow .25s ease, border-color .25s ease; }
    div[data-testid="stDataFrame"]:hover {
        border-color: rgba(96, 165, 250, .5);
        box-shadow: 0 16px 36px rgba(0, 0, 0, .28), 0 0 30px -10px rgba(34, 211, 238, .4);
    }

    /* ---- Footer ---- */
    .footer-panel { position: relative; }
    .footer-panel:before {
        content: "";
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #3b82f6, #22d3ee, #6366f1, #3b82f6);
        background-size: 200% 100%;
        animation: flow 6s linear infinite;
    }
    .footer-pill { animation: pulse 2.4s infinite; }
    .footer-link { cursor: default; }

    /* ---- Scroll reveal (progressive enhancement, Chromium) ---- */
    @supports (animation-timeline: view()) {
        .info-card, .detail, .tracker, .footer-panel {
            animation: fade-up linear both !important;
            animation-delay: 0ms !important;
            animation-timeline: view();
            animation-range: entry 0% entry 55%;
        }
    }

    /* ---- Mobile refinements ---- */
    @media (max-width: 768px) {
        .stApp { animation: none; }
        .info-card, .tracker, .topbar { -webkit-backdrop-filter: none; backdrop-filter: none; }
        .chips { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; padding-bottom: 2px; }
        .chips::-webkit-scrollbar { display: none; }
        .chip { white-space: nowrap; flex: 0 0 auto; }
        .section-label:after { display: none; }
        .step.done:not(:last-child):after {
            background: linear-gradient(180deg, #3b82f6, #22d3ee);
            animation: none;
        }
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { min-height: 50px; }
    }

    /* =====================================================
       V3: toolbar clean-up, sign-in, hero art, footer nav
       ===================================================== */

    /* Hide Deploy, Print and the "Made with Streamlit vX" row */
    [data-testid="stAppDeployButton"],
    .stAppDeployButton { display: none !important; }
    [data-testid="stMainMenuItem-print"] { display: none !important; }
    [data-testid="stMainMenuList"] ~ * { display: none !important; }
    .stMenuVersionCopyButton { display: none !important; }

    [data-testid="stCode"] pre { background: #0d1627 !important; }
    [data-testid="stCode"] code, [data-testid="stCode"] code span { color: #e5edf9 !important; }

    /* Hide the "Press Enter to submit" hint (Enter still submits the form) */
    [data-testid="InputInstructions"] { display: none !important; }

    /* Sidebar: quick track + live snapshot */
    .side-h {
        font-size: 11px; font-weight: 800; letter-spacing: 1.6px;
        color: #7dd3fc; margin: 4px 0 10px;
    }
    [data-testid="stSidebar"] [data-testid="stForm"] {
        padding: 0; border: 0; background: transparent; box-shadow: none;
        -webkit-backdrop-filter: none; backdrop-filter: none;
    }
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button,
    [data-testid="stSidebar"] div.stFormSubmitButton > button { width: 100%; min-height: 44px; }
    .snap { display: grid; gap: 8px; }
    .snap-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 10px 12px; border-radius: 12px;
        background: rgba(255, 255, 255, .05);
        border: 1px solid rgba(125, 160, 199, .18);
        transition: transform .2s ease, border-color .2s ease, background .2s ease;
    }
    .snap-row:hover { transform: translateX(4px); border-color: var(--c); background: rgba(255, 255, 255, .08); }
    .snap-row .l { display: flex; align-items: center; gap: 9px; font-size: 13px; font-weight: 600; color: #cfe0f5; }
    .snap-row .l i {
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--c); box-shadow: 0 0 10px var(--c);
    }
    .snap-row .n {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px; font-weight: 700; color: #fff;
    }
    .snap-hint { font-size: 12px; color: #9aaac2; margin-top: 10px; line-height: 1.55; }

    /* Hero illustration (replaces the old ✦) */
    @keyframes spin { to { transform: rotate(360deg); } }
    .hero-art {
        position: absolute; right: 5%; top: 50%;
        width: 260px; height: 260px;
        transform: translateY(-50%);
        z-index: 1; pointer-events: none;
    }
    .hero-art .ring {
        position: absolute; inset: 0; border-radius: 50%;
        border: 1px dashed rgba(186, 230, 253, .38);
        animation: spin 30s linear infinite;
    }
    .hero-art .ring:before {
        content: ""; position: absolute; top: -5px; left: 50%;
        width: 10px; height: 10px; margin-left: -5px; border-radius: 50%;
        background: #67e8f9; box-shadow: 0 0 14px #22d3ee;
    }
    .hero-art .r2 {
        inset: 30px; border-style: solid; border-color: rgba(103, 232, 249, .25);
        animation-duration: 42s; animation-direction: reverse;
    }
    .hero-art .r2:before { background: #a5b4fc; box-shadow: 0 0 14px #818cf8; }
    .hero-art .r3 {
        inset: 66px; border-style: dotted; border-color: rgba(255, 255, 255, .22);
        animation-duration: 24s;
    }
    .hero-art .r3:before { width: 7px; height: 7px; margin-left: -3px; top: -4px; background: #fff; box-shadow: 0 0 10px #fff; }
    .hero-art .phone {
        position: absolute; left: 50%; top: 50%;
        width: 98px; height: 178px; margin: -89px 0 0 -49px;
        border-radius: 24px;
        border: 2px solid rgba(255, 255, 255, .6);
        background: linear-gradient(160deg, rgba(255, 255, 255, .2), rgba(255, 255, 255, .04));
        box-shadow: 0 20px 44px rgba(0, 0, 0, .38), 0 0 44px rgba(34, 211, 238, .35),
                    inset 0 0 22px rgba(255, 255, 255, .1);
        overflow: hidden;
        animation: float 6s ease-in-out infinite;
    }
    .hero-art .phone:before {
        content: ""; position: absolute; top: 6px; left: 50%;
        width: 30px; height: 6px; margin-left: -15px; border-radius: 6px;
        background: rgba(255, 255, 255, .55); z-index: 2;
    }
    .hero-art .screen {
        position: absolute; inset: 20px 8px 8px; border-radius: 14px;
        background: linear-gradient(160deg, #0ea5e9, #6366f1 70%, #8b5cf6);
        padding: 12px 9px; display: grid; gap: 8px; align-content: start;
        box-shadow: inset 0 0 18px rgba(255, 255, 255, .2);
    }
    .hero-art .screen b { display: block; height: 8px; border-radius: 6px; background: rgba(255, 255, 255, .8); }
    .hero-art .screen b:nth-child(2) { width: 78%; opacity: .6; }
    .hero-art .screen b:nth-child(3) { width: 48%; opacity: .45; }
    .hero-art .screen em {
        position: absolute; left: 50%; bottom: 14px;
        width: 34px; height: 34px; margin-left: -17px; border-radius: 50%;
        display: grid; place-items: center;
        font-style: normal; font-size: 18px; font-weight: 800; color: #04121f;
        background: linear-gradient(135deg, #a7f3d0, #34d399);
        box-shadow: 0 0 22px rgba(52, 211, 153, .75);
        animation: pulse 2.2s infinite;
    }

    /* Footer rebuilt as a real container so its page links can navigate */
    .st-key-site_footer {
        position: relative; overflow: hidden;
        margin-top: 34px;
        padding: 28px 30px 0;
        gap: .3rem;
        border: 1px solid rgba(96, 165, 250, .22);
        border-radius: 22px;
        background:
            linear-gradient(110deg, rgba(14, 26, 44, .95), rgba(11, 38, 58, .9)),
            url('https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=70');
        background-size: cover;
        box-shadow: 0 10px 28px rgba(0, 0, 0, .18);
    }
    .st-key-site_footer:before {
        content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #3b82f6, #22d3ee, #6366f1, #3b82f6);
        background-size: 200% 100%;
        animation: flow 6s linear infinite;
    }
    .st-key-site_footer [data-testid="stVerticalBlock"] { gap: .15rem; }
    .st-key-site_footer .footer-bottom { margin: 22px -30px 0; }
    .st-key-site_footer div.stButton > button,
    .st-key-site_footer div.stButton > button[data-testid="stBaseButton-secondary"] {
        background: transparent;
        border: 0;
        box-shadow: none;
        -webkit-backdrop-filter: none; backdrop-filter: none;
        justify-content: flex-start;
        min-height: 34px;
        padding: 4px 0;
        width: auto;
        color: #c9d8ee;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0;
        border-radius: 8px;
    }
    .st-key-site_footer div.stButton > button > div { justify-content: flex-start; }
    .st-key-site_footer div.stButton > button:before { display: none; }
    .st-key-site_footer div.stButton > button p { color: inherit; }
    .st-key-site_footer div.stButton > button:hover,
    .st-key-site_footer div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: transparent;
        box-shadow: none;
        filter: none;
        color: #67e8f9;
        transform: translateX(6px);
    }

    @media (max-width: 900px) {
        .hero-art { width: 190px; height: 190px; right: 2%; opacity: .55; }
        .hero-art .phone { transform: scale(.78); }
    }
    @media (max-width: 768px) {
        .st-key-site_footer { padding: 22px 18px 0; border-radius: 16px; }
        .st-key-site_footer .footer-bottom { margin: 18px -18px 0; }
        .st-key-site_footer div.stButton > button { min-height: 42px; width: 100%; }
    }
    @media (max-width: 640px) { .hero-art { display: none; } }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .01ms !important;
            scroll-behavior: auto !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Reusable helpers
# --------------------------------------------------

def esc(value):
    return _html.escape(str(value))


def render_html(markup):
    """Collapse indentation/blank lines so Markdown never treats HTML as code."""
    flat = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


def api_get(path, **kwargs):
    return requests.get(
        f"{API_URL}{path}",
        timeout=10,
        **kwargs,
    )


def api_error(response, action):
    try:
        detail = response.json().get("detail", "")
    except (ValueError, AttributeError):
        detail = ""

    st.error(
        f"{action} failed (HTTP {response.status_code}). "
        f"{detail or 'Please try again.'}"
    )


def status_badge(status):
    icon, fg, bg = STATUS_STYLES.get(status, DEFAULT_STYLE)
    return (
        f'<span class="badge" style="color:{fg};background:{bg};'
        f'border-color:{fg}66">{icon} {esc(status)}</span>'
    )


def style_status_column(df):
    """Colour the status column of the table; fall back to a plain table."""
    def colour(value):
        _, fg, bg = STATUS_STYLES.get(value, DEFAULT_STYLE)
        return f"background-color: {bg}; color: {fg}; font-weight: 600"

    try:
        styler = df.style.set_properties(
            **{"background-color": "#111c2e", "color": "#e5edf9"}
        )
        mapper = getattr(styler, "map", None) or styler.applymap
        return mapper(colour, subset=["current_status"])
    except Exception:
        return df


def tracker_html(current_status):
    idx = STATUSES.index(current_status) if current_status in STATUSES else -1
    last = len(STATUSES) - 1
    steps = []
    for i, name in enumerate(STATUSES):
        if i < idx or (i == idx == last):
            cls, mark = "done", "✓"
        elif i == idx:
            cls, mark = "current", STATUS_STYLES[name][0]
        else:
            cls, mark = "", str(i + 1)
        steps.append(
            f'<div class="step {cls}"><div class="dot">{mark}</div>'
            f'<div class="step-label">{esc(name)}</div></div>'
        )
    return (
        '<div class="tracker"><div class="tracker-title">REPAIR PROGRESS</div>'
        f'<div class="stepper">{"".join(steps)}</div></div>'
    )


def show_service(service):
    st.markdown("#### Repair details")

    st.markdown("**Service ID**")
    st.code(service.get("service_id", "—"))

    status = service.get("current_status", "—")
    render_html(
        f"""
        <div class="detail-grid">
            <div class="detail"><div class="k">Case ID</div>
                <div class="v">{esc(service.get('case_id', '—'))}</div></div>
            <div class="detail"><div class="k">Device</div>
                <div class="v">📱 {esc(service.get('device_model', '—'))}</div></div>
            <div class="detail"><div class="k">Status</div>
                <div class="v">{status_badge(status)}</div></div>
            <div class="detail"><div class="k">Received</div>
                <div class="v">🗓️ {esc(service.get('received_date', '—'))}</div></div>
            <div class="detail" style="grid-column: 1 / -1;"><div class="k">Issue</div>
                <div class="v">{esc(service.get('issue_description', '—'))}</div></div>
        </div>
        """
    )
    render_html(tracker_html(status))


def card_html(label, value, icon="", accent="#60a5fa", pct=None, delay=0):
    icon_html = f'<div class="card-icon">{icon}</div>' if icon else ""
    bar = (
        f'<div class="card-bar"><span style="width:{pct}%"></span></div>'
        if pct is not None
        else ""
    )
    return (
        f'<div class="info-card" style="--accent:{accent};animation-delay:{delay}ms">'
        f'{icon_html}<div class="card-label">{esc(label)}</div>'
        f'<div class="card-value">{esc(value)}</div>{bar}</div>'
    )


def info_card(label, value, icon="", accent="#60a5fa", pct=None):
    render_html(card_html(label, value, icon, accent, pct))


def card_grid(cards, min_width=160):
    items = "".join(
        card_html(delay=i * 70, **card) for i, card in enumerate(cards)
    )
    render_html(
        f'<div class="card-grid" style="--min:{min_width}px">{items}</div>'
    )


# --------------------------------------------------
# Navigation callbacks
# --------------------------------------------------

st.session_state.setdefault("page", "Dashboard")


def go_to(name):
    """Switch page (used by the footer links); the rerun refreshes the data."""
    st.session_state["page"] = name
    st.session_state["scroll_top"] = True


def quick_track():
    value = st.session_state.get("quick_id", "").strip()
    if value:
        st.session_state["page"] = "Track Repair"
        st.session_state["track_id"] = value
        st.session_state["auto_track"] = True
        st.session_state["scroll_top"] = True


# --------------------------------------------------
# Sidebar navigation
# --------------------------------------------------

backend_state = "off"

with st.sidebar:
    render_html(
        """
        <div class="side-brand">
            <div class="side-logo">📱</div>
            <div>
                <div class="side-title">MobileCare</div>
                <div class="side-sub">REPAIR MANAGEMENT SYSTEM</div>
            </div>
        </div>
        """
    )
    st.divider()

    page = st.radio(
        "NAVIGATION",
        PAGES,
        key="page",
        format_func=lambda name: f"{NAV_ICONS[name]}  {name}",
        label_visibility="visible",
    )

    st.divider()

    st.markdown('<div class="side-h">QUICK TRACK</div>', unsafe_allow_html=True)
    with st.form("quick_track", border=False):
        st.text_input(
            "Service ID or Case ID",
            key="quick_id",
            placeholder="SRV-2026-00125",
            label_visibility="collapsed",
        )
        st.form_submit_button("Track now →", on_click=quick_track)

    st.divider()

    # Backend health now only feeds the pill in the top bar
    try:
        backend_state = "ok" if api_get("/health").ok else "warn"
    except requests.RequestException:
        backend_state = "off"

    st.markdown('<div class="side-h">LIVE SNAPSHOT</div>', unsafe_allow_html=True)
    try:
        snap_response = api_get("/services")
        snap_response.raise_for_status()
        snap = snap_response.json().get("services", [])

        def snap_count(status):
            return sum(1 for x in snap if x.get("current_status") == status)

        active_now = sum(1 for x in snap if x.get("current_status") != "Collected")
        ready_now = snap_count("Ready for Collection")
        rows = [
            ("Active repairs", active_now, "#fcd34d"),
            ("Ready for pickup", ready_now, "#6ee7b7"),
            ("In diagnosis", snap_count("Diagnosis"), "#c4b5fd"),
        ]
        render_html(
            '<div class="snap">'
            + "".join(
                f'<div class="snap-row" style="--c:{c}"><span class="l"><i></i>{esc(l)}</span>'
                f'<span class="n">{n}</span></div>'
                for l, n, c in rows
            )
            + "</div>"
            + '<div class="snap-hint">'
            + (
                f"🔔 {ready_now} repair(s) waiting for customer pickup."
                if ready_now
                else "No pickups pending right now."
            )
            + "</div>"
        )
    except (requests.RequestException, ValueError, AttributeError):
        st.caption("Connect the backend to see live counts.")

    st.markdown("---")
    st.caption("MobileCare • Service Portal")
    st.caption("FastAPI · Streamlit · SQLite")


# --------------------------------------------------
# Header
# --------------------------------------------------

live_label = {
    "ok": "● Backend online",
    "warn": "● Backend error",
    "off": "● Backend offline",
}[backend_state]
eyebrow, title, subtitle = PAGE_META[page]

if st.session_state.pop("scroll_top", False):
    scroll_js = (
        "<script>const d=window.parent.document;"
        "const m=d.querySelector('[data-testid=\"stMain\"]')||d.querySelector('section.main');"
        "if(m){m.scrollTo({top:0,behavior:'smooth'});}</script>"
    )
    try:
        if hasattr(st, "iframe"):  # newer Streamlit
            st.iframe(scroll_js, height=1)
        else:
            components.html(scroll_js, height=0)
    except Exception:
        pass

render_html(
    f"""
    <div class="topbar">
        <div class="tb-brand"><span class="tb-logo">📱</span><span>MobileCare</span></div>
        <div class="tb-right">
            <span class="tb-crumb">{NAV_ICONS[page]} {esc(page)}</span>
            <span class="tb-live {backend_state}">{live_label}</span>
        </div>
    </div>
    <div class="hero">
        <div class="eyebrow">{esc(eyebrow)}</div>
        <h1>{esc(title)}</h1>
        <p>{esc(subtitle)}</p>
        <div class="chips">
            <span class="chip">⚡ Real-time status</span>
            <span class="chip">🔒 Reliable records</span>
            <span class="chip">📱 Works on any device</span>
        </div>
        <div class="hero-art" aria-hidden="true">
            <span class="ring r1"></span><span class="ring r2"></span><span class="ring r3"></span>
            <div class="phone"><div class="screen"><b></b><b></b><b></b><em>✓</em></div></div>
        </div>
    </div>
    """
)

# --------------------------------------------------
# Dashboard
# --------------------------------------------------

if page == "Dashboard":
    st.markdown(
        '<div class="section-label">Overview</div>',
        unsafe_allow_html=True,
    )

    try:
        response = api_get("/services")
        response.raise_for_status()
        services = response.json().get("services", [])

        # Search and filter
        f1, f2 = st.columns([2, 1])
        with f1:
            search = st.text_input(
                "🔎 Search requests",
                placeholder="Search by service ID, case ID, device, or issue",
            )
        with f2:
            selected_status = st.selectbox(
                "Filter by status",
                ["All statuses"] + STATUSES,
            )

        filtered = services

        if search.strip():
            term = search.strip().lower()
            filtered = [
                service for service in filtered
                if any(
                    term in str(service.get(key, "")).lower()
                    for key in (
                        "service_id",
                        "case_id",
                        "device_model",
                        "issue_description",
                    )
                )
            ]

        if selected_status != "All statuses":
            filtered = [
                service for service in filtered
                if service.get("current_status") == selected_status
            ]

        # Summary cards
        total = len(services)
        active = sum(
            1 for service in services
            if service.get("current_status") not in ("Collected",)
        )
        completed = sum(
            1 for service in services
            if service.get("current_status") == "Collected"
        )

        def pct(n):
            return round(n * 100 / total) if total else 0

        card_grid(
            [
                dict(label="TOTAL REQUESTS", value=total, icon="📋",
                     accent="#60a5fa", pct=100 if total else 0),
                dict(label="ACTIVE REPAIRS", value=active, icon="🛠️",
                     accent="#fcd34d", pct=pct(active)),
                dict(label="COLLECTED", value=completed, icon="📦",
                     accent="#6ee7b7", pct=pct(completed)),
            ],
            min_width=210,
        )

        st.markdown(
            '<div class="section-label">Repair pipeline</div>',
            unsafe_allow_html=True,
        )

        pipeline = []
        for status in STATUSES:
            count = sum(
                1 for service in services
                if service.get("current_status") == status
            )
            icon, fg, _ = STATUS_STYLES[status]
            pipeline.append(
                dict(label=status.upper(), value=count, icon=icon,
                     accent=fg, pct=pct(count))
            )
        card_grid(pipeline, min_width=165)

        st.markdown(
            '<div class="section-label">Service requests</div>',
            unsafe_allow_html=True,
        )

        if filtered:
            df = pd.DataFrame(filtered)
            columns = [
                "service_id",
                "case_id",
                "device_model",
                "issue_description",
                "current_status",
                "received_date",
            ]
            table = style_status_column(df[columns])
            try:
                st.dataframe(table, width="stretch", hide_index=True)
            except TypeError:  # older Streamlit versions
                st.dataframe(table, use_container_width=True, hide_index=True)
            st.caption(f"Showing {len(filtered)} of {total} loaded requests.")
        else:
            st.info("No service requests match your search or filter.")

        if st.button("↻ Refresh dashboard"):
            st.rerun()

    except requests.RequestException:
        st.error("Could not load services. Make sure FastAPI is running.")
    except (ValueError, KeyError, TypeError):
        st.error("The backend returned data in an unexpected format.")

# --------------------------------------------------
# Track repair
# --------------------------------------------------

elif page == "Track Repair":
    st.markdown(
        '<div class="section-label">Find your repair</div>',
        unsafe_allow_html=True,
    )
    st.write("Enter the Service ID or Case ID associated with your repair.")

    with st.form("track_form"):
        identifier = st.text_input(
            "Service ID or Case ID",
            placeholder="SRV-2026-00125",
            key="track_id",
        )
        track_submitted = st.form_submit_button("🔎 Track repair")

    auto_track = st.session_state.pop("auto_track", False)

    if track_submitted or auto_track:
        if not identifier.strip():
            st.warning("Enter a Service ID or Case ID.")
        else:
            try:
                response = api_get(
                    f"/track/{requests.utils.quote(identifier.strip(), safe='')}"
                )

                if response.status_code == 200:
                    st.success("Repair request found.")
                    show_service(response.json()["service"])
                else:
                    api_error(response, "Tracking")

            except requests.RequestException:
                st.error("Could not connect to the backend.")

# --------------------------------------------------
# Create request
# --------------------------------------------------

elif page == "New Request":
    st.markdown(
        '<div class="section-label">Register a repair</div>',
        unsafe_allow_html=True,
    )
    st.write("Enter the customer case and device issue details.")

    with st.form("create_form", clear_on_submit=False):
        case_id = st.text_input(
            "Case ID",
            placeholder="CASE-2001",
        )
        device_model = st.text_input(
            "Device model",
            placeholder="Samsung Galaxy S24",
        )
        issue_description = st.text_area(
            "Issue description",
            placeholder="Describe the problem with the device",
            max_chars=500,
        )

        create_submitted = st.form_submit_button(
            "＋ Create service request"
        )

    if create_submitted:
        payload = {
            "case_id": case_id.strip(),
            "device_model": device_model.strip(),
            "issue_description": issue_description.strip(),
        }

        if not all(payload.values()):
            st.warning("Please complete all fields.")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/services",
                    json=payload,
                    timeout=10,
                )

                if response.status_code == 201:
                    service = response.json()["service"]
                    st.success("Service request created successfully!")
                    st.markdown("### Your new Service ID")
                    st.code(service["service_id"])
                    render_html(
                        f"""
                        <div class="detail-grid">
                            <div class="detail"><div class="k">Initial status</div>
                                <div class="v">{status_badge(service['current_status'])}</div></div>
                        </div>
                        """
                    )
                    st.info(
                        "Save the Service ID. You can use it to track "
                        "the repair or update its status."
                    )
                else:
                    api_error(response, "Create request")

            except requests.RequestException:
                st.error("Could not connect to the backend.")

# --------------------------------------------------
# Update status
# --------------------------------------------------

elif page == "Update Status":
    st.markdown(
        '<div class="section-label">Update repair progress</div>',
        unsafe_allow_html=True,
    )
    st.write("Change the status of an existing repair request.")

    with st.form("update_status_form"):
        service_id = st.text_input(
            "Service ID",
            placeholder="SRV-2026-00125",
        )
        new_status = st.selectbox(
            "New repair status",
            STATUSES,
        )
        update_submitted = st.form_submit_button("🔄 Update status")

    if update_submitted:
        if not service_id.strip():
            st.warning("Please enter a Service ID.")
        else:
            try:
                response = requests.patch(
                    f"{API_URL}/services/"
                    f"{requests.utils.quote(service_id.strip(), safe='')}/status",
                    params={"new_status": new_status},
                    timeout=10,
                )

                '''if response.status_code == 200:
                    result = response.json()
                    st.success("Repair status updated successfully!")
                    st.markdown(
                        f"### {result['current_status']}"
                    )
                    st.caption(f"Service ID: {result['service_id']}")
                    render_html(tracker_html(result["current_status"]))
                    st.info(
                        "Open Dashboard and refresh it to view the latest status."
                    )'''

                if response.status_code == 200:
                    data = response.json()
                    # Backend may return the record directly or nested under "service"
                    result = data.get("service", data) if isinstance(data, dict) else {}
                    current_status = result.get("current_status", new_status)
                    updated_id = result.get("service_id", service_id.strip())

                    st.success("Repair status updated successfully!")
                    st.markdown(f"### {current_status}")
                    st.caption(f"Service ID: {updated_id}")
                    render_html(tracker_html(current_status))
                    
                else:
                    api_error(response, "Status update")

            except requests.RequestException:
                st.error("Could not connect to the backend.")

# --------------------------------------------------
# Footer
# --------------------------------------------------

with st.container(key="site_footer"):
    footer_brand, footer_stack, footer_pages = st.columns([1.6, 1, 1])

    with footer_brand:
        render_html(
            """
            <div class="footer-brand">📱 MobileCare <span style="color:#67e8f9;">·</span> Service Portal</div>
            <div class="footer-copy">Making device care simpler, clearer, and more reliable.
            Register repairs, follow every step, and keep customers in the loop.</div>
            <span class="footer-pill">● SYSTEM WORKSPACE</span>
            """
        )

    with footer_pages:
        render_html('<div class="footer-h">PORTAL</div>')
        for name in PAGES:
            st.button(
                f"{NAV_ICONS[name]} {name}",
                key=f"footer_nav_{name}",
                on_click=go_to,
                args=(name,),
            )

    with footer_stack:
        render_html(
            """
            <div class="footer-h">BUILT WITH</div>
            <span class="footer-link">🐍 Python</span>
            <span class="footer-link">🎈 Streamlit</span>
            <span class="footer-link">⚡ FastAPI</span>
            <span class="footer-link">🗄️ SQLite</span>
            """
        )

    render_html(
        """
        <div class="footer-bottom">
            <span>© 2026 MobileCare Service Portal</span>
        </div>
        """
    )


# --------------------------------------------------
# SERVICE HISTORY
# --------------------------------------------------

st.divider()

st.header("Service History")

st.write(
    "View the complete status-change history "
    "of a service request."
)

history_service_id = st.text_input(
    "Enter Service ID",
    key="history_service_id"
)

if st.button("View Service History"):

    if not history_service_id.strip():

        st.warning("Please enter a Service ID.")

    else:

        try:
            response = requests.get(
                f"{API_URL}/services/{history_service_id.strip()}/history",
                timeout=10
            )

            if response.status_code == 200:

                history_data = response.json()
                history = history_data["history"]

                st.subheader("Status History")

                if history:

                    for record in history:

                        old_status = (
                            record["old_status"]
                            if record["old_status"]
                            else "Initial Status"
                        )

                        st.markdown(
                            f"""
                            **{old_status} → {record['new_status']}**

                            Changed at: {record['changed_at']}
                            """
                        )

                        st.divider()

                else:
                    st.info("No history records found.")

            elif response.status_code == 404:

                st.error("Service ID not found.")

            else:

                st.error(
                    f"Unable to retrieve history. "
                    f"Status code: {response.status_code}"
                )

        except requests.exceptions.RequestException as error:

            st.error(
                f"Could not connect to the backend: {error}"
            )
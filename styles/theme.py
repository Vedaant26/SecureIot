"""
SecureIoT Theme — Dark Navy Cybersecurity Dashboard
Provides custom CSS for a professional, modern appearance.
"""


def get_css():
    """Return the full custom CSS for the app."""
    return """
<style>
/* ── Import Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0b1120 0%, #0f172a 50%, #0b1120 100%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1428 0%, #111a35 100%);
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] .stMarkdown h1 {
    color: #3b82f6 !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.95rem !important;
    padding: 4px 0;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #e2e8f0 !important;
}

/* ── Hide default streamlit elements ── */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #111a35 0%, #162040 100%);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px 18px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
}
div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* ── Containers / Cards ── */
div[data-testid="stExpander"] {
    background: #111a35;
    border: 1px solid #1e293b;
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
    font-weight: 600;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 8px 24px;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
    box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.5);
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    background-color: #111a35;
    border-radius: 8px 8px 0 0;
    border: 1px solid #1e293b;
    border-bottom: none;
    color: #94a3b8;
    padding: 8px 20px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background-color: #162040 !important;
    color: #3b82f6 !important;
    border-color: #3b82f6 !important;
}

/* ── Tables ── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}
table {
    border-collapse: separate;
    border-spacing: 0;
}

/* ── Divider ── */
hr {
    border-color: #1e293b !important;
    margin: 20px 0;
}

/* ── Success / Warning / Error boxes ── */
div[data-testid="stAlert"] {
    border-radius: 10px;
    border-left-width: 4px;
}

/* ── Custom card helper class via markdown ── */
.card-container {
    background: linear-gradient(135deg, #111a35 0%, #162040 100%);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 24px;
    margin: 8px 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.card-title {
    color: #3b82f6;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 8px;
}
.card-value {
    color: #e2e8f0;
    font-size: 2rem;
    font-weight: 700;
}
.card-subtitle {
    color: #64748b;
    font-size: 0.85rem;
    margin-top: 4px;
}

/* ── Status badges ── */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.status-active { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.status-warning { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
.status-danger { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.status-info { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }

/* ── Section headers ── */
.section-header {
    color: #e2e8f0;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 24px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #1e293b;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0b1120; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* ── Code blocks ── */
code {
    background-color: #0f172a !important;
    color: #3b82f6 !important;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
}
pre {
    background-color: #0f172a !important;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 16px !important;
}
</style>
"""


def metric_card(label, value, icon="", delta=None, color="#3b82f6"):
    """Return HTML for a styled metric card."""
    delta_html = ""
    if delta is not None:
        delta_color = "#10b981" if delta >= 0 else "#ef4444"
        delta_icon = "↑" if delta >= 0 else "↓"
        delta_html = f'<div style="color:{delta_color};font-size:0.85rem;margin-top:4px;">{delta_icon} {abs(delta)}</div>'

    return f"""
    <div style="
        background: linear-gradient(135deg, #111a35 0%, #162040 100%);
        border: 1px solid #1e293b;
        border-top: 3px solid {color};
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        text-align: center;
    ">
        <div style="font-size:1.8rem;margin-bottom:6px;">{icon}</div>
        <div style="color:#94a3b8;font-size:0.75rem;font-weight:500;text-transform:uppercase;letter-spacing:1px;">
            {label}
        </div>
        <div style="color:#e2e8f0;font-size:2rem;font-weight:700;margin:4px 0;">
            {value}
        </div>
        {delta_html}
    </div>
    """


def status_badge(text, status="active"):
    """Return HTML for a status badge."""
    colors = {
        "active": ("#10b981", "rgba(16,185,129,0.15)", "rgba(16,185,129,0.3)"),
        "warning": ("#f59e0b", "rgba(245,158,11,0.15)", "rgba(245,158,11,0.3)"),
        "danger": ("#ef4444", "rgba(239,68,68,0.15)", "rgba(239,68,68,0.3)"),
        "info": ("#3b82f6", "rgba(59,130,246,0.15)", "rgba(59,130,246,0.3)"),
        "inactive": ("#64748b", "rgba(100,116,139,0.15)", "rgba(100,116,139,0.3)"),
    }
    fg, bg, bd = colors.get(status, colors["info"])
    return (
        f'<span style="display:inline-block;padding:4px 12px;border-radius:20px;'
        f'font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'
        f'background:{bg};color:{fg};border:1px solid {bd};">{text}</span>'
    )


def section_title(text, icon=""):
    """Return styled section title HTML."""
    return f"""
    <div style="color:#e2e8f0;font-size:1.3rem;font-weight:700;margin:24px 0 16px 0;
         padding-bottom:8px;border-bottom:2px solid #1e293b;">
        {icon} {text}
    </div>
    """


def plotly_theme():
    """Return a Plotly layout dict for consistent dark charts."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
        xaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b"),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        colorway=["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"],
    )

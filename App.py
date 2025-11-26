# app.py - Enhanced CAT Planner Dashboard
import streamlit as st
import pandas as pd
from io import BytesIO, StringIO
from datetime import datetime, timedelta
import random

# Page config
st.set_page_config(
    page_title="CAT Planner Pro", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎯"
)

# --- Custom CSS for Modern Design ---
st.markdown("""
<style>
    /* Main background and fonts */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom card styling */
    .metric-card {
        background: linear-gradient(145deg, #1e3a5f, #2d5a87);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 30px;
        text-align: center;
    }
    
    /* Table container */
    .table-container {
        background: rgba(255,255,255,0.03);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    .table-title {
        color: #fff;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Custom table styling */
    .styled-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px;
    }
    
    .styled-table thead tr {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
    }
    
    .styled-table th {
        padding: 15px 20px;
        text-align: left;
        font-weight: 600;
        color: #1a1a2e;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .styled-table th:first-child {
        border-radius: 10px 0 0 10px;
    }
    
    .styled-table th:last-child {
        border-radius: 0 10px 10px 0;
    }
    
    .styled-table tbody tr {
        background: rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }
    
    .styled-table tbody tr:hover {
        background: rgba(255,255,255,0.1);
        transform: scale(1.01);
    }
    
    .styled-table td {
        padding: 18px 20px;
        color: #e2e8f0;
        font-size: 0.95rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .styled-table td:first-child {
        border-radius: 10px 0 0 10px;
        font-weight: 600;
        color: #fff;
    }
    
    .styled-table td:last-child {
        border-radius: 0 10px 10px 0;
    }
    
    /* Status badges */
    .badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background: linear-gradient(90deg, #11998e, #38ef7d);
        color: #fff;
    }
    
    .badge-pending {
        background: linear-gradient(90deg, #fc4a1a, #f7b733);
        color: #fff;
    }
    
    .badge-easy {
        background: linear-gradient(90deg, #11998e, #38ef7d);
        color: #fff;
    }
    
    .badge-moderate {
        background: linear-gradient(90deg, #f093fb, #f5576c);
        color: #fff;
    }
    
    .badge-hard {
        background: linear-gradient(90deg, #eb3349, #f45c43);
        color: #fff;
    }
    
    /* Progress bar */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin-top: 10px;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.5s ease;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3a5f 0%, #16213e 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(145deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border-left: 4px solid #667eea;
        border-radius: 0 10px 10px 0;
        padding: 20px;
        margin: 20px 0;
        color: #e2e8f0;
    }
    
    /* Week card for plan */
    .week-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .week-card:hover {
        border-color: rgba(102, 126, 234, 0.5);
        transform: translateX(5px);
    }
    
    .week-card.completed {
        border-left: 4px solid #38ef7d;
        background: linear-gradient(145deg, rgba(56, 239, 125, 0.1), rgba(17, 153, 142, 0.05));
    }
    
    .week-number {
        font-size: 1.2rem;
        font-weight: 700;
        color: #4facfe;
        margin-bottom: 8px;
    }
    
    .week-target {
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Tracker stats */
    .tracker-stat {
        background: linear-gradient(145deg, rgba(79, 172, 254, 0.15), rgba(0, 242, 254, 0.05));
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(79, 172, 254, 0.2);
    }
    
    .tracker-stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4facfe;
    }
    
    .tracker-stat-label {
        color: #a0aec0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #a0aec0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: #e2e8f0;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 40px;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 50%, #667eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
        animation: gradient 3s ease infinite;
        background-size: 200% auto;
    }
    
    @keyframes gradient {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }
    
    .hero-subtitle {
        color: #a0aec0;
        font-size: 1.2rem;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Checkbox styling */
    .checkbox-cell {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .checkbox-checked {
        color: #38ef7d;
        font-size: 1.5rem;
    }
    
    .checkbox-unchecked {
        color: #a0aec0;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Compatibility helper ---
def get_data_editor():
    if hasattr(st, "data_editor"):
        return getattr(st, "data_editor"), True
    if hasattr(st, "experimental_data_editor"):
        return getattr(st, "experimental_data_editor"), True
    return None, False

data_editor_fn, has_editor = get_data_editor()

# ---------------------
# Helper: initial data
# ---------------------
def get_initial_syllabus():
    varc = [
        ("Reading Comprehension", "Economy, Psychology, Philosophy, Technology, History, Abstract RCs", "Inference, Main idea, Tone, Strengthen/Weaken", 85),
        ("Para Jumbles", "Mandatory pairs, Pronoun linkage, Chronological order", "4–5 sentence PJs", 70),
        ("Odd One Out", "Theme mismatch, Link-breaking", "TITA OOO questions", 65),
        ("Para Completion", "Logical continuation, Ending-sentence identification", "Final-sentence prediction", 60),
        ("Paragraph Summary", "Remove examples, key idea extraction", "20–40 word summaries", 75)
    ]
    dilr = [
        ("Arrangements & Ordering", "Linear, Circular, Ranking, Mixed-variable puzzles", "Mixed puzzle sets", 80),
        ("Selection & Distribution", "Committee selection, People-object assignment", "Constraint-based distribution", 72),
        ("Games & Tournaments", "Round-robin, Knockouts, Points table reasoning", "6-8 variable tournament sets", 55),
        ("Set Theory", "2-set, 3-set venn, Max/Min overlaps", "Venn + DI integration", 68),
        ("DI Charts & Tables", "Tables, Bar, Pie, Line, Caselets", "Calculation-heavy DI sets", 78),
        ("Logic Puzzles", "Binary logic, Truth–lie, Conditional logic", "Mixed DILR sets", 62)
    ]
    qa = [
        ("Number System", "Divisibility, LCM–HCF, Remainders, Cyclicity, Base", "Modular arithmetic, Last-digit tricks", 85),
        ("Arithmetic", "Percentages, Ratio, Averages, TSD, Time & Work, Profit–Loss, Mixtures", "Fast methods, LCM approach", 90),
        ("Algebra", "Linear, Quadratic, Inequalities, Modulus, Logs, Exponents", "Wavy curve, root properties", 75),
        ("Geometry & Mensuration", "Triangles, Circles, Coordinate Geo, Mensuration", "Area/length relations, formulae", 65),
        ("Modern Math", "Permutation & Combination, Probability, Sets", "Restrictions, conditional prob", 58)
    ]

    df_varc = pd.DataFrame(varc, columns=["Main Topic", "Sub-Topics", "Practice Focus", "Confidence %"])
    df_dilr = pd.DataFrame(dilr, columns=["Main Topic", "Sub-Topics", "Practice Focus", "Confidence %"])
    df_qa = pd.DataFrame(qa, columns=["Main Topic", "Sub-Topics", "Practice Focus", "Confidence %"])

    df_varc["Studied?"] = False
    df_dilr["Studied?"] = False
    df_qa["Studied?"] = False
    
    df_varc["Priority"] = ["High", "Medium", "Medium", "Low", "High"]
    df_dilr["Priority"] = ["High", "Medium", "High", "Medium", "Medium", "High"]
    df_qa["Priority"] = ["High", "High", "Medium", "Medium", "High"]

    return df_varc, df_dilr, df_qa

def get_initial_difficulty():
    rows = [
        ("VARC", "RC Abstract", "Hard", False, 45),
        ("VARC", "Para Summary", "Easy", False, 78),
        ("DILR", "Games/Tournaments", "Hard", False, 52),
        ("DILR", "Tables/Charts", "Easy", False, 85),
        ("QA", "Arithmetic", "Easy", False, 92),
        ("QA", "Geometry", "Moderate", False, 68),
        ("QA", "Probability", "Hard", False, 55),
    ]
    df = pd.DataFrame(rows, columns=["Section", "Topic Category", "Level", "Studied?", "Mastery %"])
    return df

def get_initial_plan():
    base_date = datetime.now()
    rows = [
        ("Week 1", "Percentages + 2 RCs/day + 1 DI Set", False, (base_date).strftime("%b %d"), (base_date + timedelta(days=6)).strftime("%b %d")),
        ("Week 2", "Ratio, Averages + PJ + DI Tables", False, (base_date + timedelta(days=7)).strftime("%b %d"), (base_date + timedelta(days=13)).strftime("%b %d")),
        ("Week 3", "TSD, Time & Work + Summary + Venn", False, (base_date + timedelta(days=14)).strftime("%b %d"), (base_date + timedelta(days=20)).strftime("%b %d")),
        ("Week 4", "Profit-Loss + Moderate RCs + Arrangements", False, (base_date + timedelta(days=21)).strftime("%b %d"), (base_date + timedelta(days=27)).strftime("%b %d")),
        ("Week 5", "Algebra basics + 3 RCs/day", False, (base_date + timedelta(days=28)).strftime("%b %d"), (base_date + timedelta(days=34)).strftime("%b %d")),
        ("Week 6", "Geometry basics + DI charts", False, (base_date + timedelta(days=35)).strftime("%b %d"), (base_date + timedelta(days=41)).strftime("%b %d")),
        ("Week 7", "Advanced Algebra + Hybrid sets", False, (base_date + timedelta(days=42)).strftime("%b %d"), (base_date + timedelta(days=48)).strftime("%b %d")),
        ("Week 8", "Tournaments + Abstract RC", False, (base_date + timedelta(days=49)).strftime("%b %d"), (base_date + timedelta(days=55)).strftime("%b %d")),
        ("Week 9", "P&C + Functions + Hard DI Sets", False, (base_date + timedelta(days=56)).strftime("%b %d"), (base_date + timedelta(days=62)).strftime("%b %d")),
        ("Week 10", "Full mocks (2/week)", False, (base_date + timedelta(days=63)).strftime("%b %d"), (base_date + timedelta(days=69)).strftime("%b %d")),
        ("Week 11", "Mock analysis + weak topic revision", False, (base_date + timedelta(days=70)).strftime("%b %d"), (base_date + timedelta(days=76)).strftime("%b %d")),
        ("Week 12", "Final mocks + strategy tuning", False, (base_date + timedelta(days=77)).strftime("%b %d"), (base_date + timedelta(days=83)).strftime("%b %d")),
    ]
    df = pd.DataFrame(rows, columns=["Week", "Target", "Completed?", "Start Date", "End Date"])
    return df

def get_initial_tracker():
    # Sample data for demo
    sample_data = [
        ("2024-01-15", "QA", "Arithmetic", 25, 20, 5, 80.0, "45 min", True),
        ("2024-01-16", "VARC", "RC", 12, 9, 3, 75.0, "30 min", True),
        ("2024-01-17", "DILR", "DI Sets", 8, 6, 2, 75.0, "25 min", False),
        ("2024-01-18", "QA", "Algebra", 20, 15, 5, 75.0, "40 min", True),
        ("2024-01-19", "VARC", "Para Jumbles", 10, 8, 2, 80.0, "20 min", False),
    ]
    df = pd.DataFrame(sample_data, columns=["Date", "Section", "Topic", "No. of Questions", "Correct", "Wrong", "Accuracy %", "Time Taken", "Reviewed?"])
    return df

# ---------------------
# Initialize session state
# ---------------------
if "df_varc" not in st.session_state:
    st.session_state.df_varc, st.session_state.df_dilr, st.session_state.df_qa = get_initial_syllabus()
if "df_difficulty" not in st.session_state:
    st.session_state.df_difficulty = get_initial_difficulty()
if "df_plan" not in st.session_state:
    st.session_state.df_plan = get_initial_plan()
if "df_tracker" not in st.session_state:
    st.session_state.df_tracker = get_initial_tracker()

# ---------------------
# Utility functions
# ---------------------
def to_excel_bytes(dfs: dict):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)
    bio.seek(0)
    return bio.read()

def get_badge_html(text, badge_type="default"):
    colors = {
        "success": "badge-success",
        "pending": "badge-pending",
        "easy": "badge-easy",
        "moderate": "badge-moderate",
        "hard": "badge-hard",
        "high": "badge-hard",
        "medium": "badge-moderate",
        "low": "badge-easy"
    }
    badge_class = colors.get(badge_type.lower(), "badge-pending")
    return f'<span class="badge {badge_class}">{text}</span>'

def render_progress_bar(percentage):
    return f'''
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%;"></div>
    </div>
    <div style="color: #a0aec0; font-size: 0.8rem; margin-top: 5px;">{percentage}% Complete</div>
    '''

def render_styled_table(df, section_colors=None):
    """Render a beautifully styled HTML table"""
    html = '<table class="styled-table"><thead><tr>'
    
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    
    for idx, row in df.iterrows():
        html += '<tr>'
        for col_idx, (col, val) in enumerate(row.items()):
            cell_content = str(val)
            
            # Special formatting for certain columns
            if col == "Studied?" or col == "Completed?" or col == "Reviewed?":
                if val == True or val == "True":
                    cell_content = '<span class="checkbox-checked">✓</span>'
                else:
                    cell_content = '<span class="checkbox-unchecked">○</span>'
            elif col == "Level" or col == "Priority":
                cell_content = get_badge_html(val, val)
            elif col == "Confidence %" or col == "Mastery %" or col == "Accuracy %":
                try:
                    pct = float(val)
                    color = "#38ef7d" if pct >= 80 else "#f7b733" if pct >= 60 else "#eb3349"
                    cell_content = f'<span style="color: {color}; font-weight: 600;">{pct:.0f}%</span>'
                except:
                    pass
            
            html += f'<td>{cell_content}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html

def render_week_cards(df):
    """Render study plan as beautiful week cards"""
    html = '<div style="display: grid; gap: 15px;">'
    
    for idx, row in df.iterrows():
        completed_class = "completed" if row["Completed?"] else ""
        check_icon = "✓" if row["Completed?"] else "○"
        check_color = "#38ef7d" if row["Completed?"] else "#a0aec0"
        
        html += f'''
        <div class="week-card {completed_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div class="week-number">{row["Week"]} <span style="color: #a0aec0; font-size: 0.8rem; font-weight: 400;">({row["Start Date"]} - {row["End Date"]})</span></div>
                    <div class="week-target">{row["Target"]}</div>
                </div>
                <span style="color: {check_color}; font-size: 1.5rem;">{check_icon}</span>
            </div>
        </div>
        '''
    
    html += '</div>'
    return html

# ---------------------
# Sidebar
# ---------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3rem;">🎯</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #4facfe; margin-top: 10px;">CAT Planner Pro</div>
        <div style="color: #a0aec0; font-size: 0.8rem;">Your path to IIM</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio(
        "📍 Navigation",
        ["🏠 Dashboard", "📚 Syllabus", "📊 Difficulty Analysis", "📅 3-Month Plan", "📝 Practice Tracker", "⬇️ Export Data"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Stats in Sidebar
    total_items = len(st.session_state.df_varc) + len(st.session_state.df_dilr) + len(st.session_state.df_qa)
    studied_count = st.session_state.df_varc["Studied?"].sum() + st.session_state.df_dilr["Studied?"].sum() + st.session_state.df_qa["Studied?"].sum()
    progress_pct = int((studied_count / total_items) * 100) if total_items > 0 else 0
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
        <div style="color: #a0aec0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">Overall Progress</div>
        <div style="font-size: 2rem; font-weight: 700; color: #4facfe; margin: 10px 0;">{progress_pct}%</div>
        {render_progress_bar(progress_pct)}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown('<div style="color: #a0aec0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ All", help="Mark all syllabus as studied"):
            for df in ("df_varc", "df_dilr", "df_qa"):
                st.session_state[df]["Studied?"] = True
            st.rerun()
    with col2:
        if st.button("✗ All", help="Unmark all syllabus"):
            for df in ("df_varc", "df_dilr", "df_qa"):
                st.session_state[df]["Studied?"] = False
            st.rerun()
    
    if st.button("🔄 Reset Data", use_container_width=True):
        st.session_state.df_varc, st.session_state.df_dilr, st.session_state.df_qa = get_initial_syllabus()
        st.session_state.df_difficulty = get_initial_difficulty()
        st.session_state.df_plan = get_initial_plan()
        st.session_state.df_tracker = get_initial_tracker()
        st.success("Reset complete!")
        st.rerun()
    
    st.markdown("---")
    st.markdown(f'<div style="color: #4a5568; font-size: 0.7rem; text-align: center;">Streamlit v{st.__version__}</div>', unsafe_allow_html=True)

# ---------------------
# Main Content Pages
# ---------------------

if page == "🏠 Dashboard":
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">CAT Planner Pro</div>
        <div class="hero-subtitle">Your comprehensive dashboard for CAT 2024 preparation. Track progress, manage syllabus, and ace the exam!</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics Row
    total_items = len(st.session_state.df_varc) + len(st.session_state.df_dilr) + len(st.session_state.df_qa)
    studied_count = int(st.session_state.df_varc["Studied?"].sum() + st.session_state.df_dilr["Studied?"].sum() + st.session_state.df_qa["Studied?"].sum())
    weeks_completed = int(st.session_state.df_plan["Completed?"].sum())
    tracker_entries = len(st.session_state.df_tracker)
    
    # Calculate average accuracy
    if tracker_entries > 0:
        avg_accuracy = st.session_state.df_tracker["Accuracy %"].mean()
    else:
        avg_accuracy = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📚</div>
            <div class="metric-label">Syllabus Topics</div>
            <div class="metric-value">{total_items}</div>
            <div style="color: #38ef7d; font-size: 0.85rem;">+{studied_count} completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">✅</div>
            <div class="metric-label">Topics Studied</div>
            <div class="metric-value">{studied_count}</div>
            <div style="color: #4facfe; font-size: 0.85rem;">{int(studied_count/total_items*100) if total_items > 0 else 0}% progress</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📅</div>
            <div class="metric-label">Weeks Completed</div>
            <div class="metric-value">{weeks_completed}/12</div>
            <div style="color: #f7b733; font-size: 0.85rem;">{12-weeks_completed} weeks remaining</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-label">Avg Accuracy</div>
            <div class="metric-value">{avg_accuracy:.0f}%</div>
            <div style="color: #764ba2; font-size: 0.85rem;">{tracker_entries} practice sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section Progress
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header" style="text-align: left; font-size: 1.5rem;">📊 Section Progress</div>', unsafe_allow_html=True)
        
        sections = [
            ("VARC", st.session_state.df_varc, "#667eea"),
            ("DILR", st.session_state.df_dilr, "#f093fb"),
            ("QA", st.session_state.df_qa, "#4facfe")
        ]
        
        for name, df, color in sections:
            total = len(df)
            studied = int(df["Studied?"].sum())
            pct = int((studied / total) * 100) if total > 0 else 0
            avg_conf = df["Confidence %"].mean() if "Confidence %" in df.columns else 0
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 4px solid {color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: #fff;">{name}</div>
                        <div style="color: #a0aec0; font-size: 0.85rem;">{studied}/{total} topics • Avg confidence: {avg_conf:.0f}%</div>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: {color};">{pct}%</div>
                </div>
                <div class="progress-container" style="margin-top: 15px;">
                    <div class="progress-bar" style="width: {pct}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header" style="text-align: left; font-size: 1.5rem;">🔥 Focus Areas</div>', unsafe_allow_html=True)
        
        # Find topics with low confidence
        all_topics = pd.concat([
            st.session_state.df_varc[["Main Topic", "Confidence %"]].assign(Section="VARC"),
            st.session_state.df_dilr[["Main Topic", "Confidence %"]].assign(Section="DILR"),
            st.session_state.df_qa[["Main Topic", "Confidence %"]].assign(Section="QA")
        ])
        low_conf = all_topics.nsmallest(5, "Confidence %")
        
        for idx, row in low_conf.iterrows():
            conf = row["Confidence %"]
            color = "#eb3349" if conf < 60 else "#f7b733" if conf < 75 else "#38ef7d"
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #fff; font-size: 0.9rem;">{row["Main Topic"]}</div>
                    <div style="color: #a0aec0; font-size: 0.75rem;">{row["Section"]}</div>
                </div>
                <div style="color: {color}; font-weight: 600;">{conf:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

elif page == "📚 Syllabus":
    st.markdown('<div class="section-header">📚 Complete CAT Syllabus</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🗣️ VARC", "🧩 DILR", "🔢 QA"])
    
    with tabs[0]:
        st.markdown("""
        <div class="table-container">
            <div class="table-title">🗣️ Verbal Ability & Reading Comprehension</div>
        """, unsafe_allow_html=True)
        st.markdown(render_styled_table(st.session_state.df_varc), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Editable version
        with st.expander("✏️ Edit VARC Syllabus"):
            if has_editor:
                edited = data_editor_fn(st.session_state.df_varc, key="varc_edit", use_container_width=True)
                st.session_state.df_varc = edited
            else:
                st.dataframe(st.session_state.df_varc)
    
    with tabs[1]:
        st.markdown("""
        <div class="table-container">
            <div class="table-title">🧩 Data Interpretation & Logical Reasoning</div>
        """, unsafe_allow_html=True)
        st.markdown(render_styled_table(st.session_state.df_dilr), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("✏️ Edit DILR Syllabus"):
            if has_editor:
                edited = data_editor_fn(st.session_state.df_dilr, key="dilr_edit", use_container_width=True)
                st.session_state.df_dilr = edited
            else:
                st.dataframe(st.session_state.df_dilr)
    
    with tabs[2]:
        st.markdown("""
        <div class="table-container">
            <div class="table-title">🔢 Quantitative Aptitude</div>
        """, unsafe_allow_html=True)
        st.markdown(render_styled_table(st.session_state.df_qa), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("✏️ Edit QA Syllabus"):
            if has_editor:
                edited = data_editor_fn(st.session_state.df_qa, key="qa_edit", use_container_width=True)
                st.session_state.df_qa = edited
            else:
                st.dataframe(st.session_state.df_qa)

elif page == "📊 Difficulty Analysis":
    st.markdown('<div class="section-header">📊 Difficulty Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="table-container">
            <div class="table-title">📈 Topic Difficulty & Mastery Mapping</div>
        """, unsafe_allow_html=True)
        st.markdown(render_styled_table(st.session_state.df_difficulty), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("✏️ Edit Difficulty Data"):
            if has_editor:
                edited = data_editor_fn(st.session_state.df_difficulty, key="diff_edit", use_container_width=True)
                st.session_state.df_difficulty = edited
            else:
                st.dataframe(st.session_state.df_difficulty)
    
    with col2:
        # Difficulty Distribution
        st.markdown("""
        <div class="table-container">
            <div class="table-title">📊 Distribution</div>
        """, unsafe_allow_html=True)
        
        diff_counts = st.session_state.df_difficulty["Level"].value_counts()
        for level in ["Easy", "Moderate", "Hard"]:
            count = diff_counts.get(level, 0)
            color = "#38ef7d" if level == "Easy" else "#f7b733" if level == "Moderate" else "#eb3349"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: #fff;">{level}</span>
                <span style="background: {color}; color: #fff; padding: 5px 15px; border-radius: 15px; font-weight: 600;">{count}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Average Mastery
        avg_mastery = st.session_state.df_difficulty["Mastery %"].mean()
        st.markdown(f"""
        <div class="table-container" style="margin-top: 20px;">
            <div class="table-title">🎯 Average Mastery</div>
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 3rem; font-weight: 700; color: {'#38ef7d' if avg_mastery >= 70 else '#f7b733' if avg_mastery >= 50 else '#eb3349'};">{avg_mastery:.0f}%</div>
                <div style="color: #a0aec0; font-size: 0.85rem; margin-top: 10px;">Across all topics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "📅 3-Month Plan":
    st.markdown('<div class="section-header">📅 12-Week Study Plan</div>', unsafe_allow_html=True)
    
    # Progress Overview
    completed = int(st.session_state.df_plan["Completed?"].sum())
    total_weeks = len(st.session_state.df_plan)
    
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.1)); border-radius: 20px; padding: 30px; margin-bottom: 30px; text-align: center;">
        <div style="font-size: 1rem; color: #a0aec0; text-transform: uppercase; letter-spacing: 2px;">Plan Progress</div>
        <div style="font-size: 4rem; font-weight: 800; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 10px 0;">{completed}/{total_weeks}</div>
        <div style="color: #e2e8f0;">weeks completed</div>
        {render_progress_bar(int(completed/total_weeks*100))}
    </div>
    """, unsafe_allow_html=True)
    
    # Week Cards
    col1, col2 = st.columns(2)
    
    for idx, row in st.session_state.df_plan.iterrows():
        with col1 if idx % 2 == 0 else col2:
            completed_class = "completed" if row["Completed?"] else ""
            check_icon = "✓" if row["Completed?"] else "○"
            check_color = "#38ef7d" if row["Completed?"] else "#a0aec0"
            border_color = "#38ef7d" if row["Completed?"] else "rgba(255,255,255,0.1)"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid {border_color}; border-left: 4px solid {check_color};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #4facfe; margin-bottom: 5px;">{row["Week"]}</div>
                        <div style="color: #a0aec0; font-size: 0.8rem; margin-bottom: 10px;">{row["Start Date"]} - {row["End Date"]}</div>
                        <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5;">{row["Target"]}</div>
                    </div>
                    <span style="color: {check_color}; font-size: 1.8rem; font-weight: 700;">{check_icon}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("✏️ Edit Study Plan"):
        if has_editor:
            edited = data_editor_fn(st.session_state.df_plan, key="plan_edit", use_container_width=True)
            st.session_state.df_plan = edited
        else:
            st.dataframe(st.session_state.df_plan)

elif page == "📝 Practice Tracker":
    st.markdown('<div class="section-header">📝 Practice Tracker</div>', unsafe_allow_html=True)
    
    # Quick Stats
    if len(st.session_state.df_tracker) > 0:
        total_qs = st.session_state.df_tracker["No. of Questions"].sum()
        total_correct = st.session_state.df_tracker["Correct"].sum()
        avg_acc = st.session_state.df_tracker["Accuracy %"].mean()
        reviewed = st.session_state.df_tracker["Reviewed?"].sum()
    else:
        total_qs = total_correct = avg_acc = reviewed = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [
        ("Total Questions", total_qs, "📝"),
        ("Correct Answers", total_correct, "✅"),
        ("Avg Accuracy", f"{avg_acc:.1f}%", "🎯"),
        ("Sessions Reviewed", reviewed, "📖")
    ]
    
    for col, (label, value, icon) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div class="tracker-stat">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div class="tracker-stat-value">{value}</div>
                <div class="tracker-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tracker Table
    st.markdown("""
    <div class="table-container">
        <div class="table-title">📋 Practice Sessions</div>
    """, unsafe_allow_html=True)
    
    if len(st.session_state.df_tracker) > 0:
        st.markdown(render_styled_table(st.session_state.df_tracker), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #a0aec0;">
            <div style="font-size: 3rem; margin-bottom: 15px;">📝</div>
            <div>No practice sessions yet. Add your first entry below!</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add New Entry
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="table-container">
        <div class="table-title">➕ Add New Practice Session</div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_date = st.date_input("Date", datetime.now())
        new_section = st.selectbox("Section", ["QA", "VARC", "DILR"])
    
    with col2:
        new_topic = st.text_input("Topic", placeholder="e.g., Arithmetic, RC")
        new_questions = st.number_input("No. of Questions", min_value=1, value=10)
    
    with col3:
        new_correct = st.number_input("Correct", min_value=0, value=8)
        new_time = st.text_input("Time Taken", placeholder="e.g., 30 min")
    
    if st.button("➕ Add Practice Session", use_container_width=True):
        wrong = new_questions - new_correct
        accuracy = (new_correct / new_questions) * 100 if new_questions > 0 else 0
        
        new_row = pd.DataFrame([{
            "Date": str(new_date),
            "Section": new_section,
            "Topic": new_topic,
            "No. of Questions": new_questions,
            "Correct": new_correct,
            "Wrong": wrong,
            "Accuracy %": accuracy,
            "Time Taken": new_time,
            "Reviewed?": False
        }])
        
        st.session_state.df_tracker = pd.concat([st.session_state.df_tracker, new_row], ignore_index=True)
        st.success("Practice session added!")
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Edit existing data
    with st.expander("✏️ Edit Tracker Data"):
        if has_editor:
            edited = data_editor_fn(st.session_state.df_tracker, key="tracker_edit", use_container_width=True, num_rows="dynamic")
            st.session_state.df_tracker = edited
        else:
            st.dataframe(st.session_state.df_tracker)

elif page == "⬇️ Export Data":
    st.markdown('<div class="section-header">⬇️ Export Your Data</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 10px;">💾 Save Your Progress</div>
        <div>Download your complete planner data as Excel or CSV files to backup your progress or use offline.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="table-container">
            <div class="table-title">📊 Complete Export (Excel)</div>
            <div style="color: #a0aec0; margin-bottom: 20px;">Download all sheets in a single Excel file</div>
        """, unsafe_allow_html=True)
        
        dfs = {
            "VARC": st.session_state.df_varc,
            "DILR": st.session_state.df_dilr,
            "QA": st.session_state.df_qa,
            "Difficulty": st.session_state.df_difficulty,
            "3-Month-Plan": st.session_state.df_plan,
            "Tracker": st.session_state.df_tracker
        }
        
        try:
            excel_bytes = to_excel_bytes(dfs)
            st.download_button(
                "⬇️ Download Complete Excel",
                data=excel_bytes,
                file_name=f"CAT_Planner_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel export error: {e}")
            st.info("Install openpyxl: pip install openpyxl")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="table-container">
            <div class="table-title">📄 Individual CSV Export</div>
            <div style="color: #a0aec0; margin-bottom: 20px;">Download specific sheets as CSV files</div>
        """, unsafe_allow_html=True)
        
        sheet_selection = st.selectbox(
            "Select Sheet",
            list(dfs.keys()),
            label_visibility="collapsed"
        )
        
        csv_bytes = dfs[sheet_selection].to_csv(index=False).encode("utf-8")
        st.download_button(
            f"⬇️ Download {sheet_selection}.csv",
            data=csv_bytes,
            file_name=f"{sheet_selection}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Preview
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="table-container">
        <div class="table-title">👁️ Data Preview</div>
    """, unsafe_allow_html=True)
    
    preview_tabs = st.tabs(list(dfs.keys()))
    for tab, (name, df) in zip(preview_tabs, dfs.items()):
        with tab:
            st.dataframe(df, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 40px 0 20px 0; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;">
    <div style="color: #a0aec0; font-size: 0.85rem;">
        Made with ❤️ for CAT Aspirants | 
        <span style="color: #667eea;">CAT Planner Pro</span> 2024
    </div>
</div>
""", unsafe_allow_html=True)

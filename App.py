import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CAT Planner Dashboard", layout="wide")

# ---------------------
# Helper: initial data
# ---------------------
def get_initial_syllabus():
    varc = [
        ("Reading Comprehension", "Economy, Psychology, Philosophy, Technology, History, Abstract RCs", "Inference, Main idea, Tone, Strengthen/Weaken"),
        ("Para Jumbles", "Mandatory pairs, Pronoun linkage, Chronological order", "4–5 sentence PJs"),
        ("Odd One Out", "Theme mismatch, Link-breaking", "TITA OOO questions"),
        ("Para Completion", "Logical continuation, Ending-sentence identification", "Final-sentence prediction"),
        ("Paragraph Summary", "Remove examples, key idea extraction", "20–40 word summaries")
    ]
    dilr = [
        ("Arrangements & Ordering", "Linear, Circular, Ranking, Mixed-variable puzzles", "Mixed puzzle sets"),
        ("Selection & Distribution", "Committee selection, People-object assignment", "Constraint-based distribution"),
        ("Games & Tournaments", "Round-robin, Knockouts, Points table reasoning", "6-8 variable tournament sets"),
        ("Set Theory", "2-set, 3-set venn, Max/Min overlaps", "Venn + DI integration"),
        ("DI Charts & Tables", "Tables, Bar, Pie, Line, Caselets", "Calculation-heavy DI sets"),
        ("Logic Puzzles", "Binary logic, Truth–lie, Conditional logic", "Mixed DILR sets")
    ]
    qa = [
        ("Number System", "Divisibility, LCM–HCF, Remainders, Cyclicity, Base", "Modular arithmetic, Last-digit tricks"),
        ("Arithmetic", "Percentages, Ratio, Averages, TSD, Time & Work, Profit–Loss, Mixtures", "Fast methods, LCM approach"),
        ("Algebra", "Linear, Quadratic, Inequalities, Modulus, Logs, Exponents", "Wavy curve, root properties"),
        ("Geometry & Mensuration", "Triangles, Circles, Coordinate Geo, Mensuration", "Area/length relations, formulae"),
        ("Modern Math", "Permutation & Combination, Probability, Sets", "Restrictions, conditional prob")
    ]

    df_varc = pd.DataFrame(varc, columns=["Main Topic", "Sub-Topics", "Practice Focus"])
    df_dilr = pd.DataFrame(dilr, columns=["Main Topic", "Sub-Topics", "Practice Focus"])
    df_qa = pd.DataFrame(qa, columns=["Main Topic", "Sub-Topics", "Practice Focus"])

    # add studied columns
    df_varc["Studied?"] = False
    df_dilr["Studied?"] = False
    df_qa["Studied?"] = False

    return df_varc, df_dilr, df_qa

def get_initial_difficulty():
    rows = [
        ("VARC", "RC Abstract", "Hard", False),
        ("VARC", "Para Summary", "Easy", False),
        ("DILR", "Games/Tournaments", "Hard", False),
        ("DILR", "Tables/Charts", "Easy", False),
        ("QA", "Arithmetic", "Easy", False),
        ("QA", "Geometry", "Moderate", False),
        ("QA", "Probability", "Hard", False),
    ]
    df = pd.DataFrame(rows, columns=["Section", "Topic Category", "Level", "Studied?"])
    return df

def get_initial_plan():
    rows = [
        ("Week 1", "Percentages + 2 RCs/day + 1 DI Set", False),
        ("Week 2", "Ratio, Averages + PJ + DI Tables", False),
        ("Week 3", "TSD, Time & Work + Summary + Venn", False),
        ("Week 4", "Profit-Loss + Moderate RCs + Arrangements", False),
        ("Week 5", "Algebra basics + 3 RCs/day", False),
        ("Week 6", "Geometry basics + DI charts", False),
        ("Week 7", "Advanced Algebra + Hybrid sets", False),
        ("Week 8", "Tournaments + Abstract RC", False),
        ("Week 9", "P&C + Functions + Hard DI Sets", False),
        ("Week 10", "Full mocks (2/week)", False),
        ("Week 11", "Mock analysis + weak topic revision", False),
        ("Week 12", "Final mocks + strategy tuning", False),
    ]
    df = pd.DataFrame(rows, columns=["Week", "Target", "Completed?"])
    return df

def get_initial_tracker():
    df = pd.DataFrame(columns=["Date", "Section", "Topic", "No. of Questions", "Correct", "Wrong", "Accuracy %", "Time Taken", "Reviewed?"])
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
# Utility: excel export
# ---------------------
def to_excel_bytes(dfs: dict):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)
        writer.save()
    bio.seek(0)
    return bio.read()

# ---------------------
# Sidebar / Navigation
# ---------------------
st.sidebar.title("CAT Planner")
page = st.sidebar.radio("Go to", ["Syllabus", "Difficulty", "3-Month Plan", "Tracker", "Export / Settings"])

st.sidebar.markdown("---")
if st.sidebar.button("Reset all to defaults"):
    st.session_state.df_varc, st.session_state.df_dilr, st.session_state.df_qa = get_initial_syllabus()
    st.session_state.df_difficulty = get_initial_difficulty()
    st.session_state.df_plan = get_initial_plan()
    st.session_state.df_tracker = get_initial_tracker()
    st.sidebar.success("Reset complete")

# Quick actions
if st.sidebar.button("Mark all syllabus studied"):
    for df in ("df_varc", "df_dilr", "df_qa"):
        st.session_state[df]["Studied?"] = True
    st.sidebar.success("All syllabus items marked studied")
if st.sidebar.button("Unmark all studied"):
    for df in ("df_varc", "df_dilr", "df_qa"):
        st.session_state[df]["Studied?"] = False
    st.sidebar.success("All syllabus items unmarked")

# ---------------------
# Pages
# ---------------------
st.title("📚 CAT Planner Dashboard")

if page == "Syllabus":
    st.header("Syllabus — VARC / DILR / QA")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.subheader("VARC")
        edited_varc = st.experimental_data_editor(st.session_state.df_varc, key="varc_editor", num_rows="fixed")
        st.session_state.df_varc = edited_varc
    with col2:
        st.subheader("DILR")
        edited_dilr = st.experimental_data_editor(st.session_state.df_dilr, key="dilr_editor", num_rows="fixed")
        st.session_state.df_dilr = edited_dilr
    with col3:
        st.subheader("QA")
        edited_qa = st.experimental_data_editor(st.session_state.df_qa, key="qa_editor", num_rows="fixed")
        st.session_state.df_qa = edited_qa

    st.markdown("---")
    st.info("Tip: Use the 'Studied?' column checkboxes to track progress. You can edit any cell. Changes are stored while the Streamlit session is active.")

elif page == "Difficulty":
    st.header("Difficulty Mapping")
    edited_diff = st.experimental_data_editor(st.session_state.df_difficulty, key="diff_editor", num_rows="fixed")
    st.session_state.df_difficulty = edited_diff
    st.markdown("You can change levels (Easy/Moderate/Hard) or mark studied status here.")

elif page == "3-Month Plan":
    st.header("3-Month Study Plan (Weekly Targets)")
    edited_plan = st.experimental_data_editor(st.session_state.df_plan, key="plan_editor", num_rows="fixed")
    st.session_state.df_plan = edited_plan

    st.markdown("Use the Completed? checkbox to mark finished weeks. You can edit the 'Target' description if you customize the plan.")

elif page == "Tracker":
    st.header("Practice Question Tracker")
    st.markdown("Add rows below, edit cells, and press 'Save Tracker' to persist in session.")

    col_a, col_b = st.columns([3,1])
    with col_a:
        # editable tracker
        tracker_editable = st.experimental_data_editor(st.session_state.df_tracker, key="tracker_editor")
        st.session_state.df_tracker = tracker_editable
    with col_b:
        st.write("")
        if st.button("Add empty row"):
            st.session_state.df_tracker = pd.concat([st.session_state.df_tracker, pd.DataFrame([["", "", "", "", "", "", "", "", False]], columns=st.session_state.df_tracker.columns)], ignore_index=True)
            st.experimental_rerun()
        if st.button("Delete last row"):
            if len(st.session_state.df_tracker) > 0:
                st.session_state.df_tracker = st.session_state.df_tracker.iloc[:-1]
                st.experimental_rerun()

    st.markdown("Use 'Reviewed?' column as checkbox after you analyze questions.")

elif page == "Export / Settings":
    st.header("Export / Settings")
    st.markdown("Download the current planner as an Excel file (multiple sheets) or CSV for each table.")

    dfs = {
        "VARC": st.session_state.df_varc,
        "DILR": st.session_state.df_dilr,
        "QA": st.session_state.df_qa,
        "Difficulty": st.session_state.df_difficulty,
        "3-Month-Plan": st.session_state.df_plan,
        "Tracker": st.session_state.df_tracker
    }

    excel_bytes = to_excel_bytes(dfs)
    st.download_button("⬇️ Download Excel (All sheets)", data=excel_bytes, file_name="CAT_Planner.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("---")
    st.write("Download single sheet as CSV:")
    cols = list(dfs.keys())
    sel = st.selectbox("Select sheet to download", cols)
    csv_bytes = dfs[sel].to_csv(index=False).encode("utf-8")
    st.download_button(f"⬇️ Download {sel}.csv", data=csv_bytes, file_name=f"{sel}.csv", mime="text/csv")

    st.markdown("---")
    st.write("Local persistence note: This app keeps changes in your browser session. To permanently store files, download them using the buttons above.")

# Footer / quick stats
st.markdown("---")
total_items = len(st.session_state.df_varc) + len(st.session_state.df_dilr) + len(st.session_state.df_qa)
studied_count = st.session_state.df_varc["Studied?"].sum() + st.session_state.df_dilr["Studied?"].sum() + st.session_state.df_qa["Studied?"].sum()
col1, col2, col3 = st.columns(3)
col1.metric("Syllabus items", total_items)
col2.metric("Studied items", int(studied_count))
col3.metric("Tracker rows", len(st.session_state.df_tracker))

# app.py - CAT Planner Pro with Persistent Database
import streamlit as st
import pandas as pd
import sqlite3
import json
from io import BytesIO
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DB_PATH = "cat_planner.db"

class Database:
    """Centralized Database Manager for CAT Planner"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Syllabus table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS syllabus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT NOT NULL,
                main_topic TEXT NOT NULL,
                sub_topics TEXT,
                practice_focus TEXT,
                confidence INTEGER DEFAULT 50,
                priority TEXT DEFAULT 'Medium',
                studied INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Difficulty mapping table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS difficulty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT NOT NULL,
                topic_category TEXT NOT NULL,
                level TEXT DEFAULT 'Moderate',
                studied INTEGER DEFAULT 0,
                mastery INTEGER DEFAULT 50,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Study plan table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER NOT NULL,
                week_label TEXT NOT NULL,
                target TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                start_date TEXT,
                end_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Practice tracker table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS practice_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                section TEXT NOT NULL,
                topic TEXT NOT NULL,
                questions INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0,
                wrong INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0,
                time_taken TEXT,
                reviewed INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Mock tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mock_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                test_name TEXT NOT NULL,
                varc_score REAL DEFAULT 0,
                varc_percentile REAL DEFAULT 0,
                dilr_score REAL DEFAULT 0,
                dilr_percentile REAL DEFAULT 0,
                qa_score REAL DEFAULT 0,
                qa_percentile REAL DEFAULT 0,
                total_score REAL DEFAULT 0,
                overall_percentile REAL DEFAULT 0,
                time_taken TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                target_value INTEGER DEFAULT 0,
                achieved_value INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        
        # Check if tables are empty and populate with default data
        cursor.execute("SELECT COUNT(*) FROM syllabus")
        if cursor.fetchone()[0] == 0:
            self._populate_default_syllabus(cursor)
        
        cursor.execute("SELECT COUNT(*) FROM difficulty")
        if cursor.fetchone()[0] == 0:
            self._populate_default_difficulty(cursor)
        
        cursor.execute("SELECT COUNT(*) FROM study_plan")
        if cursor.fetchone()[0] == 0:
            self._populate_default_plan(cursor)
        
        conn.commit()
        conn.close()
    
    def _populate_default_syllabus(self, cursor):
        """Populate default syllabus data"""
        varc = [
            ("VARC", "Reading Comprehension", "Economy, Psychology, Philosophy, Technology, History, Abstract RCs", "Inference, Main idea, Tone, Strengthen/Weaken", 70, "High"),
            ("VARC", "Para Jumbles", "Mandatory pairs, Pronoun linkage, Chronological order", "4–5 sentence PJs", 60, "Medium"),
            ("VARC", "Odd One Out", "Theme mismatch, Link-breaking", "TITA OOO questions", 55, "Medium"),
            ("VARC", "Para Completion", "Logical continuation, Ending-sentence identification", "Final-sentence prediction", 50, "Low"),
            ("VARC", "Paragraph Summary", "Remove examples, key idea extraction", "20–40 word summaries", 65, "High")
        ]
        
        dilr = [
            ("DILR", "Arrangements & Ordering", "Linear, Circular, Ranking, Mixed-variable puzzles", "Mixed puzzle sets", 70, "High"),
            ("DILR", "Selection & Distribution", "Committee selection, People-object assignment", "Constraint-based distribution", 62, "Medium"),
            ("DILR", "Games & Tournaments", "Round-robin, Knockouts, Points table reasoning", "6-8 variable tournament sets", 45, "High"),
            ("DILR", "Set Theory", "2-set, 3-set venn, Max/Min overlaps", "Venn + DI integration", 58, "Medium"),
            ("DILR", "DI Charts & Tables", "Tables, Bar, Pie, Line, Caselets", "Calculation-heavy DI sets", 68, "Medium"),
            ("DILR", "Logic Puzzles", "Binary logic, Truth–lie, Conditional logic", "Mixed DILR sets", 52, "High")
        ]
        
        qa = [
            ("QA", "Number System", "Divisibility, LCM–HCF, Remainders, Cyclicity, Base", "Modular arithmetic, Last-digit tricks", 75, "High"),
            ("QA", "Arithmetic", "Percentages, Ratio, Averages, TSD, Time & Work, Profit–Loss, Mixtures", "Fast methods, LCM approach", 80, "High"),
            ("QA", "Algebra", "Linear, Quadratic, Inequalities, Modulus, Logs, Exponents", "Wavy curve, root properties", 65, "Medium"),
            ("QA", "Geometry & Mensuration", "Triangles, Circles, Coordinate Geo, Mensuration", "Area/length relations, formulae", 55, "Medium"),
            ("QA", "Modern Math", "Permutation & Combination, Probability, Sets", "Restrictions, conditional prob", 48, "High")
        ]
        
        for item in varc + dilr + qa:
            cursor.execute('''
                INSERT INTO syllabus (section, main_topic, sub_topics, practice_focus, confidence, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', item)
    
    def _populate_default_difficulty(self, cursor):
        """Populate default difficulty data"""
        data = [
            ("VARC", "RC Abstract", "Hard", 0, 45),
            ("VARC", "RC Inference", "Moderate", 0, 60),
            ("VARC", "Para Summary", "Easy", 0, 75),
            ("VARC", "Para Jumbles", "Moderate", 0, 58),
            ("DILR", "Games/Tournaments", "Hard", 0, 42),
            ("DILR", "Arrangements", "Moderate", 0, 65),
            ("DILR", "Tables/Charts", "Easy", 0, 78),
            ("DILR", "Venn Diagrams", "Moderate", 0, 55),
            ("QA", "Arithmetic", "Easy", 0, 82),
            ("QA", "Algebra", "Moderate", 0, 68),
            ("QA", "Geometry", "Hard", 0, 50),
            ("QA", "Number System", "Moderate", 0, 70),
            ("QA", "P&C/Probability", "Hard", 0, 45),
        ]
        
        for item in data:
            cursor.execute('''
                INSERT INTO difficulty (section, topic_category, level, studied, mastery)
                VALUES (?, ?, ?, ?, ?)
            ''', item)
    
    def _populate_default_plan(self, cursor):
        """Populate default study plan"""
        base_date = datetime.now()
        weeks = [
            (1, "Week 1", "Percentages + 2 RCs/day + 1 DI Set"),
            (2, "Week 2", "Ratio, Averages + PJ + DI Tables"),
            (3, "Week 3", "TSD, Time & Work + Summary + Venn"),
            (4, "Week 4", "Profit-Loss + Moderate RCs + Arrangements"),
            (5, "Week 5", "Algebra basics + 3 RCs/day"),
            (6, "Week 6", "Geometry basics + DI charts"),
            (7, "Week 7", "Advanced Algebra + Hybrid sets"),
            (8, "Week 8", "Tournaments + Abstract RC"),
            (9, "Week 9", "P&C + Functions + Hard DI Sets"),
            (10, "Week 10", "Full mocks (2/week)"),
            (11, "Week 11", "Mock analysis + weak topic revision"),
            (12, "Week 12", "Final mocks + strategy tuning"),
        ]
        
        for week_num, label, target in weeks:
            start = (base_date + timedelta(days=(week_num - 1) * 7)).strftime("%Y-%m-%d")
            end = (base_date + timedelta(days=(week_num * 7) - 1)).strftime("%Y-%m-%d")
            cursor.execute('''
                INSERT INTO study_plan (week_number, week_label, target, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (week_num, label, target, start, end))
    
    # =========================
    # SYLLABUS OPERATIONS
    # =========================
    
    def get_syllabus(self, section: str = None) -> pd.DataFrame:
        """Get syllabus data"""
        conn = self.get_connection()
        if section:
            df = pd.read_sql_query(
                "SELECT * FROM syllabus WHERE section = ? ORDER BY id",
                conn, params=(section,)
            )
        else:
            df = pd.read_sql_query("SELECT * FROM syllabus ORDER BY section, id", conn)
        conn.close()
        return df
    
    def update_syllabus(self, id: int, **kwargs):
        """Update syllabus item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [id]
        
        cursor.execute(f'''
            UPDATE syllabus SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def add_syllabus_topic(self, section: str, main_topic: str, sub_topics: str = "", 
                           practice_focus: str = "", confidence: int = 50, priority: str = "Medium"):
        """Add new syllabus topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO syllabus (section, main_topic, sub_topics, practice_focus, confidence, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (section, main_topic, sub_topics, practice_focus, confidence, priority))
        conn.commit()
        conn.close()
    
    def delete_syllabus_topic(self, id: int):
        """Delete syllabus topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM syllabus WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    def mark_syllabus_studied(self, section: str = None, studied: bool = True):
        """Mark all syllabus items as studied/not studied"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if section:
            cursor.execute("UPDATE syllabus SET studied = ? WHERE section = ?", (int(studied), section))
        else:
            cursor.execute("UPDATE syllabus SET studied = ?", (int(studied),))
        conn.commit()
        conn.close()
    
    # =========================
    # DIFFICULTY OPERATIONS
    # =========================
    
    def get_difficulty(self) -> pd.DataFrame:
        """Get difficulty data"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM difficulty ORDER BY section, id", conn)
        conn.close()
        return df
    
    def update_difficulty(self, id: int, **kwargs):
        """Update difficulty item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [id]
        
        cursor.execute(f'''
            UPDATE difficulty SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def add_difficulty_item(self, section: str, topic_category: str, level: str = "Moderate", mastery: int = 50):
        """Add difficulty item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO difficulty (section, topic_category, level, mastery)
            VALUES (?, ?, ?, ?)
        ''', (section, topic_category, level, mastery))
        conn.commit()
        conn.close()
    
    def delete_difficulty_item(self, id: int):
        """Delete difficulty item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM difficulty WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    # =========================
    # STUDY PLAN OPERATIONS
    # =========================
    
    def get_study_plan(self) -> pd.DataFrame:
        """Get study plan data"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM study_plan ORDER BY week_number", conn)
        conn.close()
        return df
    
    def update_study_plan(self, id: int, **kwargs):
        """Update study plan item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [id]
        
        cursor.execute(f'''
            UPDATE study_plan SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def toggle_week_completed(self, id: int):
        """Toggle week completion status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE study_plan SET completed = NOT completed WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    # =========================
    # PRACTICE TRACKER OPERATIONS
    # =========================
    
    def get_practice_tracker(self, limit: int = None) -> pd.DataFrame:
        """Get practice tracker data"""
        conn = self.get_connection()
        query = "SELECT * FROM practice_tracker ORDER BY date DESC, id DESC"
        if limit:
            query += f" LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def add_practice_session(self, date: str, section: str, topic: str, questions: int, 
                             correct: int, time_taken: str = "", notes: str = ""):
        """Add practice session"""
        wrong = questions - correct
        accuracy = (correct / questions * 100) if questions > 0 else 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO practice_tracker (date, section, topic, questions, correct, wrong, accuracy, time_taken, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, section, topic, questions, correct, wrong, accuracy, time_taken, notes))
        conn.commit()
        conn.close()
    
    def update_practice_session(self, id: int, **kwargs):
        """Update practice session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Recalculate accuracy if questions or correct changed
        if 'questions' in kwargs or 'correct' in kwargs:
            cursor.execute("SELECT questions, correct FROM practice_tracker WHERE id = ?", (id,))
            row = cursor.fetchone()
            questions = kwargs.get('questions', row['questions'])
            correct = kwargs.get('correct', row['correct'])
            kwargs['wrong'] = questions - correct
            kwargs['accuracy'] = (correct / questions * 100) if questions > 0 else 0
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [id]
        
        cursor.execute(f'''
            UPDATE practice_tracker SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def delete_practice_session(self, id: int):
        """Delete practice session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM practice_tracker WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    def toggle_reviewed(self, id: int):
        """Toggle reviewed status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE practice_tracker SET reviewed = NOT reviewed WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    # =========================
    # MOCK TEST OPERATIONS
    # =========================
    
    def get_mock_tests(self) -> pd.DataFrame:
        """Get mock tests data"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM mock_tests ORDER BY date DESC", conn)
        conn.close()
        return df
    
    def add_mock_test(self, date: str, test_name: str, varc_score: float, varc_percentile: float,
                      dilr_score: float, dilr_percentile: float, qa_score: float, qa_percentile: float,
                      time_taken: str = "", notes: str = ""):
        """Add mock test"""
        total_score = varc_score + dilr_score + qa_score
        overall_percentile = (varc_percentile + dilr_percentile + qa_percentile) / 3
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mock_tests (date, test_name, varc_score, varc_percentile, dilr_score, dilr_percentile,
                                   qa_score, qa_percentile, total_score, overall_percentile, time_taken, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, test_name, varc_score, varc_percentile, dilr_score, dilr_percentile,
              qa_score, qa_percentile, total_score, overall_percentile, time_taken, notes))
        conn.commit()
        conn.close()
    
    def delete_mock_test(self, id: int):
        """Delete mock test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mock_tests WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    
    # =========================
    # ANALYTICS & STATS
    # =========================
    
    def get_dashboard_stats(self) -> dict:
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Syllabus stats
        cursor.execute("SELECT COUNT(*) as total, SUM(studied) as studied FROM syllabus")
        row = cursor.fetchone()
        stats['total_topics'] = row['total']
        stats['studied_topics'] = row['studied'] or 0
        
        # Section-wise stats
        cursor.execute('''
            SELECT section, COUNT(*) as total, SUM(studied) as studied, AVG(confidence) as avg_confidence
            FROM syllabus GROUP BY section
        ''')
        stats['section_stats'] = {row['section']: dict(row) for row in cursor.fetchall()}
        
        # Study plan stats
        cursor.execute("SELECT COUNT(*) as total, SUM(completed) as completed FROM study_plan")
        row = cursor.fetchone()
        stats['total_weeks'] = row['total']
        stats['completed_weeks'] = row['completed'] or 0
        
        # Practice tracker stats
        cursor.execute('''
            SELECT COUNT(*) as sessions, SUM(questions) as total_questions, 
                   SUM(correct) as total_correct, AVG(accuracy) as avg_accuracy
            FROM practice_tracker
        ''')
        row = cursor.fetchone()
        stats['practice_sessions'] = row['sessions'] or 0
        stats['total_questions'] = row['total_questions'] or 0
        stats['total_correct'] = row['total_correct'] or 0
        stats['avg_accuracy'] = row['avg_accuracy'] or 0
        
        # Mock test stats
        cursor.execute('''
            SELECT COUNT(*) as total, AVG(overall_percentile) as avg_percentile,
                   MAX(overall_percentile) as max_percentile
            FROM mock_tests
        ''')
        row = cursor.fetchone()
        stats['total_mocks'] = row['total'] or 0
        stats['avg_percentile'] = row['avg_percentile'] or 0
        stats['max_percentile'] = row['max_percentile'] or 0
        
        # Low confidence topics
        cursor.execute('''
            SELECT section, main_topic, confidence FROM syllabus
            ORDER BY confidence ASC LIMIT 5
        ''')
        stats['weak_topics'] = [dict(row) for row in cursor.fetchall()]
        
        # Recent practice
        cursor.execute('''
            SELECT date, section, topic, accuracy FROM practice_tracker
            ORDER BY date DESC, id DESC LIMIT 5
        ''')
        stats['recent_practice'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return stats
    
    def get_section_analysis(self, section: str) -> dict:
        """Get detailed section analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        analysis = {}
        
        # Topic-wise stats
        cursor.execute('''
            SELECT main_topic, confidence, studied, priority FROM syllabus WHERE section = ?
        ''', (section,))
        analysis['topics'] = [dict(row) for row in cursor.fetchall()]
        
        # Practice stats for section
        cursor.execute('''
            SELECT topic, COUNT(*) as sessions, AVG(accuracy) as avg_accuracy, SUM(questions) as total_qs
            FROM practice_tracker WHERE section = ? GROUP BY topic
        ''', (section,))
        analysis['practice_by_topic'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return analysis
    
    # =========================
    # SETTINGS OPERATIONS
    # =========================
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default
    
    def set_setting(self, key: str, value: str):
        """Set setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()
        conn.close()
    
    # =========================
    # EXPORT/IMPORT
    # =========================
    
    def export_all_data(self) -> dict:
        """Export all data as dictionary"""
        return {
            'syllabus': self.get_syllabus().to_dict('records'),
            'difficulty': self.get_difficulty().to_dict('records'),
            'study_plan': self.get_study_plan().to_dict('records'),
            'practice_tracker': self.get_practice_tracker().to_dict('records'),
            'mock_tests': self.get_mock_tests().to_dict('records'),
        }
    
    def export_to_excel(self) -> bytes:
        """Export all data to Excel"""
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine='openpyxl') as writer:
            self.get_syllabus().to_excel(writer, sheet_name='Syllabus', index=False)
            self.get_difficulty().to_excel(writer, sheet_name='Difficulty', index=False)
            self.get_study_plan().to_excel(writer, sheet_name='Study Plan', index=False)
            self.get_practice_tracker().to_excel(writer, sheet_name='Practice Tracker', index=False)
            self.get_mock_tests().to_excel(writer, sheet_name='Mock Tests', index=False)
        bio.seek(0)
        return bio.read()
    
    def reset_all_data(self):
        """Reset all data to defaults"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM syllabus")
        cursor.execute("DELETE FROM difficulty")
        cursor.execute("DELETE FROM study_plan")
        cursor.execute("DELETE FROM practice_tracker")
        cursor.execute("DELETE FROM mock_tests")
        cursor.execute("DELETE FROM daily_goals")
        
        self._populate_default_syllabus(cursor)
        self._populate_default_difficulty(cursor)
        self._populate_default_plan(cursor)
        
        conn.commit()
        conn.close()


# =============================================================================
# STREAMLIT APP CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="CAT Planner Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database():
    return Database()

db = get_database()

# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .section-header {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 25px;
    }
    
    .card {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 15px;
    }
    
    .card-title {
        color: #fff;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .badge {
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-easy { background: linear-gradient(90deg, #11998e, #38ef7d); color: #fff; }
    .badge-moderate { background: linear-gradient(90deg, #f093fb, #f5576c); color: #fff; }
    .badge-hard { background: linear-gradient(90deg, #eb3349, #f45c43); color: #fff; }
    .badge-high { background: #ef4444; color: #fff; }
    .badge-medium { background: #f59e0b; color: #fff; }
    .badge-low { background: #10b981; color: #fff; }
    
    .progress-bar-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .stat-mini {
        text-align: center;
        padding: 15px;
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
    }
    
    .stat-mini-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #4facfe;
    }
    
    .stat-mini-label {
        font-size: 0.7rem;
        color: #a0aec0;
        text-transform: uppercase;
    }
    
    .week-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 15px 20px;
        margin-bottom: 10px;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .week-card.completed {
        border-left-color: #38ef7d;
        background: rgba(56, 239, 125, 0.1);
    }
    
    .week-card:hover {
        transform: translateX(5px);
    }
    
    .table-container {
        background: rgba(255,255,255,0.03);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        overflow-x: auto;
    }
    
    .styled-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 8px;
    }
    
    .styled-table th {
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        color: #1a1a2e;
        padding: 12px 15px;
        text-align: left;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    .styled-table th:first-child { border-radius: 8px 0 0 8px; }
    .styled-table th:last-child { border-radius: 0 8px 8px 0; }
    
    .styled-table td {
        background: rgba(255,255,255,0.03);
        padding: 12px 15px;
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    
    .styled-table tr:hover td {
        background: rgba(255,255,255,0.08);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .success-btn > button {
        background: linear-gradient(90deg, #11998e, #38ef7d) !important;
    }
    
    .danger-btn > button {
        background: linear-gradient(90deg, #eb3349, #f45c43) !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_badge_html(text, badge_type="default"):
    badge_class = f"badge-{str(badge_type).lower()}"
    return f'<span class="badge {badge_class}">{text}</span>'

def render_progress_bar(percentage, color="#667eea"):
    return f'''
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: {min(percentage, 100)}%; background: {color};"></div>
    </div>
    '''

def render_styled_table(df, exclude_cols=None):
    """Render styled HTML table"""
    if exclude_cols is None:
        exclude_cols = ['id', 'created_at', 'updated_at', 'notes']
    
    display_df = df.drop(columns=[c for c in exclude_cols if c in df.columns], errors='ignore')
    
    html = '<table class="styled-table"><thead><tr>'
    for col in display_df.columns:
        html += f'<th>{col.replace("_", " ").title()}</th>'
    html += '</tr></thead><tbody>'
    
    for _, row in display_df.iterrows():
        html += '<tr>'
        for col in display_df.columns:
            val = row[col]
            cell = str(val)
            
            # Format special columns
            if col in ['studied', 'completed', 'reviewed']:
                cell = '✅' if val else '⬜'
            elif col == 'level':
                cell = get_badge_html(val, val)
            elif col == 'priority':
                cell = get_badge_html(val, val)
            elif col in ['confidence', 'mastery', 'accuracy']:
                color = '#38ef7d' if val >= 75 else '#f7b733' if val >= 50 else '#ef4444'
                cell = f'<span style="color:{color}; font-weight:600;">{val:.0f}%</span>'
            elif 'percentile' in col.lower():
                cell = f'{val:.1f}%ile'
            
            html += f'<td>{cell}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3rem;">🎯</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #4facfe; margin-top: 10px;">CAT Planner Pro</div>
        <div style="color: #a0aec0; font-size: 0.8rem;">Persistent • Smart • Beautiful</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📚 Syllabus", "📊 Difficulty", "📅 Study Plan", 
         "📝 Practice", "📈 Mock Tests", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats
    stats = db.get_dashboard_stats()
    progress = int((stats['studied_topics'] / stats['total_topics']) * 100) if stats['total_topics'] > 0 else 0
    
    st.markdown(f"""
    <div class="card">
        <div style="color: #a0aec0; font-size: 0.75rem; text-transform: uppercase;">Overall Progress</div>
        <div style="font-size: 2rem; font-weight: 700; color: #4facfe; margin: 8px 0;">{progress}%</div>
        {render_progress_bar(progress)}
        <div style="color: #a0aec0; font-size: 0.75rem; margin-top: 8px;">
            {stats['studied_topics']}/{stats['total_topics']} topics studied
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown('<div style="color: #a0aec0; font-size: 0.75rem; margin-bottom: 10px;">⚡ QUICK ACTIONS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ All", help="Mark all studied", use_container_width=True):
            db.mark_syllabus_studied(studied=True)
            st.rerun()
    with col2:
        if st.button("✗ All", help="Unmark all", use_container_width=True):
            db.mark_syllabus_studied(studied=False)
            st.rerun()
    
    st.markdown("---")
    
    # Database info
    st.markdown(f"""
    <div style="color: #4a5568; font-size: 0.7rem; text-align: center;">
        💾 SQLite Database<br>
        📁 {DB_PATH}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGES
# =============================================================================

if page == "🏠 Dashboard":
    st.markdown('<div class="section-header">🏠 Dashboard</div>', unsafe_allow_html=True)
    
    stats = db.get_dashboard_stats()
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("📚", "Topics Studied", f"{stats['studied_topics']}/{stats['total_topics']}", 
         f"{int(stats['studied_topics']/stats['total_topics']*100)}%" if stats['total_topics'] > 0 else "0%"),
        ("📅", "Weeks Done", f"{stats['completed_weeks']}/{stats['total_weeks']}", 
         f"{12 - stats['completed_weeks']} remaining"),
        ("📝", "Practice Sessions", stats['practice_sessions'], 
         f"{stats['total_questions']} questions"),
        ("🎯", "Avg Accuracy", f"{stats['avg_accuracy']:.1f}%", 
         f"{stats['total_correct']} correct"),
    ]
    
    for col, (icon, label, value, sub) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div style="color: #a0aec0; font-size: 0.8rem;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section progress
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card"><div class="card-title">📊 Section Progress</div>', unsafe_allow_html=True)
        
        section_colors = {"VARC": "#667eea", "DILR": "#f093fb", "QA": "#4facfe"}
        
        for section, data in stats['section_stats'].items():
            pct = int((data['studied'] / data['total']) * 100) if data['total'] > 0 else 0
            conf = data['avg_confidence'] or 0
            color = section_colors.get(section, "#667eea")
            
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="color: #fff; font-weight: 600;">{section}</span>
                    <span style="color: {color}; font-weight: 700;">{pct}%</span>
                </div>
                <div style="color: #a0aec0; font-size: 0.8rem; margin-bottom: 5px;">
                    {data['studied']}/{data['total']} topics • {conf:.0f}% avg confidence
                </div>
                {render_progress_bar(pct, color)}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><div class="card-title">🔥 Weak Topics</div>', unsafe_allow_html=True)
        
        for topic in stats['weak_topics']:
            conf = topic['confidence']
            color = '#ef4444' if conf < 50 else '#f7b733' if conf < 70 else '#38ef7d'
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 8px;">
                <div>
                    <div style="color: #fff; font-size: 0.9rem;">{topic['main_topic']}</div>
                    <div style="color: #a0aec0; font-size: 0.7rem;">{topic['section']}</div>
                </div>
                <span style="color: {color}; font-weight: 600;">{conf}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent practice
    if stats['recent_practice']:
        st.markdown('<div class="card"><div class="card-title">📝 Recent Practice</div>', unsafe_allow_html=True)
        
        cols = st.columns(len(stats['recent_practice']))
        for col, practice in zip(cols, stats['recent_practice']):
            with col:
                acc_color = '#38ef7d' if practice['accuracy'] >= 75 else '#f7b733' if practice['accuracy'] >= 50 else '#ef4444'
                st.markdown(f"""
                <div class="stat-mini">
                    <div style="color: #a0aec0; font-size: 0.7rem;">{practice['date']}</div>
                    <div style="color: #fff; font-size: 0.85rem; margin: 5px 0;">{practice['topic']}</div>
                    <div style="color: {acc_color}; font-size: 1.2rem; font-weight: 700;">{practice['accuracy']:.0f}%</div>
                    <div style="color: #a0aec0; font-size: 0.7rem;">{practice['section']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


elif page == "📚 Syllabus":
    st.markdown('<div class="section-header">📚 Syllabus Manager</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📖 View All", "🗣️ VARC", "🧩 DILR", "🔢 QA", "➕ Add Topic"])
    
    with tabs[0]:
        df = db.get_syllabus()
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.markdown(render_styled_table(df), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    for i, section in enumerate(["VARC", "DILR", "QA"], 1):
        with tabs[i]:
            df = db.get_syllabus(section)
            
            st.markdown(f'<div class="card"><div class="card-title">{section} Topics</div>', unsafe_allow_html=True)
            
            for _, row in df.iterrows():
                studied_icon = "✅" if row['studied'] else "⬜"
                conf_color = '#38ef7d' if row['confidence'] >= 75 else '#f7b733' if row['confidence'] >= 50 else '#ef4444'
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="padding: 10px 0;">
                        <div style="color: #fff; font-weight: 600;">{row['main_topic']} {studied_icon}</div>
                        <div style="color: #a0aec0; font-size: 0.8rem;">{row['sub_topics']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    new_conf = st.slider(
                        "Confidence", 0, 100, int(row['confidence']),
                        key=f"conf_{section}_{row['id']}",
                        label_visibility="collapsed"
                    )
                    if new_conf != row['confidence']:
                        db.update_syllabus(row['id'], confidence=new_conf)
                        st.rerun()
                
                with col3:
                    studied = st.checkbox(
                        "Studied", value=bool(row['studied']),
                        key=f"studied_{section}_{row['id']}"
                    )
                    if studied != bool(row['studied']):
                        db.update_syllabus(row['id'], studied=int(studied))
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tabs[4]:
        st.markdown('<div class="card"><div class="card-title">➕ Add New Topic</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            new_section = st.selectbox("Section", ["VARC", "DILR", "QA"])
            new_topic = st.text_input("Main Topic")
            new_subtopics = st.text_area("Sub-Topics")
        
        with col2:
            new_focus = st.text_area("Practice Focus")
            new_conf = st.slider("Initial Confidence", 0, 100, 50)
            new_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        if st.button("➕ Add Topic", use_container_width=True):
            if new_topic:
                db.add_syllabus_topic(new_section, new_topic, new_subtopics, new_focus, new_conf, new_priority)
                st.success(f"Added: {new_topic}")
                st.rerun()
            else:
                st.error("Please enter a topic name")
        
        st.markdown('</div>', unsafe_allow_html=True)


elif page == "📊 Difficulty":
    st.markdown('<div class="section-header">📊 Difficulty Mapping</div>', unsafe_allow_html=True)
    
    df = db.get_difficulty()
    
    # Stats cards
    col1, col2, col3 = st.columns(3)
    
    level_counts = df['level'].value_counts()
    for col, level, color in zip([col1, col2, col3], 
                                  ["Easy", "Moderate", "Hard"],
                                  ["#38ef7d", "#f7b733", "#ef4444"]):
        with col:
            count = level_counts.get(level, 0)
            st.markdown(f"""
            <div class="metric-card" style="text-align: center; border: 2px solid {color};">
                <div style="font-size: 2.5rem; font-weight: 700; color: {color};">{count}</div>
                <div class="metric-label">{level}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    st.markdown(render_styled_table(df), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Edit section
    with st.expander("✏️ Edit Difficulty Data"):
        for _, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{row['section']}** - {row['topic_category']}")
            
            with col2:
                new_level = st.selectbox(
                    "Level", ["Easy", "Moderate", "Hard"],
                    index=["Easy", "Moderate", "Hard"].index(row['level']),
                    key=f"level_{row['id']}",
                    label_visibility="collapsed"
                )
                if new_level != row['level']:
                    db.update_difficulty(row['id'], level=new_level)
                    st.rerun()
            
            with col3:
                new_mastery = st.number_input(
                    "Mastery", 0, 100, int(row['mastery']),
                    key=f"mastery_{row['id']}",
                    label_visibility="collapsed"
                )
                if new_mastery != row['mastery']:
                    db.update_difficulty(row['id'], mastery=new_mastery)
                    st.rerun()
            
            with col4:
                studied = st.checkbox(
                    "Done", value=bool(row['studied']),
                    key=f"diff_studied_{row['id']}"
                )
                if studied != bool(row['studied']):
                    db.update_difficulty(row['id'], studied=int(studied))
                    st.rerun()


elif page == "📅 Study Plan":
    st.markdown('<div class="section-header">📅 12-Week Study Plan</div>', unsafe_allow_html=True)
    
    df = db.get_study_plan()
    completed = int(df['completed'].sum())
    total = len(df)
    
    # Progress header
    st.markdown(f"""
    <div class="card" style="text-align: center;">
        <div style="font-size: 3rem; font-weight: 800; color: #667eea;">{completed}/{total}</div>
        <div style="color: #a0aec0; margin: 10px 0;">Weeks Completed</div>
        {render_progress_bar(int(completed/total*100) if total > 0 else 0)}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Week cards
    col1, col2 = st.columns(2)
    
    for i, row in df.iterrows():
        with col1 if i % 2 == 0 else col2:
            is_completed = bool(row['completed'])
            completed_class = "completed" if is_completed else ""
            icon = "✅" if is_completed else "⬜"
            
            st.markdown(f"""
            <div class="week-card {completed_class}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="color: #4facfe; font-weight: 700; font-size: 1.1rem;">{row['week_label']}</div>
                        <div style="color: #a0aec0; font-size: 0.8rem; margin: 5px 0;">
                            {row['start_date']} → {row['end_date']}
                        </div>
                        <div style="color: #e2e8f0; font-size: 0.9rem;">{row['target']}</div>
                    </div>
                    <span style="font-size: 1.5rem;">{icon}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Toggle Week {row['week_number']}", key=f"toggle_week_{row['id']}", use_container_width=True):
                db.toggle_week_completed(row['id'])
                st.rerun()


elif page == "📝 Practice":
    st.markdown('<div class="section-header">📝 Practice Tracker</div>', unsafe_allow_html=True)
    
    df = db.get_practice_tracker()
    
    # Stats
    if len(df) > 0:
        total_qs = int(df['questions'].sum())
        total_correct = int(df['correct'].sum())
        avg_acc = df['accuracy'].mean()
        reviewed = int(df['reviewed'].sum())
    else:
        total_qs = total_correct = reviewed = 0
        avg_acc = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    for col, (icon, label, value) in zip([col1, col2, col3, col4], [
        ("📝", "Questions", total_qs),
        ("✅", "Correct", total_correct),
        ("🎯", "Avg Accuracy", f"{avg_acc:.1f}%"),
        ("📖", "Reviewed", reviewed)
    ]):
        with col:
            st.markdown(f"""
            <div class="stat-mini">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div class="stat-mini-value">{value}</div>
                <div class="stat-mini-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add new session
    with st.expander("➕ Add Practice Session", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_date = st.date_input("Date", datetime.now())
            new_section = st.selectbox("Section", ["QA", "VARC", "DILR"])
        
        with col2:
            new_topic = st.text_input("Topic", placeholder="e.g., Arithmetic")
            new_questions = st.number_input("Total Questions", 1, 100, 10)
        
        with col3:
            new_correct = st.number_input("Correct", 0, 100, 8)
            new_time = st.text_input("Time Taken", placeholder="30 min")
        
        if st.button("➕ Add Session", use_container_width=True):
            if new_topic:
                db.add_practice_session(
                    str(new_date), new_section, new_topic, 
                    new_questions, new_correct, new_time
                )
                st.success("Session added!")
                st.rerun()
            else:
                st.error("Please enter a topic")
    
    # Sessions table
    if len(df) > 0:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 Practice Sessions</div>', unsafe_allow_html=True)
        st.markdown(render_styled_table(df), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Delete option
        with st.expander("🗑️ Delete Sessions"):
            session_to_delete = st.selectbox(
                "Select session to delete",
                df['id'].tolist(),
                format_func=lambda x: f"ID {x}: {df[df['id']==x]['date'].values[0]} - {df[df['id']==x]['topic'].values[0]}"
            )
            if st.button("🗑️ Delete Selected", use_container_width=True):
                db.delete_practice_session(session_to_delete)
                st.success("Deleted!")
                st.rerun()
    else:
        st.info("No practice sessions yet. Add your first one above!")


elif page == "📈 Mock Tests":
    st.markdown('<div class="section-header">📈 Mock Test Tracker</div>', unsafe_allow_html=True)
    
    df = db.get_mock_tests()
    
    # Add new mock test
    with st.expander("➕ Add Mock Test", expanded=len(df) == 0):
        col1, col2 = st.columns(2)
        
        with col1:
            mock_date = st.date_input("Test Date", datetime.now(), key="mock_date")
            mock_name = st.text_input("Test Name", placeholder="e.g., IMS SimCAT 1")
            
            st.markdown("**VARC**")
            varc_score = st.number_input("VARC Score", 0.0, 100.0, 0.0, key="varc_score")
            varc_pct = st.number_input("VARC Percentile", 0.0, 100.0, 0.0, key="varc_pct")
        
        with col2:
            mock_time = st.text_input("Time Taken", placeholder="2h 45m")
            mock_notes = st.text_area("Notes", placeholder="Key learnings...")
            
            st.markdown("**DILR**")
            dilr_score = st.number_input("DILR Score", 0.0, 100.0, 0.0, key="dilr_score")
            dilr_pct = st.number_input("DILR Percentile", 0.0, 100.0, 0.0, key="dilr_pct")
        
        st.markdown("**QA**")
        col1, col2 = st.columns(2)
        with col1:
            qa_score = st.number_input("QA Score", 0.0, 100.0, 0.0, key="qa_score")
        with col2:
            qa_pct = st.number_input("QA Percentile", 0.0, 100.0, 0.0, key="qa_pct")
        
        if st.button("➕ Add Mock Test", use_container_width=True):
            if mock_name:
                db.add_mock_test(
                    str(mock_date), mock_name, varc_score, varc_pct,
                    dilr_score, dilr_pct, qa_score, qa_pct, mock_time, mock_notes
                )
                st.success("Mock test added!")
                st.rerun()
            else:
                st.error("Please enter test name")
    
    # Display mock tests
    if len(df) > 0:
        # Summary stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-value">{len(df)}</div>
                <div class="metric-label">Total Mocks</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_pct = df['overall_percentile'].mean()
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-value">{avg_pct:.1f}%</div>
                <div class="metric-label">Avg Percentile</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            max_pct = df['overall_percentile'].max()
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-value">{max_pct:.1f}%</div>
                <div class="metric-label">Best Percentile</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Table
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        display_cols = ['date', 'test_name', 'varc_score', 'varc_percentile', 
                       'dilr_score', 'dilr_percentile', 'qa_score', 'qa_percentile',
                       'total_score', 'overall_percentile']
        st.markdown(render_styled_table(df[display_cols + ['id']].rename(columns={'id': 'id'})), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Trend chart
        if len(df) >= 2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-title">📈 Percentile Trend</div>', unsafe_allow_html=True)
            
            chart_df = df.sort_values('date')[['date', 'varc_percentile', 'dilr_percentile', 'qa_percentile', 'overall_percentile']]
            chart_df = chart_df.set_index('date')
            st.line_chart(chart_df)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No mock tests yet. Add your first one above!")


elif page == "⚙️ Settings":
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card"><div class="card-title">💾 Export Data</div>', unsafe_allow_html=True)
        
        try:
            excel_data = db.export_to_excel()
            st.download_button(
                "⬇️ Download Excel (All Data)",
                data=excel_data,
                file_name=f"CAT_Planner_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel export failed: {e}")
            st.info("Install openpyxl: pip install openpyxl")
        
        # Individual CSVs
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("**Individual CSV Exports:**")
        
        tables = {
            "Syllabus": db.get_syllabus(),
            "Difficulty": db.get_difficulty(),
            "Study Plan": db.get_study_plan(),
            "Practice": db.get_practice_tracker(),
            "Mock Tests": db.get_mock_tests()
        }
        
        for name, df in tables.items():
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"📄 {name}.csv",
                data=csv,
                file_name=f"{name.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"csv_{name}"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><div class="card-title">🔧 Database Management</div>', unsafe_allow_html=True)
        
        # Database stats
        stats = db.get_dashboard_stats()
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border-radius: 10px; padding: 15px; margin-bottom: 15px;">
            <div style="color: #a0aec0; font-size: 0.8rem;">Database Statistics</div>
            <div style="margin-top: 10px; color: #e2e8f0; font-size: 0.9rem;">
                • Syllabus topics: {stats['total_topics']}<br>
                • Practice sessions: {stats['practice_sessions']}<br>
                • Mock tests: {stats['total_mocks']}<br>
                • Total questions practiced: {stats['total_questions']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Danger zone
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; 
                    border-radius: 10px; padding: 15px; margin-top: 20px;">
            <div style="color: #ef4444; font-weight: 600; margin-bottom: 10px;">⚠️ Danger Zone</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Reset All Data", use_container_width=True, type="primary"):
            st.warning("Are you sure? This will delete all your data!")
            
        if st.button("⚠️ Confirm Reset", use_container_width=True):
            db.reset_all_data()
            st.success("All data has been reset to defaults!")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Database file info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
        <div class="card-title">ℹ️ Database Information</div>
        <div style="color: #a0aec0; font-size: 0.9rem;">
            <p><strong>Location:</strong> {Path(DB_PATH).absolute()}</p>
            <p><strong>Type:</strong> SQLite 3</p>
            <p>Your data is stored locally in this SQLite database file. 
            Back up this file to preserve your data across reinstalls.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div style="text-align: center; padding: 40px 0 20px 0; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;">
    <div style="color: #a0aec0; font-size: 0.85rem;">
        Made with ❤️ for CAT Aspirants | 
        <span style="color: #667eea;">CAT Planner Pro</span> v2.0
    </div>
    <div style="color: #4a5568; font-size: 0.7rem; margin-top: 5px;">
        💾 Persistent SQLite Database • 📊 Real-time Analytics • 🎨 Modern UI
    </div>
</div>
""", unsafe_allow_html=True)

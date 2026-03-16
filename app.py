import streamlit as st
import sys
import os
import traceback
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import config
from modules import database

# Inisialisasi database
database.init_database()
database.seed_default_project()
database.seed_batch_data()
database.seed_commodities()

st.set_page_config(
    page_title="ARTHARAYA Enterprise Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    word-break: break-word;
    white-space: normal;
    line-height: 1.3;
}
.sidebar .sidebar-content {
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

try:
    with open('assets/style.css', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

# ===== SESSION STATE =====
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.page = "Login"
    st.session_state.page_file = None
    st.session_state.project_id = None
    st.session_state.project_name = None

# ===== HALAMAN LOGIN (PERFECT CENTER) =====
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    /* Sembunyikan elemen default */
    section[data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }

    /* Reset total */
    .stApp {
        background: #101622;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
        padding: 0;
    }
    .main .block-container {
        padding: 0 !important;
        max-width: none !important;
        width: 100%;
    }

    /* Card login */
    .login-card {
        background: #0f172a;
        border-radius: 1.5rem;
        padding: 2.5rem 2rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        border: 1px solid #1e293b;
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }

    /* Header */
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-header h1 {
        color: #f1f5f9;
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .login-header p {
        color: #94a3b8;
        font-size: 0.9rem;
    }

    /* Footer */
    .login-footer {
        text-align: center;
        margin-top: 1.5rem;
        color: #94a3b8;
        font-size: 0.75rem;
    }
    .login-footer a {
        color: #0f49bd;
        text-decoration: underline;
    }

    /* Form input */
    .stTextInput > div, .stSelectbox > div, .stButton > div {
        width: 100%;
    }
    .stTextInput input, .stSelectbox select {
        background-color: #1e293b;
        border: 1px solid #334155;
        color: #f1f5f9;
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        width: 100%;
        font-size: 0.9rem;
    }
    .stButton button {
        background-color: #0f49bd;
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #1e3a8a;
        box-shadow: 0 4px 12px rgba(15, 73, 189, 0.3);
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="login-header">
            <h1>Artharaya Group</h1>
            <p>Enterprise Resource Portal</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username or Email", placeholder="e.g. j.doe@artharaya.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            role = st.selectbox("Pilih Role (Demo)", ["Superadmin", "Admin", "PMO", "Viewer"])
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        st.markdown("""
        <div class="login-footer">
            By signing in, you agree to our <a href="#">Acceptable Use Policy</a> and <a href="#">Data Security Protocols</a>.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted and username and password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = role
        st.session_state.page = "Executive Dashboard"
        st.session_state.page_file = "page_files/1_Executive_Dashboard.py"
        st.rerun()
    elif submitted:
        st.error("Username dan password harus diisi.")
    st.stop()

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("## 🏢 Artharaya Group")
    st.caption("Enterprise Dashboard v2.3")
    st.markdown(f"**User:** {st.session_state.username}  \n**Role:** {st.session_state.role}")
    st.markdown("---")

    projects = database.get_all_projects()
    if projects:
        project_names = [p['name'] for p in projects]
        if st.session_state.project_id is None:
            st.session_state.project_id = projects[0]['id']
            st.session_state.project_name = projects[0]['name']
        selected_project = st.selectbox(
            "Pilih Proyek",
            project_names,
            index=project_names.index(st.session_state.project_name) if st.session_state.project_name in project_names else 0
        )
        if selected_project != st.session_state.project_name:
            st.session_state.project_name = selected_project
            st.session_state.project_id = next(p['id'] for p in projects if p['name'] == selected_project)
            st.rerun()
    else:
        st.error("Tidak ada proyek.")
        st.stop()

    st.markdown("---")
    st.markdown("### Navigasi")

    menu = {
        "Executive": {
            "Executive Dashboard": "page_files/1_Executive_Dashboard.py",
            "One Page Finance": "page_files/21_One_Page_Finance.py",
            "Project Brief": "page_files/2_Project_Brief.py"
        },
        "Operations": {
            "Warehouse": "page_files/16_Warehouse.py",
            "Kios": "page_files/17_Kios.py",
            "Online": "page_files/18_Online.py",
            "Batch Tracking": "page_files/4_Batch_Tracking.py",
            "Inventory Overview": "page_files/5_Inventory.py",
            "Shrinkage (Telur Pecah)": "page_files/27_Shrinkage.py"
        },
        "Finance": {
            "Payment Tracking": "page_files/12_Payment_Tracking.py",
            "Cash Deposit": "page_files/22_Cash_Deposit.py",
            "Budget Allocation": "page_files/8_Budget_Allocation.py",
            "Operational Expenses": "page_files/25_Operational_Expenses.py",
            "Budget vs Actual": "page_files/27_Budget_vs_Actual.py"
        },
        "HR & Admin": {
            "HR Management": "page_files/19_HR_Management.py",
            "Project Data Entry": "page_files/20_Project_Data_Entry.py",
            "Inventory Adjustment": "page_files/23_Inventory_Adjustment.py",
            "New Project": "page_files/24_New_Project.py",
            "Commodities": "page_files/26_Commodities.py"
        },
        "Reporting": {
            "Sales Dashboard": "page_files/11_Sales_Dashboard.py",
            "Market Intelligence": "page_files/10_Market_Intelligence.py",
            "Risk Management": "page_files/9_Risk_Management.py",
            "SOP Procedures": "page_files/14_SOP_Procedures.py",
            "Reporting Center": "page_files/15_Reporting_Center.py"
        }
    }

    role = st.session_state.role
    if role == "Viewer":
        allowed = ["Executive"]
    elif role == "PMO":
        allowed = ["Executive", "Operations", "Finance", "Reporting"]
    elif role == "Admin":
        allowed = ["Operations", "Finance", "HR & Admin"]
    else:
        allowed = list(menu.keys())

    filtered_menu = {k: v for k, v in menu.items() if k in allowed}
    categories = list(filtered_menu.keys())

    default_cat_index = 0
    for i, cat in enumerate(categories):
        if st.session_state.page in filtered_menu[cat]:
            default_cat_index = i
            break

    selected_category = st.selectbox("Kategori", categories, index=default_cat_index, key="cat_select")
    pages_in_cat = filtered_menu[selected_category]
    page_names = list(pages_in_cat.keys())
    default_page_index = 0
    if st.session_state.page in page_names:
        default_page_index = page_names.index(st.session_state.page)
    selected_page = st.radio("Halaman", page_names, index=default_page_index, key="page_select")

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.session_state.page_file = pages_in_cat[selected_page]
        st.rerun()

    st.markdown("---")
    st.info(
        f"**Project ID:** {st.session_state.project_id}\n\n"
        f"**Project:** {st.session_state.project_name}\n\n"
        f"**Periode:** Mar 2026"
    )
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 10px;'>"
        "Powered by Agung Basuki<br>Version 2.3"
        "</p>",
        unsafe_allow_html=True
    )
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ===== LOAD HALAMAN =====
if st.session_state.page_file and os.path.exists(st.session_state.page_file):
    try:
        with open(st.session_state.page_file, encoding='utf-8-sig') as f:
            content = f.read()
        exec(content)
    except UnicodeDecodeError:
        try:
            with open(st.session_state.page_file, encoding='latin-1') as f:
                content = f.read()
            exec(content)
        except Exception as e:
            st.error(f"❌ Gagal memuat halaman (encoding): {e}")
            st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"❌ Gagal memuat halaman: {e}")
        st.code(traceback.format_exc())
else:
    st.error(f"Halaman {st.session_state.page} tidak ditemukan.")
    if os.path.exists("page_files"):
        st.write("File yang tersedia di folder page_files:")
        for f in sorted(os.listdir("page_files")):
            st.write(f"- {f}")
    else:
        st.error("Folder page_files tidak ditemukan. Pastikan file halaman sudah dipindahkan.")
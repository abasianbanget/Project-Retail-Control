# ===== HALAMAN LOGIN (DENGAN PATTERN PREMIUM) =====
if not st.session_state.logged_in:
    st.markdown("""
        <style>
        /* Reset total */
        html, body, .stApp, .main {
            margin: 0 !important;
            padding: 0 !important;
            height: 100% !important;
            width: 100% !important;
            overflow: hidden !important;
        }
        .stApp {
            background: #101622;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        /* Pattern halus (grid) untuk latar belakang */
        .stApp::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
        }
        section[data-testid="stSidebar"] { display: none; }
        header[data-testid="stHeader"] { display: none; }
        footer { display: none; }
        .main .block-container {
            padding: 0 !important;
            max-width: none !important;
        }

        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            max-width: 380px;
            margin: 0 auto;
            padding: 1rem;
            transform: translateY(-25px); /* Naikkan 25px */
            position: relative;
            z-index: 2;
        }
        .login-card {
            background: #0f172a;
            border-radius: 0.75rem;
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);
            width: 100%;
            border: 1px solid #1e293b;
            overflow: hidden;
        }
        .login-header {
            padding: 1.5rem 1.5rem 0.5rem 1.5rem;
            text-align: center;
        }
        .login-header h1 {
            color: #f1f5f9;
            font-size: 2.2rem; /* Diperbesar */
            margin-bottom: 0.25rem;
            font-weight: 600;
        }
        .login-header p {
            color: #94a3b8;
            font-size: 0.9rem;
            text-align: center;
        }
        .login-form {
            padding: 1.5rem;
        }
        .login-form .stTextInput > div,
        .login-form .stSelectbox > div,
        .login-form .stButton > div {
            width: 100%;
        }
        .login-form .stTextInput input,
        .login-form .stSelectbox select {
            background-color: #1e293b;
            border: 1px solid #334155;
            color: #f1f5f9;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            width: 100%;
            font-size: 1rem;
        }
        .login-form .stTextInput input::placeholder {
            color: #64748b;
        }
        .login-form .stButton button {
            background-color: #0f49bd;
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            font-weight: 600;
            font-size: 1rem;
            width: 100%;
            cursor: pointer;
            transition: background 0.2s;
        }
        .login-form .stButton button:hover {
            background-color: #0e3da0;
        }
        .login-footer {
            padding: 1rem 1.5rem 1.5rem 1.5rem;
            text-align: center;
            border-top: 1px solid #1e293b;
            color: #94a3b8;
            font-size: 0.75rem;
        }
        .login-footer a {
            color: #0f49bd;
            text-decoration: underline;
        }
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="stApp"><div class="login-container"><div class="login-card">', unsafe_allow_html=True)

    st.markdown("""
        <div class="login-header">
            <h1>Artharaya Group</h1>
            <p>Enterprise Resource Portal</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-form">', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="e.g. j.doe@artharaya.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        role = st.selectbox("Pilih Role (Demo)", ["Superadmin", "Admin", "PMO", "Viewer"])
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="login-footer">
            <p>By signing in, you agree to our <a href="#">Acceptable Use Policy</a> and <a href="#">Data Security Protocols</a>.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div></div></div>', unsafe_allow_html=True)

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
import streamlit as st
import requests
import json
import os

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_URL = os.getenv("CLAIMGUARD_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="ClaimGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1117 0%, #1a1d2e 100%);
    border-right: 1px solid #2a2d3e;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Main background */
.stApp {
    background: #f8f9fc;
}

/* Header */
.cg-header {
    background: linear-gradient(135deg, #0f1117 0%, #1e2235 60%, #2d3561 100%);
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.cg-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,179,237,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.cg-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #fff;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.cg-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
    font-weight: 300;
}
.cg-badge {
    display: inline-block;
    background: rgba(99,179,237,0.15);
    color: #63b3ed;
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* Cards */
.cg-card {
    background: #fff;
    border-radius: 14px;
    padding: 28px;
    border: 1px solid #e8eaf0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.cg-card h3 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: #1a202c;
    margin: 0 0 4px 0;
}
.cg-card-sub {
    color: #94a3b8;
    font-size: 0.82rem;
    margin-bottom: 20px;
}

/* Severity pill */
.pill-low    { background:#d1fae5; color:#065f46; border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.pill-medium { background:#fef3c7; color:#92400e; border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.pill-high   { background:#fee2e2; color:#991b1b; border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }

/* Damage row */
.dmg-row {
    display:flex; align-items:center; justify-content:space-between;
    padding: 12px 0;
    border-bottom: 1px solid #f1f3f8;
}
.dmg-row:last-child { border-bottom: none; }
.dmg-item { font-weight: 600; color: #1a202c; font-size: 0.9rem; }
.dmg-issue { color: #64748b; font-size: 0.82rem; margin-top: 2px; }
.dmg-cost { font-weight: 700; color: #2563eb; font-size: 0.95rem; }

/* Total bar */
.total-bar {
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
    border-radius: 12px;
    padding: 18px 24px;
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 8px;
}
.total-bar .label { color: #bfdbfe; font-size: 0.85rem; font-weight: 500; }
.total-bar .amount { color: #fff; font-size: 1.5rem; font-weight: 700; font-family: 'DM Serif Display', serif; }

/* Status chip */
.status-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f0fdf4; color: #166534;
    border: 1px solid #bbf7d0;
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.8rem; font-weight: 600;
}
.status-dot { width:7px; height:7px; background:#22c55e; border-radius:50%; display:inline-block; }

/* Auth forms */
.auth-container {
    max-width: 440px;
    margin: 60px auto;
    background: #fff;
    border-radius: 20px;
    padding: 40px;
    border: 1px solid #e8eaf0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.07);
}
.auth-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: #1a202c;
    margin-bottom: 4px;
}
.auth-sub { color: #94a3b8; font-size: 0.88rem; margin-bottom: 28px; }

/* Claim history row */
.claim-row {
    display:flex; align-items:center; justify-content:space-between;
    padding: 14px 0;
    border-bottom: 1px solid #f1f3f8;
}
.claim-row:last-child { border-bottom:none; }
.claim-id { font-weight:600; color:#2563eb; font-size:0.88rem; }
.claim-status { color:#64748b; font-size:0.82rem; }
.claim-url { color:#94a3b8; font-size:0.78rem; word-break:break-all; }

/* Step indicator */
.steps { display:flex; gap:8px; margin-bottom:24px; }
.step { flex:1; height:4px; border-radius:2px; background:#e2e8f0; }
.step.active { background:#2563eb; }
.step.done   { background:#22c55e; }
</style>
""", unsafe_allow_html=True)


# ─── Session state helpers ─────────────────────────────────────────────────────
def init_state():
    defaults = {
        "access_token": None,
        "refresh_token": None,
        "username": None,
        "page": "login",       # login | register | dashboard | upload | history
        "last_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}


def api_post(path, data=None, files=None, auth=False):
    headers = auth_headers() if auth else {}
    try:
        r = requests.post(
            f"{BASE_URL}{path}",
            data=data,
            files=files,
            headers=headers,
            timeout=60,
        )
        try:
            payload = r.json()
        except ValueError:
            payload = {"error": r.text or "Backend returned an invalid response."}
        return r.status_code, payload
    except requests.exceptions.ConnectionError:
        return 0, {"error": "Cannot reach the backend. Is Django running?"}
    except Exception as e:
        return 0, {"error": str(e)}


def api_get(path, auth=False):
    headers = auth_headers() if auth else {}
    try:
        r = requests.get(f"{BASE_URL}{path}", headers=headers, timeout=30)
        try:
            payload = r.json()
        except ValueError:
            payload = {"error": r.text or "Backend returned an invalid response."}
        return r.status_code, payload
    except requests.exceptions.ConnectionError:
        return 0, {"error": "Cannot reach the backend. Is Django running?"}
    except Exception as e:
        return 0, {"error": str(e)}


def normalize_claims_response(data):
    if isinstance(data, dict):
        claims = data.get("claims", [])
        return claims if isinstance(claims, list) else []
    if isinstance(data, list):
        return data
    return []


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='padding:10px 0 24px'>
            <div style='font-family:"DM Serif Display",serif;font-size:1.5rem;color:#fff;'>🛡️ ClaimGuard</div>
            <div style='color:#475569;font-size:0.78rem;margin-top:2px;'>AI-Powered Claims Review</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.access_token:
            st.markdown(f"""
            <div style='background:#1e2235;border-radius:10px;padding:12px 16px;margin-bottom:20px;'>
                <div style='color:#94a3b8;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;'>Logged in as</div>
                <div style='color:#e2e8f0;font-weight:600;margin-top:2px;'>{st.session_state.username}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📋  Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            if st.button("📤  New Claim", use_container_width=True):
                st.session_state.page = "upload"
                st.rerun()
            if st.button("🗂️  Claim History", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()

            st.markdown("<hr style='border-color:#2a2d3e;margin:20px 0;'>", unsafe_allow_html=True)

            if st.button("🚪  Log out", use_container_width=True):
                for k in ["access_token", "refresh_token", "username", "last_result"]:
                    st.session_state[k] = None
                st.session_state.page = "login"
                st.rerun()
        else:
            if st.button("🔐  Log In", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
            if st.button("✏️  Register", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

        st.markdown("""
        <div style='position:absolute;bottom:20px;left:16px;right:16px;'>
            <div style='color:#334155;font-size:0.72rem;text-align:center;'>v1.0 · ClaimGuard AI</div>
        </div>
        """, unsafe_allow_html=True)


# ─── Pages ────────────────────────────────────────────────────────────────────

def page_login():
    st.markdown("""
    <div class='auth-container'>
        <div class='auth-title'>Welcome back</div>
        <div class='auth-sub'>Sign in to your ClaimGuard account</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.container():
            st.markdown("<div style='background:#fff;border-radius:20px;padding:36px;border:1px solid #e8eaf0;box-shadow:0 8px 32px rgba(0,0,0,0.07);'>", unsafe_allow_html=True)
            st.markdown("<div style='font-family:\"DM Serif Display\",serif;font-size:1.9rem;color:#1a202c;margin-bottom:4px;'>Welcome back</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:#94a3b8;font-size:0.88rem;margin-bottom:24px;'>Sign in to your ClaimGuard account</div>", unsafe_allow_html=True)

            identifier = st.text_input("Username or Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            if st.button("Sign In →", use_container_width=True, type="primary"):
                if not identifier or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Authenticating..."):
                        status, data = api_post("/api/login/", data={
                            "email": identifier,
                            "password": password,
                        })
                    if status == 200 and "access" in data:
                        st.session_state.access_token = data["access"]
                        st.session_state.refresh_token = data.get("refresh")
                        st.session_state.username = identifier
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        msg = data.get("detail") or data.get("error") or "Login failed."
                        st.error(msg)

            st.markdown("<div style='text-align:center;margin-top:16px;color:#94a3b8;font-size:0.85rem;'>No account? <a href='#' style='color:#2563eb;' onclick='void(0)'>Register below</a></div>", unsafe_allow_html=True)
            if st.button("Create an account", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def page_register():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div style='background:#fff;border-radius:20px;padding:36px;border:1px solid #e8eaf0;box-shadow:0 8px 32px rgba(0,0,0,0.07);margin-top:40px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"DM Serif Display\",serif;font-size:1.9rem;color:#1a202c;margin-bottom:4px;'>Create account</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#94a3b8;font-size:0.88rem;margin-bottom:24px;'>Start reviewing claims with AI</div>", unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="johndoe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Min. 8 characters")

        if st.button("Create Account →", use_container_width=True, type="primary"):
            if not username or not email or not password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner("Creating your account..."):
                    status, data = api_post("/api/users/register/", data={
                        "username": username,
                        "email": email,
                        "password": password,
                    })
                if status in (200, 201):
                    st.success("Account created! Please log in.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    err = data.get("error") or json.dumps(data)
                    st.error(f"Registration failed: {err}")

        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def page_dashboard():
    st.markdown("""
    <div class='cg-header'>
        <div class='cg-badge'>Dashboard</div>
        <h1>🛡️ ClaimGuard AI</h1>
        <p>Upload before/after media and get an AI-powered damage assessment and cost estimate.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='cg-card' style='border-left:4px solid #2563eb;'>
            <div style='font-size:2rem;margin-bottom:8px;'>📤</div>
            <div style='font-family:"DM Serif Display",serif;font-size:1.1rem;color:#1a202c;'>Submit a Claim</div>
            <div style='color:#94a3b8;font-size:0.82rem;margin-top:4px;'>Upload before & after media for AI review</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("New Claim →", key="dash_upload"):
            st.session_state.page = "upload"
            st.rerun()

    with col2:
        st.markdown("""
        <div class='cg-card' style='border-left:4px solid #22c55e;'>
            <div style='font-size:2rem;margin-bottom:8px;'>🗂️</div>
            <div style='font-family:"DM Serif Display",serif;font-size:1.1rem;color:#1a202c;'>Claim History</div>
            <div style='color:#94a3b8;font-size:0.82rem;margin-top:4px;'>Browse all your past submissions</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View History →", key="dash_hist"):
            st.session_state.page = "history"
            st.rerun()

    with col3:
        st.markdown("""
        <div class='cg-card' style='border-left:4px solid #f59e0b;'>
            <div style='font-size:2rem;margin-bottom:8px;'>🤖</div>
            <div style='font-family:"DM Serif Display",serif;font-size:1.1rem;color:#1a202c;'>AI Workflow</div>
            <div style='color:#94a3b8;font-size:0.82rem;margin-top:4px;'>Validate → Compare → Estimate</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:0.8rem;color:#94a3b8;padding:4px 0;'>
            Powered by LangGraph + Groq
        </div>
        """, unsafe_allow_html=True)

    # Show last result if exists
    if st.session_state.last_result:
        st.markdown("<hr style='margin:24px 0;border-color:#e8eaf0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"DM Serif Display\",serif;font-size:1.3rem;color:#1a202c;margin-bottom:16px;'>Latest Claim Result</div>", unsafe_allow_html=True)
        render_result(st.session_state.last_result)


def page_upload():
    st.markdown("""
    <div class='cg-header'>
        <div class='cg-badge'>New Claim</div>
        <h1>Upload Media</h1>
        <p>Provide a reference (before) file and an incident (after) file. We'll handle the rest.</p>
    </div>
    """, unsafe_allow_html=True)

    # Step indicator
    st.markdown("""
    <div class='steps'>
        <div class='step done'></div>
        <div class='step active'></div>
        <div class='step'></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='cg-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"DM Serif Display\",serif;font-size:1.1rem;margin-bottom:4px;'>📷 Reference File</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#94a3b8;font-size:0.82rem;margin-bottom:16px;'>The <strong>before</strong> state — baseline / check-in media</div>", unsafe_allow_html=True)
        reference_file = st.file_uploader(
            "Upload reference", type=["jpg","jpeg","png","webp","mp4","mov","avi","mkv","webm"],
            key="ref_file", label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='cg-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"DM Serif Display\",serif;font-size:1.1rem;margin-bottom:4px;'>🔍 Incident File</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#94a3b8;font-size:0.82rem;margin-bottom:16px;'>The <strong>after</strong> state — current / check-out media</div>", unsafe_allow_html=True)
        incident_file = st.file_uploader(
            "Upload incident", type=["jpg","jpeg","png","webp","mp4","mov","avi","mkv","webm"],
            key="inc_file", label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Preview uploaded files
    if st.session_state.get('ref_file') and st.session_state.ref_file.type.startswith('image/'):
        st.markdown("### Reference Image Preview")
        st.image(st.session_state.ref_file)
    elif st.session_state.get('ref_file') and st.session_state.ref_file.type.startswith('video/'):
        st.markdown("### Reference Video Preview")
        st.video(st.session_state.ref_file)

    if st.session_state.get('inc_file') and st.session_state.inc_file.type.startswith('image/'):
        st.markdown("### Incident Image Preview")
        st.image(st.session_state.inc_file)
    elif st.session_state.get('inc_file') and st.session_state.inc_file.type.startswith('video/'):
        st.markdown("### Incident Video Preview")
        st.video(st.session_state.inc_file)

    with st.form("upload_form"):
        media_type = st.radio(
            "Media type",
            ["image", "video"],
            horizontal=True,
            help="Choose 'image' for photos, 'video' for video files."
        )

        submitted = st.form_submit_button("🚀  Analyse Claim", use_container_width=True, type="primary")

    if submitted:
        reference_file = st.session_state.get('ref_file')
        incident_file = st.session_state.get('inc_file')
        if not incident_file:
            st.error("Please upload the incident (after) file.")
        elif not reference_file:
            st.error("Please upload the reference (before) file.")
        else:
            with st.spinner("Running AI workflow — validate → compare → estimate..."):
                files = {
                    "media": (incident_file.name, incident_file.read(), incident_file.type),
                    "reference_media": (reference_file.name, reference_file.read(), reference_file.type),
                }
                status, data = api_post(
                    "/api/claims/uploads/",
                    data={"media_type": media_type},
                    files=files,
                    auth=True,
                )

            if status == 0:
                st.error(data.get("error"))
            elif "error" in data:
                st.error(data["error"])
            else:
                st.session_state.last_result = data
                st.success("Claim analysed successfully!")
                st.session_state.page = "dashboard"
                st.rerun()


def render_result(data: dict):
    wr = data.get("workflow_result", {})
    anomalies = wr.get("anamolies", [])
    total = wr.get("total_claim_value", 0)
    wstatus = wr.get("status", "—")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='cg-card'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;'>
            <div>
                <div style='font-family:"DM Serif Display",serif;font-size:1.2rem;color:#1a202c;'>Damage Report</div>
                <div style='color:#94a3b8;font-size:0.82rem;'>Claim #{data.get("claim_id","—")} · {data.get("media_type","—").capitalize()}</div>
            </div>
            <div class='status-chip'><span class='status-dot'></span>{wstatus}</div>
        </div>
        """, unsafe_allow_html=True)

        if anomalies:
            for a in anomalies:
                sev = a.get("severity", "Low")
                pill_class = f"pill-{sev.lower()}"
                cost = a.get("estimated_cost", 0)
                st.markdown(f"""
                <div class='dmg-row'>
                    <div>
                        <div class='dmg-item'>{a.get("item","Unknown item")}</div>
                        <div class='dmg-issue'>{a.get("issue","—")}</div>
                    </div>
                    <div style='display:flex;align-items:center;gap:12px;'>
                        <span class='{pill_class}'>{sev}</span>
                        <span class='dmg-cost'>${cost:.0f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#94a3b8;font-size:0.9rem;padding:16px 0;'>No anomalies detected.</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='total-bar' style='margin-top:16px;'>
            <span class='label'>Total Estimated Repair Cost</span>
            <span class='amount'>${total:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='cg-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"DM Serif Display\",serif;font-size:1.1rem;color:#1a202c;margin-bottom:16px;'>Claim Details</div>", unsafe_allow_html=True)

        def detail_row(label, value, color="#1a202c"):
            st.markdown(f"""
            <div style='margin-bottom:12px;'>
                <div style='color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.8px;'>{label}</div>
                <div style='color:{color};font-weight:600;font-size:0.9rem;margin-top:2px;word-break:break-all;'>{value}</div>
            </div>
            """, unsafe_allow_html=True)

        detail_row("Claim ID", f"#{data.get('claim_id','—')}")
        detail_row("Media Type", data.get("media_type","—").capitalize())
        detail_row("Status", wstatus, "#22c55e")
        detail_row("Items Found", str(len(anomalies)))
        detail_row("File Reference", data.get("image_url","—")[:40] + "..." if len(str(data.get("image_url",""))) > 40 else data.get("image_url","—"))

        # Raw JSON expander
        with st.expander("Raw JSON response"):
            st.json(data)
        st.markdown("</div>", unsafe_allow_html=True)


def page_history():
    st.markdown("""
    <div class='cg-header'>
        <div class='cg-badge'>History</div>
        <h1>Claim History</h1>
        <p>All claims submitted under your account.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading claims..."):
        status, data = api_get("/api/claims/uploads/", auth=True)

    if status == 0:
        st.error(data.get("error"))
        return
    if status == 401:
        st.error("Your session expired. Please sign in again.")
        for key in ["access_token", "refresh_token", "username", "last_result"]:
            st.session_state[key] = None
        st.session_state.page = "login"
        st.rerun()
    if isinstance(data, dict) and data.get("error"):
        st.error(data["error"])
        return

    claims = normalize_claims_response(data)

    if not claims:
        st.markdown("""
        <div class='cg-card' style='text-align:center;padding:48px;'>
            <div style='font-size:3rem;'>📭</div>
            <div style='font-family:"DM Serif Display",serif;font-size:1.3rem;color:#1a202c;margin-top:12px;'>No claims yet</div>
            <div style='color:#94a3b8;margin-top:6px;font-size:0.88rem;'>Submit your first claim to get started.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Submit a Claim →", type="primary"):
            st.session_state.page = "upload"
            st.rerun()
        return

    st.markdown(f"<div style='color:#64748b;font-size:0.88rem;margin-bottom:16px;'>{len(claims)} claim(s) found</div>", unsafe_allow_html=True)

    st.markdown("<div class='cg-card'>", unsafe_allow_html=True)
    for claim in claims:
        status_val = claim.get("status", "—")
        status_color = "#22c55e" if "complete" in status_val.lower() else "#f59e0b" if "process" in status_val.lower() else "#64748b"
        st.markdown(f"""
        <div class='claim-row'>
            <div>
                <div class='claim-id'>Claim #{claim.get("id","—")}</div>
                <div class='claim-url'>{claim.get("image_url","—")}</div>
            </div>
            <div style='text-align:right;'>
                <div style='display:inline-block;background:#f8fafc;border:1px solid #e2e8f0;border-radius:20px;padding:3px 12px;'>
                    <span style='color:{status_color};font-size:0.78rem;font-weight:600;'>{status_val}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─── App router ───────────────────────────────────────────────────────────────
render_sidebar()

if not st.session_state.access_token:
    if st.session_state.page == "register":
        page_register()
    else:
        page_login()
else:
    page = st.session_state.page
    if page == "dashboard":
        page_dashboard()
    elif page == "upload":
        page_upload()
    elif page == "history":
        page_history()
    else:
        page_dashboard()

import streamlit as st
import bcrypt

# --- Dummy user DB (can later link to DB)
USERS = {
    "admin": bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode(),
    "guest": bcrypt.hashpw("guestpass".encode(), bcrypt.gensalt()).decode()
}

def login():
    st.sidebar.subheader("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in USERS and bcrypt.checkpw(password.encode(), USERS[username].encode()):
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.sidebar.error("Invalid credentials")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None

import streamlit as st

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Settings"])

# --- Page Routing ---
if page == "Dashboard":
    st.title("📊 Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Revenue", "$12K", "+8%")
        st.line_chart([1, 3, 5, 2, 4])

    with col2:
        st.metric("Users", "1,200", "+4%")
        st.bar_chart([2, 5, 1, 6, 4])

elif page == "Settings":
    st.title("⚙️ Settings")
    st.write("Adjust preferences or view system info here.")
    st.checkbox("Enable dark mode")
    st.slider("Refresh interval (seconds)", 1, 60, 10)

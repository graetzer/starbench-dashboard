import streamlit as st

@st.dialog("Cast your vote")
def vote(item):
    st.write(f"Why is {item} your favorite?")
    reason = st.text_input("Because...")
    if st.button("Submit"):
        st.session_state.vote = {"item": item, "reason": reason}
        st.rerun()


if "login" not in st.session_state:
    # center company logo using columns
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://www.stardog.com/img/stardog-logo-optimized.svg", width=200)

    with st.form("login_form"):
        st.write("Specify credentials to login")
        endpoint = st.text_input("Stardog Endpoint", "https://doghouse.stardog.cloud:5820/")
        st.text_input("Database", "sb-dashboard", disabled=True)
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", placeholder="admin", type="password")

        # Every form must have a submit button.
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            press_login = st.form_submit_button("Login")
        with col2:
            use_local_data = st.form_submit_button("Demo Login")


        if press_login:

            if username is None or username.strip() == "" or password is None or password.strip() == "":
                st.warning("Please enter both username and password to login.")
                st.stop()

            st.session_state.login = {
                "endpoint": endpoint,
                "username": username,
                "password": password
            }
            st.rerun()
        
        if use_local_data:
            st.session_state.login = "offline"
            st.rerun()


else:
    # Define the pages
    main_page = st.Page("page_main.py", title="Main Dashboard", icon="📊")
    page_correlation = st.Page("page_correlation.py", title="Test Correlation", icon="🔍")
    page_changepoints = st.Page("page_changepoints.py", title="Change Points", icon="📉")

    # Set up navigation
    pg = st.navigation([main_page, page_correlation, page_changepoints])

    # Run the selected page
    pg.run()

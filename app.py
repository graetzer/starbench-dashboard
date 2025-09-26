import streamlit as st

@st.dialog("Cast your vote")
def vote(item):
    st.write(f"Why is {item} your favorite?")
    reason = st.text_input("Because...")
    if st.button("Submit"):
        st.session_state.vote = {"item": item, "reason": reason}
        st.rerun()

if "login" not in st.session_state:
    st.write("Specify credentials to login")

    with st.form("login_form"):
        endpoint = st.text_input("Stardog Endpoint", "https://doghouse.stardog.cloud:5820/")
        username = st.text_input("Username", "admin")
        password = st.text_input("Password", "admin", type="password")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state.login = {
                "endpoint": endpoint,
                "username": username,
                "password": password
            }
            st.rerun()        

else:
    # Define the pages
    main_page = st.Page("page_main.py", title="Dashboard Main Page", icon="🎈")
    page_correlation = st.Page("page_correlation.py", title="Test Correlation", icon="❄️")
    page_changepoints = st.Page("page_changepoints.py", title="Change Points", icon="🎉")

    # Set up navigation
    pg = st.navigation([main_page, page_correlation, page_changepoints])

    # Run the selected page
    pg.run()

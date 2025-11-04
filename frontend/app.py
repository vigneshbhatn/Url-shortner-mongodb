import streamlit as st
import requests
import time

# --- Page Configuration -----------------------------------------------
st.set_page_config(
    page_title="URL Shortener",
    page_icon="🔗",
    layout="wide"  # Use 'wide' layout for more space
)

# --- Define Backend URLs ----------------------------------------------
# We now have multiple endpoints to call
API_BASE_URL = "http://127.0.0.1:8000"
CREATE_URL_ENDPOINT = f"{API_BASE_URL}/shorten"
ADMIN_LINKS_ENDPOINT = f"{API_BASE_URL}/admin/links"
ADMIN_DELETE_ENDPOINT = f"{API_BASE_URL}/admin/"  # We will add the short_code
ADMIN_UPDATE_ENDPOINT = f"{API_BASE_URL}/admin/"  # We will add the short_code


# --- API Helper Functions ---------------------------------------------
# These functions will talk to our backend
# We use st.cache_data to cache the 'get' request
@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_all_links():
    """Fetch all links from the backend."""
    try:
        response = requests.get(ADMIN_LINKS_ENDPOINT)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching links: {response.json().get('detail')}")
            return []
    except requests.ConnectionError:
        st.error("Error: Could not connect to the backend. Is it running?")
        return []


def delete_link(short_code: str):
    """Delete a link by its short_code."""
    try:
        response = requests.delete(f"{ADMIN_DELETE_ENDPOINT}{short_code}")
        if response.status_code == 200:
            st.success(f"Deleted link '{short_code}' successfully!")
            st.cache_data.clear()  # Clear the cache so get_all_links re-runs
            time.sleep(0.5)  # Give a moment for the user to see the message
            st.rerun()  # Rerun the app to refresh the table
        else:
            st.error(f"Error deleting link: {response.json().get('detail')}")
    except requests.ConnectionError:
        st.error("Error: Could not connect to the backend.")


def update_link(short_code: str, new_target_url: str):
    """Update a link's target_url."""
    payload = {"target_url": new_target_url}
    try:
        response = requests.put(f"{ADMIN_UPDATE_ENDPOINT}{short_code}", json=payload)
        if response.status_code == 200:
            st.success(f"Updated link '{short_code}' successfully!")
            st.cache_data.clear()  # Clear the cache
            time.sleep(0.5)
            #st.rerun()  # Rerun the app to refresh
        elif response.status_code == 422:
            st.error("Error: Please enter a valid URL (e.g., 'https://...')")
        else:
            st.error(f"Error updating link: {response.json().get('detail')}")
    except requests.ConnectionError:
        st.error("Error: Could not connect to the backend.")


# --- App Title --------------------------------------------------------
st.title("🔗 URL Shortener")


# --- 1. Create New Link Section ---------------------------------------
st.header("Create a New Short URL")
with st.form(key="create_form"):
    long_url = st.text_input("Enter your long URL:", placeholder="https://www.google.com")
    submit_button = st.form_submit_button(label="Create Short URL")

if submit_button:
    if not long_url:
        st.warning("Please enter a URL first.")
    else:
        payload = {"target_url": long_url}
        try:
            response = requests.post(CREATE_URL_ENDPOINT, json=payload)
            if response.status_code == 200:
                data = response.json()
                short_url = data.get("short_url")
                st.success("Success! Here is your short URL:")
                st.code(short_url, language="text")
                st.cache_data.clear()  # Clear cache to refresh table below
                #st.rerun()
            elif response.status_code == 422:
                st.error("Error: Please enter a valid URL (e.g., 'https://...')")
            else:
                st.error(f"Error from backend: {response.json().get('detail', 'Unknown error')}")
        except requests.ConnectionError:
            st.error("Error: Could not connect to the backend.")

# --- 2. Manage Links Section ------------------------------------------
st.divider()
st.header("Manage Existing Links")

# Fetch data from our API helper
links = get_all_links()

if not links:
    st.info("No links found.")
else:
    # Build the interactive table
    # 1. Create the header
    cols = st.columns([2, 4, 2, 1])
    cols[0].write("**Short URL*")
    cols[1].write("**Original URL**")
    cols[2].write("**Update**")
    cols[3].write("**Delete**")
    st.divider()

    # 2. Iterate over data and create rows
    # 2. Iterate over data and create rows
    for link in links:
        # Get data for this row
        short_code = link['short_code']
        target_url = link['target_url']

        # --- THIS IS THE NEW LINE YOU NEED TO ADD ---
        # Build the full, clickable short URL
        full_short_url = f"{API_BASE_URL}/{short_code}"

        # Use columns for layout
        col1, col2, col3, col4 = st.columns([2, 4, 2, 1])

        # Column 1: Clickable Short URL
        # Use the new variable here
        col1.link_button(full_short_url, full_short_url)

        # Column 2: Original URL (with link)
        col2.link_button(target_url, target_url)

        # Column 3: Update Form (in an expander)
        with col3.expander("Edit"):
            with st.form(key=f"update_form_{short_code}"):
                new_url = st.text_input("New URL", value=target_url, key=f"txt_{short_code}")
                if st.form_submit_button("Update"):
                    update_link(short_code, new_url)


        # Column 4: Delete Button
        if col4.button("Delete", key=f"del_{short_code}"):
            delete_link(short_code)
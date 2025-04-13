import streamlit as st
import pandas as pd
import requests
import os

def load_data():
    """Fetches data from the server's /api/reports endpoint."""
    server_url = os.environ.get("SERVER_URL", "http://localhost:8000")
    api_endpoint = f"{server_url}/api/reports"
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if "reports" in data:
            return pd.DataFrame(data["reports"])
        else:
            st.error("Invalid data format received from the server.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the server: {e}")
        return pd.DataFrame()

st.title("Reports Database")
data = load_data()
st.dataframe(data)

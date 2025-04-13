import streamlit as st
import sqlite3
import pandas as pd

import main

main.main()

def load_data():
    conn = sqlite3.connect('reports.db')
    query = "SELECT * FROM reports"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("Reports Database")
data = load_data()
st.dataframe(data)

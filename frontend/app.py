import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("🧬 Upload PDB File")

uploaded_file = st.file_uploader("Upload a PDB file", type=["pdb"])

if uploaded_file and st.button("Upload"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    response = requests.post(f"{API_URL}/read-pdb-file/", files=files)

    if response.status_code == 200:
        st.success("✅ File uploaded successfully!")
        st.json(response.json())
    else:
        st.error("❌ Error uploading file")

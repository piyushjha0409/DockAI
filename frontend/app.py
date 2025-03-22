import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# App title and configuration
st.set_page_config(
    page_title="PDB Table Viewer",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 PDB File Table Viewer")
st.write("Upload a PDB file to view its atomic structure data as a table")

# Simple file uploader
uploaded_file = st.file_uploader("Upload a PDB file", type=["pdb", "ent", "pdbqt"])

if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")
    
    if st.button("Process PDB File"):
        with st.spinner("Reading PDB file..."):
            # Send the file to our simplified backend endpoint
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(f"{API_URL}/simple-pdb-table/", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display basic info
                st.subheader("File Information")
                st.metric("Number of atoms", result.get("row_count", 0))
                
                # Display header information if available
                if result.get("header"):
                    header = result.get("header")
                    st.subheader("PDB Header")
                    
                    info_cols = st.columns(3)
                    with info_cols[0]:
                        st.metric("PDB ID", header.get("identifier", "N/A"))
                    with info_cols[1]:
                        st.metric("Title", header.get("title", "N/A"))
                    with info_cols[2]:
                        st.metric("Resolution", f"{header.get('resolution', 'N/A')} Å" if header.get('resolution') else "N/A")
                
                # Display the atomic data table
                st.subheader("Atomic Structure Data")
                
                # Create DataFrame from the returned data
                if result.get("data"):
                    df = pd.DataFrame(result.get("data"))
                    
                    # Add column filters
                    if not df.empty:
                        column_selection = st.multiselect(
                            "Select columns to display",
                            options=df.columns.tolist(),
                            default=["chain_id", "residue_name", "residue_number", "atom_name", "x_coord", "y_coord", "z_coord"]
                        )
                        
                        if column_selection:
                            filtered_df = df[column_selection]
                            st.dataframe(filtered_df, use_container_width=True)
                        else:
                            st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("No atomic data found in the file")
                else:
                    st.error("No data returned from the server")
            else:
                st.error(f"Error processing file: {response.text}")

# Simple footer
st.markdown("---")
st.markdown("PDB Table Viewer | A simple tool to view PDB file data")
import streamlit as st
import requests
import io
import base64
from PIL import Image
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# App title and configuration
st.set_page_config(
    page_title="PDB Analysis Tool",
    page_icon="🧬",
    layout="wide"
)

# Function to display HTML content
def display_html_visualization(html_content):
    # Remove potentially problematic script tags for Streamlit
    html_content = html_content.replace("<script", "<!-- script").replace("</script>", "</script -->")
    st.components.v1.html(html_content, height=600, scrolling=True)

# Main page tabs
tab1, tab2 = st.tabs(["Structure Analysis", "Visualization"])

# Structure Analysis Tab
with tab1:
    st.header("📊 PDB Structure Analysis")
    
    uploaded_file = st.file_uploader("Upload a PDB file for analysis", type=["pdb", "ent"], key="analysis_uploader")
    
    if uploaded_file:
        st.success(f"File ready: {uploaded_file.name}")
        
        if st.button("Analyze Structure"):
            with st.spinner("Analyzing PDB structure..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_URL}/read-pdb-file/", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display structure summary
                    st.subheader("Structure Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Structure ID", result.get("structure_id", "N/A"))
                    col2.metric("Number of Chains", result.get("num_chains", 0))
                    col3.metric("Number of Residues", result.get("num_residues", 0))
                    col4.metric("Number of Atoms", result.get("num_atoms", 0))
                    
                    # Tabs for structural components
                    component_tabs = st.tabs(["Models", "Chains", "Residues", "Atoms"])
                    
                    with component_tabs[0]:
                        models_df = pd.DataFrame(result.get("models", []))
                        if not models_df.empty:
                            st.dataframe(models_df, use_container_width=True)
                        else:
                            st.info("No model data available")
                    
                    with component_tabs[1]:
                        chains_df = pd.DataFrame(result.get("chains", []))
                        if not chains_df.empty:
                            st.dataframe(chains_df, use_container_width=True)
                        else:
                            st.info("No chain data available")
                    
                    with component_tabs[2]:
                        residues_df = pd.DataFrame(result.get("residues", []))
                        if not residues_df.empty:
                            st.dataframe(residues_df, use_container_width=True)
                        else:
                            st.info("No residue data available")
                    
                    with component_tabs[3]:
                        atoms_df = pd.DataFrame(result.get("atoms", []))
                        if not atoms_df.empty:
                            if len(atoms_df) > 1000:
                                st.warning(f"Showing only 1000 of {len(atoms_df)} atoms")
                                st.dataframe(atoms_df.head(1000), use_container_width=True)
                            else:
                                st.dataframe(atoms_df, use_container_width=True)
                        else:
                            st.info("No atom data available")
                    
                    # Option to generate PDF report
                    if st.button("Generate PDF Report"):
                        with st.spinner("Creating PDF report..."):
                            # Direct file upload for PDF generation
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                            pdf_response = requests.post(
                                f"{API_URL}/generate_report/", 
                                files=files
                            )
                            
                            if pdf_response.status_code == 200:
                                # Display download link for PDF
                                pdf_data = pdf_response.content
                                st.download_button(
                                    label="Download PDF Report",
                                    data=pdf_data,
                                    file_name=f"{uploaded_file.name.split('.')[0]}_report.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.error(f"Error generating report: {pdf_response.text}")
                else:
                    st.error(f"Error analyzing structure: {response.text}")

# Visualization Tab
with tab2:
    st.header("🔬 PDB Visualization")
    
    uploaded_file = st.file_uploader("Upload a PDB file for visualization", type=["pdb", "ent"], key="viz_uploader")
    
    if uploaded_file:
        st.success(f"File ready: {uploaded_file.name}")
        
        # Visualization options in columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            viz_type = st.selectbox(
                "Visualization type",
                ["standard", "binding_site", "2d", "electrostatic"]
            )
            
            style = st.selectbox(
                "Style",
                ["cartoon", "stick", "sphere", "line"]
            )
        
        with col2:
            # Show binding residues input only when needed
            if viz_type == "binding_site":
                binding_residues = st.text_input(
                    "Binding residues (comma-separated)",
                    "A:45,A:46"
                )
                binding_list = [r.strip() for r in binding_residues.split(",")]
            else:
                binding_list = None
                
            # Color options
            background_color = st.color_picker("Background color", "#FFFFFF")
            
            # Only show opacity for 3D modes
            if viz_type in ["standard", "binding_site", "electrostatic"]:
                surface_opacity = st.slider("Surface opacity", 0.0, 1.0, 0.5, 0.1)
            else:
                surface_opacity = 0.5
        
        if st.button("Generate Visualization"):
            with st.spinner("Creating visualization..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                
                # Build parameters
                params = {
                    "visualization_type": viz_type,
                    "style": style,
                    "surface_opacity": surface_opacity,
                    "background_color": background_color,
                    "width": 800,
                    "height": 600
                }
                
                if binding_list:
                    params["binding_residues"] = binding_list
                
                # Make API request
                response = requests.post(
                    f"{API_URL}/visualize-pdb/",
                    files=files,
                    params=params
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("type") == "html":
                        st.subheader("3D Visualization")
                        display_html_visualization(result.get("content", ""))
                    
                    elif result.get("type") == "image":
                        st.subheader("2D Visualization")
                        image_data = base64.b64decode(result.get("content", ""))
                        image = Image.open(io.BytesIO(image_data))
                        st.image(image, use_column_width=True)
                    
                    # Visualization info
                    st.info(f"Visualization type: {result.get('visualization_type', 'Unknown')}")
                    
                    # Save image option for 2D visualizations
                    if result.get("type") == "image":
                        st.download_button(
                            label="Download Image",
                            data=result.get("content", ""),
                            file_name=f"{uploaded_file.name.split('.')[0]}_visualization.png",
                            mime="image/png"
                        )
                else:
                    st.error(f"Error generating visualization: {response.text}")

# Footer
st.markdown("---")
st.markdown("🧬 PDB Analysis Tool | Built with Streamlit + FastAPI")
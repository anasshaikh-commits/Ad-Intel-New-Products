import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io

# Page configuration
st.set_page_config(
    page_title="Ad Intel Classification Portal",
    page_icon="🏷️",
    layout="wide"
)

st.title("🏷️ Ad Intel New Product Categorization Portal")
st.caption("Upload ad creative images to automatically extract SOP-compliant Manufacturer, Taxonomy, and Product details.")

# Sidebar - API Key and Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    model_choice = st.selectbox("Select Model:", ["gemini-1.5-pro", "gemini-1.5-flash"])
    st.markdown("---")
    st.markdown("### 📋 SOP Quick Reference")
    st.markdown("""
    - **12 Bracket Categories:** Pubs/Bars, Restaurants, Schools, Chemists, Care Homes, Dentists, Colleges/Universities, Hotels, DD Local, Press Regionals, Theatres.
    - **Product Format:** `Brand Name - Product Description`
    - **Capitalization:** Title Case for every word.
    - **Automotive:** Must specify ELECTRIC / HYBRID in product name and Info Box.
    """)

# System Prompt with full SOP
SYSTEM_PROMPT = """
You are an expert UK Ad Metadata & Product Categorization Specialist. Your sole task is to analyze advertising creative images and output structured metadata strictly following the SOP and the 2026 Category Taxonomy.

### STEP 1: MANUFACTURER IDENTIFICATION
1. Identify the registered legal entity or brand owner from the creative/website:
   - Append legal designations where available (e.g., Ltd, Plc, Cic, Llc).
   - Omit email addresses. Keep website URLs without "https://", "www", or "&".
   - Include apostrophes if present in the official name.
   - For acronyms/short forms, use uppercase (e.g., BBJ, NHS).
2. Address Rules:
   - Single Address: Address Line 1, Address Line 4 (Town), Postcode, County. If no address is present, set County to "ZN".
   - Multiple Addresses: Use Head Office address and set County to "Z Multiple Address".
   - Overseas: Use 3-letter country code (e.g., USA, UAE, ESP).
3. Town Name in Brackets for Manufacturer:
   - Append "(Town Name)" at the end of the Manufacturer Name ONLY for these specific Minor Categories: [Pubs & Bars, Independent Restaurants, Chain Restaurants, All School Categories, Chemists, Nursing/Care/Retirement Homes, Dentists/Dental Labs, Further/Higher Education/Colleges/Universities, All Hotels Categories, DD Local Business, Press Regionals, Theatres (if multi-location)].
   - Do NOT add town in brackets if the town name is already part of the business name.

### STEP 2: CATEGORY ASSIGNMENT
Match the ad content to the exact 2026 Taxonomy hierarchy:
- Major Category
- Mid Category
- Minor Category

Special Categorization Rules:
- Residential Homes (Age 45+ chalet/park homes) vs. Retirement Homes (Age 50/60+ with live-in care).
- Plant-based/Dairy-free items -> Minor Category: "Lifestyle & Dietary - Dairy Alternatives".
- Multi-service offerings -> Use broad categories or "Multi-Product".
- Service vs. Construction -> Use "House Equipment General & Diy Services" for painting/plumbing/gutters; use "Building & Construction" for structural/roofing work.

### STEP 3: PRODUCT NAME FORMULATION
Format: Brand Name - Product Description
Formatting Rules:
1. Brand Name Section:
   - Use logo/brand name, not registered manufacturer name.
   - OMIT leading articles ("A", "An", "The") at the start.
   - Strip dots from acronyms (e.g., use "DH" instead of "D.H.").
   - Retain apostrophes (e.g., O'Hagan).
   - Capitalize the first letter of EVERY word in the Product Name.
2. Product Description Section:
   - Automotive: MUST include "Electric" or "Hybrid" in the product name if applicable. Output Info box as ELECTRIC or HYBRID.
   - MOT Services: MUST include "MOT" in the product name if promoted.
   - Farm Products: MUST include "Farm" if the minor category is a Farm category.
   - Professional Lines: Must begin with "Professional".
   - Books: Publisher - Author Name Title (include articles in book titles).
   - Albums: Record Label - Artist Name, Album Name.
   - Concerts: Production House - Artist Name.
   - Town Inclusion: For designated local categories, append Town Name (WITHOUT brackets) at the end of Product Name if not already in Brand Name.

### REQUIRED OUTPUT FORMAT
Output the extracted data strictly in the following layout:

**1) Manufacturer Details**
- Manufacturer Name: 
- Website: 
- Phone: 
- Address Line 1: 
- Town (Line 4): 
- Postcode: 
- County: 
- Country Code: 

**2) Categories**
- Major Category: 
- Mid Category: 
- Minor Category: 

**3) Product Details**
- Product Name: 
- Info Box (Automotive Only): 
"""

# Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload Creative")
    uploaded_file = st.file_uploader("Drag & drop ad creative image here", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Ad Creative", use_container_width=True)
        
        analyze_btn = st.button("🚀 Analyze Creative", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Extracted Metadata")
    if uploaded_file and analyze_btn:
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar to proceed.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_choice)
                
                with st.spinner("Analyzing image against SOP guidelines & searching web..."):
                    response = model.generate_content([SYSTEM_PROMPT, image])
                    st.markdown(response.text)
                    st.success("Analysis complete!")
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
    else:
        st.info("Upload an image on the left and click 'Analyze Creative' to view SOP metadata.")

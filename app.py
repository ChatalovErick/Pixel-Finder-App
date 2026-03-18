import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from pdf2image import convert_from_bytes
import io
import pandas as pd
import json
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Pixel Finder", layout="wide")

st.markdown("""
    <style>
    canvas { image-rendering: pixelated; }
    .stButton>button { border-radius: 5px; height: 3em; }
    .stDownloadButton>button { border-radius: 5px; height: 3em; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "all_coords" not in st.session_state:
    st.session_state.all_coords = []

if "last_added" not in st.session_state:
    st.session_state.last_added = None   # index of last added point


# --- 2. APP INFO ---
def show_app_info():

    # Using a warning box for the disclaimer to make it stand out
    st.warning("⚠️ **Disclaimer**\n\n**This app is designed to find the width (X) and height (Y) of specific pixels, and it is used for images that needs better resolution"
    " for large images.**")

    with st.expander("ℹ️ How to Use", expanded=False):
        st.markdown("""
        ### Features
        - Convert PDF → High‑resolution PNG
        - Zoom & Pan with sub‑pixel precision
        - Click to mark points
        - Name each point immediately
        - Export coordinates as CSV or JSON

        ### Instructions
        1. Upload a PDF or image  
        2. Open the annotation tool  
        3. Zoom/pan to the area you want  
        4. Click to add a point  
        5. Name it immediately  
        """)


# --- 3. ANNOTATION TOOL ---
@st.dialog("Point Annotation Studio", width="large")
def open_image_window(img_input):
    img = Image.open(img_input) if not isinstance(img_input, Image.Image) else img_input
    w, h = img.size

    canvas_width = 1200
    max_display_height = 1200

    # --- Zoom/Pan Controls ---
    c1, c2, c3 = st.columns([1, 1.5, 1.5])
    with c1: zoom = st.slider("Magnification", 1.0, 10.0, 1.0, 0.1)
    
    win_w, win_h = int(w / zoom), int(h / zoom)
    max_x, max_y = max(1, w - win_w), max(1, h - win_h)
    
    with c2: off_x = st.slider("Horizontal Pan", 0, max_x, 0)
    with c3: off_y = st.slider("Vertical Pan", 0, max_y, 0)

    cropped = img.crop((off_x, off_y, off_x + win_w, off_y + win_h))
    ratio = win_w / canvas_width
    canvas_height = min(int(win_h / ratio), max_display_height)

    st.info("🎯 Click once to place a point, name it, and click 'Confirm Point'.")

    # --- CANVAS ---
    # We don't pass initial_drawing here because we want the user to only see 
    # the point they are currently placing to avoid clutter.
    canvas_result = st_canvas(
        fill_color="rgba(255,0,0,0.3)",
        stroke_width=2,
        stroke_color="red",
        background_image=cropped,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="point",
        point_display_radius=6,
        key="canvas_studio", # Specific key for this dialog
    )

    # --- LOGIC FOR SINGLE POINT SELECTION ---
    if canvas_result.json_data and canvas_result.json_data["objects"]:
        objs = canvas_result.json_data["objects"]
        
        if len(objs) > 0:
            # Always take the last (most recent) click
            new_obj = objs[-1]
            rx = int((new_obj["left"] * ratio) + off_x)
            ry = int((new_obj["top"] * ratio) + off_y)

            st.markdown(f"**Current Selection:** Coordinates ({rx}, {ry})")
            
            # 1. Name the point
            point_name = st.text_input("Enter point name:", key="temp_name_input")
            
            # 2. Confirm and Save Button
            if st.button("✅ Confirm & Save Point", use_container_width=True):
                if point_name.strip() == "":
                    st.error("Please provide a name before saving.")
                else:
                    # Commit to session state
                    st.session_state.all_coords.append({
                        "name": point_name,
                        "x_width": rx,
                        "y_height": ry
                    })
                    st.success(f"Saved: {point_name}")
                    st.rerun() # Refresh to clear canvas and ready next point

    # --- VIEW SAVED POINTS ---
    if st.session_state.all_coords:
        with st.expander("View Saved Points", expanded=False):
            st.table(pd.DataFrame(st.session_state.all_coords))


# --- 4. MAIN UI ---
st.title("📍 Pixel Finder")
show_app_info()

with st.sidebar:
    st.header("Upload")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    st.divider()
    uploaded_img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if st.button("Clear All Points"):
        st.session_state.all_coords = []
        st.session_state.last_added = None
        st.rerun()

# --- PDF HANDLING ---
current_image = None

if uploaded_pdf:
    st.subheader("PDF Processing")
    
    # 1. Store bytes so we don't lose them
    pdf_data = uploaded_pdf.read()
    
    # 2. Dynamic Poppler Path
    # We only use the manual path if we are on Windows (local dev)
    # On Streamlit Cloud, Poppler is installed via packages.txt and doesn't need a path.
    
    try:
        # If the local folder doesn't exist, we assume we are on the Cloud/Linux
        pages = convert_from_bytes(pdf_data, dpi=300)
        
        if pages:
            current_image = pages[0]
            st.image(current_image, caption="PDF Page 1 Preview", use_container_width=True)

            # 3. Use a context manager for the Buffer (Best practice for memory)
            buf = io.BytesIO()
            current_image.save(buf, format="PNG")
            
            st.download_button(
                label="Download PNG", 
                data=buf.getvalue(), 
                file_name="converted.png", 
                mime="image/png"
            )

            if st.button("Start Annotation"):
                open_image_window(current_image)
                
    except Exception as e:
        st.error(f"Failed to convert PDF: {e}")


elif uploaded_img:
    current_image = Image.open(uploaded_img)
    st.image(current_image, caption="Uploaded Image", use_container_width=True)

    if st.button("Start Annotation"):
        open_image_window(uploaded_img)

# --- 5. DATA DISPLAY & EXPORT ---
if st.session_state.all_coords:
    st.divider()
    st.header("📊 Export Coordinates")   # <-- Title added

    df = pd.DataFrame(st.session_state.all_coords)
    st.dataframe(df, use_container_width=True)

    # Buttons side-by-side
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False).encode('utf-8'),
            "coords.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:
        st.download_button(
            "📥 Download JSON",
            json.dumps(st.session_state.all_coords, indent=4),
            "coords.json",
            "application/json",
            use_container_width=True
        )
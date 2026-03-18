# 📍  Pixel Finder App
![Python 3.11](https://img.shields.io/badge/python_3.11-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

## Precision Image & PDF Coordinate Extractor
PixelPicker is a lightweight Streamlit web application designed to help users identify the exact width (X) and height (Y) of pixels within any image or PDF document. Whether you are mapping coordinates for automation, data science, or design, PixelPicker provides sub-pixel precision with an easy-to-use "one point at a time" workflow.

## ✨ Key Features
- **PDF & Image Support:** Seamlessly convert PDF pages to high-resolution PNGs for mapping.
- **Precision Zoom & Pan:** Use magnification sliders to find the exact pixel you need.
- **One-Click Annotation:** Click a pixel, name it, and save it to your list.
- **Coordinate Export:** Download your collected data as CSV or JSON.
- **Pixel-Perfect Accuracy:** Coordinates are calculated relative to the top-left (0,0) origin of the original file.

## 🚀 Getting Started
Prerequisites
You will need Python 3.8+ and poppler (for PDF processing).

### Installation
Clone the repository:

```Bash 
git clone https://github.com/ChatalovErick/Pixel-Finder-App.git
cd Pixel-Finder-App
pip install -r requirements.txt
streamlit run app.py
```

## 🛠️ How to Use

- **Upload:** Drop a PDF or an Image into the sidebar.
- **Annotate:** Click "Start Annotation" to open the studio.
- **Find your Pixel:** Use the sliders to zoom in on a specific area.
- **Mark & Name:** Click the pixel once. A text box will appear—give your point a name (e.g., "Top-Left Button") and click Confirm & Save.

Export: Once finished, close the window and download your results from the bottom of the main page.

## ⚠️ Disclaimer
This tool measures raw pixel distances.
X (Width): Distance from the left edge.
Y (Height): Distance from the top edge.
Values are based on the image resolution and do not represent real-world units (cm/inches) unless converted manually using the file's DPI.

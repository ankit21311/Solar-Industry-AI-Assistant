import streamlit as st
from PIL import Image

def analyze_rooftop_image(image):
    """
    Simulate rooftop analysis using basic heuristics from image dimensions.
    Replace this with a real AI vision model for production.
    """
    width, height = image.size
    total_pixels = width * height

    # Use dummy logic to vary results by image size
    area_sqft = total_pixels // 1000  # Fake conversion factor
    recommended_panels = max(1, area_sqft // 20)
    estimated_output_kw = round(recommended_panels * 0.3, 2)
    payback_years = round(6 - min(4.5, recommended_panels * 0.1), 1)
    confidence = round(min(0.95, 0.7 + (recommended_panels * 0.01)), 2)

    suitable = area_sqft > 100 and confidence > 0.75
    comments = (
        "Large flat roof, suitable for multiple panels."
        if suitable else
        "Roof may be too small or obstructed. Please upload a clearer image."
    )

    return {
        "suitable": suitable,
        "area_sqft": area_sqft,
        "recommended_panels": recommended_panels,
        "estimated_output_kw": estimated_output_kw,
        "payback_years": payback_years,
        "confidence": confidence,
        "comments": comments
    }

# Streamlit UI
st.set_page_config(page_title="Solar Rooftop Analyzer", layout="centered")
st.title("🔍 Solar Rooftop Analysis Tool")
st.write("Upload a satellite image of your rooftop to assess solar panel installation feasibility.")

uploaded_file = st.file_uploader("Upload a rooftop image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Rooftop Image", use_column_width=True)

    with st.spinner("Analyzing image..."):
        results = analyze_rooftop_image(image)

    st.success("Analysis Complete ✅")
    st.markdown(f"**Suitable for Installation:** {'Yes' if results['suitable'] else 'No'}")
    st.markdown(f"**Estimated Rooftop Area:** {results['area_sqft']} sq. ft")
    st.markdown(f"**Recommended Number of Panels:** {results['recommended_panels']}")
    st.markdown(f"**Estimated Energy Output:** {results['estimated_output_kw']} kW")
    st.markdown(f"**Estimated Payback Period:** {results['payback_years']} years")
    st.markdown(f"**Confidence Score:** {results['confidence'] * 100:.1f}%")
    st.markdown(f"**Comments:** {results['comments']}")

# Sidebar Docs
st.sidebar.title("🛠 Project Info")
st.sidebar.markdown("### Setup Instructions")
st.sidebar.markdown("1. Install Python 3.9+")
st.sidebar.markdown("2. `pip install -r requirements.txt`")
st.sidebar.markdown("3. Run the app with `streamlit run app.py`")

st.sidebar.markdown("### Future Improvements")
st.sidebar.markdown("- Integrate OpenAI or Google Vision APIs")
st.sidebar.markdown("- Estimate ROI from local energy rates")
st.sidebar.markdown("- Add 3D shading analysis")
st.sidebar.markdown("- Support for multiple languages")

# Use Case Section
st.markdown("---")
st.markdown("### 🔧 Example Use Case")
st.markdown(
    "**Scenario:** A homeowner uploads a top-down satellite image of their house roof. "
    "The tool estimates usable rooftop area, suggests number of panels, expected output, "
    "and estimated payback period."
)

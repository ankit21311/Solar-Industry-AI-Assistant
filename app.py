import streamlit as st
from PIL import Image
import numpy as np
import cv2

# -------------------- Solar Knowledge Base --------------------
SOLAR_KNOWLEDGE = {
    "panel_types": {
        "monocrystalline": {"efficiency": 0.20, "cost_per_watt": 1.20, "lifespan": 25},
        "polycrystalline": {"efficiency": 0.16, "cost_per_watt": 0.90, "lifespan": 25},
        "thin_film": {"efficiency": 0.12, "cost_per_watt": 0.70, "lifespan": 20}
    },
    "installation_costs": {
        "labor_per_panel": 150,
        "permits_and_inspection": 2000,
        "inverter_cost": 1500,
        "mounting_hardware": 50
    },
    "incentives": {
        "federal_tax_credit": 0.30,
        "net_metering_rate": 0.12,
        "avg_electricity_rate": 0.13
    }
}


# -------------------- Solar Analyzer Class --------------------
class SolarAnalyzer:
    def __init__(self):
        self.knowledge_base = SOLAR_KNOWLEDGE

    def analyze_image_properties(self, image):
        try:
            img_array = np.array(image)
            height, width = img_array.shape[:2]

            if width < 300 or height < 300:
                return {"error": "Image resolution too low. Please upload a higher quality image."}

            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            if len(faces) > 0:
                return {"error": "Please upload a rooftop image only."}

            if image.mode != 'L':
                img_gray = image.convert('L')
            else:
                img_gray = image

            contrast = np.std(np.array(img_gray))
            if contrast < 10:
                return {"error": "Image has low contrast. Please upload a clearer image."}

            brightness = np.mean(img_array)
            roof_area_ratio = min(0.8, max(0.3, (brightness / 255) * 0.6 + (contrast / 100) * 0.4))

            return {
                "width": width,
                "height": height,
                "brightness": brightness,
                "contrast": contrast,
                "roof_area_ratio": roof_area_ratio
            }

        except Exception as e:
            return {"error": f"Error analyzing image: {str(e)}"}

    def calculate_solar_potential(self, props, location_factor=1.0):
        if "error" in props:
            return {"error": props["error"]}

        pixel_to_sqft = 0.1
        roof_area = props["width"] * props["height"] * pixel_to_sqft * props["roof_area_ratio"]
        panel_area = 20
        max_panels = int(roof_area * 0.75 / panel_area)

        if roof_area > 1000:
            panel_type = "monocrystalline"
        elif roof_area > 500:
            panel_type = "polycrystalline"
        else:
            panel_type = "thin_film"

        panel_specs = self.knowledge_base["panel_types"][panel_type]
        watts_per_panel = 300
        total_capacity_kw = (max_panels * watts_per_panel * panel_specs["efficiency"]) / 1000
        annual_kwh = total_capacity_kw * 1500 * location_factor

        return {
            "roof_area": round(roof_area),
            "max_panels": max_panels,
            "panel_type": panel_type,
            "panel_specs": panel_specs,
            "total_capacity_kw": round(total_capacity_kw, 2),
            "annual_production_kwh": round(annual_kwh),
            "daily_avg_kwh": round(annual_kwh / 365, 1)
        }

    def calculate_roi_analysis(self, data):
        panel_cost = data["max_panels"] * 300 * self.knowledge_base["panel_types"][data["panel_type"]]["cost_per_watt"]
        labor_cost = data["max_panels"] * self.knowledge_base["installation_costs"]["labor_per_panel"]
        system_cost = panel_cost + labor_cost + self.knowledge_base["installation_costs"]["permits_and_inspection"] + self.knowledge_base["installation_costs"]["inverter_cost"]
        net_cost = system_cost * (1 - self.knowledge_base["incentives"]["federal_tax_credit"])
        annual_savings = data["annual_production_kwh"] * self.knowledge_base["incentives"]["avg_electricity_rate"]
        payback = net_cost / annual_savings if annual_savings else float('inf')
        savings_25yr = (annual_savings * 25) - net_cost
        return {
            "system_cost": round(system_cost),
            "net_cost": round(net_cost),
            "annual_savings": round(annual_savings),
            "payback_years": round(payback, 1),
            "total_25yr_savings": round(savings_25yr),
            "roi_percentage": round((savings_25yr / net_cost) * 100, 1) if net_cost > 0 else 0
        }

    def generate_confidence_score(self, props, data):
        image_quality = min(1.0, (props["contrast"] / 50) * 0.5 + (props["brightness"] / 255) * 0.5)
        roof_factor = min(1.0, data["roof_area"] / 500)
        panel_score = min(1.0, data["max_panels"] / 10)
        confidence = image_quality * 0.4 + roof_factor * 0.3 + panel_score * 0.3
        return round(confidence, 2)

    def analyze_rooftop(self, image, location="Average US"):
        props = self.analyze_image_properties(image)
        if "error" in props:
            return {"error": props["error"]}

        solar_data = self.calculate_solar_potential(props)
        if "error" in solar_data:
            return {"error": solar_data["error"]}

        roi = self.calculate_roi_analysis(solar_data)
        confidence = self.generate_confidence_score(props, solar_data)

        suitable = solar_data["max_panels"] >= 6 and roi["payback_years"] <= 12 and confidence >= 0.6
        recommendation = self.generate_recommendations(solar_data, roi, suitable)

        return {
            "suitable": suitable,
            "confidence": confidence,
            "solar_data": solar_data,
            "roi_data": roi,
            "recommendations": recommendation
        }

    def generate_recommendations(self, solar_data, roi_data, suitable):
        if suitable:
            return {
                "recommendation": "✅ This roof is highly suitable for solar panels.",
                "message": f"Estimated production: {solar_data['annual_production_kwh']} kWh/year. Payback period: {roi_data['payback_years']} years."
            }
        else:
            return {
                "recommendation": "⚠️ This roof may not be ideal for solar panels.",
                "message": f"Payback period is high ({roi_data['payback_years']} years)."
            }


# -------------------- Streamlit App --------------------
def main():
    st.set_page_config(page_title="Solar Panel Suitability Analyzer", layout="centered")
    st.title("☀️ Solar Panel Suitability Analyzer")

    uploaded_file = st.file_uploader("📷 Upload a rooftop image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="📍 Uploaded Roof Image", use_container_width=True)

            analyzer = SolarAnalyzer()
            with st.spinner("🔍 Analyzing rooftop suitability..."):
                result = analyzer.analyze_rooftop(image)

            if "error" in result:
                st.error(result["error"])
            else:
                st.subheader("📊 Suitability Overview")
                col1, col2, col3 = st.columns(3)
                col1.metric("Confidence", f"{result['confidence'] * 100:.0f} %")
                col2.metric("Max Panels", result["solar_data"]["max_panels"])
                col3.metric("Panel Type", result["solar_data"]["panel_type"].capitalize())

                if result["suitable"]:
                    st.success(result["recommendations"]["recommendation"])
                else:
                    st.warning(result["recommendations"]["recommendation"])
                st.caption(result["recommendations"]["message"])

                with st.expander("🔍 Solar Panel Details"):
                    st.write(f"**Roof Area Estimate:** {result['solar_data']['roof_area']} sq ft")
                    st.write(f"**Total Capacity:** {result['solar_data']['total_capacity_kw']} kW")
                    st.write(f"**Annual Energy Production:** {result['solar_data']['annual_production_kwh']} kWh")
                    st.write(f"**Daily Average:** {result['solar_data']['daily_avg_kwh']} kWh")

                with st.expander("💰 ROI & Savings Analysis"):
                    st.write(f"**System Cost:** ${result['roi_data']['system_cost']:,}")
                    st.write(f"**Net Cost (after 30% tax credit):** ${result['roi_data']['net_cost']:,}")
                    st.write(f"**Annual Savings:** ${result['roi_data']['annual_savings']:,}")
                    st.write(f"**Payback Period:** {result['roi_data']['payback_years']} years")
                    st.write(f"**25-Year Net Savings:** ${result['roi_data']['total_25yr_savings']:,}")
                    st.write(f"**ROI:** {result['roi_data']['roi_percentage']} %")
        except Exception as e:
            st.error(f"Failed to process image. Please upload a valid image. Error: {str(e)}")


if __name__ == "__main__":
    main()

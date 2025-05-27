import streamlit as st
from PIL import Image
import numpy as np

# Solar industry knowledge base
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

class SolarAnalyzer:
    def __init__(self):
        self.knowledge_base = SOLAR_KNOWLEDGE

    def analyze_image_properties(self, image):
        """Extract meaningful properties from the uploaded image"""
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Check image size and flag small/poor quality images
        if width < 300 or height < 300:
            return {"error": "Image resolution is too low for analysis. Please upload a higher quality image."}
        
        # Check image contrast
        img_gray = image.convert('L')
        contrast = np.std(np.array(img_gray))
        if contrast < 10:
            return {"error": "Image has too low contrast for effective analysis."}
        
        # Simulate roof detection based on image properties
        brightness = np.mean(img_array)
        roof_area_ratio = min(0.8, max(0.3, (brightness / 255) * 0.6 + (contrast / 100) * 0.4))
        
        # More checks for any further issues, like very dark or overly bright images
        if brightness < 50:
            return {"error": "Image is too dark for analysis. Please upload a brighter image."}
        if brightness > 200:
            return {"error": "Image is too bright for analysis. Please upload a more balanced image."}
        
        return {
            "width": width,
            "height": height,
            "brightness": brightness,
            "contrast": contrast,
            "roof_area_ratio": roof_area_ratio
        }

    def calculate_solar_potential(self, image_props, location_factor=1.0):
        """Calculate solar installation potential based on image analysis"""
        
        # Validate that we have the proper properties
        if "error" in image_props:
            return {"error": image_props["error"]}
        
        # Estimate actual roof area (in sq ft)
        pixel_to_sqft_ratio = 0.1  # Simulated conversion
        estimated_roof_area = (image_props["width"] * image_props["height"] * 
                             pixel_to_sqft_ratio * image_props["roof_area_ratio"])
        
        # Panel sizing (standard residential panel is ~20 sq ft)
        panel_area = 20
        max_panels = int(estimated_roof_area * 0.75 / panel_area)  # 75% utilization
        
        # Select optimal panel type based on roof size
        if estimated_roof_area > 1000:
            panel_type = "monocrystalline"
        elif estimated_roof_area > 500:
            panel_type = "polycrystalline"
        else:
            panel_type = "thin_film"
        
        panel_specs = self.knowledge_base["panel_types"][panel_type]
        
        # Calculate energy output (300W per panel average)
        watts_per_panel = 300
        total_capacity_kw = (max_panels * watts_per_panel * panel_specs["efficiency"]) / 1000
        
        # Annual energy production (kWh) - assuming 1500 sun hours/year average
        annual_production_kwh = total_capacity_kw * 1500 * location_factor
        
        return {
            "roof_area": round(estimated_roof_area),
            "max_panels": max_panels,
            "panel_type": panel_type,
            "panel_specs": panel_specs,
            "total_capacity_kw": round(total_capacity_kw, 2),
            "annual_production_kwh": round(annual_production_kwh),
            "daily_avg_kwh": round(annual_production_kwh / 365, 1)
        }

    def calculate_roi_analysis(self, solar_data):
        """Perform comprehensive ROI analysis"""
        
        # Installation costs
        panel_cost = solar_data["max_panels"] * 300 * self.knowledge_base["panel_types"][solar_data["panel_type"]]["cost_per_watt"]
        labor_cost = solar_data["max_panels"] * self.knowledge_base["installation_costs"]["labor_per_panel"]
        system_cost = (panel_cost + labor_cost + 
                      self.knowledge_base["installation_costs"]["permits_and_inspection"] +
                      self.knowledge_base["installation_costs"]["inverter_cost"])
        
        # Apply federal tax credit
        net_cost = system_cost * (1 - self.knowledge_base["incentives"]["federal_tax_credit"])
        
        # Annual savings
        annual_savings = (solar_data["annual_production_kwh"] * 
                         self.knowledge_base["incentives"]["avg_electricity_rate"])
        
        # Payback period
        payback_years = net_cost / annual_savings if annual_savings > 0 else float('inf')
        
        # 25-year savings
        total_25yr_savings = (annual_savings * 25) - net_cost
        
        return {
            "system_cost": round(system_cost),
            "net_cost": round(net_cost),
            "annual_savings": round(annual_savings),
            "payback_years": round(payback_years, 1),
            "total_25yr_savings": round(total_25yr_savings),
            "roi_percentage": round((total_25yr_savings / net_cost) * 100, 1) if net_cost > 0 else 0
        }

    def generate_confidence_score(self, image_props, solar_data):
        """Generate confidence score based on analysis quality"""
        
        # Factors affecting confidence
        image_quality = min(1.0, (image_props["contrast"] / 50) * 0.5 + 
                           (image_props["brightness"] / 255) * 0.5)
        
        roof_size_factor = min(1.0, solar_data["roof_area"] / 500)
        panel_feasibility = min(1.0, solar_data["max_panels"] / 10)
        
        confidence = (image_quality * 0.4 + roof_size_factor * 0.3 + panel_feasibility * 0.3)
        
        return round(confidence, 2)

    def analyze_rooftop(self, image, location="Average US"):
        """Main analysis function"""
        
        # Extract image properties
        image_props = self.analyze_image_properties(image)
        
        # If there is an error in image analysis, return error message
        if "error" in image_props:
            return {"error": image_props["error"]}
        
        # Calculate solar potential
        solar_data = self.calculate_solar_potential(image_props)
        
        # If there is an error in solar potential calculation, return error message
        if "error" in solar_data:
            return {"error": solar_data["error"]}
        
        # Perform ROI analysis
        roi_data = self.calculate_roi_analysis(solar_data)
        
        # Generate confidence score
        confidence = self.generate_confidence_score(image_props, solar_data)
        
        # Determine suitability
        suitable = (solar_data["max_panels"] >= 6 and 
                   roi_data["payback_years"] <= 12 and 
                   confidence >= 0.6)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(solar_data, roi_data, suitable)
        
        return {
            "suitable": suitable,
            "confidence": confidence,
            "solar_data": solar_data,
            "roi_data": roi_data,
            "recommendations": recommendations
        }

    def generate_recommendations(self, solar_data, roi_data, suitable):
        if suitable:
            return {
                "recommendation": "This roof is highly suitable for solar panels.",
                "message": f"Estimated production: {solar_data['annual_production_kwh']} kWh/year. Payback period: {roi_data['payback_years']} years."
            }
        else:
            return {
                "recommendation": "This roof may not be suitable for solar panels.",
                "message": f"Payback period is high ({roi_data['payback_years']} years)."
            }

# In your Streamlit app
import streamlit as st
from PIL import Image

def main():
    st.title("Solar Panel Suitability Analyzer")
    uploaded_file = st.file_uploader("Upload an image of the rooftop", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Display the uploaded image
        st.image(image, caption="Uploaded Roof Image", use_container_width=True)
        
        # Initialize SolarAnalyzer
        analyzer = SolarAnalyzer()
        
        # Analyze the image
        result = analyzer.analyze_rooftop(image)
        
        # Display results
        if "error" in result:
            st.error(result["error"])
        else:
            # Show solar data
            st.subheader("Solar Panel Data")
            st.write(f"Max Panels: {result['solar_data']['max_panels']}")
            st.write(f"Panel Type: {result['solar_data']['panel_type']}")
            st.write(f"Total Capacity (kW): {result['solar_data']['total_capacity_kw']}")
            st.write(f"Annual Production (kWh): {result['solar_data']['annual_production_kwh']}")
            st.write(f"Daily Average Production (kWh): {result['solar_data']['daily_avg_kwh']}")
            
            # ROI Analysis
            st.subheader("ROI and Savings")
            st.write(f"System Cost: ${result['roi_data']['system_cost']}")
            st.write(f"Net Cost After Tax Credit: ${result['roi_data']['net_cost']}")
            st.write(f"Annual Savings: ${result['roi_data']['annual_savings']}")
            st.write(f"Payback Period: {result['roi_data']['payback_years']} years")
            st.write(f"Total Savings over 25 years: ${result['roi_data']['total_25yr_savings']}")
            st.write(f"ROI: {result['roi_data']['roi_percentage']}%")
            
            # Confidence and Suitability
            st.subheader("Confidence & Suitability")
            st.write(f"Confidence: {result['confidence']*100}%")
            if result["suitable"]:
                st.success(result["recommendations"]["recommendation"])
                st.write(result["recommendations"]["message"])
            else:
                st.warning(result["recommendations"]["recommendation"])
                st.write(result["recommendations"]["message"])

if __name__ == "__main__":
    main()

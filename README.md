# ☀️ Solar Panel Suitability Analyzer

This Streamlit application helps determine whether a rooftop is suitable for solar panel installation based on an uploaded image. It analyzes the rooftop area, calculates potential solar energy production, estimates cost, ROI, and provides recommendations.

---

## 🚀 Features

- 🖼️ Image analysis to check resolution, brightness, contrast, and presence of non-roof elements.
- 📐 Roof area estimation based on image properties.
- ⚡ Solar potential calculation using knowledge of different panel types.
- 💰 ROI analysis including system cost, federal tax credit, payback period, and 25-year savings.
- 📊 Visual report with confidence score and suitability recommendation.

---

## 🛠️ Tech Stack

- **Streamlit**: For the interactive web UI
- **OpenCV**: For image analysis (face detection, grayscale conversion)
- **Pillow (PIL)**: For image preprocessing
- **NumPy**: For numeric operations

---

## 📦 Installation

### 1. Clone the repository

git clone https://github.com/yourusername/solar-analyzer.git
cd solar-analyzer

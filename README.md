# AutoViz Streamlit App

![Python](https://img.shields.io/badge/python-3.10-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.52-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

An **interactive Streamlit app** for automatic data visualization using Seaborn, Matplotlib and Plotly.  
Upload CSV datasets and instantly generate meaningful visualizations with adjustable settings. Future updates will include **LLM-based prompt-driven plotting**.

---

## Features

### Core App Features
- **File Upload & Preview**: Upload your csv, xlsx, xml and json files. View the first few rows and summary statistics instantly.
- **Plots**: Automatically generates different types of plots including scatter plot, line plot, histogram, bar plot, count plot, box plot, violin plot, point plot.
- **Save Plots**: Export your generated visualizations as high-quality PNG images.
- **Interactive Widgets**: Easily adjust plot settings with Streamlit sliders and checkboxes.

### AutoVizEngine Functionality
AutoVizEngine automatically analyzes your dataset and generates visualizations to reveal insights. Some features include:

- Automatic plot selection based on column types (numeric, categorical, datetime)
- Target analysis: Visualizations focused on a specific target column
- Distribution plots: Histograms, boxplots, KDEs, and bar charts
- Correlation & relationship analysis: Heatmaps, scatterplots, pairplots
- Time series visualization for datetime columns

> The app integrates these visualizations seamlessly into Streamlit, so you can explore your dataset quickly without writing any plotting code.

---

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/NehalTishan/AutoViz.git
cd AutoViz
```

2. **Create a virtual environment (recommended):**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3.**Install dependencies:**

```bash
pip install -r requirements.txt
```































































































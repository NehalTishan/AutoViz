import streamlit as st
from backend_engine import AutoVizEngine
import plotly.express as px
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AutoViz Pro", layout="wide")
st.title("📊 AutoViz Data Explorer", text_alignment="center")

engine = AutoVizEngine()

PLOTLY_PALETTES = {
    "Plotly": px.colors.qualitative.Plotly,
    "D3": px.colors.qualitative.D3,
    "G10": px.colors.qualitative.G10,
    "T10": px.colors.qualitative.T10,
    "Alphabet": px.colors.qualitative.Alphabet,
}

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.sidebar.file_uploader(
    "Upload Data", type=["csv", "xlsx", "xls", "json", "xml"]
)

if not uploaded_file:
    st.info("Upload a dataset to begin")
    st.stop()

df = engine.load_data(uploaded_file)

st.subheader("Preview")
st.dataframe(df.head(), use_container_width=True)

st.subheader("Summary Statistics")
st.dataframe(df.describe(), use_container_width=True)

st.subheader("Null values:")
st.dataframe(df.isnull().sum(), use_container_width=True)

# ---------------- UI CONTROLS ----------------
library = st.sidebar.radio("Library", ["Seaborn", "Plotly"])
plot_type = st.sidebar.selectbox(
    "Plot Type",
    ["Relational", "Histogram", "Categorical", "Pairplot", "Heatmap"]
)

#figsize slider to overcome the overlapping of heatmap
# Heatmap specific controls
if plot_type == "Heatmap" and library == "Seaborn":
    st.sidebar.subheader("Heatmap Size")
    fig_width = st.sidebar.slider("Figure Width", 6, 30, 12)
    fig_height = st.sidebar.slider("Figure Height", 4, 25, 10)


all_cols = df.columns.tolist()
num_cols = df.select_dtypes(include="number").columns.tolist()


# ---------------- PARAM COLLECTION ----------------
params = {"data": df}

#x parameter collection
if plot_type not in ["Pairplot", "Heatmap"]:
    params["x"] = st.sidebar.selectbox("X Axis", all_cols)

#y parameter collection
if plot_type in ["Relational", "Categorical"]:
    is_count_plot = (plot_type == "Categorical" and 
                     library == "Plotly" and 
                     'kind' in params and 
                     params.get('kind') == 'count')
    
    if not is_count_plot:
        y_choices = num_cols if plot_type == "Relational" else all_cols
        params["y"] = st.sidebar.selectbox("Y Axis", y_choices)

#if relational plot type selector and also if the library is plotly then z axis selector for 3d
if plot_type == "Relational":
    params["kind"] = st.sidebar.radio("Kind", ["scatter", "line"])
    if library == "Plotly":
        z = st.sidebar.selectbox("Z Axis (3D)", [None] + num_cols)
        if z:
            params["z"] = z

# Add categorical plot type selector
if plot_type == "Categorical":
    if library == "Seaborn":
        cat_kinds = ["strip", "swarm", "box", "violin", "boxen", "bar", "count"]
        params["kind"] = st.sidebar.selectbox("Categorical Plot Type", cat_kinds)
    else:
        plotly_cat_kinds = ["bar", "count", "box", "violin", "strip"]
        params["kind"] = st.sidebar.selectbox("Categorical Plot Type", plotly_cat_kinds)

if plot_type == "Heatmap" and library == "Seaborn":
    params["figsize"] = (fig_width, fig_height)



# ---------------- ADVANCED OPTIONS ----------------
# ---------------- ADVANCED OPTIONS ----------------
with st.sidebar.expander("Advanced Styling"):
    hue = st.selectbox("Hue (Color)", [None] + all_cols)
    if hue:
        params["hue"] = hue
    
    # Add size and style options for relational plots
    if plot_type == "Relational":
        size_col = st.selectbox("Size(Choose column with non-null value when using plotly)", [None] + num_cols)
        if size_col:
            params["size"] = size_col
        
        if library == 'Seaborn':
            if st.checkbox("Create Subgroup"):
                order=st.selectbox("Row wise or Column wise", ['row', 'col'])
                subgroup_data = st.selectbox("select data", [None] + all_cols)
                params[order] = subgroup_data 
            params["legend"]= 'auto'
        
        style_col = st.selectbox("Style (Marker Style)", [None] + all_cols)
        if style_col:
            params["style"] = style_col
    
    #bins option for histogram of plotly and seaborn
    if plot_type == 'Histogram':
        bins=st.slider("Bins", 5, 100, 10)
        if bins:
            params["bins"] = bins
        if library == 'Seaborn':
            mult=st.selectbox("Multiple", ['layer', 'dodge', 'stack', 'fill'])
            if mult:
                params["multiple"] = mult
            kde = False
            if st.checkbox("Kde"):
                kde = True
                params["kde"] = kde
            elem = st.selectbox("Element", ['bars', 'step', 'poly'])
            if elem:
                params["element"] = elem

    
    #pallete options for seaborn and plotly
    if library == "Seaborn":
        params["palette"] = st.selectbox(
            "Palette", ["deep", "muted", "viridis", "rocket", "mako", "flare", "crest"]
        )
    else:
        if hue:
            p_key = st.selectbox("Plotly Palette", list(PLOTLY_PALETTES.keys()))
            params["palette"] = PLOTLY_PALETTES[p_key]

# ---------------- PLOT ----------------
if st.sidebar.button("Generate Plot"):
    clean_params = {k: v for k, v in params.items() if v is not None}

    if library == "Seaborn":
        fig = engine.run_seaborn(plot_type, clean_params)
        st.pyplot(fig, use_container_width=True)
    else:
        fig = engine.run_plotly(plot_type, clean_params)
        st.plotly_chart(fig, use_container_width=True)
    
    st.session_state["fig"] = fig
    st.session_state["library"] = library

# ---------------- SAVE IMAGE ----------------

if "fig" in st.session_state:
    fig = st.session_state["fig"]
    library = st.session_state["library"]

    st.markdown("### 💾 Save Figure")

    save_name = st.text_input(
        "File name",
        value="autoviz_plot.png"
    )

    if st.button("📥 Save as Image"):
        if library == "Seaborn":
            buf = BytesIO()

            # 🔥 force layout recalculation
            fig.canvas.draw()
            fig.tight_layout()

            fig.savefig(
                buf,
                format="png",
                dpi=300,
                bbox_inches="tight",
                pad_inches=0.3
            )
            buf.seek(0)

            st.download_button(
                "⬇️ Download Image",
                data=buf,
                file_name=save_name,
                mime="image/png"
            )


        else:

            # 🔥 Fix cropping
            fig.update_layout(
                width=1200,
                height=800,
                margin=dict(l=120, r=120, t=100, b=120),
            )

            img_bytes = fig.to_image(
                format="png",
                scale=3
            )

            st.download_button(
                "⬇️ Download Image",
                data=img_bytes,
                file_name=save_name,
                mime="image/png"
            )

else:
    st.info("Generate a plot first to enable saving.")



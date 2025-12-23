import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os
from io import StringIO, BytesIO

class AutoVizEngine:
    def __init__(self):
        sns.set_theme()

    def load_data(self, uploaded_file):
        """Processes CSV, Excel, JSON, and XML using original conversion logic."""
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext == '.csv':
            return pd.read_csv(uploaded_file)
        
        # Logic from file_conversion.py
        read_methods = {'.xlsx': pd.read_excel, '.xls': pd.read_excel, '.json': pd.read_json, '.xml': pd.read_xml}
        if ext in read_methods:
            df = read_methods[ext](uploaded_file)
            csv_mem = StringIO()
            df.to_csv(csv_mem, index=False)
            return pd.read_csv(StringIO(csv_mem.getvalue()))
        raise ValueError("Unsupported format")

    def run_seaborn(self, plot_type, params):
        """Maps parameters specifically for Seaborn functions."""
        # Create a copy to avoid modifying the original dict
        p = params.copy()
        data = p.pop('data')
        
        if plot_type == "Relational":
            # Seaborn uses 'height' and 'aspect'
            return sns.relplot(data=data, **p).figure
        
        elif plot_type == "Histogram":
            # Seaborn uses 'kde' and 'bins'
            return sns.histplot(data=data, **p).figure
            
        elif plot_type == "Categorical":
            # Seaborn uses 'kind' like 'strip', 'boxen', etc.
            return sns.catplot(data=data, **p).figure
        
        elif plot_type == "Pairplot":
            return sns.pairplot(data).fig

        elif plot_type == "Heatmap":
            corr = data.corr(numeric_only=True)
            figsize = p.pop("figsize", (10, 8))

            fig, ax = plt.subplots(figsize=figsize)
            sns.heatmap(
                corr,
                annot=True,
                cmap="coolwarm",
                ax=ax,
                square=True,
                cbar_kws={"shrink": 0.8}
            )
            plt.tight_layout()
            return fig



    def run_plotly(self, plot_type, params):
        """Maps parameters specifically for Plotly, including 3D."""
        p = params.copy()
        data = p.pop('data')
        z = p.pop('z', None)
        kind = p.get('kind', 'scatter')
        
        
        # Plotly uses 'color' instead of 'hue' and 'symbol' instead of 'style'
        plotly_args = {
            'data_frame': data,
            'x': p.get('x'),
            'y': p.get('y'),
            'color': p.get('hue'),
            'color_discrete_sequence': p.get('palette'),
        }

        if plot_type == "Relational":
            # Include size parameter if available
            if 'size' in p:
                plotly_args['size'] = p['size']
            # Map style to symbol for scatter plots
            if 'style' in p:
                plotly_args['symbol'] = p['style']
            
            if z: # 3D Dispatch
                if kind=='scatter':
                    return px.scatter_3d(z=z, **plotly_args)
                else:
                    # For 3D line, remove size parameter which isn't supported
                    plotly_args.pop('size', None)
                    return px.line_3d(z=z, **plotly_args)
            # 2D Dispatch
            return px.scatter(**plotly_args) if kind == 'scatter' else px.line(**plotly_args)


        elif plot_type == "Histogram":
            return px.histogram(data_frame=data, x=p.get('x'), color=p.get('hue'), 
                                nbins=p.get('bins'), color_discrete_sequence=p.get('palette'))
        
        elif plot_type == "Categorical":
            # Enhanced categorical plot handling with proper parameter mapping
            mapping = {
                "bar": px.bar, 
                "count": lambda **kwargs: px.histogram(x=kwargs.get('x'), **{k:v for k,v in kwargs.items() if k != 'y'}),
                "box": px.box, 
                "violin": px.violin, 
                "strip": px.strip
            }
            method = mapping.get(kind, px.bar)
            
            # Ensure y is only included for appropriate plot types
            if kind == "count":
                plotly_args.pop('y', None)
            
            return method(**plotly_args)
        
        elif plot_type == "Pairplot":
            # Calculate dynamic sizing based on number of columns
            num_cols = len(data.select_dtypes(include="number").columns)
                
            # Dynamic height and margin based on column count
            base_height = 800
            margin_bottom = 120 + (num_cols * 10)  # More columns = more margin
                
            fig = px.scatter_matrix(
                    data_frame=data,
                    dimensions=data.select_dtypes(include="number").columns,
                    color=p.get("hue"),
                )
                
            # 🔥 FIX: Rotate labels and adjust layout for long column names
            fig.update_xaxes(
                    tickangle=45,
                    tickfont=dict(size=10)  # Smaller font for long labels
                )
            fig.update_yaxes(
                    tickangle=45,
                    tickfont=dict(size=10)
                )
                
            # 🔥 FIX: Adjust layout to prevent label cutting
            fig.update_layout(
                    height=base_height + (num_cols * 20),  # Increase height for more columns
                    margin=dict(l=50, r=50, t=50, b=margin_bottom),
                    showlegend=True,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=1.02
                    )
                )
                
            return fig

        elif plot_type == "Heatmap":
            corr = data.corr(numeric_only=True)
            return px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale="RdBu",
                aspect="auto",
            )

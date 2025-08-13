import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go

def load_data(file_path):
    """
    Loads compound data from a CSV file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    return pd.read_csv(file_path)

def calculate_lipinski(df):
    """
    Calculates Lipinski's Rule of Five violations.
    """
    df.dropna(subset=['mw', 'logp', 'hbd', 'hba'], inplace=True)
    violations = (
        (df['mw'] > 500).astype(int) +
        (df['logp'] > 5).astype(int) +
        (df['hbd'] > 5).astype(int) +
        (df['hba'] > 10).astype(int)
    )
    df['lipinski_violations'] = violations
    df['is_drug_like'] = (violations == 0)
    return df

def calculate_pic50(df):
    """
    Calculates pIC50 values from IC50 values.
    Handles non-positive IC50 values by setting pIC50 to NaN.
    IC50 values are assumed to be in nM and converted to M for pIC50 calculation.
    """
    # Convert IC50 from nM to M
    df['ic50_M'] = df['ic50'] * 1e-9
    
    # Handle non-positive IC50 values before log transformation
    # Replace 0 or negative IC50_M with NaN to avoid log(0) or log(negative) errors
    df.loc[df['ic50_M'] <= 0, 'ic50_M'] = np.nan

    # Calculate pIC50
    df['pIC50'] = -np.log10(df['ic50_M'])
    
    # Drop the intermediate ic50_M column
    df = df.drop(columns=['ic50_M'])
    return df

# ... (existing matplotlib functions remain unchanged) ...

def plot_logp_mw_scatter(df, output_dir=None, return_fig=False):
    fig = plt.figure(figsize=(10, 8))
    sns.scatterplot(data=df, x='logp', y='mw', hue='ic50', palette='viridis', size='ic50', sizes=(20, 200), alpha=0.7)
    plt.title('LogP vs. Molecular Weight', fontsize=16)
    plt.xlabel('LogP', fontsize=12)
    plt.ylabel('Molecular Weight (MW)', fontsize=12)
    plt.legend(title='IC50 (nM)')
    plt.grid(True)
    if return_fig:
        return fig
    if output_dir:
        output_path = os.path.join(output_dir, 'scatter_logp_vs_mw.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_property_histograms(df, output_dir=None, return_fig=False):
    properties = ['mw', 'logp', 'hbd', 'hba', 'psa', 'ic50']
    fig = plt.figure(figsize=(15, 10))
    for i, prop in enumerate(properties):
        plt.subplot(2, 3, i + 1)
        sns.histplot(df[prop], kde=True, bins=30)
        plt.title(f'Distribution of {prop.upper()}')
    plt.tight_layout()
    if return_fig:
        return fig
    if output_dir:
        output_path = os.path.join(output_dir, 'histograms_molecular_properties.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_correlation_heatmap(df, output_dir=None, return_fig=False):
    corr = df[['mw', 'logp', 'hbd', 'hba', 'psa', 'ic50']].corr()
    fig = plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
    plt.title('Correlation Heatmap')
    if return_fig:
        return fig
    if output_dir:
        output_path = os.path.join(output_dir, 'correlation_heatmap.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_drug_likeness_boxplots(df, output_dir=None, return_fig=False):
    properties = ['mw', 'logp', 'ic50']
    fig = plt.figure(figsize=(18, 6))
    for i, prop in enumerate(properties):
        plt.subplot(1, 3, i + 1)
        sns.boxplot(data=df, x='is_drug_like', y=prop, hue='is_drug_like', palette='pastel', legend=False)
        plt.title(f'{prop.upper()} vs. Drug-Likeness')
    plt.tight_layout()
    if return_fig:
        return fig
    if output_dir:
        output_path = os.path.join(output_dir, 'boxplots_drug_likeness.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

# --- Fixed Plotly Functions ---

def plotly_logp_mw_scatter(df):
    fig = px.scatter(df, x='logp', y='mw', color='pIC50', 
                     hover_data=['name', 'chembl_id', 'target'],
                     title='LogP vs. Molecular Weight',
                     labels={'logp': 'LogP', 'mw': 'Molecular Weight (Da)', 'pIC50': 'pIC50'},
                     color_continuous_scale='viridis')  # Explicitly set color scale
    return fig

def plotly_property_histograms(df):
    properties = ['mw', 'logp', 'hbd', 'hba', 'psa', 'pIC50']
    # Create individual subplots for better control
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[prop.upper() for prop in properties],
        vertical_spacing=0.12
    )
    
    for i, prop in enumerate(properties):
        row = i // 3 + 1
        col = i % 3 + 1
        
        # Filter out NaN values for each property
        data_clean = df[prop].dropna()
        
        fig.add_trace(
            go.Histogram(x=data_clean, name=prop, showlegend=False, nbinsx=30),
            row=row, col=col
        )
    
    fig.update_layout(title_text='Distribution of Molecular Properties', height=600)
    return fig

def plotly_correlation_heatmap(df):
    corr = df[['mw', 'logp', 'hbd', 'hba', 'psa', 'pIC50']].corr()
    
    # Create triangular mask - set upper triangle to NaN for cleaner visualization
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.copy()
    corr_masked[mask] = np.nan
    
    # Create triangular correlation heatmap
    fig = px.imshow(corr_masked, 
                    text_auto=True, 
                    aspect="auto",
                    title='Correlation Heatmap of Molecular Properties (Triangular)',
                    color_continuous_scale='RdBu_r',  # Red=positive, Blue=negative
                    color_continuous_midpoint=0)      # Center at zero
    
    # Update layout to make it look cleaner
    fig.update_layout(
        xaxis_title="Properties",
        yaxis_title="Properties"
    )
    return fig

def plotly_drug_likeness_boxplots(df):
    properties = ['mw', 'logp', 'pIC50']
    
    # Create long format data for faceted box plots
    df_melted = df.melt(id_vars=['is_drug_like'], value_vars=properties, 
                        var_name='Property', value_name='Value')
    
    fig = px.box(df_melted, x='is_drug_like', y='Value', color='is_drug_like',
                 facet_col='Property', facet_col_wrap=3, 
                 title='Property Comparison: Drug-Like vs. Non-Drug-Like', 
                 labels={'is_drug_like': 'Is Drug-Like?', 'Value': 'Property Value'},
                 color_discrete_sequence=['lightcoral', 'lightblue'])  # Better colors
    
    fig.update_yaxes(matches=None)  # Independent y-axes
    fig.update_layout(showlegend=False)  # Remove redundant legend
    return fig

def plotly_mw_logp_density_heatmap(df):
    """
    Creates a 2D density heatmap of MW vs. LogP.
    SIMPLIFIED: Remove marginal histograms to avoid the error
    """
    # Create a clean dataframe with only the columns we need
    plot_df = df[['logp', 'mw']].copy()
    
    # Remove any NaN values
    plot_df = plot_df.dropna()
    
    # Try without marginal histograms first
    fig = px.density_heatmap(plot_df, 
                             x='logp', 
                             y='mw',
                             title='Density of Compounds in Physicochemical Space',
                             labels={'logp': 'LogP', 'mw': 'Molecular Weight (Da)'},
                             color_continuous_scale='plasma')
    return fig

def plotly_property_distribution_by_target(df):
    """
    Creates violin plots of molecular properties by target.
    """
    properties_to_plot = ['mw', 'logp', 'pIC50', 'hbd', 'hba', 'psa']
    
    # Melt the DataFrame to long format for easier plotting with px.violin
    df_melted = df.melt(id_vars=['target'], value_vars=properties_to_plot, 
                        var_name='Property', value_name='Value')
    
    # Filter out NaN values that might result from pIC50 calculation or original data
    df_melted.dropna(subset=['Value'], inplace=True)

    fig = px.violin(df_melted, x='target', y='Value', color='target', 
                    facet_col='Property', facet_col_wrap=3, 
                    title='Molecular Property Distribution by Target',
                    labels={'target': 'Target', 'Value': 'Value'},
                    category_orders={"Property": properties_to_plot},  # Ensure consistent order
                    box=True,  # Show box plot inside violin
                    points="outliers")  # Show only outlier points to avoid clutter
    
    fig.update_yaxes(matches=None)  # Allow independent y-axes for different properties
    fig.update_layout(showlegend=True)  # Keep legend for target identification
    return fig

def run_analysis(input_path, output_dir):
    """
    Runs the full analysis pipeline.
    """
    os.makedirs(output_dir, exist_ok=True)
    data = load_data(input_path)
    data_with_lipinski = calculate_lipinski(data)
    data_with_pic50 = calculate_pic50(data_with_lipinski)  # Calculate pIC50
    
    # Filter out rows with NaN pIC50 before passing to plotting functions
    data_for_plotting = data_with_pic50.dropna(subset=['pIC50'])

    # Call matplotlib functions for static output
    plot_logp_mw_scatter(data_for_plotting, output_dir)
    plot_property_histograms(data_for_plotting, output_dir)
    plot_correlation_heatmap(data_for_plotting, output_dir)
    plot_drug_likeness_boxplots(data_for_plotting, output_dir)
    print(f"\nAnalysis complete. All outputs saved to '{output_dir}'.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform molecular analysis on compound data.')
    parser.add_argument('input', type=str, help='Path to the input CSV file from ChEMBL.')
    parser.add_argument('output', type=str, help='Directory to save analysis results.')
    args = parser.parse_args()
    run_analysis(args.input, args.output)
import streamlit as st
import pandas as pd
import os
import sys

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.analysis import molecular_analysis

st.set_page_config(layout="wide", page_title="Biotech Drug Discovery Dashboard", page_icon="🔬")

# --- Sidebar ---
st.sidebar.title("About this Project")
st.sidebar.info("""
This dashboard is a tool for early-stage drug discovery analysis, designed to bridge the gap between raw chemical data and actionable insights. 
It allows researchers to interactively filter and visualize compound data based on key physicochemical properties and bioactivity.

**Relevance to Biotech:**
- **Hit Identification:** Quickly sift through thousands of compounds to identify potential 'hits'.
- **Lead Optimization:** Analyze structure-activity relationships (SAR) to guide the chemical optimization of lead compounds.
- **Candidate Selection:** De-risk drug candidates by flagging properties associated with poor pharmacokinetics (e.g., Lipinski's Rule violations).
""")

st.sidebar.title("Data Format Requirements")
st.sidebar.info("""
**Expected CSV Format:**

Your uploaded CSV file should contain these columns:

**Required Columns:**
- `chembl_id`: Compound identifier (e.g., CHEMBL123456)
- `name`: Compound name (can be empty/null)
- `target`: Target protein name (e.g., EGFR, SRC)
- `ic50`: IC50 values in nM (numeric)
- `mw`: Molecular weight in Daltons (numeric)
- `logp`: LogP lipophilicity (numeric)
- `hbd`: Hydrogen bond donors (numeric)
- `hba`: Hydrogen bond acceptors (numeric)
- `psa`: Polar surface area (numeric)

**Example Data:**
```
chembl_id,name,target,ic50,mw,logp,hbd,hba,psa
CHEMBL123,Aspirin,COX1,500,180.16,1.19,1,4,63.6
CHEMBL456,Ibuprofen,COX1,1200,206.29,3.97,1,2,37.3
```

**The app will automatically calculate:**
- Lipinski Rule of 5 violations
- Drug-likeness classification
- pIC50 values from IC50
""")

st.sidebar.title("Controls")

# --- Data Loading ---
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if st.sidebar.button("Load Sample Dataset"):
    st.session_state.data_loaded = True
    st.session_state.df = load_data(os.path.join("data", "raw", "default_drug_data.csv"))
    if st.session_state.df is not None:
        st.session_state.df = molecular_analysis.calculate_lipinski(st.session_state.df.copy())
        st.session_state.df = molecular_analysis.calculate_pic50(st.session_state.df.copy())

uploaded_file = st.sidebar.file_uploader("Or Upload Your Own Data (CSV)", type=['csv'])
if uploaded_file is not None:
    st.session_state.data_loaded = True
    st.session_state.df = pd.read_csv(uploaded_file)
    if st.session_state.df is not None:
        # Check if required columns are present
        required_cols = ['chembl_id', 'name', 'target', 'ic50', 'mw', 'logp', 'hbd', 'hba', 'psa']
        missing_cols = [col for col in required_cols if col not in st.session_state.df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            st.info("Please check the 'Data Format Requirements' section in the sidebar for the expected format.")
            st.session_state.data_loaded = False
        else:
            st.session_state.df = molecular_analysis.calculate_lipinski(st.session_state.df.copy())
            st.session_state.df = molecular_analysis.calculate_pic50(st.session_state.df.copy())
            st.success("✅ Data uploaded successfully!")

# --- Main App ---
st.title("🔬 Biotech Drug Discovery Dashboard")
st.markdown("Welcome! Load the sample dataset or upload your own to begin analysis.")

if st.session_state.data_loaded and hasattr(st.session_state, 'df') and st.session_state.df is not None:
    df = st.session_state.df

    # Show data summary
    st.subheader("📊 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Compounds", len(df))
    with col2:
        st.metric("Unique Targets", df['target'].nunique())
    with col3:
        drug_like_count = df['is_drug_like'].sum()
        st.metric("Drug-Like Compounds", f"{drug_like_count} ({drug_like_count/len(df)*100:.1f}%)")
    with col4:
        avg_potency = df['pIC50'].mean()
        st.metric("Avg pIC50", f"{avg_potency:.2f}")

    # --- Filtering Widgets ---
    st.sidebar.header("Filter Compounds")

    # Target filter
    targets = df['target'].unique().tolist()
    selected_targets = st.sidebar.multiselect("Filter by Target", options=targets, default=targets)
    
    # Apply target filter first
    df = df[df['target'].isin(selected_targets)]

    # Drug-likeness filter
    drug_like_only = st.sidebar.checkbox("Show only 'Drug-Like' compounds", value=False)
    if drug_like_only:
        df = df[df['is_drug_like']]

    # Property range filters
    mw_min, mw_max = float(df['mw'].min()), float(df['mw'].max())
    mw_range = st.sidebar.slider("Molecular Weight (MW)", mw_min, mw_max, (mw_min, mw_max))
    
    logp_min, logp_max = float(df['logp'].min()), float(df['logp'].max())
    logp_range = st.sidebar.slider("LogP", logp_min, logp_max, (logp_min, logp_max))

    # pIC50 range filter
    # Ensure pIC50 column exists and is not all NaN before getting min/max
    if 'pIC50' in df.columns and not df['pIC50'].isnull().all():
        pic50_min, pic50_max = float(df['pIC50'].min()), float(df['pIC50'].max())
        pic50_range = st.sidebar.slider(
            "pIC50", 
            min_value=pic50_min, 
            max_value=pic50_max, 
            value=(pic50_min, pic50_max)
        )
        df = df[(df['pIC50'] >= pic50_range[0]) & (df['pIC50'] <= pic50_range[1])]
    else:
        st.sidebar.warning("pIC50 data not available for filtering.")

    # Apply filters
    filtered_df = df[
        (df['mw'].between(mw_range[0], mw_range[1])) &
        (df['logp'].between(logp_range[0], logp_range[1]))
    ]
    # Note: pIC50 filter is applied directly above if available

    st.header("Filtered Compound Data")
    st.dataframe(filtered_df, use_container_width=True)
    st.markdown(f"_Displaying {len(filtered_df)} of {len(df)} compounds based on filters._")

    # --- Visualizations with Explanations ---
    st.header("Interactive Analysis")

    if not filtered_df.empty:
        # Create two columns for plots
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("What is this plot?", expanded=False):
                st.info("""
                **LogP vs. Molecular Weight:** This plot, often called a "Lipinski plot," helps visualize the 'drug-like' space. 
                - **LogP** measures a compound's lipophilicity (how well it dissolves in fats/oils).
                - **Molecular Weight (MW)** is the mass of the molecule.
                Compounds within Lipinski's Rule of Five (MW < 500, LogP < 5) are generally considered more likely to be orally available drugs.
                The color intensity represents the **pIC50** value, indicating compound potency (higher pIC50 = higher potency).
                """)
            fig_scatter = molecular_analysis.plotly_logp_mw_scatter(filtered_df)
            st.plotly_chart(fig_scatter, use_container_width=True)

            with st.expander("What is this plot?", expanded=False):
                st.info("""
                **Property Correlation (Triangular):** This heatmap shows the correlation between different molecular properties, including **pIC50**. 
                - **Red squares** indicate a strong positive correlation (as one property increases, the other tends to increase).
                - **Blue squares** indicate a strong negative correlation (as one increases, the other decreases).
                - **Triangular format** eliminates redundancy since correlations are symmetric.
                This helps in understanding relationships, for example, how molecular weight might influence PSA, or how pIC50 correlates with other properties.
                """)
            fig_heatmap = molecular_analysis.plotly_correlation_heatmap(filtered_df)
            st.plotly_chart(fig_heatmap, use_container_width=True)

        with col2:
            with st.expander("What is this plot?", expanded=False):
                st.info("""
                **Property Distributions:** These histograms show the frequency distribution of each key molecular property, including **pIC50**. This is useful for understanding the overall character of the dataset. Are the compounds generally large or small? Potent or not? This gives a high-level chemical snapshot of the library.
                """)
            fig_hist = molecular_analysis.plotly_property_histograms(filtered_df)
            st.plotly_chart(fig_hist, use_container_width=True)

            with st.expander("What is this plot?", expanded=False):
                st.info("""
                **Drug-Likeness Comparison:** These box plots compare the property distributions (MW, LogP, and **pIC50**) for compounds that pass Lipinski's Rule of Five ('True') versus those that don't ('False'). This can reveal if, for example, the more potent compounds (higher pIC50) tend to fall outside the 'drug-like' space, which is a critical consideration for development.
                """)
            fig_box = molecular_analysis.plotly_drug_likeness_boxplots(filtered_df)
            st.plotly_chart(fig_box, use_container_width=True)

        # --- Molecular Property Distribution by Target ---
        st.header("Molecular Property Distribution by Target")
        with st.expander("What is this plot?", expanded=False):
            st.info("""
            **Molecular Property Distribution by Target (Violin Plots):** These plots show the distribution of key molecular properties (Molecular Weight, LogP, pIC50, Hydrogen Bond Donors, Hydrogen Bond Acceptors, Polar Surface Area) for compounds active against different drug targets.
            - Each "violin" represents the distribution of a property for a specific target.
            - The width of the violin indicates the density of compounds at that property value.
            - The box plot inside each violin shows the median (white dot) and interquartile range (thick bar).
            This visualization is crucial for understanding the **target-specific chemical space** and identifying if certain targets prefer compounds with distinct physicochemical profiles. For example, some targets might be best inhibited by smaller, more lipophilic compounds, while others might require larger, more polar molecules.
            """ )
        fig_violin = molecular_analysis.plotly_property_distribution_by_target(filtered_df)
        st.plotly_chart(fig_violin, use_container_width=True)

        # --- Advanced 2D Density Plot ---
        st.header("Advanced 2D Density Analysis")
        with st.expander("What is this plot?", expanded=False):
            st.info("""
            **2D Density Heatmap:** This plot visualizes the density of compounds across the physicochemical space defined by Molecular Weight and LogP. 
            - **Hotter areas** (yellow/bright) indicate a high concentration of compounds with similar properties.
            - **Cooler areas** (purple/dark) represent regions with fewer compounds.
            This is more effective than a simple scatter plot for large datasets as it avoids overplotting and clearly reveals the most populated and promising regions of chemical space.
            """ )
        fig_density = molecular_analysis.plotly_mw_logp_density_heatmap(filtered_df)
        st.plotly_chart(fig_density, use_container_width=True)

    else:
        st.warning("No data matches the current filter settings.")

else:
    st.info("Click the button in the sidebar to load the sample dataset, or upload your own data to start.")
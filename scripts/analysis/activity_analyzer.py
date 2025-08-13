import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

def analyze_activity_relationships(input_csv_path, output_dir):
    """
    Analyzes the relationship between molecular properties and drug activity (IC50).

    Args:
        input_csv_path (str): Path to the input CSV file with IC50 values.
        output_dir (str): Directory to save the output plots and data.
    """
    try:
        # Read the data
        df = pd.read_csv(input_csv_path)

        # Convert IC50 to pIC50
        # ChEMBL IC50 values are typically in nM. pIC50 = -log10(IC50 * 1e-9)
        df['pIC50'] = -np.log10(df['ic50'] * 1e-9)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Properties to analyze
        properties = ['mw', 'logp', 'hbd', 'hba', 'psa']

        # Create scatter plots
        for prop in properties:
            plt.figure(figsize=(8, 6))
            sns.scatterplot(x=df[prop], y=df['pIC50'])
            plt.title(f'{prop.upper()} vs. pIC50')
            plt.xlabel(prop.upper())
            plt.ylabel('pIC50')
            plot_path = os.path.join(output_dir, f'{prop}_vs_pIC50.png')
            plt.savefig(plot_path)
            plt.close()
            print(f"Saved scatter plot to {plot_path}")

        # Calculate and save correlation matrix
        correlation_matrix = df[properties + ['pIC50']].corr()
        print("\nCorrelation Matrix:")
        print(correlation_matrix)
        corr_matrix_path = os.path.join(output_dir, 'correlation_matrix.csv')
        correlation_matrix.to_csv(corr_matrix_path)
        print(f"\nSaved correlation matrix to {corr_matrix_path}")

    except FileNotFoundError:
        print(f"Error: The file {input_csv_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze drug activity relationships.')
    parser.add_argument('input_csv', type=str, help='Path to the input CSV file with compound data and IC50 values.')
    parser.add_argument('output_dir', type=str, help='Directory to save the output plots and correlation data.')
    args = parser.parse_args()

    analyze_activity_relationships(args.input_csv, args.output_dir)

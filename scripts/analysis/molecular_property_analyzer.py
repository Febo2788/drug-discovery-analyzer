import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

def analyze_molecular_properties(input_csv_path, output_plot_dir):
    """
    Analyzes the molecular properties from the ChEMBL data.

    Args:
        input_csv_path (str): Path to the input CSV file.
        output_plot_dir (str): Directory to save the output plots.
    """
    try:
        # Read the data
        df = pd.read_csv(input_csv_path)

        # Calculate summary statistics
        summary_stats = df.describe()
        print("Summary Statistics:")
        print(summary_stats)

        # Create output directory if it doesn't exist
        os.makedirs(output_plot_dir, exist_ok=True)

        # Plot distributions of molecular properties
        properties_to_plot = ['mw', 'logp', 'hbd', 'hba', 'psa']
        for prop in properties_to_plot:
            plt.figure(figsize=(8, 6))
            sns.histplot(df[prop].dropna(), kde=True)
            plt.title(f'Distribution of {prop.upper()}')
            plt.xlabel(prop.upper())
            plt.ylabel('Frequency')
            plot_path = os.path.join(output_plot_dir, f'{prop}_distribution.png')
            plt.savefig(plot_path)
            plt.close()
            print(f"Saved {prop} distribution plot to {plot_path}")

    except FileNotFoundError:
        print(f"Error: The file {input_csv_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze molecular properties from ChEMBL compound data.')
    parser.add_argument('input_csv', type=str, help='Path to the input CSV file from ChEMBL.')
    parser.add_argument('output_dir', type=str, help='Directory to save the output plots.')
    args = parser.parse_args()

    analyze_molecular_properties(args.input_csv, args.output_dir)

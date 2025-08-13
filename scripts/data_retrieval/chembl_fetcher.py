import pandas as pd
from chembl_webresource_client.new_client import new_client
import argparse
import sys

def fetch_and_save_compounds(target_names, output_path):
    """
    Fetches compound data for a list of targets from ChEMBL and saves it as a single CSV file.

    Args:
        target_names (list): A list of target protein names (e.g., ['EGFR', 'SRC']).
        output_path (str): The file path to save the combined CSV data.
    """
    target_client = new_client.target
    activity_client = new_client.activity
    molecule_client = new_client.molecule
    
    all_target_dfs = []

    for target_name in target_names:
        print(f"--- Processing Target: {target_name} ---")
        try:
            # Search for the target
            print(f"Searching for target: {target_name}")
            target_results = target_client.search(target_name)

            if not target_results:
                print(f"Warning: Target '{target_name}' not found. Skipping.", file=sys.stderr)
                continue

            target_info = target_results[0]
            target_chembl_id = target_info['target_chembl_id']
            print(f"Found target: {target_info['pref_name']} ({target_chembl_id})")

            # Fetch activities
            print("Fetching activities...")
            activities = activity_client.filter(target_chembl_id=target_chembl_id, standard_type="IC50")

            if not activities:
                print(f"No IC50 activities found for target '{target_name}'. Skipping.", file=sys.stderr)
                continue

            # Process activities to get unique molecules and average IC50
            activity_data = {}
            for a in activities:
                mol_id = a.get('molecule_chembl_id')
                val = a.get('standard_value')
                if mol_id and val:
                    if mol_id not in activity_data:
                        activity_data[mol_id] = []
                    activity_data[mol_id].append(float(val))
            
            for mol_id, values in activity_data.items():
                activity_data[mol_id] = sum(values) / len(values)

            molecule_ids = list(activity_data.keys())
            print(f"Found {len(molecule_ids)} unique molecules with IC50 values.")

            # Fetch molecule properties
            print("Fetching molecule properties...")
            molecules = list(molecule_client.filter(molecule_chembl_id__in=molecule_ids).only(['molecule_chembl_id', 'pref_name', 'molecule_properties']))

            if not molecules:
                print("Could not retrieve molecule details. Skipping.", file=sys.stderr)
                continue

            # Prepare data for DataFrame
            data = []
            for m in molecules:
                props = m.get('molecule_properties')
                mol_id = m.get('molecule_chembl_id')
                if props and mol_id in activity_data:
                    data.append({
                        'chembl_id': mol_id,
                        'name': m.get('pref_name'),
                        'target': target_name,
                        'ic50': activity_data[mol_id],
                        'mw': props.get('mw_freebase'),
                        'logp': props.get('alogp'),
                        'hbd': props.get('hbd'),
                        'hba': props.get('hba'),
                        'psa': props.get('psa')
                    })
            
            df = pd.DataFrame(data)
            all_target_dfs.append(df)
            print(f"Successfully processed {len(df)} compounds for {target_name}.")

        except Exception as e:
            print(f"An error occurred while processing {target_name}: {e}", file=sys.stderr)
    
    if not all_target_dfs:
        print("No data was fetched for any of the specified targets.", file=sys.stderr)
        return

    # Combine all dataframes and save
    final_df = pd.concat(all_target_dfs, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    print(f"\nTotal of {len(final_df)} compounds from {len(all_target_dfs)} targets saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch ChEMBL compound data for one or more targets.')
    parser.add_argument('--targets', nargs='+', required=True, help='One or more target names to search for (e.g., EGFR SRC).')
    parser.add_argument('--output', type=str, required=True, help='The path to the output CSV file.')
    args = parser.parse_args()

    fetch_and_save_compounds(args.targets, args.output)
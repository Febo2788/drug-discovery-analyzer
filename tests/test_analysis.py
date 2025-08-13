
import pandas as pd
import pytest
import sys
import os

# Add project root to path to allow importing analysis script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.analysis import molecular_analysis

@pytest.fixture
def sample_compounds():
    """Provides a sample DataFrame for testing."""
    data = {
        'chembl_id': ['CHEMBL1', 'CHEMBL2', 'CHEMBL3', 'CHEMBL4'],
        'name': ['Drug A', 'Drug B', 'Drug C', 'Drug D'],
        'ic50': [10.5, 200.0, 600.0, 150.0],
        'mw': [450.0, 510.0, 620.0, 400.0],       # B violates MW
        'logp': [4.5, 4.8, 5.5, 6.0],             # C violates LogP, D violates LogP
        'hbd': [4, 5, 6, 3],                      # C violates HBD
        'hba': [8, 9, 11, 12],                    # C violates HBA, D violates HBA
        'psa': [90.0, 120.0, 150.0, 110.0]
    }
    return pd.DataFrame(data)

def test_calculate_lipinski(sample_compounds):
    """Tests the calculation of Lipinski's Rule of Five violations."""
    # Arrange
    df = sample_compounds

    # Act
    result_df = molecular_analysis.calculate_lipinski(df)

    # Assert
    # Expected violations: A=0, B=1, C=4, D=2
    expected_violations = [0, 1, 4, 2]
    expected_drug_like = [True, False, False, False]

    assert 'lipinski_violations' in result_df.columns
    assert 'is_drug_like' in result_df.columns
    assert result_df['lipinski_violations'].tolist() == expected_violations
    assert result_df['is_drug_like'].tolist() == expected_drug_like

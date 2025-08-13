
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-12

### Added
- **Interactive Web Dashboard:** Created a full-featured dashboard with Streamlit (`app.py`) for interactive data exploration.
- **Advanced Visualizations:** Implemented interactive plots with Plotly for a more dynamic user experience.
- **In-App Documentation:** Added an "About this Project" section and detailed explanations for each analysis directly in the UI.
- **Enhanced Filtering:** Included multiple interactive widgets to filter compounds by drug-likeness and various molecular property ranges.
- **Professional Documentation:** Overhauled the `README.md` to include screenshots, technical details, and usage instructions.
- **Containerization:** Added a `Dockerfile` and `.dockerignore` for easy, reproducible deployment.
- **Unit Testing:** Created a test suite (`tests/test_analysis.py`) using `pytest` to ensure the correctness of the analysis logic.
- **Changelog:** This `CHANGELOG.md` file was created to track the project's evolution.

### Changed
- **Modularized Plotting:** Refactored the analysis script to support both static (Matplotlib) and interactive (Plotly) plot generation.
- **Improved UI/UX:** Replaced the data loading checkbox with a more intuitive button and organized the layout for clarity.

## [0.1.0] - 2025-08-11

### Added
- **Data Retrieval Core:** Implemented the initial script (`scripts/data_retrieval/chembl_fetcher.py`) to download compound data from the ChEMBL database.
- **Initial Data Analysis:** Created the first version of the analysis script (`scripts/analysis/molecular_analysis.py`) to perform Lipinski and statistical calculations.
- **Static Visualizations:** Generated initial plots using Matplotlib and Seaborn.
- **Dependency Management:** Established the `requirements.txt` file.

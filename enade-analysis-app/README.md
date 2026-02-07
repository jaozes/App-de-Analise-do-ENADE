# Enade Analysis App

## Overview
The Enade Analysis App is a Streamlit application designed to analyze and visualize data from the National Student Performance Exam (Enade) in Brazil. The application provides users with the ability to explore various aspects of the Enade data, including comparisons between different courses and a comprehensive analysis of the entire dataset.

## Project Structure
The project consists of the following files and directories:

- **pages/**: Contains the different pages of the application.
  - **home.py**: Home page providing an overview of the project and navigation instructions.
  - **comparison.py**: Analysis page for comparing Enade data using various filters.
  - **brazil_analysis.py**: Page dedicated to a fixed analysis of all Enade data in Brazil.

- **data/**: Contains the dataset used for analysis.
  - **conceito_enade_2023.xlsx**: The Excel file containing the Enade data.

- **utils/**: Contains utility functions for data processing.
  - **filters.py**: Functions for filtering the Enade data based on user selections.

- **app.py**: The main entry point of the Streamlit application, responsible for page routing and layout.

- **requirements.txt**: Lists the dependencies required to run the application.

## Setup Instructions
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
4. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

## Usage Guidelines
- Upon launching the application, users will be directed to the home page, where they can find information about the project and how to navigate through the analysis.
- Users can access the comparison page to filter and compare Enade data based on various criteria.
- The Brazil analysis page provides insights and visualizations relevant to the entire dataset, allowing users to understand trends and patterns across all Enade data.

## Contributing
Contributions to the Enade Analysis App are welcome! Please feel free to submit issues or pull requests to enhance the functionality and usability of the application.
Data Quality Pipeline

A simple, modular data quality pipeline built with Python.
The project includes a workflow engine, reusable tools, and a sample workflow that processes CSV data.

📁 Project Structure
app/
  __init__.py
  main.py
  engine.py
  tools.py

workflows/
  data_quality_workflow.py

sample_data/
  sample.csv

scripts/
  run_sample.sh

requirements.txt
README.md

🚀 Installation
git clone <your_repo_url>
cd data_quality_pipeline

python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

pip install -r requirements.txt

▶️ Running the Pipeline
Option 1 — Run directly
python app/main.py

Option 2 — Run as a module
python -m app.main

Option 3 — Using the script
sh scripts/run_sample.sh

📊 Sample Data

A sample CSV file is included in sample_data/sample.csv for testing the workflow.

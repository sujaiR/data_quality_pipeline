Data Quality Pipeline – Workflow Engine (Tredence AI Engineering Assignment)
1. Problem Understanding

The objective of the assignment is to design and implement a minimal workflow engine in Python (FastAPI) that can:

Create workflows (graphs)

Execute workflows node-by-node

Allow each node to run a tool function

Maintain run state across nodes

Support conditional branching

Expose the engine through APIs

To demonstrate the engine, the assignment requires building a Data Quality Pipeline with stages such as:

Profiling data

Detecting anomalies

Generating data-quality rules

Applying rules

Re-running until data is clean

This repository delivers a complete, ready-to-run solution that meets all the above requirements.

2. Key Features
✅ Minimal Workflow (DAG) Execution Engine

Node execution one-by-one

Tools registry for attaching Python functions

Supports conditional branching (if anomaly_count > 0 → loop back)

✅ FastAPI Application

Exposes:

Endpoint	Description
POST /graph/create	Create a custom graph
POST /graph/create/sample	Create the sample Data Quality graph
POST /graph/run	Execute a graph
GET /graph/state/{run_id}	Get current run state
✅ Rule-Based Data Quality Pipeline

Includes:

Data profiling

Simple anomaly detection

Basic rule generation

Rule application

Loop until data is clean

✅ Clean, Modular, Human-Readable Code

Designed to look hand-written, with:

Small functions

Clear variable names

Logical module separation

3. Project Structure
data_quality_pipeline/
│
├── app/
│   ├── engine.py                     # Minimal workflow/graph engine
│   ├── tools.py                      # Tool registry + DQ functions
│   ├── main.py                       # FastAPI app + endpoints
│   └── workflows/
│       └── data_quality_workflow.py  # Pre-built DQ workflow graph
│
├── sample_data/
│   └── sample.csv
│
├── scripts/
│   └── run_sample.sh
│
├── requirements.txt
└── README.md

4. How to Run the Application

This project runs locally, VS Code, or GitHub Codespaces.

Step 1 – Install Dependencies

Inside your project folder:

pip install -r requirements.txt

Step 2 – Start FastAPI server

Run:

uvicorn app.main:app --reload --port 8000


If running in Codespaces:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Step 3 – Open API Docs

Open in browser:

http://localhost:8000/docs


This provides a full interactive Swagger UI.

5. Sample Workflow Execution
Create Sample Graph
curl -X POST http://localhost:8000/graph/create/sample

Run Data Quality Pipeline
curl -X POST http://localhost:8000/graph/run \
-H "Content-Type: application/json" \
-d "{\"initial_state\": {\"data_csv\": \"id,name,age,salary\n1,Alice,30,70000\n2,Bob,,\n3,Charlie,25,50000\"}}"

Check Run State
curl http://localhost:8000/graph/state/<run_id_here>

6. Data Quality Pipeline Logic
Node 1 → profile_data

Reads CSV

Computes missing counts

Samples values

Saves internal rows

Node 2 → detect_anomalies

Finds:

Missing ages

Non-numeric salary

Impossible age values (>120)

Node 3 → generate_rules

Creates simple rules such as:

Fill missing ages with median

Replace invalid salaries with 0

Node 4 → apply_rules

Fixes the dataset accordingly.

Loop Condition
if anomaly_count > 0 → go back to detect
else → end

7. Example Graph Definition
{
  "start": "profile",
  "nodes": {
    "profile": { "fn": "profile_data", "next": "detect" },
    "detect": { "fn": "detect_anomalies", "next": "generate" },
    "generate": { "fn": "generate_rules", "next": "apply" },
    "apply": {
      "fn": "apply_rules",
      "next": {
        "cond_key": "anomaly_count",
        "op": "gt",
        "value": 0,
        "true": "detect",
        "false": null
      }
    }
  }
}

8. What Can Be Improved (Future Scope)

Given more time, the following enhancements would elevate the engine:

Engine

Node parallelism

Retry logic

Persisting workflow runs (SQLite/Postgres)

WebSocket logs

Data Quality

Richer anomaly detection

Schema validation

Configurable rule templates

Automated rule suggestions

UI

Visual workflow designer

Real-time run monitoring

# MAGNA AI Maintenance Assistant

Technical portfolio case study of a maintenance decision-support prototype developed for MAGNA Hackathon 2026.

[Read the English presentation (PDF)](MAGNA_AI_Maintenance_Assistant.pdf)

## Run the public demo

This standalone Streamlit app uses synthetic readings and deterministic rules. It runs locally without Oracle, an OpenAI key or a network connection after dependencies are installed.

With Python 3.10 or newer installed, run these commands from the repository folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

- **Demo A** contains 80 readings across eight units. Five deviations occur on one unit. The app cites the five readings and leaves the cause undetermined with low confidence.
- **Demo B** shows a recurring deviation across units and a missing reading. Turn off **Show only readings cited in the finding** to see the unknown status in the evidence table.

`diagnostics.py` handles tolerance checks and per-unit counts. `evidence.py` validates that citations resolve to the selected readings and produces a preliminary finding. The Streamlit interface shows the result alongside its sources.

Run the diagnostic tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```


## What the hackathon prototype does

A production technician selects a station and reviews measured deviations, recent history and possible diagnostic checks in a Streamlit interface. Python compares readings from Oracle against configured limits and reports each result as in range, out of range or unknown. The history analysis checks whether deviations cluster on one unit or recur across several serial numbers.

## How the system works

1. **Retrieve and analyse.** Python loads the selected Oracle measurements, classifies them against configured limits and summarises the history.
2. **Generate an explanation.** The OpenAI Responses API receives structured diagnostic context and drafts findings, uncertainty and proposed checks.
3. **Validate and review.** Python validates evidence references and applies rules based on the recorded history. The technician reviews the evidence before making a maintenance decision.

The prototype uses Python, Oracle Database, Docker, pandas, Plotly, Streamlit and the OpenAI Responses API. An optional local Isolation Forest prototype scores unusual measurements for exploratory review.

## Anonymised example

Five out-of-range readings occurred on one of eight units in a set of 80 measurements. The prototype classified the cause as undetermined with low confidence. The concentration justified further investigation of the unit and its process conditions.

## Scope

This repository contains the portfolio presentation and a standalone synthetic demo. The case uses aggregate counts with station and product identifiers removed. The prototype supports investigation and does not control equipment or perform repairs. Qualified technicians follow approved procedures for any physical intervention. Production performance and business impact remain unmeasured.


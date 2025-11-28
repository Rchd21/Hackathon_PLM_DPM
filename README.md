📘 Regulatory GPS – UNECE R67 Compliance Assistant

A local AI-powered tool to extract, structure and analyze automotive regulatory requirements using UNECE R67.


---

🚀 Overview

This project is a complete Proof-of-Concept (POC) demonstrating automated regulatory compliance analysis for UNECE Regulation R67, focused on LPG vehicle systems.

It includes:

Streamlit UI

Local LLM processing via Mistral / Ollama

Automatic requirement extraction

Engineering reformulation

Impact analysis (components, tests, documents)

Full traceability tracking

Renault-styled dark sidebar UI


The app aims to serve as a "Regulatory GPS", helping engineers understand obligations, their technical impacts, and compliance status — completely offline, with no cloud dependency.


---

📂 Project Structure

Hackathon_PLM_DPM/
│
├── app.py                    # Streamlit front-end
├── data_store.py             # In-memory DB for regulations & requirements
├── nlp_extractor.py          # AI requirement extraction (Mistral via Ollama)
├── impact_engine.py          # Automated impact analysis
├── models.py                 # Dataclasses for core entities
├── r67_full.txt              # Extracted UNECE R67 text
├── R67.pdf                   # Source regulation (PDF)
└── requirements.txt          # Python dependencies


---

🧠 Features

1. Regulation Viewer

Displays full UNECE R67 regulatory text

Shows metadata (ID, issuer, version, date, official link)

Clean engineering-oriented layout


2. AI-Based Requirement Extraction

Powered by Mistral (local) running in Ollama, the system:

Extracts obligations and “shall” statements

Splits them into atomic, testable system requirements

Reformulates into engineering language

Generates requirement IDs (e.g., R67-1, R67-2…)

Stores results in the internal database


No API keys. No cloud. Fully local NLP.


---

3. Impact Analysis Engine

Each requirement is analyzed to infer:

Impacted components

Required tests and validations

Required documentation

Criticality level (HIGH, MEDIUM, LOW)

Recommended V&V actions


Based on intelligent keyword mapping (tank, valve, pressure, fire, documentation…).


---

4. Traceability & Auditability

Every created requirement generates:

A timestamp

A version number

A change type

A summary


The dedicated traceability page includes:

Full requirement history

Compliance metrics

Change distribution charts



---

🛠 Installation

1. Clone the repository

git clone https://github.com/Rchd21/Hackathon_PLM_DPM
cd Hackathon_PLM_DPM

2. Install Python dependencies

pip install -r requirements.txt

3. Install Ollama (for local AI)

Download from:
https://ollama.com/download

Pull the Mistral model:

ollama pull mistral

4. Run the app

streamlit run app.py

App available at:
👉 http://localhost:8501


---

🔍 How Requirement Extraction Works

Step 1 — Identify requirement candidates

Lines containing “shall” or explicit obligations are isolated.

Step 2 — AI Reformulation

Mistral rewrites each into clean engineering requirements, ensuring they are:

Atomic

Measurable

Testable

Clear and unambiguous


Step 3 — ID Assignment

If no ID exists in the text, the system generates IDs such as:

R67-1
R67-2
R67-3
...

Step 4 — Storage & Traceability

Each requirement is saved and logged for auditability.


---

📊 Example Output

Engineering Requirement Reformulation

ID	Raw Text	Engineering Requirement

R67-5	The LPG tank shall withstand pressure…	The LPG system shall withstand pressure and fire tests without leakage.


Impact Mapping Example

Requirement	Components	Tests	Documents

R67-5	LPG_TANK, LPG_VALVE	TEST_PRESSURE, TEST_LEAK	DOC_CONFORMITY, DOC_TEST_REPORT



---

📈 Future Enhancements

Cross-country compliance comparison (EU vs. Japan vs. India)

Automatic similarity detection across standards

Test-plan generation from requirements

Integration with product Bill-of-Materials

Automated PDF ingestion and OCR


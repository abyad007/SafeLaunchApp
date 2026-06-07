# Versigent Safe Launch Generator — Local Setup

## What this is
A local Python web app that generates Safe Launch plans, risk scores,
PowerPoint reports and Excel checklists — based on your Aptiv procedures.
Runs entirely on your laptop. No internet needed after install.

---

## Step 1 — Install Python (if not already installed)
1. Go to https://python.org/downloads
2. Download Python 3.11 or newer
3. During install — CHECK the box "Add Python to PATH"
4. Verify in a terminal: `python --version`

---

## Step 2 — Create the project folder
Create this folder anywhere on your laptop (e.g. Desktop):

```
SafeLaunchApp/
```

Copy all the files from this package into it.
The structure should look like this:

```
SafeLaunchApp/
  app.py
  requirements.txt
  core/
    __init__.py
    scoring_engine.py
    checklist_loader.py
    report_generator.py
    customer_rules.py
  data/
    procedures/        ← PUT YOUR PROCEDURE FILES HERE
    templates/         ← PUT Versigent_MasterTemplate.pptx HERE
    plans/
  output/
```

---

## Step 3 — Upload your procedure files
Copy these files into `data/procedures/`:

| File | Program Type |
|------|-------------|
| EAGP_4-4_MG_01-F01_EN.xlsx     | Business Transfer |
| HOGP_5-1_MG-EDS_01-F01_EN.xlsx | Restart After Shutdown |
| EAGP_5-3_ME_02_EN.xlsx         | Capacity Change |
| EANP_4-1_CS_01-03_EN.pptx     | New Program |
| EAEP_4-1_ME-EDS_10-01_EN.pptx | Engineering Change |

Copy your branding file into `data/templates/`:
- `Versigent_MasterTemplate.pptx`

**The app works without these files** — it falls back to built-in checklists.
Files just make the checklists come directly from the procedure documents.

---

## Step 4 — Install required libraries
Open a terminal (Command Prompt or PowerShell on Windows):

```bash
# Navigate to the project folder
cd C:\Users\YourName\Desktop\SafeLaunchApp

# Install everything in one command
pip install -r requirements.txt
```

This installs:
- streamlit     — the web UI framework
- python-pptx   — generates PowerPoint files
- openpyxl      — reads/writes Excel files
- reportlab     — generates PDF files
- pillow        — image handling
- pandas        — data manipulation
- plotly        — interactive charts

---

## Step 5 — Run the app
In the same terminal:

```bash
streamlit run app.py
```

Your browser opens automatically at:
**http://localhost:8501**

---

## How to stop the app
Press `Ctrl + C` in the terminal.

## How to restart
```bash
streamlit run app.py
```

---

## Troubleshooting

**"streamlit is not recognized"**
→ Run: `pip install streamlit` and try again.
→ Or try: `python -m streamlit run app.py`

**"ModuleNotFoundError: No module named 'pptx'"**
→ Run: `pip install python-pptx`

**Port already in use**
→ Run: `streamlit run app.py --server.port 8502`
→ Then open: http://localhost:8502

**Template not found (PPT export has no branding)**
→ Copy `Versigent_MasterTemplate.pptx` to `data/templates/`
→ The app still works without it — just without the wave art background.

---

## File structure explained

| File | What it does |
|------|-------------|
| `app.py` | Main UI — all Streamlit widgets and layout |
| `core/scoring_engine.py` | Risk scoring logic per program type |
| `core/checklist_loader.py` | Reads checklists from Excel or built-in fallback |
| `core/report_generator.py` | Builds PPT and Excel output files |
| `core/customer_rules.py` | OEM-specific requirements (VW, Renault, etc.) |

---

## Adding a new customer

Open `core/customer_rules.py` and add a new entry:

```python
"bmw": {
    "name": "BMW Group",
    "score_bonus": 8,
    "color": "#0066B2",
    "items": [
        "BMW SQS (Supplier Quality Standard)",
        "Formel Q — compatibility check",
        ...
    ],
    "gates": ["SB", "CD", "CA", "FA", "PA", "CT"],
},
```

Then add `"bmw": "BMW Group"` to `CUSTOMER_OPTIONS` in `app.py`.
No other changes needed.

---

## Updating a scoring weight

Open `core/scoring_engine.py`.
Each function has clearly labelled score maps at the top:

```python
# Example — change Business Transfer receiving plant weights:
recv_map = {"mature": 5, "intermediate": 12, "new": 22}
#                    ↑                    ↑           ↑
#               change these numbers to adjust risk weighting
```

Save the file and refresh the browser. Changes take effect immediately.

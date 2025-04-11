# SLACK APP TEAM 46

### Clone Repo.
```
git clone https://github.com/Sign0ret/slack-hooks.git
cd slack-hooks
```
### Dev Setup.
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```
finally add the .env file following the .env.example
### Executing using single script.
```
python run.py --dev
```
```
python run.py
```

###  Executing using separated commands.
To run Backend.
```
uvicorn app:app --host 127.0.0.1 --port 8000
```
To run Frontend.
```
streamlit run dashboard.py
```
watch the dashboard at http://localhost:8501

### Upload from URL examples: 
- https://drive.google.com/uc?export=download&id=1Sq-pRzH_mr_bSEYmDWdL7u3KWVePY12u

- https://arxiv.org/pdf/2504.07933.pdf

- https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
## TEAM Contributors.
- Carlos Iván Armenta Naranjo - A01643070
- Jorge Javier Blásquez Gonzalez - A01637706 
- Adolfo Hernández Signoret - A01637184
- Arturo Ramos Martínez - A01643269
- Moisés Adrián Cortés Ramos - A01642492
- Bryan Ithan Landín Lara - A01636271
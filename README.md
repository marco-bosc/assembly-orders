# assembly-orders

1. Aggiungi sempre a .gitignore:

venv/
.env/

2. Usa requirements.txt

Ogni volta che installi/rimuovi librerie, aggiorna il file dei requisiti:
source venv/bin/activate
pip freeze > requirements.txt

3. Crea la cartella .devcontainer

Nella root del tuo repo aggiungi una cartella:
.devcontainer/

4. Crea il file devcontainer.json

Dentro .devcontainer/ crea devcontainer.json con questo contenuto minimo:

{
  "name": "Python Dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",

  "postCreateCommand": "python -m venv venv && . venv/bin/activate && pip install -r requirements.txt"
}
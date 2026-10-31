import json
from pathlib import Path
from datetime import datetime,timezone

 # chemin du fichier 
LOG_FILE = Path("ingestion/ingestion_log.json")
DATA_DIR = Path("data/raw")

def load_ingestion_log():
    """ charge le journal d'ingestion """

    with open(LOG_FILE,"r") as file :
        log = json.load(file) 
        return log

def is_already_ingested(filename) :
    """verification si le fichier est déjà ingerer"""

    log = load_ingestion_log()

    for file in log["files"]:
        if file["filename"] == filename and file["status"]=="success" :
            return True
    return False

def register_ingestion(filename,period):
    """enregistrer une ingestion dans le log """

    file_path = DATA_DIR / filename

    #verification si le fichier existe 

    if not file_path.is_file():
        raise FileNotFoundError(f"fichier introuvable :{file_path}")

    #verfication si le fichier est deja enregistre 

    if is_already_ingested(filename) :
        print(f"{filename} est déjà ingéré.")
        return

    log = load_ingestion_log()

    info = {
        "filename": filename ,
        "periode" : period ,
        "status" : "success",
        "ingested_at" : datetime.now(timezone.utc).isoformat()
    }

    log['files'].append(info)

    with open(LOG_FILE, "w") as file:
        json.dump(log, file, indent=4)

    print(f"Ingestion enregistrée : {filename}")





print(register_ingestion(
        filename="yellow_tripdata_2026-01.parquet",
        period="2026-01" ))
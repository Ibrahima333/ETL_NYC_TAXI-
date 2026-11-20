import json
from pathlib import Path
from datetime import datetime,timezone
import requests
import pyarrow.parquet as pq
from ingestion.s3_client import upload_file_to_s3, BUCKET_NAME

 # chemin du fichier 
LOG_FILE = Path("ingestion/ingestion_log.json")

# Dossier de destination
DATA_DIR = Path("data/raw")

# URL de téléchargement
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

# Fichier à télécharger
FILENAME = "yellow_tripdata_2026-01.parquet"


def load_ingestion_log():
    """ charge le journal d'ingestion """

    with open(LOG_FILE,"r") as file :
        log = json.load(file) 
        return log

def is_already_ingested(filename) :
    """ verification si le fichier est déjà ingerer """

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


def download_file(filename):
    """ Télécharge un fichier depuis NYC TLC
    et le sauvegarde dans data/raw/.
    """

    # Construire l'URL complète
    url = f"{BASE_URL}/{filename}"

    # Construire le chemin de destination
    file_path = DATA_DIR / filename

    # Créer le dossier s'il n'existe pas
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Envoyer la requête HTTP stream=true pour eviter de telecharger le fichier en un coup enfin de ne pas surcherger la memoire
    response = requests.get(url, stream=True, timeout=60)

    # Vérifier si la requête a réussi
    response.raise_for_status()

    # Écrire progressivement le fichier
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    print(f"Téléchargement terminé : {filename}")

    return file_path

def validate_parquet(file_path):
    """
    Vérifie que le fichier est un Parquet exploitable.
    """

    try:
        parquet_file = pq.ParquetFile(file_path)

        # Récupérer les métadonnées
        metadata = parquet_file.metadata

        # Vérifier que le fichier contient des données
        if metadata.num_rows == 0:
            raise ValueError("Le fichier Parquet est vide.")

        print("Validation Parquet réussie.")
        print(f"Nombre de lignes : {metadata.num_rows}")
        print(f"Nombre de colonnes : {len(parquet_file.schema)}")

        return True

    except Exception as e:

        print(f"Erreur de validation : {e}")
        return False

    

if __name__ == "__main__":

    filename = "yellow_tripdata_2026-03.parquet"
    period = "2026-03"

    # Vérifier si le fichier est déjà ingéré
    if is_already_ingested(filename):

        print(f"{filename} est déjà ingéré.")

    else:

        # Télécharger le fichier
        file_path = download_file(filename)

        #verification si le fichier est valide 
        if validate_parquet(file_path) :
         
            try:
                # Envoyer le fichier vers RustFS
                upload_file_to_s3(
                file_path,
                BUCKET_NAME,
                filename )


                print(f"Copie locale supprimée : {filename}")

                # Enregistrer l'ingestion
                register_ingestion(filename, period)

                # Supprimer la copie locale
                file_path.unlink()
                
            except Exception as error :
                    print(f"Erreur pendant l'ingestion : {error}")
                    print("La copie locale est conservée.")




    
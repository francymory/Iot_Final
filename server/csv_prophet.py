import csv
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from server_AI import Presenza, db, app, Predizione
import pandas as pd
import prophet 
from matplotlib import pyplot as plt
import os
import plotly.graph_objs as go



def make_daily_prediction():

    path = 'dati_parchi.csv'
    df = pd.read_csv(path, header=0)
    frames = []
    for parco_valore in df['zona'].unique():
        frame = df[df['zona'] == parco_valore].copy()
        frame = frame.rename(columns={'ds': 'ds', 'y': 'y'})
        frames.append(frame)

    # Creare e allenare i modelli di Prophet per ciascuna sequenza
    modelli = []
    for frame in frames:
        model = prophet.Prophet()
        model.fit(frame)
        modelli.append(model)

    
    # Creare un dataframe futuro per i giorni successivi includendo tutte le ore.
    num_days = 2 # Qui scelgo di prevedere solo il giorno corrente + successivo
    future_date = datetime.now() 
    future_datetime = pd.date_range(start=future_date.replace(hour=0, minute=0, second=0, microsecond=0), 
                                    periods=24*num_days, freq='h')
    future_df = pd.DataFrame({'ds': future_datetime})


    # Fare le previsioni per ciascuna sequenza
    previsioni = [model.predict(future_df) for model in modelli]
    counter = 0
    # Visualizzare le previsioni per ciascuna sequenza
    for parco_valore, previsione in zip(df['zona'].unique(), previsioni):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=previsione['ds'], y=previsione['yhat'], mode='lines', name='Previsioni'))
        fig.update_layout(title=f'Previsioni per {parco_valore}', xaxis_title='Data', yaxis_title='Numero di persone')
        nome_file_html = f"{parco_valore}_previsioni.html"
        fig.write_html(nome_file_html)
        for y, ds in zip(previsione['yhat'], previsione['ds']):
            n_persone = max(0, int(y))
            predizione = Predizione(n_persone=n_persone, orario=ds, zona=parco_valore)
            db.session.add(predizione)
            db.session.commit()
            counter += 1
        
    print("Ho scritto", counter, "righe nel db per le prossime 24 ore.")
    


    
   
# Funzione per estrarre i dati dal database e creare il file CSV
def create_csv_from_database():
    # Query per estrarre i dati dal database
    data_from_db = Presenza.query.all()

    # Definizione del nome del file CSV
    csv_file_name = 'dati_parchi.csv'

    # Definizione dei campi del file CSV
    fieldnames = ['ds', 'y', 'zona']

    # Se il file non esiste, crealo e scrivi l'intestazione
    if not os.path.exists(csv_file_name):
        with open(csv_file_name, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    # Apertura del file CSV e scrittura dei dati
    with open(csv_file_name, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Dizionario per tenere traccia del numero di persone per zona e orario
        data_dict = {}

        # Iterazione sui dati estratti dal database
        for data in data_from_db:
            # Ottieni la chiave composta da zona e orario
            key = (data.zona, data.orario)

            # Aggiorna il numero di persone per la zona e l'orario corrente
            if key in data_dict:
                data_dict[key] += 1
            else:
                data_dict[key] = 1

        # Scrivi i dati nel file CSV
        for (zona, orario), num_persone in data_dict.items():
            writer.writerow({'ds': orario.strftime("%Y-%m-%d %H:%M:%S"), 'y': num_persone, 'zona': zona})

    print(f"File CSV '{csv_file_name}' aggiornato con successo.")


# Funzione per svuotare la tabella Predizione nel database
def clear_predizione_table():
    # Esegui la query per eliminare tutti i record nella tabella Predizione
    Predizione.query.delete()
    # Conferma le modifiche al database
    db.session.commit()
    print("Tabella Predizione svuotata con successo.")
    


# Funzione per svuotare la tabella Presenza nel database
def clear_presenza_table():
    # Esegui la query per eliminare tutti i record nella tabella Predizione
    Presenza.query.delete()
    # Conferma le modifiche al database
    db.session.commit()
    print("Tabella Presenza svuotata con successo.")



# Eseguire la funzione di creazione del file CSV al momento del caricamento dello script
if __name__ == "__main__":
        with app.app_context():

            clear_predizione_table()
            create_csv_from_database()
            make_daily_prediction()
            clear_presenza_table()
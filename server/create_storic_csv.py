import csv
import random
from datetime import datetime, timedelta

# Definizione dei nomi dei parchi
parchi = ["ParcoResistenza", "ParcoAmendola", "ParcoFerrari"]

# Definizione della data di inizio e fine
data_inizio = datetime(2024, 1, 1)
data_fine = datetime.now()

# Definizione del nome del file CSV
nome_file_csv = "dati_parchi.csv"

# Apertura del file CSV per la scrittura
with open(nome_file_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['ds', 'y', 'zona'])  # Intestazione del file CSV

    # Iterazione su ogni giorno nel periodo specificato
    current_date = data_inizio
    while current_date <= data_fine:
        # Generazione di dati casuali per ogni parco
        for parco in parchi:
            # Impostazione del numero di persone in base all'ora e al giorno
            num_persone = random.randint(0,3)
            
            if(parco=="ParcoResistenza"):
                 if current_date.weekday() == 6:  # 6 rappresenta Domenica
                     num_persone = random.randint(0, 20)

                 if current_date.hour >= 0 and current_date.hour <= 5:
                       num_persone = 0
                 if current_date.hour == 12:
                    num_persone = random.randint(3, 10)
            elif(parco=="ParcoAmendola"):
                 if current_date.weekday() == 5:  # 6 rappresenta Domenica
                     num_persone = random.randint(0, 20)
                 if current_date.hour >= 2 and current_date.hour <= 6:
                       num_persone = 0
                 if current_date.hour >=13 and current_date.hour <= 16:
                    num_persone = random.randint(8, 20)
                 if current_date.hour >=7 and current_date.hour <= 12:
                    num_persone = random.randint(4, 8)

            else:
                if current_date.weekday() == 4:  # 6 rappresenta Domenica
                     num_persone = random.randint(0, 20)
                if current_date.hour >= 3 and current_date.hour <= 5:
                       num_persone = 0
                if current_date.hour >=17 and current_date.hour <= 20:
                    num_persone = random.randint(8, 20)
                if current_date.hour >=11 and current_date.hour <= 14:
                    num_persone = 0

            if current_date.month >=5 and current_date.month <= 10:
                num_persone+=random.randint(0,20)
            
            # Scrittura della riga nel file CSV
            writer.writerow([current_date.strftime("%Y-%m-%d %H:%M:%S"), num_persone, parco])
        
        # Avanzamento alla prossima data
        current_date += timedelta(hours=1)

print(f"File CSV '{nome_file_csv}' creato con successo.")



    
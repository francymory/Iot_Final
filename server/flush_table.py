from server_AI import Braccialetto, db, app

# Funzione per svuotare la tabella Presenza nel database
def clear_braccialetto_table():
    # Esegui la query per eliminare tutti i record nella tabella Predizione
    Braccialetto.query.delete()
    # Conferma le modifiche al database
    db.session.commit()
    print("Tabella Braccialetto svuotata con successo.")



# Eseguire la funzione di creazione del file CSV al momento del caricamento dello script
if __name__ == "__main__":
        with app.app_context():

           clear_braccialetto_table()
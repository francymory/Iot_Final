import sqlite3

# Connessione al database
conn = sqlite3.connect('instance/braccialetti.db')
cursor = conn.cursor()

def stampa(tabella):
    # Esecuzione di una query per ottenere i dati desiderati
    query = f"SELECT * FROM {tabella};"
    cursor.execute(query)

    # Recupero dei risultati della query
    result = cursor.fetchall()

    # Stampa dei dati
    for row in result:
        print(row)

def main():
    while True:
        tabella=input("che tabella vuoi leggere?")
        if(tabella=='fine'):
            # Chiusura della connessione al database
            conn.close()
            print("ciaoooo")
            return 
        else:
            stampa(tabella)

if __name__ == "__main__":
    main()
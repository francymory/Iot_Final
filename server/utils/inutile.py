import requests
import json

print("possibili opzioni: richiesta-get, richiesta-post, svuota-predizione")
opzione=input("cosa faccio?")

if opzione=="richiesta-get":
    url = 'http://192.168.152.201:5000/others/123545'
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    print(response)

elif opzione=="richiesta-post":
# URL del server Flask

    url = 'http://192.168.1.87:5000/data'

    # Dati da inviare nel corpo della richiesta (opzionale, dipende dal tuo endpoint)
    payload = {'id': '123545', 'latitude': '44.6468305','longitude':'10.900594','caduta':'0'}
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(payload)
    # Esempio di una richiesta POST con dati nel corpo
    response = requests.post(url, data=json_data, headers=headers)
    print('Risposta POST:', response.text)

elif opzione=="svuota-predizione":
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from login_app import Predizione

    engine = create_engine('sqlite:///instance/braccialetti.db')

    # 2. Creare una sessione
    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(Predizione).delete()
    session.commit()
    print("ho svuotato la tabella predizione")
else:
    print("diocca non sai scrivere")
    quit

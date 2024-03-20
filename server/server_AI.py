from flask import Flask, request, jsonify, Response, render_template
import json
from flask_sqlalchemy import SQLAlchemy
import string, random
from math import radians, sin, cos, sqrt, atan2 
from datetime import datetime
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///braccialetti.db'
db = SQLAlchemy(app)

swagger_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "Braccialetti API",
        "description": "API per la gestione dei braccialetti",
        "version": "1.0.0"
    },
    "paths": {
        "/data": {
            "post": {
                "summary": "Bridge invia i dati del braccialetto al server",
                "responses": {
                    "200": {"description": "Successo"}
                }
            }
        },
        "/login": {
            "post": {
                "summary": "Bridge effettua procedura di login",
                "responses": {
                    "200": {"description": "Successo"},
                    "400": {"description": "Errore"}
                }
            }
        },
        "/signup": {
            "post": {
                "summary": "Bridge effettua procedura di sign up",
                "responses": {
                    "200": {"description": "Successo"},
                    "400": {"description": "Errore"}
                }
            }
        },
        "/others/{braccialetto_id}": {
            "get": {
                "summary": "Bridge chiede informazioni sugli utenti nelle vicinanze, passando il suo id",
                "parameters": [{
                    "name": "braccialetto_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }],
                "responses": {
                    "200": {"description": "Successo"},
                    "400": {"description": "Errore"}
                }
            }
        }
    }
}

# Endpoint per restituire la specifica Swagger
@app.route('/swagger.json')
def swagger():
    return jsonify(swagger_spec)

# Endpoint per visualizzare l'interfaccia Swagger UI
@app.route('/docs')
def docs():
    return render_template('swagger_ui.html', swagger_url='/swagger.json')


parchi = [
    {"nome":"ParcoFerrari",     "lat":'44.649806',  "long": '10.9073388'},
    {"nome":"ParcoResistenza",  "lat":'44.6286243', "long": '10.9318288'},
    {"nome":"ParcoAmendola",    "lat":'44.6306663', "long": '10.9094288'}
]

# tabella per le predizioni del prophet
class Predizione(db.Model):
    n_persone = db.Column(db.Integer, nullable=False)
    orario = db.Column(db.DateTime, nullable=False)
    zona = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('orario', 'zona', name='pk_predizione'),
    )

# Creo la tabella e le colonne per i braccialetti
class Braccialetto(db.Model):
    identifier = db.Column(db.String(200), primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    caduta = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Braccialetto: {self.identifier}, {self.latitude}, {self.longitude}, {self.caduta}"

# Creo la tabella per il login 
class Utente(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)

class Presenza(db.Model):
    id = db.Column(db.String(15), nullable=False)
    orario = db.Column(db.DateTime, nullable=False)
    zona = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('id', 'orario', 'zona', name='pk_presenza'),
    )
    
# Funzione per calcolare la distanza in metri tra due coordinate GPS
def calcola_distanza(lat1, lon1, lat2, lon2):
    # Raggio della Terra in metri
    R = 6371000
    # Converti le coordinate in radianti
    lat1_rad = radians(float(lat1))
    lon1_rad = radians(float(lon1))
    lat2_rad = radians(float(lat2))
    lon2_rad = radians(float(lon2))
    # Differenze tra le coordinate
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    # Calcola la distanza utilizzando la formula di Haversine
    # che brutta questa distanza geodesica
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distanza = R * c
    return distanza

def get_park(user_lat,user_long):
    best_dist=2000
    best_parco=None
    for parco in parchi:
        dist=calcola_distanza(user_lat,user_long,parco.get('lat'),parco.get('long'))
        if dist<best_dist:
            best_dist=dist
            best_parco=parco
    if best_dist>=2000:
        return None
    return best_parco.get("nome")


# Metto i dati da parte di un braccialetto, spediti con una POST nel bridge, nel DB 
@app.route('/data', methods=['POST'])
def ricevi_richiesta():
    dati_richiesta = request.get_json()
    identifier = dati_richiesta.get('id', '')
    latitude = float(dati_richiesta.get('latitude', '0.0'))
    longitude = float(dati_richiesta.get('longitude', '0.0'))
    cad=dati_richiesta.get("caduta", 0)
    caduta=0
    if cad:
        caduta = True
    else:
        caduta=False
    
    # print(f'stampa prova: ho ricevuto da identifier={identifier}, latitude={latitude}, longitude={longitude}, caduta={caduta}')

    # Cerco il braccialetto nel database
    braccialetto_esistente = Braccialetto.query.filter_by(identifier=identifier).first()

    if braccialetto_esistente:
        # Se esiste già aggiorni i dati del braccialetto esistente
        braccialetto_esistente.latitude = latitude
        braccialetto_esistente.longitude = longitude
        braccialetto_esistente.caduta = caduta
        db.session.commit()
    else:
        # Altrimenti aggiung il braccialetto e i suoi dati nel database
        braccialetto = Braccialetto(identifier=identifier, latitude=latitude, longitude=longitude, caduta=caduta)
        db.session.add(braccialetto)
        db.session.commit()
    
    park_name=get_park(latitude,longitude)
    if park_name:
        current_hour=datetime.now().strftime("%Y-%m-%d %H:00:00")
        current_hour=datetime.strptime(current_hour,"%Y-%m-%d %H:%M:%S")
       
        presenza_esistente = Presenza.query.filter_by(id=identifier,orario=current_hour,zona=park_name).first()

        if not presenza_esistente:
            presenza=Presenza(id=identifier,orario=current_hour,zona=park_name)
            db.session.add(presenza)
            db.session.commit()
    return "Info aggiunte al DB",200
    

# per generare stringhe
def genera_stringa_casuale ():
    lunghezza=10
    caratteri = string.ascii_letters + string.digits
    stringa_casuale = ''.join(random.choice(caratteri) for _ in range(lunghezza))
    return stringa_casuale


# procedura di login
@app.route('/login',methods=['POST'])
def login():
    richiesta = request.get_json()
    username=richiesta.get('username')
    password=richiesta.get('password')
    
    utente = Utente.query.filter_by(username=username,password=password).first()

    if utente:
        j_data=json.dumps({"id":utente.id})
        return Response(j_data,status=200, mimetype='application/json')        # utente valido
    else:
        j_data=json.dumps({"id":0})             # utente o password sbagliata / non esistente
        return Response(j_data,status=400, mimetype='application/json')


# procedura di sign up
@app.route('/signup',methods=['POST'])
def signup():
    richiesta = request.get_json()
    username=richiesta.get('username')
    
    utente = Utente.query.filter_by(username=username).first()

    if utente:
        data=json.dumps({"id":0})  
        return Response(data,status=400, mimetype='application/json')  # username già usato, 400 ERRORE
    
    password=richiesta.get('password')
    id=genera_stringa_casuale()       # genera identificativo
    nuovo_utente = Utente(id=id, username=username, password=password)  # creazione utente
    db.session.add(nuovo_utente)
    db.session.commit()

    data=json.dumps({"id":id})
    return Response(data,status=200, mimetype='application/json')        # utente valido


# Verifico se un braccialetto è isolato, gestisco le GET del bridge
@app.route('/others/<string:braccialetto_id>', methods=['GET'])

def check_isolato(braccialetto_id):

    braccialetto = Braccialetto.query.filter_by(identifier=braccialetto_id).first()
    if braccialetto is None:
        return jsonify({"isolato": 2}), 400     # errore

    # Verifica se il braccialetto è isolato o meno
    altri_braccialetti = Braccialetto.query.filter(Braccialetto.identifier != braccialetto_id).all()
    
    cad = 0
    lat = 0
    long = 0
    vicini = False  # Variabile booleana per tenere traccia se almeno un altro braccialetto è nel raggio d'azione

    for altro_braccialetto in altri_braccialetti:
        distanza = calcola_distanza(braccialetto.latitude, braccialetto.longitude,
                                     altro_braccialetto.latitude, altro_braccialetto.longitude)
        print(f"distanza={distanza}")
    
        if distanza <= 1000:
            vicini = True
            if altro_braccialetto.caduta == 1:
                cad = 1
                lat = altro_braccialetto.latitude
                long = altro_braccialetto.longitude

    # utilizzo dei dati calcolati dal prophet 
    isolato = 0 if vicini else 1
    predizione=1

    if isolato: # se è isolato verifica se si trova in una zona tendenzialmente poco frequentata
        print("braccialetto isolato")
        current_hour=datetime.now().strftime("%Y-%m-%d %H:00:00")
        current_hour=datetime.strptime(current_hour,"%Y-%m-%d %H:%M:%S")
        #current_hour="2026-10-21 23:00:00.000000"      # riga per testing
        print("cerco una predizione dato ", current_hour, "e ", get_park(braccialetto.latitude, braccialetto.longitude))
        predizione = Predizione.query.filter_by(orario=current_hour,zona=get_park(braccialetto.latitude,braccialetto.longitude)).first()
        if predizione:  # se esiste un record
            n_persone=predizione.n_persone  # controlla quante persone ci sono di solito
            if n_persone>0:
                predizione=0
        else:
            predizione=1

    
    # Prepariamo il dizionario dei parametri
    response_data = {
        "isolato": isolato,             # isolato 0 c'è qualcuno, isolato 1 non c'è nessuno
        "predizione": predizione,        # predizione 0 zona affollata, predizione 1 zona deserta
        "caduto": cad,                  # caduto 1 qualcuno è caduto, seguono le coordinate
        "latitude": lat,                
        "longitude": long
    }
    print("invio ", response_data)
    return jsonify(response_data), 200


if __name__ == '__main__':
    with app.app_context():
        
        db.create_all()
        app.run(host='192.168.1.52')

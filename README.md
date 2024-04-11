PASSAGGI:

1. run di server_AI.py che ti crea tabelle e database (o flush_table.py se non è la prima volta che lo runni, andrebbe fatto andare ogni 30 min)
2. run di create_storic_csv.py che ti crea o ricompila il csv dello storico (dati_parchi.csv)
3. run di csv_prophet.py che svuota la tabella predizione, allena e fa le predizioni di prophet
   e le mette nel database nella tabella predizione (ho messo che la predizione è del giorno corrente e del successivo)
4. puoi runnare server_AI.py e connetterti con mit e arduino
5. mentre va server_AI.py per vedere documentazione api vai a http://tuo_ip:5000/docs

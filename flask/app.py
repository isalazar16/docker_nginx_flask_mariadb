from flask import Flask, request
import socket
import mysql.connector
import json

app = Flask(__name__)

@app.errorhandler(400) # http 400 errorea egongo balitz, beheko testua erakutsi
def error400(e):
	return "<h1>Zerbait txarto idatzi duzu</h1>\n<p>Mesedez, berrikusi zure eskaera.</p>\n"

@app.errorhandler(404) # http 404 errorea egongo balitz, beheko testua erakutsi
def error404(e):
	return "<h1>Bilatu duzun helbidea ez da existitzen</h1>\n<p>Hurrengo helbide hauek baino ez dira existitzen: '/db', '/test', '/message'.</p>\n"

@app.errorhandler(500) # http 500 errorea egongo balitz, beheko testua erakutsi
def error500(e):
	return "<h1>Aplikazioak errore bat izan du.</h1>\n"

@app.route("/test", methods=["GET"]) # /test helbidea bilatzen bada GET eskaerarekin, 'ALIVE' + kontainerraren id-a erakutsi
def test():
	html = f"<p> ALIVE {socket.gethostname()}</p>\n"
	return html

@app.route("/message", methods=["POST"]) # /message bilatzen bada POST eskaerarekin, behekoa egin
def post_message():
	data = request.get_json() # Datu basean sartzeko datuak hartu eskaeratik

	config = { # db-ra konektatzeko konfigurazioa
	"host": "mariadb",
	"port": 3306,
	"user": "adminer",
	"password": "adminer",
	"database": "mariadb"
	}
	conn = mysql.connector.connect(**config) # db-arekin konexioa sortu
	cur = conn.cursor() # datuak db-an sartu ahal izateko kurtsorea sortu

	statement = f"insert into erregistroak values (%s, %s, %s)" # Datuak sartzeko SQL komandoa sortu
	try:
		if "From" in data and "Content" in data: # pasatutako jsonak behar dituen parametroak baditu
			cur.execute(statement, (data["From"], data["Content"], socket.gethostname())) # db-an datuak sartu
		else: # bestela, errore mezua erakutsi
			return "<h1>Parametroak txarto sartu dituzu</h1>. <p>'From' eta 'Content' giltzak dituen dict bat bidali behar duzu.</p>\n"
	except mysql.connector.Error as err:
		cur.close()
		return f"Zerbait txarto joan da: {err}"
	conn.commit() # commit egin
	cur.close() #kurtsorea zarratu
	return "<h1>Ondo egin da operazioa</h1>\n" # Operazioa ondo egin dela bueltatu

@app.route("/message", methods=["GET"]) # /message bilatzen bada GET eskaerarekin, behekoa egin
def get_message():
	config = { # db-ra konektatzeko konfigurazioa
	"host":"mariadb",
	"port": 3306,
	"user": "adminer",
	"password": "adminer",
	"database": "mariadb"
	}
	try:
		params = request.args # http eskaerako parametroak hartu
	except:
		return "<h1>Parametroak gaizki sartu dituzu<h1>\n <p>Hauek dira onartzen diren parametroak: 'eduki', 'erabiltzaile', 'ID'.</p>\n"
	# a[4]=nsin #500 errorearea agertzeko, hau deskomentatu eta localhost/message bilatu
	admitted_params = ["eduki", "erabiltzaile", "ID"] # Onartzen diren parametroen lista
	
	conn = mysql.connector.connect(**config) # db-arekin konexioa sortu
	cur = conn.cursor() # datuan db-an sartu ahal izateko kurtsorea sortu
	
	statement = f"select * from erregistroak" # Datuak atzitzeko oinarrizko SQL komandoa sortu
	# apply_par = False
	param_statement = " where "

	for ind,key in enumerate(params): # parametro denak SQL komandoan jarri, behar den bezala, baldin eta parametroak ondo badaude
		if key in admitted_params:
			if ind > 0 and ind < len(params):
				param_statement = param_statement + "and "
			param_statement = param_statement + "{} = '{}' ".format(key, params[key])
		else: # jasotako parametroak ez badaude onartzen direnen artean, errore mezua erakutsi
			return f"<h1>'{key}' parametroa ez da errekonozitu</h1>\n<p>Hauek dira onartzen diren parametroak: 'eduki', 'erabiltzaile', 'ID'.</p>\n"

	if len(params) > 0: # parametroak ezarri badira, SQL komandoaren parametroen zatia, oinarrizko komandoarekin batu
		statement = statement + param_statement

	try:
		cur.execute(statement) # datuak atzitu
	except mysql.connector.Error as err: #errorerik badago, errore mezua erakutsi
		return f"Zerbait txarto joan da: {err} \n" + statement 

	emaitzak = []
	for From, Content, ID in cur: # lortutako emaitzak "emaitzak" listan sartu
		emaitzak.append({"Erabiltzailea":From, "Edukia":Content, "Replikaren ID-a":ID})
	cur.close() # kurtsorea zarratu
	return emaitzak # emaitzak bueltatu

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) # 5000 portuan entzuten jarri

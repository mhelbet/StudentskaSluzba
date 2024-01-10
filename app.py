import configparser
from flask import Flask, request, render_template, redirect
import mysql.connector

config = configparser.ConfigParser()
config.read("config.ini")
dbconfig = config["database"]

app = Flask(__name__)

cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    host = dbconfig["host"],
    user = dbconfig["user"],
    password = dbconfig["password"],
    database = dbconfig["database"],
    port = int(dbconfig["port"]),
)

@app.get("/test")
def get_test():
    """get test metoda"""
    return "Radi!!!"



@app.get("/zadatak1")
def get_zadatak1():
    """get zadatak1 metoda"""
    args = request.args
    godina1 = args["godina1"]
    godina2 = args["godina2"]
    with cnxpool.get_connection() as db:
        z_cur = db.cursor()

        z_cur.execute(
        "SELECT p.naziv AS predmet, AVG(CASE WHEN YEAR(uo.datum) = %(godina1)s THEN uo.ocjena END) AS prosjek_ocjena, AVG(CASE WHEN YEAR(uo.datum) = %(godina2)s THEN uo.ocjena END) AS prosjek_ocjena_2 " + 
        "FROM predmeti p " + 
        "LEFT JOIN upis_ocjene uo ON p.predmet_id = uo.predmet_id " +
        "GROUP BY p.predmet_id, predmet " +
        "ORDER BY predmet ", (godina1,godina2,))

        lista = z_cur.fetchall()

        r = []
        for z in lista:
            r.append(z)

        z_cur.close()

    return { "velicina": z_cur.rowcount, "lista": r }

@app.route("/zadatak2.html")
def get_zadatak2_html():
    """ zadatak2 """

    studijski_program = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as z_cur:
            z_cur.execute("SELECT sp.ProgramID, sp.NazivPrograma,sp.Trajanje,sp.VrstaPrograma,p.predmet_id AS PredmetID,p.opis,p.naziv,p.silabus,p.ects_bodovi " +
                          "FROM studijski_program sp JOIN predmeti p ON sp.ProgramID = p.predmet_id")

            studijski_program = z_cur.fetchall()

    return render_template("zadatak2.html", studijski_program=studijski_program)

@app.route("/zadatak3.html")
def get_zadatak3_html():
    """ zadatak3 """

    return render_template("zadatak3.html")


@app.route("/zadatak4.html")
def get_zadatak4_html():
    """ zadatak4 """

    profesori = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as z_cur:
            z_cur.execute(
                "select p.profesor_id, p.ime, p.prezime from profesori as p ")
            profesori = z_cur.fetchall()

    return render_template("zadatak4.html", profesori=profesori)

@app.post("/zadatak4-unos")
def post_zadatak4():
    """zadatak4 unos"""
    req_data = request.form
    with cnxpool.get_connection() as db:
        with db.cursor() as stmt:
                stmt.execute("insert into profesori " + 
                            "(ime, prezime) " + 
                            "values (%(ime)s, %(prezime)s)",
                            req_data)
                db.commit()

    return redirect('/zadatak4.html')
            
            
@app.get("/zadatak4-brisanje")
def get_zadatak4():
    """zadatak4 brisanje"""
    args = request.args
    profesor_id = args["profesor_id"]
    with cnxpool.get_connection() as db:
        with db.cursor() as stmt:
            stmt.execute("delete from profesori where profesor_id = %s", (profesor_id,))
            db.commit()
            
    return redirect('/zadatak4.html')
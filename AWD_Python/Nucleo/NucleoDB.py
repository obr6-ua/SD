import sqlite3

class NucleoDB:

    def __init__(self):
        self.con = sqlite3.connect("nucleo.db")
        self.cur = self.con.cursor()

    ## Crear tablas
    def crear(self, tabla):
        if(tabla == "mapa"):
            self.cur.execute("CREATE TABLE mapa(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, mapa CHAR(6000))")

        elif(tabla == "ciudades"):
            print("Creando tabla ciudades...")
            self.cur.execute("CREATE TABLE ciudades(nombre VARCHAR(20), temperatura INT)")

        elif(tabla == "jugadores"):
            print("Creando tabla jugadores...")
            self.cur.execute("CREATE TABLE jugadores(alias VARCHAR(20) PRIMARY KEY, posicion CHAR(10), nivel INT, EF INT, EC INT, vivo BOOL, simbolo CHAR(1))")

        elif(tabla == "credenciales"):
            print("Creando tabla credenciales...")
            self.cur.execute("CREATE TABLE credenciales(alias VARCHAR(20) PRIMARY KEY, contraseña VARCHAR(20))")

        self.con.commit()

    ## Leer tablas
    def leer(self, tabla):
        return self.cur.execute(f"SELECT * FROM {tabla}").fetchall()

    def buscarAliasCredenciales(self,alias):
        return self.cur.execute(f"SELECT * FROM credenciales WHERE alias= '{alias}'").fetchall()

    def loginCredenciales(self,alias,contraseña):
        return self.cur.execute(f"SELECT * FROM credenciales WHERE alias = '{alias}' AND contraseña == '{contraseña}'").fetchall()


    def buscarJugador(self,alias):
        return self.cur.execute(f"SELECT * FROM jugadores WHERE alias = '{alias}'").fetchall()

    def buscarPosicion(self,pos):
        return self.cur.execute(f"SELECT * FROM jugadores WHERE posicion = '{pos}'").fetchall()
    
    ## Insertar datos en tablas
    def insertarMapa(self, mapa):
        print("Insertando mapa...")
        self.cur.execute("INSERT into mapa VALUES (?,?)", (None,mapa))
        self.con.commit()

    def insertarCiudades(self, arrayCiudades):
        print("Insertando ciudades...")
        for ciudad in arrayCiudades:
            self.cur.execute("INSERT into ciudades VALUES (?,?)",(ciudad['ciudad'], ciudad['temperatura']))
        self.con.commit()

    def insertarMetadata(self, puerto, maxPlayers, weatherPort):
        print("Insertando metadata...")
        self.cur.execute("INSERT into metadata VALUES (?,?,?)", (puerto, maxPlayers, weatherPort))
        self.con.commit()

    def insertarCredenciales(self, alias, contraseña):
        print("Insertando credenciales...")
        self.cur.execute("INSERT into credenciales VALUES (?,?)", (alias, contraseña))
        self.con.commit()

    def insertarJugador(self, alias, posicion, nivel, EF, EC, vivo, simbolo):
        print(f"Insertando jugador {alias}")
        self.cur.execute("INSERT into jugadores VALUES (?,?,?,?,?,?,?)", (alias, posicion, nivel, EF, EC, vivo, simbolo))
        self.con.commit()

    def modificarJugador(self, alias, posicion, nivel, estado):
        print(f"Modificando jugador {alias}")
        self.cur.execute(f"UPDATE jugadores SET posicion = '{posicion}', nivel = {nivel}, vivo = {estado} WHERE alias = '{alias}'")
        self.con.commit()

    def modificarCredenciales(self, aliasViejo, aliasNuevo, contraseñaNueva):
        print(f"Modificando credenciales de {aliasViejo}")
        self.cur.execute(f"UPDATE credenciales SET alias = '{aliasNuevo}', contraseña = '{contraseñaNueva}' WHERE alias = '{aliasViejo}'")
        self.con.commit()

    ## Borrar tablas
    def borrarAll(self):
        print("Borrando tablas ...")
        self.borrar("mapa")
        self.borrar("metadata")
        self.borrar("ciudades")
        self.borrar("jugadores")
        
    def crearAll(self):
        print("Creando tablas ...")
        self.crear("mapa")
        self.crear("metadata")
        self.crear("ciudades")
        self.crear("jugadores")
        
    def borrar(self, tabla):
        print(f"Borrando tabla {tabla}...")
        try:
            self.cur.execute(f"DROP TABLE {tabla}")
        except:
            print(f"Tabla {tabla} no creada, no es necesario borrar")

    def borrarJugador(self, alias):
        print(f"Borrando {alias} de tabla jugadores")
        try:
            self.cur.execute(f"DELETE from jugadores WHERE alias = '{alias}'")
            self.con.commit()
        except:
            print(f"No se ha podido borrar al jugador {alias}")
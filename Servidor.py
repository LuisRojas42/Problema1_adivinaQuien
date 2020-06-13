# !/usr/bin/env python3

import socket
import sys
import threading
import time
import pickle

# VARIABLES DE CONEXION
HOST = "192.168.100.188"
PORT = 54321
bufferSize = 1024

# VARIABLES DE JUEGO
global tablero
numJugadores = ""

class Turnos(object):
    def __init__(self, start=0):
        self.iniciaJuego = threading.Condition()
        self.numJugadores = 0
        self.conectados = 0
        self.pocision = 1
        self.tablero = []
        self.personajes = "/home/snv/Desktop/Aplicaciones para comunicaciones en Red/Problema_Uno_Servidor/personajes"

    def iniJuego(self, conn, hilo):
        aux = ""
        while True:
            with self.iniciaJuego:
                if self.numJugadores > self.conectados:
                    msj = "\n\nEsperando jugadores ("+str(self.conectados)+"/"+str(self.numJugadores)+")\n"
                    if aux != msj and hilo == 1:
                        print(msj)
                    aux = msj
                    response = bytes(msj, 'ascii')
                    conn.sendall(response)
                    time.sleep(2)
                    self.iniciaJuego.wait(0)
                else:
                    msj = "\nEsperando jugadores (" + str(self.conectados) + "/" + str(self.numJugadores) + ")\n"
                    if hilo == 1:
                        print(msj)
                    response = bytes(msj, 'ascii')
                    conn.sendall(response)
                    time.sleep(1)
                    msj = "Inicia"
                    if hilo == 1:
                        print(msj)
                    response = bytes(msj, 'ascii')
                    conn.sendall(response)
                    self.iniciaJuego.notify()
                    break;

    def setPosicion(self):
        if (self.pocision) < self.numJugadores:
            self.pocision += 1
        else:
            self.pocision = 1

    def getPosicion(self):
        return (self.pocision)

    def setConectados(self):
        self.conectados += 1

    def getConectados(self):
        return (self.conectados)

    def setNumJugadores(self):
        self.numJugadores += 1

    def getNumJugadores(self):
        return (self.numJugadores)

    def getTablero(self):
        return self.tablero

    def espera(self, turnoHilo, conn):
        while True:
            if self.pocision != turnoHilo:
                response = bytes(str(self.pocision), 'ascii')
                conn.sendall(response)
                time.sleep(1)
            else:
                response = bytes(str(self.pocision), 'ascii')
                conn.sendall(response)
                break

    def armaTablero(self):
        arch = open(self.personajes, 'r')
        for line in arch:
            valores = line.split(",")
            self.tablero.append(valores)
        arch.close()
        for i in range(10):
            print(self.tablero[i])


def servirPorSiempre(socketTcp, listaconexiones, turnos, bloqueo):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept() # Acepta conexion
            print("Conectado a", client_addr)
            gestion_conexiones(listaConexiones, client_conn)
            thread_read = threading.Thread(target=recibir_datos, args=[client_conn, listaConexiones, turnos, bloqueo])
            thread_read.start() # Inicia hilo nuevo para cada conexion
    except Exception as e:
        print(e)


def gestion_conexiones(listaconexiones, client_conn):
    listaconexiones.append(client_conn) # Forma nueva conexion en arreglo de conexiones
    for conn in listaconexiones:
        if conn.fileno() == -1: # Remueve las conexiones finalizadas
            listaconexiones.remove(conn)
    #print("conexiones: ", len(listaconexiones))


def recNumJugadores(conn):
    try:
        global numJugadores
        while True:
            # RECIBE
            data = conn.recv(1024)
            if not data:
                break
            print("numero de jugadores : ", data.decode('UTF-8'), "")
            numJugadores = repr(data)

            #ENVIA
            response = bytes("Numero de jugadores establecido", 'ascii')
            conn.sendall(response)
            return numJugadores

    except Exception as e:
        print("error en recNumJugadores()")


def armaTablero():
    tablero = "\nTABLERO\n"
    return tablero


def enviaTurno(conn, turnoHilo):
    time.sleep(1)
    response = bytes(str(turnoHilo), 'ascii')
    conn.sendall(response)


def tiroCliente(tiro):
    lugar = "sth"
    return lugar


def actTablero(tablero, tiro):
    lugarCliente = tiroCliente(tiro)
    print("Lugar cliente: ", lugarCliente)
    for i in range(10):
        print(tablero[i])
    return tablero


def valVictoria(tab):
    vic = "not yet"
    return vic


# Hilo para cada conexion
def recibir_datos(conn, listaconexiones, turnos, bloqueo):
    try:
        # VARIABLES DEL HILO
        global tablero
        turnoHilo = len(listaconexiones)
        cur_thread = threading.current_thread()
        turnos.setConectados()
        print("Jugadores conectados: ", turnos.getConectados())

        if len(listaConexiones) == 1: # Si es el primero establece dificultad y numero de jugadores
            response = bytes("1", 'ascii') # Envia "1" para notificar al cliente que es el primero
            conn.sendall(response)
            turnos.armaTablero()
            tablero = turnos.getTablero()
            numJugadores = recNumJugadores(conn)
            for x in range(int(numJugadores[2])):
                turnos.setNumJugadores()
            #print("getNumJugadores: ", turnos.getNumJugadores())

        else: # Si no, lo incorpora a la partida actual
            # ENVIA
            time.sleep(1)
            response = bytes(str(tablero), 'ascii')
            conn.sendall(response)

        turnos.iniJuego(conn, turnoHilo)  # Espera a que todos los jugadores se unan

        enviaTurno(conn, turnoHilo)

        while True:
            if turnoHilo == 1:
                print("Turno: ", turnos.getPosicion())

            turnos.espera(turnoHilo, conn) # Verifica turno y espera si no lo es

            # RECIBE
            tiro = conn.recv(bufferSize).decode("utf-8")
            if not tiro:
                print("Fin\n\n")
                break
            print("tiro de {}".format(cur_thread.name), ": ", tiro, "")

            tablero = actTablero(tablero, tiro)
            victoria = valVictoria(tablero)

            # ENVIA
            if victoria == True:
                tablero = "0"+tablero
                response = bytes(tablero, 'ascii')
            else:
                response = bytes(str(tablero), 'ascii')
            conn.sendall(response)

            # turnos.turno()
            turnos.setPosicion()


    except Exception as e:
        print(e)
    finally:
        conn.close()


listaConexiones = [] # Arreglo conexiones
host, port, numConn = sys.argv[1:4]

if len(sys.argv) != 4: # Parametros de inicio
    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    sys.exit(1)

serveraddr = (host, int(port)) # Tupla de datos de conexion
turnos = Turnos()
bloqueo = threading.Condition()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes\n\n")

    servirPorSiempre(TCPServerSocket, listaConexiones, turnos, bloqueo)
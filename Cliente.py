# !/usr/bin/env python3

import socket
from pip._vendor.distlib.compat import raw_input
import time
import ast
import speech_recognition as sr

r = sr.Recognizer()

# VARIABLES DE CONEXION
HOST = "192.168.100.188"
PORT = 54321
bufferSize = 1024

# VARIABLES DE JUEGO
NumMaxJugadores = 4

#done
def Menu():
    while True:
        print("\n******Adivina Quien*******")
        print("\n1. Conectar")
        print("2. Salir")
        opc = raw_input('')

        if opc == "1" or opc == "2":
            if opc == "2":
                print("\nHasta luego")
                exit()
            else:
                return
        else:
            print("Ingrese una opcion disponible")

#done
def Conexion():
    print("\n HOST:")
    HOST = raw_input('')
    print("\n Puerto:")
    PORT = raw_input('')
    return HOST, int(PORT)
    # return "192.168.100.188", 54321


#done
def RecibeNumJugadores():
    while True:
        print("\nNumero de jugadores:")
        numJugadores = int(raw_input(''))

        if numJugadores > 0 and numJugadores < NumMaxJugadores:
            return str(numJugadores)
        else:
            print("\nIngrese un numero valido (1-3)")


#done
def esPrimerJugador(TCPClientSocket):
    data = TCPClientSocket.recv(bufferSize)
    if data.decode('UTF-8') == "1":
        numJugadores = bytes(RecibeNumJugadores(), 'ascii')
        TCPClientSocket.sendall(numJugadores)
        data = TCPClientSocket.recv(bufferSize)
        print(data.decode('UTF-8'))
    else:
        try:
            tab = ast.literal_eval(data.decode('UTF-8'))
            for i in range(10):
                print(tab[i])
        except:
                print("..",tab)


#done
def esperaJugadores(TCPClientSocket):
    aux = ""
    while True:
        espera = TCPClientSocket.recv(bufferSize)
        if aux != espera:
            print(espera.decode('UTF-8'))
        aux = espera
        if espera.decode('UTF-8') == "Inicia":
            break;

#done
def recibeTurno(TCPClientSocket):
    while True:
        turno = TCPClientSocket.recv(bufferSize)
        if turno.decode('UTF-8') != "0":
            print("Turno asignado: ", turno.decode('UTF-8'))
            return turno.decode('UTF-8')


#done
def validaTurno(TCPClientSocket, turno):
    aux = ""
    while True:
        posicion = TCPClientSocket.recv(bufferSize)
        if posicion.decode('UTF-8') != turno:
            msj = "En turno: " + str(posicion.decode('UTF-8'))
            if aux != msj:
                print(msj)
                print("Espere su turno\n")
            aux = msj
        else:
            print("Tu turno")
            break;
        time.sleep(.1)

#not yet
def tiroCliente(TCPClientSocket):
    with sr.Microphone() as sourse:
        print("ejemplo: ¿tu personaje tiene...?")
        audio = r.listen(sourse)

        try:
            text = r.recognize_google(audio, lenguage='es-ES')
            print("dijiste: ", text)
            TCPClientSocket.sendall(bytes(text, 'ASCII'))
        except:
            print("no lo entendi")
            TCPClientSocket.sendall(bytes("0", 'ASCII'))
    # tiro = raw_input('')

# not yet
def respServidor(TCPClientSocket):
    tab = TCPClientSocket.recv(bufferSize)
    if tab.decode('UTF-8')[0] != "0":
        try:
            tab = ast.literal_eval(tab.decode('UTF-8'))
            for i in range(10):
                print(tab[i])
        except:
            print("->", tab)
    else:
        print(tab.decode('UTF-8')[1:])  # codigo "1" para victoria
        return 1


def Inicia(serverAddressPort):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect(serverAddressPort)

        # Verifica si es primer jugador
        esPrimerJugador(TCPClientSocket)

        # Espera a que todos los jugadores se conecten para empezar
        esperaJugadores(TCPClientSocket)

        # Recibe turno
        turno = recibeTurno(TCPClientSocket)

        # Comienza juego
        while True:
            # Valida turno
            validaTurno(TCPClientSocket, turno)
            time.sleep(1)

            tiroCliente(TCPClientSocket)
            victoria = respServidor(TCPClientSocket)
            if victoria:
                print("\nFIN DEL JUEGO")
                break


Menu()
serverAddressPort = Conexion()
Inicia(serverAddressPort)
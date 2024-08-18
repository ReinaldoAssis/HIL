import socket
import json
import numpy as np
import serial

def info(status, msg, pad=60):
    dot_count = pad - len(msg) - len(status)
    if dot_count < 1:
        dot_count = 1
    dots = '.' * dot_count
    print(f"{msg}{dots}{status}")

# INTERFACE GENÉRICA PARA CONEXÕES
class ConnectionInterface:
    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def send(self, message):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError

# IMPLEMENTAÇÃO TCP
class TCPConnection(ConnectionInterface):
    def __init__(self, verbose, host='localhost', port=2000):
        self.host = host
        self.port = port
        self.socket = None
        self.verbose = verbose

    def connect(self):
        failed_bind = True
        ntry = 500

        while (failed_bind):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((self.host, self.port))
                self.socket.listen(1)
                self.conn, self.addr = self.socket.accept()
                info("[OK]", f"LISTENING ON PORT {self.port}")
                failed_bind = False
            except:
                if self.verbose:
                    info("[ERR]", f"FAILED TO BIND TO {self.port}, TRYING ANOTHER ONE...")
                    self.port += 10
                    failed_bind = True
                    ntry -= 1
                    if ntry == 0:
                        raise Exception("Exceded number of attempts, failed to bind TCP port.")

    def disconnect(self):
        if self.conn:
            self.conn.close()
        if self.socket:
            self.socket.close()

    def send(self, message):
        self.conn.send(json.dumps(message).encode())

    def receive(self):
        data = self.conn.recv(1024).decode()
        if data:
            return json.loads(data)
        return None

# CLASSE PARA CONEXÃO SERIAL - NÃO IMPLEMENTADA
# Aqui é importante saber que MacOS/Linux e Windows tratam conexões diferentemente,
# port no estilo '/dev/ttyUSB0' é um padrão Mac/Linux, para windows é diferente
# mas acredito que devam existir pacotes python que lidem e generalizem isso para qualquer sistema
class SerialConnection(ConnectionInterface):
    def __init__(self, verbose, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.verbose = verbose
        self.timeout = timeout
        self.serial = None

    def connect(self):

        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if self.verbose:
                print(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            if self.verbose:
                print(f"Disconnected from {self.port}.")

    def send(self, message):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write(message.encode())
            except serial.SerialTimeoutException as e:
                print(f"Serial Timeout: {e}")

    def receive(self):
        if self.serial and self.serial.is_open:

            try:
                message = self.serial.readline().decode().strip()  
                if self.verbose:
                    print(f"Received: {message}")
                return message
            
            except serial.SerialException as e:
                print(f"Failed to receive: {e}")
        return None

# RESPONSÁVEL POR CRIAR OS DIFERENTES TIPOS DE CONEXÕES
class ConnectionFactory:
    @staticmethod
    def create_connection(conn_type, verbose=True, **kwargs):
        if conn_type == 'tcp':
            return TCPConnection(verbose, **kwargs)
        elif conn_type == 'serial':
            return SerialConnection(verbose, **kwargs)
        else:
            raise ValueError(f"Unsupported connection type: {conn_type}")

# PODEMOS TRATAR TODAS AS CONEXÕES COMO UMA RELAÇÃO CLIENTE-SERVIDOR
# @arg system - sistema a ser simulado
# @arg conn_type - tipo de conexão, apenas TCP implementado até o momento
# @arg kwargs - array de argumentos a serem passados as conexões
#----------
# TODO: No momento o loop do servidor está tratando como se fosse simular um pêndulo invertido
# e só está lidando com uma entrada (force), para simular sistemas genéricos é preciso implementar
# uma classe para lidar com até MIMO (multiple inputs multiple outputs). A ideia é deixar tudo o mais
# mastigado possível, para que na hora da aula eles só precisem definir o sistema em uma matriz (ou algo do tipo)
# e a nossa biblioteca faria o manejo necessário para lidar com isso
class GenericServer:
    def __init__(self, system, conn_type='tcp', verbose=True, **kwargs):
        self.system = system
        self.connection = ConnectionFactory.create_connection(conn_type, verbose=verbose, **kwargs)
        self.state = None

    def start(self):
        self.connection.connect()
        self.state = self.system.initial_state()

        while True:
            try:
                command = self.connection.receive()
                if not command:
                    break

                print(f"Received: {command}")
                u = [command['force']]
                t = np.linspace(0, 0.1, 10)
                state_trajectory = self.system.simulate(self.state, t, u)
                self.state = state_trajectory[-1]

                response = {'state': self.state.tolist()}
                self.connection.send(response)
                print(f"Sent: {response}")

            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                self.connection.send({'error': 'JSONDecodeError'})
            except Exception as e:
                print(f"Error: {e}")
                self.connection.send({'error': 'Exception'})

        self.connection.disconnect()
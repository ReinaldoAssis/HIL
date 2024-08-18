import socket
import json
import numpy as np
from system import InvertedPendulum
import exceptions

# TODO: o servidor ainda não está utilizando a interface genérica do lib.py, ainda não consegui
# achar alguns bugs, esse servidor funciona para a conexão tcp

# Implementei uma função simples info(status, msg) para facilitar a entrega da informação do que está sendo
# realizado, acho que isso é importante pois se algo acontecer de errado durante a aula, o usuário
# consegue saber exatamente onde no processo o erro ocorreu (por isso é importante fazer vários tratamentos
# de erro).

def info(status, msg, pad=60):
    dot_count = pad - len(msg) - len(status)
    if dot_count < 1:
        dot_count = 1
    dots = '.' * dot_count
    print(f"{msg}{dots}{status}")

def start_server():
    host = 'localhost'
    port = 2000

    info("[-]", "STARTING SOCKET")

    failed_bind = True
    ntry = 500
    while(failed_bind):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            failed_bind = False
        except:
            info("[ERR]", f"Could not bind to port {port}, trying another one...")
            port += 10
            failed_bind = True
            ntry -= 1

            if ntry == 0:
                break

    info(f"[OK]", f"BIND {host}:{port}")
    server_socket.listen(1)
    info(f"[OK]", f"LISTENING...")
    info(f"[-]", f"INITIALIZING SYSTEM...")

    try:
        system = InvertedPendulum()
        info(f"[OK]", f"{system.name} INITIALIZED")
    except Exception as e:
        exceptions.SYS_INIT_ERR(e, system)

    state = np.array([0, 0, np.pi, 0])  # Estado inicial [x, x_dot, theta, theta_dot]

    while True:
        conn, addr = server_socket.accept()
        print(f"Conectado a: {addr}")

        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

                print(f"Recebido: {data}")

                command = json.loads(data)
                u = [command['force']]
                t = np.linspace(0, 0.1, 10)
                state_trajectory = system.simulate(state, t, u)
                state = state_trajectory[-1]

                response = {'state': state.tolist()}
                conn.send(json.dumps(response).encode())
                print(f"Enviado: {json.dumps(response)}")

            except json.JSONDecodeError as e:
                print(f"Erro de decodificação JSON: {e}")
                conn.send(json.dumps({'error': 'JSONDecodeError'}).encode())
            except Exception as e:
                print(f"Erro: {e}")
                conn.send(json.dumps({'error': 'Exception'}).encode())

        conn.close()

if __name__ == "__main__":
    start_server()
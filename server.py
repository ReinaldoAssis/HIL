from system import InvertedPendulum
from lib import GenericServer

if __name__ == "__main__":
    server = GenericServer(InvertedPendulum(), conn_type='tcp', host='localhost', port=6000)
    server.start()
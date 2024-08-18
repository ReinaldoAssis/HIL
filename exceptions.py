from server import info
from system import BaseSystem

def SYS_INIT_ERR(e: Exception, sys : BaseSystem):
    info(f"[ERR] {sys.name} COULD NOT BE INITIALIZED!")
    print("\n")
    print(e)
    print("............")
    raise Exception(f"System failed to initialize {sys.name}")
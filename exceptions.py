from server import info
from system import StateSpaceSystem

def SYS_INIT_ERR(e: Exception, sys : StateSpaceSystem):
    info(f"[ERR] {sys.name} COULD NOT BE INITIALIZED!")
    print("\n")
    print(e)
    print("............")
    raise Exception(f"System failed to initialize {sys.name}")
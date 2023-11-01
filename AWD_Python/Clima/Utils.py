def comprobarArgs(args):

    if(len(args) != 1):
        print("Debe haber 1 argumento exacto")
        return False

    for arg in args:
            try:
                int(arg)
            except:
                print("Los argumentos deben ser números enteros")
                return False

    print("Argumentos OK")
    return True
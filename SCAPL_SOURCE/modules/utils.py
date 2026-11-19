import random

def print_(*args):
    print(*(str(a) for a in args))

def randomnumber(min_val,max_val):
    if isinstance(min_val, str) and "," in min_val:
        min_val, max_val = min_val.split(",")
    return random.randint(int(min_val), int(max_val))

def input_(prompt):
    return input(prompt)

def open_(filename,mode="r",data=None):
    if mode == "w" and not data==None:
        with open(filename,mode) as f :
            f.write(data)
        return open(filename,"r")
    else :
        return open(filename,mode)
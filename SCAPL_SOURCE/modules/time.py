import datetime

def hour() :
    return datetime.datetime.now().strftime("%H:%M")
def personalget(time) :
    return datetime.datetime.now().strftime(f"{time}")
import sdata
from machine import freq

def __main__(args):

    if len(args) != 1 or args[0] == "--h":
        print("Set clock speed, cpuclock <option>: -low, -turbo, --h -v -t (toggle)")
        return

    actclk = sdata.sysconfig["turbo"]
    
    if args[0] == "-v":
        print(f"CPU speed: {freq()*0.000001} MHz, Turbo: {actclk}")
        return

    turbo = False

    if args[0] == "-t":
        turbo = not actclk

    if args[0] == "-low" or turbo == False :
        f = sdata.board["mcu"][0]["speed"]["slow"]

    if args[0] == "-turbo" or turbo == True :
        f = sdata.board["mcu"][0]["speed"]["turbo"]
        
    sdata.sysconfig["turbo"] = turbo
    freq(f * 1000000)
    print("CPU speed set to " + str(f) + " Mhz")
        
if __name__ == "__main__":

    args =["-low"]
    __main__(args)
        

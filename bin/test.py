import uos
import utls

def __main__(args):

    #print(f"{args}")
    
    if len(args) == 0:
        print("Check file/directory exists\nUsage: test -f/d <path> [-v], set env var ?=1/0")
    else:

        v=False # verbose
        for a in args:
            if "-v" in args: v=True
         
        ret = False
        if "-f" in args:
            ret = utls.file_exists(args[1])
                
        if "-d" in args:
            ret = utls.isdir(args[1])
                
        if ret:
            utls.setenv("0", "1")
            if "-v" in a: print(f"{args[1]} exist")
        else:
            utls.setenv("0", "0")
            if "-v" in a: print(f"{args[1]} not exist")
    

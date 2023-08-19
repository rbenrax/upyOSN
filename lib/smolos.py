# smolOS by Krzysztof Krystian Jankowski
# Homepage: http://smol.p1x.in/os/

# Mods by rbenrax

import sdata
import utls
import uos
import utime
import sys

class smolOS:
    def __init__(self):

        try:
            del sys.modules["syscfg"]
            del sys.modules["grub"]
            #print(sys.modules)
        except:
            pass
        
        sdata.name    = "smolOS-" + uos.uname()[0]
        sdata.version = "0.5 rbenrax"

        if not utls.file_exists("/tmp"): # Temp directory
            uos.mkdir("/tmp")
            
        if not utls.file_exists("/opt"): # Specific solutions directory
            uos.mkdir("/opt")
            
        sys.path.append("/bin")
        sys.path.append("/extlib")
        sys.path.append("/opt")

        self.clear()
        print("Booting smolOS...")

        # Load board and system configuration
        try:
            # Load data
            sdata.board=utls.load_conf_file("/etc/" + sdata.name + ".board")
            self.cpu_speed_range = sdata.board["mcu"][0]["speed"] # speed of cpu 0

            #print(sdata.board)
            #...
            print("Board config loaded.")
            
            sdata.sysconfig=utls.load_conf_file("/etc/system.conf")
            self.user_commands_aliases = sdata.sysconfig["aliases"]

            #print(sdata.sysconfig)
            #...
            print("System config loaded.")
            
        except OSError as ex:

            # Set default values and continue
            self.cpu_speed_range = {"slow":80,"turbo":160} # Mhz

            self.user_commands_aliases = {"h": "help"}
            
            print("Problem loading configuration" + str(ex))
            
            if sdata.debug:
                sys.print_exception(ex)

        except Exception as ex:
            #print(ex)
            if sdata.debug:
                sys.print_exception(ex)
            pass

        # Internal Commands def
        self.user_commands = {
            "help": self.help,
            "ls": self.ls,
            "cat": self.cat,
            "cp" : self.cp,
            "mv" : self.mv,
            "rm": self.rm,
            "clear": self.clear,
            "info": self.info,
            "run": self.run_py_file,
            "sh" : self.run_sh_script,
            "py": self.run_py_code,
            "pwd": self.pwd,
            "mkdir": self.mkdir,
            "rmdir": self.rmdir,
            "cd": self.chdir,
            "exit" : self.exit
        }

        self.boot()

    def boot(self):

        if sdata.sysconfig["turbo"]:
            self.run_cmd("cpuclock -turbo")
        else:
            self.run_cmd("cpuclock -low")
            
        ##Load modules
        if utls.file_exists("/etc/init.sh"):

            self.print_msg("Normal mode boot")
            
            #/etc/init.sh
            self.run_cmd("sh /etc/init.sh")

            #/etc/rc.local
            print("Launching rc.local:")
            self.run_cmd("sh /etc/rc.local")
        else:
            self.print_msg("Recovery mode boot")
            
        ## End modules
        
        self.print_msg("Type 'help' for a smolOS manual.")

        # Main Loop
        while True:
            try:
                user_input = input("\n" + uos.getcwd() + " $: ")
                self.run_cmd(user_input)
                
            except KeyboardInterrupt:
                 self.print_msg("Shutdown smolOS..., bye.")
                 sys.exit()

            except EOFError:
                 self.print_msg("Send EOF")

            except Exception as ex:
                self.print_err("cmd error, " + str(ex))
                if sdata.debug:
                    sys.print_exception(ex)
                pass
 
 # - - - - - - - -
 
    def run_cmd(self, fcmd):
        fcmd=fcmd.strip()

        if fcmd[:3]=="py ":
            #print(f"{fcmd}")
            self.run_py_code(fcmd[3:])
            return

        parts = fcmd.split()
        
        if len(parts) > 0:
            cmd = parts[0]
            #print(f"{cmd=}")
            args=[]
            
            if len(parts) > 1:
                args = parts[1:]
                #print(f"{args=} ")
            
            if cmd in self.user_commands_aliases:    # aliases support
                cmd=self.user_commands_aliases[cmd]
            
            if cmd in self.user_commands:
                if len(args) > 0:
                    self.user_commands[cmd](*args)    
                else:
                    self.user_commands[cmd]()
            else:
                tmp = cmd.split(".")
                if len(tmp) == 2:
                    cmdl = tmp[0]
                    ext  = tmp[1]
                else:
                    cmdl = cmd
                    ext  = ""

                #print(line)
                
                if utls.file_exists("/bin/" + cmdl + ".py"):
                    
                    try:
                        ins = __import__(cmdl)
                        if '__main__' in dir(ins):
                            if len(args) > 0:
                                ins.__main__(args)
                            else:
                                ins.__main__("")

                    except Exception as e:
                        print(f"Error executing script {cmd}")
                        sys.print_exception(e)
                    
                    finally:
                        del sys.modules[cmdl]

                elif ext=="sh":
                    
                    try:
                        self.run_sh_script("/bin/" + cmdl + ".sh")
                    except Exception as e:
                        print(f"Error executing script {command}")
                        sys.print_exception(e)
                    
                else:
                    self.print_err("unknown function. Try 'help'.")

    def run_sh_script(self, ssf):
        if utls.file_exists(ssf):
            with open(ssf,'r') as f:
                cont = f.read()
                for lin in cont.split("\n"):
                    if lin.strip()=="": continue
                    if len(lin)>1 and lin[0]=="#": continue
                    cmd=lin.split("#")
                    self.run_cmd(cmd[0])
 
    def run_py_file(self, fn=""):
        if fn == "":
            self.print_err("Specify a file name to run.")
            return
        
        if utls.file_exists(fn):
            exec(open(fn).read())
        else:
            self.print_err(f"{fn} does not exists.")

    def run_py_code(self, code):
        exec(code.replace('\\n', '\n'))
            
    def exit(self):
        raise SystemExit

    def clear(self):
         print("\033[2J")
         print("\033[H")
 
 # - - -

    def help(self):
        print(sdata.name + " version " + sdata.version + "\n")

        # Ordering files
        with open("/etc/man.txt","r") as mf:
            print(mf.read())
        
        print("External commands:\n")
        
        tmp=uos.listdir("/bin")
        tmp.sort()
        buf=""
        for ecmd in tmp:
            if ecmd.endswith(".py"):
                buf += ecmd[:-3] + ", "
            else:
                buf += ecmd + ", "
        
        print(buf[:-2])

    def print_err(self, error):
        print(f"\n\033[1;37;41m<!>{error}<!>\033[0m")
        utime.sleep(1)

    def print_msg(self, message):
        print(f"\n\033[1;34;47m->{message}\033[0m")
        utime.sleep(0.5)

# - -  

    def ls(self, path="", mode="-l"):

        if "-" in path:
            mode = path
            path=""

        if "--h" in mode:
            print("List files and directories, ls <path> <options>, --h -lhasnk")
            print("-h: human readable, -a: incl. hidden, -s: subdirectories, -k: no totals, -n: no file details")
            return

        cur_dir=uos.getcwd()
        #print("0", cur_dir)
        
        tsize=0
        if utls.isdir(path):
            uos.chdir(path)
            
            if path=="" or path==".." : path=uos.getcwd()

            #print("1", path)
            
            if len(path)>0:
                if path[0]  !="/": path = "/" + path
                if path[-1] !="/": path+="/"

            #print("2", path)
            
            tmp=uos.listdir()
            tmp.sort()

            for file in tmp:
                tsize += self.info(path + file, mode)
                if "s" in mode and utls.isdir(path + file):
                    print("\n" + path + file + ":")
                    tsize += self.ls(path + file, mode)
                    print("")
            
            uos.chdir(cur_dir)
            
            if not 'k' in mode:
                if 'h' in mode:
                    print(f"\nTotal {path}: {utls.human(tsize)}")
                else:
                    print(f"\nTotal {path}: {tsize} bytes")

        else:
            print("Invalid directory")
        #print("3", uos.getcwd())
        
        return tsize
    
    def info(self, filename="", mode="-l"):
        
        if not utls.file_exists(filename):
            self.print_err("File not found")
            return
        
        # Hiden file
        if mode!="-a":
            if filename[1]==".": return 0
        
        stat = utls.get_stat(filename)
        
        #mode = stat[0]
        size = stat[6]
        mtime = stat[8]
        localtime = utime.localtime(mtime)

        if utls.isdir(filename):
            fattr= "d"
        else:
            fattr= " "

        if utls.protected(filename):
            fattr += "r-"
        else:
            fattr += "rw"

        if ".py" in filename:
            fattr += 'x'
        else:
            fattr += '-'
        
        if "h" in mode:
            ssize = f"{utls.human(size)}"
        else:
            ssize = f"{size:7}"
            
        if not "n" in mode:
            print(f"{fattr} {ssize} {utls.MONTH[localtime[1]]} " + \
                  f"{localtime[2]:0>2} {localtime[4]:0>2} {localtime[5]:0>2} {filename.split("/")[-1]}")
              
        return size

    def cat(self,filename=""):
        if filename == "": return
        with open(filename,'r') as file:
            content = file.read()
            print(content)

    def cp(self, spath="", dpath=""):
        if spath == "" or dpath=="": return
        if not utls.file_exists(spath):
            self.print_err("File source not exists.")
            return
        
        sfile = spath.split("/")[-1]
        try:
            uos.listdir(dpath)
            dpath += "/" + sfile
        except OSError:
            pass  
        
        if utls.protected(dpath):
            self.print_err("Can not overwrite system file!")
        else:                  
            with open(spath, 'rb') as fs:
                with open(dpath, "wb") as fd:
                    while True:
                        buf = fs.read(256)
                        if not buf:
                            break
                        fd.write(buf)
            
            self.print_msg("File copied successfully.")

    def mv(self,spath="", dpath=""):
        if spath == "" or dpath == "": return

        if not utls.file_exists(spath):
            self.print_err("File source not exists.")
            return

        sfile = spath.split("/")[-1]
        try:
            uos.listdir(dpath)
            dpath += "/" + sfile
        except OSError:
            pass

        if utls.protected(spath):
            self.print_err("Can not move system files!")
        else:
            uos.rename(spath, dpath)
            self.print_msg("File moved successfully.")

    def rm(self, filename=""):
        if filename == "": return
        if utls.protected(filename):
            self.print_err("Can not remove system file!")
        else:
            uos.remove(filename)
            self.print_msg(f"File {filename} removed successfully.")

    def pwd(self):
        print(uos.getcwd())
       
    def mkdir(self, path=""):
        uos.mkdir(path)
    
    def rmdir(self, path=""):
        uos.rmdir(path)
        
    def chdir(self, path=""):
        uos.chdir(path)

# Module test
if __name__ == "__main__":
    smol = smolOS()


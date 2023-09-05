# smolOS by Krzysztof Krystian Jankowski
# Homepage: http://smol.p1x.in/os/
# Adptated by rbenrax

import sys
import uos
import utime

import sdata
import utls

# Process class
class proc:
    def __init__(self):
        self.tid  = 0                # Thread id
        self.cmd  = ""               # Command
        self.args = ""               # Arguments
        self.sts  = "S"              # Process status
        self.pid  = len(sdata.procs) # Process id
        
        sdata.procs.append(self)
        
    # Lanunch new process
    def run(self, isthr, cmd, args):
        self.cmd = cmd
        self.args = args

        if isthr:
            from _thread import get_ident
            self.tid = get_ident()
        
        imerr=False    # Import module error?
        
        try:
            ins = __import__(self.cmd)
            if '__main__' in dir(ins):
                
                self.sts = "R"
                
                if len(self.args) > 0:
                    ins.__main__(self.args)
                else:
                    ins.__main__("")

        except KeyboardInterrupt:
            print(f"{self.cmd}: ended")
        except ImportError as ie:
            imerr=True
            print(f"{self.cmd}: not found")
        except Exception as e:
            imerr=True
            print(f"Error executing {self.cmd}")
            sys.print_exception(e)
        finally:
            #self.sts = "S"
            del sdata.procs[self.pid]

            if not imerr:
                del sys.modules[self.cmd]

class smolOS:
    
    def __init__(self):

        # Remove modules previusly loaded by grub
        try:
            del sys.modules["syscfg"]
            del sys.modules["grub"]
        except:
            pass
        
        # sdata store all system data
        sdata.name    = "smolOS-" + uos.uname()[0]
        sdata.version = "0.5 rbenrax"

        # Create directories
        if not utls.file_exists("/opt"): # Specific solutions directory
            uos.mkdir("/opt")

        if not utls.file_exists("/tmp"): # Temp directory
            uos.mkdir("/tmp")

        # Set library path for modules finding, by default is /lib only
        sys.path.append("/bin")
        sys.path.append("/extlib")
        #sys.path.append("/opt") # /opt directory calls need full path

        print("\033[2J\033[HBooting smolOS...")

        # Load system configuration and board definitions
        try:
            sdata.sysconfig=utls.load_conf_file("/etc/system.conf")
            #print(sdata.sysconfig)
            print("System cfg loaded.")
            
            sdata.board=utls.load_conf_file("/etc/" + sdata.name + ".board")
            #print(sdata.board)
            print("Board cfg loaded.")
            
        except OSError as ex:
            print("Problem loading configuration" + str(ex))
            if sdata.debug:
                sys.print_exception(ex)

        except Exception as ex:
            if sdata.debug:
                sys.print_exception(ex)
            pass

        # Internal Commands definition
        self.user_commands = {
            "sh" : self.run_sh_script,
            "r": self.last_cmd,
            "ps": self.ps,
            "kill": self.kill,
            "exit" : self.exit
        }

        if "turbo" in sdata.sysconfig:
            if sdata.sysconfig["turbo"]:
                self.run_cmd("cpufreq -turbo")
            else:
                self.run_cmd("cpufreq -low")

        if utls.file_exists("/etc/init.sh"):
            self.print_msg("Normal mode boot")
            
            #print("Launching init.sh:")
            self.run_cmd("sh /etc/init.sh")

            #/etc/rc.local
            print("Launching rc.local:")
            self.run_cmd("sh /etc/rc.local")
        else:
            self.print_msg("Recovery mode boot")
        
        self.prev_cmd=""
        self.print_msg("Type 'help' for a smolOS manual.")

        # Main command processing loop
        while True:
            try:
                user_input = input(uos.getcwd() + " $: ")
                self.run_cmd(user_input)
                
            except KeyboardInterrupt:
                self.exit()

            except EOFError:
                self.print_msg("Send EOF")

            except Exception as ex:
                print("cmd error, " + str(ex))
                if sdata.debug:
                    sys.print_exception(ex)
                pass
 
 # - - - - - - - -

    def run_py_code(self, code):
        exec(code.replace('\\n', '\n'))

    def run_cmd(self, fcmd):

        fcmd=fcmd.strip()

        if fcmd[:2]=="> ":
            self.run_py_code(fcmd[2:])
            return
        elif fcmd[:2]=="< ":
            self.run_py_code(f"print({fcmd[2:]})")
            return
        elif fcmd[:2]=="./":
            cwd = uos.getcwd()
            if cwd == "/":
                fcmd = "/" + fcmd[2:]
            else:
                fcmd = cwd + "/" + fcmd[2:]

        # Separate full command elements
        parts = fcmd.split()
        
        if len(parts) > 0:

            # Get command 
            cmd = parts[0]
            
            # Translate command aliases
            if sdata.sysconfig:
                if cmd in sdata.sysconfig["aliases"]:    
                    cmd=sdata.sysconfig["aliases"][cmd]
            
            # Last command repeat 
            if cmd!="r":
                self.prev_cmd = fcmd
            
            args=[]
            
            # Get command arguments
            if len(parts) > 1:
                args = parts[1:]
                #print(f"{args=} ")
            
            # Internal commands
            if cmd in self.user_commands:
                if len(args) > 0:
                    self.user_commands[cmd](*args)
                else:
                    self.user_commands[cmd]()

            # External commands or scripts
            else:
                tmp = cmd.split(".")
                if len(tmp) > 1:
                    cmdl = tmp[0]
                    ext  = tmp[-1]
                else:
                    cmdl = cmd
                    ext  = ""

                # External Python commands and programs
                if ext=="py" or ext=="":

                    if len(parts) > 1 and parts[-1]=="&": # If new thread
                        # Since most microcontrollers only have one thread more...
                        # One main thread an alternative one, for now
                        try:
                            from _thread import start_new_thread
                            newProc = proc()
                            start_new_thread(newProc.run, (True, cmdl, args[:-1]))
                        except ImportError:
                            print("System has not thread support")
                        except Exception as ex:
                            print(f"Error launching thread {ex}")
                            if sdata.debug:
                                sys.print_exception(ex)
                            
                    else:
                        newProc = proc()
                        newProc.run(False, cmdl, args)

                # External shell scripts
                elif ext=="sh":
                    try:
                        if not "/" in cmdl:
                            self.run_sh_script("/bin/" + cmdl + ".sh")
                        else:
                            self.run_sh_script(cmdl + ".sh")
                    except Exception as e:
                        print(f"Error executing script {fcmd}")
                        sys.print_exception(e)
                    
                else:
                    print(f"{cmd}: Unknown function or program. Try 'help'.")

    # Run shell script
    def run_sh_script(self, ssf):
        if utls.file_exists(ssf):
            with open(ssf,'r') as f:
                while True:
                    lin = f.readline()
                    if not lin: break

                    if lin.strip()=="": continue
                    if len(lin)>0 and lin[0]=="#": continue
                    cmdl=lin.split("#")[0] # Left comment line part
                    
                    # Translate env variables $*
                    tmp = cmdl.split()
                    
                    if not tmp[0] in ["export", "echo", "unset"]:
                        for e in tmp:
                            if e[0]=="$":
                                v=sdata.getenv(e[1:])
                                cmdl = cmdl.replace(e, v)

                    self.run_cmd(cmdl)
        else:
            print(f"{ssf}: script not found")

# - - -

    # Repeat command
    def last_cmd(self):
        # Only runs in full terminals where is unnecesary
        #from editstr import editstr
        #print('┌───┬───┬───┬───┬───┬───')
        #cmd = editstr(self.prev_cmd)
        #self.run_cmd(cmd)
        #del sys.modules["editstr"]
        self.run_cmd(self.prev_cmd)
    
    # Thread status
    def ps(self):
        print(f"Proc Sts Thread_Id Cmd/Args")
        for i in sdata.procs:
            if i.sts == "S": del sdata.procs[i.pid]
            print(f"{i.pid:4}  {i.sts}  {i.tid} {i.cmd} {i.args}")

    # Kill thread
    def kill(self, pid):
        if sdata.procs:
            sdata.procs[int(pid)].sts = "S"
            
    # System exit
    def exit(self):

        # Stop threads before exit
        for i in sdata.procs:
            self.kill(i.pid)
        utime.sleep(1)

        self.print_msg("Shutdown smolOS..., bye.")
        print("")
        
        raise SystemExit
        #sys.exit()

    def print_msg(self, message):
        print(f"\n\033[1;34;47m->{message}\033[0m")

# - -  
if __name__ == "__main__":
    smol = smolOS()

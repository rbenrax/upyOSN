import json

class BoardDef():
    def __init__(self, board):
        
        self.board={"ver"    : 1.0,
                    "board"  : board,
                    "mcu"    : "esp32-c3",
                    "arch"   : "RISC-V",
                    "spedr"  : {"slow": 80, "turbo": 160},
                    "text"   : "Example file autogenerated, must be fulfilled",
                    "5v0p" : [],
                    "3v3p" : [],
                    "gndp" : [],
                    "ena"  : [],
                    "rstp" : [],
                    "adc"  : {"adc0": 1, "adc1": 2},
                    "dac"  : {"adc0": 1, "adc1": 2},
                    "pwmp" : [],
                    "gpio" : {"gpio0": 2, "gpio1": 3},
                    "i2c"  : [{"scl1": 0, "sda1": 0}, {"scl2": 0, "sda1": 0}],
                    "spi"  : [{"mosi1": 0, "miso1": 0, "cs1": 0, "ck1": 0}],
                    "usart" : [{"tx1": 0, "rx1": 0, "cts1": 0, "rts1": 0}, {"tx2": 0, "rx2": 0}],
                    "i2s"   : [{"1clk": 0, "1io": 0}],
                    "can "  : [{"tx1": 0, "rx1": 0}],
                    "sd"    : [{"clk": 0, "cmd": 0, "data0": 0, "data1": 0, "data2": 0, "data3": 0 }],
                    "touch" : {"t1": 0, "t2": 0},
                    "othp"  : {"vout": 0, "vin": 0, "usrkey": 0, "vref": 0, "flash": 0, "wake": 0, "run": 0, "vbat": 0 },
                    "ncp"  : [],
                    "resvp" : [],
                    "ledp"  : [12, 13],
                    "neoxp" : []
                    }


    def getBoard(self):
        return self.board
    
    def dump(self):
        return json.dumps(self.board)
    
    def loads(self, data):
         self.board = json.loads(data)
         
if __name__ == "__main__":      
    b=BoardDef("ESP32C3 module with ESP32C3")

    print("Original")
    print(b.getBoard())

    s=b.dump()
    print("Codificada")
    print(s)

    b.loads(s)
    print("cargada")
    print(b.getBoard())

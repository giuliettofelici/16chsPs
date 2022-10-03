import time
import spidev
import time, smbus
bus=smbus.SMBus(1)

spi_ch = 0

# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 50000


dac_2668_res=2**16
timeout=0
value=0
msg=0

span=[0x00, 0x04, 0x02] # +5, +/- 2.5, +/-5
lsb_span=[5./dac_2668_res, 5./dac_2668_res, 10./dac_2668_res ]

conv_factor=1/0.4583125

    
    #############################################################################################
    #                                    SPI FUNCTIONS                                       #
    #############################################################################################

class SPI_2025A():

    def __init__(self, ):
        # Enable SPI
        spi_0 = spidev.SpiDev(0, spi_ch)
        spi_0.max_speed_hz = 200000
        self.spi=spi_0
        
    def init(self):
        #spi=self.spi_0
        command=[0x70,0x00,0x00]
        self.spi.xfer3(command)                 
    
    def set_span_all(self,code):
        self.toggle(False)
        low_byte=span[code]
        command=[0xE0,0x00,low_byte]
        self.spi.xfer3(command)
    
    def set_span_n(self,code,addr):
        low_byte=span[code]
        upper_byte=0x60+addr
        command=[upper_byte,0x00,low_byte]
        self.spi.xfer3(command)
   
    def monitor_mux(self,code, addr):
        low_byte=code
        command=[0xB0,0x00,low_byte]
        spi.xfer3(command)
    
    def power_down_all(self):
        command=[0x50,0x00,0x00]
        spi.xfer2(command)
    
    def power_up_all(self):
        command=[0x70,0x00,0x00]
        spi.xfer2(command)
        
    def power_down_n(self, addr):
        dato= 0x04 << 4 | addr
        command = [dato, 0x00, 0x00]
        spi.xfer3(command)
        
    def write_all(self,gspan, data):
        command=[0xC0,0x00,0x00]
        spi.xfer3(command)
        lsb=lsb_span[gspan]
        dato = int(data/lsb)
        right_byte = dato & 0xFF;
        left_byte = ( dato >> 8 ) & 0xFF
        command=[0xA0,left_byte, right_byte]
        self.spi.xfer3(command)
    
    def write_all_toggle(self, gspan, val1, val2): 
        command=[0xC0,0x00, 0x00]
        spi.xfer3(command)
        lsb=lsb_span[gspan]
        dato = int(val1/lsb)
        right_byte = dato & 0xFF
        left_byte = ( dato >> 8 ) & 0xFF
        command=[0xA0,left_byte, right_byte]
        spi.xfer3(command)
        right_byte=0xFF
        left_byte=0xFF
        command=[0xC0,left_byte, right_byte]
        spi.xfer3(command)
        dato = int(val2/lsb)
        right_byte = dato & 0xFF
        left_byte = ( dato >> 8 ) & 0xFF
        command=[0x80,left_byte, right_byte]
        spi.xfer3(command)
    
    def write_single_toggle_lib(self, span_code, val1, val2, addr, toggle_addr): 
        
        command=[0xD0, 0x00, 0x00]
        self.spi.xfer3(command)
        
        # SET SPAN CODE
        low_byte=span[span_code]
        upper_byte=0x60+addr
        command=[upper_byte,0x00,low_byte]
        self.spi.xfer3(command)
        
        # WRITE & UPDATE N
        lsb=lsb_span[span_code]
        dato = int(val1/lsb)
        right_byte = dato & 0xFF;
        left_byte = ( dato >> 8 ) & 0xFF
        op_addr=0x30+addr
        command=[op_addr,left_byte, right_byte]
        self.spi.xfer3(command)
        
        # WRITE CHANNEL A
        lsb=lsb_span[span_code]
        dato = int(val2/lsb)
        right_byte = dato & 0xFF;
        left_byte = ( dato >> 8 ) & 0xFF
        op_addr=0x00+addr
        command=[op_addr,left_byte, right_byte]
        self.spi.xfer3(command)
        
        # SELECT CHANNEL B
        op_code=0xC0
        right_byte = toggle_addr & 0xFF
        left_byte = ( toggle_addr >> 8 ) & 0xFF
        command=[op_code, left_byte, right_byte]
        spi.xfer3(command)
        
        # WRITE CHANNEL B
        lsb=lsb_span[span_code]
        dato = int(val1/lsb)
        right_byte = dato & 0xFF;
        left_byte = ( dato >> 8 ) & 0xFF
        op_addr=0x00+addr
        command=[op_addr,left_byte, right_byte]
        self.spi.xfer3(command)           
   
    def write_n(self,span, val ,addr):
        self.set_span_n(span, addr )
        lsb=lsb_span[span]
        dato = int(val/lsb)
        right_byte = dato & 0xFF;
        left_byte = ( dato >> 8 ) & 0xFF
        op_addr=0x30+addr
        command=[op_addr,left_byte, right_byte]
        self.spi.xfer3(command)
        
    def write_n_t(self,span, val ,addr):
        lsb=lsb_span[span]
        dato = int(val/lsb)
        op_addr= 0xC0
        shift = 1 << addr
        right_byte = shift & 0xFF;
        left_byte = ( shift >> 8 ) & 0xFF
        command=[op_addr,left_byte, right_byte]
        self.spi.xfer3(command)
        right_byte = dato & 0xFF;
        left_byte = ( dato >> 8 ) & 0xFF
        op_addr=0x30+addr
        command=[op_addr,left_byte, right_byte]
        spi.xfer3(command)
        
    def load_setup(self, span, val1, val2, addr):
        lsb=lsb_span[span]
        dato1=int(val1/lsb)
        dato2=int(val2/lsb)
        self.set_span_n(span, addr)
        right_byte = dato & 0xFF;
        left_byte = ( dato >> 8 ) & 0xFF
        op_addr=0x00+addr
        command=[op_addr,left_byte, right_byte]
        spi.xfer3(command)
        bit_shift = 1 << addr
        op_addr= 0xC0
        right_byte = bit_shift & 0xFF;
        left_byte = ( bit_shift >> 8 ) & 0xFF
        command=[op_addr,left_byte, right_byte]
        spi.xfer3(command)
        op_addr=0x00+addr
        command=[op_addr,left_byte, right_byte]
        spi.xfer3(command)
    
    def update_all(self):
        #spi=self.spi_0
        self.toggle(False)
        command=[0x90, 0x00, 0x00]
        self.spi.xfer3(command)
        
    def toggle(self, flag):
        if flag:
            command=[0xD0, 0x00, 0x01]
            self.spi.xfer3(command)
            #print("TOGGLE ON")
        else:
            command=[0xD0, 0x00, 0x00]
            self.spi.xfer3(command)
            #print("TOGGLE OFF")
            
    def toggle_sel(self, flag, toggle_addr):
        print("flag= ", flag, "toggle_addr= ", toggle_addr)
        right_byte = toggle_addr & 0xFF;
        left_byte = ( toggle_addr >> 8 ) & 0xFF
        command=[0xC0, left_byte, right_byte]
        
        if flag: 
            command=[0xC0, left_byte, right_byte]
            self.spi.xfer3(command)
            command=[0xD0, 0x00, 0x01]
            self.spi.xfer3(command)
            print("Address= ", left_byte, right_byte)
            print("TOGGLE SELECTED ON")
        else:
            command=[0xD0, 0x00, 0x00]
            self.spi.xfer3(command)
            print("TOGGLE SELECTED OFF")   
        
my2025=SPI_2025A()

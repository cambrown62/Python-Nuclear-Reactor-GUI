# The purpose of this file is to display plant data in a graphical user interface format

import Tkinter as tk
import ttk
import numpy as np
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot
import matplotlib.ticker as plticker
import socket
import RPi_Functions_Socket as RPi_Socket
import RPi_Functions_Parsing as RPi_Parsing
import RPi_Functions_Calcs as RPi_Calcs
import time
from collections import defaultdict
import decimal

matplotlib.use('TkAgg')
style.use('ggplot')

class LiveGraph:
    def __init__(self, tab, reactor, sensor, rownum, colnum):
        self.f = Figure(figsize=(6,4))
        self.a = self.f.add_subplot(111)
        self.f.tight_layout()
        self.f.subplots_adjust(top=.85, left=.13)
        self.grph = FigureCanvasTkAgg(self.f, master=tab)
        #self.toolbar = NavigationToolbar2TkAgg(self.grph, gui)
        self.grph.show()
        self.grph._tkcanvas.grid(row=rownum, column=colnum, columnspan=2)
        self.grph.get_tk_widget().grid(row=rownum, column=colnum, columnspan=2)
        self.loc = plticker.MultipleLocator(base=100.0)
        self.ani = animation.FuncAnimation(self.f, self.animate, fargs=(sensor, reactor), interval=5000)

    def animate(self, framenumber, sensor, reactor):
        self.a.clear()
        #print self.xList
        self.a.plot(xList, yDict[reactor][sensor], color='r')
        self.title = str(sensor) + '\nCurrent Value: ' + str(D(yDict[reactor][sensor][-1]).quantize(twoplaces))
        self.a.set_title(self.title)
        #self.a.set_xlabel('Each tick approx. 10 seconds')
        #self.a.axis = xList[0], max(xList)+5, min(yDict[reactor][sensor])-5, max(yDict[reactor][sensor])+100
        self.a.xaxis.set_major_locator(self.loc)
        self.a.set_xlim([xList[0], max(xList)+100])
        self.a.set_ylim([min(yDict[reactor][sensor])-5, max(yDict[reactor][sensor])+5])
        self.a.axes.get_xaxis().set_ticklabels([])
        self.y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        self.a.yaxis.set_major_formatter(self.y_formatter)


def compiler():
    global i, xList, yDict
    #print yDict
    sensor_data_string, tcp_status = RPi_Socket.tcp_client_exchange(None, rpi_socket)
    #print sensor_data_string
    #print tcp_status
    if tcp_status:
        sensor_data = RPi_Parsing.string2dictionary(sensor_data_string)
        #print sensor_data
        for x in sensor_data:
            for item in sensor_data[x]:
                if len(yDict[x][item]) > 1199:
                    yDict[x][item] = yDict[x][item][1:len(yDict[x][item])]
                    
                else:
                    pass
                yDict[x][item].append(sensor_data[x][item])
                
        #print len(yDict[0]['RTO'])
        if len(xList) > 1199:
            xList = xList[1:len(xList)]
        else:
            pass
        xList.append(i)
        i += 1
        #print yDict
        BoP_data = RPi_Calcs.balance_of_plant(sensor_data)
        for x in BoP_data:
            for item in BoP_data[x]:
                if len(BoPdict[x][item]) > 100:
                    BoPdict[x][item] = BoPdict[x][item][1:-1]
                else:
                    pass
                
                BoPdict[x][item].append(BoP_data[x][item])
        #print BoPdict
        
        gui.after(100, compiler)




# Initializing variables
yDict = {}                      
i = 0
xList = []
D = decimal.Decimal
twoplaces = D('0.01')


            
# Create a TCP socket
rpi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rpi_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
rpi_server = ('', 10000)
rpi_socket.bind(rpi_server)
rpi_socket.listen(5)



sensor_data_string, tcp_status = RPi_Socket.tcp_client_exchange(None, rpi_socket)
#print sensor_data_string
if tcp_status:
    #print 'hi'
    sensor_data_dummy = RPi_Parsing.string2dictionary(sensor_data_string)
    #print sensor_data_dummy
    yDict = sensor_data_dummy
    #print yDict
    for y in yDict:
        for key in yDict[y]:
            yDict[y][key] = []
                
    sensor_data_dummy = RPi_Parsing.string2dictionary(sensor_data_string)
    BoP_data_dummy = RPi_Calcs.balance_of_plant(sensor_data_dummy)
    BoPdict = BoP_data_dummy
    for y in BoPdict:
        for key in BoPdict[y]:
            BoPdict[y][key] = []
                    
    #print BoPdict

            
#print sensor_data_string
# Defining the GUI
gui = tk.Tk()
gui.title('Operator Interface')
gui.geometry('1600x800')
compiler()

# Initializing Tkinter variables inside the mainloop

class SummaryVars:

    def __init__(self, reactor, col):
        
        self.PTIvar = tk.DoubleVar()
        self.PTOvar = tk.DoubleVar()
        self.STIvar = tk.DoubleVar()
        self.STOvar = tk.DoubleVar()
        self.RTOvar = tk.DoubleVar()
        self.PMFvar = tk.DoubleVar()
        self.SMFvar = tk.DoubleVar()
        #self.RTOSvar = tk.DoubleVar()

        self.update_vars(reactor)
        self.updatelabels(col)

    def update_vars(self, reactor):

        self.PTIvar.set(D(yDict[reactor]['PTI'][-1]).quantize(twoplaces))
        self.PTOvar.set(D(yDict[reactor]['PTO1'][-1]).quantize(twoplaces))
        self.STOvar.set(D(yDict[reactor]['STO1'][-1]).quantize(twoplaces))
        self.STIvar.set(D(yDict[reactor]['STI'][-1]).quantize(twoplaces)) 
        self.RTOvar.set(D(yDict[reactor]['RTO'][-1]).quantize(twoplaces)) 
        self.PMFvar.set(D(yDict[reactor]['PMF1'][-1]).quantize(twoplaces)) 
        self.SMFvar.set(D(yDict[reactor]['SMF1'][-1]).quantize(twoplaces))
        #self.RTOSvar.set(D(yDict[reactor]['RTOS'][-1]).quantize(twoplaces))

        gui.after(900, self.update_vars, reactor) 

    def updatelabels(self, col):

        self.RTOlabel = ttk.Label(master=sumtab, textvariable=self.RTOvar)
        self.RTOlabel.grid(row=rh, column=col)
    
        self.PTIlabel = ttk.Label(master=sumtab, textvariable=self.PTIvar, background='WHITE')
        self.PTIlabel.grid(row=ri, column=col, pady=(10,0))

        self.PTOlabel = ttk.Label(master=sumtab, textvariable=self.PTOvar)
        self.PTOlabel.grid(row=rj, column=col)

        self.PMFlabel = ttk.Label(master=sumtab, textvariable=self.PMFvar, background='WHITE')
        self.PMFlabel.grid(row=rk, column=col)

        self.STIlabel = ttk.Label(master=sumtab, textvariable=self.STIvar, background='WHITE')
        self.STIlabel.grid(row=rm, column=col)

        self.STOlabel = ttk.Label(master=sumtab, textvariable=self.STOvar)
        self.STOlabel.grid(row=rl, column=col, pady=(10,0))

        self.SMFlabel = ttk.Label(master=sumtab, textvariable=self.SMFvar)
        self.SMFlabel.grid(row=rn, column=col)

        #self.RTOSlabel = ttk.Label(master=sumtab, textvariable=self.RTOSvar)
        #self.RTOSlabel.grid(row=rh, column=col+1, sticky='W')
            

R1PL1var = tk.DoubleVar()
R1PL2var = tk.DoubleVar()
R1PL3var = tk.DoubleVar()

R2PL1var = tk.DoubleVar()
R2PL2var = tk.DoubleVar()
R2PL3var = tk.DoubleVar()

R3PL1var = tk.DoubleVar()
R3PL2var = tk.DoubleVar()
R3PL3var = tk.DoubleVar()

R4PL1var = tk.DoubleVar()
R4PL2var = tk.DoubleVar()
R4PL3var = tk.DoubleVar()

R1Pvar = tk.DoubleVar()
R2Pvar = tk.DoubleVar()
R3Pvar = tk.DoubleVar()
R4Pvar = tk.DoubleVar()
RXtotvar = tk.DoubleVar()

PLPHX1var = tk.DoubleVar()
PLPHX2var = tk.DoubleVar()
PLPHX3var = tk.DoubleVar()

PLPHX4var = tk.DoubleVar()
PLPHX5var = tk.DoubleVar()
PLPHX6var = tk.DoubleVar()

PLPHX7var = tk.DoubleVar()
PLPHX8var = tk.DoubleVar()
PLPHX9var = tk.DoubleVar()

PLPHX10var = tk.DoubleVar()
PLPHX11var = tk.DoubleVar()
PLPHX12var = tk.DoubleVar()

PHX1_3Pvar = tk.DoubleVar()
PHX4_6Pvar = tk.DoubleVar()
PHX7_9Pvar = tk.DoubleVar()
PHX10_12Pvar = tk.DoubleVar()

BCPvar1 = tk.DoubleVar()
BCPvar2 = tk.DoubleVar()
BCPvar3 = tk.DoubleVar()
HSvar = tk.DoubleVar()

BCPtotvar= tk.DoubleVar()

R1NPvar = tk.DoubleVar()
R2NPvar = tk.DoubleVar()
R3NPvar = tk.DoubleVar()
R4NPvar = tk.DoubleVar()

SVNPvar = tk.DoubleVar()

SVTvar = tk.DoubleVar()
HSTIvar = tk.DoubleVar()
HSTOvar = tk.DoubleVar()
HSMFvar = tk.DoubleVar()
HSPvar = tk.DoubleVar()
EHLvar = tk.DoubleVar()

BCTIvar = tk.DoubleVar()
BCTOvar = tk.DoubleVar()
BCMFvar = tk.DoubleVar()

PHXPS1 = tk.DoubleVar()
PHXPS2 = tk.DoubleVar()
PHXPS3 = tk.DoubleVar()
PHXPS4 = tk.DoubleVar()
PHXPS5 = tk.DoubleVar()
PHXPS6 = tk.DoubleVar()
PHXPS7 = tk.DoubleVar()
PHXPS8 = tk.DoubleVar()
PHXPS9 = tk.DoubleVar()
PHXPS10 = tk.DoubleVar()
PHXPS11 = tk.DoubleVar()
PHXPS12 = tk.DoubleVar()

PHXPS1_3 = tk.DoubleVar()
PHXPS4_6 = tk.DoubleVar()
PHXPS7_9 = tk.DoubleVar()
PHXPS10_12 = tk.DoubleVar()

RTOS1 = tk.DoubleVar()
RTOS2 = tk.DoubleVar()
RTOS3 = tk.DoubleVar()
RTOS4 = tk.DoubleVar()


# Creating the tabbed notebook
notebook = ttk.Notebook(gui)
notebook.pack(fill='both', expand=1)

sumtab = ttk.Frame(notebook)
sumtab.pack()
BoPtab = ttk.Frame(notebook)
BoPtab.pack()
rx1tab = ttk.Frame(notebook)
rx1tab.pack()
rx2tab = ttk.Frame(notebook)
rx2tab.pack()
rx3tab = ttk.Frame(notebook)
rx3tab.pack()
rx4tab = ttk.Frame(notebook)
rx4tab.pack()
svtab = ttk.Frame(notebook)
svtab.pack()
bctab = ttk.Frame(notebook)
bctab.pack()

notebook.add(sumtab, text='     Summary     ')
notebook.add(BoPtab, text='Balance of Plant')
notebook.add(rx1tab, text='     Reactor 1     ')
notebook.add(rx2tab, text='     Reactor 2     ')
notebook.add(rx3tab, text='     Reactor 3     ')
notebook.add(rx4tab, text='     Reactor 4     ')
notebook.add(svtab, text='     Salt Vault     ')
notebook.add(bctab, text='      Brayton      ')

pittlogo=tk.PhotoImage(file='pitt-logo')

# Summary page row indices
r=1
ra=2
rb=3
rc=4
rd=5
re=6
rf=7
rg=8
rh=9
ri=10
rj=11
rk=12
rl=13
rm=14
rn=15
ro=16
rp=17
rq=18
rs=19
rt=20
ru=21
rv=22

# Summary page column indices
c=1
ca=2
cf=3
cb=4
cg=5
cc=6
ch=7
cd=8
ci=9
ce=10

logo1 = ttk.Label(master=sumtab, image=pittlogo).grid(row=r, column=c)

R1sum = ttk.Label(master=sumtab, text='Reactor 1', background='WHITE').grid(row=rg, column=ca, padx=14, pady=10)
R2sum = ttk.Label(master=sumtab, text='Reactor 2', background='WHITE').grid(row=rg, column=cf, pady=10)
R3sum = ttk.Label(master=sumtab, text='Reactor 3', background='WHITE').grid(row=rg, column=cb, pady=10)
R4sum = ttk.Label(master=sumtab, text='Reactor 4', background='WHITE').grid(row=rg, column=cg, pady=10)
'''
RTOS1header = ttk.Label(master=sumtab, text='Setpoint', background='WHITE').grid(row=rg, column=cf, pady=10, sticky='W')
RTOS2header = ttk.Label(master=sumtab, text='Setpoint', background='WHITE').grid(row=rg, column=cg, pady=10, sticky='W')
RTOS3header = ttk.Label(master=sumtab, text='Setpoint', background='WHITE').grid(row=rg, column=ch, pady=10, sticky='W')
RTOS4header = ttk.Label(master=sumtab, text='Setpoint', background='WHITE').grid(row=rg, column=ci, pady=10, sticky='W')
'''

PTIsum = ttk.Label(master=sumtab, text='PL Hot Leg Temp (C)', background='WHITE').grid(row=ri, column=c, sticky='E', pady=(10,0))
PTOsum = ttk.Label(master=sumtab, text='PL Cold Leg Temp (C)').grid(row=rj, column=c, sticky='E')
STIsum = ttk.Label(master=sumtab, text='SL Hot Leg Temp (C)').grid(row=rl, column=c, sticky='E', pady=(10,0))
STOsum = ttk.Label(master=sumtab, text='SL Cold Leg Temp (C)', background='WHITE').grid(row=rm, column=c, sticky='E')
RTOsum = ttk.Label(master=sumtab, text='Reactor Temperature Out (C)').grid(row=rh, column=c, sticky='E')
PMFsum = ttk.Label(master=sumtab, text='Primary Loop Mass Flow (kg/s)', background='WHITE').grid(row=rk, column=c, sticky='E')
SMFsum = ttk.Label(master=sumtab, text='Secondary Loop Mass Flow (kg/s)').grid(row=rn, column=c, sticky='E')

SVsum = ttk.Label(master=sumtab, text='Salt Vault', background='WHITE').grid(row=ro, column=ca)
BCsum = ttk.Label(master=sumtab, text='Brayton Cycle', background='WHITE').grid(row=ro, column=cg, pady=14)

SVTsum = ttk.Label(master=sumtab, text='Salt Vault Temperature (C)').grid(row=rp, column=c, sticky='E')
HSTIsum = ttk.Label(master=sumtab, text='Heat Sink Hot Leg (C)', background='WHITE').grid(row=rq, column=c, sticky='E', pady=(10,0))
HSTOsum = ttk.Label(master=sumtab, text='Heat Sink Cold Leg (C)').grid(row=rs, column=c, sticky='E')
HSMFsum = ttk.Label(master=sumtab, text='Heat Sink Mass Flow (kg/s)', background='WHITE').grid(row=rt, column=c, sticky='E')
EHLsum = ttk.Label(master=sumtab, text='Environmental Heat Loss (MW)').grid(row=ru, column=1, sticky='E')

BCTIsum = ttk.Label(master=sumtab, text='Brayton Cycle Temperature In (C)').grid(row=rp, column=cf, columnspan=2, sticky='E')
BCTOsum = ttk.Label(master=sumtab, text='Brayton Cycle Temperature Out (C)', background='WHITE').grid(row=rq, column=cf, columnspan=2, sticky='E')
BCMFsum = ttk.Label(master=sumtab, text='Brayton Cycle Mass Flow (C)').grid(row=rs, column=cf, columnspan=2, sticky='E')

SVTsum2 = ttk.Label(master=sumtab, textvariable=SVTvar).grid(row=rp, column=ca)
HSTIsum2 = ttk.Label(master=sumtab, textvariable=HSTIvar).grid(row=rs, column=ca)
HSTOsum2 = ttk.Label(master=sumtab, textvariable=HSTOvar, background='WHITE').grid(row=rq, column=ca, pady=(10,0))
HSMFsum2 = ttk.Label(master=sumtab, textvariable=HSMFvar, background='WHITE').grid(row=rt, column=ca)
EHLsum2 = ttk.Label(master=sumtab, textvariable=EHLvar).grid(row=ru, column=ca)

BCTIsum2 = ttk.Label(master=sumtab, textvariable=BCTIvar).grid(row=rp, column=cg)
BCTOsum2 = ttk.Label(master=sumtab, textvariable=BCTOvar, background='WHITE').grid(row=rq, column=cg)
BCMFsum2 = ttk.Label(master=sumtab, textvariable=BCMFvar).grid(row=rs, column=cg)

BoPSumheader = ttk.Label(master=sumtab, text='Balance of Plant (MW)', background='WHITE').grid(row=ra, column=cf, pady=15)

RXPheader = ttk.Label(master=sumtab, text='Reactors 1-4 Power & Total', background='WHITE').grid(row=rb, column=c, padx=10)
RXP1sum = ttk.Label(master=sumtab, textvariable=R1Pvar).grid(row=rc, column=c)
RXP2sum = ttk.Label(master=sumtab, textvariable=R2Pvar, background='WHITE').grid(row=rd, column=c)
RXP3sum = ttk.Label(master=sumtab, textvariable=R3Pvar).grid(row=re, column=c)
RXP4sum = ttk.Label(master=sumtab, textvariable=R4Pvar, background='WHITE').grid(row=rf, column=c)

PHXheader = ttk.Label(master=sumtab, text='PHX Power', background='WHITE').grid(row=rb, column=ca, padx=10)
PHX1_3sum = ttk.Label(master=sumtab, textvariable=PHX1_3Pvar).grid(row=rc, column=ca)
PHX4_6sum = ttk.Label(master=sumtab, textvariable=PHX4_6Pvar, background='WHITE').grid(row=rd, column=ca)
PHX7_9sum = ttk.Label(master=sumtab, textvariable=PHX7_9Pvar).grid(row=re, column=ca)
PHX10_12sum = ttk.Label(master=sumtab, textvariable=PHX10_12Pvar, background='WHITE').grid(row=rf, column=ca)

'''
PHXPSheader = ttk.Label(master=sumtab, text='PHX Power Setpoint', background='WHITE').grid(row=rb, column=cf, columnspan=2)
PHXPS1_3sum = ttk.Label(master=sumtab, textvariable=PHXPS1_3).grid(row=rc, column=cf, columnspan=2)
PHXPS4_6sum = ttk.Label(master=sumtab, textvariable=PHXPS4_6).grid(row=rd, column=cf, columnspan=2)
PHXPS7_9sum = ttk.Label(master=sumtab, textvariable=PHXPS7_9).grid(row=re, column=cf, columnspan=2)
PHXPS10_12sum = ttk.Label(master=sumtab, textvariable=PHXPS10_12).grid(row=rf, column=cf, columnspan=2)
'''

RXNPheader = ttk.Label(master=sumtab, text='PHX Net Power', background='WHITE').grid(row=rb, column=cf, padx=10)
RXNP1sum = ttk.Label(master=sumtab, textvariable=R1NPvar).grid(row=rc, column=cf)
RXNP2sum = ttk.Label(master=sumtab, textvariable=R2NPvar, background='WHITE').grid(row=rd, column=cf)
RXNP3sum = ttk.Label(master=sumtab, textvariable=R3NPvar).grid(row=re, column=cf)
RXNP4sum = ttk.Label(master=sumtab, textvariable=R4NPvar, background='WHITE').grid(row=rf, column=cf)
RXNPtotsum = ttk.Label(master=sumtab, textvariable=RXtotvar).grid(column=c, row=rg)

BCPheader = ttk.Label(master=sumtab, text='Brayton Cycle Total Power', background='WHITE').grid(row=rb, column=cg, padx=10)
BCPtotsum = ttk.Label(master=sumtab, textvariable=BCPtotvar).grid(row=rc, column=cg)
HSPheader = ttk.Label(master=sumtab, text='Heat Sink Power', background='WHITE').grid(row=rd, column=cg)
HSPsum = ttk.Label(master=sumtab, textvariable=HSPvar).grid(row=re, column=cg)

SVNPheader = ttk.Label(master=sumtab, text='Salt Vault Net Power', background='WHITE').grid(row=rb, column=cb, padx=10)
SVNPsum = ttk.Label(master=sumtab, textvariable=SVNPvar).grid(row=rc, column=cb)

Faultheader = ttk.Label(master=sumtab, text='Faults', background='WHITE').grid(row=rv, column=cf, pady=15)

SummaryVars(0, 2)
SummaryVars(1, 3)
SummaryVars(2, 4)
SummaryVars(3, 5)



def var_update():
    
    R1PL1var.set(D(BoPdict[0]['RXP'][-1]).quantize(twoplaces))
    #R1PL2var.set(D(BoPdict[0]['RXP'][-1]/3).quantize(twoplaces))
    #R1PL3var.set(D(BoPdict[0]['RXP'][-1]/3).quantize(twoplaces))

    R2PL1var.set(D(BoPdict[1]['RXP'][-1]).quantize(twoplaces))
    #R2PL2var.set(D(BoPdict[1]['RXP'][-1]/3).quantize(twoplaces))
    #R2PL3var.set(D(BoPdict[1]['RXP'][-1]/3).quantize(twoplaces))

    R3PL1var.set(D(BoPdict[2]['RXP'][-1]).quantize(twoplaces))
    #R3PL2var.set(D(BoPdict[2]['RXP'][-1]/3).quantize(twoplaces))
    #R3PL3var.set(D(BoPdict[2]['RXP'][-1]/3).quantize(twoplaces))

    R4PL1var.set(D(BoPdict[3]['RXP'][-1]).quantize(twoplaces))
    #R4PL2var.set(D(BoPdict[3]['RXP'][-1]/3).quantize(twoplaces))
    #R4PL3var.set(D(BoPdict[3]['RXP'][-1]/3).quantize(twoplaces))  

    R1Pvar.set(D(BoPdict[0]['RXP'][-1]).quantize(twoplaces))
    R2Pvar.set(D(BoPdict[1]['RXP'][-1]).quantize(twoplaces))
    R3Pvar.set(D(BoPdict[2]['RXP'][-1]).quantize(twoplaces))
    R4Pvar.set(D(BoPdict[3]['RXP'][-1]).quantize(twoplaces))
    RXtotvar.set(D(BoPdict[0]['RXP'][-1]+BoPdict[1]['RXP'][-1]+BoPdict[2]['RXP'][-1]+BoPdict[3]['RXP'][-1]).quantize(twoplaces))

    PLPHX1var.set(D(BoPdict[0]['PHXP1'][-1]).quantize(twoplaces))
    PLPHX2var.set(D(BoPdict[0]['PHXP2'][-1]).quantize(twoplaces))
    PLPHX3var.set(D(BoPdict[0]['PHXP3'][-1]).quantize(twoplaces))

    PLPHX4var.set(D(BoPdict[1]['PHXP1'][-1]).quantize(twoplaces))
    PLPHX5var.set(D(BoPdict[1]['PHXP2'][-1]).quantize(twoplaces))
    PLPHX6var.set(D(BoPdict[1]['PHXP3'][-1]).quantize(twoplaces))

    PLPHX7var.set(D(BoPdict[2]['PHXP1'][-1]).quantize(twoplaces))
    PLPHX8var.set(D(BoPdict[2]['PHXP2'][-1]).quantize(twoplaces))
    PLPHX9var.set(D(BoPdict[2]['PHXP3'][-1]).quantize(twoplaces))

    PLPHX10var.set(D(BoPdict[3]['PHXP1'][-1]).quantize(twoplaces))
    PLPHX11var.set(D(BoPdict[3]['PHXP2'][-1]).quantize(twoplaces))
    PLPHX12var.set(D(BoPdict[3]['PHXP3'][-1]).quantize(twoplaces))

    PHX1_3Pvar.set(D(BoPdict[0]['PHXP1'][-1]+BoPdict[0]['PHXP2'][-1]+BoPdict[0]['PHXP3'][-1]).quantize(twoplaces))
    PHX4_6Pvar.set(D(BoPdict[1]['PHXP1'][-1]+BoPdict[1]['PHXP2'][-1]+BoPdict[1]['PHXP3'][-1]).quantize(twoplaces))
    PHX7_9Pvar.set(D(BoPdict[2]['PHXP1'][-1]+BoPdict[2]['PHXP2'][-1]+BoPdict[2]['PHXP3'][-1]).quantize(twoplaces))
    PHX10_12Pvar.set(D(BoPdict[3]['PHXP1'][-1]+BoPdict[3]['PHXP2'][-1]+BoPdict[3]['PHXP3'][-1]).quantize(twoplaces))

    BCPvar1.set(D(BoPdict[4]['BCP1'][-1]).quantize(twoplaces))
    BCPvar2.set(D(BoPdict[4]['BCP2'][-1]).quantize(twoplaces))
    BCPvar3.set(D(BoPdict[4]['BCP3'][-1]).quantize(twoplaces))
    HSvar.set(D(BoPdict[4]['HSP'][-1]).quantize(twoplaces))

    BCPtotvar.set(D(BoPdict[4]['BCP1'][-1]+BoPdict[4]['BCP2'][-1]+BoPdict[4]['BCP3'][-1]).quantize(twoplaces))

    R1NPvar.set(D(BoPdict[0]['PHXNP'][-1]).quantize(twoplaces))
    R2NPvar.set(D(BoPdict[1]['PHXNP'][-1]).quantize(twoplaces))
    R3NPvar.set(D(BoPdict[2]['PHXNP'][-1]).quantize(twoplaces))
    R4NPvar.set(D(BoPdict[3]['PHXNP'][-1]).quantize(twoplaces))

    SVNPvar.set(D(BoPdict[4]['SVNP'][-1]).quantize(twoplaces))

    SVTvar.set(D(BoPdict[4]['SVT'][-1]).quantize(twoplaces))
    HSTIvar.set(D(BoPdict[4]['HSTI'][-1]).quantize(twoplaces))
    HSTOvar.set(D(BoPdict[4]['HSTO'][-1]).quantize(twoplaces))
    HSMFvar.set(D(BoPdict[4]['HSMF'][-1]).quantize(twoplaces))
    HSPvar.set(D(BoPdict[4]['HSP'][-1]).quantize(twoplaces))
    EHLvar.set(D(BoPdict[4]['EHL'][-1]).quantize(twoplaces))
    
    BCTIvar.set(D(BoPdict[4]['BCTI1'][-1]).quantize(twoplaces))
    BCTOvar.set(D(BoPdict[4]['BCTO1'][-1]).quantize(twoplaces))
    BCMFvar.set(D(BoPdict[4]['BCMF1'][-1]).quantize(twoplaces))

    PHXPS1.set(D(yDict[0]['PHXP1S'][-1]).quantize(twoplaces))
    PHXPS2.set(D(yDict[0]['PHXP2S'][-1]).quantize(twoplaces))
    PHXPS3.set(D(yDict[0]['PHXP3S'][-1]).quantize(twoplaces))
    PHXPS4.set(D(yDict[1]['PHXP1S'][-1]).quantize(twoplaces))
    PHXPS5.set(D(yDict[1]['PHXP2S'][-1]).quantize(twoplaces))
    PHXPS6.set(D(yDict[1]['PHXP3S'][-1]).quantize(twoplaces))
    PHXPS7.set(D(yDict[2]['PHXP1S'][-1]).quantize(twoplaces))
    PHXPS8.set(D(yDict[2]['PHXP2S'][-1]).quantize(twoplaces))
    PHXPS9.set(D(yDict[2]['PHXP3S'][-1]).quantize(twoplaces))
    PHXPS10.set(D(yDict[3]['PHXP1S'][-1]).quantize(twoplaces))
    PHXPS11.set(D(yDict[3]['PHXP2S'][-1]).quantize(twoplaces))
    PHXPS12.set(D(yDict[3]['PHXP3S'][-1]).quantize(twoplaces))

    PHXPS1_3.set(D(yDict[0]['PHXP1S'][-1]+yDict[0]['PHXP2S'][-1]+yDict[0]['PHXP3S'][-1]).quantize(twoplaces))
    PHXPS4_6.set(D(yDict[1]['PHXP1S'][-1]+yDict[1]['PHXP2S'][-1]+yDict[1]['PHXP3S'][-1]).quantize(twoplaces))
    PHXPS7_9.set(D(yDict[2]['PHXP1S'][-1]+yDict[2]['PHXP2S'][-1]+yDict[2]['PHXP3S'][-1]).quantize(twoplaces))
    PHXPS10_12.set(D(yDict[3]['PHXP1S'][-1]+yDict[3]['PHXP2S'][-1]+yDict[3]['PHXP3S'][-1]).quantize(twoplaces))

    RTOS1.set(D(yDict[0]['RTOS'][-1]).quantize(twoplaces))
    RTOS2.set(D(yDict[1]['RTOS'][-1]).quantize(twoplaces))
    RTOS3.set(D(yDict[2]['RTOS'][-1]).quantize(twoplaces))
    RTOS4.set(D(yDict[3]['RTOS'][-1]).quantize(twoplaces))

    gui.after(900, var_update)


def BoPlabels():
    '''
    BoPtab.grid_rowconfigure(1, weight=0)
    BoPtab.grid_rowconfigure(2, weight=1)
    BoPtab.grid_rowconfigure(3, weight=1)
    BoPtab.grid_rowconfigure(4, weight=1)
    BoPtab.grid_rowconfigure(5, weight=1)
    BoPtab.grid_rowconfigure(6, weight=1)
    BoPtab.grid_rowconfigure(7, weight=1)
    BoPtab.grid_rowconfigure(8, weight=1)
    BoPtab.grid_rowconfigure(9, weight=1)
    BoPtab.grid_rowconfigure(10, weight=1)
    BoPtab.grid_rowconfigure(11, weight=1)
    BoPtab.grid_rowconfigure(12, weight=1)
    BoPtab.grid_rowconfigure(13, weight=1)
    BoPtab.grid_rowconfigure(14, weight=1)
    BoPtab.grid_rowconfigure(15, weight=1)
    BoPtab.grid_rowconfigure(16, weight=1)
    BoPtab.grid_rowconfigure(17, weight=1)
    
    BoPtab.grid_columnconfigure(1, weight=1)
    BoPtab.grid_columnconfigure(3, weight=1)
    BoPtab.grid_columnconfigure(5, weight=1)
    BoPtab.grid_columnconfigure(6, weight=1)
    '''
    logo2 = ttk.Label(master=BoPtab, image=pittlogo).grid(row=1, column=1)

    R1label = ttk.Label(master=BoPtab, text='R1 Power', background='WHITE').grid(row=2, column=1, sticky='e')
    R12PL1 = ttk.Label(master=BoPtab, textvariable=R1PL1var).grid(row=4, column=1, sticky='e')
    #R12PL2 = ttk.Label(master=BoPtab, textvariable=R1PL2var).grid(row=4, column=1)
    #R12PL3 = ttk.Label(master=BoPtab, textvariable=R1PL3var).grid(row=5, column=1)

    R2label = ttk.Label(master=BoPtab, text='R2 Power', background='WHITE').grid(row=6, column=1, sticky='e')
    R22PL1 = ttk.Label(master=BoPtab, textvariable=R2PL1var).grid(row=8, column=1, sticky='e')
    #R22PL2 = ttk.Label(master=BoPtab, textvariable=R2PL2var).grid(row=8, column=1)
    #R22PL3 = ttk.Label(master=BoPtab, textvariable=R2PL3var).grid(row=9, column=1)

    R3label = ttk.Label(master=BoPtab, text='R3 Power', background='WHITE').grid(row=10, column=1, sticky='e')
    R32PL1 = ttk.Label(master=BoPtab, textvariable=R3PL1var).grid(row=12, column=1, sticky='e')
    #R32PL2 = ttk.Label(master=BoPtab, textvariable=R3PL2var).grid(row=12, column=1)
    #R32PL3 = ttk.Label(master=BoPtab, textvariable=R3PL3var).grid(row=13, column=1)

    R4label = ttk.Label(master=BoPtab, text='R4 Power', background='WHITE').grid(row=14, column=1, sticky='e')
    R42PL1 = ttk.Label(master=BoPtab, textvariable=R4PL1var).grid(row=16, column=1, sticky='e')
    #R42PL2 = ttk.Label(master=BoPtab, textvariable=R4PL2var).grid(row=16, column=1)
    #R42PL3 = ttk.Label(master=BoPtab, textvariable=R4PL3var).grid(row=17, column=1)

    PLlabel = ttk.Label(master=BoPtab, text='PHX Power', background='WHITE').grid(row=2, column=3, padx=10)
    PHXtotheader = ttk.Label(master=BoPtab, text='Total', background='WHITE').grid(row=2, column=4, padx=10)
    PL2PHX1 = ttk.Label(master=BoPtab, textvariable=PLPHX1var).grid(row=3, column=3)
    PL2PHX2 = ttk.Label(master=BoPtab, textvariable=PLPHX2var).grid(row=4, column=3)
    PL2PHX3 = ttk.Label(master=BoPtab, textvariable=PLPHX3var).grid(row=5, column=3)
    PHXtot1 = ttk.Label(master=BoPtab, textvariable=PHX1_3Pvar).grid(row=4, column=4)

    PL2PHX4 = ttk.Label(master=BoPtab, textvariable=PLPHX4var).grid(row=7, column=3)
    PL2PHX5 = ttk.Label(master=BoPtab, textvariable=PLPHX5var).grid(row=8, column=3)
    PL2PHX6 = ttk.Label(master=BoPtab, textvariable=PLPHX6var).grid(row=9, column=3)
    PHXtot2 = ttk.Label(master=BoPtab, textvariable=PHX4_6Pvar).grid(row=8, column=4)

    PL2PHX7 = ttk.Label(master=BoPtab, textvariable=PLPHX7var).grid(row=11, column=3)
    PL2PHX8 = ttk.Label(master=BoPtab, textvariable=PLPHX8var).grid(row=12, column=3)
    PL2PHX9 = ttk.Label(master=BoPtab, textvariable=PLPHX9var).grid(row=13, column=3)
    PHXtot3 = ttk.Label(master=BoPtab, textvariable=PHX7_9Pvar).grid(row=12, column=4)

    PL2PHX10 = ttk.Label(master=BoPtab, textvariable=PLPHX10var).grid(row=15, column=3)
    PL2PHX11 = ttk.Label(master=BoPtab, textvariable=PLPHX11var).grid(row=16, column=3)
    PL2PHX12 = ttk.Label(master=BoPtab, textvariable=PLPHX12var).grid(row=17, column=3)
    PHXtot4 = ttk.Label(master=BoPtab, textvariable=PHX10_12Pvar).grid(row=16, column=4)

    BClabel = ttk.Label(master=BoPtab, text='Brayton Cycle Thermal Power', background='WHITE').grid(row=2, column=5)
    BCPtotheader = ttk.Label(master=BoPtab, text='Total', background='WHITE').grid(row=2, column=6, padx=10)
    BCPlabel1 = ttk.Label(master=BoPtab, textvariable=BCPvar1).grid(row=3, column=5, rowspan=3)
    BCPlabel2 = ttk.Label(master=BoPtab, textvariable=BCPvar2).grid(row=7, column=5, rowspan=3)
    BCPlabel3 = ttk.Label(master=BoPtab, textvariable=BCPvar3).grid(row=11, column=5, rowspan=3)
    BCPtot = ttk.Label(master=BoPtab, textvariable=BCPtotvar).grid(row=8, column=6)

    HSlabel = ttk.Label(master=BoPtab, text='Heat Sink Thermal Power', background='WHITE').grid(row=14, column=5)
    HSlabel1 = ttk.Label(master=BoPtab, textvariable=HSvar).grid(row=15, column=5, rowspan=3)

    R1NPheader = ttk.Label(master=BoPtab, text='PHX1-3 Net Power' , background='WHITE').grid(row=2 , column=7)
    R1NPlabel = ttk.Label(master=BoPtab, textvariable=R1NPvar).grid(row=3 , column=7)

    R2NPheader = ttk.Label(master=BoPtab, text='PHX4-6 Net Power' , background='WHITE').grid(row=5 , column=7)
    R2NPlabel = ttk.Label(master=BoPtab, textvariable=R2NPvar).grid(row=6 , column=7)

    R3NPheader = ttk.Label(master=BoPtab, text='PHX7-9 Net Power' , background='WHITE').grid(row=8 , column=7)
    R3NPlabel = ttk.Label(master=BoPtab, textvariable=R3NPvar).grid(row=9 , column=7)

    R4NPheader = ttk.Label(master=BoPtab, text='PHX10-12 Net Power' , background='WHITE').grid(row=11 , column=7)
    R4NPlabel = ttk.Label(master=BoPtab, textvariable=R4NPvar).grid(row=12 , column=7)

    SVNPheader = ttk.Label(master=BoPtab, text='Salt Vault Net Power' , background='WHITE').grid(row=14 , column=7)
    SVNPlabel = ttk.Label(master=BoPtab, textvariable=SVNPvar).grid(row=15 , column=7)

            

class Radiobuttons:

    def __init__(self, tab, reactor, col):
        self.tabcol = tk.IntVar()
        #self.tabcol.set(1)
        logo = ttk.Label(master=tab, image=pittlogo).grid(row=1, column=1, sticky='w')
        self.createRBs(tab, reactor, col)
        
    def createRBs(self, tab, reactor, col):

        if tab == rx1tab or tab == rx2tab or tab == rx3tab or tab == rx4tab:
            self.PTIbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=1, command=lambda: self.rbsequence(tab, reactor, col), text='PL Hot Leg Temp (C)')
            self.PTIbutton.grid(row=4, column=col, pady=1, padx=7, sticky='W')

            self.PTObutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=2, command=lambda: self.rbsequence(tab, reactor, col), text='PL Cold Leg Temp (C)')
            self.PTObutton.grid(row=5, column=col, pady=1, padx=7, sticky='W')

            self.STIbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=3, command=lambda: self.rbsequence(tab, reactor, col), text='SL Cold Leg Temp (C)')
            self.STIbutton.grid(row=6, column=col, pady=1, padx=7, sticky='W')

            self.STObutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=4, command=lambda: self.rbsequence(tab, reactor, col), text='SL Hot Leg Temp (C)')
            self.STObutton.grid(row=7, column=col, pady=1, padx=7, sticky='W')

            self.RTObutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=5, command=lambda: self.rbsequence(tab, reactor, col), text='Reactor Temperature Out (C)')
            self.RTObutton.grid(row=8, column=col, pady=1, padx=7, sticky='W')

            self.PMFbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=6, command=lambda: self.rbsequence(tab, reactor, col), text='Primary Mass Flow (kg/s)')
            self.PMFbutton.grid(row=9, column=col, pady=1, padx=7, sticky='W')

            self.SMFbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=7, command=lambda: self.rbsequence(tab, reactor, col), text='Secondary Mass Flow (kg/s)')
            self.SMFbutton.grid(row=10, column=col, pady=1, padx=7, sticky='W')

        if tab == bctab:
            self.BCTIbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=8, command=lambda: self.rbsequence(tab, reactor, col), text='Brayton Temperature In (C)')
            self.BCTIbutton.grid(row=4, column=col, pady=1, padx=7, sticky='W')

            self.BCTObutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=9, command=lambda: self.rbsequence(tab, reactor, col), text='Brayton Temperature Out (C)')
            self.BCTObutton.grid(row=5, column=col, pady=1, padx=7, sticky='W')

            self.BCMFbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=10, command=lambda: self.rbsequence(tab, reactor, col), text='Brayton Mass Flow (kg/s)')
            self.BCMFbutton.grid(row=6, column=col, pady=1, padx=7, sticky='W')

            self.BCEPbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=11, command=lambda: self.rbsequence(tab, reactor, col), text='Brayton Electrical Power (MW)')
            self.BCEPbutton.grid(row=7, column=col, pady=1, padx=7, sticky='W')

        if tab == svtab:
            self.SVTbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=12, command=lambda: self.rbsequence(tab, reactor, col), text='Salt Vault Temperature (C)')
            self.SVTbutton.grid(row=4, column=col, pady=1, padx=7, sticky='W')

            self.HSTbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=13, command=lambda: self.rbsequence(tab, reactor, col), text='Heat Sink Temperature In (C)')
            self.HSTbutton.grid(row=5, column=col, pady=1, padx=7, sticky='W')

            self.HSMFbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=14, command=lambda: self.rbsequence(tab, reactor, col), text='Heat Sink Mass Flow (kg/s)')
            self.HSMFbutton.grid(row=6, column=col, pady=1, padx=7, sticky='W')

            self.HSTPbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=15, command=lambda: self.rbsequence(tab, reactor, col), text='Heat Sink Thermal Power (MW)')
            self.HSTPbutton.grid(row=7, column=col, pady=1, padx=7, sticky='W')

            self.ELbutton = tk.Radiobutton(master=tab, variable=self.tabcol, value=16, command=lambda: self.rbsequence(tab, reactor, col), text='Environmental Heat Loss (MW)')
                                           
            self.ELbutton.grid(row=8, column=col, pady=1, padx=7, sticky='W')    

    def rbsequence(self, tab, reactor, col):
        
        if self.tabcol.get() == 1:
            LiveGraph(tab, reactor, 'PTI', 2, col)
        elif self.tabcol.get() == 2:
            LiveGraph(tab, reactor, 'PTO1', 2, col)
        elif self.tabcol.get() == 3:
            LiveGraph(tab, reactor, 'STI', 2, col)
        elif self.tabcol.get() == 4:
            LiveGraph(tab, reactor, 'STO1', 2, col)
        elif self.tabcol.get() == 5:
            LiveGraph(tab, reactor, 'RTO', 2, col)
        elif self.tabcol.get() == 6:
            LiveGraph(tab, reactor, 'PMF1', 2, col)
        elif self.tabcol.get() == 7:
            LiveGraph(tab, reactor, 'SMF1', 2, col)
        elif self.tabcol.get() == 8:
            LiveGraph(tab, reactor, 'BCTI1', 2, col)
        elif self.tabcol.get() == 9:
            LiveGraph(tab, reactor, 'BCTO1', 2, col)
        elif self.tabcol.get() == 10:
            LiveGraph(tab, reactor, 'BCMF1', 2, col)
        elif self.tabcol.get() == 11:
            LiveGraph(tab, reactor, 'BCP1', 2, col)
        elif self.tabcol.get() == 12:
            LiveGraph(tab, reactor, 'SVT', 2, col)
        elif self.tabcol.get() == 13:
            LiveGraph(tab, reactor, 'HSTI', 2, col)
        elif self.tabcol.get() == 14:
            LiveGraph(tab, reactor, 'HSMF', 2, col)
        elif self.tabcol.get() == 15:
            LiveGraph(tab, reactor, 'HSP', 2, col)
        elif self.tabcol.get() == 16:
            LiveGraph(tab, reactor, 'EHL', 2, col)
        

        
class Labelupdate:

    def __init__(self, tab, reactor):
        
        self.PTIvar = tk.DoubleVar()
        self.PTOvar = tk.DoubleVar()
        self.STIvar = tk.DoubleVar()
        self.STOvar = tk.DoubleVar()
        self.RTOvar = tk.DoubleVar()
        self.PMFvar = tk.DoubleVar()
        self.SMFvar = tk.DoubleVar()

        self.SVTvar = tk.DoubleVar()
        self.HSTvar = tk.DoubleVar()
        self.HSMFvar = tk.DoubleVar()
        self.HSTPvar = tk.DoubleVar()
        self.ELvar = tk.DoubleVar()

        self.BCTIvar = tk.DoubleVar()
        self.BCTOvar = tk.DoubleVar()
        self.BCMFvar = tk.DoubleVar()
        self.BCEPvar = tk.DoubleVar()
        
        dummy = 1
        self.update_vars(reactor, tab)
        self.updatelabels(tab)
        
    def update_vars(self, reactor, tab):

        if tab == rx1tab or tab == rx2tab or tab == rx3tab or tab == rx4tab:
            self.PTIvar.set(D(yDict[reactor]['PTI'][-1]).quantize(twoplaces))
            self.PTOvar.set(D(yDict[reactor]['PTO1'][-1]).quantize(twoplaces))
            self.STOvar.set(D(yDict[reactor]['STO1'][-1]).quantize(twoplaces))
            self.STIvar.set(D(yDict[reactor]['STI'][-1]).quantize(twoplaces)) 
            self.RTOvar.set(D(yDict[reactor]['RTO'][-1]).quantize(twoplaces)) 
            self.PMFvar.set(D(yDict[reactor]['PMF1'][-1]).quantize(twoplaces)) 
            self.SMFvar.set(D(yDict[reactor]['SMF1'][-1]).quantize(twoplaces))

        if tab == svtab:
            self.SVTvar.set(D(yDict[reactor]['SVT'][-1]).quantize(twoplaces))
            self.HSTvar.set(D(yDict[reactor]['HSTI'][-1]).quantize(twoplaces))
            self.HSMFvar.set(D(yDict[reactor]['HSMF'][-1]).quantize(twoplaces))
            self.HSTPvar.set(D(yDict[reactor]['HSP'][-1]).quantize(twoplaces)) 
            self.ELvar.set(D(yDict[reactor]['EHL'][-1]).quantize(twoplaces))

        if tab == bctab:
            self.BCTIvar.set(D(yDict[reactor]['BCTI1'][-1]).quantize(twoplaces))
            self.BCTOvar.set(D(yDict[reactor]['BCTO1'][-1]).quantize(twoplaces))
            self.BCMFvar.set(D(yDict[reactor]['BCMF1'][-1]).quantize(twoplaces))
            self.BCEPvar.set(D(yDict[reactor]['BCP1'][-1]).quantize(twoplaces))  

        gui.after(900, self.update_vars, reactor, tab) 

    def updatelabels(self, tab):

        if tab == rx1tab or tab == rx2tab or tab == rx3tab or tab == rx4tab:
            self.PTIlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.PTIvar)
            self.PTIlabel.grid(row=4, column=2, sticky='E')

            self.PTOlabel = ttk.Label(master=tab, textvariable=self.PTOvar)
            self.PTOlabel.grid(row=5, column=2, sticky='E')

            self.STIlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.STIvar)
            self.STIlabel.grid(row=6, column=2, sticky='E')

            self.STOlabel = ttk.Label(master=tab, textvariable=self.STOvar)
            self.STOlabel.grid(row=7, column=2, sticky='E')

            self.RTOlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.RTOvar)
            self.RTOlabel.grid(row=8, column=2, sticky='E')

            self.PMFlabel = ttk.Label(master=tab, textvariable=self.PMFvar)
            self.PMFlabel.grid(row=9, column=2, sticky='E')

            self.SMFlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.SMFvar)
            self.SMFlabel.grid(row=10, column=2, sticky='E')

        if tab == svtab:
            self.SVTlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.SVTvar)
            self.SVTlabel.grid(row=4, column=2, sticky='E')

            self.HSTlabel = ttk.Label(master=tab, textvariable=self.HSTvar)
            self.HSTlabel.grid(row=5, column=2, sticky='E')

            self.HSMFlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.HSMFvar)
            self.HSMFlabel.grid(row=6, column=2, sticky='E')

            self.HSTPlabel = ttk.Label(master=tab, textvariable=self.HSTPvar)
            self.HSTPlabel.grid(row=7, column=2, sticky='E')

            self.EHLlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.ELvar)
            self.EHLlabel.grid(row=8, column=2, sticky='E')

        if tab == bctab:
            self.BCTIlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.BCTIvar)
            self.BCTIlabel.grid(row=4, column=2, sticky='E')

            self.BCTOlabel = ttk.Label(master=tab, textvariable=self.BCTOvar)
            self.BCTOlabel.grid(row=5, column=2, sticky='E')

            self.BCMFlabel = ttk.Label(master=tab, background='WHITE', textvariable=self.BCMFvar)
            self.BCMFlabel.grid(row=6, column=2, sticky='E')

            self.BCEPlabel = ttk.Label(master=tab, textvariable=self.BCEPvar)
            self.BCEPlabel.grid(row=7, column=2, sticky='E')

r1update = Labelupdate(rx1tab, 0)
r2update = Labelupdate(rx2tab, 1)
r3update = Labelupdate(rx3tab, 2)
r4update = Labelupdate(rx4tab, 3)
svupdate = Labelupdate(svtab, 4)
bcupdate = Labelupdate(bctab, 4)

#print yDict[0]
#print BoPdict[0]
#print yDict[4]
#print BoPdict[4]

for x in range(1,4,2):
    Radiobuttons(rx1tab, 0, x)
    Radiobuttons(rx2tab, 1, x)
    Radiobuttons(rx3tab, 2, x)
    Radiobuttons(rx4tab, 3, x)
    Radiobuttons(svtab, 4, x)
    Radiobuttons(bctab, 4, x)


var_update()
BoPlabels()


#LiveGraph(tab1, 0, 'PTI', 1, 1)
#LiveGraph(tab1, 0, 'RTO', 1, 3)

'''
PHXPbutton1 = ttk.Radiobutton(master=tab1, command=LiveGraph(tab1, 0, 'PHXP', 1, 1), variable=1)
PHXPbutton1.grid(row=9, column=1)

PHXEbutton1 = ttk.Radiobutton(master=tab1, command=LiveGraph(tab1, 0, 'PHXE', 1, 1), variable=1)
PHXEbutton1.grid(row=10, column=1)

RXPbutton1 = ttk.Radiobutton(master=tab1, command=LiveGraph(tab1, 0, 'RXP', 1, 1), variable=1)
RXPbutton1.grid(row=11, column=1)
'''


gui.mainloop()











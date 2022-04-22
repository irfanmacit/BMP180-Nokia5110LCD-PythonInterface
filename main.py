
## these codes are written by irfanmacit@gmail.com
## you can use and share distribute freeeeely happy fun
## updated and rewriting April, 2021

import sys
import serial
import serial.tools.list_ports

from time import *
import pymysql.cursors

from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QTableWidgetItem, QTabWidget, \
    QHeaderView  # Tasarladığımız arayüzün kullanılabilmesi için

from BMP180Nokia5110 import *

app = QtWidgets.QApplication(sys.argv)

MainWindow = QtWidgets.QMainWindow()

ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

###########DATABASE CONNECTION##################
import sqlite3

global kursor
global baglanti

baglanti = sqlite3.connect('BMP180Nokia5110.db')
kursor = baglanti.cursor()

print("Veriabanına bağlandı..")
ui.statusbar.showMessage(" " * 1 + " Veritabanı Bağlantısı Yapıldı ...!", 1500)

##################################################



def START_MEASURE():
    port = "COM8"
    baud = 115200

    global seri

    try:

        seri = serial.Serial(port, baudrate=baud, timeout=0)

        if seri.is_open:
            ui.statusbar.showMessage(" " * 1 + " Seri Port Bağlantısı Yapıldı ...!", 1500)

            global timer1
            timer1 = QtCore.QTimer()
            timer1.start(300)
            timer1.timeout.connect(SENSOR)

    except:

        ui.statusbar.showMessage(" " * 1 + " Bağlantı yapılamadı lütfen portları kontrol edin...!", 1500)

def STOP_MEASURE():
    try:

        global seri
        timer1.stop()
        if seri.is_open:
            seri.close()
            print("Bağlantı kapatıldı")
            ui.lcdTemp.display("....")
            ui.lcdAltitude.display("....")
            ui.lcdPressure.display("....")


    except:

        ui.statusbar.showMessage(" " * 1 + " COM portları kontrol edin ...!", 1500)


def SENSOR():
    global seri

    data = seri.read(31)  # Seri Porttan 5 bytelık veri okunuyor
    #    data = ser.readlines()
    print("Bekleyen byte sayısı :", seri.in_waiting)
    print("Veri boyutu: ", seri.bytesize)
    print("Veri özelliği: ", seri.BYTESIZES)
    print("Alınan veri: ", data)
    print("\n")

    veri1 = str(data)
    veri = veri1.replace('\\n', '0')
    print("kırpılmış veri: ", str(veri))
    print("\n")

    global derece, yukseklik, basinci

    if len(veri) > 17:  # b'' boşluk içermiyorsa yoksa program duruyor
        sicaklik = veri[2:6]
        print("Sıcaklık: ", sicaklik)
        yukselti = veri[7:11]
        print("Yükselti: ", yukselti)
        basinc = veri[12:16]
        print("Basınç: ", basinc)

        derece = float(veri[2:6])
        yukseklik = float(veri[7:11])
        basinci = float(veri[12:16])
        DBRECORD()
        LISTING()

        if derece > 30.0:
            ui.lcdTemp.setStyleSheet("""QLCDNumber { 
                                                background-color: red; 
                                                color: white; }""")
        else:
            ui.lcdTemp.setStyleSheet("""QLCDNumber 
                                               { background-color: green; 
                                                 color: yellow;
                                               }""")
        if basinci > 1000.0:
            ui.lcdPressure.setStyleSheet("""QLCDNumber { 
                                                background-color: blue; 
                                                color: yellow; }""")
        else:
            ui.lcdPressure.setStyleSheet("""QLCDNumber 
                                               { background-color: red; 
                                                 color: yellow;
                                               }""")
        ui.lcdAltitude.setStyleSheet("""QLCDNumber 
                                                       { background-color: purple; 
                                                         color: yellow;
                                                       }""")
        ui.lcdTemp.display(derece)
        ui.lcdAltitude.display(yukseklik)
        ui.lcdPressure.display(basinci)

def DBRECORD():
    row = ui.tblDatabase.rowCount()
    ui.tblDatabase.setRowCount(row + 1)
    kursor.execute("INSERT INTO barometer (time, temp, pressure, altitude) VALUES (?,?,?,?)", \
                             (ctime(), derece, basinci, yukseklik))
    baglanti.commit()

def LISTING():
    ui.tblDatabase.clear()
    ui.tblDatabase.setHorizontalHeaderLabels(('id', 'time', 'temp', 'pressure', 'altitude'))
    ui.tblDatabase.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    kursor.execute("SELECT * FROM barometer")
    for satirIndeks, satirVerisi in enumerate(kursor):
        for sutunIndeks, sutunVerisi in enumerate(satirVerisi):
            ui.tblDatabase.setItem(satirIndeks, sutunIndeks, QTableWidgetItem(str(sutunVerisi)))
    baglanti.commit()


def EXIT_MEASURE():
    baglanti.close()
    seri.close()
    sys.exit(app.exec_())



ui.pbStart.clicked.connect(START_MEASURE)
ui.pbStop.clicked.connect(STOP_MEASURE)
ui.pbExit.clicked.connect(EXIT_MEASURE)

sys.exit(app.exec_())



import copy
import sys
import os
import time
import ncloader
import ntpath

import pandas as pd
import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QFileDialog, QApplication, QWidget, QLabel, QComboBox, QCheckBox

dFCutstemp = ''

pd.options.mode.chained_assignment = None

def LeftAngle(row):
    if row['AngleL2'].find('I') > -1:
        return '90'
    if row['AngleL2'].find('V') > -1:
        return '45'
    return float(row['AngleL2']) * 1


def RightAngle(row):
    if row['AngleR2'].find('I') > -1:
        return '90'
    if row['AngleR2'].find('V') > -1:
        return '45'
    return float(row['AngleR2']) * 1


def LeftAngleSaw(row):
    if row['AngleL2'].find('I') > -1:
        return '900'
    if row['AngleL2'].find('V') > -1:
        return '450'
    return float(row['AngleL2']) * 10


def RightAngleSaw(row):
    if row['AngleR2'].find('I') > -1:
        return '900'
    if row['AngleR2'].find('V') > -1:
        return '450'
    return float(row['AngleR2']) * 10


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Cutting lists generator'
        self.left = 100
        self.top = 100
        self.width = 350
        self.height = 260
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.textbox = QLineEdit(self)
        self.textbox.move(30, 20)
        self.textbox.setAlignment(Qt.AlignCenter)
        self.textbox.resize(280, 40)

        self.label1 = QLabel('Program creates files for double head saws', self)

        self.label1.resize(270, 120)
        self.label1.move(40, 30)
        self.label1.setAlignment(Qt.AlignCenter)

        self.checkBJM = QCheckBox('BJM', self)
        self.checkBJM.setChecked(True)
        self.checkBJM.move(70, 165)

        self.checkETX = QCheckBox('ETX', self)
        self.checkETX.move(200, 165)

        listCut = ["Ruch głowicy", "Ruch piły"]
        self.combo = QComboBox(self)
        self.combo.clear()
        self.combo.addItems(listCut)
        self.combo.move(200, 125)

        searchbtn = QPushButton('Logikal', self)
        searchbtn.move(40, 120)
        searchbtn.clicked.connect(self.openFileNameDialog)

        self.labelScratch = QLabel('Scratch DB_Zlec:', self)
        self.labelScratch.move(40, 205)

        self.textScratch = QLineEdit(self)
        self.textScratch.move(150, 200)
        self.textScratch.setAlignment(Qt.AlignCenter)
        self.textScratch.resize(150, 30)

        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Wyszukaj plik *.ncx z listą cięć", "",
                                                  "NCX Excel files (*.NCX)", options=options)

        if fileName:
            print(fileName)
            self.textbox.setText(fileName)
            x = self.ncxToCun(fileName)
            time.sleep(1.0)
            self.saveFileDialog(x)

    def saveFileDialog(self, dataFrame):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Wpisz nazwe zlecenia i wybierz lokalizacje w celu zapisu", "",
                                                  "CUN Files (*.CUN)", options=options)

        profilList = dataFrame['Profil'].unique()
        iterator = '0'
        ntpath.basename("a/b/c")

        def path_leaf(path):
            head, tail = ntpath.split(path)
            return tail or ntpath.basename(head)

        if fileName:
            print(fileName)

            for p in profilList:
                if 'cutProfil' in dFCutstemp.columns:
                    df = dFCutstemp[dFCutstemp['cutProfil'] == p]
                else:
                    df = dFCutstemp[dFCutstemp['Profil'] == p]
                short = str(p)[-4:]

                if self.checkETX.isChecked():
                    dirName = os.path.dirname(fileName)
                    shortFileName = os.path.basename(fileName)
                    #dirToLocation = dirToLocation.encode()
                    file = open(dirName + '/ETX/' + shortFileName + short + '.txt', 'w')

                    if 'AngleL2' in df.columns:
                        for i, row_ in df.iterrows():
                            if i < df.shape[0] - 1:
                                file.write(path_leaf(fileName + short) + '\n' + row_['Opis'] + '\n' + row_['Numer'] + '\n' + row_['Profil'] + ';' + row_['CNC'] + '\n' + str(row_['DlugoscCiecia']) + ';' + str(
                                    row_['AngleL2']) + ';' + str(row_['AngleR2']) + '\n')
                            else:
                                file.write(path_leaf(fileName + short) + '\n' + row_['Opis'] + '\n' + row_['Numer'] + '\n' + row_['Profil'] + ';' + row_[
                                    'CNC'] + '\n' + str(row_['DlugoscCiecia']) + ';' + str(
                                    row_['AngleL2']) + ';' + str(row_['AngleR2']))
                        file.close()
                    else:
                        for i, row_ in df.iterrows():
                            if i < df.shape[0] - 1:
                                file.write(path_leaf(fileName + short) + '\n' + row_['cutDescription'] + '\n' + row_['cutNumber'] + '\n' + row_['cutProfil'] + ';' + row_['cutCNC'] + '\n' + str(row_['cutLength']) + ';' + str(
                                    row_['cutAngleL']) + ';' + str(row_['cutAngleR']) + '\n')
                            else:
                                file.write(path_leaf(fileName + short) + '\n' + row_['cutDescription'] + '\n' + row_['cutNumber'] + '\n' + row_['cutProfil'] + ';' + row_['cutCNC'] + '\n' + str(row_['cutLength']) + ';' + str(
                                    row_['cutAngleL']) + ';' + str(row_['cutAngleR']))
                        file.close()

            for p in profilList:
                df = dataFrame[dataFrame['Profil'] == p]
                short = str(p)[-4:]
                file = open(fileName + short + '.CUN', 'w')
                file.write(chr(1) + "Star - New Record ")
                for i in range(62):
                    file.write(chr(0))
                file.write("cfrdts" + chr(0) + "        CHIL soft tm  ")
                file.write(chr(0))
                file.close()
                basepath = os.path.basename(fileName)+short
                print(basepath)

                for (idx, profil) in df.iterrows():

                    dlugosc_dec = int(profil.DlugoscCiecia)
                    kat_lewy_dec = int(profil.AngleL2)
                    kat_prawy_dec = int(profil.AngleR2)
                    kat_lewy_dziesietne = int(round(((kat_lewy_dec % 1) * 10), 0))
                    kat_prawy_dziesietne = int(round(((kat_prawy_dec % 1) * 10), 0))
                    if kat_lewy_dziesietne > 0:
                        kat_lewy_dziesietne *= 6
                    if kat_prawy_dziesietne > 0:
                        kat_prawy_dziesietne *= 6

                    ilosc_dec = int(profil.Ilosc)
                    wys_dec = int(profil.Wysokosc)

                    hexed_dlu = hex(dlugosc_dec).replace('x', '')
                    hexed_kat_L = hex(kat_lewy_dec).replace('x', '')
                    hexed_kat_R = hex(kat_prawy_dec).replace('x', '')
                    hexed_katDzies_L = hex(kat_lewy_dziesietne).replace('x', '')
                    hexed_katDzies_R = hex(kat_prawy_dziesietne).replace('x', '')
                    hexed_ilosc = hex(ilosc_dec).replace('x', '')
                    hexed_wys = hex(wys_dec).replace('x', '')

                    if (len(hexed_dlu) % 2 > 0):
                        hexed_dlu = hexed_dlu[1:]

                    if (len(hexed_kat_L) % 2 > 0):
                        hexed_kat_L = hexed_kat_L[1:]

                    if (len(hexed_kat_R) % 2 > 0):
                        hexed_kat_R = hexed_kat_R[1:]

                    if (len(hexed_katDzies_L) % 2 > 0):
                        hexed_katDzies_L = hexed_katDzies_L[1:]

                    if (len(hexed_katDzies_R) % 2 > 0):
                        hexed_katDzies_R = hexed_katDzies_R[1:]

                    if (len(hexed_ilosc) % 2 > 0):
                        hexed_ilosc = hexed_ilosc[1:]

                    if (len(hexed_wys) % 2 > 0):
                        hexed_wys = hexed_wys[1:]

                    hexed_dlu_rev = hexed_dlu[2:] + hexed_dlu[0:2]
                    hexed_kat_L_rev = hexed_kat_L[2:] + hexed_kat_L[0:2]
                    hexed_kat_R_rev = hexed_kat_R[2:] + hexed_kat_R[0:2]
                    hexed_katDzies_L = hexed_katDzies_L[2:] + hexed_katDzies_L[0:2]
                    hexed_katDzies_R = hexed_katDzies_R[2:] + hexed_katDzies_R[0:2]
                    hexed_ilosc_rev = hexed_ilosc[2:] + hexed_ilosc[0:2]
                    hexed_wys_rev = hexed_wys[2:] + hexed_wys[0:2]

                    hexed_dlu_int1 = int(hexed_dlu_rev[2:], 16)
                    hexed_dlu_int2 = int(hexed_dlu_rev[0:2], 16)

                    textCombo = str(self.combo.currentText())
                    if textCombo == "Ruch piły":
                        hexed_kat_L_int1 = int(hexed_kat_L_rev[2:], 16)
                        hexed_kat_R_int1 = int(hexed_kat_R_rev[2:], 16)

                    hexed_katDzies_L_int = int(hexed_katDzies_L[0:2], 16)
                    hexed_katDzies_R_int = int(hexed_katDzies_R[0:2], 16)

                    hexed_kat_L_int2 = int(hexed_kat_L_rev[0:2], 16)
                    hexed_kat_R_int2 = int(hexed_kat_R_rev[0:2], 16)

                    if (hexed_ilosc_rev[2:]) == "":
                        hexed_ilosc_int1 = 0
                    else:
                        hexed_ilosc_int1 = int(hexed_ilosc_rev[2:], 16)

                    hexed_ilosc_int2 = int(hexed_ilosc_rev[0:2], 16)

                    if (hexed_wys_rev[2:]) == "":
                        hexed_wys_int1 = 0
                    else:
                        hexed_wys_int1 = int(hexed_wys_rev[2:], 16)

                    hexed_wys_int2 = int(hexed_wys_rev[0:2], 16)

                    dlu_hex = chr(hexed_dlu_int2) + chr(hexed_dlu_int1)
                    kat_L_hex = chr(hexed_kat_L_int2)
                    if textCombo == "Ruch piły":
                        kat_L_hex += chr(hexed_kat_L_int1)

                    kat_R_hex = chr(hexed_kat_R_int2)
                    if textCombo == "Ruch piły":
                        kat_R_hex += chr(hexed_kat_R_int1)

                    katDzies_L_hex = chr(hexed_katDzies_L_int)
                    katDzies_R_hex = chr(hexed_katDzies_R_int)

                    ilosc_hex = chr(hexed_ilosc_int2) + chr(hexed_ilosc_int1)
                    wys_hex = chr(hexed_wys_int2) + chr(hexed_wys_int1)

                    profil = str(profil.Profil).replace(' ', '')
                    profil = profil.replace('\s', '')

                    file = open(fileName+short+'.CUN', 'a')
                    file.write(profil)
                    offset = len(profil)
                    offsetpath = len(basepath)

                    for i in range(30 - offset):
                        file.write(chr(0))
                    file.close()

                    file = open(fileName+short+'.CUN', 'ab')

                    file.write(bytearray(dlu_hex, 'latin_1'))
                    for i in range(3):
                        file.write(bytearray(chr(0) + chr(0), 'latin_1'))

                    if textCombo == "Ruch głowicy":
                        file.write(bytearray(kat_L_hex + katDzies_L_hex + chr(0), 'latin_1'))
                        file.write(bytearray(chr(0) + chr(0) + chr(0) + kat_R_hex + katDzies_R_hex + chr(0), 'latin_1'))
                        file.write(bytearray(chr(0) + chr(0) + chr(0), 'latin_1'))
                    else:
                        file.write(bytearray(chr(90) + chr(0) + chr(0), 'latin_1'))
                        file.write(bytearray(kat_L_hex + chr(0) + chr(90) + chr(0) + chr(0), 'latin_1'))
                        file.write(bytearray(kat_R_hex + chr(0), 'latin_1'))


                    for i in range(21 - offsetpath):
                        file.write(bytearray(chr(0), 'latin_1'))
                    file.write(bytearray(basepath, 'latin_1'))
                    for i in range(3):
                        file.write(bytearray(chr(0), 'latin_1'))

                    file.write(bytearray(ilosc_hex, 'latin_1'))

                    for i in range(68):
                        file.write(bytearray(chr(0), 'latin_1'))

                    file.close()

                self.textbox.setText('Export ' + os.path.basename(fileName) + ' wykonany pomyślnie')

    def getBarsSQL(self, zlecText):
        import pyodbc

        server = '10.111.40.147'
        database = 'hpl2018'
        username = 'hplpawel'
        password = 'hahaha123'
        driver = '{MySQL ODBC 8.0 Unicode Driver}'  # Driver you need to connect to the database
        port = '3306'
        cnn = pyodbc.connect('DRIVER=' + driver + ';PORT=' + port + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username +
                             ';PWD=' + password)

        DF = pd.read_sql_query("SELECT * FROM " + zlecText, cnn)

        filterProfilOk = [col for col in DF if col.startswith('P')]
        filterDefekt = [col for col in DF if col.startswith('D')]

        DFProfil = DF[filterProfilOk][DF[filterProfilOk] > 0]
        DFWady = DF[filterDefekt][DF[filterDefekt] > 0]

        DFProfil.dropna(axis=1, how='all', inplace=True)
        DFWady.drop(columns='DATE', inplace=True)
        DFWady.dropna(axis=1, how='all', inplace=True)

        return DFProfil, DFWady

    def ncxToCun(self, filepath):
        with open(filepath) as f:
            content = f.read()

        cutsStr = content.split(':CUT')

        arrBars = ncloader.load(content)

        cuts = []
        for bar in arrBars:
            cuts += bar.barCuts

        for cut_ in cuts:
            if cut_.cutProfil.endswith('A') or cut_.cutProfil.endswith('E'):
                cut_.cutProfil = cut_.cutProfil[:-1]
            if len(cut_.cutMacros) > 0 or len(cut_.cutWorks) > 0:
                cut_.cutCNC = 'CNC'
            else:
                cut_.cutCNC = ''

        global dFCutstemp
        dFCutstemp = pd.DataFrame.from_records([cut_.to_dict() for cut_ in cuts])

        cols = ['cutIlosc', 'cutLength', 'cutProfil', 'cutDescription', 'cutAngleL', 'cutAngleR', 'cutCNC', 'cutNumber']
        dFCuts = dFCutstemp[cols]
        dFCuts.columns = ['Ilosc', 'DlugoscCiecia', 'Profil', 'Opis', 'AngleL2', 'AngleR2', 'CNC', 'Numer']

        profilList = dFCuts['Profil'].unique()
        profilList = np.delete(profilList, np.nan)

        #if dfCuts['AngleL2']

        dFCuts['Ilosc'] = dFCuts['Ilosc'].astype(str)
        dFCuts['Ilosc'] = dFCuts['Ilosc'].str.replace('\s', '')
        dFCuts['Ilosc'] = dFCuts['Ilosc'] + '0'

        dFCuts['Wysokosc'] = 0

        dropProfile = ['']

        if self.checkBJM.isChecked():
            dropProfile += ['421113', '422083', '421263', '422223', '421613', '422493', '421703', '422583']
            dropProfile += ['421793', '422703', '421803', '422713', '423223', '422273', '422273']

        dFCuts['Ilosc'] = dFCuts['Ilosc'].astype(int)
        dFCuts['DlugoscCiecia'] = dFCuts['DlugoscCiecia']*10
        dFCuts['DlugoscCiecia'] = dFCuts['DlugoscCiecia'].astype(int)
        dFCuts['Ilosc'] = dFCuts['Ilosc'].astype(str)
        dFCuts['DlugoscCiecia'] = dFCuts['DlugoscCiecia'].astype(str)
        dFCuts_filtered = dFCuts[~dFCuts['Profil'].isin(dropProfile)]
        dFCuts_filtered.loc[dFCuts_filtered['AngleL2'] == 135.0, 'AngleL2'] = 45.0
        dFCuts_filtered.loc[dFCuts_filtered['AngleR2'] == 135.0, 'AngleR2'] = 45.0
        if len(self.textScratch.text()) > 0:
            optimize = self.optimizeScratch(dFCuts_filtered, 25, filepath)
            return optimize
        else:
            return dFCuts_filtered

    def optimizeScratch(self, dataFrame, zapasTolerancji, filepath):
        cuts = dataFrame.reset_index()
        profil = dataFrame['Profil'].iloc[0]
        rest, wady = self.getBarsSQL(self.textScratch.text())
        rest = list(rest.values)
        wady = list(wady.values)

        elements = []
        cut_idx = 0

        with open(filepath) as f:
            content = f.read()
        barStr = list(content.split(':BAR'))
        cutsStr = list(content.split(':CUT'))
        optimCuts = pd.DataFrame(columns=['index', 'Ilosc', 'DlugoscCiecia', 'Profil', 'AngleL2', 'AngleR2', 'CNC', 'Opis', 'Numer', 'indexLocal'])

        for _ in range(len(barStr)-len(rest)):
            rest.append(np.array([6600]))

        for j in range(len(rest)):
            elements.append([])
            for i in range(len(rest[j])):
                elements[j].append([])
                for idx, c in cuts.iterrows():
                    cCut = int(c['DlugoscCiecia'])/10
                    if cCut < rest[j][i] - zapasTolerancji:
                        removed = False
                        rest[j][i] -= cCut
                        elements[j][i].append(cCut)
                        item = cuts.loc[idx]
                        item['indexLocal'] = 10*j+i
                        optimCuts.loc[optimCuts.shape[0]] = item
                        with open(self.textScratch.text() + 'optim.NCX', 'w', encoding='utf-8') as outfile:
                            for cut in cutsStr:
                                if str(cCut) in cut and removed is False:
                                    cutsStr.remove(cut)
                                    removed = True
                                else:
                                    outfile.write(':CUT')
                                    outfile.write(cut)
                        cuts.drop(index=idx, axis=0, inplace=True)

        optimCuts.sort_values(by=['indexLocal'])
        global dFCutstemp
        dFCutstemp = copy.copy(optimCuts)
        dFCutstemp.Ilosc = dFCutstemp.Ilosc.str[:-1]
        dFCutstemp.DlugoscCiecia = dFCutstemp.DlugoscCiecia.str[:-1]

        optimCuts['Wysokosc'] = 0
        optimCuts.drop(['index', 'indexLocal', 'CNC', 'Opis', 'Numer'], axis=1, inplace=True)
        self.printBar(filepath, elements, rest, wady, profil)
        return optimCuts

    def printBar(self, filepath_, elements_, rest_, wady_, profil_):
        import math
        short_ = str(profil_)[-4:]
        sum = 0
        sum_prof = 0
        splitFilepath = filepath_.split('/')
        with open('Z:\\emmegifdd\\ETX'+splitFilepath[-1][:-4]+short_+'_r.txt', 'w', encoding='utf-8') as outfile:
            for i in range(len(elements_)):
                sum_prof = 0
                outfile.write('Belka nr: ' + str(i + 1)+'\n')
                for j in range(len(elements_[i])):
                    sum = 0
                    for k in range(len(elements_[i][j])):
                        sum += elements_[i][j][k]
                        sum_prof += elements_[i][j][k]  # Mierzenie długości profila (6600)
                        outfile.write('prof: ' + str(elements_[i][j][k])+'\n')
                    if (math.isnan(rest_[i][j])) == False:
                        wada = 0
                        sum_prof += rest_[i][j]  # Mierzenie długości profila (6600)
                        try:
                            if (math.isnan(wady_[i][j])) == False:
                                wada += (wady_[i][j])
                                sum_prof += wada  # Mierzenie długości profila (6600)
                        except:
                            wada = 0
                        outfile.write('def: ' + str('%.1f' % (rest_[i][j] + wada))+'\n')
                outfile.write(str(sum_prof)+'\n')
                outfile.write(''+'\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

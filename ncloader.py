import re
import math

def load(content):
    class Bar(object):
        barNumber = 0
        barLength = 0.0
        barProfil = ''
        barHeight = 0.0
        barWidth = 0.0
        barCuts = []

        def __init__(self, number):
            self.barNumber = number
            self.barCuts = []

    class Cut(object):
        cutLength = 0
        cutAngleL = 0.0
        cutAngleR = 0.0
        cutNumber = 0
        cutProfil = ''
        cutDescription = ''
        cutMacros = []
        cutWorks = []

        def __init__(self, length):
            self.cutLength = length
            self.cutDescription = ''
            self.cutWorks = []
            self.cutMacros = []

        def to_dict(self):
            return {
                'cutDescription': self.cutDescription,
                'cutIlosc': 1,
                'cutProfil': self.cutProfil,
                'cutNumber': self.cutNumber,
                'cutLength': self.cutLength,
                'cutAngleL': self.cutAngleL,
                'cutAngleR': self.cutAngleR,
                'cutCNC': self.cutCNC
            }

    class Macro(object):
        Ident = ''
        Comment = ''
        Description = ''
        WX = 0.0
        Obrot = 0.0
        Type = ''
        Width = 0
        Height = 0
        PosY = 0
        Approach = 0
        End = 0
        Frez = 0

        def __init__(self, ident):
            self.Ident = ident
            self.Frez = 0

    class Work(object):
        workComment = ''
        workType = ''
        workWX = 0.0
        workWY = 0.0
        workSide = 0
        workHeight = 0.0
        workDepth = 0.0

        def __init__(self, comment):
            self.workComment = comment

    bars = content.split(':BAR')
    ilosc_ciec = 0
    ilosc_obr = 0
    ilosc_obrCiec = 0
    idx = 0
    arrBars = [Bar(0)]

    for x in bars:
        # arrCuts.append('')
        sub_idx = 0
        macro_idx = 0
        work_idx = 0

        for y in x.split('\n'):
            if y.startswith('BNo'):
                bNum = re.search(r'= (\d*)', y, flags=0).group(1)
                arrBars.append(Bar(bNum))

            if y.startswith('BLength'):
                arrBars[idx].barLength = re.search(r'= (\d*.\d*)', y, flags=0).group(1)

            if y.startswith('BIdentNo'):
                arrBars[idx].barProfil = re.search(r'= "(.*)"', y, flags=0).group(1)

            if y.startswith('BHeight'):
                arrBars[idx].barHeight = re.search(r'= (\d*.\d*)', y, flags=0).group(1)

            if y.startswith('BWidth'):
                arrBars[idx].barWidth = re.search(r'= (\d*.\d*)', y, flags=0).group(1)

            if y.startswith('CLength'):
                tempLen = float(re.search(r'= (\d*.\d*)', y, flags=0).group(1))
                arrBars[idx].barCuts.append(Cut(tempLen))
                ilosc_ciec += 1
                macro_idx = 0
                sub_idx += 1

            if y.startswith('CDescription'):
                arrBars[idx].barCuts[sub_idx - 1].cutDescription = re.search(r'= "(.*)"', y, flags=0).group(1)
                arrBars[idx].barCuts[sub_idx - 1].cutProfil = arrBars[idx].barProfil
                arrBars[idx].barCuts[sub_idx - 1].cutMacros = []

            if y.startswith('CAngleLH'):
                arrBars[idx].barCuts[sub_idx - 1].cutAngleL = float(re.search(r'= (\d*.\d*)', y, flags=0).group(1))

            if y.startswith('CAngleRH'):
                arrBars[idx].barCuts[sub_idx - 1].cutAngleR= float(re.search(r'= (\d*.\d*)', y, flags=0).group(1))

            if y.startswith('CPartNo'):
                arrBars[idx].barCuts[sub_idx - 1].cutNumber = re.search(r'= (\d*)', y, flags=0).group(1)

            if y.startswith('WMacroIdent'):
                arrBars[idx].barCuts[sub_idx - 1].cutMacros.append(Macro(re.search(r'= "(.*)"', y, flags=0).group(1)))
                macro_idx += 1
                work_idx = 0

            if y.startswith('WComment') and macro_ident.startswith(':WMacroIdent'):
                if macro_idx > 0:
                    arrBars[idx].barCuts[sub_idx - 1].cutMacros[macro_idx - 1].Comment = (
                        re.search(r'= "(.*)"', y, flags=0).group(1))

            if y.startswith('WX1') and macro_ident.startswith('WParent'):
                if macro_idx > 0:
                    if '-' in y:
                        arrBars[idx].barCuts[sub_idx - 1].cutMacros[macro_idx - 1].WX = float(
                            (re.search(r'= (-\d*.\d*)', y, flags=0).group(1)))
                    else:
                        arrBars[idx].barCuts[sub_idx - 1].cutMacros[macro_idx - 1].WX = float(
                            (re.search(r'= (\d*.\d*)', y, flags=0).group(1)))



            # if y.startswith(':WORK'):
            # print(macro_ident)

            macro_ident = y
        idx += 1

    return arrBars


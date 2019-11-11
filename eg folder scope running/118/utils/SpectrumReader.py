# -*- coding: utf-8 -*-
"""
@author:
Ilia Kudarenko
Rinat Ismagilov
"""

import numpy as np
import re, time

class SpectrumReader:
    def read_swan_band(self, file_name='SWAN_band'):
        """
            Reads swan_spectrum from file file_name
            @param file_name: file name with spectrum data at the same path (default 'SWAN_band')

            @return np.array (x, y) : x - array of wavelength in A, y - array of intensity in Arb. Units
        """

        with open(file_name, 'r') as f:
            strlist = f.readlines()
        # 4 lines in file are additional parameters
        t_rot = float(re.sub(r'[^=]+=\s*(\S+)\s*', r'\1', strlist[0]))
        t_vib = float(re.sub(r'[^=]+=\s*(\S+)\s*', r'\1', strlist[1]))
        i_max = float(re.sub(r'[^=]+=\s*(\S+)\s*', r'\1', strlist[2]))
        n0 = float(re.sub(r'[^=]+=\s*(\S+)\s*', r'\1', strlist[3]))
        x = []
        y = []
        for s in strlist[4:]:
            l, i = [float(x) for x in s.split()]
            x.append(l)
            y.append(i)
        x, y = np.array(x), np.array(y)
        return x, y

    def read_exp_spectrum(self, file_name='exp.txt'):

        """
            Reads experimental spectrum. Default is Kudarenko's file 'exp.txt'
            @param file_name: file name with spectrum data at the same path (default 'exp.txt')

            @return np.array (x, y) : where x - array of wavelength in A, y - array of intensity in Arb. Units
        """

        # загрузка экспериментальных данных
        with open(file_name, 'r') as f:
            strlist = f.readlines()
        exp_x = []
        exp_y = []
        for s in strlist:
            l, i = [float(x) for x in s.split()]
            exp_x.append(l)
            exp_y.append(i)
        exp_x, exp_y = np.array(exp_x), np.array(exp_y)
        return exp_x, exp_y


if __name__ == '__main__':
    start_time = time.time()
    spectrum_reader = SpectrumReader()
    print("--- %s seconds ---" % (time.time() - start_time))

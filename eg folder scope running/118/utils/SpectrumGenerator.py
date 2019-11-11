# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 23:27:00 2018
Modified 29.06.2018

@author:
Ilia Kudarenko
Rinat Ismagilov
"""

import time
import os
from os import system
from PyAutoItPy import AutoItX, WinHandle
import matplotlib.pyplot as plt
import numpy as np


class ModelSpectrumGenerator:
    """
        Class for executing exe-program. This exe-program (m.b. written by using FORTRAN language)
        runs in DOS-window; based on input parameters generates OES spectrum.
        For example "SWAN_BAND.exe" generates OES spectrum for C2 at the same directory with name "SWAN_band" (without any extension).
        TODO: Realize for other exe-programs
    """

    def __init__(self, file_name='SWAN_BAND.exe'):
        """
            Constructor
            @param file_name: ".exe" file name at the same path (default 'SWAN_BAND.exe')
            @return: no return value
        """
        self.file_name = file_name

    def swan_spectrum(self, t_rot, t_vib, zero = 0, v_upper = 0, delta_v = 0, h_bet = 0, full_width = 15, max_amp = 1):
        """
            Execute "*.exe" file for generating swan spectrum
            @param v_upper: quantum number of upper vibrational state of C2 (default 0)
            @param delta_v: difference between v_upper and lower state (default 0)
            @param t_rot: rotational temperature in K
            @param t_vib: vibrational temperature in K
            @param h_bet: hydrogen line amplitude in A
            @param full_width: FWHM of the hydrogen line in A(apparatus function - spectrometer)
            @param max_amp: maximum amplitude of modeled C2 line in A
            @param zero: chosen ground "zero" value of modeled spectrum(default 0)

            @return: no return value
        """

        # Chunk from Kudarenko
        # запуск программы для получения спектра по заданным параметрам

        #	start_time = time.time()
        #	print('******', t_vib)
        CallRes = system('start ' + self.file_name)
        # Если проблемы, выходим.
        if CallRes != 0:
            print('It is not possible to start notebook!')
            exit(CallRes)
        Automat = AutoItX()
        # Это заголовок для поиска окна в формате AutoIt
        Title = '[CLASS:SWAN_BANDFRAME]'
        ##Это идентификатор контрола в формате AutoIt
        Control = '[CLASS:SWAN_BANDGraphic; INSTANCE:1]'
        ##Ну и пока пустой Handle
        Handle = None
        ##Ждем появления окна, вдруг еще не открылось
        Opened = Automat.WinWait(Title, 5)
        ##Выходим, если не дождались открытия блокнота.
        if not Opened:
            print('Something wrong...')
            exit(-1)
        # Если открылось - получаем Handle, чтобы работать с конкретно данным окном.
        Handle = WinHandle(Automat.WinGetHandle(Title))
        # Выходим, если не удалось получить Handle окна.
        if not Handle:
            print('It is not possible to get - Handle!')
            exit(-1)
        # Активируем окно, иначе некоторые функции могут не сработать
        Automat.WinActivate(Handle)
        # Уж совсем на всякий случай перемещаем фокус ввода в нужный контрол.
        Automat.ControlFocus(Handle, Control)
        Automat.Send('%d %d{ENTER}' % (v_upper, delta_v))
        Automat.Send('%f %f{ENTER}' % (t_rot, t_vib))
        # При v_upper = delta_v = 0 спрашивает h_bet
        if (v_upper == delta_v) and (delta_v == 0):
            Automat.Send(str(h_bet) + '{ENTER}')
        Automat.Send(str(full_width) + '{ENTER}')
        Automat.Send(str(max_amp) + '{ENTER}')
        Automat.Send(str(zero) + '{ENTER}')

        CloseWindow = Automat.WinWaitActive('[CLASS:#32770]', 5)
        if not CloseWindow:
            print('Not closing!')
            exit(-1)
        Automat.Send('{TAB}{ENTER}')


    def rename_spectrum_file(self, new_name, old_name='SWAN_band', directory ='modeled spectra'):
        """
             Renames file with swan spectrum and place it for a particular directory.
             @param new_name: new name for file
             @param old_name: target file-name which will be renamed (default 'SWAN_band')
             @param directory: directory name where renamed file will be placed (default 'modeled spectra')

             @return: no return value
        """

        if not os.path.exists(directory):
            os.makedirs(directory)
        os.rename(old_name, directory+"/"+new_name)


if __name__ == '__main__':
    start_time = time.time()
    spectrum_reader = SpectrumReader2()
    spectrum_runner = ModelSpectrumGenerator()

    # ----------------- OES EXPERIMENT ------------------------
    exp_x, exp_y = spectrum_reader.read_exp_spectrum()
    # калибровка спектра по максимуму С2
    exp_x = (np.array(exp_x)) * 10 - 4.9

    # TODO: !плохо вычитает прямую!... реальный нуль получается ниже!

    # # вычетание прямой (желательно реализовать между двумя локальными минимуми в правой и левой половинах спектра, чтобы не уходило в минус)
    # left_min_indx = np.argmin(exp_y[0:int(len(exp_y)/2)])
    # right_min_indx = np.argmin(exp_y[int(len(exp_y)/2):])
    # print(exp_y[left_min_indx],exp_y[right_min_indx])
    # exp_y = np.array(exp_y) - np.amin(exp_y)
    # exp_y = np.array(exp_y) - exp_y[left_min_indx] - ((exp_y[right_min_indx] - exp_y[left_min_indx]) / (exp_x[right_min_indx] - exp_x[left_min_indx])) * (exp_x - exp_x[left_min_indx])
    #

    exp_y = np.array(exp_y) - exp_y[0] - (exp_y[-1] - exp_y[0]) / (exp_x[-1] - exp_x[0]) * (exp_x - exp_x[0])

    # нормировка на максимум С2
    exp_y = exp_y / np.amax(exp_y[13:])

    plt.plot(exp_x[13:], exp_y[13:], '-o')

    # ----------------- end OES EXPERIMENT ------------------------


    # 1 чтение файла Swan_band
    xX, yY = spectrum_reader.read_swan_band()
    plt.plot(xX, yY, '-o')

    spectrum_runner.rename_spectrum_file(time.strftime("%Y-%m-%d %Hh%Mm%S", time.gmtime(time.time())) + ".txt")
    print("--- %s seconds ---" % (time.time() - start_time))

    spectrum_runner.swan_spectrum(1500,3000)

    # 2 чтение файла Swan_band
    xX1, yY1 = spectrum_reader.read_swan_band()
    plt.plot(xX1, yY1, '-*')

    plt.ylim([-0.2, 1.1])
    print("--- %s seconds ---" % (time.time() - start_time))
    plt.show()

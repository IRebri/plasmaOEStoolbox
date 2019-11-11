# -*- coding: utf-8 -*-
"""
Created on Fri 13.07.2018

@author:
Rinat Ismagilov
"""

import numpy as np
from utils import SpectrumGenerator, SpectrumModifier, SpectrumReader
from utils.pyOESconsts import Consts
from utils import SpectrumGenerator


class SwanSpectrumStandardizator:
    """
        Class responsible for standardization of experimental or theoretically generated spectrum.
        It wraps all functions similarly to "workflow_starter.py"

    """
    def __init__(self, exp_dir = "spectra", theor_dir = "modeled spectra"):
        """
            Constructor
            @param string exp_dir: folder path, where experimental OES data are stored (default 'spectra')
            @param string theor_dir: folder path, where theoretically calculated OES data are stored (default 'modeled spectra')

            @return: no return value
        """
        self.exp_dir = exp_dir
        self.theor_dir = theor_dir
        self.reader = SpectrumReader.SpectrumReader()
        self.modifier = SpectrumModifier.SpectrumModifier()

    def get_spectrum(self, file, is_theor_spectrum = True):
        """
            Reads swan_spectrum from file file_name in corresponding folder which chosen by is_theor_spectrum flag
            @param string file: name of the file with spectrum data at some folder (e.g. 'UEFx30y20.txt', "Trot1500Tvib3000Default.txt")
            @param Boolean is_theor_spectrum: flag used to shoose modification route

            @return np.array (x, y) : standard x - array of wavelength in A, y - array of intensity in Arb. Units (for now implemented 50x50 points)
        """
        if is_theor_spectrum:

            x_theor, y_theor = self.reader.read_swan_band(file_name = self.theor_dir + "/" + file)

            # 1 masking - working only with Swan Band (0,0). Exe file generates spectra only until 5200.8A
            mask_theor = (x_theor > 5033.) & (x_theor < 5200.5)
            x_theor_mask, y_theor_mask = np.copy(x_theor[mask_theor]), np.copy(y_theor[mask_theor])

            # 2 deTrending - substract the line
            # No need

            # 3 standardizing - make x grid similar to all spectra (includes interpolation to increase/decrease the number of X,Y points)
            x_theor_std, y_theor_std = self.modifier.make_standard_xgrid_spectrum(x_theor_mask, y_theor_mask)

            # 4 translation maximum - align to theoretical  5165.2A
            y_theor_shiftedC2 = self.modifier.translate_OY_along_x_to_merge_lines(x_theor_std, y_theor_std,
                                                                             expected_max=5165.2, max_region=200.,
                                                                             line=Consts.C2_SWAN_BAND[
                                                                                 'vibr trans (0,0)'])

            # 5 normilize - devide by max C2 intensity
            y_theor_new = self.modifier.normalize_by_division_with_max_intensity(x_theor_std, y_theor_shiftedC2)

            x, y = x_theor_std, y_theor_new

        else:
            x_exp, y_exp = self.reader.read_exp_spectrum(file_name = self.exp_dir + "/" + file)

            # transform wavelength: nm --> A
            x_exp, y_exp = x_exp * 10, y_exp * 10

            # 1 masking - working only with Swan Band (0,0)
            mask = (x_exp > 5033.) & (x_exp < 5220.)
            # right boundary is a little bit bigger than for theoretical, because there might be huge shifts. Anyway it will be implicitly cut during standardization step; Left boundary empirically optimized
            x_exp_mask, y_exp_mask = np.copy(x_exp[mask]), np.copy(y_exp[mask])

            # 2 deTrending - substract the line
            y_detrend = self.modifier.detrend_by_line_from_2left_right_minpoints(x_exp_mask, y_exp_mask)

            # 3 standardizing - make x grid similar to all spectra (includes interpolation to increase/decrease the number of X,Y points)
            x_std, y_std = self.modifier.make_standard_xgrid_spectrum(x_exp_mask, y_detrend)

            # 4 translation maximum - align to theoretical  5165.2A
            y_shiftedC2 = self.modifier.translate_OY_along_x_to_merge_lines(x_std, y_std, expected_max=5165.2,
                                                                       max_region=200.,
                                                                       line=Consts.C2_SWAN_BAND['vibr trans (0,0)'])

            # 5 normilize - devide by max C2 intensity
            y_exp_new = self.modifier.normalize_by_division_with_max_intensity(x_std, y_shiftedC2)

            x, y = x_std, y_exp_new

        return x, y

    def get_std_xy(self, x_exp, y_exp):
        """
            Preprocessed Intensity row
            @param x_exp: (np.array) spectrum y coordinate - experimental wavelength (in A)
            @param y_exp: (np.array) spectrum y coordinate - experimental intensity

            @return np.array (x, y) : standard x - array of wavelength in A, y - array of intensity in Arb. Units (for now implemented 50x50 points)
        """

        # transform wavelength: nm --> A
        x_exp, y_exp = x_exp * 10, y_exp * 10

        # 1 masking - working only with Swan Band (0,0)
        mask = (x_exp > 5033.) & (x_exp < 5220.)
        # right boundary is a little bit bigger than for theoretical, because there might be huge shifts. Anyway it will be implicitly cut during standardization step; Left boundary empirically optimized
        x_exp_mask, y_exp_mask = np.copy(x_exp[mask]), np.copy(y_exp[mask])

        # 2 deTrending - substract the line
        y_detrend = self.modifier.detrend_by_line_from_2left_right_minpoints(x_exp_mask, y_exp_mask)

        # 3 standardizing - make x grid similar to all spectra (includes interpolation to increase/decrease the number of X,Y points)
        x_std, y_std = self.modifier.make_standard_xgrid_spectrum(x_exp_mask, y_detrend)

        # 4 translation maximum - align to theoretical  5165.2A
        y_shiftedC2 = self.modifier.translate_OY_along_x_to_merge_lines(x_std, y_std, expected_max=5165.2,
                                                                        max_region=200.,
                                                                        line=Consts.C2_SWAN_BAND['vibr trans (0,0)'])

        # 5 normilize - devide by max C2 intensity
        y_exp_new = self.modifier.normalize_by_division_with_max_intensity(x_std, y_shiftedC2)

        return x_std, y_exp_new





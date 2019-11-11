# -*- coding: utf-8 -*-
"""

@author:
Rinat Ismagilov

"""

import time
import numpy as np
from scipy.ndimage.interpolation import shift
from scipy import interpolate
from utils.pyOESconsts import Consts


class SpectrumModifier:
    def translate_OY_along_x_to_merge_lines(self, spectra_x, spectra_y, expected_max, max_region, line = Consts.H_BETTA_ANG['486nm 4to2 Aqua 2.55eV']):
        """"
           Analyzes the spectrum (spectra_x, spectra_y) with expected peak at expected_max wavelength(A). Search that peak not far from expected_max in
           region (expected_max - max_region/2; expected_max + max_region/2;). After that translates given spectrum (spectra_x, spectra_y) OY along OX to fit found maximum with given line.

           @param spectra_x: x-coordinate, wavelength in A (np.array) of spectrum
           @param spectra_y: y-coordinate, intensity in a.u. (np.array) of spectrum
           @param expected_max: x-coordinate in A of expected peak which will be at the same place as given line
           @param max_region: region boundary (x-coordinate in A) for searching expected peak (expected_max - max_region/2; expected_max + max_region/2;)
           @param line: x-coordinate in A where expected peak should be (fit to given line)

           @return: y - np.array of intensity in arb. units, shifted spectra_y along x for some deltaX in order to merge expected_max with given theoretical line
        """
        mask = (spectra_x > (expected_max - (max_region/2.))) & (spectra_x < (expected_max + (max_region/2.)))
        x_mask = np.copy(spectra_x[mask])
        y_mask = np.copy(spectra_y[mask])
        x_max = x_mask[np.argmax(y_mask)]
        x_shift = line - x_max
        if abs(x_shift) > (x_mask[1]-x_mask[0])/2:
            arg_shift = int(round(x_shift/(x_mask[1]-x_mask[0])))
            # print(str(arg_shift))
            y_shifted = shift(spectra_y, arg_shift, cval=np.NaN)
            # y_shifted = shift(spectra_y, (arg_shift - ((np.sign(arg_shift) + 1) / 2)), cval=np.NaN)
            # ((np.sign(arg_shift)+1)/2)  - костыль, т.к. при смещении справа плохо работает
        else:
            y_shifted = spectra_y
        return y_shifted
               # numpy.logical_not(numpy.isnan(x))

    def detrend_by_line_from_2left_right_minpoints(self, x, y):
        """"
           Analyzes the spectrum (x, y) with some linear trend. Subtraction line constructed by connecting 2 points (A and B) from left and right side of x interval.
           These points are local minimums of y, i.e. y(A)<=y(for any x from left half of {x}) and y(B)=>y(for any x from right half of {x})

           @param x: np.array, x-coordinate (wavelength in A) of spectrum
           @param y: np.array, y-coordinate (intensity in arb.units) of spectrum

           @return: y_detrended - np.array, new filtered/detrended spectrum to the same x
        """
        mid_indx = int(len(y) / 2)
        left_min_indx = np.argmin(y[0:mid_indx])
        right_min_indx = np.argmin(y[mid_indx + 1:]) + mid_indx + 1
        y_detrended = y - np.amin(y)
        y_detrended = y_detrended - y_detrended[left_min_indx] - ((y_detrended[right_min_indx] - y_detrended[left_min_indx]) / (
                x[right_min_indx] - x[left_min_indx])) * (x - x[left_min_indx])
        return y_detrended

    def normalize_by_division_with_max_intensity(self, x, y, max_region = 100., expected_max = Consts.C2_SWAN_BAND['vibr trans (0,0)']):
        """"
           Analyzes the spectrum (x, y). Method is searching expected peak at expected_max point (wavelength, A) not far from it in
           region (expected_max - max_region/2; expected_max + max_region/2;). Finally, it divides all spectrum given Y(x) by found Ymax(Xmax) and returned y_div

           @param spectra_x: x-coordinate, wavelength in A (np.array) of spectrum
           @param spectra_y: y-coordinate, intensity in a.u. (np.array) of spectrum
           @param max_region: region boundary (x-coordinate in A) for searching expected peak (expected_max - max_region/2; expected_max + max_region/2;)
           @param expected_max: x-coordinate in A of expected peak (as Default - Consts.C2_SWAN_BAND['vibr trans (0,0)'] = 5165.2A)

           @return: y_div - np.array of intensity in arb. units, normalized (devided) by specified local peak
        """
        mask = (x > (expected_max - (max_region / 2.))) & (x < (expected_max + (max_region / 2.)))
        y_div = y/np.amax(y[mask])
        return y_div

    def make_standard_xgrid_spectrum(self, x, y, start = 5036., stop = 5200., num = 50, endpoint = True):
        """"
           Analyzes, interpolates the spectrum (x, y) by scipy.interpolate.interp1 ('cubic').
           Returns x_new and y_new in standardized xgrid with num points (equidistant from start to stop)

           @param x: x-coordinate, wavelength in A (np.array) of spectrum
           @param y: y-coordinate, intensity in a.u. (np.array) of spectrum
           @param start: the starting x-value of the interval. Should be inside x-range (default is 5036)
           @param stop: the end x-value of the interval. Should be inside x-range (default is 5210)

           @return: x_new, y_new - (tuple of two np.arrays) new interpolated STANDARDized spectrum
        """

        # f = interpolate.interp1d(x, y, kind='cubic')
        tck = interpolate.splrep(x, y, s=0) # https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        x_new = np.linspace(start, stop, num, endpoint)
        y_new = interpolate.splev(x_new, tck, der=0)
        # y_new = f(x_new)
        return x_new, y_new

if __name__ == '__main__':
    start_time = time.time()
    spectrum_reader = SpectrumReader()
    print("--- %s seconds ---" % (time.time() - start_time))
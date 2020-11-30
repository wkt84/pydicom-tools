import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import RegularGridInterpolator as rgi

import pydicom


class Dose:
    def __init__(self, path):
        self._ds = pydicom.dcmread(path)
        # Modalityチェック
        if self._ds.Modality != 'RTDOSE':
            raise TypeError('This file is not DICOM RT Dose.')
        self._analyze_dicom(self._ds)

    def _analyze_dicom(self, ds):
        self.shape = ds.pixel_array.shape
        self.dose = ds.pixel_array * ds.DoseGridScaling
        self._origin = list(map(float, ds.ImagePositionPatient))
        self.x_array = np.linspace(
            self._origin[0], self._origin[0] +
            (int(ds.Columns) - 1) * float(ds.PixelSpacing[1]), int(ds.Columns))
        self.y_array = np.linspace(
            self._origin[1],
            self._origin[1] + (int(ds.Rows) - 1) * float(ds.PixelSpacing[0]),
            int(ds.Rows))
        self.z_array = np.array(ds.GridFrameOffsetVector) + self._origin[2]

    def get_2d_plane(self, v, axis):
        if axis == 'axial':
            f = interp1d(self.z_array,
                         self.dose,
                         axis=0,
                         bounds_error=False,
                         fill_value=0.)
            return f(v)
        elif axis == 'coronal':
            f = interp1d(self.y_array,
                         self.dose,
                         axis=1,
                         bounds_error=False,
                         fill_value=0.)
            return f(v)
        elif axis == 'sagittal':
            f = interp1d(self.x_array,
                         self.dose,
                         axis=2,
                         bounds_error=False,
                         fill_value=0.)
            return f(v)
        else:
            raise ValueError('No axis.')

    def get_point_dose(self, v):
        data_grid = [self.x_array, self.y_array, self.z_array]
        f = rgi(data_grid,
                self.dose.transpose(),
                bounds_error=False,
                fill_value=0)
        return f(v)

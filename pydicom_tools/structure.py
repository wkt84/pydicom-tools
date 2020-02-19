import random
import numpy as np
from matplotlib.path import Path
import pydicom


class RTSS:
    """
    RT Structure Setを扱うためのクラス

    rtss = RTSS(path_to_rtss)

    でRTSS読み込み
    """
    def __init__(self, path):
        self._rtss = pydicom.dcmread(path)

        # Modalityチェック
        if self._rtss.Modality != 'RTSTRUCT':
            raise TypeError('This file is not DICOM RT StructureSet.')

        self.structures = {}
        for roi in self._rtss.StructureSetROISequence:
            self.structures[roi.ROINumber] = roi.ROIName

        self.points = self._get_points()
        self.paths = self._get_paths()
        self.colors = self._get_colors()

    def _get_points(self):
        _points_dict = {}

        for contour in self._rtss.ROIContourSequence:
            _structure = self.structures[contour.ReferencedROINumber]
            _points = {}
            # Emptyか確認
            if not hasattr(contour, 'ContourSequence'):
                _points_dict[_structure] = None
                continue
            for c in contour.ContourSequence:
                if c.ContourGeometricType != 'CLOSED_PLANAR':
                    continue
                _contour_data = c.ContourData
                _x = [float(x) for x in _contour_data[::3]]
                _y = [float(y) for y in _contour_data[1::3]]
                _z = float(_contour_data[2])
                _xy = list(zip(_x, _y))
                _xy.append(_xy[0])

                if _z not in _points:
                    _points[_z] = []
                _points[_z].append(_xy)

            _points_dict[_structure] = _points

        return _points_dict

    def _get_paths(self):
        _paths_dict = {}
        for contour in self._rtss.ROIContourSequence:
            _structure = self.structures[contour.ReferencedROINumber]
            _points = self.points[_structure]
            _paths = {}

            # Emptyか確認
            if _points is None:
                _paths_dict[_structure] = None
                continue

            for z, p in _points.items():
                if len(p) > 1:
                    for i, c in enumerate(p):
                        _codes = np.ones(len(c)) * Path.LINETO
                        _codes[0] = Path.MOVETO  # 輪郭点のはじめはMOVETO
                        _codes[-1] = Path.CLOSEPOLY  # 輪郭点の終わりはCLOSEPOLY
                        if i == 0:  # 最初の輪郭
                            _all_paths = c
                            _all_codes = _codes
                        else:  # 2つ目以降の輪郭を合体
                            _all_paths = np.concatenate((_all_paths, c))
                            _all_codes = np.concatenate((_all_codes, _codes))
                else:  # 同じz座標に輪郭が1つの場合
                    _all_paths = p[0]
                    _all_codes = np.ones(len(p[0])) * Path.LINETO
                    _all_codes[0] = Path.MOVETO
                    _all_codes[-1] = Path.CLOSEPOLY
                _paths[z] = Path(_all_paths, _all_codes)
            _paths_dict[_structure] = _paths

        return _paths_dict

    def _get_colors(self):
        _colors = {}
        for contour in self._rtss.ROIContourSequence:
            _structure = self.structures[contour.ReferencedROINumber]
            if hasattr(contour, 'ROIDisplayColor'):
                _color = [
                    float(contour.ROIDisplayColor[0]) / 255.,
                    float(contour.ROIDisplayColor[1]) / 255.,
                    float(contour.ROIDisplayColor[2]) / 255., 0.2
                ]
            else:
                _color = [
                    random.random() / 255.,
                    random.random() / 255.,
                    random.random() / 255., 0.2
                ]
            _colors[_structure] = _color

        return _colors

    def calc_volume(self, structure_name):
        """
        structure_name : str
        """
        if structure_name not in self.structures.values():
            raise ValueError(f"{structure_name} was not found.")

        _points = self.points[structure_name]

        if _points is None:
            raise ValueError(f"{structure_name} is empty.")

        _thickness = self._calc_thickness(_points)

        _s = 0

        for pts in _points.values():
            for p in pts:
                for i in range(len(p) - 1):
                    _s += (p[i][0] * p[i + 1][1] - p[i + 1][0] * p[i][1]) / 2.

        _v = _s * _thickness / 1000.

        return _v

    def _calc_thickness(self, _points):
        _z_list = [z for z in _points.keys()]
        _z_diff = np.diff(sorted(_z_list))

        return _z_diff.min()

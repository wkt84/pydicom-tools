import os
import numpy as np

import pydicom


class CTImage:
    """
    CTを扱うためのクラス

    ct = CTImage()
    ct.load(path)

    でpathに存在するCTシリーズを読み込み
    """
    def __init__(self):
        """コンストラクタ"""
        self.is_loaded = False

    def load(self, path):
        """pathを指定して、CTの情報を取得"""
        if self._has_one_series(path):
            _dcm_files = self._select_cts(path)
            _ref_ct = None
            self.number_of_slices = len(_dcm_files)
            i = 0
            for dcm_file, position in sorted(_dcm_files.items(),
                                             key=lambda x: -x[1]):
                if _ref_ct is None:
                    _ref_ct = pydicom.dcmread(os.path.join(path, dcm_file))
                    self.rows = int(_ref_ct.Rows)
                    self.columns = int(_ref_ct.Columns)
                    self.volume = np.zeros(
                        (self.number_of_slices, self.rows, self.columns))
                    self.position = _ref_ct.ImagePositionPatient
                    self.pixel_spacing = _ref_ct.PixelSpacing
                    self.for_uid = _ref_ct.FrameOfReferenceUID
                    self.thickness = float(_ref_ct.SliceThickness)
                dcm_data = pydicom.dcmread(os.path.join(path, dcm_file))
                hu_value = dcm_data.pixel_array * dcm_data.RescaleSlope + \
                    dcm_data.RescaleIntercept
                self.volume[i, :, :] = hu_value
                i += 1
            self.x_min = float(self.position[0])
            self.x_max = self.x_min + \
                (self.columns - 1) * float(self.pixel_spacing[1])
            self.x_array = np.linspace(self.x_min,
                                       self.x_max,
                                       num=self.columns)
            self.y_min = float(self.position[1])
            self.y_max = self.y_min + \
                (self.rows - 1) * float(self.pixel_spacing[0])
            self.y_array = np.linspace(self.y_min, self.y_max, num=self.rows)
            self.z_min = min(_dcm_files.values())
            self.z_max = max(_dcm_files.values())
            self.z_array = np.linspace(self.z_max,
                                       self.z_min,
                                       num=self.number_of_slices)
            self.is_loaded = True
        else:
            return "There are no CT seriese or more than 2 CT seriese."

    def _select_cts(self, path):
        """指定されたディレクトリから、DICOM CTとそのスライス位置を抽出"""
        if self._has_one_series(path):
            _dcm_files = {}
            for file_path in os.listdir(path):
                if os.path.isdir(os.path.join(path, file_path)):
                    continue
                if pydicom.misc.is_dicom(os.path.join(path, file_path)):
                    dcm_data = pydicom.dcmread(os.path.join(path, file_path))
                    if dcm_data.Modality == 'CT':
                        slice_position = float(dcm_data.ImagePositionPatient[2])
                        _dcm_files[file_path] = slice_position
            return _dcm_files
        else:
            return "There are no CT seriese or more than 2 CT seriese."

    def _has_one_series(self, path):
        """指定されたディレクトリにCTシリーズが1種類だけしかないか判定"""
        uids = []
        for file_path in os.listdir(path):
            if os.path.isdir(os.path.join(path, file_path)):
                continue
            if pydicom.misc.is_dicom(os.path.join(path, file_path)):
                dcm_file = pydicom.dcmread(os.path.join(path, file_path))
                if dcm_file.Modality == 'CT':
                    uids.append(dcm_file.SeriesInstanceUID)
        if len(set(uids)) == 1:
            return True
        else:
            return False

import numpy as np
from .ct import CTImage

ITK_AVAILABLE = True
try:
    import itk
except ImportError:
    ITK_AVAILABLE = False


class DRR:
    """
    DRRに関するクラス
    """
    def __init__(self, ct, beam, size=256):
        if ITK_AVAILABLE:
            self.size = size
            self.image = self._make_drr(ct, beam, size)
            self.extent = (-size/2., size/2., -size/2., size/2.)
        else:
            print(
                'You need ITK to make DRR.\n'
                'Install ITK with "pip install itk".'
            )

    def _make_drr(self, ct, beam, size):
        """
        CTImageクラスのインスタンスとBeamからDRR生成

        Parameters
        ----------
        ct : Instance of CTImage class
            CTImageクラスのインスタンス
        beam : object
            BeamSequenceの要素
        size : float
            DRR Imageのサイズ(mm)
        """
        if not isinstance(ct, CTImage):
            raise TypeError(
                "1st argument must be the instance of CTImage class.")

        # isocenter座標、ガントリ角、カウチ角度の取り出し
        cp_0 = beam.ControlPointSequence[0]  # 最初のコントロールポイント
        isocenter = cp_0.IsocenterPosition
        gan_angle = np.radians(float(cp_0.GantryAngle))
        couch_angle = np.radians(float(cp_0.PatientSupportAngle))

        # numpy配列からITK Imageに変換
        image = itk.GetImageFromArray(ct.volume.astype(np.int16))

        # 原点位置をIsocenter位置に設定
        origin = (ct.position[0] - isocenter[0],
                  ct.position[1] - isocenter[1],
                  -ct.position[2]+isocenter[2])
        # ボクセル間隔を設定
        spacing = (ct.pixel_spacing[0], ct.pixel_spacing[1], ct.thickness)

        image.SetOrigin(origin)
        image.SetSpacing(spacing)

        # RayCastの設定
        image_type = itk.Image[itk.SS, 3]
        ray_caster_type = \
            itk.RayCastInterpolateImageFunction[image_type, itk.D]
        interp = ray_caster_type.New()
        interp.SetInputImage(image)

        # 仮想線源の位置を設定 (SAD=1000 mm)
        g_sin = np.sin(gan_angle)
        g_cos = np.cos(gan_angle)
        c_sin = np.sin(couch_angle)
        c_cos = np.cos(couch_angle)

        focus = (1000*g_sin*c_cos, -1000*g_cos, 1000*g_sin*c_sin)
        interp.SetFocalPoint(focus)

        # 仮想線源位置が変更された際の変換
        transform_type = itk.TranslationTransform[itk.D, 3]
        transform = transform_type.New()
        interp.SetTransform(transform)

        # ピクセル間を線形に補間
        interpolate_type = \
            itk.LinearInterpolateImageFunction[image_type, itk.D]
        aux_interpolator = interpolate_type.New()
        interp.SetInterpolator(aux_interpolator)

        # HU値-200以上のみを反映
        interp.SetThreshold(-200)

        # 256x256ピクセルのDRRを生成
        drr = np.zeros((256, 256))

        # 1ピクセルサイズ
        pixel = size / 256.

        for i in range(256):
            for j in range(256):
                query = ((i-128)*pixel*g_cos*c_cos-(j-128)*pixel*c_sin,
                         (i-128)*pixel*g_sin,
                         (i-128)*pixel*g_cos*c_sin+(j-128)*pixel*c_cos)
                drr[j, i] = interp.Evaluate(query)

        return drr

import numpy as np
import itk

from .ct import CTImage

def make_drr(ct, isocenter, gan_angle):
    """
    CTImageクラスのインスタンスとIsocenter座標、ガントリアングルからDRR生成
    """
    if not isinstance(ct, CTImage):
        return

    # numpy配列からITK Imageに変換
    image = itk.GetImageFromArray(ct.volume.astype(np.int16))

    # 原点位置をIsocenter位置に設定
    origin = (ct.position[0]-isocenter[0], ct.position[1]-isocenter[1], -ct.position[2]+isocenter[2])
    # ボクセル間隔を設定
    spacing = (ct.pixel_spacing[0], ct.pixel_spacing[1], ct.thickness)

    image.SetOrigin(origin)
    image.SetSpacing(spacing)

    # RayCastの設定
    image_type = itk.Image[itk.SS, 3]
    ray_caster_type = itk.RayCastInterpolateImageFunction[image_type, itk.D]
    interp = ray_caster_type.New()
    interp.SetInputImage(image)

    # 仮想線源の位置を設定 (SID=1000 mm)
    gan_angle = np.radians(gan_angle)
    sin = np.sin(gan_angle)
    cos = np.cos(gan_angle)

    focus = (1000 * sin, -1000 * cos, 0)
    interp.SetFocalPoint(focus)

    # 仮想線源位置が変更された際の変換
    transform_type = itk.TranslationTransform[itk.D, 3]
    transform = transform_type.New()
    interp.SetTransform(transform)

    # ピクセル間を線形に補間
    interpolate_type = itk.LinearInterpolateImageFunction[image_type, itk.D]
    aux_interpolator = interpolate_type.New()
    interp.SetInterpolator(aux_interpolator)

    # HU値-100以上のみを反映
    interp.SetThreshold(-100)

    # 25x25cm^2のDRRを生成
    drr = np.zeros((250,250))

    for i in range(250):
        for j in range(250):
            query = ((i-125)*cos, (i-125)*sin, (j-125))
            drr[j, i] = interp.Evaluate(query)
    
    return drr

import numpy as np
import matplotlib.pyplot as plt


def make_bev(beam, ax):

    # Leaf対の数
    num_of_leaves = beam.BeamLimitingDeviceSequence[2].NumberOfLeafJawPairs

    cp0 = beam.ControlPointSequence[0]  # 最初のコントロールポイント

    # X Jawの位置
    jaw_x = cp0.BeamLimitingDevicePositionSequence[0].LeafJawPositions
    # Y Jawの位置
    jaw_y = cp0.BeamLimitingDevicePositionSequence[1].LeafJawPositions
    # MLCの位置
    leaf_position = cp0.BeamLimitingDevicePositionSequence[2].LeafJawPositions

    # Leaf境界のY座標
    boundaries = np.array(
        beam.BeamLimitingDeviceSequence[2].LeafPositionBoundaries)
    leaf_widths = np.diff(boundaries)  # Leafの幅

    leaf_length = 200  # Leafの長さ

    # コリメータ回転対応
    angle = float(cp0.BeamLimitingDeviceAngle)
    angle_rad = np.radians(angle)
    a_sin = np.sin(angle_rad)
    a_cos = np.cos(angle_rad)

    # X/Y Jaw
    x_0 = jaw_x[0]*a_cos - jaw_y[0]*a_sin
    y_0 = jaw_x[0]*a_sin + jaw_y[0]*a_cos
    ax.add_patch(plt.Rectangle(
        xy=(x_0, y_0),
        width=jaw_x[1]-jaw_x[0],
        height=jaw_y[1]-jaw_y[0],
        fill=False, ec='yellow', angle=angle, lw=1.5))

    for i in range(num_of_leaves):
        # X1側のMLC
        x_1 = (leaf_position[i]-leaf_length)*a_cos - boundaries[i]*a_sin
        y_1 = (leaf_position[i]-leaf_length)*a_sin + boundaries[i]*a_cos
        ax.add_patch(plt.Rectangle(
            xy=(x_1, y_1),
            width=leaf_length,
            height=leaf_widths[i],
            fill=True, ec='blue', angle=angle, lw=1., alpha=0.3))

        # X2側のMLC
        x_2 = leaf_position[i+num_of_leaves]*a_cos - boundaries[i]*a_sin
        y_2 = leaf_position[i+num_of_leaves]*a_sin + boundaries[i]*a_cos
        ax.add_patch(plt.Rectangle(
            xy=(x_2, y_2),
            width=leaf_length,
            height=leaf_widths[i],
            fill=True, ec='blue', angle=angle, lw=1., alpha=0.3))

    ax.patch.set_facecolor('gray')

    # 表示範囲の設定、最も長い対角線+marginが表示範囲に含まれるように
    disp = max([np.sqrt(i**2 + j**2) for i in jaw_x for j in jaw_y])
    margin = 30
    disp += margin
    ax.set_xlim([-disp, disp])
    ax.set_ylim([-disp, disp])
    ax.set_aspect('equal')

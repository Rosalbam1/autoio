"""
  autowrite
"""

import autowrite


GEO_SYMBS = ('C', 'C', 'H', 'H', 'H', 'H', 'H', 'H')
XYZ1 = (
    (-1.4283035320563338, 0.013425343735546437, -0.030302158896694683),
    (1.4283027358735494, -0.013425597530894248, 0.0303022919384165),
    (-2.1972722614281355, -0.19229727219177065, 1.8778380427620682),
    (-2.121310184939721, 1.792702413487708, -0.8231106338374065),
    (-2.1448124562913287, -1.5396513482615042, -1.191852168914227),
    (2.1448121742707795, 1.539654946791746, 1.1918517388178247),
    (2.1972712765396953, 0.1922944277301287, -1.8778395029874426),
    (2.121312248031497, -1.7927029137609576, 0.8231123911174519))
XYZ2 = (
    (-1.4283035320563338, 0.013425343735546437, -0.030302158896694683),
    (1.4283027358735494, -0.013425597530894248, 0.0303022919384165),
    (-4.1448124562913287, -1.5396513482615042, -1.191852168914227),
    (4.1448121742707795, 1.539654946791746, 1.1918517388178247),
    (4.1972712765396953, 0.1922944277301287, -1.8778395029874426),
    (4.121312248031497, -1.7927029137609576, 0.8231123911174519),
    (-4.1972722614281355, -0.19229727219177065, 1.8778380427620682),
    (-4.121310184939721, 1.792702413487708, -0.8231106338374065))
COMMENT1_STR = 'Comment line 1'
COMMENT2_STR = 'Comment line 2'

ZMA_SYMBS = ('C', 'O', 'H', 'H', 'H', 'H')
ZMA_KEY_MAT = (
    (None, None, None),
    (1, None, None),
    (1, 2, None),
    (1, 2, 3),
    (1, 2, 3),
    (2, 1, 3))
ZMA_NAME_MAT = (
    (None, None, None),
    ('R1', None, None),
    ('R2', 'A2', None),
    ('R3', 'A3', 'D3'),
    ('R4', 'A4', 'D4'),
    ('R5', 'A5', 'D5'))
ZMA_VAL_DCT = {
    'R1': 2.67535, 'R2': 2.06501, 'A2': 109.528, 'R3': 2.06501,
    'A3': 109.528, 'D3': 120.808, 'R4': 2.06458, 'A4': 108.982,
    'D4': 240.404, 'R5': 1.83748, 'A5': 107.091, 'D5': 299.596}


def test__geo():
    """ test autowrite.geom.write
        test autowrite.geom.write_xyz
        test autowrite.geom.write_xyz_trajectory
    """

    geo_str = autowrite.geom.write(GEO_SYMBS, XYZ1)
    assert geo_str == (
        'C   -1.428304   0.013425  -0.030302\n'
        'C    1.428303  -0.013426   0.030302\n'
        'H   -2.197272  -0.192297   1.877838\n'
        'H   -2.121310   1.792702  -0.823111\n'
        'H   -2.144812  -1.539651  -1.191852\n'
        'H    2.144812   1.539655   1.191852\n'
        'H    2.197271   0.192294  -1.877840\n'
        'H    2.121312  -1.792703   0.823112'
    )

    xyz_str = autowrite.geom.write_xyz(GEO_SYMBS, XYZ1, comment=COMMENT1_STR)
    assert xyz_str == (
        ' 8\n'
        'Comment line 1\n'
        'C   -1.428304   0.013425  -0.030302\n'
        'C    1.428303  -0.013426   0.030302\n'
        'H   -2.197272  -0.192297   1.877838\n'
        'H   -2.121310   1.792702  -0.823111\n'
        'H   -2.144812  -1.539651  -1.191852\n'
        'H    2.144812   1.539655   1.191852\n'
        'H    2.197271   0.192294  -1.877840\n'
        'H    2.121312  -1.792703   0.823112'
    )

    xyzs_lst = (XYZ1, XYZ2)
    comments = (COMMENT1_STR, COMMENT2_STR)
    xyz_traj_str = autowrite.geom.write_xyz_trajectory(
        GEO_SYMBS, xyzs_lst, comments=comments)
    assert xyz_traj_str == (
        ' 8\n'
        'Comment line 1\n'
        'C   -1.428304   0.013425  -0.030302\n'
        'C    1.428303  -0.013426   0.030302\n'
        'H   -2.197272  -0.192297   1.877838\n'
        'H   -2.121310   1.792702  -0.823111\n'
        'H   -2.144812  -1.539651  -1.191852\n'
        'H    2.144812   1.539655   1.191852\n'
        'H    2.197271   0.192294  -1.877840\n'
        'H    2.121312  -1.792703   0.823112\n'
        ' 8\n'
        'Comment line 2\n'
        'C   -1.428304   0.013425  -0.030302\n'
        'C    1.428303  -0.013426   0.030302\n'
        'H   -4.144812  -1.539651  -1.191852\n'
        'H    4.144812   1.539655   1.191852\n'
        'H    4.197271   0.192294  -1.877840\n'
        'H    4.121312  -1.792703   0.823112\n'
        'H   -4.197272  -0.192297   1.877838\n'
        'H   -4.121310   1.792702  -0.823111'
    )


def test__zma():
    """ test autowrite.zmatrix.write
    """

    zma_str = autowrite.zmatrix.write(
        ZMA_SYMBS, ZMA_KEY_MAT, ZMA_NAME_MAT, ZMA_VAL_DCT,
        mat_delim=' ', setval_sign='=')
    assert zma_str == (
        'C  \n'
        'O  1    R1 \n'
        'H  1    R2  2    A2 \n'
        'H  1    R3  2    A3  3    D3 \n'
        'H  1    R4  2    A4  3    D4 \n'
        'H  2    R5  1    A5  3    D5 \n'
        '\n'
        'R1   =   2.675350\n'
        'R2   =   2.065010\n'
        'R3   =   2.065010\n'
        'R4   =   2.064580\n'
        'R5   =   1.837480\n'
        'A2   = 109.528000\n'
        'A3   = 109.528000\n'
        'A4   = 108.982000\n'
        'A5   = 107.091000\n'
        'D3   = 120.808000\n'
        'D4   = 240.404000\n'
        'D5   = 299.596000'
    )

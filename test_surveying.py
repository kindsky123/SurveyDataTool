import unittest
import math
from surveying import distance, azimuth, coordinate_forward, coordinate_inverse


class TestSurveying(unittest.TestCase):
    """测试 surveying.py 中的测绘计算函数"""

    def test_distance(self):
        """测试两点距离计算"""
        # 3-4-5 三角形
        self.assertAlmostEqual(distance(0, 0, 3, 4), 5.0, places=6)
        # 同一点距离为 0
        self.assertAlmostEqual(distance(1, 2, 1, 2), 0.0, places=6)
        # 负数坐标
        self.assertAlmostEqual(distance(-1, -1, 2, 3), 5.0, places=6)

    def test_azimuth(self):
        """测试方位角计算（0°~360°）"""
        # 第一象限（东北）
        self.assertAlmostEqual(azimuth(0, 0, 1, 1), 45.0, places=6)
        # 第二象限（西北）
        self.assertAlmostEqual(azimuth(0, 0, -1, 1), 135.0, places=6)
        # 第三象限（西南）
        self.assertAlmostEqual(azimuth(0, 0, -1, -1), 225.0, places=6)
        # 第四象限（东南）
        self.assertAlmostEqual(azimuth(0, 0, 1, -1), 315.0, places=6)
        # 正北（X 轴正方向）
        self.assertAlmostEqual(azimuth(0, 0, 1, 0), 0.0, places=6)
        # 正东（Y 轴正方向）
        self.assertAlmostEqual(azimuth(0, 0, 0, 1), 90.0, places=6)

    def test_coordinate_forward(self):
        """测试坐标正算"""
        # 起点(0,0)，距离5，方位角90°（正东）→ 终点(0, 5)
        x, y = coordinate_forward(0, 0, 5, 90)
        self.assertAlmostEqual(x, 0.0, places=6)
        self.assertAlmostEqual(y, 5.0, places=6)

        # 起点(1,1)，距离√2，方位角45° → 终点(2, 2)
        x, y = coordinate_forward(1, 1, math.sqrt(2), 45)
        self.assertAlmostEqual(x, 2.0, places=6)
        self.assertAlmostEqual(y, 2.0, places=6)

        # 起点(10, 10)，距离0 → 终点不变
        x, y = coordinate_forward(10, 10, 0, 30)
        self.assertAlmostEqual(x, 10.0, places=6)
        self.assertAlmostEqual(y, 10.0, places=6)

    def test_coordinate_inverse(self):
        """测试坐标反算"""
        # 两点 (0,0) 和 (3,4) → 距离5，方位角53.130102°
        dis, ang = coordinate_inverse(0, 0, 3, 4)
        self.assertAlmostEqual(dis, 5.0, places=6)
        self.assertAlmostEqual(ang, 53.13010235415598, places=6)

        # 同一点 → 距离0，方位角0
        dis, ang = coordinate_inverse(1, 1, 1, 1)
        self.assertAlmostEqual(dis, 0.0, places=6)
        self.assertAlmostEqual(ang, 0.0, places=6)

        # 验证：坐标正算和坐标反算互为逆运算
        x1, y1 = 10, 20
        x2, y2 = 30, 50
        dis, ang = coordinate_inverse(x1, y1, x2, y2)
        x3, y3 = coordinate_forward(x1, y1, dis, ang)
        self.assertAlmostEqual(x3, x2, places=6)
        self.assertAlmostEqual(y3, y2, places=6)


if __name__ == "__main__":
    unittest.main()
import unittest
import math
from traverse import traverse_calculation, adjust_traverse


class TestTraverse(unittest.TestCase):
    """测试 traverse.py 中的导线计算函数"""

    def test_traverse_calculation_perfect_closure(self):
        """测试理想闭合导线（闭合差为0）"""
        # 一个正方形导线：从(0,0)出发，方位角0°，边长10
        # 观测数据：4个点，每个转角90°，边长10
        observed = [
            {"name": "A", "angle": 90, "distance": 10, "remark": ""},
            {"name": "B", "angle": 90, "distance": 10, "remark": ""},
            {"name": "C", "angle": 90, "distance": 10, "remark": ""},
            {"name": "D", "angle": 90, "distance": 10, "remark": ""},
        ]

        results, closure = traverse_calculation(0, 0, 0, observed)

        # 验证点数量
        self.assertEqual(len(results), 4)

        # 验证最后一个点应该回到起点附近（理想闭合）
        # A点: (0,0)
        # B点: (10,0)   ← 方位角0°，边长10
        # C点: (10,10)  ← 转90°后方位角90°，边长10
        # D点: (0,10)   ← 再转90°后方位角180°，边长10
        # 回到起点: (0,0) ← 再转90°后方位角270°，边长10
        self.assertAlmostEqual(results[0]["x"], 10.0, places=6)
        self.assertAlmostEqual(results[0]["y"], 0.0, places=6)
        self.assertAlmostEqual(results[1]["x"], 10.0, places=6)
        self.assertAlmostEqual(results[1]["y"], 10.0, places=6)
        self.assertAlmostEqual(results[2]["x"], 0.0, places=6)
        self.assertAlmostEqual(results[2]["y"], 10.0, places=6)
        self.assertAlmostEqual(results[3]["x"], 0.0, places=6)
        self.assertAlmostEqual(results[3]["y"], 0.0, places=6)

        # 验证闭合差为0
        self.assertAlmostEqual(closure["fx"], 0.0, places=6)
        self.assertAlmostEqual(closure["fy"], 0.0, places=6)
        self.assertAlmostEqual(closure["f"], 0.0, places=6)
        self.assertAlmostEqual(closure["total_distance"], 40.0, places=6)

    def test_traverse_with_known_point(self):
        """测试包含已知点的导线"""
        observed = [
            {"name": "已知起点", "angle": 0, "distance": 0, "remark": "已知"},
            {"name": "A", "angle": 90, "distance": 10, "remark": ""},
            {"name": "B", "angle": 90, "distance": 10, "remark": ""},
        ]

        results, closure = traverse_calculation(0, 0, 0, observed)

        # 第一个点（已知点）应该保持起点坐标
        self.assertEqual(results[0]["name"], "已知起点")
        self.assertEqual(results[0]["x"], 0)
        self.assertEqual(results[0]["y"], 0)
        self.assertIsNone(results[0]["dx"])

        # 后续点正常计算
        self.assertEqual(results[1]["name"], "A")
        self.assertAlmostEqual(results[1]["x"], 10.0, places=6)
        self.assertAlmostEqual(results[1]["y"], 0.0, places=6)

        self.assertEqual(results[2]["name"], "B")
        self.assertAlmostEqual(results[2]["x"], 10.0, places=6)
        self.assertAlmostEqual(results[2]["y"], 10.0, places=6)

    def test_adjust_traverse(self):
        """测试导线平差（闭合差分配）"""
        # 使用正方形导线数据
        observed = [
            {"name": "A", "angle": 90, "distance": 10, "remark": ""},
            {"name": "B", "angle": 90, "distance": 10, "remark": ""},
            {"name": "C", "angle": 90, "distance": 10, "remark": ""},
            {"name": "D", "angle": 90, "distance": 10, "remark": ""},
        ]

        results, closure = traverse_calculation(0, 0, 0, observed)
        adjusted = adjust_traverse(results, closure)

        # 验证平差后坐标与原始一致（因为闭合差为0）
        for i in range(len(results)):
            self.assertAlmostEqual(adjusted[i]["x"], results[i]["x"], places=6)
            self.assertAlmostEqual(adjusted[i]["y"], results[i]["y"], places=6)


if __name__ == "__main__":
    unittest.main()
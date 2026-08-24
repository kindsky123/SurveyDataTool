import unittest
import os
import tempfile
from data_process import read_points, validate_points, get_points_stats


class TestDataProcess(unittest.TestCase):
    """测试 data_process.py 中的数据读取与处理函数"""

    def setUp(self):
        """每个测试前执行：创建临时CSV文件"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        self.temp_file.close()
        self.filename = self.temp_file.name

    def tearDown(self):
        """每个测试后执行：删除临时文件"""
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def write_csv(self, content):
        """辅助方法：写入CSV内容到临时文件"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(content)

    def test_read_points_valid(self):
        """测试正常读取CSV"""
        self.write_csv("点号,X,Y\nP001,1000.123,2000.456\nP002,1050.231,2080.123\n")
        points = read_points(self.filename)
        self.assertEqual(len(points), 2)
        self.assertEqual(points[0]["id"], "P001")
        self.assertAlmostEqual(points[0]["x"], 1000.123, places=3)
        self.assertAlmostEqual(points[0]["y"], 2000.456, places=3)

    def test_read_points_missing_column(self):
        """测试CSV缺少必需列"""
        self.write_csv("编号,X,Y\nA1,1000,2000\n")
        with self.assertRaises(ValueError) as context:
            read_points(self.filename)
        self.assertIn("缺少必需列", str(context.exception))

    def test_read_points_empty_header(self):
        """测试CSV只有表头没有数据"""
        self.write_csv("点号,X,Y\n")
        # read_points 正常返回空列表
        points = read_points(self.filename)
        self.assertEqual(len(points), 0)

    def test_read_points_non_numeric(self):
        """测试CSV包含非数字坐标 -> 不崩溃，保留原始字符串"""
        self.write_csv("点号,X,Y\nA1,abc,2000\n")
        points = read_points(self.filename)
        self.assertEqual(points[0]["x"], "abc")  # 不是 float，是字符串

    def test_validate_points_empty(self):
        """测试空数据校验"""
        valid, msg = validate_points([])
        self.assertFalse(valid)
        self.assertIn("没有测量点数据", msg)

    def test_validate_points_duplicate(self):
        """测试重复点号校验"""
        points = [
            {"id": "P001", "x": 1, "y": 2},
            {"id": "P001", "x": 3, "y": 4}
        ]
        valid, msg = validate_points(points)
        self.assertFalse(valid)
        self.assertIn("重复", msg)

    def test_validate_points_empty_id(self):
        """测试空点号校验"""
        points = [
            {"id": "", "x": 1, "y": 2}
        ]
        valid, msg = validate_points(points)
        self.assertFalse(valid)
        self.assertIn("空的测量点编号", msg)

    def test_get_points_stats(self):
        """测试统计函数"""
        points = [
            {"id": "P001", "x": 100, "y": 200},
            {"id": "P002", "x": 200, "y": 300},
            {"id": "P003", "x": 300, "y": 400}
        ]
        stats = get_points_stats(points)
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["x_min"], 100)
        self.assertEqual(stats["x_max"], 300)
        self.assertEqual(stats["x_avg"], 200)
        self.assertEqual(stats["y_min"], 200)
        self.assertEqual(stats["y_max"], 400)
        self.assertEqual(stats["y_avg"], 300)

    def test_get_points_stats_empty(self):
        """测试空数据统计"""
        stats = get_points_stats([])
        self.assertIsNone(stats)


if __name__ == "__main__":
    unittest.main()
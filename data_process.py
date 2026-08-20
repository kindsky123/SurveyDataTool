import csv


# csv测量数据文件读取
def read_points(filename):
    # 读取测量点并把点放进列表
    points = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # 检查表头是否包含必需的列
        required = ["点号", "X", "Y"]

        if not reader.fieldnames:
            raise ValueError("CSV文件为空或没有表头！")

        missing = [col for col in required if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV缺少必需列：{missing}")

        for row in reader:
            # 点号原样保存
            point_id = row["点号"]

            # 尝试转成数字，转不了就保留原文，交给 validate_points 检查
            try:
                x = float(row["X"])
            except ValueError:
                x = row["X"]

            try:
                y = float(row["Y"])
            except ValueError:
                y = row["Y"]

            points.append({
                "id": point_id,
                "x": x,
                "y": y
            })

    return points


def find_point(points, point_id):
    # 查找点函数
    for point in points:
        if point["id"] == point_id:
            return point

    return None


# Day 6 新增：测量点数据校验

def validate_points(points):

    # 用来保存已经出现过的点号
    valid_points = []
    point_ids = set()

    # 遍历所有测量点
    for point in points:

        # 检查点号是否为空
        if not point["id"]:
            return False, "存在空的测量点编号！"

        # 检查点号是否重复
        if point["id"] in point_ids:
            return False, f"测量点 {point['id']} 重复！"

        point_ids.add(point["id"])

        # 检查 X 坐标
        try:
            float(point["x"])
        except (ValueError, TypeError):
            return False, f"测量点 {point['id']} 的X坐标不是数字！"

        # 检查 Y 坐标
        try:
            float(point["y"])
        except (ValueError, TypeError):
            return False, f"测量点 {point['id']} 的Y坐标不是数字！"

    return True, "测量点数据检查通过！"


# ===============================
# 保存计算结果
# ===============================

def save_results(filename, results):
    # 把Python里面的数据写入CSV

    with open(
        filename,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "起点",
                "终点",
                "距离",
                "方位角"
            ]
        )

        writer.writeheader()

        for result in results:
            writer.writerow(result)
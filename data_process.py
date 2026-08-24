import csv


# ==============================
# CSV 测量数据文件读取
# ==============================

def read_points(filename):
    """
    读取测量点 CSV 文件
    
    CSV 格式要求：
        表头必须包含：点号, X, Y
        坐标值必须为数字
    
    返回：
        points: 点列表，每个点包含 id, x, y
        如果数据有问题，会抛出 ValueError
    """
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


# ==============================
# 查找点
# ==============================

def find_point(points, point_id):
    """根据点号查找测量点"""
    for point in points:
        if point["id"] == point_id:
            return point
    return None


# ==============================
# 测量点数据校验
# ==============================

def validate_points(points):
    """
    校验测量点数据
    
    检查项：
        1. 是否有数据
        2. 点号是否为空
        3. 点号是否重复
        4. X 坐标是否为数字
        5. Y 坐标是否为数字
    
    返回：
        (True, "检查通过") 或 (False, "错误信息")
    """
    # 检查是否没有数据
    if not points:
        return False, "文件中没有测量点数据！"

    point_ids = set()

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


# ==============================
# 测量点统计
# ==============================

def get_points_stats(points):
    """
    统计测量点数据
    
    返回：
        stats: 字典，包含 count, x_min, x_max, y_min, y_max, x_avg, y_avg
        如果 points 为空，返回 None
    """
    if not points:
        return None

    n = len(points)
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]

    stats = {
        "count": n,
        "x_min": min(xs),
        "x_max": max(xs),
        "y_min": min(ys),
        "y_max": max(ys),
        "x_avg": sum(xs) / n,
        "y_avg": sum(ys) / n,
    }
    return stats


# ==============================
# 保存计算结果
# ==============================

def save_results(filename, results, include_cumulative=False):
    """
    把 Python 里面的数据写入 CSV
    
    参数：
        filename: 保存的文件名
        results: 结果列表，每个元素包含"起点""终点""距离""方位角"
        include_cumulative: 是否包含累计边长列
    """
    # 定义字段名
    fieldnames = ["起点", "终点", "距离", "方位角"]
    if include_cumulative:
        fieldnames.append("累计边长")
    
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        cumulative = 0
        for result in results:
            if include_cumulative:
                cumulative += result["距离"]
                result["累计边长"] = round(cumulative, 3)
            writer.writerow(result)
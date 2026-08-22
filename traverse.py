import math
import csv


def read_traverse_data(filename):
    """
    读取导线观测数据 CSV 文件
    格式：点号, 角(度), 边长(米), 备注
    备注列可选，标注"已知"表示该点为已知点
    """
    data = []
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            point = {
                "name": row["点号"],
                "angle": float(row["角(度)"]),
                "distance": float(row["边长(米)"]),
                "remark": row.get("备注", "")
            }
            data.append(point)
    return data


def traverse_calculation(start_x, start_y, start_azimuth, observed_data):
    """
    导线坐标推算
    
    参数：
        start_x, start_y: 起点坐标
        start_azimuth: 起始方位角（度）
        observed_data: 观测数据列表，每个元素包含 name, angle, distance, remark
    
    返回：
        results: 列表，每个元素包含点号、X、Y、坐标增量
        closure: 闭合差字典 {fx, fy, f, k, total_distance}
    """
    results = []
    
    # 当前坐标和方位角
    cur_x = start_x
    cur_y = start_y
    cur_azimuth = start_azimuth
    
    total_distance = 0
    sum_dx = 0
    sum_dy = 0
    
    for point in observed_data:
        # 跳过已知点（仅用于记录，不参与计算）
        if point["remark"] == "已知":
            results.append({
                "name": point["name"],
                "x": cur_x,
                "y": cur_y,
                "dx": None,
                "dy": None,
                "distance": None
            })
            continue
        
        # 计算新的方位角：新方位角 = 当前方位角 + 180° - 转角
        # 注意：这里的转角是左角（观测方向为顺时针）
        new_azimuth = cur_azimuth + 180 - point["angle"]
        
        # 标准化到 0~360°
        new_azimuth = new_azimuth % 360
        
        # 计算坐标增量
        angle_rad = math.radians(new_azimuth)
        dx = point["distance"] * math.cos(angle_rad)
        dy = point["distance"] * math.sin(angle_rad)
        
        # 累加
        total_distance += point["distance"]
        sum_dx += dx
        sum_dy += dy
        
        # 推算新坐标
        cur_x += dx
        cur_y += dy
        
        results.append({
            "name": point["name"],
            "x": cur_x,
            "y": cur_y,
            "dx": dx,
            "dy": dy,
            "distance": point["distance"],
            "azimuth": new_azimuth
        })
        
        # 更新当前方位角用于下一步
        cur_azimuth = new_azimuth
    
    # 计算闭合差
    fx = sum_dx
    fy = sum_dy
    f = math.sqrt(fx**2 + fy**2)
    k = f / total_distance if total_distance > 0 else 0
    
    closure = {
        "fx": fx,
        "fy": fy,
        "f": f,
        "k": k,
        "total_distance": total_distance,
        "sum_dx": sum_dx,
        "sum_dy": sum_dy
    }
    
    return results, closure


def format_traverse_report(results, closure):
    """格式化输出导线计算结果"""
    print("=" * 60)
    print("              导线计算结果")
    print("=" * 60)
    print("\n【导线点坐标】")
    print("-" * 60)
    print(f"{'点号':<8} {'X坐标':<12} {'Y坐标':<12} {'ΔX':<12} {'ΔY':<12} {'边长':<10}")
    print("-" * 60)
    
    for r in results:
        if r["dx"] is None:
            print(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {'(已知)':<12} {'(已知)':<12} {'':<10}")
        else:
            print(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {r['dx']:<12.3f} {r['dy']:<12.3f} {r['distance']:<10.3f}")
    
    print("-" * 60)
    print(f"\n【闭合差】")
    print(f"fx = {closure['fx']:.6f} m")
    print(f"fy = {closure['fy']:.6f} m")
    print(f"全长闭合差 f = {closure['f']:.6f} m")
    print(f"导线总长 = {closure['total_distance']:.3f} m")
    print(f"相对闭合差 K = 1/{int(1/closure['k']) if closure['k'] > 0 else '∞'}")
    print("=" * 60)
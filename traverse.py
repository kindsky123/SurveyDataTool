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

def adjust_traverse(results, closure):
    """
    按边长比例分配闭合差，计算各点平差后坐标
    
    参数：
        results: traverse_calculation 返回的结果列表
        closure: traverse_calculation 返回的闭合差字典
    
    返回：
        adjusted_results: 包含平差后坐标的结果列表
    """
    total_dist = closure['total_distance']
    fx = closure['fx']
    fy = closure['fy']
    
    if total_dist == 0:
        return results
    
    adjusted_results = []
    cum_dx_adj = 0  # 累计 X 改正数
    cum_dy_adj = 0  # 累计 Y 改正数
    
    for r in results:
        new_r = r.copy()
        
        # 已知点不参与平差
        if r['dx'] is None:
            new_r['adj_x'] = r['x']
            new_r['adj_y'] = r['y']
            new_r['vx'] = None
            new_r['vy'] = None
            adjusted_results.append(new_r)
            continue
        
        # 计算该边改正数（反号按边长比例分配）
        vx = -fx * (r['distance'] / total_dist)
        vy = -fy * (r['distance'] / total_dist)
        
        # 累计改正数
        cum_dx_adj += vx
        cum_dy_adj += vy
        
        # 平差后坐标 = 原始坐标 + 累计改正数
        new_r['adj_x'] = r['x'] + cum_dx_adj
        new_r['adj_y'] = r['y'] + cum_dy_adj
        new_r['vx'] = vx
        new_r['vy'] = vy
        
        adjusted_results.append(new_r)
    
    return adjusted_results


def format_adjusted_report(adjusted_results, closure):
    """格式化输出平差后的导线计算结果"""
    print("=" * 70)
    print("              导线平差结果")
    print("=" * 70)
    
    print("\n【原始坐标与改正数】")
    print("-" * 70)
    print(f"{'点号':<8} {'原始X':<12} {'原始Y':<12} {'Vx':<12} {'Vy':<12} {'平差后X':<12} {'平差后Y':<12}")
    print("-" * 70)
    
    for r in adjusted_results:
        if r['vx'] is None:
            print(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {'(已知)':<12} {'(已知)':<12} {r['x']:<12.3f} {r['y']:<12.3f}")
        else:
            print(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {r['vx']:<12.3f} {r['vy']:<12.3f} {r['adj_x']:<12.3f} {r['adj_y']:<12.3f}")
    
    print("-" * 70)
    
    # 精度评定
    print("\n【精度评定】")
    print(f"全长闭合差 f = {closure['f']:.6f} m")
    print(f"导线总长 = {closure['total_distance']:.3f} m")
    print(f"相对闭合差 K = 1/{int(1/closure['k']) if closure['k'] > 0 else '∞'}")
    
    # 判断是否合格（按 1/2000 限差）
    if closure['k'] > 0:
        k_allow = 1 / 2000
        if closure['k'] <= k_allow:
            print("✅ 精度评定：合格（K ≤ 1/2000）")
        else:
            print("❌ 精度评定：不合格（K > 1/2000），建议重测")
    else:
        print("✅ 精度评定：完美闭合")
    print("=" * 70)


def save_traverse_report(results, closure, adjusted_results, start_x, start_y, start_azimuth, filename=None):
    """
    导出导线计算报告到 .txt 文件
    
    参数：
        results: 原始计算结果列表
        closure: 闭合差字典
        adjusted_results: 平差后结果列表（如果进行了平差）
        start_x, start_y: 起点坐标
        start_azimuth: 起始方位角
        filename: 指定文件名，如果为 None 则自动生成
    """
    import os
    from datetime import datetime
    
    # 自动生成文件名
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"traverse_report_{timestamp}.txt"
    
    # 确保 output 目录存在
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        # 标题
        f.write("=" * 60 + "\n")
        f.write("                    导线测量计算报告\n")
        f.write("=" * 60 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 输入数据
        f.write("【输入数据】\n")
        f.write(f"起点坐标: X={start_x:.3f}, Y={start_y:.3f}\n")
        f.write(f"起始方位角: {start_azimuth:.3f}°\n")
        f.write(f"观测点数: {len(results)}\n\n")
        
        # 原始计算结果
        f.write("【原始计算结果】\n")
        f.write("=" * 60 + "\n")
        f.write(f"{'点号':<8} {'X坐标':<12} {'Y坐标':<12} {'ΔX':<12} {'ΔY':<12} {'边长':<10}\n")
        f.write("-" * 60 + "\n")
        
        for r in results:
            if r["dx"] is None:
                f.write(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {'(已知)':<12} {'(已知)':<12} {'-':<10}\n")
            else:
                f.write(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {r['dx']:<12.3f} {r['dy']:<12.3f} {r['distance']:<10.3f}\n")
        
        f.write("\n")
        
        # 闭合差
        f.write("【闭合差】\n")
        f.write(f"fx = {closure['fx']:.6f} m\n")
        f.write(f"fy = {closure['fy']:.6f} m\n")
        f.write(f"全长闭合差 f = {closure['f']:.6f} m\n")
        f.write(f"导线总长 = {closure['total_distance']:.3f} m\n")
        k_str = f"1/{int(1/closure['k'])}" if closure['k'] > 0 else "∞"
        f.write(f"相对闭合差 K = {k_str}\n\n")
        
        # 平差结果（如果有）
        if adjusted_results:
            f.write("【平差结果】\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'点号':<8} {'原始X':<12} {'原始Y':<12} {'Vx':<12} {'Vy':<12} {'平差后X':<12} {'平差后Y':<12}\n")
            f.write("-" * 70 + "\n")
            
            for r in adjusted_results:
                if r['vx'] is None:
                    f.write(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {'(已知)':<12} {'(已知)':<12} {r['x']:<12.3f} {r['y']:<12.3f}\n")
                else:
                    f.write(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {r['vx']:<12.3f} {r['vy']:<12.3f} {r['adj_x']:<12.3f} {r['adj_y']:<12.3f}\n")
            
            f.write("\n")
        
        # 精度评定
        f.write("【精度评定】\n")
        f.write(f"全长闭合差 f = {closure['f']:.6f} m\n")
        f.write(f"导线总长 = {closure['total_distance']:.3f} m\n")
        f.write(f"相对闭合差 K = {k_str}\n")
        
        if closure['k'] > 0:
            if closure['k'] <= 1/2000:
                f.write("✅ 精度评定：合格（K ≤ 1/2000）\n")
            else:
                f.write("❌ 精度评定：不合格（K > 1/2000），建议重测\n")
        else:
            f.write("✅ 精度评定：完美闭合\n")
        
        f.write("=" * 60 + "\n")
        f.write(f"报告保存路径: {filepath}\n")
    
    return filepath

def traverse_adjust(start_x, start_y, end_x, end_y, start_azimuth, end_azimuth, observed_data):
    """
    附和导线计算（含平差）
    
    参数：
        start_x, start_y: 起点已知坐标
        end_x, end_y: 终点已知坐标
        start_azimuth: 起始方位角（度）
        end_azimuth: 终边方位角（度）
        observed_data: 观测数据列表
    
    返回：
        results: 各点坐标
        closure: 角度闭合差、坐标闭合差
        adjusted_results: 平差后结果
    """
    import math
    
    # 第一步：角度平差
    # 计算理论终边方位角
    # 理论上：α_终 = α_起 + n*180° - Σβ (左角)
    n = len(observed_data)
    sum_angle = sum([p["angle"] for p in observed_data])
    theory_end_azimuth = (start_azimuth + n * 180 - sum_angle) % 360
    
    # 角度闭合差
    angle_error = theory_end_azimuth - end_azimuth
    # 角度改正数（反号平均分配）
    angle_correction = -angle_error / n
    
    # 应用角度改正数到每个观测角
    corrected_data = []
    for p in observed_data:
        new_p = p.copy()
        new_p["angle"] = p["angle"] + angle_correction
        corrected_data.append(new_p)
    
    # 第二步：用改正后的角度推算坐标
    results = []
    cur_x, cur_y = start_x, start_y
    cur_azimuth = start_azimuth
    total_distance = 0
    sum_dx, sum_dy = 0, 0
    
    for p in corrected_data:
        # 计算新方位角
        new_azimuth = (cur_azimuth + 180 - p["angle"]) % 360
        angle_rad = math.radians(new_azimuth)
        dx = p["distance"] * math.cos(angle_rad)
        dy = p["distance"] * math.sin(angle_rad)
        
        cur_x += dx
        cur_y += dy
        total_distance += p["distance"]
        sum_dx += dx
        sum_dy += dy
        
        results.append({
            "name": p["name"],
            "x": cur_x,
            "y": cur_y,
            "dx": dx,
            "dy": dy,
            "distance": p["distance"],
            "azimuth": new_azimuth
        })
    
    # 第三步：坐标闭合差
    fx = end_x - cur_x
    fy = end_y - cur_y
    f = math.sqrt(fx**2 + fy**2)
    k = f / total_distance if total_distance > 0 else 0
    
    closure = {
        "angle_error": angle_error,
        "angle_correction": angle_correction,
        "fx": fx,
        "fy": fy,
        "f": f,
        "k": k,
        "total_distance": total_distance
    }
    
    # 第四步：平差（按边长分配坐标闭合差）
    adjusted_results = []
    cum_dx_adj = 0
    cum_dy_adj = 0
    
    for i, r in enumerate(results):
        new_r = r.copy()
        vx = -fx * (r["distance"] / total_distance) if total_distance > 0 else 0
        vy = -fy * (r["distance"] / total_distance) if total_distance > 0 else 0
        cum_dx_adj += vx
        cum_dy_adj += vy
        new_r["adj_x"] = r["x"] + cum_dx_adj
        new_r["adj_y"] = r["y"] + cum_dy_adj
        new_r["vx"] = vx
        new_r["vy"] = vy
        adjusted_results.append(new_r)
    
    return results, closure, adjusted_results


def format_traverse_adjust_report(results, closure, adjusted_results, start_x, start_y, end_x, end_y):
    """格式化输出附和导线计算结果"""
    print("=" * 70)
    print("              附和导线计算结果")
    print("=" * 70)
    
    print(f"\n已知起点: ({start_x:.3f}, {start_y:.3f})")
    print(f"已知终点: ({end_x:.3f}, {end_y:.3f})")
    print(f"导线总长: {closure['total_distance']:.3f} m")
    
    print("\n【角度平差】")
    print(f"角度闭合差: {closure['angle_error']:.6f}°")
    print(f"角度改正数: {closure['angle_correction']:.6f}° (每个转角)")
    
    print("\n【推算坐标】")
    print("-" * 70)
    print(f"{'点号':<8} {'X':<12} {'Y':<12} {'ΔX':<12} {'ΔY':<12} {'边长':<10}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<8} {r['x']:<12.3f} {r['y']:<12.3f} {r['dx']:<12.3f} {r['dy']:<12.3f} {r['distance']:<10.3f}")
    
    print("\n【坐标闭合差】")
    print(f"fx = {closure['fx']:.6f} m")
    print(f"fy = {closure['fy']:.6f} m")
    print(f"全长闭合差 f = {closure['f']:.6f} m")
    k_str = f"1/{int(1/closure['k'])}" if closure['k'] > 0 else "∞"
    print(f"相对闭合差 K = {k_str}")
    
    # 精度评定
    print("\n【精度评定】")
    if closure['k'] > 0:
        if closure['k'] <= 1/2000:
            print("✅ 精度评定：合格（K ≤ 1/2000）")
        else:
            print("❌ 精度评定：不合格（K > 1/2000），建议重测")
    else:
        print("✅ 精度评定：完美附和")
    
    print("\n【平差后坐标】")
    print("-" * 70)
    print(f"{'点号':<8} {'平差后X':<12} {'平差后Y':<12} {'Vx':<12} {'Vy':<12}")
    print("-" * 70)
    for r in adjusted_results:
        print(f"{r['name']:<8} {r['adj_x']:<12.3f} {r['adj_y']:<12.3f} {r['vx']:<12.6f} {r['vy']:<12.6f}")
    print("=" * 70)
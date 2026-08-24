from surveying import (
    distance,
    azimuth,
    coordinate_forward,
    coordinate_inverse
)

from data_process import (
    read_points,
    find_point,
    save_results,
    validate_points,
    get_points_stats
)

from visualization import plot_points
from error_handler import input_float
from traverse import (
    read_traverse_data,
    traverse_calculation,
    format_traverse_report,
    adjust_traverse,
    format_adjusted_report,
    save_traverse_report
)

import os


# ==============================
# 文件夹设置
# ==============================

DATA_DIR = "data"
OUTPUT_DIR = "output"


# ==============================
# 公共函数：读取并校验 CSV 文件
# ==============================

def load_points_from_file():
    """让用户输入CSV文件名，读取并校验测量点数据"""
    filename = input("请输入CSV文件名：")
    filepath = os.path.join(DATA_DIR, filename)

    try:
        points = read_points(filepath)
    except FileNotFoundError:
        print("文件不存在！请检查文件名。")
        return None
    except ValueError as error:
        print(f"数据格式错误：{error}")
        return None

    valid, message = validate_points(points)
    if not valid:
        print(f"数据检查失败：{message}")
        return None

    print(f"已读取 {len(points)} 个有效测量点")
    return points


# ==============================
# 主程序
# ==============================

def main():
    while True:
        try:
            print("================================")
            print("       SurveyDataTool")
            print("       测绘数据处理工具")
            print("================================")

            print("1. 两点距离")
            print("2. 方位角")
            print("3. 坐标正算")
            print("4. 坐标反算")
            print("5. 读取测量点数据")
            print("6. 测量点距离及方位角")
            print("7. 批量计算测量点数据")
            print("8. 测量点可视化")
            print("9. 测量点统计")
            print("10. 导线计算")
            print("0. 退出")

            choice = input("请选择功能：")

            # ==============================
            # 0. 退出
            # ==============================
            if choice == "0":
                print("程序结束")
                break

            # ==============================
            # 1. 两点距离
            # ==============================
            elif choice == "1":
                print("你选择了：两点距离")
                x1 = input_float("请输入A点X坐标：")
                y1 = input_float("请输入A点Y坐标：")
                x2 = input_float("请输入B点X坐标：")
                y2 = input_float("请输入B点Y坐标：")
                result = distance(x1, y1, x2, y2)
                print(f"A-B距离：{result:.3f} m")

            # ==============================
            # 2. 方位角
            # ==============================
            elif choice == "2":
                print("你选择了：方位角")
                x1 = input_float("请输入A点X坐标：")
                y1 = input_float("请输入A点Y坐标：")
                x2 = input_float("请输入B点X坐标：")
                y2 = input_float("请输入B点Y坐标：")
                angle = azimuth(x1, y1, x2, y2)
                print(f"A-B方位角：{angle:.3f}°")

            # ==============================
            # 3. 坐标正算
            # ==============================
            elif choice == "3":
                print("你选择了：坐标正算")
                x = input_float("请输入起点X坐标：")
                y = input_float("请输入起点Y坐标：")
                distance_value = input_float("请输入距离：")
                angle = input_float("请输入方位角：")
                x_end, y_end = coordinate_forward(x, y, distance_value, angle)
                print(f"终点X坐标：{x_end:.3f}")
                print(f"终点Y坐标：{y_end:.3f}")

            # ==============================
            # 4. 坐标反算
            # ==============================
            elif choice == "4":
                print("你选择了：坐标反算")
                x1 = input_float("请输入A点X坐标：")
                y1 = input_float("请输入A点Y坐标：")
                x2 = input_float("请输入B点X坐标：")
                y2 = input_float("请输入B点Y坐标：")
                dis, angle = coordinate_inverse(x1, y1, x2, y2)
                print(f"A-B距离：{dis:.3f} m")
                print(f"A-B方位角：{angle:.3f}°")

            # ==============================
            # 5. 读取测量点数据
            # ==============================
            elif choice == "5":
                print("你选择了：读取测量点数据")
                points = load_points_from_file()
                if points is None:
                    continue
                print(f"读取成功！共读取 {len(points)} 个有效测量点：")
                for point in points:
                    print(f"{point['id']}: X={point['x']:.3f}, Y={point['y']:.3f}")

            # ==============================
            # 6. 测量点距离及方位角
            # ==============================
            elif choice == "6":
                print("你选择了：测量点距离与方位角")
                points = load_points_from_file()
                if points is None:
                    continue

                point1_id = input("请输入起点点号：")
                point2_id = input("请输入终点点号：")
                point1 = find_point(points, point1_id)
                point2 = find_point(points, point2_id)

                if point1 is None or point2 is None:
                    print("点号不存在！")
                else:
                    dis = distance(point1["x"], point1["y"], point2["x"], point2["y"])
                    angle = azimuth(point1["x"], point1["y"], point2["x"], point2["y"])
                    print(f"{point1_id}-{point2_id}距离：{dis:.3f} m")
                    print(f"{point1_id}-{point2_id}方位角：{angle:.3f}°")

            # ==============================
            # 7. 批量计算测量点数据
            # ==============================
            elif choice == "7":
                print("你选择了：批量计算测量点数据")
                points = load_points_from_file()
                if points is None:
                    continue

                total_pairs = len(points) - 1
                if total_pairs <= 0:
                    print("错误：至少需要 2 个点才能进行批量计算！")
                    continue

                print(f"\n共有 {total_pairs} 对相邻点需要计算\n")

                results = []
                cumulative_dist = 0

                for i in range(total_pairs):
                    p1 = points[i]
                    p2 = points[i + 1]

                    print(f"正在计算：第 {i+1}/{total_pairs} 对点 ({p1['id']} → {p2['id']})")

                    dis = distance(p1["x"], p1["y"], p2["x"], p2["y"])
                    angle = azimuth(p1["x"], p1["y"], p2["x"], p2["y"])

                    cumulative_dist += dis

                    results.append({
                        "起点": p1["id"],
                        "终点": p2["id"],
                        "距离": round(dis, 3),
                        "方位角": round(angle, 3)
                    })

                print(f"\n✅ 计算完成！")
                print(f"共计算 {len(results)} 对点，累计边长 {cumulative_dist:.3f} m")

                output_file = os.path.join(OUTPUT_DIR, "result.csv")
                save_results(output_file, results, include_cumulative=True)
                print(f"结果已保存：{output_file}")

            # ==============================
            # 8. 测量点可视化
            # ==============================
            elif choice == "8":
                print("你选择了：测量点可视化")
                points = load_points_from_file()
                if points is None:
                    continue

                plot_points(points)
                print("测量点图已保存：survey_points.png")

            # ==============================
            # 9. 测量点统计
            # ==============================
            elif choice == "9":
                print("你选择了：测量点统计")
                points = load_points_from_file()
                if points is None:
                    continue

                stats = get_points_stats(points)
                print("=" * 40)
                print("          测量点统计结果")
                print("=" * 40)
                print(f"点数量：{stats['count']}")
                print(f"X坐标范围：{stats['x_min']:.3f}  ~  {stats['x_max']:.3f}")
                print(f"Y坐标范围：{stats['y_min']:.3f}  ~  {stats['y_max']:.3f}")
                print(f"X坐标平均值：{stats['x_avg']:.3f}")
                print(f"Y坐标平均值：{stats['y_avg']:.3f}")
                print("=" * 40)

            # ==============================
            # 10. 导线计算
            # ==============================
            elif choice == "10":
                print("你选择了：导线计算")
                print("\n请输入导线观测数据文件（CSV格式）")
                print("文件格式：点号, 角(度), 边长(米), 备注")
                print("备注列填写'已知'表示该点为已知点（不参与计算）")
                print()

                filename = input("请输入CSV文件名：")
                filepath = os.path.join(DATA_DIR, filename)

                try:
                    observed_data = read_traverse_data(filepath)
                except FileNotFoundError:
                    print("文件不存在！请检查文件名。")
                    continue
                except ValueError as error:
                    print(f"数据格式错误：{error}")
                    continue
                except KeyError as error:
                    print(f"CSV缺少必需列：{error}")
                    continue

                if not observed_data:
                    print("文件中没有数据！")
                    continue

                print(f"已读取 {len(observed_data)} 条观测数据")

                # 输入起点坐标和起始方位角
                print("\n请输入导线起点信息：")
                start_x = input_float("起点X坐标：")
                start_y = input_float("起点Y坐标：")
                start_azimuth = input_float("起始方位角（度）：")

                # 执行导线计算
                results, closure = traverse_calculation(start_x, start_y, start_azimuth, observed_data)

                # 输出原始结果
                format_traverse_report(results, closure)

                # 执行平差（分配闭合差）
                print("\n是否进行平差计算？")
                print("1. 是（按边长分配闭合差）")
                print("2. 否（仅查看原始结果）")
                adjust_choice = input("请选择：")

                adjusted_results = None
                if adjust_choice == "1":
                    adjusted_results = adjust_traverse(results, closure)
                    format_adjusted_report(adjusted_results, closure)
                else:
                    print("已跳过平差")

                # 询问是否导出报告
                print("\n是否导出计算报告？")
                print("1. 是（保存到 output/ 目录）")
                print("2. 否")
                save_choice = input("请选择：")

                if save_choice == "1":
                    report_path = save_traverse_report(
                        results,
                        closure,
                        adjusted_results,
                        start_x,
                        start_y,
                        start_azimuth
                    )
                    print(f"✅ 报告已保存：{report_path}")
                else:
                    print("已跳过报告导出")

            # ==============================
            # 无效输入
            # ==============================
            else:
                print("请输入正确的功能编号！")

        except Exception as e:
            print(f"程序发生意外错误：{e}")
            print("请重试或联系开发者")
            continue


if __name__ == "__main__":
    main()
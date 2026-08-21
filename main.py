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
    validate_points
    get_points_stats
)

from visualization import plot_points

from error_handler import (
    input_float,
    load_points_from_file
)

import os


# ==============================
# 文件夹设置
# ==============================

DATA_DIR = "data"
OUTPUT_DIR = "output"





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

                results = []
                for i in range(len(points) - 1):
                    p1 = points[i]
                    p2 = points[i + 1]
                    dis = distance(p1["x"], p1["y"], p2["x"], p2["y"])
                    angle = azimuth(p1["x"], p1["y"], p2["x"], p2["y"])
                    results.append({
                        "起点": p1["id"],
                        "终点": p2["id"],
                        "距离": round(dis, 3),
                        "方位角": round(angle, 3)
                    })

                output_file = os.path.join(OUTPUT_DIR, "result.csv")
                save_results(output_file, results)
                print(f"计算完成，结果已保存：{output_file}")



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
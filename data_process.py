import csv
#csv测量数据文件读取

def read_points(filename):
# 读取测量点并把点放进列表
    points = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # 核心代码：读取csv文件并转化成字符串格式

        for row in reader:
            point = {
                "id": row["点号"],
                "x": float(row["X"]),
                "y": float(row["Y"])
            }

            points.append(point)

    return points

def find_point(points,point_id):
# 查找点函数
    for point in points:
        if point["id"] == point_id:
            return point

    return None

#===================待理解===================
def save_results(filename, results):
# 把python里面的数据写入csv
    with open(filename, "w", encoding="utf-8", newline="") as file:
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

#===================待理解===================

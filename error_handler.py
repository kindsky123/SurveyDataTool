# ==============================
# 异常处理 / 输入辅助函数
# ==============================
import os


# ==============================
# 文件夹设置
# ==============================

DATA_DIR = "data"
OUTPUT_DIR = "output"

def input_float(message):
    """让用户输入一个数字，如果输入非法则循环重试"""
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("输入错误！请输入数字。")

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
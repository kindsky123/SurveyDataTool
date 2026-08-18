import matplotlib.pyplot as plt
# 导入绘图库，并起简称

def plot_points(points):
    x = [point["x"] for point in points]
    y = [point["y"] for point in points]
# 提取points里面的坐标
    plt.figure(figsize=(8, 6))
# 创建一个8*6大小的画布
    plt.scatter(x, y)
    plt.plot(x,y)
# 把测量点画出来,并连接
    for point in points:
        plt.annotate(
            point["id"],
            (point["x"], point["y"])
        )
# 标注坐标
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Survey Points")
# 设置轴的名称,标题名称
    plt.grid(True)
# 显示网格

# 保存图片
    plt.savefig(
    "output/survey_points.png",
    dpi=150,
    bbox_inches="tight")


    print("测量点图已保存：output/survey_points.png")

    plt.close()
# 关闭画布
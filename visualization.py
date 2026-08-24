import matplotlib.pyplot as plt


def plot_points(points):
    """
    绘制测量点：
        - 等比例坐标轴
        - 点之间带方向箭头
        - 点号标注偏移
    """
    if not points:
        print("没有数据可绘制！")
        return

    x = [point["x"] for point in points]
    y = [point["y"] for point in points]

    plt.figure(figsize=(8, 6))

    # 绘制散点
    plt.scatter(x, y, color='blue', s=50, zorder=3, label='测量点')

    # 绘制连线带箭头
    for i in range(len(points) - 1):
        x1, y1 = points[i]["x"], points[i]["y"]
        x2, y2 = points[i+1]["x"], points[i+1]["y"]
        dx = x2 - x1
        dy = y2 - y1

        length = (dx**2 + dy**2)**0.5
        if length > 0:
            ratio = 0.85
            arrow_start_x = x1 + dx * (1 - ratio)
            arrow_start_y = y1 + dy * (1 - ratio)
            plt.arrow(
                arrow_start_x, arrow_start_y,
                dx * ratio, dy * ratio,
                head_width=length * 0.05,
                head_length=length * 0.08,
                fc='red', ec='red',
                length_includes_head=True,
                zorder=2,
                label='导线方向' if i == 0 else ""
            )

    # 计算平均坐标用于标注偏移方向
    avg_x = sum(x) / len(x)
    avg_y = sum(y) / len(y)

    for point in points:
        # 根据点相对于中心的位置决定标注偏移方向
        offset_x = 0.8 if point["x"] < avg_x else -0.8
        offset_y = 0.8 if point["y"] < avg_y else -0.8

        plt.annotate(
            point["id"],
            (point["x"], point["y"]),
            xytext=(offset_x, offset_y),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold'
        )

    # 等比例坐标轴
    plt.axis('equal')

    # 标签和网格
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Survey Points")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # 保存图片
    plt.savefig(
        "output/survey_points.png",
        dpi=150,
        bbox_inches="tight"
    )

    print("测量点图已保存：output/survey_points.png")

    plt.close()
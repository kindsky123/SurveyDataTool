from surveying import distance,azimuth,coordinate_forward,coordinate_inverse


while True:
    print("================================")
    print("       SurveyDataTool")
    print("       测绘数据处理工具")
    print("================================")
    print("1. 两点距离")
    print("2. 方位角")
    print("3. 坐标正算")
    print("4. 坐标反算")
    print("0. 退出")

    choice = input("请选择功能：")

    if choice == "0":
        print("程序结束")
        break

    if choice == "1":
        print("你选择了：两点距离")

        x1 = float(input("请输入A点X坐标："))
        y1 = float(input("请输入A点Y坐标："))
        x2 = float(input("请输入B点X坐标："))
        y2 = float(input("请输入B点Y坐标："))

        result = distance(x1, y1, x2, y2)

        print(f"A-B距离：{result:.3f} m")

    if choice == "2":
        print("你选择了：方位角")

        x1 = float(input("请输入A点X坐标："))
        y1 = float(input("请输入A点Y坐标："))
        x2 = float(input("请输入B点X坐标："))
        y2 = float(input("请输入B点Y坐标："))

        angle = azimuth(x1,y1,x2,y2)

        print(f"A-B方位角：{angle:.3f}°")

    if choice == "3":
        print("你选择了：坐标正算")

        x = float(input("请输入起点X坐标："))
        y = float(input("请输入起点Y坐标："))
        distance_value = float(input("请输入距离："))
        angle = float(input("请输入方位角："))

        x_end, y_end = coordinate_forward(x, y, distance_value, angle)

        print(f"终点X坐标：{x_end:.3f}")
        print(f"终点Y坐标：{y_end:.3f}")

    if choice == "4":
        print("你选择了：坐标反算")

        x1 = float(input("请输入A点X坐标："))
        y1 = float(input("请输入A点Y坐标："))
        x2 = float(input("请输入B点X坐标："))
        y2 = float(input("请输入B点Y坐标："))

        dis, angle = coordinate_inverse(x1, y1, x2, y2)

        print(f"A-B距离：{dis:.3f} m")
        print(f"A-B方位角：{angle:.3f}°")

    if choice not in ["0", "1", "2", "3", "4"]:
        print("请输入正确的功能编号！")
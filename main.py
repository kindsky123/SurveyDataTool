from surveying import distance,azimuth,coordinate_forward

x1=float(input("请输入A点x坐标："))
y1=float(input("请输入A点y坐标："))

x2=float(input("请输入B点x坐标："))
y2=float(input("请输入B点y坐标："))

result=distance(x1,y1,x2,y2)
angle=azimuth(x1,y1,x2,y2)

x_end, y_end = coordinate_forward(x1, y1, 50, 53.130102)

print(f"正算结果：X={x_end:.3f}, Y={y_end:.3f}")

print(f"A-B距离:{result:.3f} m")
print(f"A-B方位角:{angle:.3f} °")
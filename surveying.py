import math

def distance(x1,y1,x2,y2):
    #功能1：计算两点之间的距离
    dx=x2-x1
    dy=y2-y1
    dis=math.sqrt(dx**2+dy**2)

    return dis

def azimuth(x1,y1,x2,y2):
    #功能2：计算坐标方位角
    dx=x2-x1
    dy=y2-y1

    angle=math.atan2(dy,dx)

    angle=math.degrees(angle) 
    #弧度转角度
    if angle<0:
        angle+=360

    return angle

def coordinate_forward(x,y,distance,angle):
    #坐标正算-计算坐标增量
    ang_rad=math.radians(angle)
    #弧度转角度
    dx=distance*math.cos(ang_rad)
    dy=distance*math.sin(ang_rad)
    x_end=x+dx
    y_end=y+dy

    return x_end,y_end
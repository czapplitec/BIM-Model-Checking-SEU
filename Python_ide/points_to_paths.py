import numpy as np
from basic_geometry import Point, Line

Inf = float('Inf')
APPROXIMATION_OF_POINT = 10000
a = len(str(APPROXIMATION_OF_POINT))


########################################################################################################################
########################################################################################################################
def approximation_of_a_real_number(amy):
    """
    约等于的算法。
    只需要用在建立Point的步骤即可（此处备用）
    """
    return int(amy * APPROXIMATION_OF_POINT) / APPROXIMATION_OF_POINT


########################################################################################################################
########################################################################################################################
def dijkstra(adj, src, dst, n):
    """
    求距离的算法（必须在排除出界之后才可以使用）
        adj是二维数组
        src是起始点的index
        dst是结束点的index
        n是点的个数
    返回：
        距离值dist[dst]
        过程点index集合drawing_preparation
    """
    dist = [Inf] * n
    dist[src] = 0
    book = [0] * n  # 记录已经确定的顶点
    # 每次找到起点到该点的最短途径
    u = src
    drawing_preparation = []
    for i in range(n - 1):  # 找n-1次
        book[u] = 1  # 已经确定
        # 更新距离并记录最小距离的结点
        next_u, minVal = 0, float('inf')
        for v in range(n):  # w
            w = adj[u][v]
            if w == Inf:  # 结点u和v之间没有边
                continue
            if not book[v] and dist[u] + w < dist[v]:  # 判断结点是否已经确定了，
                dist[v] = dist[u] + w
                if dist[v] < minVal:
                    next_u, minVal = v, dist[v]
        # 开始下一轮遍历
        drawing_preparation.append(u)
        u = next_u
    drawing_preparation.append(dst)
    return dist[dst], drawing_preparation


########################################################################################################################
########################################################################################################################
def line_check(frontier_line_list, list_of_points, path):
    """
    下面是判断直线是否出界的算法：
    1.path和frontier有公共点，要么交叉，要么重合
        1.1. path和frontier交叉的话，在端点则不出界，反之出界
        1.2. path和frontier重合的话，frontier>=path则不出界，反之出界
    2.path和frontier无公共点，则对任意一个端点调用point_check_poly（实际上很难出现这种情况）
        2.1.若点在poly外，则出界
        2.2.反之则不出界
    """
    outcome = False
    path_line = path.turn_it_to_a_line()
    for frontier in frontier_line_list:
        if not path_line == frontier:
            crossed, overlapped = Line.cross_check(frontier, path_line)
            if crossed and not overlapped:
                outcome = True
            else:
                mid_point = Point((path_line.s1.x + path_line.s2.x) / 2, (path_line.s1.y + path_line.s2.y) / 2,
                                  path_line.s1.z)
                outcome = point_check_polygon(mid_point, list_of_points)
    return outcome


########################################################################################################################
########################################################################################################################
def point_check_polygon(p, poly):
    """
    以下是判断点是否在多边形内的算法
    输入p（Point）和poly（多边形，用有顺序的点表示）
    返回四种情况：在内部/在外部/在边线上（端点外）/与端点重合
    """
    px = p.x
    py = p.y
    flag = False
    i = 0
    l = len(poly)
    j = l - 1
    while i < l:
        sx = poly[i].x
        sy = poly[i].y
        tx = poly[j].x
        ty = poly[j].y
        # 点与多边形顶点重合
        if (sx == px and sy == py) or (tx == px and ty == py):
            return px, py
        # 判断线段两端点是否在射线两侧
        if (sy < py & ty >= py) | (sy >= py & ty < py):
            # 线段上与射线 Y 坐标相同的点的 X 坐标
            x = sx + (py - sy) * (tx - sx) / (ty - sy)
            # 点在多边形的边上
            if x == px:
                return px, py
            # 射线穿过多边形的边界
            if x > px:
                flag = not flag
        j = i
        i += 1
    # 射线穿过多边形边界的次数为奇数时点在多边形内
    judge = (px, py) if flag else 'out'
    if not judge == 'out':
        return False
    else:
        return True


########################################################################################################################
########################################################################################################################
def bounding_box(list_of_points):
    """
    求中心点的算法。
    list_of_points是二维点的集合
    返回其中心点
    【疑问：有时list_of_points为空集，目前解决手段是返回指定点0，0；但是据图来看，没有这样的问题】
    【疑问：目前位置不准】
    """
    if not list_of_points:
        return Point(0, 0)
    else:
        p = list_of_points[0]
        minimal_point = Point(p.x, p.y)
        maximal_point = Point(p.x, p.y)
        for anypoint in list_of_points:
            minx = minimal_point.x
            maxx = maximal_point.x
            miny = minimal_point.y
            maxy = maximal_point.y
            px = anypoint.x
            py = anypoint.y
            if px <= minx:
                minimal_point = Point(px, miny)
            if py <= miny:
                minimal_point = Point(minx, py)
            if px >= maxx:
                maximal_point = Point(px, maxy)
            if py >= maxy:
                maximal_point = Point(maxx, py)

        return Point((maxx + minx) / 2, (maxy + miny) / 2)



# 这个函数用来输出矩阵中的第n大的值，用于dijkstra算法。因为最大值是inf，所以最大逃生距离是第二大的值
def find_sub_max(arr, n):
    z = arr
    for i in range(n - 1):
        arr_ = arr
        arr_[np.argmax(arr_)] = np.min(arr)
        arr = arr_
    return np.max(arr_), z.index(np.max(arr_))

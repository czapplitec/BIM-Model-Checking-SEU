from __future__ import division
from basic_geometry import Point, Line
import numpy as np
import math

Inf = float('Inf')
APPROXIMATION_OF_POINT = 10000
a = len(str(APPROXIMATION_OF_POINT))
APPROXIMATION = 1000
o_factor = 1 / 500


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
def dijkstra(graph, starting, ending, n):  # starting为源点，ending为终点
    dist = [[] for i in range(n)]  # 存储源点到每一个终点的最短路径的长度
    pata = [[] for i in range(n)]  # 存储每一条最短路径中倒数第二个顶点的下标
    flag = [[] for i in range(n)]  # 记录每一个顶点是否求得最短路径
    index = 0
    # 初始化
    while index < n:
        dist[index] = graph[starting][index]
        flag[index] = 0
        if graph[starting][index] < Inf:  # 正无穷
            pata[index] = starting
        else:
            pata[index] = -1  # 表示从顶点starting到index无路径
        index += 1
    flag[starting] = 1
    pata[starting] = 0
    dist[starting] = 0
    index = 1
    while index < n:
        Mindist = Inf
        j = 0
        while j < n:
            if flag[j] == 0 and dist[j] < Mindist:
                # 如果j还没确定，而且到j的距离更短
                t_index = j  # t_index为目前从V-S集合中找出的距离源点starting最断路径的顶点
                Mindist = dist[j]
            j += 1
        flag[t_index] = 1
        ending_index = 0
        Mindist = Inf  # 表示无穷大，若两点间的距离小于Mindist说明两点间有路径
        # 更新dist列表，符合思想中第三条
        while ending_index < n:
            if flag[ending_index] == 0:
                if graph[t_index][ending_index] < Mindist and dist[
                    t_index] + graph[t_index][ending_index] < dist[ending_index]:
                    dist[ending_index] = dist[t_index] + graph[t_index][ending_index]
                    pata[ending_index] = t_index
            ending_index += 1
        index += 1
    vertex_endnode_path = []  # 存储从源点到终点的最短路径
    return dist[ending], start_end_pata(pata, starting, ending, vertex_endnode_path)


# 根据本文上述定义的pata递归求路径
def start_end_pata(pata, start, endnode, path):
    if start == endnode:
        path.append(start)
    else:
        path.append(endnode)
        start_end_pata(pata, start, pata[endnode], path)
    return path


########################################################################################################################
########################################################################################################################
def line_check(frontier_line_list, path):
    from basic_geometry import Line
    # 【3月6日】能有别的也叫Line，所以不得不在此处新引用
    """
    下面是判断直线是否出界的算法：
    1.path和frontier有公共点，要么交叉，要么重合
        1.1. path和frontier交叉的话，在端点则不出界，反之出界
        1.2. path和frontier重合的话，frontier>=path则不出界，反之出界
    2.path和frontier无公共点，则对任意一个端点调用point_check_poly（实际上很难出现这种情况）
        2.1.若点在poly外，则出界
        2.2.反之则不出界
    """
    for frontier in frontier_line_list:
        if Line.line_check_cross(frontier, path) == "[CROSSED]: not on edge":
            print("  ")
            print("situation 1")
            print(path)
            print(frontier)

            return True
    mid_point = Point((path.start.x + path.end.x) / 2, (path.start.y + path.end.y) / 2)
    outcome = point_check_polygon(mid_point, frontier_line_list)
    # if outcome:
    #     print("  ")
    #     print("line_check mid_point out")
    #     print(path)
    #     print(mid_point)

    return point_check_polygon(mid_point, frontier_line_list)


########################################################################################################################
########################################################################################################################
def point_check_polygon(p, frontier_line_list):
    """
    以下是判断点是否在多边形内的算法
    输入p（Point）和poly（多边形，用有顺序的点表示）
    返回四种情况：在内部/在外部/在边线上（端点外）/与端点重合
    """
    px = float(p.x)
    py = float(p.y)
    flag = True
    i = 0
    l = len(frontier_line_list)
    while i < l:
        sx = frontier_line_list[i].start.x
        sy = frontier_line_list[i].start.y
        tx = frontier_line_list[i].end.x
        ty = frontier_line_list[i].end.y
        if ty > py > sy or sy > py > ty:
            # 若论纵坐标，p在s和t中间 则作一条水平向右的射线，有可能相交。
            # x就是射线的直线与st直线的交点
            # 如果x在px右边则记为有交点
            # 有奇数个交点时在内部（False）
            # 也就是，每有一次交点，就变换一次flag。0次是在外部，因此是True
            x = sx + (ty - sy) * (tx - sx) / (py - sy)
            if x >= px - o_factor:
                # 这个交点的横坐标只有大于px才说明p在内部，等于则说明在边界上。考虑到p是中点，所以直接算出界
                # 【3月9日】 中点一定会在自己这条线上，因此为简便起见，直接加上大于等于
                # 【3月10日】 左上角的Bedroom 2左边线有点问题，加一个o_factor冗余度
                flag = not flag
        i += 1
    i = 0
    while i < l:
        sx = frontier_line_list[i].start.x
        sy = frontier_line_list[i].start.y
        tx = frontier_line_list[i].end.x
        ty = frontier_line_list[i].end.y
        if math.isclose(sy, py, rel_tol=o_factor) & math.isclose(ty, py, rel_tol=o_factor):
            if sx <= px <= tx or tx <= px <= sx:
                flag = False
        i += 1
    i = 0
    while i < l:
        sx = frontier_line_list[i].start.x
        sy = frontier_line_list[i].start.y
        tx = frontier_line_list[i].end.x
        ty = frontier_line_list[i].end.y
        if math.isclose(sx, px, rel_tol=o_factor) & math.isclose(tx, px, rel_tol=o_factor):
            if sx <= px <= tx or tx <= px <= sx:
                flag = False
        i += 1
    # 射线穿过多边形边界的次数为奇数时点在多边形内
    return flag


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
    for i in range(n - 1):
        arr_ = arr
        arr_[np.argmax(arr_)] = np.min(arr)
        # 把最大的换成最小值。n=1时不换，n=2时换一次
        arr = arr_
    z = arr
    return np.max(arr), z.index(np.max(arr))

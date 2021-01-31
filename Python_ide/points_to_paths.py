import numpy as np
from basic_geometry import Path, Line, Point, Edge, Vector, Triangle, BoundingBox, Space
import ifcopenshell
from ifcopenshell import geom

settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
Inf = float('Inf')

'''
对于多个destination求解的办法：（原则：dijkstra只能采用一个destination和一个起点，所以对于一个destination要先在房间的各个frontier循环）
1.将space和space.list_of_destination输入get_paths
2.判断destination个数，并依次运算
3.每次运算要返回drawing_list和exit_distance，每个drawing_list对应的list_of_point是不同的
4.求最短的exit_distance，拿着这个destination再去算一次dijkstra
5.get_paths返回这一次的结果，主程序要再把destination给append进去才能正确绘制。

寻找路径的步骤：
1.输入 list_of_points destination 
2.将 destination 加入之后， 单循环生成 path_line_list
3.对每一个 path 循环，排除所有出界项
4.把剩下的 path 转化成长度，用二维数组或矩阵表示
5.输出矩阵进行dijkstra运算

get_exit_distance是对一个space的函数，允许有多个destination
get_paths_of_certain_destination是对一个space和其中一个特定destination的函数
dijkstra是求路径函数
'''


def get_exit_distance(space):
    destination_list = space.destination_list
    distance_of_every_destination = []
    for destination in destination_list:
        exit_distance_of_this_destination, drawing_list_of_the_destination = get_paths_of_certain_destination(space,
                                                                                                              destination)
        distance_of_every_destination.append(exit_distance_of_this_destination)
        drawing_list = drawing_list_of_the_destination
    exit_distance = find_sub_max(distance_of_every_destination, 2)
    real_destination = destination_list[0]
    for destination in destination_list:
        exit_distance_of_this_destination, drawing_list_of_the_destination = get_paths_of_certain_destination(space,
                                                                                                              destination)
        if exit_distance_of_this_destination == exit_distance:
            real_destination = destination
            drawing_list = drawing_list_of_the_destination
    return exit_distance, drawing_list, real_destination


def get_paths_of_certain_destination(space, destination):
    list_of_points = space.point_list
    frontier_line_list = set()
    path_line_list = set()
    for p1 in list_of_points:
        path_line_list.add(Line(destination, p1))
        for p2 in list_of_points:
            if not p1 == p2:
                path_line_list.add(Line(p1, p2))
    path_line_list_duplicated = []
    for pl1 in path_line_list:
        for pl2 in path_line_list:
            if not pl1 == pl2:
                if pl1.s1 == pl2.s2 and pl1.s2 == pl2.s1:
                    path_line_list_duplicated.append(pl2)
    for dp in path_line_list.copy():
        if dp in path_line_list.copy():
            path_line_list.remove(dp)
    # 除重，未排除出界项
    for i in range(0, len(list_of_points) - 1):
        frontier_line_list.add(Line(list_of_points[i], list_of_points[i + 1]))
    frontier_line_list.add(Line(list_of_points[0], list_of_points[len(list_of_points) - 1]))
    # 用point_list来输出frontier_line_list
    # 下一步输出Dijkstra算法需要的矩阵
    new_lop = list_of_points
    new_lop.append(destination)
    # list_of_points就是space.point_list,new_lop是加上destination之后的，用于dijkstra运算。new_lop不能包含边界信息，因为顺序是乱的。
    # 边界信息用frontier_line_list来表示
    q = len(new_lop)
    matrix_for_all = np.zeros(shape=(q, q))
    i = 0
    for p1 in new_lop:
        list_for_this_point = []
        for p2 in new_lop:
            path_trial = Path(p1, p2)
            if p1 == p2:
                list_for_this_point.append(0)
                # 如果点重合，即代表距离是0
            else:
                outcome = line_check(frontier_line_list, new_lop, path_trial)
                # 如果path与frontier相交，且交点不是端点，则出界
                # 否则，就是path完全在内部或外部的情况，此时用点来检测（都包含在line_check内部）
                # 出界则outcome=True
                if not outcome:
                    list_for_this_point.append(path_trial.length)
                else:
                    list_for_this_point.append(Inf)
                    # 出界，则两点距离为无限大
        matrix_for_all[i] = list_for_this_point
        i += 1
        # i 是点在new_lop的index
    distance_of_single_destination = []
    for i in range(len(new_lop)):
        exit_distance_of_any_frontier, drawing_list_of_any_frontier = dijkstra(matrix_for_all, i,
                                                                               len(new_lop) - 1, len(new_lop))
        distance_of_single_destination.append(exit_distance_of_any_frontier)
        drawing_list_of_this_destination = drawing_list_of_any_frontier
    exit_distance_of_this_destination = find_sub_max(
        distance_of_single_destination, 2)
    # 求出距离最大的一个

    for i in range(len(new_lop)):
        exit_distance_of_any_frontier, drawing_list_of_any_frontier = dijkstra(matrix_for_all, i,
                                                                               len(new_lop) - 1, len(new_lop))
        if exit_distance_of_any_frontier == exit_distance_of_this_destination:
            drawing_list_of_this_destination = drawing_list_of_any_frontier
    return exit_distance_of_this_destination, drawing_list_of_this_destination


"""
dist为起点->每个结点的距离的列表。（所以起点要赋值为0:dist[src] = 0）
book的作用是记录已经确定了最短距离的结点的列表。
Src表示起点的编号，Dst表示终点的编号，N表示结点个数.
"""


def dijkstra(adj, src, dst, n):
    dist = [Inf] * n
    dist[src] = 0
    book = [0] * n  # 记录已经确定的顶点
    # 每次找到起点到该点的最短途径
    u = src
    drawing_list = []
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
        drawing_list.append(u)
        u = next_u
    drawing_list.append(dst)
    return dist[dst], drawing_list


"""
下面是判断出界的算法，分别是线段出界、点出界。出界则outcome=True
线与线相交，若在端点，则 Overlapped=True ,在其他点相交则 crossed=True， 若不相交则均为False
首先判断线段是否与各边界线（除了line_of_destination之外）相交（line_check，cross_check），求Overlapped,crossed，若Overlapped=True，则outcome=True
(crossed包含了Overlapped)
若Overlapped=False，则判断其端点是否在多边形内（point_check)，直接返回outcome
"""


def line_check(frontier_line_list, list_of_points, path):
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
                outcome = point_check(mid_point, list_of_points)
    return outcome


# “判断点是否在多边形内”的算法
# 存在 点在边界上的问题
def point_check(p, poly):
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
            return (px, py)
        # 判断线段两端点是否在射线两侧
        if (sy < py and ty >= py) or (sy >= py and ty < py):
            # 线段上与射线 Y 坐标相同的点的 X 坐标
            x = sx + (py - sy) * (tx - sx) / (ty - sy)
            # 点在多边形的边上
            if x == px:
                return (px, py)
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


def get_plan(space):
    edge_list = []
    line_list = []
    list_of_points = []
    shape = geom.create_shape(settings, space)
    verts = shape.geometry.verts
    faces = shape.geometry.faces
    bottom_triangles = []
    for i in range(0, len(faces) - 1, 3):
        p1 = Point(verts[3 * faces[i] + 0], verts[3 * faces[i] + 1],
                   verts[3 * faces[i] + 2])
        p2 = Point(verts[3 * faces[i + 1] + 0], verts[3 * faces[i + 1] + 1],
                   verts[3 * faces[i + 1] + 2])
        p3 = Point(verts[3 * faces[i + 2] + 0], verts[3 * faces[i + 2] + 1],
                   verts[3 * faces[i + 2] + 2])
        triangle = Triangle(p1, p2, p3)
        nv = Vector.cross(triangle.e1.vector, triangle.e2.vector)
        ref = Vector(0, 0, -1)
        if Vector.equals(ref, nv.normalize()):
            bottom_triangles.append(triangle)
            edge_list.append(triangle.e1)
            edge_list.append(triangle.e2)
            edge_list.append(triangle.e3)
    # 除重环节
    duplicated_edges = set()
    for edge in edge_list:
        for e in edge_list:
            if Edge.negative(edge, e):
                duplicated_edges.add(edge)
                duplicated_edges.add(e)
    for edge in duplicated_edges:
        for e in edge_list:
            if Edge.duplicated(edge, e) or Edge.negative(edge, e):
                edge_list.remove(e)
    for edge in edge_list:
        line_list.append(edge.turn_it_to_a_line)
        list_of_points.append(edge.s1)
        # 确认边清理完毕后，点列即为“每个边的端点”，此处取起点
    for anything in list_of_points:
        if anything is None:
            print("None! in list_of_points")
    for anything in line_list:
        if anything is None:
            print("None! in line_list")
    for anything in edge_list:
        if anything is None:
            print("None! in edge_list")
    return edge_list, line_list, list_of_points


def door_to_destination(door):
    shape = geom.create_shape(settings, door)
    verts = shape.geometry.verts
    faces = shape.geometry.faces
    bottom_triangles = []
    points = []
    for i in range(0, len(verts) - 1, 3):
        point = Point(verts[i], verts[i + 1], verts[i + 2])
        points.append(point)
    bb = BoundingBox(points)
    des = bb.destination
    return des


def overkill(space1, space2):
    space2_origin = space2
    removal = False
    if not space1 == space2:
        for frontier1 in space1.edge_list:
            for frontier2 in space2.edge_list:
                new_frontier = Line.overkill(frontier1, frontier2)
                if not new_frontier == None:
                    space1.edge_list.append(new_frontier)
        if not space2 == space2_origin:
            removal = True
            space1.point_list = []
            for frontier in space1.edge_list:
                space1.point_list.append(frontier.s1)
    return removal, space1, space2


# 除重算法，space1,space2 是房间，removal是“要不要去掉space2
# 目前还没用上


def find_sub_max(arr, n):
    z = arr
    for i in range(n - 1):
        arr_ = arr
        arr_[np.argmax(arr_)] = np.min(arr)
        arr = arr_
    return np.max(arr_)  # ,   z.index(np.max(arr_))
# 这个函数用来输出矩阵中的第n大的值，用于dijkstra算法之后
# 因为最大值是inf，所以最大逃生距离是第二大的值

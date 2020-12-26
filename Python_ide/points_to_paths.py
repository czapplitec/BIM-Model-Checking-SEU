import numpy as np
from basic_geometry import Path, Line, Point, Edge, Vector, Triangle, BoundingBox

Inf = float('Inf')


# 这个函数用来输出矩阵中的第n大的值，用于dijkstra算法。因为最大值是inf，所以最大逃生距离是第二大的值
def find_sub_max(arr, n):
    z = arr
    for i in range(n - 1):
        arr_ = arr
        arr_[np.argmax(arr_)] = np.min(arr)
        arr = arr_
    return np.max(arr_), z.index(np.max(arr_))


# “判断点是否在多边形内”的算法
def rs(p, poly):
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


def get_pathes(list_of_points, destination):
    frontier_line_list = set()
    path_line_list = set()
    number_of_frontier = len(list_of_points)
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
    # print(len(list_of_points))
    # print("!!!")
    # print(len(path_line_list))
    # print("???")

    for i in range(0, number_of_frontier - 1):
        frontier_line_list.add(Line(list_of_points[i], list_of_points[i + 1]))
    frontier_line_list.add(Line(list_of_points[0], list_of_points[number_of_frontier - 1]))
    # 下一步输出Dijkstra算法需要的矩阵
    list_of_points.append(destination)
    q = len(list_of_points)
    matrix_for_all = np.zeros(shape=(q, q))
    i = 0
    for p1 in list_of_points:
        list_for_this_point = []
        for p2 in list_of_points:
            path_trial = Path(p1, p2)
            if p1 == p2:
                list_for_this_point.append(0)
            else:
                if not checkit_and_turn(frontier_line_list, list_of_points, path_trial):
                    list_for_this_point.append(path_trial.length)
                else:
                    list_for_this_point.append(Inf)
        matrix_for_all[i] = list_for_this_point
        i += 1
    distance_of_all = []
    for i in range(len(list_of_points)):
        d, dl = dijkstra(matrix_for_all, i, len(list_of_points) - 1, len(list_of_points))
        # 此时的drawing_list并不一定是需要的路径，它只是按顺序的最后一条
        distance_of_all.append(d)
        answer, answer_index = find_sub_max(distance_of_all, 2)
        d, drawing_list = dijkstra(matrix_for_all, answer_index, len(list_of_points) - 1, len(list_of_points))
    return answer, drawing_list, list_of_points


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


"""
# 下面是判断直线是否出界的算法。
# 如果交叉的话则必出界
# 如果重叠的话（前面已经排除完全重合）则必出界
# 只有“在端点交叉”和“完全重合”是“不出界”
# 还有一种情况未检测，这种情况下，检测该path的中点是否在多边形内部即可
"""


def checkit_and_turn(frontier_line_list, list_of_points, path):
    outcome = True
    path_line = path.turn_it_to_a_line()
    for frontier in frontier_line_list:
        if not path_line == frontier:
            Crossed, Overlapped = Line.check_and_turn(frontier, path_line)
            if Crossed or Overlapped:
                outcome = True
    if outcome:
        mid_point = Point((path_line.s1.x + path_line.s2.x) / 2, (path_line.s1.y + path_line.s2.y) / 2, path_line.s1.z)
        outcome = rs(mid_point, list_of_points)
    return Crossed

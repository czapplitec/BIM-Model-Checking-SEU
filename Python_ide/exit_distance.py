import sys
import numpy as np
import time
import ifcopenshell
from ifcopenshell import geom
import os.path
from matplotlib import pyplot as plt
from basic_geometry import Point, Line, Space, Door
from points_to_paths import dijkstra, point_check_polygon, line_check, find_sub_max

model = ifcopenshell.open(os.path.dirname(__file__) + '/ifc/Duplex_A_20110505.ifc')
Inf = float('Inf')
settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
plt.figure(figsize=(100, 100))
"""
【3月11日】
1.已能正确显示逃生路径和逃生距离
2.不能正确显示foyer和hallway，怀疑是ifcopenshell类引用问题
3.已将各对象注释完毕
4.二楼的一些房间有多余的点，在调试overkill的时候没有出现，不影响求距离
"""
########################################################################################################################
########################################################################################################################
for ira in model.by_type("IfcRelAggregates"):
    """
    本循环建立于"IfcRelAggregates"，目的在于建立房间的平面信息（具体方法在类定义里面）
    space_bigger可能是层，spaces_smaller可能是房间
    localtime title是图里的标题
    """
    space_bigger = ira.RelatingObject
    spaces_smaller = ira.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        fig, ax = plt.subplots(figsize=(40, 40))
        plt.axis("equal")
        localtime = time.asctime(time.localtime(time.time()))
        title = space_bigger.Name + str(localtime)
        ax.set_title(title, fontsize=128)
        spaces = []
        for space_smaller in spaces_smaller:
            if space_smaller.is_a("IfcSpace"):
                spaces.append(space_smaller)
        for space in spaces:
            ############################################################################################################
            ############################################################################################################
            """
            子循环，包含了：
                1.平面生成、创建每个房间的基本属性对象(edge point destination)
                2.作图
            【特别注意】：
            space是自动生成的对象 sic（space in class是其用Space类描述的形式）
            因为都在for space in spaces循环里面，所以不存在space对应不同的sic互相覆盖的问题
            """
            sic = Space(space_bigger.Name, space.GlobalId, space.LongName, space)
            # 这一步输入了space在ifc文件中能找到的信息。edge_list，point_list都是已经过overkill的版本
            edge_list = sic.edge_list
            # 边界
            point_list = sic.point_list
            # 所有点
            destination_list_original = []
            # 1.平面生成、创建每个房间的基本属性对象(edge point destination)
            ax.annotate(sic.space_longname + ":" + str(len(sic.point_list)),
                        xy=(sic.tag_of_space.x, sic.tag_of_space.y), fontsize=72)
            # ax.scatter(sic.tag_of_space.x, sic.tag_of_space.y, color='green', s=200, alpha=0.5)
            for edge in edge_list:
                ax.plot([edge.start.x, edge.end.x], [edge.start.y, edge.end.y], linewidth=4, color='black', alpha=0.3)
                # 画边线
                ax.scatter(edge.start.x, edge.start.y, color='red', s=25, alpha=0.5)
                # 画各个起点
                ax.scatter(edge.end.x, edge.end.y, color='blue', s=50, alpha=0.5)
                # 画各个终点（颜色略有不同，可以看出线的方向
            for point in point_list:
                ax.scatter(point.x, point.y, color='red', s=25, alpha=0.5)
                ax.annotate(str(point_list.index(point)) + str(point),
                            xy=(point.x, point.y), fontsize=16)
            # 2.作图
            ############################################################################################################
            ############################################################################################################
            if point_list:
                # 没有点的房间不参与循环，防止foyer和hallway报错
                for IfcRelSpaceBoundary in model.by_type("IfcRelSpaceBoundary"):
                    """
                    本循环建立于"IfcRelSpaceBoundary"，主要负责由门到Destination的转化（包括投影）
                    一个IfcRelSpaceBoundary对应一个space，一个IfcRelSpaceBoundary对应一个IfcBuildingElement
                    本循环包括了：
                        3.找门
                        4.求投影：首先对edge循环，然后找最近的 然后用line内置方法
                        5.求距离：（对destination_list循环，然后找最近的）
                            （1）：排除出界量
                            （2）：转换为二维数组
                            （3）：进入dijkstra算法
                    特别注意：edge是line对象
                    """
                    space_to_judge = IfcRelSpaceBoundary.RelatingSpace
                    element_to_judge = IfcRelSpaceBoundary.RelatedBuildingElement
                    if space_to_judge == space:
                        # destination_list_original是一个房间所有门的逃生距离
                        if element_to_judge is not None:
                            if element_to_judge.is_a("IfcDoor"):
                                element_to_judge = Door(space, element_to_judge.GlobalId, element_to_judge)
                                des = element_to_judge.destination
                                # des是门的bounding box点
                                # 3.找门
                                distance_list_for_each_destination = []
                                # distance_list_for_each_destination是一个门到所有角点的距离
                                for edge in edge_list:
                                    edge_distance = Line.line_get_point_distance(edge, des)
                                    distance_list_for_each_destination.append(edge_distance)
                                for item in distance_list_for_each_destination:
                                    if item is None:
                                        distance_list_for_each_destination.remove(item)
                                        # 去掉所有None，因为min函数不能求None和float的大小值
                                projection_distance = min(distance_list_for_each_destination)
                                for edge in edge_list:
                                    edge_distance = Line.line_get_point_distance(edge, des)
                                    if edge_distance == projection_distance:
                                        line_of_destination = edge
                                        projection_of_des = Line.line_get_foot(line_of_destination, des)
                                        if projection_of_des:
                                            # 若点可求，则打印为粉红色
                                            ax.scatter(projection_of_des.x, projection_of_des.y, color='pink',
                                                       s=200,
                                                       alpha=0.8)
                                            ax.annotate(str(projection_of_des),
                                                        xy=(projection_of_des.x, projection_of_des.y), fontsize=16)
                                            destination_list_original.append(projection_of_des)
                                        else:
                                            pass
                                else:
                                    pass
            else:
                # print("(This is the terminal)")
                pass
            ############################################################################################################
            ############################################################################################################
            sic.destination_list = destination_list_original
            exit_distance_list = []
            # 4.求投影
            for d1 in destination_list_original:
                for d2 in destination_list_original:
                    if d1 != d2:
                        if d1 != 0 and d2 != 0:
                            if Point.point_check_overlap(d1, d2):
                                i = destination_list_original.index(d2)
                                destination_list_original[i] = 0
            while 0 in destination_list_original:
                destination_list_original.remove(0)
            # destination_list_original除重
            # print(sic)
            if destination_list_original:
                for destination in destination_list_original:
                    # destination = destination_list_original[i]
                    # print("new destination" + str(destination))
                    """
                    求距离的循环，因为存在一个房间多个门的情况，必须首先对des循环
                    本循环包含了：
                        5.求距离：（对destination_list循环，然后找最近的）
                            5.1：排除出界量
                                5.1.1：建立基本属性对象
                                5.1.2：路径除重
                                5.1.3：排除出界
                            5.2：转换为二维数组
                            5.3：开始循环，进入dijkstra算法
                    """
                    list_of_point = sic.point_list
                    # list_of_point是点列（边界点——（不包含destination））
                    frontier_line_list = sic.edge_list
                    # frontier_line_list是所有边界的集合
                    path_line_list = []
                    # path_line_list是所有路径的集合
                    n = len(sic.point_list)
                    # 5.1.1：建立基本属性对象list_of_point点 frontier_line_list边界 path_line_list路径 n是个数
                    ########################################################################################
                    ########################################################################################
                    for p1 in list_of_point:
                        # print(list_of_point.index(p1))
                        # print(p1)
                        path_line_list.append(Line(destination, p1))
                        for p2 in list_of_point:
                            if not p1 == p2:
                                path_line_list.append(Line(p1, p2))
                                # 所有的路径
                    for pl1 in path_line_list:
                        for pl2 in path_line_list:
                            if pl1 != 0 and pl2 != 0:
                                if pl1.start == pl2.end and pl1.end == pl2.start:
                                    i = path_line_list.index(pl2)
                                    path_line_list[i] = 0
                    while 0 in path_line_list:
                        path_line_list.remove(0)
                    """for path_original in path_line_list:
                        ax.plot([path_original.start.x, path_original.end.x],
                                [path_original.start.y, path_original.end.y], linewidth=24,
                                color='red', alpha=0.6)"""
                    # 标记一下有哪些路径
                    # 5.1.2：路径除重
                    newlist_of_point = []
                    for p in list_of_point:
                        newlist_of_point.append(p)
                    newlist_of_point.append(destination)
                    """在这里加上了destination，为了drawing_list服务（注意每次只讨论一个destination）
                    凡涉及出界，就用原版，涉及各点求距离，就用新版"""
                    q = len(newlist_of_point)
                    matrix_for_all = np.zeros(shape=(q, q))
                    """print(str(len(path_line_list))+"   path_line_list")
                    print(str(len(frontier_line_list))+"   frontier_line_list")"""
                    # 创造距离表
                    ########################################################################################
                    ########################################################################################
                    for p1 in newlist_of_point:
                        list_for_this_point = []
                        # list_for_this_point是每个边界点到其他点的距离，构成matrix_for_all的q个元素
                        for p2 in newlist_of_point:
                            if p1 == p2:
                                list_for_this_point.append(0)
                            else:
                                path_trial = Line(p1, p2)
                                if not line_check(frontier_line_list, path_trial):
                                    # 特别注意 因为list_of_point_original的点的顺序并不是完全的顺逆时针，所以存在问题。
                                    # 【3月8日】：已解决顺序问题
                                    list_for_this_point.append(path_trial.length)
                                else:
                                    list_for_this_point.append(Inf)
                                    # ax.plot([path_trial.start.x, path_trial.end.x],
                                    #         [path_trial.start.y, path_trial.end.y], linewidth=12,
                                    #         color='red', alpha=0.6)
                        i = newlist_of_point.index(p1)
                        matrix_for_all[i] = list_for_this_point
                    print(matrix_for_all)
                    ########################################################################################
                    ########################################################################################
                    # 5.1.3 排除出界
                    # 5.2 转化为二维数组
                    distance_of_des_to_each_frontier = []
                    for i in range(len(newlist_of_point)):
                        """
                        5.3: 寻找最短路径
                            5.3.1：对每个destination求最短距离
                            5.3.2：找到所有destination最短的路径
                            （特别注意：drawing_list必须搭配append过destination的point_list使用）
                            5.3.3：绘制最短路径
                        """
                        distance_of_any_frontier, drawing_list_of_any_frontier = dijkstra(matrix_for_all, i,
                                                                                          len(list_of_point), q)
                        # 此时的drawing_list并不一定是需要的路径
                        distance_of_des_to_each_frontier.append(distance_of_any_frontier)
                    answer = max(distance_of_des_to_each_frontier)
                    answer_index = distance_of_des_to_each_frontier.index(answer)
                    pre_exit_distance, pre_drawing_list = dijkstra(matrix_for_all, answer_index, len(list_of_point),
                                                                   q)
                    exit_distance_list.append([destination, pre_exit_distance, pre_drawing_list])
                    # 求出本destination的路径
                e_club = []  # 临时集合，用来找出最短路径距离值
                for e in exit_distance_list:
                    e_club.append(e[1])
                e_min = min(e_club)
                sic.exit_distance = e_min
                for e in exit_distance_list:
                    if e[1] == e_min:
                        sic.best_destination = e[0]
                        sic.drawing_list = e[2]
                # print(sic.drawing_list)
                drawing_pre = []
                for p in sic.point_list:
                    drawing_pre.append(p)
                drawing_pre.append(sic.best_destination)
                # 5.3.2：找到所有destination最短的路径 特别注意：drawing_list必须搭配append过destination的point_list使用
                for i in range(len(sic.drawing_list) - 1):
                    start = drawing_pre[sic.drawing_list[i]]
                    end = drawing_pre[sic.drawing_list[i + 1]]
                    ax.plot([start.x, end.x], [start.y, end.y], color='purple', linewidth=12)
            else:
                pass
            print(sic)

    plt.show()

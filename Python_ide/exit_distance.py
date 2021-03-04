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
【3月4日检测】：
1. 一层整体存在偏移问题
2. foyer不能正确显示
3. overkill不能正确返回（每一次都是若l2start在l1上，l2end也在，则l1end和l1start是端点）
4. 后段代码未响应。
5. boundingbox点明显不对
"""
########################################################################################################################
########################################################################################################################
print("TEST START")

print("TEST END")
########################################################################################################################
########################################################################################################################
for ira in model.by_type("IfcRelAggregates"):
    """
    本循环建立于"IfcRelAggregates"，目的在于建立房间的平面信息（具体方法在类定义里面）
    space_bigger可能是层，spaces_smaller可能是房间
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
            """
            子循环，包含了：
                1.平面生成、创建每个房间的基本属性对象(edge point destination)
                2.作图
            【疑问】：FOYER和HALLWAY的点为0
            
            """
            space = Space(space_bigger.Name, space.GlobalId, space.LongName, space)
            # 这一步输入了space在ifc文件中能找到的信息。edge_list，point_list都是已经过overkill的版本
            edge_list = space.edge_list
            point_list = space.point_list
            # 1.平面生成、创建每个房间的基本属性对象(edge point destination)
            ax.annotate(space.space_longname + ":" + str(len(space.point_list)),
                        xy=(space.tag_of_space.x , space.tag_of_space.y ), fontsize=72)
            ax.scatter(space.tag_of_space.x, space.tag_of_space.y, color='green', s=200, alpha=0.5)
            for edge in edge_list:
                ax.plot([edge.start.x, edge.end.x], [edge.start.y, edge.end.y], linewidth=4, color='black', alpha=0.3)
                ax.scatter(edge.start.x, edge.start.y, color='red', s=25, alpha=0.5)
                ax.scatter(edge.end.x, edge.end.y, color='blue', s=50, alpha=0.5)
            """for space in spaces:
                if space.LongName=="Foyer":
                    print("LA")"""
            # for point in point_list:
            #     ax.scatter(point.x, point.y, color='red', s=25, alpha=0.5)
            print(space)
        # plt.show()
        # 2.作图
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
                特别注意：edge也是line对象
                """
                space_to_judge = IfcRelSpaceBoundary.RelatingSpace
                element_to_judge = IfcRelSpaceBoundary.RelatedBuildingElement
                if space_to_judge == space:
                    destination_list_original = []
                    if element_to_judge is not None:
                        if element_to_judge.is_a("IfcDoor"):
                            element_to_judge = Door(space, element_to_judge.GlobalId)
                            des = element_to_judge.destination
                            # 3.找门
                            distance_list_for_each_destination = []
                            for edge in edge_list:
                                edge_distance = edge.line_get_point_distance(des, edge)
                                distance_list_for_each_destination.append(edge_distance)
                            projection_distance = min(distance_list_for_each_destination)
                            for edge in edge_list:
                                edge_distance = edge.line_get_point_distance(des, edge)
                                if edge_distance == projection_distance:
                                    line_of_destination = edge
                                    projection_of_des = line_of_destination.line_get_foot(des)
                                    destination_list_original.append(projection_of_des)
                    space.destination_list = destination_list_original
                    exit_distance_list = []
                    # 4.求投影
                    for destination in space.destination_list:
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
                        list_of_point = space.point_list
                        frontier_line_list = set()
                        path_line_list = set()
                        n = len(list_of_point)
                        # 5.1.1：建立基本属性对象list_of_point点 frontier_line_list边界 path_line_list路径 n是个数
                        for p1 in list_of_point:
                            path_line_list.add(Line(destination, p1))
                            for p2 in list_of_point:
                                if not p1 == p2:
                                    path_line_list.add(Line(p1, p2))
                        path_line_list_duplicated = []
                        for pl1 in path_line_list:
                            for pl2 in path_line_list:
                                if not pl1 == pl2:
                                    if pl1.start == pl2.end and pl1.end == pl2.start:
                                        path_line_list_duplicated.append(pl2)
                        for dp in path_line_list.copy():
                            if dp in path_line_list_duplicated:
                                path_line_list.remove(dp)
                        # 5.1.2：路径除重
                        for i in range(0, n - 1):
                            frontier_line_list.add(Line(list_of_point[i], list_of_point[i + 1]))
                        frontier_line_list.add(Line(list_of_point[0], list_of_point[n - 1]))
                        list_of_point_original = list_of_point
                        list_of_point.append(destination)
                        q = len(list_of_point)
                        matrix_for_all = np.zeros(shape=(q, q))
                        for p1 in list_of_point:
                            list_for_this_point = []
                            for p2 in list_of_point:
                                path_trial = Line(p1, p2)
                                if p1 == p2:
                                    list_for_this_point.append(0)
                                else:
                                    if not line_check(frontier_line_list, list_of_point, path_trial):
                                        list_for_this_point.append(path_trial.length)
                                    else:
                                        list_for_this_point.append(Inf)
                            matrix_for_all[i] = list_for_this_point
                        distance_of_all = []
                        # 5.1.3 排除出界
                        # 5.2 转化为二维数组
                        for i in range(len(list_of_point)):
                            """
                            5.3: 寻找最短路径
                                5.3.1：对每个destination求最短距离
                                5.3.2：找到所有destination最短的路径
                                （特别注意：drawing_list必须搭配append过destination的point_list使用）
                                5.3.3：绘制最短路径
                            """
                            distance_of_any_frontier, drawing_list_of_any_frontier = dijkstra(matrix_for_all, i,
                                                                                              len(list_of_point) - 1,
                                                                                              len(list_of_point))
                            # 此时的drawing_list并不一定是需要的路径
                            distance_of_all.append(distance_of_any_frontier)
                            if max(distance_of_all) == Inf:
                                answer, answer_index = find_sub_max(distance_of_all, 2)
                            else:
                                answer, answer_index = find_sub_max(distance_of_all, 1)
                            pre_exit_distance, pre_drawing_list = dijkstra(matrix_for_all, answer_index,
                                                                           len(list_of_point) - 1,
                                                                           len(list_of_point))
                            exit_distance_list.append([destination, pre_exit_distance, pre_drawing_list])
                            # 求出本destination的路径
                    e_club = []  # 临时集合，用来找出最短路径距离值
                    for e in exit_distance_list:
                        e_club.append(e[1])
                    e_min = min(e_club)
                    e_min_index = e_club.index(e_min)
                    space.exit_distance = e_min
                    space.drawing_list = exit_distance_list[e_min_index][2]
                    list_of_point = space.point_list.append(exit_distance_list[e_min_index][0])
                    # 5.3.2：找到所有destination最短的路径 特别注意：drawing_list必须搭配append过destination的point_list使用
                    drawing_list = space.drawing_list
                    for i in range(len(drawing_list) - 2):
                        start = list_of_point[drawing_list[i]]
                        end = list_of_point[drawing_list[i + 1]]
                        ax.plot([start.x, end.x], [start.y, end.y], color='purple', linewidth=4)
    plt.show()

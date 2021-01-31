import sys
import ifcopenshell
from ifcopenshell import geom
import os.path
from matplotlib import pyplot as plt
from basic_geometry import Point, Edge, Vector, Triangle, BoundingBox, Line, Space, Storey
from points_to_paths import get_exit_distance, find_sub_max, dijkstra, get_plan, door_to_destination

sys.path.append('C:\ifcopenshell_12.6')
Inf = float('Inf')
model = ifcopenshell.open(os.path.dirname(__file__) + '/ifc/Duplex_A_20110505.ifc')
settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
storeys = []

print("########### stage 1 finding spaces #############")
for ira in model.by_type("IfcRelAggregates"):
    # 为了从某一层开始而使用了IfcRelAggregates
    distance_of_each_space = []
    space_bigger = ira.RelatingObject
    spaces_smaller = ira.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        spaces = []
        for space_smaller in spaces_smaller:
            if space_smaller.is_a("IfcSpace"):
                spaces.append(space_smaller)
        space_bigger = Storey(spaces, space_bigger.GlobalId, space_bigger.Name)
        storeys.append(space_bigger)
print("########### stage 1 done #######################")
print("########### stage 2 forming frontier ###########")
for storey in storeys:
    spaces = storey.contained_spaces
    classified_spaces = []
    for space in spaces:
        edge_list, line_list, point_list = get_plan(space)  # 存放边界 转化为直线的边界 边界点
        # 以上的这些在每个Space中是唯一的
        space = Space(space.LongName, space.GlobalId, storey.name, point_list, edge_list,
                      destination_list=None, exit_distance=None, sequence=None, line_of_destination=None,
                      real_destination=None)
        print(str(space.name).ljust(16, " ") + "   guid(" + str(space.guid) + ")   story(" + str(
            storey.name) + "): edges: " + str(
            len(space.edge_list)) + ": points: " + str(
            len(space.point_list)))
        classified_spaces.append(space)
    storey.contained_spaces = classified_spaces
print("########### stage 2 done ####################")
print("########### stage 3 exit distance ###########")

# 接下来是门，用IfcRelSpaceBoundary找
# 这个循环是建立在space上面的
for storey in storeys:
    spaces = storey.contained_spaces
    for space in spaces:
        destination_list = []  # 因为有可能存在多个目标点
        drawing_list = []  # 但只有一条最短路径（取点的集合）
        distance_length_list = []  # 这是过程变量，不用返回
        exit_distance_list = []
        print(str(space.name).ljust(11, " ") + "(test) " + "   guid(" + str(
            space.guid) + ")   story(" + str(
            storey.name) + "): edges: " + str(
            len(space.edge_list)) + ": points: " + str(
            len(space.point_list)))
        # 测试一下，为什么point_list的元素个数变多了？每有一个des，len(point_list)就会加2
        for irsb in model.by_type("IfcRelSpaceBoundary"):
            space_to_judge = irsb.RelatingSpace
            # 一个IfcRelSpaceBoundary对应一个space
            element_to_judge = irsb.RelatedBuildingElement
            # 一个IfcRelSpaceBoundary对应一个IfcBuildingElement
            if space_to_judge.GlobalId == space.guid:
                # 锁定到每个房间
                if element_to_judge is not None:
                    if element_to_judge.is_a("IfcDoor"):
                        door = element_to_judge
                        des = door_to_destination(door)
                        # des 是door的boundingbox点
                        for edge in space.edge_list:
                            edge_line1 = edge.turn_it_to_a_line()
                            edge_distance = edge_line1.get_point_line_distance(des, edge_line1)
                            # 把边界转化为line类型，调用get_point_line_distance求destination到各frontier直线的长度
                            distance_length_list.append(edge_distance)
                        projection_distance = min(distance_length_list)
                        # 先求出最短距离，再找是哪一条边
                        for edge in space.edge_list:
                            edge_line1 = edge.turn_it_to_a_line()
                            edge_distance = edge_line1.get_point_line_distance(des, edge_line1)
                            if edge_distance == projection_distance:  # 找出最近的线（edge）
                                space.line_of_destination = edge_line1  # 这个房间的门线是line_of_destination
                                projection_of_des = edge_line1.getfootPoint(
                                    des)  # projection_of_des是des的投影点，也是用于计算的destination
                                destination_list.append(
                                    projection_of_des)  # 输出投影 projection_of_des,门线 line_of_destination
                        space.destination_list = destination_list
                        real_exit_distance, real_drawing_list, real_des = get_exit_distance(space)  # 求路径的方法
                        space.exit_distance = real_exit_distance
                        space.sequence = real_drawing_list
                        space.real_destination = real_des
                        print(str(space.name).ljust(18, " ") + "   guid(" + str(space.guid) + ")   story(" + str(
                            storey.name) + "): edges: " + str(
                            len(space.edge_list)) + ": points: " + str(
                            len(space.point_list)))
print("########### stage 3 done ##############")
print("########### stage 4 drawing ###########")
# 目前报错为 Traceback (most recent call last):
#   File "C:/repositories/BIM-Model-Checking-SEU/Python_ide/exit_distance.py", line 114, in <module>
#     for projection_of_des in space.destination_list:
# TypeError: 'NoneType' object is not iterable
# for storey in storeys:
#     spaces = storey.contained_spaces
#     fig, ax = plt.subplots()
#     plt.axis("equal")
#     plt.figure(figsize=(100, 100))
#     ax.set_title(storey.name, fontsize=18)
#     for space in spaces:
#         point_list = space.point_list
#         point_list.append(real_des)
#         tag_of_space = BoundingBox(space.point_list).destination
#         drawing_list = space.sequence
#         for projection_of_des in space.destination_list:
#             ax.scatter(projection_of_des.x, projection_of_des.y, color='blue', s=4)
#         for edge in space.edge_list:
#             ax.plot([edge.s1.x, edge.s2.x], [edge.s1.y, edge.s2.y], color='black', linewidth=0.5)
#             ax.annotate(space.name, xy=(tag_of_space.x, tag_of_space.y))
#             ax.scatter(tag_of_space.x, tag_of_space.y, color='green', s=4)
#         for i in range(len(drawing_list) - 1):
#             start = space.point_list[drawing_list[i]]
#             end = space.point_list[drawing_list[i + 1]]
#             ax.plot([start.x, end.x], [start.y, end.y], color='purple', linewidth=1)
#         print(str(space.name) + ": edges: " + str(len(space.edge_list)) + ": points: " + str(
#             len(space.point_list)))
#         print(space.name + "'s escape distance = " + str(space.exit_distance))
#     plt.savefig(format(str(storey.name), '0>5s') + '.png')
#     plt.show()
#
# print("########### stage 4 done ##############")

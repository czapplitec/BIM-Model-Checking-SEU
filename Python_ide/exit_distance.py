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
Inf = float('Inf')
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
        distance_of_space = 250  # 每个房间的逃生距离
        edge_list, line_list, point_list = get_plan(space)  # 存放边界 转化为直线的边界 边界点
        # 以上的这些在每个Space中是唯一的
        space = Space(space.LongName, space.GlobalId, storey.name, point_list, edge_list,
                      destination_list=None, exit_distance=None, sequence=None, line_of_destination=None,
                      real_destination=None)
        print(str(space.name).ljust(13, " ") + ": edges: " + str(len(edge_list)) + ": points: " + str(
            len(point_list)))
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
        for irsb in model.by_type("IfcRelSpaceBoundary"):
            space_to_judge = irsb.RelatingSpace
            # 一个IfcRelSpaceBoundary对应一个space
            element_to_judge = irsb.RelatedBuildingElement
            # 一个IfcRelSpaceBoundary对应一个IfcBuildingElement
            if space_to_judge.GlobalId == space.guid:
                # 锁定到每个房间
                if not element_to_judge == None:
                    if element_to_judge.is_a("IfcDoor"):
                        door = element_to_judge
                        des = door_to_destination(door)
                        for edge in space.edge_list:
                            edge_line1 = edge.turn_it_to_a_line()
                            edge_distance = edge_line1.get_point_line_distance(des, edge_line1)
                            distance_length_list.append(edge_distance)
                        projection_distance = min(distance_length_list)
                        # 先求出最短距离，再找是哪一条边
                        for edge in space.edge_list:
                            edge_line1 = edge.turn_it_to_a_line()
                            edge_distance = edge_line1.get_point_line_distance(des, edge_line1)
                            if edge_distance == projection_distance:  # 找出最近的线（edge）
                                space.line_of_destination = edge_line1
                                projection_of_des = edge_line1.getfootPoint(des)
                                destination_list.append(
                                    projection_of_des)  # 输出投影 projection_of_des,门线 line_of_destination
                        space.destination_list = destination_list
                        real_exit_distance, real_drawing_list, real_des = get_exit_distance(space)
                        space.exit_distance = real_exit_distance
                        space.sequence = real_drawing_list
                        space.real_destination = real_des

print("########### stage 3 done ##############")
print("########### stage 4 drawing ###########")

for storey in storeys:
    spaces = storey.contained_spaces
    fig, ax = plt.subplots()
    plt.axis("equal")
    plt.figure(figsize=(100, 100))
    ax.set_title(storey.name, fontsize=18)
    for space in spaces:
        point_list = space.point_list
        point_list.append(real_des)
        tag_of_space = BoundingBox(space.point_list).destination
        drawing_list = space.sequence
        for projection_of_des in space.destination_list:
            ax.scatter(projection_of_des.x, projection_of_des.y, color='blue', s=4)
        for edge in space.edge_list:
            ax.plot([edge.s1.x, edge.s2.x], [edge.s1.y, edge.s2.y], color='black', linewidth=0.5)
            ax.annotate(space.name, xy=(tag_of_space.x, tag_of_space.y))
            ax.scatter(tag_of_space.x, tag_of_space.y, color='green', s=4)
        for i in range(len(drawing_list) - 1):
            start = space.point_list[drawing_list[i]]
            end = space.point_list[drawing_list[i + 1]]
            ax.plot([start.x, end.x], [start.y, end.y], color='purple', linewidth=1)
        print(str(space.name) + ": edges: " + str(len(space.edge_list)) + ": points: " + str(
            len(space.point_list)))
        print(space.name + "'s escape distance = " + str(space.exit_distance))
    # if space.name == 'Foyer':
    #     for edge in space.edge_list:
    #         ax.plot([edge.s1.x, edge.s2.x], [edge.s1.y, edge.s2.y], linewidth=0.5)
    #         for i in range(len(point_list)):
    #             point_of_edge = point_list[i]
    #             ax.annotate(i, xy=(point_of_edge.x, point_of_edge.y), fontsize='xx-small', fontweight='normal')
    #             ax.scatter(point_of_edge.x, point_of_edge.y, color='red', s=3)
plt.savefig(format(str(storey.name), '0>5s') + '.png')
plt.show()

print("########### stage 4 done ##############")

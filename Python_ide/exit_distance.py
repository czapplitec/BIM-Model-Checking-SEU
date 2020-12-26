import sys

sys.path.append('C:\ifcopenshell_12.6')
from matplotlib import pyplot as plt
import ifcopenshell
from ifcopenshell import geom
import os.path
from basic_geometry import Point, Edge, Vector, Triangle, BoundingBox, Line, Space
from points_to_paths import get_pathes, find_sub_max, dijkstra

model = ifcopenshell.open(os.path.dirname(__file__) + '/ifc/Duplex_A_20110505.ifc')
Inf = float('Inf')
settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

for ira in model.by_type("IfcRelAggregates"):
    # 为了从某一层开始而使用了IfcRelAggregates
    distance_of_spaces = []
    space_bigger = ira.RelatingObject
    spaces_smaller = ira.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        fig, ax = plt.subplots()
        # 每层楼创建一次画布，注意在画完线条之后要调用plt.show()指令（在spyder中不需要）
        plt.axis("equal")
        # 使坐标轴缩放比例相等
        ax.set_title(space_bigger.Name, fontsize=18)
        """
        for all_doors in model.by_type("IfcDoor"):
            shape = geom.create_shape(settings, all_doors)
            verts = shape.geometry.verts
            faces = shape.geometry.faces
            points = []
            #门的底面坐标点
            for i in range(0, len(verts) - 1, 3):
                point = Point(verts[i], verts[i + 1], verts[i + 2])
                points.append(point)
            dc = BoundingBox(points)
            doors_center = dc.destination
            ax.scatter(doors_center.x, doors_center.y, color='blue', s=6)
        对门使用BoundingBox，调出中心点打印（蓝色）
        经过验证，红色点能完全覆盖蓝色点。蓝色点即为所有门的坐标（所有层都存在）
        """
        print('!!!!!!!!!!!\n!!!!!!!!!!!')
        print(space_bigger.Name + "!!!!")
        print('!!!!!!!!!!!\n!!!!!!!!!!!')
        spaces = []
        for space_smaller in spaces_smaller:
            if space_smaller.is_a("IfcSpace"):
                spaces.append(space_smaller)
        # 对每个房间导出平面
        for space in spaces:
            h = 0
            distance_of_space = 250
            # 每个房间的逃生距离
            edge_list = []
            # 存放边界
            line_list = []
            # 存放转化为直线的边界
            point_list = []
            # 边界点
            duplicated_edges = set()
            # 重复的边（用于mesh）
            distance_length_list = []
            # 存放逃生点到各个edge的距离
            destination_list=[]
            # 因为门不止一个，所以暂且设置一个destination的list
            # 以上的这些在每个Space中是唯一的
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
                    if Edge.duplicated(edge, e):
                        edge_list.remove(e)
            for edge in edge_list:
                line_list.append(edge.turn_it_to_a_line)
                point_list.append(edge.s1)
                # 确认边清理完毕后，点列即为“每个边的端点”，此处取起点
            bb_space = BoundingBox(point_list)
            tag_of_space = bb_space.destination
            # tag_of_space是标签的起点
            for edge in edge_list:
                ax.plot([edge.s1.x, edge.s2.x], [edge.s1.y, edge.s2.y], color='black', linewidth=0.5)
                ax.annotate(space.LongName, xy=(tag_of_space.x, tag_of_space.y))
                ax.scatter(tag_of_space.x, tag_of_space.y, color='green', s=4)
            print(str(space.LongName).ljust(13, " ") + ": edges: " + str(len(edge_list)) + ": points: " + str(
                len(point_list)) + "(before overkill)")
            # 接下来是overkill除重环节，用于实际上相连的房间
            """
            space = Space(point_list, edge_list, None, space.Name, space.GlobalId,
                                                  space_bigger.Name)
            for space1 in spaces:
                for space2 in spaces:
                    space2_origin = space2
                    if not space1 == space2:
                        for frontier1 in space1.edge_list:
                            for frontier2 in space2.edge_list:
                                new_frontier = Line.overkill(frontier1, frontier2)
                                if not new_frontier == None:
                                    space1.edge_list.append(new_frontier)
                        if not space2 == space2_origin:
                            spaces.remove(space2)
                            space1.point_list = []
                            for frontier in space1.edge_list:
                                space1.point_list.append(frontier.s1)
                                # 修正point_list
            """
            # 接下来是门，用IfcRelSpaceBoundary找
            # 这个循环是建立在space上面的
            for irsb in model.by_type("IfcRelSpaceBoundary"):
                space_to_judge = irsb.RelatingSpace
                # 一个IfcRelSpaceBoundary对应一个space
                element_to_judge = irsb.RelatedBuildingElement
                # 一个IfcRelSpaceBoundary对应一个IfcBuildingElement
                if space_to_judge == space:
                    # 锁定到每个房间
                    if not element_to_judge == None:
                        if element_to_judge.is_a("IfcDoor"):
                            door = element_to_judge
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
                            ax.scatter(bb.destination.x, bb.destination.y, color='red', s=4)
                            for edge in edge_list:
                                edge_line1 = edge.turn_it_to_a_line()
                                edge_distance = edge_line1.get_point_line_distance(des, edge_line1)
                                distance_length_list.append(edge_distance)
                            projection_distance = min(distance_length_list)
                            # 先求出最短距离，再找是哪一条边
                            for edge in edge_list:
                                edge_line1 = edge.turn_it_to_a_line()
                                edge_distance = edge_line1.get_point_line_distance(des, edge_line1)
                                if edge_distance == projection_distance:
                                    h += 1
                                    # 找出最近的线（edge）
                                    line_of_destination = edge_line1
                                    projection_of_des = line_of_destination.getfootPoint(des)

                                    """
                                    print(space.LongName.ljust(10, "_") + "__Destination: " + str(
                                        bb.destination.x) + "," + str(
                                        bb.destination.y) + "," + str(bb.destination.z))
                                    print(space.LongName.ljust(10, "_") + "__Projection_of_destination: " + str(
                                        projection_of_des.x) + "," + str(projection_of_des.y) + "," + str(
                                        projection_of_des.z))
                                    """

                                    ax.scatter(projection_of_des.x, projection_of_des.y, color='blue', s=4)
                                    # 这里打印出的是目标点des到最近的edge上的投影projection_of_des


                                    distance_of_space, drawing_list, list_of_points = get_pathes(point_list,
                                                                                                 projection_of_des)
                                    for i in range(len(drawing_list) - 1):
                                        start = list_of_points[drawing_list[i]]
                                        end = list_of_points[drawing_list[i + 1]]
                                        ax.plot([start.x, end.x], [start.y, end.y], color='purple', linewidth=0.3)
                                    distance_of_spaces.append([space, distance_of_space])
                else:
                    continue
        for relationship in distance_of_spaces:
            if relationship[1] < 1000:
                print(relationship[0].LongName.ljust(11, " ") + "'s escape distance = " + str(relationship[1]))

        plt.savefig(format(str(space_bigger.Name), '0>5s') + '.png')
        plt.show()
"""
测试投影能否正常运行
fig, tx = plt.subplots()
test_point = Point(4, 0, 0)
tx.set_title("test", fontsize=18)
tl_start = Point(0, 0, 0)
tl_end = Point(5, 5, 0)
tx.plot([tl_start.x, tl_end.x], [tl_start.y, tl_end.y], color='black', linewidth=0.5)
tx.scatter(test_point.x, test_point.y, color="red", s=6)
test_line = Line(tl_start, tl_end)
projection = test_line.getfootPoint(test_point)
tx.scatter(projection.x, projection.y, color="blue", s=6)
print(projection)
plt.axis("equal")
plt.show()
print(find_sub_max([1,2,3,4],2))
Adjacent = [[0, 1, 12, Inf, Inf, Inf],
            [Inf, 0, 9, 3, Inf, Inf],
            [Inf, Inf, 0, Inf, 5, Inf],
            [Inf, Inf, 4, 0, 13, 15],
            [Inf, Inf, Inf, Inf, 0, 4],
            [Inf, Inf, Inf, Inf, Inf, 0]]
Src, Dst, N = 0, 5, 6
print(dijkstra(Adjacent, Src, Dst, N))


# qwe=np.array('int')
lista=[8,9,7,8,6]
for i,j in lista:
    print("i:"+str(i))
    print("j:"+str(j))
"""
Adjacent = [[0, 1, 12, Inf, Inf, Inf],
            [Inf, 0, 9, 3, Inf, Inf],
            [Inf, Inf, 0, Inf, 5, Inf],
            [Inf, Inf, 4, 0, 13, 15],
            [Inf, Inf, Inf, Inf, 0, 4],
            [Inf, Inf, Inf, Inf, Inf, 0]]
Src, Dst, N = 0, 5, 6
print(dijkstra(Adjacent, Src, Dst, N))



import sys

sys.path.append('C:\ifcopenshell_12.6')
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import ifcopenshell
from ifcopenshell import geom

settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
import os.path

model = ifcopenshell.open(os.path.dirname(__file__) + '/ifc/Duplex_A_20110505.ifc')
from basic_geometry import Point, Edge, Vector, Triangle, BoundingBox
from points_to_paths import get_pathes

# 基本设置

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
        # for all_doors in model.by_type("IfcDoor"):
        #     shape = geom.create_shape(settings, all_doors)
        #     verts = shape.geometry.verts
        #     faces = shape.geometry.faces
        #     points = []
        #     #门的底面坐标点
        #     for i in range(0, len(verts) - 1, 3):
        #         point = Point(verts[i], verts[i + 1], verts[i + 2])
        #         points.append(point)
        #     dc = BoundingBox(points)
        #     doors_center = dc.destination
        #     ax.scatter(doors_center.x, doors_center.y, color='blue', s=6)
        # 对门使用BoundingBox，调出中心点打印（蓝色）
        # 经过验证，红色点能完全覆盖蓝色点。蓝色点即为所有门的坐标（所有层都存在）


        print('!!!!!!!!!!!\n!!!!!!!!!!!')
        print(space_bigger.Name + "!!!!")
        print('!!!!!!!!!!!\n!!!!!!!!!!!')
        spaces = []
        for space_smaller in spaces_smaller:
            if space_smaller.is_a("IfcSpace"):
                spaces.append(space_smaller)
        # 对每个房间导出平面
        for space in spaces:
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
                point_list.append(edge.start)
                # 确认边清理完毕后，点列即为“每个边的端点”，此处取起点
                # point_list.append(edge.end)
                # 此处用matplot输出平面图,用for循环一条一条画
            bb_space = BoundingBox(point_list)
            tag_of_space = bb_space.destination
            # tag_of_space是标签的起点
            for edge in edge_list:
                ax.plot([edge.start.x, edge.end.x], [edge.start.y, edge.end.y], color='black', linewidth=0.5)
                ax.annotate(space.LongName, xy=(tag_of_space.x, tag_of_space.y))
                ax.scatter(tag_of_space.x, tag_of_space.y, color='green', s=6)
            print(str(space.LongName).ljust(13," ") + ": edges: " + str(len(edge_list)) + ": points: " + str(len(point_list)))
            # 接下来是门，用IfcRelSpaceBoundary找
        for irsb in model.by_type("IfcRelSpaceBoundary"):
            space_to_judge = irsb.RelatingSpace
            # 一个IfcRelSpaceBoundary对应一个space
            element_to_judge = irsb.RelatedBuildingElement
            # 一个IfcRelSpaceBoundary对应一个IfcBuildingElement
            for space in spaces:
                if space_to_judge == space:
                    # 锁定到每个房间
                    if not element_to_judge == None:
                        if element_to_judge.is_a("IfcDoor"):
                            print(" ")
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
                            print(space.LongName.ljust(10,"_") + "__Destination: " + str(bb.destination.x) + "," + str(
                                bb.destination.y) + "," + str(bb.destination.z))
                            ax.scatter(bb.destination.x, bb.destination.y, color='red', s=6)
                            # 此刻打印出的是目标点des（红色），注意是使用IfcRelSpaceBoundary调出的，有可能存在不全的问题
                            # 经过验证，红色点能完全覆盖蓝色点。蓝色点即为所有门的坐标（所有层都存在）
                            for edge in edge_list:
                                edge_line1 = edge.turn_it_to_a_line()
                                edge_distance = edge_line1.distance_from_a_point(des)
                                distance_length_list.append(edge_distance)
                                projection_distance = min(distance_length_list)
                                # 求出最短距离
                            for edge in edge_list:
                                edge_line1 = edge.turn_it_to_a_line()
                                edge_distance = edge_line1.distance_from_a_point(des)
                                if edge_distance == projection_distance:
                                    # 找出最近的线（edge）
                                    line_of_destination = edge_line1
                                    projection_of_des = line_of_destination.get_the_projection(des)
                                    print(space.LongName.ljust(10,"_") + "__Projection_of_destination: " + str(
                                        projection_of_des.x) + "," + str(projection_of_des.y) + "," + str(
                                        projection_of_des.z))
                                    # ax.scatter(projection_of_des.x,projection_of_des.y,color='blue',s=6)
                                    # 这里打印出的是目标点des到最近的edge上的投影projection_of_des
                                    distance_of_space=get_pathes(point_list,projection_of_des)
                                    distance_of_spaces.append([space,distance_of_space])
        for relationship in distance_of_spaces:
            print(relationship[0].LongName.ljust(12," ")+"'s escape distance = "+str(relationship[1]))
        plt.savefig(format(str(space_bigger.Name), '0>5s') + '.png')
        plt.show()

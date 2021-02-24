import numpy as np
import math
import ifcopenshell
from sympy import *
from ifcopenshell import geom
from points_to_paths import bounding_box
import os.path

model = ifcopenshell.open(os.path.dirname(__file__) + '/ifc/Duplex_A_20110505.ifc')

settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
APPROXIMATION = 100
a = len(str(APPROXIMATION))
"""
basic_geometry是包含了所有类对象的tab。
1.包括：
    ZPoint（三维点）
    Point（二维点）
    Vector
    Line
    Space
    Door
2.每个类对象都包含：基本的函数、说明、初步的自动化操作、打印形式
3.不包含：自定义函数如bounding_box、dijkstra等等；mat plot绘图
"""


def approximation_of_a_real_number(amy):
    return int(amy * APPROXIMATION) / APPROXIMATION


########################################################################################################################
########################################################################################################################
class ZPoint(object):
    """
    ZPoint是三维点
    """

    def __init__(self, x, y, z):
        self.x = approximation_of_a_real_number(x)
        self.y = approximation_of_a_real_number(y)
        self.z = approximation_of_a_real_number(z)

    @staticmethod
    def point_check_overlap(p1, p2):
        """
        检验两个点是否重合
        （因为输入的过程中已有取整，所以不用写成约等于）
        """
        if p1.x == p2.x and p1.y == p2.y and p1.z == p2.z:
            return True
        else:
            return False

    def __str__(self):
        app = len(str(APPROXIMATION))
        msg = "(3D Point)" + str(self.x).ljust(app, " ") + str(self.y).ljust(app, " ") + str(self.z).ljust(app, " ")
        return msg

    def get_dimensional(self):
        """
        二维化
        （在门的bounding box中有作用，目前的解决方式是直接在verts中取前两位生成二维点）
        """
        return Point(self.x, self.y)


########################################################################################################################
########################################################################################################################
class Point(object):
    """
    Point是二维点
    """

    def __init__(self, x, y):
        self.x = approximation_of_a_real_number(x)
        self.y = approximation_of_a_real_number(y)

    @staticmethod
    def point_check_overlap(p1, p2):
        """
        检验两个点是否重合
        （因为输入的过程中已有取整，所以不用写成约等于）
        """
        if p1.x == p2.x and p1.y == p2.y:
            return True
        else:
            return False

    def __str__(self):
        msg = "(Point) " + "x:" + str(self.x).ljust(a, " ") + "y:" + str(self.y).ljust(a, " ")
        return msg


########################################################################################################################
########################################################################################################################
class Vector(object):
    """
    本程序中，Vector必须用点生成，其np形式随之自动生成
    Vector内置函数包括：
        1. 加减乘除（以免np.array形式不兼容）
        2. 检查一个面是否向上(vector_check_vertical)
    """

    def __init__(self, p1, p2):
        self.start = p1
        self.end = p2
        self.x = p2.x - p1.x
        self.y = p2.y - p1.y
        self.z = p2.z - p1.z
        self.arr = np.array([self.x, self.y, self.z])

    def __str__(self):
        msg = "(Vector) " + str(self.x).ljust(a, " ") + str(self.y).ljust(a, " ") + str(self.z).ljust(a,
                                                                                                      " ") \
              + " start:" + str(self.start) + " end:" + str(self.end)
        return msg

    @staticmethod
    def sub(v1, v2):
        return v1.arr - v2.arr

    @staticmethod
    def multiply(v1, v2):
        return Vector(ZPoint(0, 0, 0),
                      ZPoint(v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x))

    @staticmethod
    def vector_check_vertical(v1, v2):
        v = Vector.multiply(v1, v2)
        if v.x <= 1 / APPROXIMATION and v.y <= 1 / APPROXIMATION and v.z < 0:
            return True
        else:
            return False

    @staticmethod
    def vector_check_parallel(v1, v2):
        """
        先求模，再变为标向量，再看是不是相等
        """
        c = 1 / APPROXIMATION
        v1 = v1.normalize()
        v2 = v2.normalize()
        if abs(v1.x - v2.x) < c and abs(v1.y - v2.y) < c and abs(v1.z - v2.z) < c:
            return True
        else:
            return False

    def magnitude(self):
        import math
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        m = self.magnitude()
        return Vector(ZPoint(0, 0, 0), ZPoint(self.x / m, self.y / m, self.z / m))


########################################################################################################################
########################################################################################################################
class Line(object):
    """
    line和vector本质的区别在于vector是三维的而line是二维的
    line在此处指线段
    line也是用起点和终点生成的
    line内置函数包括：
        1. 求点是否在直线上(line_check_point_on)
        2. 求直线是否相交或重叠等等(line_check_cross)
        3. 求垂足(line_get_foot)
        4. 求点到直线距离(line_get_point_distance)
        5. 求合并直线(line_get_overkill)
    Line用标准式Ax+By+C=0表示，水平则A=0，垂直则B=0
    【疑问】合并直线目前还没有用上
    【疑问】Line的除重与除逆必须用近似值处理
    """

    def __init__(self, p1, p2):
        """
        直线用两个点形成。
        表达式为标准式。
        【疑问】在测试中，出现了完全重合的两个点的直线。
        """
        self.start = p1
        self.end = p2
        self.x = p2.x - p1.x
        self.y = p2.y - p1.y  # 终点减起点
        self.arr = np.array([self.x, self.y])
        self.A = p2.y - p1.y
        self.B = p1.x - p2.x
        self.C = p2.x * p1.y - p1.x * p2.y
        # 修改ABC，使之符合标准式
        if p2.y - p1.y == 0:  # 水平，A=0，B为1
            self.A = 0
            self.B = 1
            if p1.x - p2.x == 0:
                self.C = None
            else:
                self.C = (p2.x * p1.y - p1.x * p2.y) / (p1.x - p2.x)
        elif p2.x - p1.x == 0:  # 垂直，B=0，A为1
            self.A = 1
            self.B = 0
            if p1.y - p2.y == 0:
                self.C = None
            else:
                self.C = (p2.x * p1.y - p1.x * p2.y) / (p2.y - p1.y)
        else:
            self.A = (p2.y - p1.y) / (p2.y - p1.y)
            self.B = (p1.x - p2.x) / (p2.y - p1.y)
            self.C = (p2.x * p1.y - p1.x * p2.y) / (p2.y - p1.y)

    def __str__(self):
        msg = "(Line) " + ("(" + str(self.A) + ")*x+(" + str(self.B) + ")*y+(" + str(
            self.C) + ") = 0").ljust(35, " ") + " start:" + str(self.start) + " end:" + str(self.end)
        return msg

    @staticmethod
    def line_check_point_on(line, p):
        return abs(p.x * line.A + p.y * line.B + line.C) <= 1 / 100

    @staticmethod
    def line_check_cross(l1, l2):
        a1 = l1.A
        a2 = l2.A
        b1 = l1.B
        b2 = l2.B
        c1 = l1.C
        c2 = l2.C
        # 首先检测重合
        if a1 == a2 and b1 == b2:  # 平行
            if c1 == c2:  # 完全重合
                return "[SHARED] totally the same"
            else:  # 平行，检测是否有重合
                if Line.line_check_point_on(l1, l2.start):
                    return "[SHARED] can be composed"
                if Line.line_check_point_on(l1, l2.end):
                    return "[SHARED] can be composed"
                else:  # 平行,不重合
                    return "[SEPARATED]"
        else:  # 不平行
            x = Symbol('x')
            y = Symbol('y')
            dictionary = solve([a1 * x + b1 * y + c1, a2 * x + b2 * y + c2], [x, y])
            # 这里有时会报错 unsupported operands
            # 解方程，若a和b不等于端点x和y，则在中间相交
            new_x = dictionary.get(x)
            new_y = dictionary.get(y)
            math.isclose(new_x, l1.start.x)
            if (math.isclose(new_x, l1.start.x) & math.isclose(new_y, l1.start.y)) | (
                    math.isclose(new_x, l1.end.x) & math.isclose(new_y, l1.end.y)) | (
                    math.isclose(new_x, l2.start.x) & math.isclose(new_y, l2.start.y)) | (
                    math.isclose(new_x, l2.end.x) & math.isclose(new_y, l2.end.y)):
                return "[CROSSED]: on edge"
            else:
                return "[CROSSED]: not on edge"

    @staticmethod
    def line_get_foot(line, p):
        if Line.line_check_point_on(line, p):
            print("You are trying to get foot point from a point on the line, it doesn't exist.")
            return ConnectionRefusedError
        else:
            x0 = p.x
            y0 = p.y
            x1 = line.start.x
            y1 = line.start.y
            x2 = line.end.x
            y2 = line.end.y
            k = -((x1 - x0) * (x2 - x1) + (y1 - y0) * (y2 - y1)) / \
                ((x2 - x1) ** 2 + (y2 - y1) ** 2) * 1.0
            x_n = k * (x2 - x1) + x1
            y_n = k * (y2 - y1) + y1
            return Point(x_n, y_n)

    @staticmethod
    def line_get_point_distance(line, p):
        foot = Line.line_get_foot(line, p)
        if foot != ConnectionRefusedError:
            distance = math.sqrt((foot.x - p.x) ** 2 + (foot.y - p.y) ** 2)
            return distance

    @staticmethod
    def line_get_overkill(l1, l2):
        if Line.line_check_cross(l1, l2) == "[SHARED] can be composed":
            if Line.line_check_point_on(l1, l2.start) and not Line.line_check_point_on(l1,
                                                                                       l2.end):
                # 若l2start在l1上，l2end不在，则l2end是端点
                if Line.line_check_point_on(l2, l1.start):
                    # 若l1start在l2上，l1end不在，则l1end是端点
                    # 【经过检测，这一条不会触发】
                    return Line(l2.end, l1.end)
                elif Line.line_check_point_on(l2, l1.end):
                    # 若l1end在l2上，l1start不在，则l1start是端点
                    # 【经过检测，这一条不会触发】
                    return Line(l2.end, l1.start)
            elif Line.line_check_point_on(l1, l2.start) and Line.line_check_point_on(l1,
                                                                                     l2.end):
                # 若l2start在l1上，l2end也在，则l1end和l1start是端点
                return l1
            else:
                # 若l2start不在l1上，l2end在，则l2start是端点
                if Line.line_check_point_on(l2, l1.start):
                    # 若l1start在l2上，l1end不在，则l1end是端点
                    # 【经过检测，这一条不会触发】
                    return Line(l2.start, l1.end)
                elif Line.line_check_point_on(l2, l1.end):
                    # 若l1end在l2上，l1start不在，则l1start是端点
                    # 【经过检测，这一条不会触发】
                    return Line(l2.start, l1.start)
                    # Line(Point(0,0),Point(4,4))
        else:
            return None

    @staticmethod
    def negative(e1, e2):
        if Point.point_check_overlap(e1.start, e2.end) and Point.point_check_overlap(e1.end, e2.start):
            return True
        else:
            return False

    @staticmethod
    def duplicated(e1, e2):
        if Point.point_check_overlap(e1.start, e2.start) and Point.point_check_overlap(e1.end, e2.end):
            return True
        else:
            return False


########################################################################################################################
########################################################################################################################
class Space(object):
    """
    Space代表房间，需要point_list和frontier_list、destination_list等等
    内置的方法有：
    1. 直接用geom输出point_list等等(__init__)
    2. 寻找逃生路径
    3. （可能在未来用上）设定房间为逃生目的地、指出楼梯空间
    值得注意的是，此处不进行IFC OPEN SHELL的调用
    """

    def __init__(self, storey_name, space_guid, space_longname, space_itself):
        shape = geom.create_shape(settings, space_itself)
        verts = shape.geometry.verts
        faces = shape.geometry.faces
        edge_list_original = []
        point_list = []
        # 输入坐标环节，是程序中唯一的三维部分
        for i in range(0, len(faces) - 1, 3):
            p1 = ZPoint(verts[3 * faces[i] + 0], verts[3 * faces[i] + 1],
                        verts[3 * faces[i] + 2])
            p2 = ZPoint(verts[3 * faces[i + 1] + 0], verts[3 * faces[i + 1] + 1],
                        verts[3 * faces[i + 1] + 2])
            p3 = ZPoint(verts[3 * faces[i + 2] + 0], verts[3 * faces[i + 2] + 1],
                        verts[3 * faces[i + 2] + 2])
            nv = Vector.multiply(Vector(p1, p2), Vector(p1, p3))
            ref = Vector(ZPoint(0, 0, -1), ZPoint(0, 0, 0))
            if Vector.vector_check_parallel(ref, nv):
                edge_list_original.append(Line(p1, p2))
                edge_list_original.append(Line(p2, p3))
                edge_list_original.append(Line(p3, p1))
        edge_list_substitute = edge_list_original
        duplicated_edges = set()
        # 除相反环节:用negative
        for edge in edge_list_substitute:
            for e in edge_list_substitute:
                if Line.negative(edge, e):
                    duplicated_edges.add(edge)
                    duplicated_edges.add(e)
        # 除重环节
        for edge in duplicated_edges:
            for e in edge_list_substitute:
                if Line.duplicated(edge, e):
                    edge_list_substitute.remove(e)
        edge_list_substitute_substitute = edge_list_substitute
        """
        overkill环节
        edge_list_substitute_substitute是第二个替代品（用于在for循环中不显得混乱）
        1.原始列表 edge_list_substitute
        2.for循环 e1与e2判断
        3.为了保证不重复计算，每一次生效的overkill对list的影响必须立刻实现
        4.直到不能再overkill时，停止
        """
        for e1 in edge_list_substitute_substitute:
            for e2 in edge_list_substitute_substitute:
                if e1 != e2:
                    # 【疑问】：overkill尚存在问题。
                    if Line.line_check_cross(e1, e2) == "[SHARED] can be composed":
                        new_line = Line.line_get_overkill(e1, e2)
                        edge_list_substitute_substitute.remove(e1)
                        index = edge_list_substitute_substitute.index(e2)
                        edge_list_substitute_substitute.insert(index, new_line)
                        edge_list_substitute_substitute.remove(e2)
                    if Line.line_check_cross(e1, e2) == "[SHARED] totally the same":
                        edge_list_substitute_substitute.remove(e1)
        # overkill done
        edge_list = edge_list_substitute_substitute
        for edge in edge_list:
            point_list.append(edge.start)  # 确认边清理完毕后，点列即为“每个边的端点”，此处取起点
        tag_of_space = bounding_box(point_list)  # tag_of_space是标签的起点
        self.point_list = point_list
        self.edge_list = edge_list
        self.tag_of_space = tag_of_space
        self.destination_list = []
        self.distance_list = []
        self.drawing_list = []
        self.best_destination = None
        self.exit_distance = None
        self.storey_name = storey_name
        self.space_longname = space_longname
        self.space_guid = space_guid

    def __str__(self):
        msg = "(Space): " + "{Storey}: " + str(self.storey_name) + "  {Name}: " + str(
            self.space_longname).ljust(12, " ") + "  {Guid}: " + str(
            self.space_guid) + "  {Has got ? destinations}: " + str(
            str(self.destination_list)) + "  {The best one is}: " + str(
            self.best_destination) + "  {Exit distance}: " + str(self.exit_distance) + "  {POINTS}: " + str(
            len(self.point_list)) + "  {EDGES}: " + str(len(self.edge_list))
        return msg


########################################################################################################################
########################################################################################################################
class Door(object):
    """
    Door是门
    内置的方法如下：
    1. 直接生成bounding_box
    值得注意的是，求投影的步骤应在主程序中进行。
    """

    def __init__(self, space_belonged, door_guid):
        shape = geom.create_shape(settings, self)
        verts = shape.geometry.verts
        points = []
        for i in range(0, len(verts) - 1, 3):
            point = Point(verts[i], verts[i + 1])
            points.append(point)
        bb = bounding_box(points)
        self.destination = bb
        self.space_belonged = space_belonged
        self.door_guid = door_guid

    def __str__(self):
        msg = "(Door): " + "Space: " + str(self.space_belonged) + "  Destination: " + str(
            self.destination) + "  Guid: " + str(self.door_guid)
        return msg

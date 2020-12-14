d = 1000
c = 0.0000001


class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def magnitude(self):
        import math
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        m = self.magnitude()
        return Vector(self.x / m, self.y / m, self.z / m)

    @staticmethod
    def cross(a, b):
        cp = Vector(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x)
        return cp

    def equals(v1, v2):
        if abs(v1.x - v2.x) < c and abs(v1.y - v2.y) < c and abs(v1.z - v2.z) < c:
            return True
        else:
            return False

    @staticmethod
    def same_direction(v1, v2):
        n1 = v1.normalize()
        n2 = v2.normalize()
        if Vector.equals(n1, n2):
            return True
        else:
            return False

    @staticmethod
    def same_length(v1, v2):
        m1 = v1.magnitude()
        m2 = v2.magnitude()
        if m1 - m2 < c:
            return True
        else:
            return False


class Path(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        import math
        self.length = math.sqrt(
            (self.start.x - self.end.x) * (self.start.x - self.end.x) + (self.start.y - self.end.y) * (
                        self.start.y - self.end.y))
        # path的起点和终点允许相等，方便使用dijkstra算法

    def turn_it_to_a_line(self):
        return Line(self.start, self.end)

    @staticmethod
    def are_them_attached(d1, d2):
        if Point.equals(d1.start, d2.end) or Point.equals(d2.start, d1.end):
            return True
        else:
            return False


class Line(object):
    def __init__(self, s1, s2):
        import math
        self.s1 = s1
        self.s2 = s2
        self.length = math.sqrt((s2.x - s1.x) * (s2.x - s1.x) + (s2.y - s1.y) * (s2.y - s1.y))

    def distance_from_a_point(self, t3):
        import math
        _dis = 0
        v1 = Vector(t3.x - self.s1.x, t3.y - self.s1.y, 0)
        v2 = Vector(self.s2.x - self.s1.x, self.s2.y - self.s1.y, 0)
        k = (Vector.cross(v2, v2)).magnitude() / (Vector.cross(v1, v2)).magnitude()
        if k <= 0:
            _dis = math.sqrt((self.s1.x - t3.x) * (self.s1.x - t3.x) + (self.s1.y - t3.y) * (self.s1.y - t3.y))
        if k >= 1:
            _dis = math.sqrt((self.s2.x - t3.x) * (self.s2.x - t3.x) + (self.s2.y - t3.y) * (self.s2.y - t3.y))
        else:
            v_vertical = Vector(self.s2.x - self.s1.x, self.s1.y - self.s2.y, 0)
            _dis = abs(Vector.cross(v_vertical, v1).magnitude() / (self.length))
        return _dis

    def get_the_projection(self, t3):
        v1 = Vector(t3.x - self.s1.x, t3.y - self.s1.y, 0)
        v2 = Vector(self.s2.x - self.s1.x, self.s2.y - self.s1.y, 0)
        k = (Vector.cross(v2, v2)).magnitude() / (Vector.cross(v1, v2)).magnitude()
        t0 = Point(k * self.s2.x + (1 - k) * self.s1.x, k * self.s2.y + (1 - k) * self.s1.y,
                   k * self.s2.z + (1 - k) * self.s1.z)
        return t0

    # get the projection of the destination to the nearset edge of the room
    @staticmethod
    def check_and_turn(line1, line2):
        # line1 must be the border
        crossed = False
        overlapped = False
        x = y = 0
        x1 = line1.s1.x
        x2 = line1.s2.x
        x3 = line2.s1.x
        x4 = line2.s2.x
        y1 = line1.s1.y
        y2 = line1.s2.y
        y3 = line2.s1.y
        y4 = line2.s2.y
        if (x2 - x1) == 0:
            k1 = None
        else:
            k1 = (y2 - y1) * 1.0 / (x2 - x1)
            b1 = y1 * 1.0 - x1 * k1 * 1.0
        if (x4 - x3) == 0:
            k2 = None
            b2 = 0
        else:
            k2 = (y4 - y3) * 1.0 / (x4 - x3)
            b2 = y3 * 1.0 - x3 * k2 * 1.0
        if k1 is None:
            if not k2 is None:
                x = x1
                y = k2 * x1 + b2
                crossed = True
        elif k2 is None:
            x = x3
            y = k1 * x3 + b1
        elif not k2 == k1:
            x = (b2 - b1) * 1.0 / (k1 - k2)
            y = k1 * x * 1.0 + b1 * 1.0
            crossed = True
        if x == x1 and y == y1:
            overlapped = True
        if x == x2 and y == y2:
            overlapped = True
        return crossed, overlapped


class BoundingBox(object):
    def __init__(self, points):
        p = points[0]
        self.min = Point(p.x, p.y, p.z)
        self.max = Point(p.x, p.y, p.z)
        for point in points:
            if point.x < self.min.x:
                self.min.x = point.x
            if point.y < self.min.y:
                self.min.y = point.y
            if point.z < self.min.z:
                self.min.z = point.z
            if point.x > self.max.x:
                self.max.x = point.x
            if point.y > self.max.y:
                self.max.y = point.y
            if point.z > self.max.z:
                self.max.z = point.z
        self.destination = Point((self.max.x + self.min.x) / 2, (self.max.y + self.min.y) / 2, self.min.z)


class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def equals(s1, s2):
        if abs(s1.x - s2.x) < c and abs(s1.y - s2.y) < c and abs(s1.z - s2.z) < c:
            return True
        else:
            return False


class Edge(object):
    def __init__(self, s1, s2):
        self.start = s1
        self.end = s2
        self.vector = Vector(s2.x - s1.x, s2.y - s1.y, s2.z - s1.z)

    @staticmethod
    def negative(e1, e2):
        if Point.equals(e1.start, e2.end) and Point.equals(e1.end, e2.start):
            return True
        else:
            return False

    @staticmethod
    def duplicated(e1, e2):
        if Point.equals(e1.start, e2.start) and Point.equals(e1.end, e2.end):
            return True
        else:
            return False

    def turn_it_to_a_line(self):
        return Line(self.start, self.end)


class Triangle(object):
    def __init__(self, s1, s2, p3):
        self.s1 = s1
        self.s2 = s2
        self.p3 = p3
        self.e1 = Edge(s1, s2)
        self.e2 = Edge(s2, p3)
        self.e3 = Edge(p3, s1)

print("START__________________________________________________________________START")
import math
import ifcopenshell
from ifcopenshell import geom
settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
d=1000
c=0.0000001
class Distance(object):
    def __init__(self,start,end):
        self.start=start
        self.end=end
    def turn_it_to_a_line(self):
        self.line=Line(self.start,self.end)
    def are_them_attached(d1,d2):
        if Point.equals(d1.start,d2.end) or Point.equals(d2.start,d1.end):
            return True
        else:
            return False
class Line(object):
    def __init__(self,p1,p2):
        import math
        self.p1=p1
        self.p2=p2
        self.length=math.sqrt((p2.x-p1.x)*(p2.x-p1.x)+(p2.y-p1.y)*(p2.y-p1.y))
    @staticmethod
    def distance_from_a_point(self,t3):
        dis=0
        t1=self.p1
        t2=self.p2
        v1=Vector(t3.x-t1.x,t3.y,t1.y,0)
        v2=Vector(t2.x-t1.x,t2.y-t1.y,0)
        k = (Vector.cross(v2,v2))/(Vector.cross(v1,v2))
        if k<=0:
            dis=math.sqrt((t1.x-t3.x)*(t1.x-t3.x)+(t1.y-t3.y)*(t1.y-t3.y))
        if k>=1:
            dis=math.sqrt((t2.x-t3.x)*(t2.x-t3.x)+(t2.y-t3.y)*(t2.y-t3.y))
        else:
            v_vertical=Vector(t2.x-t1.x,t1.y-t2.y,0)
            dis=abs(Vector.cross(v_vertical,v1)/(self.length))
        return dis
    @staticmethod
    def get_the_projection(self,t3):
        t1=self.p1
        t2=self.p2
        v1=Vector(t3.x-t1.x,t3.y,t1.y,0)
        v2=Vector(t2.x-t1.x,t2.y-t1.y,0)
        k = (Vector.cross(v2,v2))/(Vector.cross(v1,v2))
        t0=Point(k*t2.x+(1-k)*t1.x,k*t2.y+(1-k)*t1.y,k*t2.z+(1-k)*t1.z)
        return t0
    @staticmethod
    #get the projection of the destination to the nearset edge of the room
    def check_and_turn(line1,line2):
        # line1 must be the border
        crossed = False
        overlapped = False
        x = y = 0
        x1=line1.p1.x
        x2=line1.p2.x
        x3=line2.p1.x
        x4=line2.p2.x
        y1=line1.p1.y
        y2=line1.p2.y
        y3=line2.p1.y
        y4=line2.p2.y
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
        if x==x1 and y==y1:
            overlapped = True
        if x==x2 and y==y2:
            overlapped = True
        return crossed, overlapped
class BoundingBox(object):
    def __init__(self,points):
        p=points[0]
        self.min=Point(p.x,p.y,p.z)
        self.max=Point(p.x,p.y,p.z)
        for point in points:
            if point.x<self.min.x:
                self.min.x=point.x
            if point.y<self.min.y:
                self.min.y=point.y
            if point.z<self.min.z:
                self.min.z=point.z
            if point.x>self.max.x:
                self.max.x=point.x
            if point.y>self.max.y:
                self.max.y=point.y
            if point.z>self.max.z:
                self.max.z=point.z
        self.destination=Point((self.max.x+self.min.x)/2,(self.max.y+self.min.y)/2,self.min.z)
class Point(object):
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    @staticmethod
    def equals(p1,p2):
        if p1.x-p2.x<c and p1.y-p2.y<c and p1.z-p2.z<c:
            return True
        else:
            return False
class Vector(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def magnitude(self):
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

    def normalize(self):
        m=self.magnitude()
        return Vector(self.x/m,self.y/m,self.z/m)

    @staticmethod
    def cross(a,b):
        cp = Vector(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x)
        return cp

    def equals(v1,v2):
         if v1.x-v2.x<c and v1.y-v2.y<c and v1.z-v2.z<c:
            return True
         else:
            return False

    def same_direction(v1,v2):
        n1=v1.normalize()
        n2=v2.normalize()
        if Vector.equals(n1,n2):
            return True
        else:
            return False

    def same_length(v1,v2):
        m1=v1.magnitude()
        m2=v2.magnitude()
        if m1-m2<c:
            return True
        else:
            return False

class Edge(object):
    def __init__(self,p1,p2):
        self.start=p1
        self.end=p2
        self.vector=Vector(p2.x-p1.x,p2.y-p1.y,p2.z-p1.z)
    @staticmethod
    def negative(e1,e2):
        if Point.equals(e1.start,e2.end) and Point.equals(e1.end,e2.start):
            return True
        else:
            return False
    def duplicated(e1,e2):
        if Point.equals(e1.start,e2.start) and Point.equals(e1.end,e2.end):
            return True
        else:
            return False
    def turn_it_to_a_line(self):
        return Line(self.start,self.end)

class Triangle(object):
    def __init__(self,p1,p2,p3):
        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.e1=Edge(p1,p2)
        self.e2=Edge(p2,p3)
        self.e3=Edge(p3,p1)

for ira in model.by_type("IfcRelAggregates"):
    space_bigger=ira.RelatingObject
    spaces_smaller=ira.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        spaces=[]
        for space_smaller in spaces_smaller:
            if space_smaller.is_a("IfcSpace"):
                spaces.append(space_smaller)
##############################################################################
        for space in spaces:
            edge_list=[]
            line_list=[]
            distance_list=set()
            point_list=set()
            duplicated_edges=set()
            shape=geom.create_shape(settings,space)
            verts=shape.geometry.verts
            faces=shape.geometry.faces
            bottom_triangles=[]
            for i in range(0,len(faces)-1,3):
                p1=Point(verts[3*faces[i] + 0], verts[3*faces[i] + 1],
                               verts[3*faces[i] + 2])
                p2=Point(verts[3*faces[i+1] + 0], verts[3*faces[i+1] + 1],
                               verts[3*faces[i+1] + 2])
                p3=Point(verts[3*faces[i+2] + 0], verts[3*faces[i+2] + 1],
                               verts[3*faces[i+2] + 2])
                triangle=Triangle(p1,p2,p3)
                nv=Vector.cross(triangle.e1.vector,triangle.e2.vector)
                ref=Vector(0,0,-1)
                if Vector.equals(ref,nv.normalize()):
                    bottom_triangles.append(triangle)
                    edge_list.append(triangle.e1)
                    edge_list.append(triangle.e2)
                    edge_list.append(triangle.e3)
##############################################################################
            duplicated_edges=set()
            for edge in edge_list:
                for e in edge_list:
                    if Edge.negative(edge,e):
                        duplicated_edges.add(edge)
                        duplicated_edges.add(e)
            for edge in duplicated_edges:
                for e in edge_list:
                    if Edge.duplicated(edge,e):
                        edge_list.remove(e)
                        pass
            for edge in edge_list:
                line_list.append(edge.turn_it_to_a_line)
                point_list.add(edge.start)
                point_list.add(edge.end)
            print(str(space.LongName)+": edges: "+str(len(edge_list))+": points: "+str(len(point_list)))
##############################################################################
            for irsb in model.by_type("IfcRelSpaceBoundary"):
                spaces_to_judge=irsb.RelatingSpace
                elements_to_judge=irsb.RelatedBuildingElement
                for space_to_judge in spaces_to_judge:
                    for space in spaces:
                        if space_to_judge==space:
                            for element_to_judge in elements_to_judge:
                                if element_to_judge.is_a("IfcDoor"):
                                    door=element_to_judge
                                    shape=geom.create_shape(settings,door)
                                    verts=shape.geometry.verts
                                    faces=shape.geometry.faces
                                    bottom_triangles=[]
                                    points=[]
                                    for i in range(0,len(verts)-1,3):
                                        point=Point(verts[i],verts[i+1],verts[i+2])
                                        points.append(point)
                                    bb=BoundingBox(points)
                                    des=bb.destination
                                    point_list.add(des)
                                    print(d.GlobalId+"__Destination: "+str(bb.destination.x)+","+str(bb.destination.y)+","+str(bb.destination.z))
                                    #here is the destination of the room
###############################################################################
                                    for point in point_list:
                                        for p in point_list:
                                            if not p==point:
                                                dis=Distance(p,point)
                                                dis_line=dis.turn_it_to_a_line
                                                distance_list.add(dis)
                                                # line_list.append(dis_line)
                                                
                
                
                                    
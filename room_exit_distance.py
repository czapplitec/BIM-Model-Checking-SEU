print("START__________________________________________________________________START")
from ifcopenshell import geom
settings = geom.settings()
d=1000000000000000
###############################################################################
###############################################################################
class Line(object):
    def __init__(self,p1,p2):
        import math
        self.p1=p1
        self.p2=p2
        self.length=math.sqrt((p2.x-p1.x)*(p2.x-p1.x)+(p2.y-p1.y)*(p2.y-p1.y))
    @staticmethod
    def distance(self,t3):
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
    def get_the_shade(self,t3):
        t1=self.p1
        t2=self.p2
        v1=Vector(t3.x-t1.x,t3.y,t1.y,0)
        v2=Vector(t2.x-t1.x,t2.y-t1.y,0)
        k = (Vector.cross(v2,v2))/(Vector.cross(v1,v2))
        t0=Point(k*t2.x+(1-k)*t1.x,k*t2.y+(1-k)*t1.y,k*t2.z+(1-k)*t1.z)
        return t0
    @staticmethod
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
    @staticmethod
    def is_upper(self,t3):
        upper=True
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
            dis=Vector.cross(v_vertical,v1)/(self.length)
        if dis>0:
            upper=False
        return upper
####################
class Point(object):
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    @staticmethod
    def equals(p1,p2):
        c=0.1
        if p1.x-p2.x<c and p1.y-p2.y<c and p1.z-p2.z<c:
            return True
        else:
            return False
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"
###################
class Edge(object):
    def __init__(self,p1,p2):
        self.bgn=p1
        self.end=p2
        self.vector=Vector(p2.x-p1.x,p2.y-p1.y,p2.z-p1.z)
        self.line=Line(p1,p2)
    @staticmethod
    def negative(e1,e2):
        if Point.equals(e1.bgn,e2.end) and Point.equals(e1.end,e2.bgn):
            return True
        else:
            return False
    def duplicated(e1,e2):
        if Point.equals(e1.bgn,e2.bgn) and Point.equals(e1.end,e2.end):
            return True
        else:
            return False
    def __str__(self):
        return "Beginning:("+str(self.bgn.x)+","+str(self.bgn.y)+","+str(self.bgn.y)+","+ \
            ")   End:("+str(self.end.x)+","+str(self.end.y)+","+str(self.end.y)+")"
#####################
class Vector(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    @staticmethod
    def cross(a,b):
        c = Vector(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x)
        return c
###################
class Face(object):
    def __init__(self,p1,p2,p3):
        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.e1=Edge(p1,p2)
        self.e2=Edge(p2,p3)
        self.e3=Edge(p3,p1)
###############################################################################
###############################################################################
for ira in model.by_type("IfcRelAggregates"):
    space_bigger=ira.RelatingObject
    spaces_smaller=ira.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        for space_smaller in spaces_smaller:
            name_of_room=str(space_bigger.Name)+"  "+str(space_smaller.LongName)
            edge_list=[]
            line_list=[]
            shapes=geom.create_shape(settings,space_smaller)
            verts=shapes.geometry.verts
            faces=shapes.geometry.faces
            for j in range(0,len(faces)-1,3):
                p1=Point(verts[3*faces[j] + 0], verts[3*faces[j] + 1],
                               verts[3*faces[j] + 2])
                p2=Point(verts[3*faces[j+1] + 0], verts[3*faces[j+1] + 1],
                               verts[3*faces[j+1] + 2])
                p3=Point(verts[3*faces[j+2] + 0], verts[3*faces[j+2] + 1],
                               verts[3*faces[j+2] + 2])
                face=Face(p1,p2,p3)
                nv=Vector.cross(face.e1.vector,face.e2.vector)
                if abs(nv.z )> abs(nv.x)* d and abs(nv.z) > abs(nv.y)* d and nv.z>0:
                # if int(nv.x)==0 and int(nv.y)==0 and nv.z>0:
                    edge_list.append(face.e1)
                    edge_list.append(face.e2)
                    edge_list.append(face.e3)
###############################################################################
            duplicated_edges=set()
            for edge in edge_list:
                for e in edge_list:
                    if Edge.negative(edge,e):
                        duplicated_edges.add(edge)
            for edge in duplicated_edges:
                    edge_list.remove(edge)
            for edge in edge_list:
                line_list.append(edge.line)
            print(name_of_room+"'s edges    = "+str(len(edge_list)))
###############################################################################
        ciss=space_bigger.ContainsElements
        for cis in ciss:
            elements = cis.RelatedElements
            for element in elements:
                if element.is_a("IfcDoor"):
                    settings.set(settings.USE_WORLD_COORDS, True)
                    shapes_doors=geom.create_shape(settings,element)
                    verts_doors=shapes_doors.geometry.verts
                    z_verts=[]
                    y_verts=[]
                    x_verts=[]
                    for j in range(0,len(verts_doors)-1,3):
                        z_verts.append(verts_doors[j+2])
                        y_verts.append(verts_doors[j+1])
                        x_verts.append(verts_doors[j])
                    import operator
                    z_min_index, z_min_number = min(enumerate(z_verts), key=operator.itemgetter(1))
                    y_min_index, y_min_number = min(enumerate(y_verts), key=operator.itemgetter(1))
                    x_min_index, x_min_number = min(enumerate(x_verts), key=operator.itemgetter(1))
                    y_max_index, y_max_number = max(enumerate(y_verts), key=operator.itemgetter(1))
                    x_max_index, x_max_number = max(enumerate(x_verts), key=operator.itemgetter(1))
                    xt=(x_max_number+x_min_number)*0.5
                    yt=(y_max_number+y_min_number)*0.5
                    zt=z_min_number
                    original_terminate=Point(xt,yt,zt)
                    print(original_terminate)
                    dis_of_lines=[]


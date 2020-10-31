print("START__________________________________________________________________START")

from ifcopenshell import geom
settings = geom.settings()
d=1000
#判断法向量的参数
class Line(object):
    def __init__(self,p1,p2):
        self.p1=p1
        self.p2=p2
    @staticmethod
    def check(l1,l2):
        v31=Vector(l1.p1.x-l2.p1.x,l1.p1.y-l2.p1.y,l1.p1.z-l2.p1.z)
        v34=Vector(l2.p2.x-l2.p1.x,l2.p2.y-l2.p1.y,l2.p1.z-l2.p2.z)
        v32=Vector(l1.p2.x-l2.p1.x,l1.p2.y-l2.p1.y,l1.p1.z-l2.p2.z)
        c1=Vector.cross(v31,v34)
        c2=Vector.cross(v32,v34)
        if c1*c2<0:
            return False
#直线，用于判断出界
    

class Point(object):
    def __init__(self,x,y,z,sequence):
        self.x=x
        self.y=y
        self.z=z
        self.sequence=sequence
    @staticmethod
    def equals(p1,p2):
        c=0.1
        if p1.x-p2.x<c and p1.y-p2.y<c and p1.z-p2.z<c:
            return True
        else:
            return False
    def __str__(self):
        return "sequence:%s " % (self.sequence)
#点（sequence是指其在faces中的代号，无法用来比较）

class Edge(object):
    def __init__(self,p1,p2):
        self.bgn=p1
        self.end=p2
        self.vector=Vector(p2.x-p1.x,p2.y-p1.y,p2.z-p1.z)
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
        return "beginning:%s , end:%d" % (self.bgn.sequence, self.end.sequence)
#边，有起点和终点

class Vector(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    @staticmethod
    def cross(a,b):
        c = Vector(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x)
        return c


class Face(object):
    def __init__(self,p1,p2,p3):
        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.e1=Edge(p1,p2)
        self.e2=Edge(p2,p3)
        self.e3=Edge(p3,p1)
#判断向上的部分移到for循环里了

for ira in model.by_type("IfcRelAggregates"):
    space_bigger=ira.RelatingObject
    spaces_smaller=ira.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        on_the_plan=[]
#存放门和房间的list
        num_list=[]
#存放边的list
        ciss=space_bigger.ContainsElements
        for space_smaller in spaces_smaller:
            on_the_plan.append(space_smaller)
        for cis in ciss:
            elements = cis.RelatedElements
            for element in elements:
                if element.is_a("IfcDoor"):
                    on_the_plan.append(element)
        for otp in on_the_plan:
            shapes=geom.create_shape(settings,otp)
            verts=shapes.geometry.verts
            faces=shapes.geometry.faces
#创建faces和verts
            test = 0
#debug用的参数
            # print(otp.Name)
            # print(verts)
            # print(len(verts)/3)
            # print(faces)
            # print(len(faces)/3)
            for j in range(0,len(faces)-1,3):
#经检查这一步应该是对的
                p1=Point(verts[faces[j] + 0], verts[faces[j] + 1],
                               verts[faces[j] + 2],j)
                p2=Point(verts[faces[j+1] + 0], verts[faces[j+1] + 1],
                               verts[faces[j+1] + 2],j+1)
                p3=Point(verts[faces[j+2] + 0], verts[faces[j+2] + 1],
                               verts[faces[j+2] + 2],j+2)
                face=Face(p1,p2,p3)
                nv=Vector.cross(face.e1.vector,face.e2.vector)
                if abs(nv.z )> abs(nv.x)* d and abs(nv.z) > abs(nv.y)* d and nv.z>0:
#判断是否朝上（很有可能有BUG）
                    test=test+1   
                    num_list.append(face.e1)
                    num_list.append(face.e2)
                    num_list.append(face.e3)
            # print(test)
        txt_name_of_floor=str(space_bigger.Name)
        print(txt_name_of_floor+"'s edges         = "+str(len(num_list)))
        duplicated_edges=set()
#去重复
        for edge in num_list:
            for e in num_list:
                if Edge.negative(edge,e):
                    duplicated_edges.add(edge)
                    duplicated_edges.add(e)
                if Edge.duplicated(edge,e):
                    duplicated_edges.add(edge)
                    break
        for edge in duplicated_edges:
            if edge in num_list:
                num_list.remove(edge)
        print(txt_name_of_floor+"'s left edges    = "+str(len(num_list)))
        for edge in num_list:
            print(edge)

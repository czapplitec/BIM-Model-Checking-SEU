from ifcopenshell import geom

class Face(object):
    def __init__(self,p1,p2,p3):
        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.e1=Edge(p1,p2)
        self.e2=Edge(p2,p3)
        self.e3=Edge(p3,p1)
        self.nv=Vector.cross(self.e1.vector, self.e2.vector)
        
    def get_point(self):
        if self.nv.z < self.nv.x * 10000 and self.nv.z < self.nv.y * 10000 and self.nv.z<0:
            return True
        else:
            return False
        
        
class Vector(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        
    @staticmethod
    def cross(a,b):
        c = Vector(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x)
        return c
        
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
            
        
class Point(object):
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        
    @staticmethod
    def equals(p1,p2):
        c=0.00000001
        if p1.x-p2.x<c and p1.y-p2.y<c and p1.z-p2.z<c:
            return True
        else:
            return False
        
    

settings = geom.settings()
for space in model.by_type("IfcSpace"):
    shape = geom.create_shape(settings, space)
    faces = shape.geometry.faces
    verts = shape.geometry.verts
    num_list = [ ]

    for j in range(0,len(faces)-1,3):
        p1=Point(verts[faces[j] + 0], verts[faces[j] + 1],
                       verts[faces[j] + 2])
        p2=Point(verts[faces[j+1] + 0], verts[faces[j+1] + 1],
                       verts[faces[j+1] + 2])
        p3=Point(verts[faces[j+2] + 0], verts[faces[j+2] + 1],
                       verts[faces[j+2] + 2])
        face = Face(p1,p2,p3)
        
        judge = face.get_point()
       
        if judge:
            for i in range(0,len(faces)-1,3):
                list_of_vectors=[face.e1.vector,face.e2.vector,face.e3.vector]
                num_list.append(face.e1)
                num_list.append(face.e2)
                num_list.append(face.e3)
    
    print("all edges= "+str(len(num_list)))
    duplicated_edges=set()
    for edge in num_list:
        for e in num_list:
            if Edge.negative(edge,e):
                duplicated_edges.add(edge)
                duplicated_edges.add(e)
    
    for edge in duplicated_edges:
        num_list.remove(edge)
    print("reduced edges="+str(len(num_list)))
print("START__________________________________________________________________START")

import ifcopenshell
from ifcopenshell import geom
import basic_geometry as bg
from basic_geometry import Point
from basic_geometry import Vector
from basic_geometry import Edge
from basic_geometry import Triangle

settings = geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)
d=1000

''' 
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
'''    

model=ifcopenshell.open('Duplex_A_20110505.ifc')

for ira in model.by_type("IfcRelAggregates"):
    space_bigger=ira.RelatingObject
    spaces_smaller=ira.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        spaces=[]
        doors=[]
        bb_doors={}
        ciss=space_bigger.ContainsElements
        for space_smaller in spaces_smaller:
            if space_smaller.is_a("IfcSpace"):
                spaces.append(space_smaller)
        for cis in ciss:
            elements = cis.RelatedElements
            for element in elements:
                if element.is_a("IfcDoor"):
                    doors.append(element)
        for door in doors:
            shape=geom.create_shape(settings,door)
            verts=shape.geometry.verts
            faces=shape.geometry.faces
            bottom_triangles=[]
            points=[]
            for i in range(0,len(verts)-1,3):
                point=Point(verts[i],verts[i+1],verts[i+2])
                points.append(point)
            bb=bg.BoundingBox(points)
            bb_doors[door]=bb
            
        for d in bb_doors.keys():
            bb=bb_doors.get(d)
            min=bb.min
            max=bb.max
            print(d.GlobalId+": min: ("+str(min.x)+","+str(min.y)+","+str(min.z)+"), max: ("+str(max.x)+","+str(max.y)+","+str(max.z)+")")
            
        for space in spaces:
            num_list=[]
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
                    num_list.append(triangle.e1)
                    num_list.append(triangle.e2)
                    num_list.append(triangle.e3)
            
            duplicated_edges=set()
            for edge in num_list:
                for e in num_list:
                    if not edge==e:
                        if Edge.negative(edge,e):
                            duplicated_edges.add(edge)
                            duplicated_edges.add(e)
            for edge in duplicated_edges:
                if edge in num_list:
                    num_list.remove(edge)
            print(str(space.GlobalId)+": ")
            for edge in num_list:
                print(edge)

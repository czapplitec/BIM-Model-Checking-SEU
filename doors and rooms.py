print("START_________________________________START")

from ifcopenshell import geom
settings = geom.settings()

class Point(object):
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    @staticmethod
    def equals(p1,p2):
        c=0.00001
        if p1.x-p2.x<c and p1.y-p2.y<c and p1.z-p2.z<c:
            return True
        else:
            return False
class Relationship(object):
    def __init__(self,door,room,pointq):
        self.door=door
        self.room=room
        self.point=pointq
    def __str__(self):
        return self.door.ljust(25, )+"   "+self.room.ljust(25, )
        # +str(point.x)+","+str(point.y)+","+str(point.z)
    @staticmethod
    def equal(r1,r2):
        if r1.door==r2.door and r1.room==r2.room:
            return True
        else:
            return False
relationship_pool=[]

for relation in model.by_type("IfcRelAggregates"):
    space_bigger=relation.RelatingObject
    space_smaller=relation.RelatedObjects
    if space_bigger.is_a("IfcBuildingStorey"):
        rooms = space_smaller
        storey = space_bigger
        for room in rooms:
            shape_room=geom.create_shape(settings,room)
            vertices_room = shape_room.geometry.verts
            points_room=[]
            for j in range(0,len(vertices_room)-1,3):
                p=Point(vertices_room[j], vertices_room[j+1],vertices_room[j+ 2])
                points_room.append(p)
            ciss = storey.ContainsElements
            for cis in ciss:
                eles = cis.RelatedElements
                for ele in eles:
                    if ele.is_a("IfcDoor"):
                        shape_door=geom.create_shape(settings,ele)
                        vertices_door = shape_door.geometry.verts
                        points_door=[]
                        for j in range(0,len(vertices_door)-1,3):
                            p2=Point(vertices_door[j], vertices_door[j+1],vertices_door[j+ 2])
                            points_door.append(p2)
                            for point in points_door:
                                for point2 in points_room:
                                    if Point.equals(point,point2):
                                        rela=Relationship(ele.GlobalId,room.GlobalId,point2)
                                        relationship_pool.append(rela)
                                        break
print(len(relationship_pool))
for r1 in relationship_pool:
    for r2 in relationship_pool:
        if Relationship.equal(r1,r2):
            relationship_pool.remove(r2)
for r1 in relationship_pool:
    for r2 in relationship_pool:
        if Relationship.equal(r1,r2):
            relationship_pool.remove(r2)
for r1 in relationship_pool:
    for r2 in relationship_pool:
        if Relationship.equal(r1,r2):
            relationship_pool.remove(r2)
print(len(relationship_pool))
# def f(a,b):
#     return a.door-b.door
# if relationship_pool:
#     relationship_pool.sort(f,lambda)
#     last=relationship_pool[-1]
#     for i in range(len(relationship_pool)-2,-1,-1):
#         if last==relationship_pool[i]:
#             del relationship_pool[i]
#         else:
#             last=relationship_pool[i]      
        
for rs in relationship_pool:
    print(rs)


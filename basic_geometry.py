# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:54:54 2020

@author: zhang
"""
import math
c=0.000001


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


#a 3d cartesian point that has coordinates x, y, z        
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

#a 3d vector that has direction x, y, z
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
        

#a 3D segment that has a direction defined by a start point and an end point
class Edge(object):
    def __init__(self,p1,p2):
        if not Point.equals(p1, p2):
            self.start=p1
            self.end=p2
            self.vector=Vector(p2.x-p1.x,p2.y-p1.y,p2.z-p1.z)
        else:
            raise Exception("Two points of the segment are the same: p1: "+str(p1.x)+" "+str(p1.y)+" "+str(p1.z)+" p2: "+str(p2.x)+" "+str(p2.y)+" "+str(p2.z))
    
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
    def __str__(self):
        return "beginning:%s , end:%d" % (self.bgn.sequence, self.end.sequence)

#a 3D triangle that is defined by     
class Triangle(object):
    def __init__(self,p1,p2,p3):
        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.e1=Edge(p1,p2)
        self.e2=Edge(p2,p3)
        self.e3=Edge(p3,p1)

            
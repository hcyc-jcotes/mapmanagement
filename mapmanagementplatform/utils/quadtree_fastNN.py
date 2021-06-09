# import numpy as np
# import numba
# from numba import jit, cuda,f8

# from numba import jit,jitclass,deferred_type, optional, f8
# from numba import jitclass, deferred_type
# from numba import boolean, int32, float64,uint8
# from numba.typed import List


class Point:

    def __init__(self,id, x, y, data=None):
        self.id,self.x, self.y = id,x, y
        self.data = data

    def distance_to(self, other):
        try:
            other_x, other_y = other.x, other.y
        except AttributeError:
            other_x, other_y = other
        return np.hypot(self.x - other_x, self.y - other_y)

class Rect(object):

    def __init__(self, cx, cy, w, h):
        self.cx, self.cy = cx, cy
        self.w, self.h = w, h
        self.west_edge, self.east_edge = cx - w/2, cx + w/2
        self.north_edge, self.south_edge = cy - h/2, cy + h/2
    
    def contains(self, point):
        try:
            point_x, point_y = point.x, point.y
        except AttributeError:
            point_x, point_y = point

        return (point_x >= self.west_edge and
                point_x <  self.east_edge and
                point_y >= self.north_edge and
                point_y < self.south_edge)

    def intersects(self, other):
        return not (other.west_edge > self.east_edge or
                    other.east_edge < self.west_edge or
                    other.north_edge > self.south_edge or
                    other.south_edge < self.north_edge)

    def draw(self, ax, c='k', lw=1, **kwargs):
        x1, y1 = self.west_edge, self.north_edge
        x2, y2 = self.east_edge, self.south_edge
        ax.plot([x1,x2,x2,x1,x1],[y1,y1,y2,y2,y1], c=c, lw=lw, **kwargs)

class QuadTree:
    def __init__(self, boundary, max_points, depth=5):

        self.boundary = boundary
        self.max_points = max_points
        self.points = []
        self.depth = depth
        self.divided = False

    def sub_divide(self):

        cx, cy = self.boundary.cx, self.boundary.cy
        w, h = self.boundary.w / 2, self.boundary.h / 2

        self.nw = QuadTree(Rect(cx - w/2, cy - h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.ne = QuadTree(Rect(cx + w/2, cy - h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.se = QuadTree(Rect(cx + w/2, cy + h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.sw = QuadTree(Rect(cx - w/2, cy + h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.divided = True
    
    def insert(self, point):

        if not self.boundary.contains(point):
            return False
        
        if len(self.points) < self.max_points:
            self.points.append(point)
            return True

        if not self.divided:
            self.sub_divide()

        return (self.ne.insert(point) or self.nw.insert(point) or self.se.insert(point) or self.sw.insert(point))
    
    def query(self, boundary, found_points):
        if not self.boundary.intersects(boundary):
            return False

        for point in self.points:
            if boundary.contains(point):
                found_points.append(int(point.id))

        if self.divided:
            self.nw.query(boundary, found_points)
            self.ne.query(boundary, found_points)
            self.se.query(boundary, found_points)
            self.sw.query(boundary, found_points)
        return found_points


    def query_circle(self, boundary, centre, radius, found_points):
        # implementing
        return found_points

    def query_radius(self, centre, radius, found_points):
        # implementing
        return self.query_circle(boundary, centre, radius, found_points)


    def __len__(self):
        npoints = len(self.points)
        if self.divided:
            npoints += len(self.nw)+len(self.ne)+len(self.se)+len(self.sw)
        return npoints

    def draw(self, ax):
        self.boundary.draw(ax)
        if self.divided:
            self.nw.draw(ax)
            self.ne.draw(ax)
            self.se.draw(ax)
            self.sw.draw(ax)
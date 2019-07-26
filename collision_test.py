from base import *
from collision import *

poly2 = [Vec(1, 1),
         Vec(1, 2),
         Vec(2, 2),
         Vec(2, 1)]

poly1 = [Vec(1, 0),
         Vec(0, 1),
         Vec(1, 1),
         Vec(1, 0)]

#print(collide(poly1, poly2))

polys = [poly1, poly2]

def get_support_point(direction, polygon):
    return max(map(lambda vertex: direction.dot(vertex), polygon))

def get_support_point2(direction, polygon):
    return min(map(lambda vertex: direction.dot(vertex), polygon))

def collide_along(direction, polygon1, polygon2):
    p1_sp_min = min(map(lambda vertex: direction.dot(vertex), polygon1))
    p2_sp_min = min(map(lambda vertex: direction.dot(vertex), polygon2))
    p1_sp_max = max(map(lambda vertex: direction.dot(vertex), polygon1))
    p2_sp_max = max(map(lambda vertex: direction.dot(vertex), polygon2))

    print(p1_sp_min, p1_sp_max, p2_sp_min, p2_sp_max)

    return left > right or right < left

# For the x-axis:
print(get_support_point(Vec(1, 0), poly1), get_support_point2(Vec(1, 0), poly2), end=2*'\n')

print(collide_along(Vec(1, 0), poly1, poly2))

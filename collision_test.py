from base import *
from collision import *

poly2 = [Vec(1, 1),
         Vec(1, 2),
         Vec(2, 1)]

poly1 = [Vec(0, 0),
         Vec(0, 1),
         Vec(1, 0)]

#print(collide(poly1, poly2))

polys = [poly1, poly2]

def get_support_point(direction, polygon):
    return max(map(lambda vertex: direction.dot(vertex), polygon))

def get_support_point2(direction, polygon):
    return min(map(lambda vertex: direction.dot(vertex), polygon))

def collide_along(direction, polygon1, polygon2):
    # Calculate support points.
    polygon1_projected = map(lambda vertex: direction.dot(vertex), polygon1)
    polygon2_projected = map(lambda vertex: direction.dot(vertex), polygon2)
    p1_max = max(polygon1_projected)
    p1_min = min(polygon1_projected)
    p2_max = max(polygon2_projected)
    p2_min = min(polygon2_projected)

    if p1_min > p2_max or p1_max < p2_min:
        # They are not touching.
        return False
    else:
        # They are intersecting.
        return True

# For the x-axis:
print(get_support_point(Vec(1, 0), poly1), get_support_point2(Vec(1, 0), poly2), end=2*'\n')

print(collide_along(Vec(1, 0), poly1, poly2))

from base import *

__all__ = ['Collider',
           'get_support',
           'get_separation', 'collide', 'collide_point',
           'collide_all',
           'get_intersector']


class Collider:
    def __init__(self, vertices):
        self.vertices = vertices
    
    def get_vertices(self):
        return tuple(self.vertices)


def get_support(n, poly):
    return max(poly, key=lambda v: v.dot(n))


def get_separation(p1, p2):
    highest_d = float('-inf')
    normal = Vec(0, 0)
    for i in range(len(p1)):
        # Find this edge.
        j = (i + 1) % len(p1)
        edge = p1[i] - p1[j]
        n = Vec(x=-edge.y, y=edge.x)
        n = n / abs(n)     # Normalise n.

        # Find support point of p2 along -n.
        s = get_support(-n, p2)
        # Find distance of support point from edge.
        d = n.dot(s - p1[i])

        # Keep track of shallowest depth.
        if d > highest_d:
            highest_d = d
            normal = n

    return  highest_d, normal


def collide(p1, p2):
    sep1 = get_separation(p1, p2) 
    sep2 = get_separation(p2, p1) 

    if sep1[0] > sep2[0]:
        return sep1
    else:
        # Invert normal so that it always points away from p1 and
        # towards p2.
        return (sep2[0], -sep2[1])


def collide_point(s, p1):
    biggest_d = float('-inf')
    for i in range(len(p1)):
        j = (i + 1) % len(p1)
        side = p1[i] - p1[j]
        n = Vec(x=-side.y, y=side.x)
        n = n / abs(n)     # Normalise n.

        d = n.dot(s - p1[i])

        if d > biggest_d:
            biggest_d = d

    return biggest_d


def collide_all(colliders):
    polys = [c.get_vertices() for c in colliders]

    collisions = []

    for start in range(len(colliders) - 1):
        head = polys[start]
        tail = polys[start + 1:]

        for i, poly in enumerate(tail):
            separation, axis = collide(head, poly)
            if separation < 0.0:
                collisions.append(
                    (colliders[start],
                     colliders[start + 1 + i],
                     separation,
                     axis)
                )

    return collisions


def get_intersector(p1, p2, axis):
    #'''
    intersecting_points = []
    intersecting_points += [p for p in p1 if collide_point(p, p2) < 0]
    intersecting_points.extend(filter(lambda p: collide_point(p, p1) < 0, p2))

    if len(intersecting_points) == 0:
        #return None
        return max(p1, key=lambda p: collide_point(p, p2))

    intersector = sum(intersecting_points, Vec(0, 0)) / len(intersecting_points)

    return intersector
    #'''

    p1_sorted = sorted(p1, key=lambda v: v.dot(-axis))

    # Find the first point that collides with p2.
    for s1 in p1_sorted:
        depth = collide_point(s1, p2)
        if depth < 0.0:
            break
    else:
        s1 = None

    p2_sorted = sorted(p2, key=lambda v: v.dot(axis))

    # Find the first point that collides with p1.
    for s2 in p2_sorted:
        depth = collide_point(s2, p1)
        if depth < 0.0:
            break
    else:
        s2 = None
    
    if s1 is None:
        if s2 is None:
            # Only edges intersect - guess a reasonable point.
            return p1_sorted[0]
        else:
            return s2
    elif s2 is None:
        return s1
    elif s1.dot(axis) > s2.dot(-axis):
        return s1
    else:
        return s2

from base import *

__all__ = ['get_support',
           'get_separation', 'collide', 'collide_point',
           'collide_all',
           'get_intersector']


def get_support(n, poly):
    return max(poly, key=lambda v: v.dot(n))


def get_separation(p1, p2):
    highest_d = float('-inf')
    normal = Vec(0, 0)
    vertex_index = 0
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
            vertex_index = i

    return highest_d, normal, vertex_index


def collide(p1, p2):
    sep1 = get_separation(p1, p2) 
    sep2 = get_separation(p2, p1)

    # todo: introduce bias to this calculation
    if sep1[0] > sep2[0]:
        # Ref = 1  Inc = 2  Ref_i = sep1[2]
        # inc_i = get_incident_normal(p1, p2, ref_i)
        return sep1
    else:
        # Invert normal so that it always points away from p1 and
        # towards p2.
        return (sep2[0], -sep2[1])


def get_incident_normal(ref_n, inc_p, inc_i):
    left_edge = inc_p[inc_i - 1] - inc_p[inc_i]  # Need not wrap the index here as Python does it automatically.
    right_edge = inc_p[inc_i] - inc_p[(inc_i + 1) % len(inc_p)]

    if ref_n.dot(left_edge) > ref_n.dot(right_edge):
        return ...
    else:
        return ...


def get_intersector(p1, p2, axis):
    intersecting_points = []
    intersecting_points += [i for i, p in enumerate(p1) if collide_point(p, p2) < 0]
    intersecting_points += [i for i, p in enumerate(p2) if collide_point(p, p1) < 0]

    if len(intersecting_points) == 0:
        return None
        # return max(p1, key=lambda p: collide_point(p, p2))

    # intersector = sum(intersecting_points, Vec(0, 0)) / len(intersecting_points)
    intersector = intersecting_points[0]

    return intersector


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
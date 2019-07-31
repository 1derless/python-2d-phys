from base import *

__all__ = ['collide_along', 'collide', 'collide_all']


def collide_along(direction, polygon1, polygon2):
    if isinstance(polygon1, Poly):
        polygon1 = polygon1.vertices
    if isinstance(polygon2, Poly):
        polygon2 = polygon2.vertices

    # Calculate support points.
    polygon1_projected = map(lambda vertex: direction.dot(vertex), polygon1)
    polygon2_projected = map(lambda vertex: direction.dot(vertex), polygon2)
    p1_min, p1_max = min_max(polygon1_projected)
    p2_min, p2_max = min_max(polygon2_projected)

    if p1_min > p2_max or p1_max < p2_min:
        # They are not touching.
        return False
    else:
        # They are intersecting.
        return True


def collide(polygon1, polygon2):
    # Work out which axes need to be tested against.
    test_axes = []
    for polygon in (polygon1.vertices, polygon2.vertices):
        for v1, v2 in zip(polygon, polygon[1:]):
            side = v2 - v1
            normal = Vec(x=-side.y, y=side.x)
            test_axes.append(normal)
        side = polygon[-1] - polygon[0]
        normal = Vec(x=side.y, y=-side.x)
        test_axes.append(normal)

    # Test the polygons against the determined axes.
    return all(map(lambda d: collide_along(d,
                                           polygon1.vertices,
                                           polygon2.vertices),
                   test_axes))


def collide_all(shapes, callback):
   if len(shapes) <= 1:
       return

   for shape in shapes[1:]:
       if collide(shapes[0], shape):
           callback(shapes[0], shape)

   return collide_all(shapes[1:], callback)

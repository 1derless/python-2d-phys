from base import *

__all__ = ['collide_along', 'collide', 'collide_all']


def collide_along(direction, polygon1, polygon2):
    #if isinstance(polygon1, Poly):
    #    polygon1 = polygon1.vertices
    #if isinstance(polygon2, Poly):
    #    polygon2 = polygon2.vertices

    # Calculate support points.
    polygon1_projected = map(lambda vertex: direction.dot(vertex), polygon1)
    polygon2_projected = map(lambda vertex: direction.dot(vertex), polygon2)
    p1_min, p1_max = min_max(polygon1_projected)
    p2_min, p2_max = min_max(polygon2_projected)

    print(f'Seps: {p1_max - p2_min, p2_max - p1_min}')
    if p1_min > p2_max:
        #print(f'Separated by {p1_min - p2_max}.')
        # There is no penetration.
        return None
    elif p1_max < p2_min:
        #print(f'Separated by {p2_min - p1_max}.')
        return None
    else:
        # Return minimum penetration.
        return min(p1_max - p2_min, p2_max - p1_min)


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

    # Test the polygons against the determined axes and record the axis along
    # which the polygongs interpenetrate the smallest amount.
    least_penetration = float('inf')
    axis_of_least_penetration = None
    for axis in test_axes:
        axis_norm = axis / abs(axis)
        penetration = collide_along(axis_norm, polygon1.vertices, polygon2.vertices)

        # Return if an axis of separation was found.
        if penetration is None:
            return None

        elif penetration < least_penetration:
            least_penetration = penetration
            axis_of_least_penetration = axis_norm

        #print('Axis:', axis_of_least_penetration, 'Depth:', penetration)

    # Test the polygons against the determined axes.
    #           all(map(lambda axis: collide_along(axis,
    #                                                   polygon1.vertices,
    #                                                   polygon2.vertices),
    #                   test_axes))
    return axis_of_least_penetration * penetration


def collide_all(shapes, callback):
    if len(shapes) <= 1:
        return

    for shape in shapes[1:]:
        penetration_axis = collide(shapes[0], shape)
        if penetration_axis is not None:
           callback(shapes[0], shape, axis=penetration_axis)

    return collide_all(shapes[1:], callback)

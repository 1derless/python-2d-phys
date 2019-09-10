'''
File format:
pickle the following
[
  version [str]
    of ['version 1', 'version 2']
  [
    features [str]
      of ['collision']
  ]
  gravity [Vec]
  [
    entities
  ]
  [
    (springs) --empty if no springs
  ]
]
'''

import pickle

import phys
import colliding_world


def load(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)

        if data[0] != 'version 2':
            raise IOError('Unreadable file version.')

        version, features, gravity, entities, springs = data

        if 'collision' in features:
            system = colliding_world.CollidingWorld()
        else:
            system = phys.System()

        system.gravity = gravity

        for entity in entities:
            system.add_ent(entity)

        for spring in springs:
            system.add_spring(spring)

        return system


def save(path, system):
    with open(path, 'wb') as file:
        data = ['version 2']

        # Specify features.
        if isinstance(system, colliding_world.CollidingWorld):
            data.append(['collision'])
        else:
            data.append([])

        data.append(system.gravity)
        data.append(system._entities)
        data.append(system._springs)

        pickle.dump(data, file)

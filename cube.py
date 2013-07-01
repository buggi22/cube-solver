import random

class Cube:
  faces = ['front', 'back', 'up', 'down', 'left', 'right']
  standard_colors = ['red', 'orange', 'yellow', 'white', 'blue', 'green']

  cw_neighbors = {
    'front': ['up', 'right', 'down', 'left'],
    'back': ['up', 'left', 'down', 'right'],
    'up': ['left', 'back', 'right', 'front'],
    'down': ['back', 'left', 'front', 'right'],
    'left': ['up', 'front', 'down', 'back'],
    'right': ['up', 'back', 'down', 'front'],
  }
  
  def __init__(self):
    self.reset()

  def __str__(self):
    result = 'Cube:\n'
    for face in Cube.faces:
      neighbors = Cube.cw_neighbors[face]
      result += '  ' + str(face) + ':\n'
      result += '    center: ' + str(self.get_color(face)) + '\n'
      result += '    edges:\n'
      for n in neighbors:
        result += '      ' + str(n) + ': ' + str(self.get_color(face, n)) + '\n'
      result += '    corners:\n'
      for i in [0,2]:
        for j in [1,3]:
          result += '      ' + str(neighbors[i]) + ', ' + str(neighbors[j]) \
              + ': ' + str(self.get_color(face, neighbors[i], neighbors[j])) \
              + '\n'
    return result

  def reset(self):
    self.cube = {}
    for face, color in zip(Cube.faces, Cube.standard_colors):
      self.set_color(color, face)
      neighbors = Cube.cw_neighbors[face]
      for i in [0,2]:
        for j in [1,3]:
          self.set_color(color, face, neighbors[i], neighbors[j])
      for n in neighbors:
        self.set_color(color, face, n)

  def key_at(self, face, edge=None, edge2=None):
    assert(face != None)
    if edge == None and edge2 == None:
      return 'center'
    assert(edge != None)
    if edge2 == None:
      return (edge,)
    return tuple(sorted([edge, edge2]))

  def get_color(self, face, edge=None, edge2=None):
    return self.cube[face][self.key_at(face, edge, edge2)]
  
  def set_color(self, color, face, edge=None, edge2=None):
    if not(face in Cube.faces):
      raise "unrecognized face"
    if not(face in self.cube):
      self.cube[face] = {}
    self.cube[face][self.key_at(face, edge, edge2)] = color
  
  def get_color_from_coords(self, face, x, y):
    assert(x in [-1,0,1])
    assert(y in [-1,0,1])

    neighbors = Cube.cw_neighbors[face]

    if x == 0 and y == 0: # center
      return self.get_color(face)
    elif x != 0 and y != 0: # corner
      if (x, y) == (1, -1):
        return self.get_color(face, neighbors[0], neighbors[1])
      elif (x, y) == (1, 1):
        return self.get_color(face, neighbors[1], neighbors[2])
      elif (x, y) == (-1, 1):
        return self.get_color(face, neighbors[2], neighbors[3])
      elif (x, y) == (-1, -1):
        return self.get_color(face, neighbors[3], neighbors[0])
    else: # edge
      if (x, y) == (0, -1):
        return self.get_color(face, neighbors[0])
      elif (x, y) == (1, 0):
        return self.get_color(face, neighbors[1])
      elif (x, y) == (0, 1):
        return self.get_color(face, neighbors[2])
      elif (x, y) == (-1, 0):
        return self.get_color(face, neighbors[3])

    raise "could not get color from coords"
  
  def rotate_colors(self, colors):
    return [colors[len(colors)-1]] + colors[:len(colors)-1]

  def rotate(self, face, times=1):
    if (times < 0):
      raise "Cannot rotate a negative number of times"
    if times == 0:
      return
    
    # perform one clockwise rotation
    neighbors = Cube.cw_neighbors[face]
    num_neighbors = len(neighbors)
    # first, rotate the edges
    colors = [self.get_color(n, face) for n in neighbors]
    for n, c in zip(neighbors, self.rotate_colors(colors)):
      self.set_color(c, n, face)
  
    # next, rotate the corners
    # on-face corners
    colors = [
        self.get_color(face, neighbors[i], neighbors[(i+1) % num_neighbors]) \
        for i in range(num_neighbors)]
    for i, c in zip(range(num_neighbors), self.rotate_colors(colors)):
      self.set_color(c, face, neighbors[i], neighbors[(i+1) % num_neighbors])

    # off-face corners toward the CW and CCW directions
    cw_offset = 1
    ccw_offset = num_neighbors-1
    for offset in [cw_offset, ccw_offset]:
      colors = []
      for n in neighbors:
        neighbors_of_neighbors = Cube.cw_neighbors[n]
        index = neighbors_of_neighbors.index(face)
        edge2 = neighbors_of_neighbors[(index+offset) % num_neighbors]
        colors += [self.get_color(n, face, edge2)]
      for n, c in zip(neighbors, self.rotate_colors(colors)):
        neighbors_of_neighbors = Cube.cw_neighbors[n]
        index = neighbors_of_neighbors.index(face)
        edge2 = neighbors_of_neighbors[(index+offset) % num_neighbors]
        self.set_color(c, n, face, edge2)

    # perform the remainder of the rotation
    self.rotate(face, times-1)

  def apply_sequence(self, sequence):
    for face, times in sequence:
      self.rotate(face, times)

  def scramble(self, moves=30, seed=1001):
    sequence = self.generate_scramble_sequence(moves, seed)
    self.apply_sequence(sequence)
    return sequence

  def generate_scramble_sequence(self, moves=30, seed=1001):
    if seed != 'same_seed': # special value to avoid resetting the seed
      random.seed(seed)
    sequence = []
    for i in range(moves):
      face = random.choice(['front','back','up','down','left','right'])
      times = random.randint(1,3)
      sequence.append((face, times))
    return sequence

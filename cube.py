import random
import copy

class Cube:
  faces = ['front', 'back', 'up', 'down', 'left', 'right']
  standard_colors = ['red', 'orange', 'yellow', 'white', 'blue', 'green']

  # Define the neighbors of each face, in the clockwise (CW) direction.
  #
  # Note: Any change to this order will affect the behavior of 
  # get_color_from_coords.  Wherever possible,"up" should be the first
  # neighbor; the first neighbor of "up" should be "left", and the first
  # neighbor of "down" should be "back".
  _cw_neighbors = {
    'front': ['up', 'right', 'down', 'left'],
    'back': ['up', 'left', 'down', 'right'],
    'up': ['left', 'back', 'right', 'front'],
    'down': ['back', 'left', 'front', 'right'],
    'left': ['up', 'front', 'down', 'back'],
    'right': ['up', 'back', 'down', 'front'],
  }
  
  def __init__(self, to_copy=None):
    if to_copy == None:
      self.reset()
    else:
      self.reset_to(to_copy)

  def __str__(self):
    result = 'Cube:\n'
    for face in Cube.faces:
      neighbors = Cube.cw_neighbor_edges(face)
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

  def __eq__(self, other):
    try:
      return self.cube == other.cube
    except AttributeError:
      return False

  def is_solved(self):
    return self == Cube()

  def reset(self):
    self.cube = {}
    for face, color in zip(Cube.faces, Cube.standard_colors):
      self.set_color(color, face)
      neighbors = Cube.cw_neighbor_edges(face)
      for i in [0,2]:
        for j in [1,3]:
          self.set_color(color, face, neighbors[i], neighbors[j])
      for n in neighbors:
        self.set_color(color, face, n)

  def reset_to(self, to_copy):
    self.cube = copy.deepcopy(to_copy.cube)

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

    neighbors = Cube.cw_neighbor_edges(face)

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

  def get_dest_face(self, color):
    lookup = dict(zip(Cube.standard_colors, Cube.faces))
    return lookup[color]

  # Find the move needed to relocate (source_face, source_edge)
  # to (source_face, dest_edge)
  def get_simple_move(self, source_face, source_edge, dest_edge):
    neighbors = Cube.cw_neighbor_edges(source_face)
    source_index = neighbors.index(source_edge)
    dest_index = neighbors.index(dest_edge)
    return (source_face, (dest_index - source_index) % 4)
 
  def get_simple_move_corners(self, source_face, source_corner, dest_corner):
    source_corner = tuple(sorted(source_corner))
    dest_corner = tuple(sorted(dest_corner))
    corners = [tuple(sorted(x)) for x in Cube.cw_corners_on_face(source_face)]
    source_index = corners.index(source_corner)
    dest_index = corners.index(dest_corner)
    return (source_face, (dest_index - source_index) % 4)

  def is_cubie_in_layer(self, cubie, layer):
    return any([face == layer for face in cubie])

  def get_move_cubie_into_layer(self, source_cubie, layer):
    if self.is_cubie_in_layer(source_cubie, layer):
      return []
    opposite_layer = Cube.opposite_face(layer)
    if len(source_cubie) == 2: # edge
      source_face, source_edge = source_cubie
      if source_face == opposite_layer:
        return [(source_edge, 2)]
      elif source_edge == opposite_layer:
        return [(source_face, 2)]
      else:
        neighbors = Cube.cw_neighbor_edges(layer)
        face_index = neighbors.index(source_face)
        edge_index = neighbors.index(source_edge)
        times = (edge_index - face_index) % 4
        assert times == 1 or times == 3
        return [(source_face, times)]
    elif len(source_cubie) == 3: # corner
      non_opposites = [f for f in source_cubie if f != opposite_layer]
      print layer
      print opposite_layer
      print source_cubie
      print non_opposites
      assert len(non_opposites) == 2
      return self.get_move_cubie_into_layer(non_opposites, layer)
    else:
      raise Exception("cubie must be specified with 2 or 3 coordinates")

  @staticmethod
  def cw_neighbor_edges(face):
    return Cube._cw_neighbors[face]

  @staticmethod
  def cw_corners_on_face(face):
    neighbors = Cube.cw_neighbor_edges(face)
    return zip(neighbors, Cube.rotate_list(neighbors))

  @staticmethod
  def cw_neighbor_corners(corner):
    face, edge, edge2 = corner
    face_neighbors = Cube.cw_neighbor_edges(face)
    index1 = face_neighbors.index(edge)
    index2 = face_neighbors.index(edge2)
    if (index1 + 1) % 4 == index2:
      return [corner, (edge, face, edge2), (edge2, face, edge)] 
    elif (index1 - 1) % 4 == index2:
      return [corner, (edge2, face, edge), (edge, face, edge2)] 
    else:
      raise Exception("edges on corner must be adjacent neighbors of face")

  @staticmethod
  def opposite_face(face):
    opposites = [f for f in Cube.faces if
        (f != face and f not in Cube.cw_neighbor_edges(face))]
    assert len(opposites) == 1
    return opposites[0]

  @staticmethod
  def corners_equal(cornerA, cornerB):
    faceA, edgeA1, edgeA2 = cornerA
    faceB, edgeB1, edgeB2 = cornerB
    if faceA != faceB:
      return False
    else:
      return tuple(sorted([edgeA1, edgeA2])) == tuple(sorted([edgeB1, edgeB2]))

  @staticmethod
  def same_cubie(c1, c2):
    return sorted(c1) == sorted(c2)

  @staticmethod 
  def rotate_list(to_rotate):
    return [to_rotate[len(to_rotate)-1]] + to_rotate[:len(to_rotate)-1]

  def rotate(self, face, times=1):
    if (times < 0):
      raise "Cannot rotate a negative number of times"
    if times == 0:
      return
    
    # perform one clockwise rotation
    neighbors = Cube.cw_neighbor_edges(face)
    num_neighbors = len(neighbors)

    # first, rotate the edges
    # on-face edges
    colors = [self.get_color(face, n) for n in neighbors]
    for n, c in zip(neighbors, Cube.rotate_list(colors)):
      self.set_color(c, face, n)
    # off-face edges
    colors = [self.get_color(n, face) for n in neighbors]
    for n, c in zip(neighbors, Cube.rotate_list(colors)):
      self.set_color(c, n, face)
  
    # next, rotate the corners
    # on-face corners
    colors = [
        self.get_color(face, neighbors[i], neighbors[(i+1) % num_neighbors]) \
        for i in range(num_neighbors)]
    for i, c in zip(range(num_neighbors), Cube.rotate_list(colors)):
      self.set_color(c, face, neighbors[i], neighbors[(i+1) % num_neighbors])
    # two off-face corners (one corner closer to the CW direction, and the other
    # corner closer to the CCW direction)
    cw_offset = 1
    ccw_offset = num_neighbors-1
    for offset in [cw_offset, ccw_offset]:
      colors = []
      for n in neighbors:
        neighbors_of_neighbors = Cube.cw_neighbor_edges(n)
        index = neighbors_of_neighbors.index(face)
        edge2 = neighbors_of_neighbors[(index+offset) % num_neighbors]
        colors += [self.get_color(n, face, edge2)]
      for n, c in zip(neighbors, Cube.rotate_list(colors)):
        neighbors_of_neighbors = Cube.cw_neighbor_edges(n)
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
    prev_face = None
    for i in range(moves):
      available_faces = [] + Cube.faces
      if prev_face != None:
        available_faces.remove(prev_face)
      face = random.choice(available_faces)
      prev_face = face
      times = random.randint(1,3)
      sequence.append((face, times))
    return sequence

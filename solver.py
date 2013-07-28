from cube import Cube

class Unsolved:
  def __init__(self, source_face, source_edge, source_edge2,
      dest_face, dest_edge, dest_edge2):
    self.source_face = source_face
    self.source_edge = source_edge
    self.source_edge2 = source_edge2
    self.dest_face = dest_face
    self.dest_edge = dest_edge
    self.dest_edge2 = dest_edge2

  def __str__(self):
    return "Unsolved: source=(%s, %s, %s), dest=(%s, %s, %s)" \
        % (self.source_face, self.source_edge, self.source_edge2,
            self.dest_face, self.dest_edge, self.dest_edge2)

class PhaseSolver:
  max_attempts = 20

  def run(self, cube, debug_display=None):
    solution = []
    unsolved = self.find_unsolved(cube)
    attempts = 0
    if debug_display is not None:
      debug_display.draw()
    while len(unsolved) > 0:
      new_steps = self.solve_case(cube, unsolved)
      solution += new_steps
      cube.apply_sequence(new_steps)
      if debug_display is not None:
        debug_display.draw()
      unsolved = self.find_unsolved(cube)
      attempts += 1
      if attempts >= self.max_attempts:
        print "WARNING: exceeded max_attempts"
        break
    return solution

class LowerEdges(PhaseSolver):
  def find_unsolved(self, cube):
    unsolved = []
    for face in Cube.faces:
      for edge in Cube.cw_neighbor_edges(face):
        if cube.get_color(face, edge) == 'white':
          dest_face = 'down'
          other_color = cube.get_color(edge, face)
          dest_edge = cube.get_dest_face(other_color)
          if face != dest_face or edge != dest_edge:
            unsolved.append(
                Unsolved(face, edge, None, dest_face, dest_edge, None))

    def sorter(u):
      if u.source_face == 'down': return 0
      elif u.source_face == 'up': return 1
      elif u.source_edge == 'up': return 2
      elif u.source_edge != 'down': return 3
      else: return 4
      
    unsolved.sort(key=sorter)

    return unsolved

  def solve_case(self, cube, unsolved):
    case = unsolved[0]
    steps = []
    if case.source_face == 'down':
      steps.append(cube.get_simple_move(
          'down', case.source_edge, case.dest_edge))
    elif case.source_face == 'up':
      steps.append(cube.get_simple_move(
          'up', case.source_edge, case.dest_edge))
      steps.append((case.dest_edge, 2))
    elif case.source_edge == 'up':
      neighbors = Cube.cw_neighbor_edges('up')
      index = neighbors.index(case.dest_edge)
      dest_edge_offset = neighbors[(index + 1) % 4]
      steps.append(cube.get_simple_move(
          'up', case.source_face, dest_edge_offset))
      steps.append((dest_edge_offset, 1))
      steps.append((case.dest_edge, 3))
      steps.append((dest_edge_offset, 3))
    else:
      face, times = cube.get_simple_move(case.source_face, case.source_edge, 'up')
      steps.append((face, times))
      steps.append(('up', 1))
      steps.append((face, -times % 4))
    return steps

class LowerCorners(PhaseSolver):
  def find_unsolved(self, cube):
    print "Finding unsolved " + self.__class__.__name__
    unsolved = []
    for face in Cube.faces:
      for edge, edge2 in Cube.cw_corners_on_face(face):
        if cube.get_color(face, edge, edge2) == 'white':
          dest_face = 'down'

          other_color = cube.get_color(edge, face, edge2)
          dest_edge = cube.get_dest_face(other_color)

          other_color2 = cube.get_color(edge2, face, edge)
          dest_edge2 = cube.get_dest_face(other_color2)

          already_solved = Cube.corners_equal( \
              (face, edge, edge2), (dest_face, dest_edge, dest_edge2))
          if not already_solved:
            new_case = Unsolved(face, edge, edge2, dest_face, dest_edge, dest_edge2)
            print new_case
            unsolved.append(new_case)

    def sorter(u):
      source_cubie = (u.source_face, u.source_edge, u.source_edge2)
      dest_cubie = (u.dest_face, u.dest_edge, u.dest_edge2)
      if cube.is_cubie_in_layer(source_cubie, 'up'):
        assert dest_cubie[0] == 'down'
        cubie_above_dest = ('up', u.dest_edge, u.dest_edge2)
        if Cube.same_cubie(source_cubie, cubie_above_dest):
          return 0
        else:
          return 1
      else:
        return 2
      
    unsolved.sort(key=sorter)

    return unsolved

  def solve_case(self, cube, unsolved):
    case = unsolved[0]
    print "DEBUG: case = " + str(case)
    source_cubie = (case.source_face, case.source_edge, case.source_edge2)
    if cube.is_cubie_in_layer(source_cubie, 'up'):
      corner_neighbors = Cube.cw_neighbor_corners(source_cubie)
      upper_corners = [c for c in corner_neighbors if c[0] == 'up']
      assert (len(upper_corners) == 1)
      upper_corner = upper_corners[0]
      setup_move = cube.get_simple_move_corners(
          'up', (upper_corner[1], upper_corner[2]), \
          (case.dest_edge, case.dest_edge2))
      times = setup_move[1]
      if times != 0:
        print "DEBUG: returning setup_move " + str([setup_move])
        return [setup_move]
      upper_corner_index = corner_neighbors.index(upper_corner)
      if upper_corner_index == 0:
        edge_below = tuple([f for f in source_cubie if f != 'up'])
        assert len(edge_below) == 2
        setup_sequence = cube.get_move_cubie_into_layer(edge_below, 'up')
        print "DEBUG: edge_below = {0}, setup_sequence = {1}".format(edge_below, setup_sequence)
        steps = setup_sequence + [('up', 2)] + \
            Solver.reverse_sequence(setup_sequence)
      elif upper_corner_index == 1:
        steps = [(case.source_face, 3), ('up', 3), (case.source_face, 1)]
      elif upper_corner_index == 2:
        steps = [(case.source_face, 1), ('up', 1), (case.source_face, 3)]
      else:
        raise Exception("upper_corner_index should be 0, 1, or 2")
      print "DEBUG: returning upper_corner_index " + str(upper_corner_index) + \
          ", steps = " + str(steps)
      return steps
    else:
      setup_sequence = cube.get_move_cubie_into_layer(
          (case.source_face, case.source_edge, case.source_edge2), 'up')
      print "DEBUG: setup_sequence = " + str(setup_sequence)
      steps = setup_sequence + [('up', 1)] + \
          Solver.reverse_sequence(setup_sequence)
      print "DEBUG: returning steps = " + str(steps)
      return steps

class MiddleEdges(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, unsolved):
    return []

class UpperEdgesOrientation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, unsolved):
    return []

class UpperEdgesPermutation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, unsolved):
    return []

class UpperCornersOrientation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, unsolved):
    return []

class UpperCornersPermutation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, unsolved):
    return []

class Solver:
  phase_solvers = [
    LowerEdges(),
    LowerCorners(),
    MiddleEdges(),
    UpperEdgesOrientation(),
    UpperEdgesPermutation(),
    UpperCornersOrientation(),
    UpperCornersPermutation(),
  ]

  def __init__(self, debug_display=None):
    self.debug_display = debug_display

  # Note: A "move with N y-rotations" denotes N clockwise rotations around
  # the up-down axis (as viewed from above), followed by the original move,
  # followed by N counterclockwise rotations around the up-down axis.
  @staticmethod
  def move_with_y_rotation(move, num_rotations=1):
    num_rotations = num_rotations % 4
    face, times = move
    if num_rotations == 0 or face == 'up' or face == 'down':
      return move

    up_cw_neighbor_edges = Cube.cw_neighbor_edges('up')
    new_face_index = (up_cw_neighbor_edges.index(face) - num_rotations) % 4
    return (up_cw_neighbor_edges[new_face_index], times)

  @staticmethod
  def sequence_with_y_rotation(sequence, num_rotations=1):
    return [Solver.move_with_y_rotation(move, num_rotations) \
        for move in sequence]

  @staticmethod
  def reverse_sequence(sequence):
    return [(face, -times % 4) for (face, times) in reversed(sequence)]

  def find_solution(self, cube):
    solution = []
    initial_cube = Cube(cube)  # save a copy so we can reset later

    for phase_solver in self.phase_solvers:
      print "About to solve phase: " + phase_solver.__class__.__name__
      solution += phase_solver.run(cube, debug_display=self.debug_display)

    if not cube.is_solved():
      print 'WARNING: could not fully solve the cube'

    cube.reset_to(initial_cube)
    if self.debug_display is not None:
      self.debug_display.draw()

    return solution

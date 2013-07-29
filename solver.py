from cube import Cube
import sys
import traceback

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
  max_attempts = 30

  def run(self, cube, debug_display=None, print_debug=False):
    solution = []
    if print_debug: print "DEBUG: about to call " + self.__class__.__name__ + ".find_unsolved"
    unsolved = self.find_unsolved(cube, print_debug=print_debug)
    attempts = 0
    if debug_display is not None:
      debug_display.draw()
    while len(unsolved) > 0:
      if print_debug: print "DEBUG: about to call " + self.__class__.__name__ + ".solve_case"
      new_steps = self.solve_case(cube, unsolved, print_debug=print_debug)
      solution += new_steps
      cube.apply_sequence(new_steps)
      if debug_display is not None:
        debug_display.draw()
      if print_debug: print "DEBUG: about to call " + self.__class__.__name__ + ".find_unsolved"
      unsolved = self.find_unsolved(cube, print_debug=print_debug)
      attempts += 1
      if attempts >= self.max_attempts:
        raise Exception("exceeded max_attempts = {0}".format(self.max_attempts))
    return solution

class LowerEdges(PhaseSolver):
  def find_unsolved(self, cube, print_debug=False):
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
      if u.source_face == 'up': return 0
      elif u.source_face == 'down': return 1
      elif u.source_edge == 'up': return 2
      elif u.source_edge != 'down': return 3
      else: return 4
      
    unsolved.sort(key=sorter)

    return unsolved

  def solve_case(self, cube, unsolved, print_debug=False):
    case = unsolved[0]
    steps = []
    if case.source_face == 'up':
      steps.append(cube.get_simple_move(
          'up', case.source_edge, case.dest_edge))
      steps.append((case.dest_edge, 2))
    elif case.source_face == 'down':
      steps.append((case.source_edge, 2))
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
  def find_unsolved(self, cube, print_debug=False):
    #print "Finding unsolved " + self.__class__.__name__
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
            #print new_case
            unsolved.append(new_case)

    def sorter(u):
      source_cubie = (u.source_face, u.source_edge, u.source_edge2)
      dest_cubie = (u.dest_face, u.dest_edge, u.dest_edge2)
      if cube.is_cubie_in_layer(source_cubie, 'up'):
        assert dest_cubie[0] == 'down'
        cubie_above_dest = ('up', u.dest_edge, u.dest_edge2)
        if u.source_face != 'up':
          if Cube.same_cubie(source_cubie, cubie_above_dest):
            return 0
          else:
            return 1
        else:
          if Cube.same_cubie(source_cubie, cubie_above_dest):
            return 2
          else:
            return 3
      else:
        return 4
      
    unsolved.sort(key=sorter)

    return unsolved

  def solve_case(self, cube, unsolved, print_debug=False):
    case = unsolved[0]
    if print_debug: print "DEBUG: case = " + str(case)
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
        if print_debug: print "DEBUG: returning setup_move " + str([setup_move])
        return [setup_move]
      upper_corner_index = corner_neighbors.index(upper_corner)
      if upper_corner_index == 0:
        edge_below = tuple([f for f in source_cubie if f != 'up'])
        assert len(edge_below) == 2
        setup_sequence = cube.get_move_cubie_into_layer(edge_below, 'up')
        if print_debug: print "DEBUG: edge_below = {0}, setup_sequence = {1}".format(edge_below, setup_sequence)
        steps = setup_sequence + [('up', 2)] + \
            Solver.reverse_sequence(setup_sequence)
      elif upper_corner_index == 1:
        steps = [(case.source_face, 3), ('up', 3), (case.source_face, 1)]
      elif upper_corner_index == 2:
        steps = [(case.source_face, 1), ('up', 1), (case.source_face, 3)]
      else:
        raise Exception("upper_corner_index should be 0, 1, or 2")
      if print_debug: print "DEBUG: returning upper_corner_index " + str(upper_corner_index) + ", steps = " + str(steps)
      return steps
    else:
      setup_sequence = cube.get_move_cubie_into_layer(source_cubie, 'up')
      if print_debug: print "DEBUG: setup_sequence = " + str(setup_sequence)
      steps = setup_sequence + [('up', 1)] + \
          Solver.reverse_sequence(setup_sequence)
      if print_debug: print "DEBUG: returning steps = " + str(steps)
      return steps

class MiddleEdges(PhaseSolver):
  def find_unsolved(self, cube, print_debug=False):
    edges = []
    edges.extend([('up', f) for f in Cube.cw_neighbor_edges('up')])
    edges.extend([c for c in Cube.cw_corners_on_face('up')])
    edges.extend([('down', f) for f in Cube.cw_neighbor_edges('down')])

    unsolved = []
    for f1, f2 in edges:
      color1 = cube.get_color(f1, f2)
      color2 = cube.get_color(f2, f1)
      dest_f1 = cube.get_dest_face(color1)
      dest_f2 = cube.get_dest_face(color2)
      already_solved = (f1 == dest_f1 and f2 == dest_f2)
      if not already_solved:
        assert f1 != 'down' and f2 != 'down'
        assert dest_f1 != 'down' and dest_f2 != 'down'
        if dest_f1 != 'up' and dest_f2 != 'up':
          unsolved.append(Unsolved(f1, f2, None, dest_f1, dest_f2, None))

    def sorter(u, print_debug=False):
      if cube.is_cubie_in_layer((u.source_face, u.source_edge), 'up'):
        if u.source_face == 'up':
          non_up = u.source_edge
          non_up_dest = u.dest_edge
        else:
          non_up = u.source_face
          non_up_dest = u.dest_face
        if non_up == non_up_dest:
          return 0  # in top layer and aligned
        else:
          return 1  # in top layer but not aligned
      else:
        return 2  # not in top layer

    # NOTE: Sorting by the worst-case number of times "solve_case" must be
    # invoked to solve each cubie.
    unsolved.sort(key=sorter)

    return unsolved

  def solve_case(self, cube, unsolved, print_debug=False):
    case = unsolved[0]
    source_cubie = (case.source_face, case.source_edge)
    source_face, source_edge = source_cubie
    dest_cubie = (case.dest_face, case.dest_edge)
    dest_face, dest_edge = dest_cubie

    if cube.is_cubie_in_layer(source_cubie, 'up'):
      up_index = source_cubie.index('up')
      assert up_index == 0 or up_index == 1
      non_up_index = (up_index + 1) % 2
      non_up = source_cubie[non_up_index]
      non_up_dest = dest_cubie[non_up_index]
      if non_up == non_up_dest:  # in top layer and aligned
        up_dest = dest_cubie[up_index]
        seq1 = [cube.get_simple_move('up', non_up, up_dest)]
        seq2 = cube.get_move_cubie_into_layer((up_dest, non_up_dest), 'up')
        seq3 = cube.get_move_cubie_into_layer((non_up_dest, up_dest), 'up')
        return Solver.reverse_sequence(seq1) + seq2 + seq1 + \
            Solver.reverse_sequence(seq2) + Solver.reverse_sequence(seq3) + \
            Solver.reverse_sequence(seq2) + seq3 + seq2
      else:  # in top layer but not aligned
        return [cube.get_simple_move('up', non_up, non_up_dest)]

    else:
      seq1 = [cube.get_simple_move('up', source_edge, source_face)]
      seq2 = cube.get_move_cubie_into_layer((source_face, source_edge), 'up')
      seq3 = cube.get_move_cubie_into_layer((source_edge, source_face), 'up')
      setup_sequence = cube.get_move_cubie_into_layer(source_cubie, 'up')
      return Solver.reverse_sequence(seq1) + seq2 + seq1 + \
          Solver.reverse_sequence(seq2) + Solver.reverse_sequence(seq3) + \
          Solver.reverse_sequence(seq2) + seq3 + seq2

class UpperEdgesOrientation(PhaseSolver):
  def find_unsolved(self, cube, print_debug=False):
    unsolved = []
    for n in Cube.cw_neighbor_edges('up'):
      up_color = cube.get_color('up', n)
      if up_color != 'yellow':
        unsolved.append(Unsolved(n, 'up', None, 'up', n, None))
    return unsolved

  def solve_case(self, cube, unsolved, print_debug=False):
    if print_debug: print "DEBUG: unsolved = " + str([str(u) for u in unsolved])
    if len(unsolved) == 4:
      if print_debug: print "DEBUG: len(unsolved) == 4"
      return [('front', 1), ('right', 1), ('up', 1),
          ('right', 3), ('up', 3), ('front', 3)]
    elif len(unsolved) == 2:
      f0 = unsolved[0].source_face
      f1 = unsolved[1].source_face
      _, times = cube.get_simple_move('up', f0, f1)
      if print_debug: print "DEBUG: f0 = {0}, f1 = {1}, times = {2}".format(f0, f1, times)
      if times == 1 or times == 3:
        if times == 3:
          f0, f1 = f1, f0  # we want f1 to be immediate CW neighbor of f0

        if f0 == 'right':
          return [('front', 1), ('up', 1), ('right', 1),
              ('up', 3), ('right', 3), ('front', 3)]
        else:
          return [cube.get_simple_move('up', f0, 'right')]
      else:
        assert times == 2
        if f0 == 'front' or f1 == 'front':
          return [('front', 1), ('right', 1), ('up', 1),
              ('right', 3), ('up', 3), ('front', 3)]
        else:
          return [('up', 1)]
    raise Exception("num unsolved should be 2 or 4, was " + str(len(unsolved)))

class UpperEdgesPermutation(PhaseSolver):
  def __init__(self, allow_complex_permutations=True):
    self.allow_complex_permutations = allow_complex_permutations

  def find_unsolved(self, cube, print_debug=False):
    unsolved = []
    num_unsolved = 0
    for n in Cube.cw_neighbor_edges('up'):
      non_up_color = cube.get_color(n, 'up')
      dest_face = cube.get_dest_face(non_up_color)
      if dest_face != n:
        num_unsolved += 1
      unsolved.append(Unsolved(n, 'up', None, dest_face, 'up', None))
    # either return all edges, or none of them
    if num_unsolved > 0:
      return unsolved
    else:
      return []

  def solve_case(self, cube, unsolved, print_debug=False):
    assert len(unsolved) == 4
    turns = []
    for u in unsolved:
      _, num_turns = cube.get_simple_move('up', u.source_face, u.dest_face)
      turns.append(num_turns)

    # Simplest case: all edges need to be turned by the same amount
    if len(set(turns)) == 1:
      return [('up', turns[0])]

    if not self.allow_complex_permutations:
      raise Exception("trying to solve disallowed complex permutation")

    turns, min_index = Solver.normalize_turns(turns)

    other_face = unsolved[(min_index + 3) % 4].source_face
    if turns == [0, 0, 1, 3] or turns == [0, 1, 3, 0]:
      return [('up', 1)]
    elif turns == [0, 2, 3, 3]:
      # counter-clockwise
      return [(other_face, 1), ('up', 1), (other_face, 3),
          ('up', 1), (other_face, 1), ('up', 2), (other_face, 3)]
    elif turns == [0, 1, 1, 2] or turns == [0, 2, 0, 2]:
      # clockwise or swap edges
      return [(other_face, 1), ('up', 2), (other_face, 3),
          ('up', 3), (other_face, 1), ('up', 3), (other_face, 3)]
    else:
      raise Exception("unrecognized turns pattern: " + str(turns))

class UpperCornersOrientation(PhaseSolver):
  def find_unsolved(self, cube, print_debug=False):
    unsolved = []
    for dest_edge, dest_edge2 in Cube.cw_corners_on_face('up'):
      #print dest_edge, dest_edge2
      if cube.get_color('up', dest_edge, dest_edge2) != 'yellow':
        corner_neighbors = Cube.cw_neighbor_corners(
            ('up', dest_edge, dest_edge2))
        #print corner_neighbors
        colors = [cube.get_color(face, edge, edge2)
            for face, edge, edge2 in corner_neighbors]
        #print colors
        yellow_index = colors.index('yellow')
        assert yellow_index == 1 or yellow_index == 2
        yellow_corner = corner_neighbors[yellow_index]
        unsolved.append(Unsolved(
            yellow_corner[0], yellow_corner[1], yellow_corner[2],
            'up', dest_edge, dest_edge2))
    return unsolved

  def solve_case(self, cube, unsolved, print_debug=False):
    if print_debug: print "DEBUG: unsolved = " + str([str(u) for u in unsolved])
    case = unsolved[0]

    source_corner = (case.source_face, case.source_edge, case.source_edge2)
    dest_corner = (case.dest_face, case.dest_edge, case.dest_edge2)

    source_non_upper_edges = tuple([f for f in source_corner if f != 'up'])
    setup_sequence = [cube.get_simple_move_corners('up',
        source_non_upper_edges, ('right', 'back'))]

    dest_corner_neighbors = Cube.cw_neighbor_corners(dest_corner)
    corner_index = dest_corner_neighbors.index(source_corner)
    assert corner_index == 1 or corner_index == 2

    if corner_index == 1:
      steps = [('down', 1), ('right', 1), ('down', 3), ('right', 3),
          ('down', 1), ('right', 1), ('down', 3), ('right', 3)]
    else:
      steps = [('right', 1), ('down', 1), ('right', 3), ('down', 3),
          ('right', 1), ('down', 1), ('right', 3), ('down', 3)]

    return setup_sequence + steps

class UpperCornersPermutation(PhaseSolver):
  def find_unsolved(self, cube, print_debug=False):
    unsolved = []
    num_unsolved = 0
    for edge, edge2 in Cube.cw_corners_on_face('up'):
      color_edge = cube.get_color(edge, edge2, 'up')
      color_edge2 = cube.get_color(edge2, edge, 'up')
      dest_edge = cube.get_dest_face(color_edge)
      dest_edge2 = cube.get_dest_face(color_edge2)
      if edge != dest_edge and edge2 != dest_edge2:
        num_unsolved += 1
      else:
        assert edge == dest_edge and edge2 == dest_edge2
      unsolved.append(Unsolved(
          'up', edge, edge2, 'up', dest_edge, dest_edge2))
    # return either all edges or none
    if num_unsolved > 0:
      return unsolved
    else:
      return []

  def solve_case(self, cube, unsolved, print_debug=False):
    if print_debug: print "DEBUG: unsolved = " + str([str(u) for u in unsolved])

    turns = []
    for u in unsolved:
      _, num_turns = cube.get_simple_move_corners('up',
          (u.source_edge, u.source_edge2), (u.dest_edge, u.dest_edge2))
      turns.append(num_turns)

    turns, min_index = Solver.normalize_turns(turns, subtract_min=False)

    seq = [('right', 3), ('down', 2), ('right', 1)]
    u1 = [('up', 1)]
    u2 = [('up', 2)]
    u3 = [('up', 3)]

    if turns == [0, 1, 1, 2] or turns == [1, 3, 1, 3] \
        or turns == [2, 2, 2, 2]:
      # clockwise, adjacent corners, or opposite corners
      steps = seq + u2 + seq + u3 + seq + u3 + seq
    elif turns == [0, 2, 3, 3]:  # counterclockwise
      steps = seq + u1 + seq + u1 + seq + u2 + seq
    else:
      raise Exception("unrecognized turns " + str(turns))

    return Solver.sequence_with_y_rotation(steps, min_index)

class Solver:
  phase_solvers = [
    LowerEdges(),
    LowerCorners(),
    MiddleEdges(),
    UpperEdgesOrientation(),
    UpperEdgesPermutation(),
    UpperCornersOrientation(),
    UpperEdgesPermutation(allow_complex_permutations=False),
    UpperCornersPermutation(),
  ]

  def __init__(self, debug_display=None, print_debug=False):
    self.debug_display = debug_display
    self.print_debug = print_debug

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

  @staticmethod
  def normalize_turns(turns, subtract_min=True):
      min_turns = min(turns)
      min_index = turns.index(min_turns)
      if min_index == 0 and turns[3] == min_turns:
        # special case when two adjacent min_turns wrap around
        min_index = 3
      if subtract_min:
        normalized = [turns[(i + min_index) % 4] - min_turns
            for i in range(len(turns))]
      else:
        normalized = [turns[(i + min_index) % 4] for i in range(len(turns))]
      return normalized, min_index

  def find_solution(self, cube):
    solution = []
    initial_cube = Cube(cube)  # save a copy so we can reset later

    try:
      for phase_solver in self.phase_solvers:
        #print "About to solve phase: " + phase_solver.__class__.__name__
        solution += phase_solver.run(cube, debug_display=self.debug_display,
          print_debug=self.print_debug)
    except Exception as e:
      print "WARNING: encountered exception:"
      traceback.print_exc(file=sys.stdout)

    if not cube.is_solved():
      print 'WARNING: could not fully solve the cube'

    cube.reset_to(initial_cube)
    if self.debug_display is not None:
      self.debug_display.draw()

    return solution

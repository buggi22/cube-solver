from cube import Cube

class Solver:
  BOTTOM_CORNER_1 = [('right', 1), ('up', 1), ('right', 3)]
  BOTTOM_CORNER_2 = [('front', 3), ('up', 3), ('front', 1)]

  # Note: A "move with N y-rotations" denotes N clockwise rotations around
  # the up-down axis (as viewed from above), followed by the original move,
  # followed by N counterclockwise rotations around the up-down axis.
  def move_with_y_rotation(self, move, num_rotations=1):
    num_rotations = num_y_rotations % 4
    face, times = move
    if num_rotations == 0 or face == 'up' or face == 'down':
      return move

    up_cw_neighbors = Cube.cw_neighbors['up']
    new_face_index = (up_cw_neighbors.index(face) - num_rotations) % 4
    return (up_cw_neighbors[new_face_index], times)

  def sequence_with_y_rotation(self, sequence, num_rotations=1):
    return [self.move_with_y_rotation(move, num_rotations) \
        for move in sequence]

  @staticmethod
  def find_solution(cube):
    solution = []

    phase_solvers = [
        LowerEdges(),
        LowerCorners(),
        MiddleEdges(),
        UpperEdgesOrientation(),
        UpperEdgesPermutation(),
        UpperCornersOrientation(),
        UpperCornersPermutation(),
    ]
    for phase_solver in phase_solvers:
      solution += phase_solver.run(cube)

    if not cube.is_solved():
      print 'Warning: could not fully solve the cube'

    return solution

class PhaseSolver:
  max_attempts = 100

  def run(self, cube):
    solution = []
    unsolved = self.find_unsolved(cube)
    attempts = 0
    while len(unsolved) > 0:
      solution += self.solve_case(cube, unsolved[0])
      unsolved = self.find_unsolved(cube)
      attempts += 1
      if attempts >= self.max_attempts:
        raise Exception("exceeded max_attempts")
    return solution

class LowerEdges(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, case):
    return []

class LowerCorners(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, case):
    return []

class MiddleEdges(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, case):
    return []

class UpperEdgesOrientation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, case):
    return []

class UpperEdgesPermutation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, case):
    return []

class UpperCornersOrientation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, case):
    return []

class UpperCornersPermutation(PhaseSolver):
  def find_unsolved(self, cube):
    return []

  def solve_case(self, cube, case):
    return []

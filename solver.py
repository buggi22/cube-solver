from cube import Cube

class Solver:
  BOTTOM_CORNER_1 = [('right', 1), ('up', 1), ('right', 3)]
  BOTTOM_CORNER_2 = [('front', 3), ('up', 3), ('front', 1)]

  def __init__(self, cube):
    self.cube = cube
    self.reset()

  def reset(self):
    self.solution = []

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

  def find_solution(self):
    self.reset()

    # TODO

    return self.solution

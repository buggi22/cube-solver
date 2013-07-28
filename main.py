import graphics
from cube import Cube
from solver import Solver

def run_sequence(sequence, cube, display):
  for move in sequence:
    display.wait_for_key()
    face, times = move
    cube.rotate(face, times)
    display.draw()
  display.wait_for_key()

cube = Cube()
display = graphics.CubeDisplay(cube)

sequence = cube.generate_scramble_sequence(moves=10)
print 'Scrambling sequence: ' + str(sequence)
run_sequence(sequence, cube, display)

solution = Solver(debug_display=display).find_solution(cube)
print 'Solution sequence: ' + str(solution)
run_sequence(solution, cube, display)

display.wait_until_quit()

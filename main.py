import graphics
from cube import Cube
from solver import Solver

def run_sequence(sequence, cube, display):
  for move in sequence:
    raw_input('press enter ')
    print move
    face, times = move
    cube.rotate(face, times)
    display.draw()
  raw_input('press enter ')

cube = Cube()
display = graphics.CubeDisplay(cube)

sequence = cube.generate_scramble_sequence(moves=10)
print 'Scrambling sequence: ' + str(sequence)
run_sequence(sequence, cube, display)

solution = Solver().find_solution(cube)
print 'Solution sequence: ' + str(solution)
run_sequence(solution, cube, display)

display.wait_until_quit()

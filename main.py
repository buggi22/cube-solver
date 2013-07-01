import graphics
from cube import Cube

cube = Cube()
display = graphics.CubeDisplay(cube)
raw_input('press enter')

cube.reset()
sequence = cube.generate_scramble_sequence(moves=10)
print sequence
for move in sequence:
  print move
  face, times = move
  cube.rotate(face, times)
  display.draw()
  text = raw_input('press enter ')
  if text == 'y':
    print cube

display.wait_until_quit()

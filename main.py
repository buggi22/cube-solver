import graphics
from cube import Cube

cube = Cube()
display = graphics.CubeDisplay(cube)
raw_input('press enter')

#for face in Cube.faces:
#  for times in [1,2,3]:
#    cube.rotate(face, times)
#    display.draw()
#    raw_input('press enter')
#
#for face in Cube.faces:
#  cube.reset()
#  display.draw()
#  raw_input('press enter')
#  cube.rotate(face)
#  display.draw()
#  raw_input('press enter')

cube.reset()
#sequence = cube.generate_scramble_sequence(moves=10)
#print sequence
sequence = [('front', 1), ('left', 1)]
for move in sequence:
  print move
  face, times = move
  cube.rotate(face, times)
  display.draw()
  text = raw_input('press enter ')
  if text == 'y':
    print cube

display.wait_until_quit()

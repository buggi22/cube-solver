import graphics
from cube import Cube

cube = Cube()
display = graphics.CubeDisplay(cube)
raw_input('press enter')

for face in Cube.faces:
  for times in [1,2,3]:
    cube.rotate(face, times)
    display.draw()
    raw_input('press enter')

for face in Cube.faces:
  cube.reset()
  display.draw()
  raw_input('press enter')
  cube.rotate(face)
  display.draw()
  raw_input('press enter')

sequence = cube.scramble()
display.draw()
print sequence
raw_input('press enter')
display.wait_until_quit()

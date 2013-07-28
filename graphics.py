import pygame, sys
from pygame.locals import *
from cube import Cube

class RGB:
  UNKNOWN_RGB = (150, 150, 150)
  BLACK = (0, 0, 0)
  colors_rgb = {
    'unknown': UNKNOWN_RGB,
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'orange': (255, 150, 0),
  }
 
  @staticmethod
  def get(color):
    return RGB.colors_rgb.get(color, RGB.UNKNOWN_RGB)

class CubeDisplay:
  small_cube_width = 20
  small_cube_height = 30
  isometric_slope = 1.0/2.0
  isometric_rise = small_cube_width * isometric_slope
  outer_margin_in_small_cube_widths = 2
  inner_margin_in_small_cube_widths = 2

  total_cube_width = small_cube_width * 6
  total_cube_height = small_cube_height * 3 + isometric_rise * 6
  outer_margin_width = outer_margin_in_small_cube_widths * small_cube_width
  inner_margin_width = inner_margin_in_small_cube_widths * small_cube_width

  def __init__(self, cube):
    self.cube = cube
    self.windowSurface = None
    self.init_pygame()
    self.draw()

  def init_pygame(self):
    if self.windowSurface == None:
      pygame.init()
      window_dimensions = ( \
         int(2*self.outer_margin_width + self.inner_margin_width \
             + 2*self.total_cube_width), \
         int(2*self.outer_margin_width + self.total_cube_height))
      self.windowSurface = pygame.display.set_mode(window_dimensions)
      pygame.display.set_caption('Cubes!')
      pygame.key.set_repeat(200, 50)

  def draw(self):
    self.windowSurface.fill(RGB.get('white'))

    for face in Cube.faces:
      for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
          color = self.cube.get_color_from_coords(face, i, j)
          self.draw_oblique_square(color, i, j, face)

    pygame.display.update()

  def draw_oblique_square(self, color, center_x, center_y, face):
    width = CubeDisplay.small_cube_width
    height = CubeDisplay.small_cube_height
    slope = CubeDisplay.isometric_slope
    rise = CubeDisplay.isometric_rise

    if face in ['right', 'front', 'up']:
      delta_x = self.outer_margin_width + self.total_cube_width / 2
      delta_y = self.outer_margin_width + self.total_cube_height / 2 \
          + rise * 1.5
    elif face in ['left', 'back', 'down']:
      delta_x = self.outer_margin_width + self.total_cube_width * 1.5 \
          + self.inner_margin_width
      delta_y = self.outer_margin_width + self.total_cube_height / 2 \
          - rise * 1.5

    if face == 'up':
      delta_y -= height * 2
    elif face == 'down':
      delta_y += height * 2
    elif face == 'front':
      delta_x -= width * 1.5
    elif face == 'back':
      delta_x -= width * 1.5
    elif face == 'right':
      delta_x += width * 1.5
    elif face == 'left':
      delta_x += width * 1.5

    if face == 'left' or face == 'front':
      # pieces that slope down and to the right
      points = [
        (-width/2, -height/2 - rise/2),
        (width/2, -height/2 + rise/2),
        (width/2, height/2 + rise/2),
        (-width/2, height/2 - rise/2),
      ]
      delta_x += width * center_x
      delta_y += height * center_y + rise * center_x
    elif face == 'up' or face == 'down':
      # "level" pieces
      points = [
        (0, -rise),
        (width, 0),
        (0, rise),
        (-width, 0),
      ]
      delta_x += width * (center_x + center_y)
      delta_y += rise * (-center_x + center_y)
    elif face == 'right' or face == 'back':
      # pieces that slope up and to the right
      points = [
        (-width/2, -height/2 + rise/2),
        (width/2, -height/2 - rise/2),
        (width/2, height/2 - rise/2),
        (-width/2, height/2 + rise/2),
      ]
      delta_x += width * center_x
      delta_y += height * center_y - rise * center_x
    else:
      raise "Unrecognized face " + str(face)

    points = [(int(x + delta_x), int(y + delta_y)) for (x,y) in points]
    color_rgb = color if isinstance(color, tuple) else RGB.get(color)
    pygame.draw.polygon(self.windowSurface, color_rgb, points)
    pygame.draw.polygon(self.windowSurface, RGB.BLACK, points, 2)

  def quit(self):
    pygame.quit()
    sys.exit(0)
    self.windowSurface = None

  def wait_for_key(self):
    done = False
    while not done:
      pygame.time.wait(10)
      for event in pygame.event.get():
        if event.type == QUIT:
          self.quit()
          done = True
        elif event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            self.quit()
          done = True

  def wait_until_quit(self):
    done = False
    while not done:
      pygame.time.wait(10)
      for event in pygame.event.get():
        if event.type == QUIT:
          self.quit()
          done = True
        elif event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            self.quit()
            done = True

from cube import Cube
from solver import Solver
import random

num_trials = 1000
scramble_moves_per_trial = 100

results = []

successes = 0
attempts = 0

for i in range(1, num_trials + 1):
  cube = Cube()
 
  scramble = cube.generate_scramble_sequence(
      moves=scramble_moves_per_trial, seed=i)
  
  cube.apply_sequence(scramble)
 
  result = "" 
  if cube.is_solved():
    result += "NOTE: cube was already solved! "
  
  solution = Solver().find_solution(cube)
  attempts += 1
  
  cube.apply_sequence(solution)
  success = cube.is_solved()
  if success:
    result += "Successfully solved!"
    successes += 1
  else:
    result += "Could not solve"

  results.append((i, success, result))

  print ("Progress: finished {0} trials, with {1} successes " + \
      "and {2} failures").format(attempts, successes, attempts - successes)

print ("Summary: finished {0} trials, with {1} successes " + \
    "and {2} failures").format(attempts, successes, attempts - successes)
if successes < attempts:
  print "Failures:"
  for seed, success, result in results:
    if not success:
      print "seed = {0}: {1}".format(seed, result)

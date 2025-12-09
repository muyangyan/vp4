import plado
from plado.parser import parse, parse_and_normalize
domain, problem = parse("data/deterministic/blocksworld/blocksworld.pddl", "data/deterministic/maze/maze.pddl")
# alternatively, with performing additional normalization steps
# domain, problem = parse_and_normalize(PATH_TO_DOMAIN, PATH_TO_PROBLEM)


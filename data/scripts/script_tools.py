# module to help parse pokered source

import os

# find path to top level based on where we are
# this should work even if someone renamed the repo directory
cwd = os.getcwd().split("/")
if cwd[-1] == "scripts":
    TOP_PATH = "../../"
elif cwd[-1] == "data":
    TOP_PATH = "../"
else: # assume we are in top directory
    TOP_PATH =  ""

# paths to data files
POKERED_PATH = TOP_PATH + "external/pokered/"

MOVE_CONSTANTS_FILE = POKERED_PATH + "constants/move_constants.asm"
MOVE_DATA_FILE = POKERED_PATH + "data/moves/moves.asm"

POKEMON_CONSTANTS_FILE = POKERED_PATH + "constants/pokemon_constants.asm"
POKEDEX_CONSTANTS_FILE = POKERED_PATH + "constants/pokedex_constants.asm"
POKEMON_BASE_STATS_DIR = POKERED_PATH + "data/pokemon/base_stats/"
POKEMON_EVOS_MOVES_FILE = POKERED_PATH + "data/pokemon/evos_moves.asm"

TRAINER_CONSTANTS_FILE = POKERED_PATH + "constants/trainer_constants.asm"
TRAINER_AI_FILE = POKERED_PATH + "data/trainers/ai_pointers.asm"
TRAINER_PARTIES_FILE = POKERED_PATH + "data/trainers/parties.asm"


# info for pickling
PICKLE_PATH = TOP_PATH + "data/"
PICKLE_EXT = ".pkl" # in case we decide to change it later

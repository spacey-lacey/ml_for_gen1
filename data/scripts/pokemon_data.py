#!/bin/python
import re
import pandas
import pickle
from pathlib import Path
from local_pathfinder import find_data_path, find_pokered_path


# find the files we need
pokered_path = find_pokered_path()
pokemon_constants_path = pokered_path / "constants/pokemon_constants.asm"
pokedex_constants_path = pokered_path / "constants/pokedex_constants.asm"
pokemon_base_stats_dir_path = pokered_path / "data/pokemon/base_stats"
pokemon_evos_moves_path = pokered_path / "data/pokemon/evos_moves.asm"

# places to store info we read in
pokemon_names = []
index = {}
dex_no = {}
typing = {} # "type" is reserved :/
catch_rate = {}
learnset = {}
tmhm_moves = {}
evolution = {}
preevolution = {}


# get "internal indices" from table in constants file
pattern = r"const\s+(?P<name>\w+)" # name = pokemon name
skip_lines = [r"const_skip", r"NO_MON", r"FOSSIL", r"MON_GHOST"]
i = 0
with open(pokemon_constants_path) as f:
    for line in f:
        collect = re.search(pattern, line)
        skip = any([re.search(skip_line, line) for skip_line in skip_lines])
        if skip: # empty index
            i += 1
        elif collect:
            name = collect.group("name")
            pokemon_names.append(name)
            index[name] = i
            i += 1
        elif i > 0: # we're after the list
            break
        else: # we're before the list
            continue

# get dex numbers from table in constants file
pattern = r"const\s+DEX_(?P<name>\w+)" # name = pokemon name
i = 1
with open(pokedex_constants_path) as f:
    for line in f:
        collect = re.search(pattern, line)
        if collect:
            name = collect.group("name")
            dex_no[name] = i
            i += 1
        elif i > 1: # we're after the list
            break
        else: # we're before the list
            continue


# get info from base stats, which are in separate files
# the names of the files are the pokemon names in lowercase with no underscores
# so we map lowercase name to properly formatted (uppercase) name
formatted_pokemon_name = dict({(name.lower().replace("_", ""), name) for name in pokemon_names})

type_pattern = r"(?P<type1>\w+),\s*(?P<type2>\w+)\s*;\s*type"
catch_rate_pattern = r"(?P<rate>\d+)\s*;\s*catch rate"
learnset_pattern = r"(?P<move1>\w+),\s*(?P<move2>\w+),\s*(?P<move3>\w+),\s*(?P<move4>\w+)\s*;\s*level 1 learnset"

# tmhm moves list has an arbitrary number of rows/columns
# so look for the line above and the line below to start/stop tmhm moves
tmhm_begin_pattern = r"\s*tmhm\s*"
tmhm_end_pattern = r";\s*end"

for file_name in pokemon_base_stats_dir_path.glob("*.asm"):
    lowercase_name = file_name.stem
    name = formatted_pokemon_name[lowercase_name]
    collecting_tmhm = False # whether we are in the tmhm list

    with open(file_name) as f:
        for line in f:
            collect_types = re.search(type_pattern, line)
            collect_catch_rate = re.search(catch_rate_pattern, line)
            collect_learnset = re.search(learnset_pattern, line)
            begin_collect_tmhm = re.search(tmhm_begin_pattern, line)
            end_collect_tmhm = re.search(tmhm_end_pattern, line)

            if collect_types:
                type1 = collect_types.group("type1")
                type2 = collect_types.group("type2")
                types = [type1]
                if (type2 != type1): # only add second type if it's different
                    types.append(type2)
                typing[name] = types

            elif collect_catch_rate:
                catch_rate[name] = int(collect_catch_rate.group("rate"))

            elif collect_learnset:
                moves = []
                for i in range(1, 5):
                    move = collect_learnset.group("move" + str(i))
                    if move != "NO_MOVE":
                        moves.append(move)
                learnset[name] = [(1, move) for move in moves] # lv 1 learnset

            elif begin_collect_tmhm:
                collecting_tmhm = True
                tmhm_moves[name] = []
            elif end_collect_tmhm:
                collecting_tmhm = False
                break

            if collecting_tmhm:
                chunks = re.split(r"\W+", line)[1:-1]
                for chunk in chunks:
                    if chunk == "tmhm":
                        continue
                    else:
                        tmhm_moves[name].append(chunk)
            else:
                continue


# finally, evolutions and level-up learnsets
# here the pokemon names have initial capitals and some underscores (:
new_pokemon_pattern = r"(?P<name>\w+)EvosMoves:" # name is pokemon name

# the number of evlutions is arbitrary, but there's one per line
evos_begin_pattern = r";\s*Evolutions"
found_evo_pattern = r"(?P<level>\d+),\s*(?P<pokemon>\w+)" # pokemon it evolves into
# same with the moves
moves_begin_pattern = r";\s*Learnset"
found_move_pattern = r"(?P<level>\d+),\s*(?P<move>\w+)"
collecting_evos = False # these need to be here
collecting_moves = False
with open(pokemon_evos_moves_path) as f:
    for line in f:
        new_pokemon = re.search(new_pokemon_pattern, line)
        begin_collect_evos = re.search(evos_begin_pattern, line)
        begin_collect_moves = re.search(moves_begin_pattern, line)
        found_evo = re.search(found_evo_pattern, line)
        found_move = re.search(found_move_pattern, line)

        if new_pokemon:
            collecting_moves = False
            # convert Camel_Case pokemon names to lowercase
            lowercase_name = new_pokemon.group("name").lower().replace("_", "")
            try:
                name = formatted_pokemon_name[lowercase_name]
            except KeyError:
                pass # missingno

        elif begin_collect_evos:
            evolution[name] = []
            collecting_evos = True
        elif collecting_evos and found_evo:
            # the name of the evolution is written like POKEMON_NAME
            evolution[name].append((int(found_evo.group("level")), found_evo.group("pokemon")))

        elif begin_collect_moves:
            collecting_evos = False
            collecting_moves = True
        elif collecting_moves and found_move:
            learnset[name].append((int(found_move.group("level")), found_move.group("move")))

        else:
            continue

# link pokemon with their pre evolution
for name in pokemon_names:
    preevolution[name] = [] # have to fill these in first
for name in pokemon_names:
    for (level, pokemon) in evolution[name]:
        preevolution[pokemon].append((level, name))


# convert to a dict of tuples for pandas constructor
tuples_dict = {name: (index[name], dex_no[name], typing[name], catch_rate[name],
                      learnset[name], tmhm_moves[name], evolution[name], preevolution[name])
                    for name in pokemon_names}
pokemon_data = pandas.DataFrame.from_dict(tuples_dict, orient="index",
                                          columns=["index", "dex_no", "type", "catch_rate", "learnset", "tmhm_moves", "evolution", "preevolution"])

# pickle
data_path = find_data_path() # save the files here
pokemon_data_path = data_path / "pokemon_data.pkl"
pokemon_data.to_pickle(pokemon_data_path, compression = None, protocol = pickle.DEFAULT_PROTOCOL)
print("Wrote to", pokemon_data_path)

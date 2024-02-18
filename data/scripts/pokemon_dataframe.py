#!/bin/python
import re
import os
import pickle
import pandas
from script_tools import *

# TODO: add an optional argument for a different pokered path

# places to store info we read in
pokemon_names = []
index = {}
dex_no = {}
typing = {} # "type" is reserved
catch_rate = {}
learnset = {}
tmhm_moves = {}
evolution = {}
preevolution = {}

# get indices from table in constants file
pattern = r"const\s+(?P<name>\w+)"
skip_lines = [r"const_skip", r"NO_MON", r"FOSSIL", r"MON_GHOST"]
i = 0
with open(POKEMON_CONSTANTS_FILE) as f:
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
pattern = r"const\s+DEX_(?P<name>\w+)"
i = 1
with open(POKEDEX_CONSTANTS_FILE) as f:
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


# get info from base stats
# these are all in separate files so it's kind of a pain
# plus they're written in lowercase with no underscores

# map lowercase name to properly formatted (uppercase) name
formatted_pokemon_name = dict({(name.lower().replace("_", ""), name) for name in pokemon_names})

# so many patterns
type_pattern = r"(?P<type1>\w+),\s*(?P<type2>\w+)\s*;\s*type"
catch_rate_pattern = r"(?P<rate>\d+)\s*;\s*catch rate"
learnset_pattern = r"(?P<move1>\w+),\s*(?P<move2>\w+),\s*(?P<move3>\w+),\s*(?P<move4>\w+)\s*;\s*level 1 learnset"
tmhm_begin_pattern = r"\s*tmhm\s*"
tmhm_end_pattern = r";\s*end"

for filename in os.listdir(POKEMON_BASE_STATS_DIR):
    lowercase_name = filename.removesuffix(".asm")
    name = formatted_pokemon_name[lowercase_name]
    collecting_tmhm = False
    with open(POKEMON_BASE_STATS_DIR + filename) as f:
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
                # this is the level 1 learnset
                learnset[name] = [(1, move) for move in moves]

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


# finally, evolutions and learnset
# in this file the pokemon names have initial capitals and some unserscores (:
new_pokemon_pattern = r"(?P<name>\w+)EvosMoves:"
evos_begin_pattern = r";\s*Evolutions"
moves_begin_pattern = r";\s*Learnset"
found_evo_pattern = r"(?P<level>\d+),\s*(?P<pokemon>\w+)"
found_move_pattern = r"(?P<level>\d+),\s*(?P<move>\w+)"
collecting_evos = False
collecting_moves = False
name = ""

with open(POKEMON_EVOS_MOVES_FILE) as f:
    for line in f:
        new_pokemon = re.search(new_pokemon_pattern, line)
        begin_collect_evos = re.search(evos_begin_pattern, line)
        begin_collect_moves = re.search(moves_begin_pattern, line)
        found_evo = re.search(found_evo_pattern, line)
        found_move = re.search(found_move_pattern, line)

        if new_pokemon:
            collecting_moves = False
            lowercase_name = new_pokemon.group("name").lower().replace("_", "")
            try:
                name = formatted_pokemon_name[lowercase_name]
            except KeyError:
                pass # missingno

        elif begin_collect_evos:
            evolution[name] = []
            collecting_evos = True
        elif collecting_evos and found_evo:
            # the name of the evolution is formatted properly
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
pokemon_data_filename = PICKLE_PATH + "pokemon_data" + PICKLE_EXT
pokemon_data.to_pickle(pokemon_data_filename, compression = None, protocol = pickle.DEFAULT_PROTOCOL)
print("Wrote to", pokemon_data_filename)

pokemon_names_filename = PICKLE_PATH + "pokemon_names" + PICKLE_EXT
with open(pokemon_names_filename, "wb") as f:
    pickle.dump(pokemon_names, f)
print("Wrote to", pokemon_names_filename)

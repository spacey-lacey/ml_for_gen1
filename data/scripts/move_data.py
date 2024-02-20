#!/bin/python
import re
import pandas
import pickle
from pathlib import Path
from pathfinder import find_data_path, find_pokered_path


# find the files we need
pokered_path = find_pokered_path()
print(pokered_path)
move_constants_path = pokered_path / "constants/move_constants.asm"
move_data_path = pokered_path / "data/moves/moves.asm"

# places to store info we read in
move_names = []
index = {}
effect = {}
power = {}
typing = {} # "type" is reserved
accuracy = {}
pp = {}

# get indices from table in constants file
pattern = r"\s*const\s+(?P<name>\w+)"
skip_lines = [r"const_skip", r"NO_MOVE"]
i = 0
with open(move_constants_path) as f:
    for line in f:
        collect = re.search(pattern, line)
        skip = any([re.search(skip_line, line) for skip_line in skip_lines])
        if skip: # empty index
            i += 1
        elif collect:
            name = collect.group("name")
            move_names.append(name)
            index[name] = i
            i += 1
        elif i > 0: # we're after the list
            break
        else: # we're before the list
            continue

# now the data file
# break up the pattern to make it a little easier to read
pattern = r"\s*move\s+"
pattern += r"(?P<name>\w+),\s+"
pattern += r"(?P<effect>\w+),\s+"
pattern += r"(?P<power>\d+),\s+"
pattern += r"(?P<typing>\w+),\s+"
pattern += r"(?P<accuracy>\d+),\s+"
pattern += r"(?P<pp>\d+)"
with open(move_data_path) as f:
    for line in f:
        collect = re.search(pattern, line)
        if collect:
            name = collect.group("name")
            effect[name] = collect.group("effect")
            power[name] = int(collect.group("power"))
            typing[name] = collect.group("typing")
            accuracy[name] = int(collect.group("accuracy"))
            pp[name] = int(collect.group("pp"))
        elif len(effect) > 0:
            break
        else:
            continue

# convert to a dict of tuples for pandas constructor
tuples_dict = {name: (index[name], effect[name], power[name], typing[name], accuracy[name], pp[name]) for name in move_names}
move_data = pandas.DataFrame.from_dict(tuples_dict, orient="index",
                                       columns=["index", "effect", "power", "type", "accuracy", "pp"])
# the pandas have arrived...

# create a column to separate attack and status moves
move_data["damaging"] = move_data["power"] > 0

# pickle and save to data directory
data_path = find_data_path()
move_data_path = data_path / "move_data.pkl"
move_data.to_pickle(move_data_path, compression = None, protocol = pickle.DEFAULT_PROTOCOL)
print("Wrote to", move_data_path)

#!/bin/python
import re
import pickle
import pandas
from script_tools import *

# TODO: add an optional argument for a different pokered path

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
with open(MOVE_CONSTANTS_FILE) as f:
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
with open(MOVE_DATA_FILE) as f:
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

# pickle
move_data_filename = PICKLE_PATH + "move_data" + PICKLE_EXT
move_data.to_pickle(move_data_filename, compression = None, protocol = pickle.DEFAULT_PROTOCOL)
print("Wrote to", move_data_filename)

move_names_filename = PICKLE_PATH + "move_names" + PICKLE_EXT
with open(move_names_filename, "wb") as f:
    pickle.dump(move_names, f)
print("Wrote to", move_names_filename)

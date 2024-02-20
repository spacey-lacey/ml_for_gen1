#!/bin/python
import re
import pandas
from pathlib import Path
from pathfinder import find_data_path, find_pokered_path


# find the files we need
pokered_path = find_pokered_path()
trainer_constants_path = pokered_path / "constants/trainer_constants.asm"
trainer_ai_path = pokered_path / "data/trainers/ai_pointers.asm"
trainer_parties_path = pokered_path / "data/trainers/parties.asm"

# places to store info we read in
trainer_classes = []
from_index = {} # get trainer class from index
index = {}
ai_type = {} # later fill special moves
parties = {}
n_parties = {}

# get indices from table in constants file
pattern = r"const\s+(?P<name>\w+)"
skip_lines = [r"const_skip", r"NOBODY", r"UNUSED", r"CHIEF"]
i = 0
with open(trainer_constants_path) as f:
    for line in f:
        collect = re.search(pattern, line)
        skip = any([re.search(skip_line, line) for skip_line in skip_lines])

        if skip: # empty index
            i += 1
        elif collect:
            name = collect.group("name")
            if re.search("PSYCHIC", name):      # remove _TR from psychic
                name = name.replace("_TR", "")  # we don't have that ambiguity
            trainer_classes.append(name)
            index[name] = i
            from_index[i] = name
            i += 1
        elif i > 0: # we're after the list
            break
        else: # we're before the list
            continue

# get AI data from table
pattern = r"dbw\s+\d+,\s*(?P<ai_type>\w+)"
i = 0
with open(trainer_ai_path) as f:
    for line in f:
        collect = re.search(pattern, line)
        if collect:
            i += 1
            try:
                name = from_index[i]
            except KeyError: # skip unused trainers
                continue
            else:
                ai_type[name] = collect.group("ai_type")
        else:
            continue

# get party data from table
# annoyingly this file uses camel case for the class names
# we'll compare lowercase to lowercase
formatted_class_name = dict({(name.lower().replace("_", ""), name) for name in trainer_classes})

new_class_pattern = r"(?P<name>\w+)Data:"
generic_party_pattern = r"db\s+\d+,\s*\w+"
special_party_pattern = r"db\s+\$FF"

with open(trainer_parties_path) as f:
    for line in f:
        new_class = re.search(new_class_pattern, line)
        collect_generic_party = re.search(generic_party_pattern, line)
        collect_special_party = re.search(special_party_pattern, line)

        if new_class:
            # annoyingly the rival is called "green" here
            lowercase_name = new_class.group("name").lower().replace("green", "rival")
            try:
                name = formatted_class_name[lowercase_name]
            except KeyError:
                continue # unused class
            else:
                parties[name] = []

        elif collect_generic_party:
            # pattern is " db, level, pokemon, pokemon, ..., 0 "
            chunks = re.split(r"\W+", line)[2:-2]
            level = int(chunks[0]) # same level for all party members
            parties[name].append([(level, pokemon) for pokemon in chunks[1:]])

        elif collect_special_party:
            # pattern is " db $FF, level, pokemon, level, pokemon,..., 0 "
            chunks = re.split(r"\W+", line)[3:-2]
            party = []
            for i in range(0, len(chunks), 2):
                party.append((int(chunks[i]), chunks[i+1])) # not all same lvl
            parties[name].append(party)

        else:
            continue

# record the number of parties for each class
n_parties = {name: len(parties[name]) for name in trainer_classes}

# convert to a dict of tuples for pandas constructor
tuples_dict = {name: (index[name], ai_type[name], parties[name], n_parties[name])
               for name in trainer_classes}
trainer_data = pandas.DataFrame.from_dict(tuples_dict, orient="index",
                                          columns=["index", "ai_type", "parties", "n_parties"])
print(trainer_data)

# pickle
data_path = find_data_path() # save to data dir
trainer_data_path = data_path / "trainer_data.pkl"
trainer_data.to_pickle(trainer_data_path, compression = None, protocol = pickle.DEFAULT_PROTOCOL)
print("Wrote to", trainer_data_path)

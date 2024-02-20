ifndef VIRTUAL_ENV
	$(error Not in virtual environment)
endif

# relative paths to directories
battle = ../battle
data = ../data
pg1 = ../external/PokemonGen1/PokemonGeneration1
pg1_dll := $(pg1)/bin/Debug/*/PokemonGeneration1.dll
pokered = ../external/pokered
scripts = ../data/scripts

#------------------------------------------------------------------------------

pg1_dll := $(addprefix $(pg1)/,$(dll_subpath))
upgrade_tool := $(addprefix $(pg1)/,.config/dotnet-tools.json)

pkl_files := $(addprefix $(data)/,move_data.pkl pokemon_data.pkl trainer_data.pkl)

#------------------------------------------------------------------------------

all: data_files battle_deps
	

data_files: $(pkl_files)

$(pkl_files): $(subst $(data)/,$(scripts)/,$(@:.pkl=.py)) # make sure no space!!
	python $(subst $(data)/,$(scripts)/,$(@:.pkl=.py)) # idk why i can't get this automatically


battle_deps: $(pg1_dll)

$(pg1_dll):
	$(error Couldn't find PokemonGeneration1.dll! See PokemonGen1/INSTALL.md for instructions.)


clean:
	$(RM) $(data)/*.pkl $(scripts)/__pycache__

#------------------------------------------------------------------------------

RM := rm -rf

.PHONY: all clean data_files battle_deps


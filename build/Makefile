include definitions.mk

#------------------------------------------------------------------------------

data_files: $(move_data_files) $(pokemon_data_files) $(trainer_data_files)

$(move_data_files): $(move_data_script_deps) $(move_data_pokered_deps)
	python $(addprefix $(scripts_dir)/, fetch_move_data.py)
$(pokemon_data_files): $(pokemon_data_script_deps) $(pokemon_data_pokered_deps)
	python $(addprefix $(scripts_dir)/, fetch_pokemon_data.py)
$(trainer_data_files): $(trainer_data_script_deps) $(trainer_data_pokered_deps)
	python $(addprefix $(scripts_dir)/, fetch_trainer_data.py)


clean:
	$(RM) $(data_dir)/*.pkl $(scripts_dir)/__pycache__
# probably need to move these to definitions at some point

#------------------------------------------------------------------------------

ifndef VIRTUAL_ENV
	$(error Not in virtual environment)
endif

RM := rm -rf

.PHONY: clean data_files


# relative paths to directories
pokered_dir := ../external/pokered
data_dir := ../data
scripts_dir := ../data/scripts


# data_files

move_data_files := \
$(addprefix $(data_dir)/, \
	move_data.pkl \
	move_names.pkl \
)
move_data_script_deps := \
$(addprefix $(scripts_dir)/, \
	fetch_move_data.py \
	script_tools.py \
)
move_data_pokered_deps := \
$(addprefix $(pokered_dir)/, \
	constants/move_constants.asm \
	data/moves/moves.asm \
)

pokemon_data_files := \
$(addprefix $(data_dir)/, \
	pokemon_data.pkl \
	pokemon_names.pkl \
)
pokemon_data_script_deps := \
$(addprefix $(scripts_dir)/, \
	fetch_pokemon_data.py \
	script_tools.py \
)
pokemon_data_pokered_deps := \
$(addprefix $(pokered_dir)/, \
	constants/pokedex_constants.asm \
	constants/pokemon_constants.asm \
	data/pokemon/base_stats/*.asm \
	data/pokemon/evos_moves.asm \
)

trainer_data_files := \
$(addprefix $(data_dir)/, \
	trainer_data.pkl \
	trainer_classes.pkl \
)
trainer_data_script_deps := \
$(addprefix $(scripts_dir)/, \
	fetch_trainer_data.py \
	script_tools.py \
)
trainer_data_pokered_deps := \
$(addprefix $(pokered_dir)/, \
	constants/trainer_constants.asm \
	data/trainers/ai_pointers.asm \
	data/trainers/parties.asm \
)

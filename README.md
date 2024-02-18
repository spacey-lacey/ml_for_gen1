This project is an attempt to replace the trainer AI programmed by the devs with...well, a trainer AI programmed by AI.

As you can see, things are very much under construction.

A rough sketch of the intended process:
1. ~~Use the data files from [pret/pokered](pret/pokered) to collect move, Pokemon, and trainer data.  Use scripts to create and pickle pandas dataframes for later use.~~ **Done!**
2. Create a python wrapper for the implementation of the battle system in [in-op/PokemonGen1](in-op/PokemonGen1).  It is written in C#, so we'll have to use Python.NET.
3. Implement a deep-Q reinforcement model with tf-agents and keras. This will use the wrapper to interface with the battle system.
2. Train the model via some kind of input system I will hopefully set up.  Otherwise we'll train on randomly generated Pokemon.
3. Test the model via the same input system or in some kind of interactive battle interface (theoretically, training could be done this way too, but it would probably take ages).  With some adjustments, we could probably use the C# program in [in-op/PokemonGen1](in-op/PokemonGen1).
4. Use tensorflow lite to optimize the model(s) and use its C interface.
5. Compile the C implementation for rgbds with [sdcc](https://sourceforge.net/projects/sdcc/).  It can output assembly code for rgbds.
6. Try to implement in an actual game build.  I would assume the implementation would be largely lookup tables, so hopefully RAM won't be an issue.  I think we can have as much ROM as we want if the game will only be played on emulators.

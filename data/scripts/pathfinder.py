from pathlib import Path


def find_base_path():
    '''
    Find relative path to base directory from where the script is executed.
    This should work even if the repo name changes.
    '''
    cwd = Path.cwd()
    if cwd.name == "scripts":
        base_path = Path("../..")
    elif cwd.name == "data" or cwd.name == "build":
        base_path = Path("..")
    else: # assume we are in base directory
        base_path = Path(".")
    return (base_path)

def find_relative_directory_path(directory_path_relative_to_base):
    '''
    Find relative path to given directory from where the script is executed.
    Give the path as though you were in the "main" directory of the repo.
    '''
    cwd = Path.cwd()
    if cwd.name == directory_path_relative_to_base:
        relative_path = Path(".")
    elif cwd.parent.name == directory_path_relative_to_base:
        relative_path = Path("..")
    else:
        base_path = find_base_path()
        relative_path = base_path / directory_path_relative_to_base
    return (relative_path)

def find_build_path():
    '''
    Find relative path to build directory from where the script is executed.
    '''
    return find_relative_directory_path("build")

def find_data_path():
    '''
    Find relative path to data directory from where the script is executed.
    '''
    return find_relative_directory_path("data")

def find_pokered_path():
    '''
    Find relative path to pokered from where the script is executed.
    '''
    return find_relative_directory_path("external/pokered")


if __name__ == "__main__":
    print("cwd:", Path.cwd())
    print("base_path:", find_base_path())
    print("build_path:", find_build_path())
    print("data_path:", find_data_path())
    print("pokered_path:", find_pokered_path())

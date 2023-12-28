# This module contains functions responsible for finding files with matching names.


import os


def confirmFolderAccessibility(folder_path: "str") -> "bool":
    """
    Returns whether or not a folder be scanned.
    """

    try:
        os.access(folder_path, os.R_OK)
    except (FileNotFoundError, PermissionError):
        return False
    else:
        return True


def hashFolderContents(
    folder_path: "str", excluded_file_names: "set" = (".DS_Store", ".localized")
) -> "list":
    """
    Hashes every file name in a folder and adds it to a list.

    Ignores folders and returns an empty list if the folder could not be accessed.

    folder_path (str): The directory path of the folder to get names from.
    excluded_file_names (set, optional): Files with names in this set will be ignored. Defaults to (".DS_Store", ".localized").
    """

    # Checks if 'folder_path' is accessible. Returns an empty list if it is not.
    if confirmFolderAccessibility(folder_path) == False:
        return []

    # Stores the names of every non-folder file thats name isn't in 'excluded_file_names'.
    file_name_list = []
    for file_name in os.listdir(folder_path):
        if os.path.isdir(file_name) == False and file_name not in excluded_file_names:
            file_name_list.append(file_name)

    # Converts names to hashes and stores them.
    file_hash_list = []
    for file_name in file_name_list:
        file_hash_list.append(hash(file_name))

    return file_hash_list


def scanFolder(root_path: "str") -> "dict":
    """
    Scans a nested folder structure for files with matching names.

    Returns a dictionary that has file names as keys and directory paths to files with that name as output.

    Args:
        root_path (str): The directory path of the folder to scan.

    Raises:
        ValueError: 'root_path' was either not found or not readable.
    """

    # Confirms that 'root_path' is accessible.
    if confirmFolderAccessibility(root_path) == False:
        raise ValueError(f"{root_path} could not be accessed.", end="\n\n")

    # Stores the directory path of every nested folder under 'root_path'.
    folder_path_list = [dirpath for dirpath, dirnames, filenames in os.walk(root_path)]

    # Every hashed file name in the 'root_path' nested folder structure.
    total_hash_list = []

    # Indexes of 'total_hash_list' that denote the parent folders of subsequent values.
    # 'total_hash_list[]
    total_folder_index_list = []

    # Collects hashed file names, stores their position, and removes any empty or unaccessible folder paths from 'folder_path_list'.
    for folder_path in folder_path_list:
        # The hashed names of every non-folder files in 'folder_path'.
        hash_list = hashFolderContents(folder_path)

        if len(hash_list) > 0:  # If the folder was accessible and contained files.
            total_folder_index_list.append(len(total_hash_list))
            for item in hash_list:
                total_hash_list.append(item)
        else:  # If the folder was unaccessible or didn't contain any files.
            folder_path_list.remove(folder_path)

    #
    duplicate_hash_list = []
    duplicate_hash_paths_list = []

    #
    hash_list_length = len(hash_list)
    current_item_index = 0

    #
    while hash_list_length > 0:
        current_item = total_hash_list[current_item_index]

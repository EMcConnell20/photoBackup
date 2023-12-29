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


def checkExtensionType(file_name: "str") -> "str":
    extension_name = file_name[-3] + file_name[-2] + file_name[-1]

    return extension_name


def hashFolderContents(
    folder_path: "str",
    excluded_file_names: "set" = (".DS_Store", ".localized"),
    excluded_file_types: "set" = ("zip"),
) -> "list":
    """
    Hashes every file name in a folder and adds it to a list.

    Ignores folders and returns an empty list if the folder could not be accessed.

    folder_path (str): The directory path of the folder to get names from.
    excluded_file_names (set, optional): Files with names in this set will be ignored. Defaults to (".DS_Store", ".localized").
    excluded_file_types (set, optional): Files with extensions in this set will be ignored. Defaults to ("zip).
    """

    # Checks if 'folder_path' is accessible. Returns an empty list if it is not.
    if confirmFolderAccessibility(folder_path) == False:
        return []

    # Stores the names of every non-folder file thats name isn't in 'excluded_file_names'.
    file_name_list = []
    for file_name in os.listdir(folder_path):
        if (
            os.path.isdir(file_name) == False
            and file_name not in excluded_file_names
            and checkExtensionType(file_name) not in excluded_file_types
        ):
            file_name_list.append(file_name)

    # Converts names to hashes and stores them.
    file_hash_list = []
    for file_name in file_name_list:
        file_hash_list.append(hash(file_name))

    return file_hash_list


def createFilePathList(file_hash: "int", hash_parent_paths: "list") -> "list":
    """
    Scans folders for hashed file names that match 'file_hash'.
    Returns a list of the directory paths of those files.

    Args:
        file_hash (int): The hash value to search for.
        hash_parent_paths (list): The parent folders of the duplicate names.
    """
    # The directory paths of files with duplicate hashes.
    file_path_list = []

    # Checks each folder in 'hash_parent_paths' for a file name with the hash value 'file_hash'.
    for folder_path in hash_parent_paths:
        file_name_list = os.listdir(folder_path)

        for file_name in file_name_list:
            if hash(file_name) == file_hash:
                file_path_list.append(os.path.join(folder_path, file_name))
                break

    return file_path_list


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

    # Indexes of 'total_hash_list' that denote the parent folders of subsequent values in that list.
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

    # Stores all duplicate hashes.
    duplicate_hash_list = []

    # Stores the parent folder paths of all duplicate hashes.
    duplicate_hash_paths_list = []

    # Stores the length of 'total_hash_list' so that the loop doesn't have to check it every single time.
    hash_list_length = len(total_hash_list)

    # Finds duplicate hashes and creates nested lists of directory paths that the hash came from.
    while hash_list_length > 0:
        current_item = total_hash_list[0]
        item_count = total_hash_list.count(current_item)

        if item_count > 1:
            folder_index = 0
            path_list = []

            # Creates a list of folder paths that 'current_item' is in.
            while item_count > 0:
                item_index = total_hash_list.index(current_item)

                while (
                    folder_index < len(total_folder_index_list) - 1
                    and item_index >= total_folder_index_list[folder_index + 1]
                ):
                    folder_index += 1

                path_list.append(folder_path_list[folder_index])
                total_hash_list.remove(current_item)
                item_count -= 1
                hash_list_length -= 1

                iterator = folder_index + 1
                while iterator < len(total_folder_index_list):
                    if iterator != 0:
                        total_folder_index_list[iterator] -= 1

                        while (
                            iterator < len(total_folder_index_list)
                            and total_folder_index_list[iterator]
                            == total_folder_index_list[iterator - 1]
                        ):
                            total_folder_index_list.pop(iterator - 1)
                            folder_path_list.pop(iterator - 1)
                            total_folder_index_list[iterator - 1] -= 1

                    iterator += 1

            duplicate_hash_list.append(current_item)
            duplicate_hash_paths_list.append(path_list)
        else:
            total_hash_list.remove(current_item)
            hash_list_length -= 1

            iterator = 0
            while iterator < len(total_folder_index_list):
                if iterator != 0:
                    total_folder_index_list[iterator] -= 1

                    while iterator < len(total_folder_index_list) and (
                        total_folder_index_list[iterator]
                        == total_folder_index_list[iterator - 1]
                    ):
                        total_folder_index_list.pop(iterator - 1)
                        folder_path_list.pop(iterator - 1)
                        total_folder_index_list[iterator - 1] -= 1

                iterator += 1

    # Stores the directory path of every file with duplicate names.
    duplicate_directory_path_list = []

    # Finds and records the directory path of every file with a hash in 'duplicate_hash_list'.
    for iterator in range(len(duplicate_hash_list)):
        for directory_path in createFilePathList(
            duplicate_hash_list[iterator], duplicate_hash_paths_list[iterator]
        ):
            duplicate_directory_path_list.append(directory_path)

    # End
    return duplicate_directory_path_list


if __name__ == "__main__":
    os.system("clear")
    root_path = input("Root Folder Path: ")

    path_list = scanFolder(root_path)
    print(f"\n{path_list}")

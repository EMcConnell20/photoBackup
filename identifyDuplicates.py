## TO DO
# I'd like to create a CSV that identifies the files that are duplicates

# Specify the root folder
#root_folder = '/Volumes/Video/takeOutoutput'
import hashlib
import os
import csv
from collections import defaultdict
import os

def get_all_files(root_folder):
    return [
        os.path.join(foldername, filename)
        for foldername, _, filenames in os.walk(root_folder)
        for filename in filenames
        if filename != ".DS_Store"
    ]

def identify_duplicate_files(file_list):
    file_locations = defaultdict(list)
    for file_path in file_list:
        file_name = os.path.basename(file_path)
        file_locations[file_name].append(file_path)
    duplicate_files = {name: locations for name, locations in file_locations.items() if len(locations) > 1}
    return duplicate_files

def write_to_csv(duplicate_files, output_csv):
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['File Name', 'Locations']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for file_name, locations in duplicate_files.items():
            writer.writerow({'File Name': file_name, 'Locations': ', '.join(locations)})

def hash_duplicates(duplicate_files):

    hashed_files = {}

    for key, value_list in duplicate_files.items():
    
    # Iterate through each item in the list
        for item in value_list:
            # Hash the file
            hash_value = hash_file(item)
            dictionary_item = {'location': item, 'hash': hash_value}
            # Add the hash value to the dictionary
            if key in hashed_files:
                hashed_files[key].append(dictionary_item)
            else:
                hashed_files[key] = [dictionary_item]
    return hashed_files

def hash_file(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
    
def check_duplicate_hash(hashed_files):

    with open(hash_csv, 'w', newline='') as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(['File Name', 'Location1', 'Hash1', 'Location2', 'Hash2'])

        for filename, records in hashed_files.items():
            print(f"File: {filename}")

            # Iterate through the list of records for each file
            for i in range(len(records) - 1):
                hash1 = records[i]['hash']
                hash2 = records[i + 1]['hash']
                
                # Compare hash values
                if hash1 == hash2:
                    print(f"  Hash values match for locations {records[i]['location']} and {records[i + 1]['location']}")
                else:
                    print(f"  Hash values do not match for locations {records[i]['location']} and {records[i + 1]['location']}")


# Specify the root folder
root_folder = 'test'
output_csv = 'output/duplicate_files.csv'
hash_csv = 'output/hashed_files.csv'

# Get a list of all files in subfolders
all_files_list = get_all_files(root_folder)

# Identify duplicate file names and their locations
duplicate_files = identify_duplicate_files(all_files_list)

# Write the output to a CSV file
write_to_csv(duplicate_files, output_csv)

hashed_files = hash_duplicates(duplicate_files)
#print(hashed_files)
check_duplicate_hash(hashed_files)
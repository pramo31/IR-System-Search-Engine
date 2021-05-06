#!/usr/bin/env python

"""DocumentUtils.py: Classes containing Read and Write Utilities"""
__author__ = "Pramodh Acharya"

import os


class DocumentReader:

    def __init__(self):
        pass

    # Reads the content of a file
    def read_file(self, file_name):
        with open(file_name, encoding='utf-8-sig') as file:
            read_data = file.readlines()
        return read_data

    # Reads and returns each of the file inside the directory in a List
    def read_files_in_directory(self, directory):
        directories = os.listdir(directory)

        separator = '/'
        reader = []

        for each in directories:
            folder = f"{directory}{separator}{each}"
            if (os.path.isdir(folder)):
                reader.extend(self.read_files_in_directory(folder))
            else:
                file_name = os.path.join(folder)
                reader.append(self.read_file(file_name))

        return [e for s in reader for e in s]

    def get_all_files(self, directory):
        directories = os.listdir(directory)
        separator = '/'
        files = []
        for each in directories:
            folder = f"{directory}{separator}{each}"
            if (not os.path.isdir(folder)):
                files.append(os.path.join(folder))

        return files

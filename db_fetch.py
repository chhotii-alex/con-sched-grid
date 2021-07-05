import csv
from session import Session

def get_session_data():
    results = []
    file_name = "example-data/pocketprogram.csv"
    # See https://discuss.codecademy.com/t/what-does-the-newline-argument-do/463575
    # for an explanation of why we use the newline argument when opening a file
    # for the csv module to read.
    fh = open(file_name, 'rt', encoding='utf-8', newline='')
    reader = csv.DictReader(fh)
    for row in reader:
        results.append(Session(row))
    return results


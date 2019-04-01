from functions import createFolders, readCsv, createExcelFile
import pprint
import json

chunk = [vectorData for vectorData in readCsv()]

# json_file = {}
# for key, *data in chunk:
#     json_file[key] = data

# with open("output12.json", 'w') as f:
#     json.dump(json_file, f)

createExcelFile(chunk)

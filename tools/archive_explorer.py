import zipfile
import sys

from sm_parser.parser import SmParser

filename = sys.argv[1]

zipfile = zipfile.ZipFile(filename)


def filter_sm(filename): return filename.lower().endswith(".sm")


sm_files = filter(filter_sm, zipfile.namelist())

for i in sm_files:
    print(i)
    data = zipfile.open(i)
    parser = SmParser(data.read())
    parser.parse()
    print(parser.song)
    print(parser.song.get_bpm())
    print(parser.song.notes)

import hashlib
import sys
import zipfile
from io import BytesIO

import mutagen

from sm_parser.parser import SmParser

filename = sys.argv[1]

my_zipfile = zipfile.ZipFile(filename)


def filter_sm(filename): return filename.lower().endswith(".sm")


sm_files = filter(filter_sm, my_zipfile.namelist())

print(my_zipfile.infolist())

dirs = {}


def is_dir(zip_file: zipfile.ZipInfo) -> bool:
    return zip_file.filename[-1] == "/"


def is_music(zip_file: zipfile.ZipInfo) -> bool:
    filename = zip_file.filename.lower()
    return filename.endswith("mp3") or filename.endswith("ogg")


for i in my_zipfile.infolist():
    if is_dir(i):
        dirs[i.filename.split("/")[0]] = []
    if is_music(i):
        print(i)
        buffer = BytesIO(my_zipfile.open(i).read())
        print(mutagen.File(buffer))

print("Pack name: %s" % dirs)


for i in sm_files:
    print(i)
    pack_name = i.split("/")[0]
    data = my_zipfile.open(i)
    buffer = data.read()

    parser = SmParser(buffer)
    parser.parse()

    print(parser.song)
    print(parser.song.get_bpm())
    print(parser.song.parse_notes())

    song_hash = hashlib.sha256(buffer)
    dirs[pack_name].append({"parser": parser, "id": song_hash.hexdigest()})

for key, values in dirs.items():
    print(key, values)

    for value in values:
        parser = value['parser']
        song = parser.song
        notes = song.parse_notes()
        document = {
            "pack": key,
            "title": song.title,
            "artist": song.artist,
            "credit": song.credit,
            # self.banner = None
            # self.music = None
            "author": song.author,
            "mean_bpm": song.get_mean_bpm(),
            "bpm": [x[1] for x in song.get_bpm()],
            "type": list({x.dance_type for x in notes}),
            "difficulty": list({x.difficultly.lower() for x in notes}),
        }
        print(document)

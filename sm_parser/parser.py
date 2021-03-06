import logging
from operator import itemgetter
from typing import List

logger = logging.getLogger(__name__)


class SmParser(object):
    INFO = 1
    DATA = 2
    END_DATA = 3
    SONG = 4

    def __init__(self, content: bytes):
        self.content = content.decode("utf-8")
        self.state = self.INFO
        self.song = Song()

    def parse(self):
        self.state = self.INFO

        line_data = ""

        for line in self.content.split("\n"):
            line = line.strip()

            while line:
                # detect and remove comment on a line
                # there's can be an // anywhere in the line
                # discard everything after
                comment_pos = line.find("//")
                if comment_pos > -1:
                    # clean the data after removing the comment
                    line = line[:comment_pos].strip()
                if self.state == self.INFO:
                    # print("info")
                    separator = line.find(":")
                    if not line.find("#") == 0 and not separator > 0:
                        logger.debug("Line don't follow the format")
                        break
                    key = line[1:separator].strip().lower()
                    # print(key)
                    line = line[separator+1:]
                    line_data = ""
                    # We now seek data
                    self.state = self.DATA

                if self.state == self.DATA:
                    # We have encountered a new tag data, discard accumulated data
                    if line.find("#") == 0 and line.find(":") > 0:
                        self.state = self.INFO
                        continue
                    if line.endswith(";"):
                        line_data += line[:-1]
                        self.state = self.END_DATA
                    else:
                        # Remove comments
                        if not line_data.startswith("//"):
                            line_data += line
                        break

                if self.state == self.END_DATA:
                    # print("key: %s data: %s" % (key, line_data))
                    if hasattr(self.song, key):
                        if key == "notes":
                            self.song.notes.append(line_data)
                        else:
                            setattr(self.song, key, line_data)
                    line_data = ""
                    self.state = self.INFO


class Song(object):
    def __init__(self):
        self.title = None
        self.subtitle = None
        self.artist = None
        self.genre = None
        self.credit = None
        self.banner = None
        self.music = None
        self.author = None
        self.bpms = None
        self.parsed_bpms = None
        self.notes = []

    def __str__(self):
        return "%s - %s" % (self.title, self.artist)

    def get_bpm(self) -> List[List[float]]:
        # cache
        if self.parsed_bpms is not None:
            return self.parsed_bpms

        if self.bpms:
            self.parsed_bpms = [list(map(float, x.split("="))) for x in self.bpms.split(",")]
        else:
            self.parsed_bpms = []
        return self.parsed_bpms

    def get_mean_bpm(self) -> float:
        bpm_list = self.get_bpm()
        if not bpm_list:
            raise AttributeError("No BPM data")
        return sum(map(itemgetter(1), bpm_list)) / len(bpm_list)

    def parse_notes(self):
        if not self.notes:
            return None
        return [StepChart(x) for x in self.notes]


class StepChart(object):
    def __init__(self, raw_chart):
        self.raw_chart = raw_chart
        self.dance_type = None
        self.dance_sub_type = None
        self.difficultly_description = None
        self.difficultly = None
        self.steps = 0
        self.groove = None
        self.step_data = None
        self.n_th = 0
        self.measures = 0

        self.parse()

    def parse(self):
        split_data = self.raw_chart.split(":")

        self.dance_type, self.dance_sub_type = split_data[0].split('-')
        self.difficultly_description = split_data[1]
        self.difficultly = split_data[2]
        self.steps = int(split_data[3])
        self.groove = split_data[4]
        self.step_data = split_data[5].split(",")

    def __str__(self):
        return "%s %s %s" % (self.dance_type, self.dance_sub_type, self.difficultly)

    def __repr__(self):
        return "<%s>" % self.__str__()

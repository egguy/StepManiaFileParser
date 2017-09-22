import logging

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
        self.bpm = None

    def __str__(self):
        return "%s - %s" % (self.title, self.artist)

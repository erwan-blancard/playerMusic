import os

import pygame
import music_tag
from PIL import Image


class Track:

    def __init__(self, filepath):
        self.filepath = filepath
        self.length = -1.0
        self.name = os.path.basename(filepath)
        self.artist = "Inconnu"
        self.PIL_supported = True
        self.cover: pygame.Surface = None
        try:
            song = music_tag.load_file(filepath)
        except Exception as e:
            print("Error trying to retrieve metadata:", e)
            self.PIL_supported = False

        # check metadata if suppor
        if self.PIL_supported:
            try:
                title = str(song["title"].value)
                if len(title) > 0:
                    self.name = title
            except Exception as e: print(e)
            try:
                self.length = song["#length"].value
            except Exception as e: print(e)
            try:
                artist = str(song["artist"].value)
                if len(artist) > 1:
                    self.artist = artist
            except Exception as e: print(e)

            # load cover
            try:
                metadata_art = song["artwork"]
                cover_img = metadata_art.first.thumbnail([256, 256])
                mode = cover_img.mode
                size = cover_img.size
                data = cover_img.tobytes()
                self.cover = pygame.image.fromstring(data, size, mode)
            except Exception as e:
                print("Error loading thumbnail:", e)
            print(self.name, self.length, self.artist)

        # for playlist
        self.broken_flag = False

    def get_name(self):
        return self.name

    def get_length(self):
        return self.length

    def get_artist(self):
        return self.artist

    def get_filepath(self):
        return self.filepath

    def get_cover(self):
        return self.cover

    def is_PIL_supported(self):
        return self.PIL_supported

    def is_broken(self):
        return self.broken_flag

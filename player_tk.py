import time
from tkinter import *
import threading
import os
import glob
import vlc
import pynput.keyboard
from pynput.keyboard import Key, Controller, KeyCode
import itertools
import shutil
from natsort import natsorted
import sys
from tinytag import TinyTag
from threading import Timer

keyboard = Controller()

sys.setrecursionlimit(10 ** 6)


class Player:
    def __init__(self):
        def available_dir(path):
            return path.replace("\\", "//")

        # self.video_path = (available_dir(bundle_dir) + "//")
        self.video_path = available_dir(os.getcwd()) + "//"
        # self.video_path = "path/to/video/folder"
        self.fav_video_path = self.video_path + "Up"
        self.non_fav_video_path = self.video_path + "Down"
        # print(self.video_path)

        self.files = glob.glob(self.video_path + '*.mp4', recursive=True) + glob.glob(self.video_path + '*.ts',
                                                                                      recursive=True)
        self.files = natsorted(self.files, reverse=True)
        print("Total videos : " + str(len(self.files)))
        try:
            g = open(os.path.join(self.video_path + "log.txt"), "r", encoding="utf8")
            lines = g.read().split("\n")
            last_line = lines[0]
            indices = [i for i, s in enumerate(self.files) if last_line in s][0]  # get index at 0 position
            print(indices)
            self.video = self.files[indices]
            self.i = indices
            self.length = TinyTag.get(self.video).duration
            print(self.length)
        except FileNotFoundError:
            self.video = self.files[0]
            self.i = 0
            self.length = TinyTag.get(self.video).duration
            pass

        def timer_started():
            print("Timer started")

        self.toggle = itertools.cycle([True, False])
        self.media_player = vlc.MediaPlayer("--verbose=-1")
        self.media = vlc.Media(self.video)
        self.media_player.set_media(self.media)
        self.media_player.audio_set_volume(35)
        root.overrideredirect(False)
        self.t = Timer(0, timer_started)
        self.t.daemon = True
        self.t.start()
        title.set(str(self.i + 1) + "/" + str(len(self.files)) + " : " + os.path.basename(
            self.files[self.i]) + "  [" + str(int(self.length)) + " s]")
        self.media_player.play()

    def log(self, lines):
        f = open(os.path.join(self.video_path + "log.txt"), "w", encoding="utf8")
        f.writelines(lines)
        f.close()

    def play_next(self):
        keyboard.press(Key.right)

    def moveNplayNext(self, path):
        self.video = self.files[self.i]
        try:
            self.next_video = self.files[self.i + 1]
        except IndexError:
            self.i = 0
            self.next_video = self.files[self.i + 1]
        # print("Currently playing : " + os.path.basename(self.files[self.i]))
        self.length = TinyTag.get(self.next_video).duration
        title.set(str(self.i + 1) + "/" + str(len(self.files)) + " : " + os.path.basename(
            self.files[self.i]) + "  [" + str(int(self.length)) + " s]")
        self.log(os.path.basename(self.files[self.i]))
        media = vlc.Media(self.next_video)
        self.media_player.set_media(media)
        self.media_player.play()
        shutil.move(self.video, path + "/" + os.path.basename(self.files[self.i]))
        self.files.remove(self.video)
        self.t = Timer(self.length, self.play_next)
        self.t.daemon = True
        self.t.start()

    def process_key_press(self, key):
        print(key)

        if self.t.is_alive():
            self.t.cancel()

        root.overrideredirect(True)
        try:
            if key == KeyCode(char='1'):
                self.one = self.video_path + "1"
                if not os.path.exists(self.one):
                    os.mkdir(self.one)
                self.moveNplayNext(self.one)

            if key == KeyCode(char='2'):
                self.two = self.video_path + "2"
                if not os.path.exists(self.two):
                    os.mkdir(self.two)
                self.moveNplayNext(self.two)

            if key == KeyCode(char='3'):
                self.three = self.video_path + "3"
                if not os.path.exists(self.three):
                    os.mkdir(self.three)
                self.moveNplayNext(self.three)

            if key == KeyCode(char=','):
                current_vol = self.media_player.audio_get_volume()
                self.media_player.audio_set_volume(current_vol - 5)

            if key == KeyCode(char='.'):
                current_vol = self.media_player.audio_get_volume()
                self.media_player.audio_set_volume(current_vol + 5)

            if key == key.space:
                # print("Currently playing : " + os.path.basename(self.files[self.i]))
                title.set(str(self.i + 1) + "/" + str(len(self.files)) + " : " + os.path.basename(
                    self.files[self.i]) + "  [" + str(int(self.length)) + " s]")
                self.log(os.path.basename(self.files[self.i]))
                if next(self.toggle):
                    self.media_player.play()
                else:
                    self.media_player.pause()

            if key == key.right:
                self.i += 1
                if self.i + 1 > len(self.files):
                    self.i = 0
                # print("Currently playing : " + os.path.basename(self.files[self.i]))
                self.video = self.files[self.i]
                self.length = TinyTag.get(self.video).duration
                title.set(str(self.i + 1) + "/" + str(len(self.files)) + " : " + os.path.basename(
                    self.files[self.i]) + "  [" + str(int(self.length)) + " s]")
                self.log(os.path.basename(self.files[self.i]))
                media = vlc.Media(self.video)
                self.media_player.set_media(media)
                self.media_player.play()
                self.t = Timer(self.length, self.play_next)
                self.t.daemon = True
                self.t.start()
            if key == key.left:
                # self.pos = 0
                self.i -= 1
                if self.i < 0:
                    self.i = len(self.files) - 1
                # print("Currently playing : " + os.path.basename(self.files[self.i]))
                self.video = self.files[self.i]
                self.length = TinyTag.get(self.video).duration
                title.set(str(self.i + 1) + "/" + str(len(self.files)) + " : " + os.path.basename(
                    self.files[self.i]) + "  [" + str(int(self.length)) + " s]")
                self.log(os.path.basename(self.files[self.i]))
                media = vlc.Media(self.video)
                self.media_player.set_media(media)
                self.media_player.play()
                self.t = Timer(self.length, self.play_next)
                self.t.daemon = True
                self.t.start()
            if key == key.up:
                if not os.path.exists(self.fav_video_path):
                    os.mkdir(self.fav_video_path)
                self.moveNplayNext(self.fav_video_path)

            if key == key.down:
                if not os.path.exists(self.non_fav_video_path):
                    os.mkdir(self.non_fav_video_path)
                self.moveNplayNext(self.non_fav_video_path)

            if key == key.enter:
                self.media_player.toggle_fullscreen()

            if key == key.end:
                self.pos = self.media_player.get_position()
                self.pos += 0.1
                if self.pos >= 1:
                    self.play_next()
                    pass
                self.media_player.set_position(self.pos)

            if key == key.home:
                self.pos = self.media_player.get_position()
                self.pos -= 0.1
                if self.pos <= 0:
                    self.pos = 0
                self.media_player.set_position(self.pos)

            if key == key.esc:
                self.media_player.stop()
                root.destroy()
                exit()
        except AttributeError:
            pass

    def run(self):
        pynput.keyboard.Listener(on_press=self.process_key_press).start()


# Create object
root = Tk()

root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.configure(bg="white")
root.attributes('-alpha', 0.8)
root.wm_attributes("-topmost", True)
root.wm_attributes("-transparentcolor", "white")
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(20, weight=1)
title = StringVar()
percentLabel = Label(root, textvariable=title, bg="gray", font="TimeNewRoman")
# percentLabel.pack()
percentLabel.grid(row=1, column=20)
closeButton = Button(root, text="   X   ", command=root.quit, bg="gray", borderwidth=0, font=("TimeNewRoman", 13))
closeButton.grid(row=1, column=30)


def on_enter(e):
    percentLabel.grid(row=1, column=20)
    closeButton.config(background='red')


def on_leave(e):
    closeButton.config(background='gray')
    percentLabel.grid_forget()


closeButton.bind('<Enter>', on_enter)
closeButton.bind('<Leave>', on_leave)
percentLabel.grid_forget()
play = Player()
thr = threading.Thread(target=play.run).start()
root.overrideredirect(True)
root.mainloop()

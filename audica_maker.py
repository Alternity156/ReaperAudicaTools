"""
Importing sys and setting this variable is a must to get tkinter to work in reascript.
"""

import sys

sys.argv = ["Main"]

"""
We need stuff to work with, this part imports stuff.
"""

from reaper_python import *

from tkinter import Tk, Frame, LabelFrame, Label, Entry, Button, Scale, Checkbutton, OptionMenu, \
    IntVar, StringVar, Toplevel, font, HORIZONTAL

from tkinter.ttk import Notebook
from subprocess import Popen
from zipfile import ZipFile

import os
import time
import json

"""
Base64 strings from rpp files for OGG Vorbis render settings.

Could not find a way to accurately decode and recreate them, so I gathered these basic settings.
"""

vbr_zero_point_zero = "dmdnbwAAAAAAgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.0
vbr_zero_point_one = "dmdnb83MzD0AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.1
vbr_zero_point_two = "dmdnb83MTD4AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.2
vbr_zero_point_three = "dmdnb5qZmT4AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.3
vbr_zero_point_four = "dmdnb83MzD4AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.4
vbr_zero_point_five = "dmdnbwAAAD8AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.5
vbr_zero_point_six = "dmdnb5qZGT8AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.6
vbr_zero_point_seven = "dmdnbzMzMz8AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.7
vbr_zero_point_eight = "dmdnb83MTD8AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.8
vbr_zero_point_nine = "dmdnb2ZmZj8AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 0.9
vbr_one_point_zero = "dmdnbwAAgD8AgAAAAIAAAAAgAAAAAAEAAA=="  ## OGG Vorbis VBR 1.0

"""
Default track names, will be editable maybe one day?
"""

main_audio_track_name = "Main Audio"
extras_audio_track_name = "Extras Audio"
left_sustain_track_name = "Left Sustain"
right_sustain_track_name = "Right Sustain"

sampler_track_name = "SAMPLER"

expert_lh_track_name = "Expert - LH"
expert_rh_track_name = "Expert - RH"
expert_melee_track_name = "Expert - Melee"

advanced_lh_track_name = "Hard - LH"
advanced_rh_track_name = "Hard - RH"
advanced_melee_track_name = "Hard - Melee"

moderate_lh_track_name = "Normal - LH"
moderate_rh_track_name = "Normal - RH"
moderate_melee_track_name = "Normal - Melee"

beginner_lh_track_name = "Easy - LH"
beginner_rh_track_name = "Easy - RH"
beginner_melee_track_name = "Easy - Melee"

"""
REAPER command IDs
"""

file_export_project_midi = 40849

"""
Function to post messages in the REAPER console. Use that often, REAPER mostly don't show crash reports.
"""


def msg(m):
    RPR_ShowConsoleMsg(str(m) + "\n")


"""
Classes to handle Audica files
"""


class desc:
    songID = ""
    moggSong = ""
    title = ""
    artist = ""
    midiFile = ""
    targetDrums = ""
    fusionSpatialized = "fusion/guns/default/drums_default_spatial.fusion"
    fusionUnspatialized = "fusion/guns/default/drums_default_sub.fusion"
    sustainSongRight = ""
    sustainSongLeft = ""
    fxSong = ""
    tempo = 0.0
    songEndEvent = ""
    highScoreEvent = ""
    songEndPitchAdjust = 0.0
    prerollSeconds = 0.0
    previewStartSeconds = 0.0
    useMidiForCues = False
    hidden = False
    offset = 0
    author = ""

    def load_desc_file(self, file):
        try:
            f = open(file, 'r')
        except:
            f = file
        try:
            desc_file = json.load(f)
        except:
            desc_file = json.loads(f)
        self.songID = desc_file["songID"]
        self.moggSong = desc_file["moggSong"]
        self.title = desc_file["title"]
        self.artist = desc_file["artist"]
        try:
            self.author = desc_file["author"]
        except:
            try:
                self.author = desc_file["mapper"]
            except:
                pass
        self.midiFile = desc_file["midiFile"]
        try:
            self.targetDrums = desc_file["targetDrums"]
            if self.targetDrums == "":
                self.targetDrums = "fusion/target_drums/destruct.json"
        except:
            self.fusionSpatialized = desc_file["fusionSpatialized"]
            self.targetDrums = "fusion/target_drums/destruct.json"
            try:
                self.fusionUnspatialized = desc_file["fusionUnspatialized"]
            except:
                pass
        self.sustainSongRight = desc_file["sustainSongRight"]
        self.sustainSongLeft = desc_file["sustainSongLeft"]
        self.fxSong = desc_file["fxSong"]
        try:
            self.tempo = desc_file["tempo"]
        except:
            pass
        self.songEndEvent = desc_file["songEndEvent"][25:]
        try:
            self.highScoreEvent = desc_file["highScoreEvent"][34:]
        except:
            pass
        try:
            self.songEndPitchAdjust = desc_file["songEndPitchAdjust"]
        except:
            pass
        self.prerollSeconds = desc_file["prerollSeconds"]
        try:
            self.previewStartSeconds = desc_file["previewStartSeconds"]
        except:
            pass
        self.useMidiForCues = desc_file["useMidiForCues"]
        self.hidden = desc_file["hidden"]
        try:
            self.offset = desc_file["offset"]
        except:
            pass
        try:
            f.close()
        except:
            pass

    def save_desc_file(self, file):
        line = "{\n"
        line = line + "\t\"songID\": " + json.dumps(self.songID) + ",\n"
        line = line + "\t\"moggSong\": " + json.dumps(self.moggSong) + ",\n"
        line = line + "\t\"title\": " + json.dumps(self.title) + ",\n"
        line = line + "\t\"artist\": " + json.dumps(self.artist) + ",\n"
        line = line + "\t\"author\": " + json.dumps(self.author) + ",\n"
        line = line + "\t\"midiFile\": " + json.dumps(self.midiFile) + ",\n"
        line = line + "\t\"targetDrums\": " + json.dumps(self.targetDrums) + ",\n"
        line = line + "\t\"sustainSongRight\": " + json.dumps(self.sustainSongRight) + ",\n"
        line = line + "\t\"sustainSongLeft\": " + json.dumps(self.sustainSongLeft) + ",\n"
        line = line + "\t\"fxSong\": " + json.dumps(self.fxSong) + ",\n"
        line = line + "\t\"tempo\": " + json.dumps(self.tempo) + ",\n"
        line = line + "\t\"songEndEvent\": " + json.dumps("event:/song_end/song_end_" + self.songEndEvent) + ",\n"
        line = line + "\t\"highScoreEvent\": " + json.dumps(
            "event:/results/results_high_score_" + self.highScoreEvent) + ",\n"
        line = line + "\t\"songEndPitchAdjust\": " + json.dumps(self.songEndPitchAdjust) + ",\n"
        line = line + "\t\"prerollSeconds\": " + json.dumps(self.prerollSeconds) + ",\n"
        line = line + "\t\"previewStartSeconds\": " + json.dumps(self.previewStartSeconds) + ",\n"
        line = line + "\t\"useMidiForCues\": " + json.dumps(self.useMidiForCues) + ",\n"
        templine = line + "\t\"hidden\": " + json.dumps(self.hidden)
        if self.offset != 0:
            line = templine + ",\n"
        else:
            line = templine + "\n"
        templine = line + "\t\"offset\": " + json.dumps(self.offset)
        if self.offset != 0:
            line = templine + "\n"
        line = line + "}"

        f = open(file, "w")
        f.write(line)
        f.close()


class sustains:
    moggPathL = ""
    moggPathR = ""
    midiPath = ""
    pansL = 0.0
    pansR = 0.0
    volsL = 0.0
    volsR = 0.0

    def save_file_l(self, file):
        line = "(mogg_path \"" + self.moggPathL + "\")\n"
        line = line + "(midi_path \"" + self.midiPath + "\")\n"
        line = line + "\n"
        line = line + "(tracks\n"
        line = line + "  (\n"
        line = line + "    (sustain_l 0 event:/gameplay/sustain_left)\n"
        line = line + "  )\n"
        line = line + ")\n"
        line = line + "(pans (" + str(self.pansL) + "))\n"
        line = line + "(vols (" + str(self.volsL) + "))\n"
        f = open(file, "w")
        f.write(line)
        f.close()

    def save_file_r(self, file):
        line = "(mogg_path \"" + self.moggPathR + "\")\n"
        line = line + "(midi_path \"" + self.midiPath + "\")\n"
        line = line + "\n"
        line = line + "(tracks\n"
        line = line + "  (\n"
        line = line + "    (sustain_r 0 event:/gameplay/sustain_right)\n"
        line = line + "  )\n"
        line = line + ")\n"
        line = line + "(pans (" + str(self.pansR) + "))\n"
        line = line + "(vols (" + str(self.volsR) + "))\n"
        f = open(file, "w")
        f.write(line)
        f.close()


class song:
    moggPath = ""
    midiPath = ""
    pansL = 0.0
    pansR = 0.0
    volsL = 0.0
    volsR = 0.0

    def save_file(self, file):
        line = "(mogg_path \"" + self.moggPath + "\")\n"
        line = line + "(midi_path \"" + self.midiPath + "\")\n"
        line = line + "\n"
        line = line + "(tracks\n"
        line = line + "  (\n"
        line = line + "    (mix (0 1) event:/gameplay/song_audio)\n"
        line = line + "  )\n"
        line = line + ")\n"
        line = line + "(pans (" + str(self.pansL) + " " + str(self.pansR) + "))\n"
        line = line + "(vols (" + str(self.volsL) + " " + str(self.volsR) + "))\n"
        f = open(file, "w")
        f.write(line)
        f.close()


class extras:
    moggPath = ""
    midiPath = ""
    pansL = 0.0
    pansR = 0.0
    volsL = 0.0
    volsR = 0.0

    def save_file(self, file):
        line = "(mogg_path \"" + self.moggPath + "\")\n"
        line = line + "(midi_path \"" + self.midiPath + "\")\n"
        line = line + "\n"
        line = line + "(tracks\n"
        line = line + "  (\n"
        line = line + "    (mix (0 1) event:/gameplay/song_fx_audio)\n"
        line = line + "  )\n"
        line = line + ")\n"
        line = line + "(pans (" + str(self.pansL) + " " + str(self.pansR) + "))\n"
        line = line + "(vols (" + str(self.volsL) + " " + str(self.volsR) + "))\n"
        f = open(file, "w")
        f.write(line)
        f.close()


"""
Class to handle what needs to be done with rpp files.

We have to play with rpp files because I didn't find a way to render multiple audio files other than using the
REAPER command line arguments, which are used with a project, so we have to modify a rpp file as needed before
rendering each audio file.
"""


class rppHandler:
    def __init__(self, file):
        self.file = file
        self.data = []

        self.load_data()

    def load_data(self):
        f = open(self.file, "r")
        temp = []
        for line in f:
            temp.append(line)
        f.close()
        self.data = temp

    def save_data(self, filename):
        f = open(filename, "w")
        for line in self.data:
            f.write(line)
        f.close()

    def mute_track(self, track_name):
        self.changeMute(track_name, True)

    def unmute_track(self, track_name):
        self.changeMute(track_name, False)

    def set_file_render_path(self, path):
        path_string = "  RENDER_FILE \"" + path + "\"\n"
        temp_data = []
        for i in range(len(self.data)):
            if "RENDER_FILE" in self.data[i]:
                temp_data.append(path_string)
            else:
                temp_data.append(self.data[i])
        self.data = temp_data

    def set_sample_rate_and_channels(self, sample_rate, channels):
        settings_string = "  RENDER_FMT 0 " + str(channels) + " " + str(sample_rate) + "\n"
        temp_data = []
        for i in range(len(self.data)):
            if "RENDER_FMT" in self.data[i]:
                temp_data.append(settings_string)
            else:
                temp_data.append(self.data[i])
        self.data = temp_data

    def changeMute(self, track_name, to_mute):
        temp_data = []
        data_to_insert = []
        for i in range(len(self.data)):
            if "TRACK" in self.data[i]:
                if "NAME" in self.data[i + 1]:
                    if track_name in self.data[i + 1]:
                        settings = self.data[i + 6]
                        temp = ""
                        for l in range(len(settings)):
                            if l == 13:
                                if to_mute == True:
                                    temp = temp + "1"
                                elif to_mute == False:
                                    temp = temp + "0"
                                else:
                                    temp = temp + settings[l]
                            else:
                                temp = temp + settings[l]
                        data_to_insert = [i + 6, temp]
            if data_to_insert != []:
                if i != data_to_insert[0]:
                    temp_data.append(self.data[i])
            else:
                temp_data.append(self.data[i])
        if data_to_insert != []:
            temp_data.insert(data_to_insert[0], data_to_insert[1])
        self.data = temp_data

    def change_render_settings(self, setting):
        temp_data = []
        data_to_insert = []
        for i in range(len(self.data)):
            if "RENDER_CFG" in self.data[i]:
                setting = "    " + setting + "\n"
                data_to_insert = [i + 1, setting]
            if data_to_insert != []:
                if i != data_to_insert[0]:
                    temp_data.append(self.data[i])
            else:
                temp_data.append(self.data[i])
        if data_to_insert != []:
            temp_data.insert(data_to_insert[0], data_to_insert[1])
        self.data = temp_data


"""
Usefull functions, may be moved in their own py file eventually along with the rppHandler class.
"""


def get_reaper_install_dir():
    return RPR_GetExePath()


def get_curr_project_filename():
    proj = RPR_EnumProjects(-1, "", 512)
    if proj[2] == "":
        return None
    else:
        return proj[2]


def get_script_path():
    return sys.path[0]


def get_timeline_cursor_position():
    return RPR_GetCursorPosition()


def save_project():
    RPR_Main_SaveProject(0, True)


def export_midi():
    RPR_Main_OnCommand(file_export_project_midi, 0)


def ogg2mogg(input, output):
    ogg2mogg_path = get_script_path() + os.sep + "ogg2mogg.exe"
    Popen("\"" + ogg2mogg_path + "\" \"" + input + "\" \"" + output + "\"")


def test():
    msg(ogg2mogg("D:\\Audica Customs\\Projects\\Rush - Tom Sawyer\\tomsawyer.ogg",
                 "D:\\Audica Customs\\Projects\\Rush - Tom Sawyer\\tomsawyer.mogg"))


"""
Tkinter GUI
"""


class mainApp(Frame):

    def __init__(self, master):

        """
        Data file paths
        """

        self.settings_file = get_script_path() + os.sep + "settings.json"
        self.metadata_file = get_curr_project_filename().replace(".rpp", "_metadata.json")

        """
        Default settings
        """

        self.audio_quality = 7

        self.render_extras = False
        self.render_sustains = False
        self.warning_checkbox_var = IntVar()
        self.warning_checkbox_var.set(0)  # Warning box, if set to true it won't show again (True == 1)

        self.sample_rate_list = ["44100", "48000"]
        self.note_list = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
        self.drum_kit_list = ["Cosmic Cafe", "Crunch", "Destruct", "God City", "HM-X0X", "M-Cue", "Custom"]

        """
        Window setup
        """

        self.master = master

        self.notebook = Notebook(self.master)
        self.tab1 = Frame(self.notebook)
        self.tab2 = Frame(self.notebook)
        self.tab3 = Frame(self.notebook)

        """
        Tab 1
        """

        self.song_id_label = Label(self.tab1, text="songID: ")
        self.song_id_label.grid(row=0, column=0)

        self.song_id_entry_var = StringVar()
        self.song_id_entry_var.set("")
        self.song_id_entry = Entry(self.tab1, textvariable=self.song_id_entry_var, width=24)
        self.song_id_entry.grid(row=0, column=1, columnspan=2)

        self.title_label = Label(self.tab1, text="Title: ")
        self.title_label.grid(row=1, column=0)

        self.title_entry_var = StringVar()
        self.title_entry_var.set("")
        self.title_entry = Entry(self.tab1, textvariable=self.title_entry_var, width=24)
        self.title_entry.grid(row=1, column=1, columnspan=2)

        self.artist_label = Label(self.tab1, text="Artist: ")
        self.artist_label.grid(row=2, column=0)

        self.artist_entry_var = StringVar()
        self.artist_entry_var.set("")
        self.artist_entry = Entry(self.tab1, textvariable=self.artist_entry_var, width=24)
        self.artist_entry.grid(row=2, column=1, columnspan=2)

        self.author_label = Label(self.tab1, text="Author: ")
        self.author_label.grid(row=3, column=0)

        self.author_entry_var = StringVar()
        self.author_entry_var.set("")
        self.author_entry = Entry(self.tab1, textvariable=self.author_entry_var, width=24)
        self.author_entry.grid(row=3, column=1, columnspan=2)

        self.preroll_seconds_label = Label(self.tab1, text="Preroll seconds: ")
        self.preroll_seconds_label.grid(row=4, column=0)

        self.preroll_seconds_entry_var = StringVar()
        self.preroll_seconds_entry_var.set("0.0")
        self.preroll_seconds_entry = Entry(self.tab1, textvariable=self.preroll_seconds_entry_var, width=24)
        self.preroll_seconds_entry.grid(row=4, column=1, columnspan=2)

        self.preview_start_seconds_label = Label(self.tab1, text="Preview start seconds: ")
        self.preview_start_seconds_label.grid(row=5, column=0)

        self.preview_start_seconds_entry_var = StringVar()
        self.preview_start_seconds_entry_var.set("0.0")
        self.preview_start_seconds_entry = Entry(self.tab1, textvariable=self.preview_start_seconds_entry_var)
        self.preview_start_seconds_entry.grid(row=5, column=1)

        self.set_preview_button = Button(self.tab1, text="Set", command=self.set_preview_start_seconds)
        self.set_preview_button.grid(row=5, column=2)

        self.end_pitch_adjust_label = Label(self.tab1, text="End Pitch Adjust: ")
        self.end_pitch_adjust_label.grid(row=6, column=0)

        self.end_pitch_adjust_entry_var = StringVar()
        self.end_pitch_adjust_entry_var.set("0.0")
        self.end_pitch_adjust_entry = Entry(self.tab1, textvariable=self.end_pitch_adjust_entry_var, width=24)
        self.end_pitch_adjust_entry.grid(row=6, column=1, columnspan=2)

        self.target_drums_section = LabelFrame(self.tab1, text="Target Drums")
        self.target_drums_section.grid(row=7, columnspan=3)

        self.target_drums_entry_var = StringVar()
        self.target_drums_entry_var.set("")
        self.target_drums_entry = Entry(self.target_drums_section, textvariable=self.target_drums_entry_var, width=26)
        self.target_drums_entry.grid(row=0, column=0)

        self.target_drums_dropdown_var = StringVar()
        self.target_drums_dropdown_var.set("Destruct")
        self.target_drums_dropdown = OptionMenu(self.target_drums_section, self.target_drums_dropdown_var,
                                                *self.drum_kit_list)
        self.setMaxWidth(self.drum_kit_list, self.target_drums_dropdown)
        self.target_drums_dropdown.grid(row=0, column=1)

        self.song_end_event_section = LabelFrame(self.tab1, text="End Event")
        self.song_end_event_section.grid(row=8, column=0)

        self.song_end_event_dropdown_var = StringVar()
        self.song_end_event_dropdown_var.set(self.note_list[0])
        self.song_end_event_dropdown = OptionMenu(self.song_end_event_section, self.song_end_event_dropdown_var,
                                                  *self.note_list)
        self.song_end_event_dropdown.config(width=10)
        self.song_end_event_dropdown.grid()

        self.high_score_event_section = LabelFrame(self.tab1, text="High Score Event")
        self.high_score_event_section.grid(row=8, column=1, columnspan=2)

        self.high_score_event_dropdown_var = StringVar()
        self.high_score_event_dropdown_var.set(self.note_list[0])
        self.high_score_event_dropdown = OptionMenu(self.high_score_event_section, self.high_score_event_dropdown_var,
                                                    *self.note_list)
        self.high_score_event_dropdown.config(width=10)
        self.high_score_event_dropdown.grid()

        self.override_song_id_checkbox_var = IntVar()
        self.override_song_id_checkbox = Checkbutton(self.tab1, variable=self.override_song_id_checkbox_var,
                                                     text="Override songID variable")
        self.override_song_id_checkbox.grid(row=9, columnspan=3)

        self.dont_render_checkbox_var = IntVar()
        self.dont_render_checkbox = Checkbutton(self.tab1, variable=self.dont_render_checkbox_var,
                                                text="Don't render audio")
        self.dont_render_checkbox.grid(row=10, columnspan=3)

        self.save_metadata_button = Button(self.tab1, text="Save metadata and moggsong", command=self.save_metadata)
        self.save_metadata_button.grid(row=11, columnspan=3)

        self.update_midi_button = Button(self.tab1, text="Update MIDI", command=self.update_midi)
        self.update_midi_button.grid(row=12, columnspan=3)

        self.start_button = Button(self.tab1, text="Make Audica file", command=self.handle_start)
        self.start_button.grid(row=13, columnspan=3)

        self.project_needed_explaination = Label(self.tab1, text="Your project file needs to be updated (saved).\n" \
                                                                 "Make sure to save your project before rendering.\n\n" \
                                                                 "Don't render audio will assume that audio exists\n" \
                                                                 "with names: projectfilename.mogg,\n" \
                                                                 "projectfilename_extras.mogg,\n" \
                                                                 "projectfilename_sustain_l.mogg and/or\n" \
                                                                 "projectfilename_sustain_r.mogg in the project\n" \
                                                                 "folder, matching the chosen track in the Settings\n" \
                                                                 "tab.")
        self.project_needed_explaination.grid(row=14, columnspan=3, sticky="W")

        """
        Tab 2
        """

        self.main_audio_label = Label(self.tab2, text="Main Audio")
        self.main_audio_label.grid(row=0, column=0, columnspan=4)

        self.main_audio_pan_label = Label(self.tab2, text="Pan")
        self.main_audio_pan_label.grid(row=1, column=0, columnspan=2)

        self.main_audio_pan_left_frame = LabelFrame(self.tab2, text="L")
        self.main_audio_pan_left_frame.grid(row=2, column=0)

        self.main_audio_pan_left_slider_var = IntVar()
        self.main_audio_pan_left_slider_var.set(0.0)
        self.main_audio_pan_left_slider = Scale(self.main_audio_pan_left_frame,
                                                variable=self.main_audio_pan_left_slider_var, to=-10.0, from_=10.0,
                                                digits=3, resolution=0.01)
        self.main_audio_pan_left_slider.grid(row=0, column=0)

        self.main_audio_pan_right_frame = LabelFrame(self.tab2, text="R")
        self.main_audio_pan_right_frame.grid(row=2, column=1)

        self.main_audio_pan_right_slider_var = IntVar()
        self.main_audio_pan_right_slider_var.set(0.0)
        self.main_audio_pan_right_slider = Scale(self.main_audio_pan_right_frame,
                                                 variable=self.main_audio_pan_right_slider_var, to=-10.0, from_=10.0,
                                                 digits=3, resolution=0.01)
        self.main_audio_pan_right_slider.grid(row=0, column=0)

        self.main_audio_vol_label = Label(self.tab2, text="Volume")
        self.main_audio_vol_label.grid(row=1, column=2, columnspan=2)

        self.main_audio_vol_left_frame = LabelFrame(self.tab2, text="L")
        self.main_audio_vol_left_frame.grid(row=2, column=2)

        self.main_audio_vol_left_slider_var = IntVar()
        self.main_audio_vol_left_slider_var.set(0.0)
        self.main_audio_vol_left_slider = Scale(self.main_audio_vol_left_frame,
                                                variable=self.main_audio_vol_left_slider_var, to=-10.0, from_=10.0,
                                                digits=3, resolution=0.01)
        self.main_audio_vol_left_slider.grid(row=0, column=0)

        self.main_audio_vol_right_frame = LabelFrame(self.tab2, text="R")
        self.main_audio_vol_right_frame.grid(row=2, column=3)

        self.main_audio_vol_right_slider_var = IntVar()
        self.main_audio_vol_right_slider_var.set(0.0)
        self.main_audio_vol_right_slider = Scale(self.main_audio_vol_right_frame,
                                                 variable=self.main_audio_vol_right_slider_var, to=-10.0, from_=10.0,
                                                 digits=3, resolution=0.01)
        self.main_audio_vol_right_slider.grid(row=0, column=0)

        self.extras_audio_label = Label(self.tab2, text="Extras Audio")
        self.extras_audio_label.grid(row=3, column=0, columnspan=4)

        self.extras_audio_pan_label = Label(self.tab2, text="Pan")
        self.extras_audio_pan_label.grid(row=4, column=0, columnspan=2)

        self.extras_audio_pan_left_frame = LabelFrame(self.tab2, text="L")
        self.extras_audio_pan_left_frame.grid(row=5, column=0)

        self.extras_audio_pan_left_slider_var = IntVar()
        self.extras_audio_pan_left_slider_var.set(0.0)
        self.extras_audio_pan_left_slider = Scale(self.extras_audio_pan_left_frame,
                                                  variable=self.extras_audio_pan_left_slider_var, to=-10.0, from_=10.0,
                                                  digits=3, resolution=0.01)
        self.extras_audio_pan_left_slider.grid(row=0, column=0)

        self.extras_audio_pan_right_frame = LabelFrame(self.tab2, text="R")
        self.extras_audio_pan_right_frame.grid(row=5, column=1)

        self.extras_audio_pan_right_slider_var = IntVar()
        self.extras_audio_pan_right_slider_var.set(0.0)
        self.extras_audio_pan_right_slider = Scale(self.extras_audio_pan_right_frame,
                                                   variable=self.extras_audio_pan_right_slider_var, to=-10.0,
                                                   from_=10.0, digits=3, resolution=0.01)
        self.extras_audio_pan_right_slider.grid(row=0, column=0)

        self.extras_audio_vol_label = Label(self.tab2, text="Volume")
        self.extras_audio_vol_label.grid(row=4, column=2, columnspan=2)

        self.extras_audio_vol_left_frame = LabelFrame(self.tab2, text="L")
        self.extras_audio_vol_left_frame.grid(row=5, column=2)

        self.extras_audio_vol_left_slider_var = IntVar()
        self.extras_audio_vol_left_slider_var.set(0.0)
        self.extras_audio_vol_left_slider = Scale(self.extras_audio_vol_left_frame,
                                                  variable=self.extras_audio_vol_left_slider_var, to=-10.0, from_=10.0,
                                                  digits=3, resolution=0.01)
        self.extras_audio_vol_left_slider.grid(row=0, column=0)

        self.extras_audio_vol_right_frame = LabelFrame(self.tab2, text="R")
        self.extras_audio_vol_right_frame.grid(row=5, column=3)

        self.extras_audio_vol_right_slider_var = IntVar()
        self.extras_audio_vol_right_slider_var.set(0.0)
        self.extras_audio_vol_right_slider = Scale(self.extras_audio_vol_right_frame,
                                                   variable=self.extras_audio_vol_right_slider_var, to=-10.0,
                                                   from_=10.0, digits=3, resolution=0.01)
        self.extras_audio_vol_right_slider.grid(row=0, column=0)

        self.sustain_audio_label = Label(self.tab2, text="Sustain Audio")
        self.sustain_audio_label.grid(row=6, column=0, columnspan=4)

        self.sustain_audio_pan_label = Label(self.tab2, text="Pan")
        self.sustain_audio_pan_label.grid(row=7, column=0, columnspan=2)

        self.sustain_audio_pan_left_frame = LabelFrame(self.tab2, text="L")
        self.sustain_audio_pan_left_frame.grid(row=8, column=0)

        self.sustain_audio_pan_left_slider_var = IntVar()
        self.sustain_audio_pan_left_slider_var.set(0.0)
        self.sustain_audio_pan_left_slider = Scale(self.sustain_audio_pan_left_frame,
                                                   variable=self.sustain_audio_pan_left_slider_var, to=-10.0,
                                                   from_=10.0, digits=3, resolution=0.01)
        self.sustain_audio_pan_left_slider.grid(row=0, column=0)

        self.sustain_audio_pan_right_frame = LabelFrame(self.tab2, text="R")
        self.sustain_audio_pan_right_frame.grid(row=8, column=1)

        self.sustain_audio_pan_right_slider_var = IntVar()
        self.sustain_audio_pan_right_slider_var.set(0.0)
        self.sustain_audio_pan_right_slider = Scale(self.sustain_audio_pan_right_frame,
                                                    variable=self.sustain_audio_pan_right_slider_var, to=-10.0,
                                                    from_=10.0, digits=3, resolution=0.01)
        self.sustain_audio_pan_right_slider.grid(row=0, column=0)

        self.sustain_audio_vol_label = Label(self.tab2, text="Volume")
        self.sustain_audio_vol_label.grid(row=7, column=2, columnspan=2)

        self.sustain_audio_vol_left_frame = LabelFrame(self.tab2, text="L")
        self.sustain_audio_vol_left_frame.grid(row=8, column=2)

        self.sustain_audio_vol_left_slider_var = IntVar()
        self.sustain_audio_vol_left_slider_var.set(0.0)
        self.sustain_audio_vol_left_slider = Scale(self.sustain_audio_vol_left_frame,
                                                   variable=self.sustain_audio_vol_left_slider_var, to=-10.0,
                                                   from_=10.0, digits=3, resolution=0.01)
        self.sustain_audio_vol_left_slider.grid(row=0, column=0)

        self.sustain_audio_vol_right_frame = LabelFrame(self.tab2, text="R")
        self.sustain_audio_vol_right_frame.grid(row=8, column=3)

        self.sustain_audio_vol_right_slider_var = IntVar()
        self.sustain_audio_vol_right_slider_var.set(0.0)
        self.sustain_audio_vol_right_slider = Scale(self.sustain_audio_vol_right_frame,
                                                    variable=self.sustain_audio_vol_right_slider_var, to=-10.0,
                                                    from_=10.0, digits=3, resolution=0.01)
        self.sustain_audio_vol_right_slider.grid(row=0, column=0)

        """
        Tab 3
        """

        self.audio_quality_frame = LabelFrame(self.tab3, text="Audio Quality")
        self.audio_quality_frame.grid(row=0, column=0, rowspan=3)

        self.slider_var = IntVar()
        self.slider_var.set(self.audio_quality)
        self.slider = Scale(self.audio_quality_frame, orient=HORIZONTAL, variable=self.slider_var, to=10)
        self.slider.grid(row=1, column=0)

        self.render_extras_checkbox_var = IntVar()
        self.render_extras_checkbox = Checkbutton(self.tab3, variable=self.render_extras_checkbox_var,
                                                  text="Render extras audio")
        self.render_extras_checkbox.grid(row=0, column=1, columnspan=2, sticky="W")

        self.render_sustains_checkbox_var = IntVar()
        self.render_sustains_checkbox = Checkbutton(self.tab3, variable=self.render_sustains_checkbox_var,
                                                    text="Render sustains audio")
        self.render_sustains_checkbox.grid(row=1, column=1, columnspan=2, sticky="W")

        self.sample_rate_dropdown_var = StringVar()
        self.sample_rate_dropdown_var.set(self.sample_rate_list[0])
        self.sample_rate_dropdown = OptionMenu(self.tab3, self.sample_rate_dropdown_var, *self.sample_rate_list)
        self.sample_rate_dropdown.grid(row=2, column=1, sticky="E")

        self.sample_rate_label = Label(self.tab3, text="Hz")
        self.sample_rate_label.grid(row=2, column=2, sticky="W")

        self.render_wait_time_label = Label(self.tab3, text="Render wait time: ")
        self.render_wait_time_label.grid(row=3, column=0)

        self.render_wait_time_entry_var = StringVar()
        self.render_wait_time_entry_var.set(30.0)
        self.render_wait_time_entry = Entry(self.tab3, textvariable=self.render_wait_time_entry_var)
        self.render_wait_time_entry.grid(row=3, column=1, columnspan=2)

        self.save_settings_button = Button(self.tab3, text="Save Settings", command=self.save_settings)
        self.save_settings_button.grid(row=5, columnspan=3)

        self.render_wait_time_explaination = Label(self.tab3, text="Render wait time is the time to wait to start the\n" \
                                                                   "next render. This time includes the render time of\n" \
                                                                   "the next audio file that will be rendered and time to\n" \
                                                                   "open and close REAPER. Until I find a better way\n" \
                                                                   "to render, this is what works. During this wait\n" \
                                                                   "time, your REAPER instance will freeze, along with\n" \
                                                                   "this window, so don't be alarmed.\n\n" \
                                                                   "If the render wait time is too short, the process will\n" \
                                                                   "either crash, or not work properly. The time will vary\n" \
                                                                   "depending on your machine and your project.")
        self.render_wait_time_explaination.grid(row=7, columnspan=3, sticky="W")

        """
        Final notebook setup
        """

        self.notebook.add(self.tab1, text="Metadata")
        self.notebook.add(self.tab2, text="moggsong")
        self.notebook.add(self.tab3, text="Render")

        self.notebook.grid(row=0, column=0)

        """
        Trace setup
        """

        self.title_entry_var.trace("w", self.songID_entry_tracer)
        self.author_entry_var.trace("w", self.songID_entry_tracer)
        self.override_song_id_checkbox_var.trace("w", self.songID_override_tracer)
        self.target_drums_dropdown_var.trace("w", self.target_drums_tracer)

        """
        Loading stuff if stuff exists
        """

        try:
            self.load_settings()
        except:
            pass
        try:
            self.load_metadata()
        except:
            pass

        """
        Activate tracers once after loading to make sure the GUI is behaving correctly.
        """

        self.songID_entry_tracer()
        self.songID_override_tracer()
        self.target_drums_tracer()

    def handle_start(self):
        if self.warning_checkbox_var.get() == 0:
            self.warning_popup()
            if self.warning_checkbox_var.get() == 1:
                self.save_settings()
        self.make_audica()

    def get_project_path(self):
        project_path = get_curr_project_filename()

        if project_path == None:
            self.warning2 = Toplevel()
            self.warning2_label = Label(self.warning2, text="Could not find your REAPER project.\n\n" \
                                                            "The procedure requires a reaper project so\n" \
                                                            "you will now get asked to save your project.")
            self.warning2_label.grid(row=0)
            self.warning2_button = Button(self.warning2, text="Continue", command=self.warning2.destroy)
            self.warning2_button.grid(row=1)
            self.warning2.wait_window()
            save_project()
            project_path = get_curr_project_filename()

        return project_path

    def update_midi(self):
        project_path = self.get_project_path()
        export_midi()
        midi_filename = project_path.replace(".rpp", ".mid")
        audica_filename = os.path.dirname(project_path) + os.sep + self.song_id_entry_var.get() + ".audica"
        temp_audica_file = os.path.dirname(project_path) + os.sep + "temp.audica"
        f_in = ZipFile(audica_filename, "r")
        f_out = ZipFile(temp_audica_file, "w")
        for item in f_in.infolist():
            buffer = f_in.read(item.filename)
            if item.filename[-4:] != ".mid":
                f_out.writestr(item, buffer)
        f_out.write(midi_filename, os.path.basename(midi_filename))
        f_out.close()
        f_in.close()
        os.remove(audica_filename)
        os.remove(midi_filename)
        os.rename(temp_audica_file, audica_filename)

    def make_audica(self):
        extras_checkbox = self.render_extras_checkbox_var.get()
        sustains_checkbox = self.render_sustains_checkbox_var.get()
        project_path = self.get_project_path()

        export_midi()

        if self.dont_render_checkbox_var.get() == 0:
            self.render()

        desc_file = desc()
        song_moggsong = song()

        main_moggsong_filename = project_path.replace(".rpp", ".moggsong")
        main_mogg_filename = project_path.replace(".rpp", ".mogg")
        main_ogg_filename = project_path.replace(".rpp", ".ogg")
        desc_filename = os.path.dirname(project_path) + os.sep + "song.desc"
        midi_filename = project_path.replace(".rpp", ".mid")

        desc_file.moggSong = os.path.basename(main_moggsong_filename)
        desc_file.midiFile = os.path.basename(midi_filename)
        desc_file.songID = self.song_id_entry_var.get()
        desc_file.title = self.title_entry_var.get()
        desc_file.artist = self.artist_entry_var.get()
        desc_file.targetDrums = self.target_drums_entry_var.get()
        desc_file.songEndEvent = self.song_end_event_dropdown_var.get()
        desc_file.highScoreEvent = self.high_score_event_dropdown_var.get()
        desc_file.songEndPitchAdjust = float(self.end_pitch_adjust_entry_var.get())
        desc_file.prerollSeconds = float(self.preroll_seconds_entry_var.get())
        desc_file.previewStartSeconds = float(self.preview_start_seconds_entry_var.get())
        desc_file.author = self.author_entry_var.get()
        desc_file.useMidiForCues = True

        song_moggsong.moggPath = os.path.basename(main_mogg_filename)
        song_moggsong.midiPath = os.path.basename(midi_filename)
        song_moggsong.pansL = float(self.main_audio_pan_left_slider_var.get())
        song_moggsong.pansR = float(self.main_audio_pan_right_slider_var.get())
        song_moggsong.volsL = float(self.main_audio_vol_left_slider_var.get())
        song_moggsong.volsR = float(self.main_audio_vol_right_slider_var.get())
        song_moggsong.save_file(main_moggsong_filename)

        if extras_checkbox == 1:
            extras_moggsong_filename = project_path.replace(".rpp", "_extras.moggsong")
            extras_mogg_filename = project_path.replace(".rpp", "_extras.mogg")
            extras_ogg_filename = project_path.replace(".rpp", "_extras.ogg")

            desc_file.fxSong = os.path.basename(extras_moggsong_filename)

            extras_moggsong = extras()
            extras_moggsong.moggPath = os.path.basename(extras_mogg_filename)
            extras_moggsong.midiPath = os.path.basename(midi_filename)
            extras_moggsong.pansL = float(self.extras_audio_pan_left_slider_var.get())
            extras_moggsong.pansR = float(self.extras_audio_pan_right_slider_var.get())
            extras_moggsong.volsL = float(self.extras_audio_vol_left_slider_var.get())
            extras_moggsong.volsR = float(self.extras_audio_vol_right_slider_var.get())
            extras_moggsong.save_file(extras_moggsong_filename)

        if sustains_checkbox == 1:
            sustain_l_moggsong_filename = project_path.replace(".rpp", "_sustain_l.moggsong")
            sustain_l_mogg_filename = project_path.replace(".rpp", "_sustain_l.mogg")
            sustain_l_ogg_filename = project_path.replace(".rpp", "_sustain_l.ogg")
            sustain_r_moggsong_filename = project_path.replace(".rpp", "_sustain_r.moggsong")
            sustain_r_mogg_filename = project_path.replace(".rpp", "_sustain_r.mogg")
            sustain_r_ogg_filename = project_path.replace(".rpp", "_sustain_r.ogg")

            desc_file.sustainSongLeft = os.path.basename(sustain_l_moggsong_filename)
            desc_file.sustainSongRight = os.path.basename(sustain_r_moggsong_filename)

            sustains_moggsong = sustains()
            sustains_moggsong.moggPathL = os.path.basename(sustain_l_mogg_filename)
            sustains_moggsong.moggPathR = os.path.basename(sustain_r_mogg_filename)
            sustains_moggsong.midiPath = os.path.basename(midi_filename)
            sustains_moggsong.pansL = float(self.sustain_audio_pan_left_slider_var.get())
            sustains_moggsong.pansR = float(self.sustain_audio_pan_right_slider_var.get())
            sustains_moggsong.volsL = float(self.sustain_audio_vol_left_slider_var.get())
            sustains_moggsong.volsR = float(self.sustain_audio_vol_right_slider_var.get())
            sustains_moggsong.save_file_l(sustain_l_moggsong_filename)
            sustains_moggsong.save_file_r(sustain_r_moggsong_filename)

        desc_file.save_desc_file(desc_filename)
        processes = []

        if self.dont_render_checkbox_var.get() == 0:
            p1 = ogg2mogg(main_ogg_filename, main_mogg_filename)
            processes.append(p1)
            if extras_checkbox == 1:
                p2 = ogg2mogg(extras_ogg_filename, extras_mogg_filename)
                processes.append(p2)
            if sustains_checkbox == 1:
                p3 = ogg2mogg(sustain_l_ogg_filename, sustain_l_mogg_filename)
                p4 = ogg2mogg(sustain_r_ogg_filename, sustain_r_mogg_filename)
                processes.append(p3)
                processes.append(p4)

        for p in processes:
            p.kill()

        audica_filename = os.path.dirname(project_path) + os.sep + self.song_id_entry_var.get() + ".audica"

        f = ZipFile(audica_filename, "w")

        f.write(desc_filename, os.path.basename(desc_filename))
        f.write(midi_filename, os.path.basename(midi_filename))
        f.write(main_mogg_filename, os.path.basename(main_mogg_filename))
        f.write(main_moggsong_filename, os.path.basename(main_moggsong_filename))
        if extras_checkbox == 1:
            f.write(extras_mogg_filename, os.path.basename(extras_mogg_filename))
            f.write(extras_moggsong_filename, os.path.basename(extras_moggsong_filename))
        if sustains_checkbox == 1:
            f.write(sustain_l_mogg_filename, os.path.basename(sustain_l_mogg_filename))
            f.write(sustain_l_moggsong_filename, os.path.basename(sustain_l_moggsong_filename))
            f.write(sustain_r_mogg_filename, os.path.basename(sustain_r_mogg_filename))
            f.write(sustain_r_moggsong_filename, os.path.basename(sustain_r_moggsong_filename))
        f.close()

        os.remove(desc_filename)
        os.remove(midi_filename)
        try:
            os.remove(main_ogg_filename)
        except:
            pass
        os.remove(main_moggsong_filename)
        if extras_checkbox == 1:
            try:
                os.remove(extras_ogg_filename)
            except:
                pass
            os.remove(extras_moggsong_filename)
        if sustains_checkbox == 1:
            try:
                os.remove(sustain_l_ogg_filename)
                os.remove(sustain_r_ogg_filename)
            except:
                pass
            os.remove(sustain_l_moggsong_filename)
            os.remove(sustain_r_moggsong_filename)

    def warning_popup(self):
        self.warning = Toplevel()

        self.warning_label_1 = Label(self.warning, text="Your main instance of REAPER and this script will freeze\n" \
                                                        "for the wait time set in seconds times the number of audio\n" \
                                                        "files to render, for example: If you render sustains and\n" \
                                                        "main audio with a 20 seconds wait time, they will freeze for\n" \
                                                        "60 seconds.")
        self.warning_label_1.grid(row=0)

        self.warning_label_2 = Label(self.warning, text="You will aslo be asked to export your MIDI file,\n" \
                                                        "it needs to be in the same folder as your project with the\n" \
                                                        "same filename as your project, but .mid instead of .rpp.")
        self.warning_label_2.grid(row=1)

        self.warning_checkbox = Checkbutton(self.warning, variable=self.warning_checkbox_var,
                                            text="Don't show this again")
        self.warning_checkbox.grid(row=2)

        self.warning_button = Button(self.warning, text="Continue", command=self.warning.destroy)
        self.warning_button.grid(row=3)

        self.warning.wait_window()

    def render(self):
        extras = self.render_extras_checkbox_var.get()
        sustains = self.render_sustains_checkbox_var.get()
        project_rpp = get_curr_project_filename()
        rpp = rppHandler(project_rpp)
        main_audio_rpp = project_rpp.replace(".rpp", "_main.rpp")
        extras_audio_rpp = project_rpp.replace(".rpp", "_extras.rpp")
        sustain_l_audio_rpp = project_rpp.replace(".rpp", "_sustain_l.rpp")
        sustain_r_audio_rpp = project_rpp.replace(".rpp", "_sustain_r.rpp")
        files_to_render = []
        rpp.change_render_settings(self.get_audio_quality_string())
        rpp.set_sample_rate_and_channels(self.sample_rate_dropdown_var.get(), "2")
        rpp.mute_track(sampler_track_name)
        rpp.mute_track(extras_audio_track_name)
        rpp.mute_track(left_sustain_track_name)
        rpp.mute_track(right_sustain_track_name)
        rpp.unmute_track(main_audio_track_name)
        rpp.set_file_render_path(main_audio_rpp.replace("_main.rpp", ".ogg"))
        rpp.save_data(main_audio_rpp)
        files_to_render.append(main_audio_rpp)
        if extras == 1:
            rpp.mute_track(main_audio_track_name)
            rpp.unmute_track(extras_audio_track_name)
            rpp.set_file_render_path(extras_audio_rpp.replace(".rpp", ".ogg"))
            rpp.save_data(extras_audio_rpp)
            files_to_render.append(extras_audio_rpp)
        if sustains == 1:
            rpp.set_sample_rate_and_channels(self.sample_rate_dropdown_var.get(), "1")
            rpp.mute_track(main_audio_track_name)
            rpp.mute_track(extras_audio_track_name)
            rpp.unmute_track(left_sustain_track_name)
            rpp.set_file_render_path(sustain_l_audio_rpp.replace(".rpp", ".ogg"))
            rpp.save_data(sustain_l_audio_rpp)
            files_to_render.append(sustain_l_audio_rpp)
            rpp.mute_track(left_sustain_track_name)
            rpp.unmute_track(right_sustain_track_name)
            rpp.set_file_render_path(sustain_r_audio_rpp.replace(".rpp", ".ogg"))
            rpp.save_data(sustain_r_audio_rpp)
            files_to_render.append(sustain_r_audio_rpp)
        reaper_path = get_reaper_install_dir() + os.sep + "reaper.exe"
        processes = []
        for project in files_to_render:
            p = Popen("\"" + reaper_path + "\" -nosplash -renderproject \"" + project + "\"")
            processes.append(p)
            time.sleep(float(self.render_wait_time_entry_var.get()))
        for p in processes:
            p.kill()
        os.remove(main_audio_rpp)
        if extras == 1:
            os.remove(extras_audio_rpp)
        if sustains == 1:
            os.remove(sustain_l_audio_rpp)
            os.remove(sustain_r_audio_rpp)
        return files_to_render

    def set_preview_start_seconds(self):
        self.preview_start_seconds_entry_var.set(get_timeline_cursor_position())

    def save_settings(self):
        data = {"audio_quality": self.slider_var.get(),
                "render_extras_audio": self.render_extras_checkbox_var.get(),
                "render_sustain_audio": self.render_sustains_checkbox_var.get(),
                "sample_rate": self.sample_rate_dropdown_var.get(),
                "render_wait_time": self.render_wait_time_entry_var.get(),
                "warning_popup": self.warning_checkbox_var.get()
                }
        with open(self.settings_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_settings(self):
        f = open(self.settings_file, "r")
        data = json.load(f)
        f.close()
        self.slider_var.set(data["audio_quality"])
        self.render_extras_checkbox_var.set(data["render_extras_audio"])
        self.render_sustains_checkbox_var.set(data["render_sustain_audio"])
        self.sample_rate_dropdown_var.set(data["sample_rate"])
        self.render_wait_time_entry_var.set(data["render_wait_time"])
        self.warning_checkbox_var.set(data["warning_popup"])

    def save_metadata(self):
        data = {"songID": self.song_id_entry_var.get(),
                "title": self.title_entry_var.get(),
                "artist": self.artist_entry_var.get(),
                "author": self.author_entry_var.get(),
                "preroll_seconds": self.preroll_seconds_entry_var.get(),
                "preview_start_seconds": self.preview_start_seconds_entry_var.get(),
                "end_pitch_adjust": self.end_pitch_adjust_entry_var.get(),
                "target_drums_path": self.target_drums_entry_var.get(),
                "target_drums_selection": self.target_drums_dropdown_var.get(),
                "end_event": self.song_end_event_dropdown_var.get(),
                "high_score_event": self.high_score_event_dropdown_var.get(),
                "main_audio_pan_left": self.main_audio_pan_left_slider_var.get(),
                "main_audio_pan_right": self.main_audio_pan_right_slider_var.get(),
                "main_audio_vol_left": self.main_audio_vol_left_slider_var.get(),
                "main_audio_vol_right": self.main_audio_vol_right_slider_var.get(),
                "extras_audio_pan_left": self.extras_audio_pan_left_slider_var.get(),
                "extras_audio_pan_right": self.extras_audio_pan_right_slider_var.get(),
                "extras_audio_vol_left": self.extras_audio_vol_left_slider_var.get(),
                "extras_audio_vol_right": self.extras_audio_vol_right_slider_var.get(),
                "sustain_audio_pan_left": self.sustain_audio_pan_left_slider_var.get(),
                "sustain_audio_pan_right": self.sustain_audio_pan_right_slider_var.get(),
                "sustain_audio_vol_left": self.sustain_audio_vol_left_slider_var.get(),
                "sustain_audio_vol_right": self.sustain_audio_vol_right_slider_var.get(),
                "dont_render": self.dont_render_checkbox_var.get(),
                "override_song_id": self.override_song_id_checkbox_var.get()
                }
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_metadata(self):
        f = open(self.metadata_file, "r")
        data = json.load(f)
        f.close()
        self.override_song_id_checkbox_var.set(data["override_song_id"])
        self.song_id_entry_var.set(data["songID"])
        self.title_entry_var.set(data["title"])
        self.artist_entry_var.set(data["artist"])
        self.author_entry_var.set(data["author"])
        self.preroll_seconds_entry_var.set(data["preroll_seconds"])
        self.preview_start_seconds_entry_var.set(data["preview_start_seconds"])
        self.end_pitch_adjust_entry_var.set(data["end_pitch_adjust"])
        self.target_drums_entry_var.set(data["target_drums"])
        self.target_drums_dropdown_var.set(data["target_drums_selection"])
        self.song_end_event_dropdown_var.set(data["end_event"])
        self.high_score_event_dropdown_var.set(data["high_score_event"])
        self.main_audio_pan_left_slider_var.set(data["main_audio_pan_left"])
        self.main_audio_pan_right_slider_var.set(data["main_audio_pan_right"])
        self.main_audio_vol_left_slider_var.set(data["main_audio_vol_left"])
        self.main_audio_vol_right_slider_var.set(data["main_audio_vol_right"])
        self.extras_audio_pan_left_slider_var.set(data["extras_audio_pan_left"])
        self.extras_audio_pan_right_slider_var.set(data["extras_audio_pan_right"])
        self.extras_audio_vol_left_slider_var.set(data["extras_audio_vol_left"])
        self.extras_audio_vol_right_slider_var.set(data["extras_audio_vol_right"])
        self.sustain_audio_pan_left_slider_var.set(data["sustain_audio_pan_left"])
        self.sustain_audio_pan_right_slider_var.set(data["sustain_audio_pan_right"])
        self.sustain_audio_vol_left_slider_var.set(data["sustain_audio_vol_left"])
        self.sustain_audio_vol_right_slider_var.set(data["sustain_audio_vol_right"])
        self.dont_render_checkbox_var.set(data["dont_render"])

    def songID_entry_tracer(self, *args):
        if self.override_song_id_checkbox_var.get() == 0:
            self.song_id_entry_var.set(
                self.title_entry_var.get().replace(" ", "") + "-" + self.author_entry_var.get().replace(" ", ""))

    def songID_override_tracer(self, *args):
        if self.override_song_id_checkbox_var.get() == 0:
            self.song_id_entry.config(state='readonly')
            self.songID_entry_tracer()
        elif self.override_song_id_checkbox_var.get() == 1:
            self.song_id_entry.config(state='normal')

    def target_drums_tracer(self, *args):
        if self.target_drums_dropdown_var.get() == "Custom":
            self.target_drums_entry.config(state='normal')
        else:
            self.target_drums_entry.config(state='readonly')
        if self.target_drums_dropdown_var.get() == "Destruct":
            self.target_drums_entry_var.set("fusion/target_drums/destruct.json")
        elif self.target_drums_dropdown_var.get() == "Cosmic Cafe":
            self.target_drums_entry_var.set("fusion/target_drums/cosmiccafe.json")
        elif self.target_drums_dropdown_var.get() == "Crunch":
            self.target_drums_entry_var.set("fusion/target_drums/crunch.json")
        elif self.target_drums_dropdown_var.get() == "God City":
            self.target_drums_entry_var.set("fusion/target_drums/godcity.json")
        elif self.target_drums_dropdown_var.get() == "HM-X0X":
            self.target_drums_entry_var.set("fusion/target_drums/hm-x0x.json")
        elif self.target_drums_dropdown_var.get() == "M-Cue":
            self.target_drums_entry_var.set("fusion/target_drums/m-cue.json")

    def setMaxWidth(self, stringList, element):
        f = font.nametofont(element.cget("font"))
        zerowidth = f.measure("0")
        w = max([f.measure(i) for i in stringList]) / zerowidth
        element.config(width=int(w))

    def get_audio_quality_string(self):
        if self.slider_var.get() == 0:
            return vbr_zero_point_zero
        elif self.slider_var.get() == 1:
            return vbr_zero_point_one
        elif self.slider_var.get() == 2:
            return vbr_zero_point_two
        elif self.slider_var.get() == 3:
            return vbr_zero_point_three
        elif self.slider_var.get() == 4:
            return vbr_zero_point_four
        elif self.slider_var.get() == 5:
            return vbr_zero_point_five
        elif self.slider_var.get() == 6:
            return vbr_zero_point_six
        elif self.slider_var.get() == 7:
            return vbr_zero_point_seven
        elif self.slider_var.get() == 8:
            return vbr_zero_point_eight
        elif self.slider_var.get() == 9:
            return vbr_zero_point_nine
        elif self.slider_var.get() == 10:
            return vbr_one_point_zero


"""
Loop setup
"""

root = Tk()
root.title("Audica Maker")

app = mainApp(root)

root.mainloop()

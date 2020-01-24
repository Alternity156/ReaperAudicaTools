import sys
sys.argv = ["Main"]

from reaper_python import *
from tkinter import Tk, Frame, Label, OptionMenu, StringVar, Button, Toplevel, Entry, END, LabelFrame, filedialog

import time
import json
import os

ticks_per_quarter = 480


def add_callback(control, fun):
    def inner():
        return fun(control)
    control['command'] = inner


def msg(m):
    RPR_ShowConsoleMsg(str(m) + "\n")


def get_curr_project_filename():
    proj = RPR_EnumProjects(-1, "", 512)
    if proj[2] == "":
        return None
    else:
        return proj[2]


def get_tracks_matching_names(match_strings):
    tracks = []
    tracknames = []
    for i in range(RPR_CountTracks(0)):
        retval, track, trackname, buffer_size = RPR_GetTrackName(RPR_GetTrack(0, i), "", 100)
        for s in match_strings:
            if s in trackname:
                if "LH" in trackname or "RH" in trackname or "Melee" in trackname:
                    tracks.append(track)
                    tracknames.append(trackname)
    return tracks, tracknames


def is_track_empty(track):
    retval, take, note_count, cc_count, text_count = RPR_MIDI_CountEvts(RPR_GetMediaItemTake(RPR_GetTrackMediaItem(track, 0), 0), 0, 0, 0)
    if note_count == 0:
        return True
    else:
        return False


def is_tempo_empty():
    if RPR_CountTempoTimeSigMarkers(0) != 0:
        return False
    else:
        return True


def wipe_track2(track):
    retval, take, note_count, cc_count, text_count = RPR_MIDI_CountEvts(
        RPR_GetMediaItemTake(RPR_GetTrackMediaItem(track, 0), 0), 0, 0, 0)
    for i in range(note_count):
        RPR_MIDI_DeleteNote(take, i)
    for i in range(cc_count):
        msg(RPR_MIDI_GetCC(take, i, 0, 0, 0, 0, 0, 0, 0))
    for i in range(text_count):
        RPR_MIDI_DeleteTextSysexEvt(take, i)


def wipe_track(track):
    retval = RPR_DeleteTrackMediaItem(track, RPR_GetTrackMediaItem(track, 0))
    project_length = RPR_GetProjectLength(0)
    media_item = RPR_CreateNewMIDIItemInProj(track, 0.0, project_length, False)
    RPR_UpdateTimeline()


def wipe_tempo_map():
    for i in range(RPR_CountTempoTimeSigMarkers(0)):
        RPR_DeleteTempoTimeSigMarker(0, i)


def load_cues(filename):
    with open(filename) as f:
        return json.load(f)


class mainApp(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.master = master

        self.proceed = False

        self.difficulties = ["Expert", "Hard", "Normal", "Easy", "Community"]

        self.label = Label(self.master, text="Difficulty :")
        self.label.grid(row=0, column=0)

        self.difficulty_var = StringVar()
        self.difficulty_var.set(self.difficulties[0])
        self.difficulty_dropdown = OptionMenu(self.master, self.difficulty_var, *self.difficulties)
        self.difficulty_dropdown.grid(row=0, column=1)

        self.start_button = Button(self.master, text="Import cues", command=self.import_cues)
        self.start_button.grid(row=2, columnspan=2)

    def import_cues(self):

        def do_work(tracks):
            initial_dir = os.path.dirname(get_curr_project_filename())
            cues_file = filedialog.askopenfilename(initialdir=initial_dir, title="Select cues file",
                                                   filetypes=(("cues files", "*.cues"), ("all files", "*.*")))
            cues = load_cues(cues_file)
            for cue in cues["cues"]:
                tick = cue["tick"]
                tickLength = cue["tickLength"]
                pitch = cue["pitch"]
                velocity = cue["velocity"]
                x = cue["gridOffset"]["x"]
                y = cue["gridOffset"]["y"]
                z = 0
                if "zOffset" in cue:
                    z = cue["zOffset"]
                handType = cue["handType"]
                behavior = cue["behavior"]

                channel = 0
                cc16 = x
                cc17 = y
                cc18 = z
                cc19 = 0
                cc20 = 0
                cc21 = 0

                if behavior == 2:
                    channel = 1
                elif behavior == 1:
                    channel = 2
                elif behavior == 4:
                    channel = 3
                elif behavior == 5:
                    channel = 4

                while cc16 > 1:
                    cc16 -= 1
                    cc19 += 1
                while cc17 > 1:
                    cc17 -= 1
                    cc20 += 1
                while cc18 > 1:
                    cc18 -= 1
                    cc21 += 1
                while cc16 < -1:
                    cc16 += 1
                    cc19 -= 1
                while cc17 < -1:
                    cc17 += 1
                    cc20 -= 1
                while cc18 < -1:
                    cc18 += 1
                    cc21 -= 1

                track = None

                for i in range(len(tracks[0])):
                    if handType == 0:
                        if "Melee" in tracks[1][i]:
                            track = tracks[0][i]
                    elif handType == 1:
                        if "RH" in tracks[1][i]:
                            track = tracks[0][i]
                    elif handType == 2:
                        if "LH" in tracks[1][i]:
                            track = tracks[0][i]

                take = RPR_GetMediaItemTake(RPR_GetTrackMediaItem(track, 0), 0)

                RPR_MIDI_InsertNote(take, False, False, tick, tick + tickLength, channel, pitch, velocity, False)

                if cc16 != 0:
                    RPR_MIDI_InsertCC(take, False, False, tick, 176, 0, 16, int(cc16 * 64 + 64))
                if cc17 != 0:
                    RPR_MIDI_InsertCC(take, False, False, tick, 176, 0, 17, int(cc17 * 64 + 64))
                if cc18 != 0:
                    RPR_MIDI_InsertCC(take, False, False, tick, 176, 0, 18, int(cc18 * 64 + 64))
                if cc19 != 0:
                    RPR_MIDI_InsertCC(take, False, False, tick, 176, 0, 19, int(cc19 + 64))
                if cc20 != 0:
                    RPR_MIDI_InsertCC(take, False, False, tick, 176, 0, 20, int(cc20 + 64))
                if cc21 != 0:
                    RPR_MIDI_InsertCC(take, False, False, tick, 176, 0, 21, int(cc21 + 64))

                if behavior == 2:
                    RPR_MIDI_InsertTextSysexEvt(take, False, False, tick, 1, "h", 1)
                elif behavior == 1:
                    RPR_MIDI_InsertTextSysexEvt(take, False, False, tick, 1, "v", 1)
                elif behavior == 4:
                    RPR_MIDI_InsertTextSysexEvt(take, False, False, tick, 1, "C", 1)
                elif behavior == 5:
                    RPR_MIDI_InsertTextSysexEvt(take, False, False, tick, 1, "c", 1)

            for i in range(len(cues["tempos"])):
                RPR_AddTempoTimeSigMarker(0, RPR_MIDI_GetProjTimeFromPPQPos(take, cues["tempos"][i]["tick"]),
                                          cues["tempos"][i]["tempo"], 0, 0, 0)

            for i in range(len(tracks[0])):
                trackname = tracks[1][i]
                take = RPR_GetMediaItemTake(RPR_GetTrackMediaItem(tracks[0][i], 0), 0)
                RPR_MIDI_InsertTextSysexEvt(take, False, False, 0, 3, trackname, len(trackname))

            for repeater in cues["repeaters"]:

                tick = repeater["tick"]
                tickLength = repeater["tickLength"]
                pitch = repeater["pitch"]
                velocity = repeater["velocity"]
                handType = repeater["handType"]

                track = None

                for i in range(len(tracks[0])):
                    if handType == 0:
                        if "Melee" in tracks[1][i]:
                            track = tracks[0][i]
                    elif handType == 1:
                        if "RH" in tracks[1][i]:
                            track = tracks[0][i]
                    elif handType == 2:
                        if "LH" in tracks[1][i]:
                            track = tracks[0][i]

                take = RPR_GetMediaItemTake(RPR_GetTrackMediaItem(track, 0), 0)

                RPR_MIDI_InsertNote(take, False, False, tick, tick + tickLength, 0, pitch, velocity, False)

        tracks = get_tracks_matching_names([self.difficulty_var.get()])
        found = False
        for track in tracks[0]:
            if not is_track_empty(track):
                found = True
                self.warning_popup()
                break
        if self.proceed:
            for track in tracks[0]:
                wipe_track(track)
            self.proceed = False
            if not is_tempo_empty():
                found = True
                self.warning_popup(mode=1)
                if self.proceed:
                    wipe_tempo_map()
                    self.proceed = False
                    do_work(tracks)
            else:
                do_work(tracks)
        if found == False:
            do_work(tracks)

    def continue_handle(self, button):
        if button["text"] == "Continue":
            self.proceed = True
        elif button["text"] == "Cancel":
            self.proceed = False
        self.warning.destroy()

    def warning_popup(self, mode=0):

        self.warning = Toplevel()
        if mode == 0:
            self.warning_label = Label(self.warning, text="Found notes in the selected track. If you continue they will be wiped.")
        elif mode == 1:
            self.warning_label = Label(self.warning, text="Found a tempo/time sig marker. All markers will be wiped.")

        self.warning_label.grid(row=0, columnspan=20)

        self.warning_continue_button = Button(self.warning, text="Continue")
        self.warning_continue_button.grid(row=1, column=9)

        self.warning_cancel_button = Button(self.warning, text="Cancel")
        self.warning_cancel_button.grid(row=1, column=10)

        add_callback(self.warning_continue_button, self.continue_handle)
        add_callback(self.warning_cancel_button, self.continue_handle)

        self.warning.wait_window()


"""
Loop setup
"""

root = Tk()
root.title("Cues Import")

app = mainApp(root)

root.mainloop()

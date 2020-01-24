import sys
sys.argv = ["Main"]

from reaper_python import *
from collections import OrderedDict
from tkinter import Tk, Frame, Label, OptionMenu, StringVar, Button

import time
import json
import os


ticks_per_quarter = 480


class cues:

    def __init__(self):
        self.cues = []
        self.repeaters = []
        self.tempos = []
        self.targetSpeed = 1.0

    def add_cue(self, tick=0, tickLength=120, pitch=0, velocity=20, xOffset=0.0, yOffset=0.0, zOffset=0.0, handType=0,
                behavior=0):
        cue = {"tick": tick,
               "tickLength": tickLength,
               "pitch": pitch,
               "velocity": velocity,
               "gridOffset": {"x": xOffset, "y": yOffset},
               "zOffset": zOffset,
               "handType": handType,
               "behavior": behavior}

        self.cues.append(cue)

    def add_repeater(self, tick=0, tickLength=120, pitch=0, velocity=20, handType=0):
        repeater = {"handType": handType,
                    "tick": tick,
                    "tickLength": tickLength,
                    "pitch": pitch,
                    "velocity": velocity}

        self.repeaters.append(repeater)

    def add_tempo(self, tick=0, tempo=0):
        t = {"tempo": tempo,
             "tick": tick}

        self.tempos.append(t)

    def save(self, file):
        sort = ['tick', 'tickLength', 'pitch', 'velocity', 'gridOffset', 'zOffset', 'handType', 'behavior']
        cuesSorted = [OrderedDict(sorted(item.items(), key=lambda item: sort.index(item[0]))) for item in self.cues]
        data = {"cues": sorted(cuesSorted, key=lambda x: x['tick']),
                "repeaters": self.repeaters,
                "tempos": self.tempos,
                "targetSpeed": self.targetSpeed}
        with open(file, "w") as f:
            json.dump(data, f, indent=4)


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


def seconds_to_ticks(seconds, difficulty):
    ticks = 0
    tracks = get_tracks_matching_names([difficulty])
    temp_ticks = RPR_MIDI_GetPPQPosFromProjTime(RPR_GetMediaItemTake(RPR_GetTrackMediaItem(tracks[0][0], 0), 0), seconds)
    if temp_ticks != -1:
        ticks = temp_ticks
    return ticks


def is_sustain(tick, end_tick):
    return end_tick - tick > ticks_per_quarter


def is_melee(pitch):
    return 98 <= pitch <= 101


def is_chain_node(channel):
    return channel == 4


def is_chain(channel):
    return channel == 3


def is_horizontal(channel):
    return channel == 1


def is_vertical(channel):
    return channel == 2


"""
MIDI events will be returned in 3 lists. 0 = Left hand, 1 = Right hand and 2 = Melees
Every event in each list has this data:
0-  Pitch
1-  Velocity
2-  Tick
3-  TickLength
4-  Channel
5-  CC16 Value
6-  CC17 Value
7-  CC18 Value
8-  CC19 Value
9-  CC20 Value
10- CC21 Value
"""


def get_midi_events(tracks):
    lh_events = []
    rh_events = []
    melee_events = []
    for track in tracks:
        retval, take, note_count, cc_count, text_count = RPR_MIDI_CountEvts(RPR_GetMediaItemTake(RPR_GetTrackMediaItem(track, 0), 0), 0, 0, 0)
        retval4, _, trackname, buffer_size = RPR_GetTrackName(track, "", 100)
        for i in range(note_count):
            retval2, _, note_index, note_selected, note_muted, note_start_tick, note_end_tick, note_channel, pitch, velocity = RPR_MIDI_GetNote(take, i, 0, 0, 0, 0, 0, 0, 0)
            cc16 = -1
            cc17 = -1
            cc18 = -1
            cc19 = -1
            cc20 = -1
            cc21 = -1
            for j in range(cc_count):
                reval3, _, cc_index, cc_selected, cc_muted, cc_tick, cc_channel_message, cc_channel, cc_number, cc_value = RPR_MIDI_GetCC(take, j, 0, 0, 0, 0, 0, 0, 0)
                if cc_tick == note_start_tick:
                    if cc_number == 16:
                        cc16 = cc_value
                    elif cc_number == 17:
                        cc17 = cc_value
                    elif cc_number == 18:
                        cc18 = cc_value
                    elif cc_number == 19:
                        cc19 = cc_value
                    elif cc_number == 20:
                        cc20 = cc_value
                    elif cc_number == 21:
                        cc21 = cc_value
            if "LH" in trackname:
                lh_events.append([pitch, velocity, int(note_start_tick), int(note_end_tick - note_start_tick), note_channel, cc16, cc17, cc18, cc19, cc20, cc21])
            elif "RH" in trackname:
                rh_events.append([pitch, velocity, int(note_start_tick), int(note_end_tick - note_start_tick), note_channel, cc16, cc17, cc18, cc19, cc20, cc21])
            elif "Melee" in trackname:
                melee_events.append([pitch, velocity, int(note_start_tick), int(note_end_tick - note_start_tick), note_channel, cc16, cc17, cc18, cc19, cc20, cc21])
    return lh_events, rh_events, melee_events


def get_tempo_data(difficulty):
    tempo_count = RPR_CountTempoTimeSigMarkers(0)
    tempos = []
    for i in range(tempo_count):
        retval, proj, index, time_pos, measure_pos, beat_pos, bpm, timesig_num, timesig_denom, tempo_bool = RPR_GetTempoTimeSigMarker(0, i, 0, 0, 0, 0, 0, 0, 0)
        tempos.append([bpm, seconds_to_ticks(time_pos, difficulty)])
    return tempos


#start = time.time()

#data = get_midi_events(get_tracks_matching_names(["Expert"])[0])

#end = time.time()

#msg("Finished! The process took " + str(end - start) + " seconds.")
#msg(data[0][0])


class mainApp(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.master = master

        self.difficulties = ["Expert", "Hard", "Normal", "Easy", "Community"]

        self.label = Label(self.master, text="Difficulty :")
        self.label.grid(row=0, column=0)

        self.difficulty_var = StringVar()
        self.difficulty_var.set(self.difficulties[0])
        self.difficulty_dropdown = OptionMenu(self.master, self.difficulty_var, *self.difficulties)
        self.difficulty_dropdown.grid(row=0, column=1)

        self.start_button = Button(self.master, text="Convert to cues", command=self.convert)
        self.start_button.grid(row=1, columnspan=2)

    def convert(self):
        difficulty = self.difficulty_var.get()
        cues_filename = get_curr_project_filename().replace(".rpp", "_" + difficulty + ".cues")
        note_data = get_midi_events(get_tracks_matching_names([difficulty])[0])
        tempo_data = get_tempo_data(difficulty)
        cues_data = cues()
        count = 0
        for data in tempo_data:
            cues_data.add_tempo(tick=data[1], tempo=data[0])
        for data in note_data:
            hand = 0
            if count == 0:
                hand = 2
            elif count == 1:
                hand = 1
            for d in data:
                tick = d[2]
                tickLength = d[3]
                pitch = d[0]
                velocity = d[1]
                behavior = 0
                x = 0
                y = 0
                z = 0
                if is_chain(d[4]):
                    behavior = 4
                elif is_chain_node(d[4]):
                    behavior = 5
                elif is_horizontal(d[4]):
                    behavior = 2
                elif is_melee(pitch):
                    behavior = 6
                elif is_sustain(tick, tick + tickLength):
                    behavior = 3
                elif is_vertical(d[4]):
                    behavior = 1
                if d[5] != -1:
                    x = (d[5] - 64) / 64.0
                if d[6] != -1:
                    y = (d[6] - 64) / 64.0
                if d[7] != -1:
                    z = (d[7] - 64) / 64.0
                if d[8] != -1:
                    x = d[8] - 64
                if d[9] != -1:
                    y = d[9] - 64
                if d[10] != -1:
                    z = d[10] - 64
                if pitch < 107:
                    cues_data.add_cue(tick=tick, tickLength=tickLength,pitch=pitch, velocity=velocity, xOffset=x, yOffset=y, zOffset=z, handType=hand, behavior=behavior)
                else:
                    cues_data.add_repeater(tick=tick, tickLength=tickLength, pitch=pitch, velocity=velocity, handType=hand)
            count = count + 1
        cues_data.save(cues_filename)

"""
Loop setup
"""

root = Tk()
root.title("Cues export")

app = mainApp(root)

root.mainloop()
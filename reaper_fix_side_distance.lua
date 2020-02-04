rows = 7
cols = 12
function run()
	local modifiedNotes = false
	for i=0, reaper.CountTracks(0)-1 do
		local track = reaper.GetTrack(0, i)
		for i=0, reaper.CountTrackMediaItems(track)-1 do
			local mediaItem = reaper.GetTrackMediaItem(track, i)
			for j=0, reaper.CountTakes(mediaItem)-1 do
				local take = reaper.GetTake(mediaItem, j)
				local retval, notecnt, ccevtcnt, textsysevntcnt = reaper.MIDI_CountEvts(take)
				for k=0, notecnt-1 do
					local retval, selected, muted, startppqpos, endppqpos, chan, pitch, vel = reaper.MIDI_GetNote(take, k)
					if pitch < 84 then
						location = pitch
						cc16 = 64
						cc19 = 64
						while location > 11 do location = location - 12 end
						for l=0, ccevtcnt-1 do
							local retv, sel, m, ppqpos, chanmsg, c, msg2, msg3 = reaper.MIDI_GetCC(take, l)
							if ppqpos == startppqpos then
								if msg2 == 16 then
									cc16 = msg3
								elseif msg2 == 19 then
									cc19 = msg3
								end
							end
						end
						x_offset = ((cc16-64)/64.0) + (cc19-64)
						x_location = (location-5.5) + x_offset
						z_offset = math.abs((math.abs(x_location)) / 9)
						small_offset = math.floor(z_offset*64+64)
						if small_offset ~= 0 then
							reaper.MIDI_InsertCC(take, selected, muted, startppqpos, 176, 0, 18, small_offset)
							modifiedNotes = true
						end
					end
				end
				reaper.MIDI_Sort(take)
			end
		end
	end
	if modifiedNotes == true then
		reaper.Undo_OnStateChange("Fix Side Distance")
	end
end

function math.clamp(val, min, max)
    if min - val > 0 then return min end
    if max - val < 0 then return max end
    return val
end

run()
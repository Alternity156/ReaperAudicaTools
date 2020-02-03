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
					cc18 = 64
					cc21 = 64
					new_pitch = pitch
					if selected == true then
						for l=0, ccevtcnt-1 do
							local retv, sel, m, ppqpos, chanmsg, c, msg2, msg3 = reaper.MIDI_GetCC(take, l)
							if ppqpos == startppqpos then
								if msg2 == 18 then
									cc18 = msg3
									reaper.MIDI_DeleteCC(take, l)
								elseif msg2 == 21 then
									cc21 = msg3
									reaper.MIDI_DeleteCC(take, l)
								end
							end
						end
						if cc18 == 127 then
							cc18 = 64
							cc21 = cc21 + 1
						else
							cc18 = cc18 + 1
						end
						reaper.MIDI_SetNote(take, k, selected, muted, startppqpos, endppqpos, chan, new_pitch, vel, true)
						if cc18 ~= 64 then
							reaper.MIDI_InsertCC(take, selected, muted, startppqpos, 176, 0, 18, cc18)
						end
						if cc21 ~= 64 then
							reaper.MIDI_InsertCC(take, selected, muted, startppqpos, 176, 0, 21, cc21)
						end
						modifiedNotes = true
					end
				end
				reaper.MIDI_Sort(take)
			end
		end
	end
	if modifiedNotes == true then
		reaper.Undo_OnStateChange("Move Targets Up")
	end
end

run()
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
					cc17 = 64
					cc20 = 64
					new_pitch = pitch
					if selected == true then
						for l=0, ccevtcnt-1 do
							local retv, sel, m, ppqpos, chanmsg, c, msg2, msg3 = reaper.MIDI_GetCC(take, l)
							if ppqpos == startppqpos then
								if msg2 == 17 then
									cc17 = msg3
									reaper.MIDI_DeleteCC(take, l)
								elseif msg2 == 20 then
									cc20 = msg3
									reaper.MIDI_DeleteCC(take, l)
								end
							end
						end
						if cc17 == 127 then
							if new_pitch > 71 then
								cc20 = cc20 + 1
								cc17 = 64
							else
								cc17 = 64
								new_pitch = new_pitch + 12
							end
						else
							cc17 = cc17 + 1
						end
						reaper.MIDI_SetNote(take, k, selected, muted, startppqpos, endppqpos, chan, new_pitch, vel, true)
						if cc17 ~= 64 then
							reaper.MIDI_InsertCC(take, selected, muted, startppqpos, 176, 0, 17, cc17)
						end
						if cc20 ~= 64 then
							reaper.MIDI_InsertCC(take, selected, muted, startppqpos, 176, 0, 20, cc20)
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
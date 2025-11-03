window_w = 970
window_h = 500
menu_bar_h = 80
menu_bar_y = window_h - menu_bar_h
rows = 7
cols = 12
xpos = 40
ypos = 40
xspacing = 80
yspacing = 56
radiusMax = 95
radiusMin = 20
ticksPerQuarter = 480
meleeOffsetScale = 8

difficulty = {x=10, y=menu_bar_y, buttonWidth=80, buttonHeight=13, xStep=0, yStep=15, options={"Easy", "Normal", "Hard", "Expert"}, selected="Expert", label="Difficulty"}
displayStyle = {x=120, y=menu_bar_y, buttonWidth=100, buttonHeight=13, xStep=0, yStep=15, options={"Full", "Standard", "Minimal"}, selected="Standard", label="Display Style"}
targetSpeed = {x=250, y=menu_bar_y, buttonWidth=100, buttonHeight=13, xStep=0, yStep=15, options={"Slow", "Medium", "Fast", "Very Fast"}, selected="Medium", label="Target Speed"}
gridviewerMode = {x=380, y=menu_bar_y, buttonWidth=100, buttonHeight=13, xStep=0, yStep=15, options={"Playback", "Place Target", "Place Melee"}, selected="Playback", label="Mode"}
placementMode = {x=510, y=menu_bar_y, buttonWidth=100, buttonHeight=13, xStep=0, yStep=15, options={"Grid Snap", "Free"}, selected="Grid Snap", label="Placement"}
velocity = {x=640, y=menu_bar_y, buttonWidth=80, buttonHeight=13, xStep=0, yStep=15, options={"Kick", "Snare", "Perc."}, selected="Kick", label="Velocity"}

old_mouse_cap = 0
has_window_focus = true

function init(window_w, window_h, window_x, window_y, docked)
   gfx.init("Audica Grid Viewer" , window_w, window_h, docked, window_x, window_y)  -- name,w,h,dockstate,xpos,ypos
end

function Update()
   gfx.update()

   -- Ignore the first click when the window isn't in focus
   if gfx.getchar(65536) & 2 == 2 and not window_has_focus then
      old_mouse_cap = gfx.mouse_cap & (1 | 2 | 64)
   end
   window_has_focus = (gfx.getchar(65536) & 2 == 2)

   UpdateSelector(difficulty)
   UpdateSelector(displayStyle)
   UpdateSelector(targetSpeed)
   UpdateSelector(gridviewerMode)
   if gridviewerMode.selected ~= "Playback" then
      UpdateSelector(placementMode)
   end
   if gridviewerMode.selected == "Place Target" then
      UpdateSelector(velocity)
      UpdatePlaceTarget()
   elseif gridviewerMode.selected == "Place Melee" then
      UpdatePlaceMelee()
   end

   old_mouse_cap = gfx.mouse_cap & (1 | 2 | 64)

   local quitting = false

   local queuedChar = gfx.getchar()
   while not quitting and queuedChar ~= 0 do
      if queuedChar == 32 then
         -- Press <space> to play/stop
         reaper.Main_OnCommandEx(40044, 0, 0)
      elseif queuedChar == 26 then
         -- ctrl-z/ctrl-shift-z undo/redo
         if DetectModifier(8) then
            reaper.Main_OnCommandEx(40030, 0, 0)
         else
            reaper.Main_OnCommandEx(40029, 0, 0)
         end
      elseif queuedChar == 27 or queuedChar == -1 then
         -- Press <ESC> or close the window to quit the script
         quitting = true
      end
      
      queuedChar = gfx.getchar()
   end

   if not quitting then reaper.defer(run) else gfx.quit() end
end

-- DRAW IN GFX WINDOW
function run()
   local cursorTick = GetCursorTick()

   gfx.x,gfx.y = 0,0
   gfx.printf("tick: %d", cursorTick)

   local tracks,tracknames = GetTracksMatchingNames({difficulty.selected, "Community"})
   local targets = {}
   local ccs = {}
   local trackColors = {}
   local overdriveSections = {}

   for trackIndex,track in ipairs(tracks) do
      local trackname = tracknames[trackIndex]
      trackColors[trackname] = GetTrackColor(track, trackname)
      for i=0,reaper.CountTrackMediaItems(track)-1 do
         local mediaItem = reaper.GetTrackMediaItem(track, i)
         local takeOffsetSeconds = reaper.GetMediaItemInfo_Value(mediaItem, "D_POSITION")
         local takeOffsetTicks = SecondsToTicks(takeOffsetSeconds)
         for j=0,reaper.CountTakes(mediaItem)-1 do
            local take = reaper.GetTake(mediaItem, j)
            local retval,notecnt,ccevtcnt,textsyxevntcnt = reaper.MIDI_CountEvts(take)
            for k=0,notecnt-1 do
               local retval, selected, muted, startppqpos, endppqpos, chan, pitch, vel  = reaper.MIDI_GetNote(take, k)
               local tick = startppqpos + takeOffsetTicks
               local endTick = endppqpos + takeOffsetTicks
               if cursorTick + ticksPerQuarter * 4 > tick and (cursorTick - ticksPerQuarter <= tick or cursorTick <= endTick) and pitch < 107 then
                  if pitch == 106 then
                     table.insert(overdriveSections, {["tick"]=tick, ["endTick"]=endTick})
                  else
                     local newTarget = {["pitch"]=pitch, ["tick"]=tick, ["endTick"]=endTick, ["track"]=trackname, ["channel"]=chan}
                     LinkSimultaneous(targets, newTarget)
                     LinkNext(targets, newTarget)
                     table.insert(targets, newTarget)
                  end
               end
            end
            for k=0,ccevtcnt-1 do
               local retval, selected, muted, ppqpos, chanmsg, chan, msg2, msg3 = reaper.MIDI_GetCC(take, k)
               local tick = ppqpos + takeOffsetTicks
               table.insert(ccs, {["cc"]=msg2, ["val"]=msg3, ["tick"]=tick, ["track"]=trackname})
            end
         end
      end
   end

   local gridAlpha = 1.0
   if gridviewerMode.selected == "Place Melee" then
      gridAlpha = 0.4
   end

   for i=0,rows*cols-1 do
      local centerX,centerY = GetPosForPitch(i, 0, 0)

      setcolor(1, 1, 1, gridAlpha)
      if (i % cols >= 3 and i % cols <= 8 and i / cols >= 1 and i / cols <= 6) then
         DrawShape("circle", centerX, centerY, radiusMin, false)
      end

      gfx.x = centerX-3
      if i >= 10 then
         gfx.x = gfx.x - 4
      end
      gfx.y = centerY - 3
      setcolor(1, 1, 1, gridAlpha * 0.5)
      gfx.printf("%d", i)
   end

   gridAlpha = 1.0
   if gridviewerMode.selected == "Place Target" then
      gridAlpha = 0.4
   end

   for i=98,101 do
      local centerX,centerY = GetPosForPitch(i, 0, 0)

      setcolor(1, 1, 1, gridAlpha)
      DrawShape("octagon", centerX, centerY, radiusMin, false)

      gfx.x = centerX-3
      if i >= 10 then
         gfx.x = gfx.x - 4
      end
      if i >= 100 then
         gfx.x = gfx.x - 4
      end
      gfx.y = centerY - 3
      setcolor(1, 1, 1, gridAlpha * 0.5)
      gfx.printf("%d", i);
   end

   for key,value in pairs(targets) do
      local channel = value["channel"]
      local shape = "circle"
      local isSustain = IsSustain(value["tick"], value["endTick"]) and not IsMelee(value["pitch"])
      local scale = 1

      if IsMelee(value["pitch"]) then
         shape = "octagon"
      elseif isSustain or IsChain(channel) then
         shape = "diamond"
      end

      if IsChainNode(channel) then
         scale = .5
      end

      local centerX,centerY = GetPosForPitch(value["pitch"], FindCCOffset(value, ccs))

      local r,g,b = reaper.ColorFromNative(trackColors[value["track"]])
      setcolor(r/255, g/255, b/255, 1)

	  local targetSpeedMap = {["Slow"]=4, ["Medium"]=3, ["Fast"]=2, ["Very Fast"]=1}
	  local targetSpeed = targetSpeedMap[targetSpeed.selected]

      local t = math.min(1, 1 - (value["tick"] - cursorTick) / (ticksPerQuarter * targetSpeed))

      if displayStyle.selected == "Full" then
         local hazeLerp = (t - 0.5) * 2
         if hazeLerp > 0 then
            local haze = math.max(0, math.sin(hazeLerp * math.pi * 2 * .75))
            if haze > 0 then
               gfx.a = lerp(0, 0.3, haze)
               DrawShape(shape, centerX, centerY, lerp(radiusMin,radiusMax,.5) * scale, true)
            end
         end
      end

      if t > .75 and value["simultaneous"] ~= nil then
         local otherCenterX, otherCenterY = GetPosForPitch(value["simultaneous"]["pitch"], FindCCOffset(value["simultaneous"], ccs))
         local a = 1.0
         if not isSustain then
            a = (value["tick"] - cursorTick) / ticksPerQuarter
            if a < 0 then a = -a * 2.0 end
            a = math.max(0, 0.6 * math.min(1.0, 1.0 - a))
         end
         local r,g,b = gfx.r, gfx.g, gfx.b
         setcolor(1,1,1,0.6 * a)
         DrawLine(centerX, centerY, otherCenterX, otherCenterY, 3)
         gfx.r,gfx.g,gfx.b = r,g,b
      end

      if value["next"] ~= nil then
         local otherCenterX, otherCenterY = GetPosForPitch(value["next"]["pitch"], FindCCOffset(value["next"], ccs))
         if IsChain(value["channel"]) and IsChainNode(value["next"]["channel"]) then
            local t = (value["tick"] - cursorTick) / (ticksPerQuarter * 2)
            if t < 0 then t = -2.0 * t end
            t = 1.0 - t
            if t > 0 then
               gfx.a = t * 0.5
               DrawLine(centerX, centerY, otherCenterX, otherCenterY, 2.5)
               gfx.a = t * 0.8
               DrawLine(centerX, centerY, otherCenterX, otherCenterY, 1.8)
            end
         else
            local travel = ((value["next"]["tick"] - cursorTick) / ticksPerQuarter)
            if travel > 0.0 and travel < 1.0 then
               travel = travel ^ 1.5
               gfx.a = 0.2
               for advance=5,1,-1 do
                  local gradient = (advance / 5.0) * travel
                  DrawLine(otherCenterX, otherCenterY, lerp(otherCenterX, centerX, gradient), lerp(otherCenterY, centerY, gradient), 2)
               end
            end
         end
      end

      gfx.a = 1
      local circleShrink = (t - .75) * 4
      local cutoffTick = math.min(value["endTick"], value["tick"] + (ticksPerQuarter / 4))
      if circleShrink >= 0 and (cutoffTick > cursorTick or isSustain) then
         if displayStyle.selected ~= "Minimal" and t < 1 then
            DrawShape(shape, centerX, centerY, lerp(radiusMax, radiusMin, circleShrink) * scale, false)
         end
         local r,g,b = gfx.r, gfx.g, gfx.b
         if IsOverdrive(value["tick"], overdriveSections) then setcolor(1,1,1,1) end

         if isSustain or IsChain(channel) or IsMelee(value["pitch"]) then
            DrawShape(shape, centerX, centerY, 11 * scale, true)
         elseif channel == 1 then gfx.rect(centerX-11,centerY-1,25,6,true)
         elseif channel == 2 then gfx.rect(centerX-2,centerY-11,6,25,true)
         else gfx.rect(centerX-7,centerY-7,16,15,true) end
         gfx.r,gfx.g,gfx.b = r,g,b
      end

      if t == 1 then
         local a = 1.0
         if not isSustain then
             a = 1.0 - ((cursorTick - value["tick"]) / (ticksPerQuarter / 2))
         end
         local r,g,b,m = gfx.r, gfx.g, gfx.b, gfx.mode
         setcolor(1, 1, 1, math.max(0.0, 0.6 * a))
         gfx.mode = 1
         DrawShape(shape, centerX, centerY, radiusMin * scale, true)
         gfx.r,gfx.g,gfx.b = r,g,b
         gfx.mode = m
      end
   end

   setcolor(0, 0, 0, 1)
   gfx.rect(0, menu_bar_y, window_w, menu_bar_h)

   DrawSelector(difficulty)
   DrawSelector(displayStyle)
   DrawSelector(targetSpeed)
   DrawSelector(gridviewerMode)
   if gridviewerMode.selected ~= "Playback" then
      DrawSelector(placementMode)
   end
   if gridviewerMode.selected == "Place Target" then
      DrawSelector(velocity)
   end

   Update()
end -- END DEFER

function setcolor(r,g,b,a)
   gfx.r = r
   gfx.g = g
   gfx.b = b
   gfx.a = a
end

function lerp(a, b, t)
   return (a * (1.0 - t)) + (b * t)
end

function DrawShape(type, x, y, radius, filled)
   if type == "circle" then
      gfx.circle(x, y, radius, filled, true)
   else
      x,y = math.floor(x) + 0.5,math.floor(y) + 0.5
      if type == "diamond" then
         DrawPolygon(filled, x - radius, y, x, y - radius, x + radius, y, x, y + radius)
      elseif type == "octagon" then
         local halfEdgeLength = radius * math.sin(math.pi/8.0)
         DrawPolygon(filled,
                     x - radius, y - halfEdgeLength,
                     x - halfEdgeLength, y - radius,
                     x + halfEdgeLength, y - radius,
                     x + radius, y - halfEdgeLength,
                     x + radius, y + halfEdgeLength,
                     x + halfEdgeLength, y + radius,
                     x - halfEdgeLength, y + radius,
                     x - radius, y + halfEdgeLength)
      end
   end
end

function SecondsToTicks(seconds)
   local ticks = 0
   for i=0,reaper.CountMediaItems(0)-1 do
      ticks = reaper.MIDI_GetPPQPosFromProjTime(reaper.GetTake(reaper.GetMediaItem(0,i),0), seconds)
      if ticks ~= -1 then
         break
      end
   end
   return ticks
end

function GetCursorTick()
   local cursorTime = reaper.GetCursorPosition()
   if reaper.GetPlayState() == 1 then
      cursorTime = reaper.GetPlayPosition()
   end

   return SecondsToTicks(cursorTime)
end

function LinkSimultaneous(targets, newTarget)
   if not IsChainNode(newTarget["channel"]) then
      for key,value in pairs(targets) do
         if not IsChainNode(value["channel"]) then
            if newTarget["tick"] == value["tick"] and IsMelee(newTarget["pitch"]) == IsMelee(value["pitch"]) then
               value["simultaneous"] = newTarget
               break
            end
         end
      end
   end
end

function LinkNext(targets, newTarget)
   if not IsMelee(newTarget["pitch"]) then
      for key,value in pairs(targets) do
         if newTarget["track"] == value["track"] and newTarget["tick"] > value["tick"] and value["next"] == nil then
            value["next"] = newTarget
         end
      end
   end
end

function IsSustain(tick, endTick)
   return endTick - tick > (ticksPerQuarter / 2)
end

function IsMelee(pitch)
   return pitch >= 98 and pitch <= 101
end

function IsChain(channel)
   return channel == 3 or IsChainNode(channel)
end

function IsChainNode(channel)
   return channel == 4
end

function IsOverdrive(ticks, overdriveSections)
   for key,value in pairs(overdriveSections) do
      if ticks >= value["tick"] and ticks <= value["endTick"] then
         return true
      end
   end
   return false
end

function DrawPolygon(filled, ...)
   local pointList = {...}
   if #pointList >= 6 then
      if filled then
         gfx.triangle(table.unpack(pointList))
      else
         for p = 1,#pointList-2,2 do
            gfx.line(pointList[p], pointList[p+1], pointList[p+2], pointList[p+3])
         end
         gfx.line(pointList[#pointList-1], pointList[#pointList], pointList[1], pointList[2])
      end
   end
end

function DrawLine(x1,y1,x2,y2,thickness)
   local L = math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

   gfx.triangle(x1 + (thickness - 1) * (y2-y1) / L, y1 + (thickness - 1) * (x1-x2) / L,
                x2 + (thickness - 1) * (y2-y1) / L, y2 + (thickness - 1) * (x1-x2) / L,
                x1 - (thickness - 1) * (y2-y1) / L, y1 - (thickness - 1) * (x1-x2) / L,
                x2 - (thickness - 1) * (y2-y1) / L, y2 - (thickness - 1) * (x1-x2) / L)
end

function GetTracksMatchingNames(matchStrings)
   local tracks,tracknames = {},{}
   for i=0,reaper.CountTracks(0)-1 do
      local track = reaper.GetTrack(0, i)
      local trackname = ""
      local _,trackname = reaper.GetTrackName(track, trackname)
      for _,matchString in ipairs(matchStrings) do
         if string.find(trackname, matchString) then
            table.insert(tracks, track)
            table.insert(tracknames, trackname)
            break
         end
      end
   end
   return tracks,tracknames
end

function GetTrackColor(track, trackname)
   local color = reaper.GetTrackColor(track)
   if color ~= 0 then
       color = color & ~0x01000000
   else
       local r,g,b
       if string.find(trackname, "RH") then r,g,b = 255,119,0
       elseif string.find(trackname, "LH") then r,g,b = 0,170,255
       elseif string.find(trackname, "both") then r,g,b = 255,0,255
       else r,g,b = 160,160,160 end
  
       color = reaper.ColorToNative(r, g, b)
   end
   return color
end

function GetPosForPitch(pitch, offsetX, offsetY)
   if IsMelee(pitch) then
      local col = pitch % 2
      local row = 1 - math.floor((pitch - 98) / 2)
      local centerX = 4*xspacing+col*4*xspacing + offsetX * xspacing * meleeOffsetScale
      local centerY = 3*yspacing+row*yspacing - offsetY * yspacing * meleeOffsetScale + 7
      return centerX, centerY
   end
   local col = pitch % cols + offsetX
   local row = rows - math.floor(pitch / cols) - 1 - offsetY

   local centerX = xpos+col*xspacing
   local centerY = ypos+row*yspacing
   return centerX, centerY
end

function FindCCOffset(value, ccs)
   local ccX = 0
   local ccY = 0
   for keyCC,valueCC in pairs(ccs) do
      if valueCC["track"] == value["track"] and math.abs(valueCC["tick"] - value["tick"]) <= 10 then
         if valueCC["cc"] == 16 then
            ccX = ccX + (valueCC["val"] - 64) / 64.0
         end
         if valueCC["cc"] == 17 then
            ccY = ccY + (valueCC["val"] - 64) / 64.0
         end
         if valueCC["cc"] == 19 then
            ccX = ccX + (valueCC["val"] - 64)
         end
         if valueCC["cc"] == 20 then
            ccY = ccY + (valueCC["val"] - 64)
         end
      end
   end
   return ccX, ccY
end

function GatherPlaceInputs()
   local track,tracktype,click_x,click_y = nil,nil,gfx.mouse_x,gfx.mouse_y

   if IsPointInButton(click_x, click_y, {x=0, y=0, w=window_w, h=menu_bar_y}) then
      if DetectClick(1) then
         tracktype = "LH"
      elseif DetectClick(2) then
         tracktype = "RH"
      elseif DetectClick(64) then
         tracktype = "Melee"
      end
      
      if tracktype ~= nil then
         local tracks,tracknames = GetTracksMatchingNames({difficulty.selected, "Community"})
         for i,trackname in ipairs(tracknames) do
            if string.find(trackname, tracktype) then
               track = tracks[i]
               break
            end
         end
      end
   end

   return track,tracktype,click_x,click_y,GetCursorTick()
end

function UpdatePlaceTarget()
   local track,tracktype,click_x,click_y,cursorTick = GatherPlaceInputs()

   if track ~= nil then
      local grid_x = math.floor(((click_x - xpos) / xspacing) + 0.5)
      local grid_y = math.floor(((click_y - ypos) / yspacing) + 0.5)
      local offset_x = click_x - ((grid_x * xspacing) + xpos)
      local offset_y = click_y - ((grid_y * yspacing) + ypos)
      local ccX = 64.0 + (64.0 * offset_x / xspacing)
      local ccY = 64.0 + (64.0 * -offset_y / yspacing)
      local newpitch = grid_x + (cols * ((rows-1) - grid_y))
      local channel = 0
      if DetectModifier(8) then
         channel = 1
      elseif DetectModifier(4) then
         channel = 2
      end
      local velocityMap = {["Kick"]=20, ["Snare"]=127, ["Perc."]=60}
      local velocity = velocityMap[velocity.selected]

      PlaceNote(track, tracktype, cursorTick, newpitch, channel, velocity, ccX, ccY)
   end
end

function UpdatePlaceMelee()
   local track,tracktype,click_x,click_y,cursorTick = GatherPlaceInputs()

   if track ~= nil then
      local newpitch = 98
      local channel = 0
      local velocity = 3

      if click_x >= window_w/2.0 then
         newpitch = newpitch + 1
      end
      if click_y < menu_bar_y/2.0 then
         newpitch = newpitch + 2
      end
      local base_x,base_y = GetPosForPitch(newpitch, 0, 0)
      local offset_x = click_x - base_x
      local offset_y = click_y - base_y
      local ccX = 64.0 + (64.0 * offset_x / (xspacing * meleeOffsetScale))
      local ccY = 64.0 + (64.0 * -offset_y / (yspacing * meleeOffsetScale))

      PlaceNote(track, tracktype, cursorTick, newpitch, channel, velocity, ccX, ccY)
   end
end

function PlaceNote(track, tracktype, cursorTick, newpitch, channel, velocity, ccX, ccY)
   local matched,moved,insertTake,insertTick = false,false
   for i=0,reaper.CountTrackMediaItems(track)-1 do
      local mediaItem = reaper.GetTrackMediaItem(track, i)
      local takeOffsetSeconds = reaper.GetMediaItemInfo_Value(mediaItem, "D_POSITION")
      local takeDurationSeconds = reaper.GetMediaItemInfo_Value(mediaItem, "D_LENGTH")
      local takeOffsetTicks = SecondsToTicks(takeOffsetSeconds)
      local takeEndOffsetTicks = takeOffsetTicks + SecondsToTicks(takeDurationSeconds)
      local newNoteStartTick = cursorTick - takeOffsetTicks
      if newNoteStartTick >= 0 and newNoteStartTick + 120 < takeEndOffsetTicks then
         for j=0,reaper.CountTakes(mediaItem)-1 do
            local take = reaper.GetTake(mediaItem, j)
            if insertTake == nil then
               insertTake,insertTick = take,newNoteStartTick
            end
            local _,notecnt,_,_ = reaper.MIDI_CountEvts(take)
            local k=0
            while k < notecnt do
               local _,_,_,startppqpos,endppqpos,_,pitch,_ = reaper.MIDI_GetNote(take, k)
               if startppqpos <= newNoteStartTick and endppqpos > newNoteStartTick and pitch < 106 then
                  if pitch == newpitch then
                     matched = true
                  elseif not matched then
                     insertTake,insertTick,moved = take,newNoteStartTick,true
                  end
                  DeleteNote(track, take, k, startppqpos + takeOffsetTicks)
                  notecnt = notecnt - 1
               else
                  k = k + 1
               end
            end
         end
      end
   end
   
   if matched then
      reaper.Undo_OnStateChange("reaper_gridviewer: Delete " .. tracktype  .. " note")
   elseif insertTake ~= nil then
      reaper.MIDI_InsertNote(insertTake, false, false, insertTick, insertTick + 120, channel, newpitch, velocity)
      if placementMode.selected == "Free" then
         ccX = math.max(0, math.min(127, math.floor(ccX + 0.5)))
         ccY = math.max(0, math.min(127, math.floor(ccY + 0.5)))
         reaper.MIDI_InsertCC(insertTake, false, false, insertTick, 0xb0, channel, 16, ccX)
         reaper.MIDI_InsertCC(insertTake, false, false, insertTick, 0xb0, channel, 17, ccY)
      end
      if moved then
         reaper.Undo_OnStateChange("reaper_gridviewer: Moved " .. tracktype  .. " note")
      else
         reaper.Undo_OnStateChange("reaper_gridviewer: Insert " .. tracktype  .. " note")
      end
   end
end

function DeleteNote(track, noteTake, noteIndex, noteStartTick)
   reaper.MIDI_DeleteNote(noteTake, noteIndex)

   for i=0,reaper.CountTrackMediaItems(track)-1 do
      local mediaItem = reaper.GetTrackMediaItem(track, i)
      local takeOffsetSeconds = reaper.GetMediaItemInfo_Value(mediaItem, "D_POSITION")
      local takeOffsetTicks = SecondsToTicks(takeOffsetSeconds)
      for j=0,reaper.CountTakes(mediaItem)-1 do
         local take = reaper.GetTake(mediaItem, j)
         local _,_,ccevtcnt,txtevtcnt = reaper.MIDI_CountEvts(take)
         local k=0
         while k < ccevtcnt do
            local _,_,_,ppqpos,_,_,cc,_ = reaper.MIDI_GetCC(take, k)
            local tick = ppqpos + takeOffsetTicks
            if (cc == 16 or cc == 17 or cc == 18 or cc == 19 or cc == 20 or cc == 21) and math.abs(tick - noteStartTick) <= 10 then
               reaper.MIDI_DeleteCC(take, k)
               ccevtcnt = ccevtcnt - 1
            else
               k = k + 1
            end
         end
         k=0
         while k < txtevtcnt do
            local _,_,_,ppqpos,evttype,_ = reaper.MIDI_GetTextSysexEvt(take, k)
            local tick = ppqpos + takeOffsetTicks
            if evttype == 1 and math.abs(tick - noteStartTick) <= 10 then
               reaper.MIDI_DeleteTextSysexEvt(take, k)
               txtevtcnt = txtevtcnt - 1
            else
               k = k + 1
            end
         end
      end
   end
end

function UpdateSelector(selectorSpec)
   local button = {x=selectorSpec.x, y=selectorSpec.y+gfx.texth+2, w=selectorSpec.buttonWidth, h=selectorSpec.buttonHeight}
   if DetectClick(1) then
      for _,optionLabel in ipairs(selectorSpec.options) do
         if IsPointInButton(gfx.mouse_x, gfx.mouse_y, button) then selectorSpec.selected = optionLabel end
         button.x = button.x + selectorSpec.xStep
         button.y = button.y + selectorSpec.yStep
      end
   end
end

function DrawSelector(selectorSpec)
   if type(selectorSpec.label) == "string" then
      setcolor(1,1,1,1)
      gfx.x,gfx.y = selectorSpec.x, selectorSpec.y
      gfx.printf(selectorSpec.label or "")
   end
   
   local button = {x=selectorSpec.x, y=selectorSpec.y+gfx.texth+2, w=selectorSpec.buttonWidth, h=selectorSpec.buttonHeight}
   for _,optionLabel in ipairs(selectorSpec.options) do
      button.label = optionLabel
      button.isSelected = (optionLabel == selectorSpec.selected)
      DrawButton(button)
      button.x = button.x + selectorSpec.xStep
      button.y = button.y + selectorSpec.yStep
   end
end

function DrawButton(buttonSpec)
   if buttonSpec.isSelected then
      setcolor(1,1,1,1)
   else
      setcolor(0.3,0.3,0.3,1)
   end

   gfx.rect(buttonSpec.x,buttonSpec.y,buttonSpec.w,buttonSpec.h,false)
   setcolor(1,1,1,1)
   gfx.x,gfx.y = buttonSpec.x+2,buttonSpec.y+2
   gfx.printf(buttonSpec.label)
end

function IsPointInButton(x, y, buttonSpec)
   return x > buttonSpec.x and y > buttonSpec.y and x < (buttonSpec.x+buttonSpec.w) and y < (buttonSpec.y+buttonSpec.h)
end

function DetectClick(buttonMask)
   return ((gfx.mouse_cap & buttonMask) ~= 0) and ((old_mouse_cap & buttonMask) == 0)
end

function DetectModifier(modifierMask)
   return ((gfx.mouse_cap & modifierMask) ~= 0)
end

init(window_w, window_h)
run()

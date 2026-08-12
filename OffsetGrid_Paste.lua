-- OffsetGrid_Paste.lua
-- Paste OffsetGrid text from clipboard into MIDI
-- Auto-creates item if needed and auto-resizes
--
-- Author: Mahbod (Mabbie) Fard
-- Project: OffsetGrid - https://github.com/mabbiexfard/OffsetGrid
-- License: MIT

local text = reaper.CF_GetClipboard()
if not text or text == "" then return end

local lines = {}
for line in text:gmatch("[^\r\n]+") do table.insert(lines, line) end

-- 1. Read GRID
local spq = 8
if lines[1] and lines[1]:match("GRID:%s*HIRES") then
    spq = 24
    table.remove(lines, 1)
elseif lines[1] and lines[1]:match("GRID:%s*LOWRES") then
    spq = 8
    table.remove(lines, 1)
end

local tpq = reaper.SNM_GetIntConfigVar("miditicksperbeat", 960)
local tps = tpq / spq
local cursor_pos = reaper.GetCursorPosition()

-- 2. Determine Take / Item (Create if missing)
local take = reaper.MIDIEditor_GetTake(reaper.MIDIEditor_GetActive())
local item = nil

if take then
    item = reaper.GetMediaItemTake_Item(take)
else
    local track = reaper.GetSelectedTrack(0, 0)
    if not track then
        reaper.MB("Please select a track to create a MIDI item.", "OffsetGrid - Error", 0)
        return
    end
    -- Create a temporary 1-measure item, it will be resized later
    local qn_start = reaper.TimeMap2_timeToQN(0, cursor_pos)
    local end_pos = reaper.TimeMap2_QNToTime(0, qn_start + 4)
    item = reaper.CreateNewMIDIItemInProj(track, cursor_pos, end_pos, false)
    take = reaper.GetActiveTake(item)
end

local cursor_ppq = reaper.MIDI_GetPPQPosFromProjTime(take, cursor_pos)

-- 3. Parse Notes and find Max End PPQ
local max_end_ppq = 0
local notes_to_insert = {}

for _, line in ipairs(lines) do
    local pitches_str, beat_str, offset_str, dur_str, vel_str = line:match("(%S+)%s+(%d+)%.(%d+)%s+(%d+)%s+(%d+)")
        
    if pitches_str then
        local beat = tonumber(beat_str)
        local offset = tonumber(offset_str)
        local dur = tonumber(dur_str)
        local vel = tonumber(vel_str)

        local abs_step = (beat * spq) + offset
        local start_ppq = cursor_ppq + (abs_step * tps)
        local end_ppq = start_ppq + (dur * tps)
        
        if end_ppq > max_end_ppq then max_end_ppq = end_ppq end

        for pitch in pitches_str:gmatch("%d+") do
            table.insert(notes_to_insert, {
                start = start_ppq,
                ["end"] = end_ppq,
                pitch = tonumber(pitch),
                vel = vel
            })
        end
    end
end

if #notes_to_insert == 0 then return end

-- 4. Auto-Resize Item Logic
local item_start = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
local item_len = reaper.GetMediaItemInfo_Value(item, "D_LENGTH")
local item_end = item_start + item_len

local max_end_time = reaper.MIDI_GetProjTimeFromPPQPos(take, max_end_ppq)

-- Extend item to the right if notes go beyond current boundary
if max_end_time > item_end then
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", max_end_time - item_start)
    reaper.UpdateItemInProject(item)
end

-- 5. Insert Notes
for _, n in ipairs(notes_to_insert) do
    reaper.MIDI_InsertNote(take, false, false, n.start, n["end"], 0, n.pitch, n.vel, false)
end

reaper.MIDI_Sort(take)
reaper.UpdateArrange()

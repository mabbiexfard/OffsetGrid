-- OffsetGrid_Copy.lua
-- Copy selected MIDI notes to OffsetGrid text format (Beat.Offset)
-- Works in both MIDI Editor and Arrange View
--
-- Author: Mahbod (Mabbie) Fard
-- Project: OffsetGrid - https://github.com/mabbiexfard/OffsetGrid
-- License: MIT

-- 1. Get Take (From MIDI Editor OR Selected Item)
local take = reaper.MIDIEditor_GetTake(reaper.MIDIEditor_GetActive())
if not take then
    local item = reaper.GetSelectedMediaItem(0, 0)
    if item then
        take = reaper.GetActiveTake(item)
    end
end

if not take or not reaper.TakeIsMIDI(take) then
    reaper.MB("Please select a MIDI item or open it in the MIDI editor.", "OffsetGrid - Error", 0)
    return
end

local tpq = reaper.SNM_GetIntConfigVar("miditicksperbeat", 960)
local _, notecnt, _, _ = reaper.MIDI_CountEvts(take)

if notecnt == 0 then
    reaper.MB("No notes found in the selected item.", "OffsetGrid - Empty", 0)
    return
end

-- Collect selected notes (or all if none selected)
local notes = {}
local has_selection = false
for i = 0, notecnt - 1 do
    local _, sel, _, startppq, endppq, _, pitch, vel = reaper.MIDI_GetNote(take, i)
    if sel then has_selection = true end
    table.insert(notes, {sel=sel, start=startppq, end_=endppq, pitch=pitch, vel=vel})
end

local target_notes = {}
for _, n in ipairs(notes) do
    if not has_selection or n.sel then table.insert(target_notes, n) end
end

if #target_notes == 0 then return end

-- Calculate baseline PPQ (Start of item or minimum note start)
local item = reaper.GetMediaItemTake_Item(take)
local item_start_time = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
local base_ppq = reaper.MIDI_GetPPQPosFromProjTime(take, item_start_time)

-- 2. Detect Grid Resolution (LOWRES vs HIRES)
-- Check if any note deviates from the 1/32 grid (8 steps per beat)
local requires_hires = false
local spq_low = 8
local tps_low = tpq / spq_low

for _, n in ipairs(target_notes) do
    local rel_ppq = n.start - base_ppq
    local steps = rel_ppq / tps_low
    -- If step is not an integer (with a small margin of error for MIDI humanization), it's a triplet/hires
    if math.abs(steps - math.floor(steps + 0.5)) > 0.05 then
        requires_hires = true
        break
    end
end

local spq = requires_hires and 24 or 8
local tps = tpq / spq
local grid_tag = requires_hires and "GRID: HIRES" or "GRID: LOWRES"

-- 3. Group Chords and Format
local chords = {}
local current_chord = nil
local margin = 10 -- PPQ margin to consider notes as a chord

for _, n in ipairs(target_notes) do
    if current_chord and math.abs(n.start - current_chord.start) <= margin then
        table.insert(current_chord.pitches, n.pitch)
    else
        if current_chord then table.insert(chords, current_chord) end
        
        local rel_ppq = n.start - base_ppq
        local abs_step = math.floor((rel_ppq / tps) + 0.5)
        local beat = math.floor(abs_step / spq)
        local offset = abs_step % spq
        local dur_steps = math.max(1, math.floor(((n.end_ - n.start) / tps) + 0.5))
        
        current_chord = {
            pitches = {n.pitch},
            beat = beat,
            offset = offset,
            dur = dur_steps,
            vel = n.vel,
            start = n.start
        }
    end
end
if current_chord then table.insert(chords, current_chord) end

-- 4. Generate Output String
local lines = {grid_tag}
for _, chord in ipairs(chords) do
    table.sort(chord.pitches)
    local pitches_str = table.concat(chord.pitches, "+")
    local line = string.format("%s %d.%d %d %d", pitches_str, chord.beat, chord.offset, chord.dur, chord.vel)
    table.insert(lines, line)
end

local final_text = table.concat(lines, "\n")
reaper.CF_SetClipboard(final_text)

-- 5. GUI Message Box
reaper.MB("MIDI data copied successfully!\n\n" .. grid_tag .. "\nNotes: " .. #target_notes, "OffsetGrid - Copied", 0)

Here’s the improved README.

Copy everything below this line and replace the current README content with it:

---

# OffsetGrid

**Precision Beat.Offset MIDI text format for humans and AI**

Created by **Mahbod (Mabbie) Fard**

---

## What is OffsetGrid?

OffsetGrid is a clean, human-readable and AI-friendly text format for representing MIDI notes using a dual-resolution step grid.

### Core Syntax

Pitch(es) Beat.Offset Duration Velocity

### Dual Grid System

- **GRID: LOWRES** → 1 Beat = 8 Steps (great for straight rhythms)
- **GRID: HIRES** → 1 Beat = 24 Steps (supports triplets + straight rhythms)

### Example

GRID: HIRES  
36 0.0 6 110  
38 0.12 3 100  
36+40 1.0 12 95

---

## Features

- Extremely compact and readable
- Excellent for Large Language Models (low token count)
- Perfect for copy-paste workflows in DAWs (especially REAPER)
- Automatic chord support using `+`
- Clear integer duration system

---

## REAPER Scripts

Two scripts are included:

- **OffsetGrid_Copy.lua** → Copies selected MIDI notes to OffsetGrid text (puts it in the clipboard)
- **OffsetGrid_Paste.lua** → Pastes OffsetGrid text from the clipboard into a MIDI item

### How to use the scripts in REAPER

1. Copy the `.lua` files into your REAPER Scripts folder
2. In REAPER go to **Actions → Show action list → New action → Load ReaScript**
3. Load both scripts and optionally assign keyboard shortcuts

---

## Files in this repository

- `OffsetGrid_Spec.md` → Official specification
- `OffsetGrid_Copy.lua` → MIDI to OffsetGrid
- `OffsetGrid_Paste.lua` → OffsetGrid to MIDI

---

## Author

**Mahbod (Mabbie) Fard**  
GitHub: [mabbiexfard](https://github.com/mabbiexfard)

---

## License

MIT License

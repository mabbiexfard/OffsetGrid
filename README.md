# OffsetGrid

**Precision Beat.Offset MIDI text format for humans and AI**

Created by **Mahbod (Mabbie) Fard**

---

## What is OffsetGrid?

OffsetGrid is a clean, human-readable and AI-friendly plain-text format for representing MIDI notes.

It uses a dual-resolution step grid that keeps straight rhythms extremely compact while still supporting triplets with full precision.

### Core Syntax

```
Pitch(es) Beat.Offset Duration Velocity
```

| Field        | Description                                              |
|--------------|----------------------------------------------------------|
| Pitch(es)    | MIDI note number (0–127). Chords use `+` (e.g. `60+64+67`) |
| Beat.Offset  | Position as `Beat.Offset` (Beat starts at 0)             |
| Duration     | Integer steps according to the active grid               |
| Velocity     | MIDI velocity (1–127)                                    |

### Dual Grid System

| Grid          | Steps per Beat | Best for                          |
|---------------|----------------|-----------------------------------|
| `GRID: LOWRES`  | 8              | Straight rhythms (lower token count) |
| `GRID: HIRES`   | 24             | Triplets + straight rhythms       |

Every OffsetGrid file begins with one of these two lines.

---

## Quick Example

```
GRID: HIRES
36 0.0 6 110
38 0.12 3 100
36+40 1.0 12 95
```

---

## Features

- Extremely compact and readable
- Excellent for Large Language Models (very low token count)
- Perfect for copy-paste workflows in DAWs
- Automatic chord support with `+`
- Clear integer duration system
- Works great with REAPER via the included scripts

---

## REAPER Scripts

Two scripts are included for seamless workflow inside REAPER:

| Script                  | Purpose                                      |
|-------------------------|----------------------------------------------|
| `OffsetGrid_Copy.lua`   | Copies selected MIDI notes → OffsetGrid text (clipboard) |
| `OffsetGrid_Paste.lua`  | Pastes OffsetGrid text from clipboard → MIDI item        |

### How to install the scripts

1. Copy both `.lua` files into your REAPER Scripts folder  
   (usually `~/Library/Application Support/REAPER/Scripts` on macOS  
   or `%APPDATA%\REAPER\Scripts` on Windows)
2. In REAPER go to **Actions → Show action list → New action → Load ReaScript**
3. Load both scripts
4. (Optional) Assign keyboard shortcuts for fast access

---

## Python Converter

A command-line tool (`offsetgrid.py`) is included to convert between OffsetGrid text and standard MIDI files.

### Requirements

```bash
pip install mido
```

### Usage

**OffsetGrid → MIDI**

```bash
python offsetgrid.py to-midi input.txt output.mid
```

**MIDI → OffsetGrid**

```bash
python offsetgrid.py from-midi input.mid -o output.txt
```

Force HIRES grid:

```bash
python offsetgrid.py from-midi input.mid --hires -o output.txt
```

The converter automatically detects whether to use `GRID: LOWRES` or `GRID: HIRES`.

---

## Duration Tables

### LOWRES (8 steps per beat)

| Steps | Duration   |
|-------|------------|
| 1     | 1/32       |
| 2     | 1/16       |
| 4     | 1/8        |
| 8     | 1/4        |
| 16    | 1/2        |
| 32    | Whole note |

### HIRES (24 steps per beat)

| Steps | Duration     |
|-------|--------------|
| 3     | 1/32         |
| 6     | 1/16         |
| 12    | 1/8          |
| 24    | 1/4          |
| 4     | 1/16 triplet |
| 8     | 1/8 triplet  |
| 16    | 1/4 triplet  |

---

## Files in this repository

| File                    | Description                              |
|-------------------------|------------------------------------------|
| `OffsetGrid_Spec.md`    | Official specification                   |
| `OffsetGrid_Copy.lua`   | REAPER script: MIDI → OffsetGrid         |
| `OffsetGrid_Paste.lua`  | REAPER script: OffsetGrid → MIDI         |
| `offsetgrid.py`         | Python converter (text ↔ MIDI)           |
| `LICENSE`               | MIT License                              |

---

## Author

**Mahbod (Mabbie) Fard**  
GitHub: [mabbiexfard](https://github.com/mabbiexfard)

---

## License

MIT License

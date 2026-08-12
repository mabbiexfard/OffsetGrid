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

## Status

Currently in early public release.

Coming soon:
- Official Specification
- REAPER scripts (Copy MIDI → OffsetGrid / Paste OffsetGrid → MIDI)
- Python converter
- Documentation

---

## Author

**Mahbod (Mabbie) Fard**  
GitHub: [mabbiexfard](https://github.com/mabbiexfard)

---

## License

MIT License

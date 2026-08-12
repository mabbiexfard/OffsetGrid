# OffsetGrid Specification 1.0

**Precision Beat.Offset MIDI Text Format**

Created by **Mahbod (Mabbie) Fard**

---

## Overview

OffsetGrid is a human-readable and AI-friendly plain-text format for representing MIDI notes.

It uses a dual-resolution step grid system that allows both efficient straight rhythms and precise triplet support.

### Core Format

```
Pitch(es) Beat.Offset Duration Velocity
```

- **Pitch(es)**: MIDI note number (0-127). Multiple notes for a chord are joined with `+`
- **Beat.Offset**: Position in the form `Beat.Offset`
- **Duration**: Integer value based on the current grid
- **Velocity**: MIDI velocity (1-127)

---

## GRID System

The first line of every OffsetGrid file must declare the grid resolution:

### GRID: LOWRES
- 1 Beat = 8 Steps
- Offset range: 0 – 7
- Best for straight rhythms (lower token count)

**Duration table (LOWRES):**
- 1 = 1/32
- 2 = 1/16
- 4 = 1/8
- 8 = 1/4
- 16 = 1/2
- 32 = whole note

### GRID: HIRES
- 1 Beat = 24 Steps
- Offset range: 0 – 23
- Supports both straight rhythms and triplets without rounding errors

**Duration table (HIRES):**

Straight:
- 3 = 1/32
- 6 = 1/16
- 12 = 1/8
- 24 = 1/4

Triplet:
- 4 = 1/16t
- 8 = 1/8t
- 16 = 1/4t

---

## Examples

### LOWRES Example

```
GRID: LOWRES
49 0.0 2 70
52 0.2 2 70
49 0.4 2 70
51 0.6 2 71
45 1.0 2 63
47 1.2 2 71
37 1.4 8 107
54 2.4 2 69
52 2.6 2 75
56 3.0 2 70
52 3.2 2 66
51 3.4 2 46
52 3.6 2 65
37 4.0 6 107
```

### HIRES Example

```
GRID: HIRES
36 0.0 3 127
49 0.0 3 117
36+50 0.12 3 127
36 2.12 4 127
36 2.16 4 127
36 2.20 4 127
38+49 3.0 4 127
36 3.12 6 127
36 4.0 6 127
49 4.1 3 113
36 4.12 3 127
36+49 5.0 3 127
36 5.12 3 127
36+38 6.0 3 127
49 6.1 3 111
36 6.12 3 127
38 7.0 3 127
49 7.1 3 111
36 7.6 3 127
38 7.12 3 127
38 7.18 3 127
```

---

## Rules

1. The first line must be either `GRID: LOWRES` or `GRID: HIRES`.
2. Each subsequent line represents one note or one chord.
3. Chords are written by joining MIDI note numbers with `+` (example: `60+64+67`).
4. Beat starts at 0.
5. Offset must be within the legal range of the chosen grid.
6. Duration must be a positive integer from the duration table of the active grid.
7. Velocity must be an integer between 1 and 127.

---

## Author

**Mahbod (Mabbie) Fard**  
GitHub: https://github.com/mabbiexfard

---

## License

MIT License

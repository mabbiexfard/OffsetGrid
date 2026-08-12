# OffsetGrid

**A precision, human-readable text format for MIDI , built so AI models and musicians can read and write music together.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-early%20%2F%20experimental-orange)
![REAPER](https://img.shields.io/badge/DAW-REAPER-05a4dc)

Created by **Mahbod (Mabbie) Fard** , [@mabbiexfard](https://github.com/mabbiexfard)

---

## TL;DR

OffsetGrid converts MIDI notes into a compact plain-text format like this:

```
GRID: HIRES
36 0.0 6 110
38 0.12 3 100
36+40 1.0 12 95
```

...and back into MIDI again. That's the whole idea. It's not a DAW, not an AI, and not a music generator , it's a small, deterministic language for *note data* (pitch, position, duration, velocity) that both humans and language models can read, write, and edit directly.

---

## The Problem

Large language models are increasingly good at reasoning about music in words , "make the bassline funkier," "thin out the pre-chorus," "shift this note half a beat later." What they're bad at is reasoning about a raw MIDI file, which is a binary event stream designed for sequencers, not for text-based reasoning.

Today, turning a musical instruction into an actual edit almost always means a human sitting in a piano roll doing it by hand. OffsetGrid exists to shrink that gap: a note representation simple enough to fit cheaply in an LLM's context window, and unambiguous enough to convert back into exact, correct MIDI.

## What OffsetGrid Is

- A **plain-text, line-based representation** of MIDI notes and chords
- **Human-readable** | you can read and hand-edit a file without special tooling
- **Deterministic** | the same MIDI always produces the same text, and vice versa
- **Token-efficient** | designed to stay compact in an LLM's context, so more of a piece of music fits in a single prompt
- **Round-trippable** | convert MIDI → OffsetGrid → MIDI without losing note data
- A small, MIT-licensed **open specification**, not tied to any one tool or vendor

## What OffsetGrid Is Not

- **Not a DAW.** It doesn't play, mix, or render audio.
- **Not an AI model.** It doesn't generate or edit music by itself , it's the format an AI or a human writes in.
- **Not a full music-project format.** It only covers note-level data (pitch, timing, duration, velocity) , not CC data, pitch bend, automation, articulations, plugins, or audio.
- **Not (yet) DAW-native.** Right now it moves in and out of REAPER via copy/paste scripts, not a live two-way connection.

These are deliberate scope limits, not oversights , see [Roadmap](#roadmap--not-yet-covered) for what's intentionally left out of v1.

---

## How It Fits Together

OffsetGrid sits between three things that don't naturally speak the same language: a language model, a MIDI file, and a DAW.

```
   You / an LLM (ChatGPT, Claude, Gemini, local models…)
              │  "make the bassline funkier,
              │   keep the kick pattern intact"
              ▼
         OffsetGrid text
   ┌───────────────────────┐
   │ GRID: HIRES            │
   │ 36 0.0 6 110            │
   │ 38 0.12 3 100            │
   │ 36+40 1.0 12 95           │
   └───────────────────────┘
              │
              ▼  offsetgrid.py  /  OffsetGrid_Paste.lua
            MIDI
              │
              ▼
            REAPER
```

And the reverse direction works the same way: select notes in REAPER → `OffsetGrid_Copy.lua` → OffsetGrid text → paste into a chat with an editing instruction → get edited OffsetGrid text back → `OffsetGrid_Paste.lua` → updated MIDI in REAPER.

OffsetGrid itself is just the format in the middle. It's meant to be a small, reusable building block , useful on its own for copy/paste workflows, and usable as an interchange layer inside larger AI-assisted production tools.

---

## Format at a Glance

Every line describes one note or one chord:

```
Pitch(es) Beat.Offset Duration Velocity
```

| Field | Description |
|---|---|
| **Pitch(es)** | MIDI note number (0–127). Chords are joined with `+`, e.g. `60+64+67` (C major) |
| **Beat.Offset** | Position as `Beat.Offset` , beats start at `0` |
| **Duration** | An integer step count, read from the active grid's duration table |
| **Velocity** | MIDI velocity, `1`–`127` |

Every file opens with a grid declaration:

| Grid | Steps per beat | Best for |
|---|---|---|
| `GRID: LOWRES` | 8 | Straight rhythms , lowest token count |
| `GRID: HIRES` | 24 | Straight rhythms **and** triplets, with no rounding error |

### Example

```
GRID: HIRES
36 0.0 3 127
49 0.0 3 117
36+50 0.12 3 127
38+49 3.0 4 127
36 4.0 6 127
```

### Duration tables

**LOWRES** (8 steps/beat)

| Steps | Duration |
|---|---|
| 1 | 1/32 |
| 2 | 1/16 |
| 4 | 1/8 |
| 8 | 1/4 |
| 16 | 1/2 |
| 32 | Whole note |

**HIRES** (24 steps/beat)

| Steps | Duration (straight) |
|---|---|
| 3 | 1/32 |
| 6 | 1/16 |
| 12 | 1/8 |
| 24 | 1/4 |

| Steps | Duration (triplet) |
|---|---|
| 4 | 1/16t |
| 8 | 1/8t |
| 16 | 1/4t |

Full rules live in [`OffsetGrid_Spec.md`](OffsetGrid_Spec.md).

---

## Getting Started

### Option A , REAPER, copy/paste workflow

1. Copy both `.lua` files into your REAPER Scripts folder:
   - macOS: `~/Library/Application Support/REAPER/Scripts`
   - Windows: `%APPDATA%\REAPER\Scripts`
2. In REAPER: **Actions → Show action list → New action → Load ReaScript**, and load both files.
3. (Optional) Assign keyboard shortcuts to each for fast access.

Then:
- Select MIDI notes (in the MIDI editor or arrange view) and run **OffsetGrid_Copy** → OffsetGrid text lands on your clipboard.
- Run **OffsetGrid_Paste** with OffsetGrid text on your clipboard → it creates or fills a MIDI item, auto-resizing as needed.

### Option B , command line, file-based workflow

```bash
pip install mido
```

```bash
# OffsetGrid → MIDI
python offsetgrid.py to-midi input.txt output.mid

# MIDI → OffsetGrid
python offsetgrid.py from-midi input.mid -o output.txt

# Force HIRES resolution on export
python offsetgrid.py from-midi input.mid --hires -o output.txt
```

The converter automatically chooses `GRID: LOWRES` or `GRID: HIRES` based on the source MIDI unless you force one.

---

## A Typical AI-Assisted Workflow

1. In REAPER, select a bassline MIDI item and run **OffsetGrid_Copy**.
2. Paste the resulting text into a chat with any LLM, along with a plain-language instruction:

   > "Here's a bassline in OffsetGrid format. Thin out the notes that fall *between* the beats , keep anything landing exactly on a beat. Don't change velocity."

3. The model edits the text directly , removing or shifting lines , and returns updated OffsetGrid text.
4. Copy that text, run **OffsetGrid_Paste** back in REAPER, and audition the result in context.

Because the format is just text, this works with any model you have access to , there's no plugin or API key required to try it.

---

## Design Principles

- **Compact** , minimize tokens per note so more of a track fits in an LLM's context window
- **Human-readable** , no special viewer needed; it's legible in a plain text editor
- **Deterministic** , one correct text form per MIDI input, and vice versa, so round-trips are lossless for note data
- **Grid-explicit** , timing resolution is declared up front, so both people and models know exactly what a duration value means

---

## Roadmap / Not Yet Covered

OffsetGrid v1 intentionally covers only note-level data. Not yet represented:

- CC / modulation data
- Pitch bend
- Sustain and other performance controllers
- Articulations
- Automation and tempo changes

These are reasonable directions for a future spec version, and contributions or proposals are welcome , see [Contributing](#contributing).

---

## Project Status

OffsetGrid is early and experimental (current release: `v1.0.0`). The spec, scripts, and converter all work today, but the format hasn't been battle-tested across large libraries or many DAWs yet. Feedback, bug reports, and real-world usage are genuinely useful at this stage , please open an issue if something breaks or reads ambiguously.

---

## Contributing

Issues and pull requests are welcome , whether that's a bug in the REAPER scripts or the Python converter, a clarification for the spec, or a proposal for extending the format (CC data, other DAWs, other languages' bindings). If you build something on top of OffsetGrid, open an issue and let me know , it's helpful to see how the format holds up outside of REAPER.

---

## Files in This Repository

| File | Description |
|---|---|
| [`OffsetGrid_Spec.md`](OffsetGrid_Spec.md) | Official format specification |
| [`OffsetGrid_Copy.lua`](OffsetGrid_Copy.lua) | REAPER script: MIDI → OffsetGrid |
| [`OffsetGrid_Paste.lua`](OffsetGrid_Paste.lua) | REAPER script: OffsetGrid → MIDI |
| [`offsetgrid.py`](offsetgrid.py) | Command-line converter (text ↔ MIDI) |
| [`LICENSE`](LICENSE) | MIT License |

---

## License

MIT License , see [`LICENSE`](LICENSE). Use it, fork it, build on it.

## Author

**Mahbod (Mabbie) Fard**
GitHub: [@mabbiexfard](https://github.com/mabbiexfard)

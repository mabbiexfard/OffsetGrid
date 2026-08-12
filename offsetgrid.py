#!/usr/bin/env python3
"""
OffsetGrid - Precision Beat.Offset MIDI text format converter

Author: Mahbod (Mabbie) Fard
Project: https://github.com/mabbiexfard/OffsetGrid
License: MIT

This tool converts between OffsetGrid text and standard MIDI files.
"""

import argparse
import re
import sys
from pathlib import Path
from collections import defaultdict

try:
    import mido
except ImportError:
    print("Error: The 'mido' library is required.")
    print("Install it with:  pip install mido")
    sys.exit(1)


# ============================================================
# Duration tables
# ============================================================

LOWRES_DURATIONS = {
    1: 1 / 32,
    2: 1 / 16,
    4: 1 / 8,
    8: 1 / 4,
    16: 1 / 2,
    32: 1.0,
}

HIRES_DURATIONS = {
    # Straight
    3: 1 / 32,
    6: 1 / 16,
    12: 1 / 8,
    24: 1 / 4,
    # Triplet
    4: 1 / 16 / 1.5,   # ≈ 1/16t
    8: 1 / 8 / 1.5,    # ≈ 1/8t
    16: 1 / 4 / 1.5,   # ≈ 1/4t
}


def find_best_duration(steps_per_beat: int, duration_in_beats: float) -> int:
    """
    Find the best integer duration value for the given grid.

    Strategy:
    1. Prefer the exact number of steps when the duration lands cleanly
       on the grid (this preserves information for round-trips).
    2. Otherwise fall back to the nearest entry in the preferred table.
    """
    table = LOWRES_DURATIONS if steps_per_beat == 8 else HIRES_DURATIONS

    exact_steps = max(1, round(duration_in_beats * steps_per_beat))

    # If the duration is a clean multiple of the step size, keep the exact count.
    # This is especially useful for values that are legal but not in the "preferred" table
    # (e.g. duration 6 on LOWRES).
    expected_beats = exact_steps / steps_per_beat
    if abs(expected_beats - duration_in_beats) < 1e-6:
        return exact_steps

    # Otherwise choose the closest preferred table entry
    best = exact_steps
    best_diff = float("inf")
    for steps, beats in table.items():
        diff = abs(beats - duration_in_beats)
        if diff < best_diff:
            best_diff = diff
            best = steps
    return max(1, best)


# ============================================================
# Core converter class
# ============================================================

class OffsetGridConverter:
    def __init__(self, ppq: int = 960):
        self.ppq = ppq

    def text_to_midi(self, text: str) -> mido.MidiFile:
        """Convert OffsetGrid text to a mido.MidiFile object."""
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

        if not lines:
            raise ValueError("Empty OffsetGrid text")

        # Detect grid
        first = lines[0].upper()
        if "HIRES" in first:
            steps_per_beat = 24
            lines = lines[1:]
        elif "LOWRES" in first:
            steps_per_beat = 8
            lines = lines[1:]
        else:
            # Default to LOWRES if no tag
            steps_per_beat = 8

        ticks_per_step = self.ppq / steps_per_beat

        mid = mido.MidiFile(ticks_per_beat=self.ppq)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        events = []  # (start_tick, end_tick, pitch, velocity)

        for line in lines:
            # Match: pitches beat.offset duration velocity
            match = re.match(r"^([\d+]+)\s+(\d+)\.(\d+)\s+(\d+)\s+(\d+)$", line)
            if not match:
                continue

            pitches_str, beat_str, offset_str, dur_str, vel_str = match.groups()
            beat = int(beat_str)
            offset = int(offset_str)
            dur_steps = int(dur_str)
            velocity = max(1, min(127, int(vel_str)))

            start_tick = int((beat * steps_per_beat + offset) * ticks_per_step)
            end_tick = start_tick + int(dur_steps * ticks_per_step)

            for pitch_str in pitches_str.split("+"):
                pitch = int(pitch_str)
                if 0 <= pitch <= 127:
                    events.append((start_tick, end_tick, pitch, velocity))

        # Collect all note_on / note_off and sort stably
        messages = []
        for start, end, pitch, vel in events:
            messages.append((start, "note_on", pitch, vel))
            messages.append((end, "note_off", pitch, 0))

        # note_offs before note_ons at the exact same tick
        messages.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))

        last_tick = 0
        for tick, msg_type, pitch, vel in messages:
            delta = max(0, tick - last_tick)
            track.append(mido.Message(msg_type, note=pitch, velocity=vel, time=delta))
            last_tick = tick

        return mid

    def midi_to_text(self, midi: mido.MidiFile, force_hires: bool = False) -> str:
        """Convert a mido.MidiFile to OffsetGrid text."""
        ppq = midi.ticks_per_beat or self.ppq

        # Collect all notes (absolute ticks)
        notes = []  # (start_tick, end_tick, pitch, velocity)

        for track in midi.tracks:
            absolute_tick = 0
            active_notes = {}  # pitch → (start_tick, velocity)

            for msg in track:
                absolute_tick += msg.time
                if msg.type == "note_on" and msg.velocity > 0:
                    active_notes[msg.note] = (absolute_tick, msg.velocity)
                elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                    if msg.note in active_notes:
                        start, vel = active_notes.pop(msg.note)
                        notes.append((start, absolute_tick, msg.note, vel))

        if not notes:
            return "GRID: LOWRES\n"

        # --------------------------------------------------
        # Improved auto-detection of grid resolution
        # --------------------------------------------------
        steps_low = 8
        ticks_per_step_low = ppq / steps_low
        tolerance = 0.06  # ~6 % of a 1/32 step – tight but still allows mild humanization

        needs_hires = force_hires
        if not force_hires:
            off_grid_count = 0
            total_checks = 0

            for start, end, pitch, vel in notes:
                for tick in (start, end):
                    step = tick / ticks_per_step_low
                    total_checks += 1
                    if abs(step - round(step)) > tolerance:
                        off_grid_count += 1

            # If more than ~8 % of start/end positions are off the 8-step grid → HIRES
            if total_checks > 0 and (off_grid_count / total_checks) > 0.08:
                needs_hires = True

            # Extra safety: any single note that is clearly off (e.g. true triplet) forces HIRES
            if not needs_hires:
                for start, end, pitch, vel in notes:
                    step = start / ticks_per_step_low
                    if abs(step - round(step)) > 0.12:
                        needs_hires = True
                        break

        steps_per_beat = 24 if needs_hires else 8
        ticks_per_step = ppq / steps_per_beat
        grid_tag = "GRID: HIRES" if needs_hires else "GRID: LOWRES"

        # --------------------------------------------------
        # Group notes that start at the same time into chords
        # --------------------------------------------------
        groups = defaultdict(list)  # start_tick → list of (end, pitch, vel)

        for start, end, pitch, vel in notes:
            groups[start].append((end, pitch, vel))

        lines = [grid_tag]

        for start_tick in sorted(groups.keys()):
            chord_notes = groups[start_tick]

            # Use median duration & velocity for more robust chord representation
            ends = sorted(n[0] for n in chord_notes)
            vels = sorted(n[2] for n in chord_notes)
            end_tick = ends[len(ends) // 2]
            velocity = vels[len(vels) // 2]

            abs_step = round(start_tick / ticks_per_step)
            beat = abs_step // steps_per_beat
            offset = abs_step % steps_per_beat

            duration_in_beats = (end_tick - start_tick) / ppq
            dur_steps = find_best_duration(steps_per_beat, duration_in_beats)

            pitches = sorted(n[1] for n in chord_notes)
            pitches_str = "+".join(str(p) for p in pitches)

            lines.append(f"{pitches_str} {beat}.{offset} {dur_steps} {velocity}")

        return "\n".join(lines)


# ============================================================
# Command line interface
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="OffsetGrid converter – convert between OffsetGrid text and MIDI files"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # to-midi
    to_midi = subparsers.add_parser("to-midi", help="Convert OffsetGrid text → MIDI file")
    to_midi.add_argument("input", help="Input .txt file (OffsetGrid format)")
    to_midi.add_argument("output", help="Output .mid file")

    # from-midi
    from_midi = subparsers.add_parser("from-midi", help="Convert MIDI file → OffsetGrid text")
    from_midi.add_argument("input", help="Input .mid file")
    from_midi.add_argument("-o", "--output", help="Output .txt file (optional, prints to screen if omitted)")
    from_midi.add_argument("--hires", action="store_true", help="Force HIRES grid")

    args = parser.parse_args()
    converter = OffsetGridConverter()

    if args.command == "to-midi":
        text = Path(args.input).read_text(encoding="utf-8")
        mid = converter.text_to_midi(text)
        mid.save(args.output)
        print(f"Saved: {args.output}")

    elif args.command == "from-midi":
        mid = mido.MidiFile(args.input)
        text = converter.midi_to_text(mid, force_hires=args.hires)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
            print(f"Saved: {args.output}")
        else:
            print(text)


if __name__ == "__main__":
    main()

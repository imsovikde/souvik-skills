# score2md ABC Markdown Reference

Use this reference when inspecting, repairing, or validating playable ABC notation inside Markdown. For source routing and non-symbolic conversion, read `source-routing.md`.

## Viewer-Safe Shape

The Markdown file should contain one ABC fence:

````markdown
```abc
X:1
T:Song Title
C:Composer Or Original
M:4/4
Q:1/4=120
L:1/16
%%score {RH LH}
V:RH clef=treble name="Piano RH"
V:LH clef=bass name="Piano LH"
K:Dm
[V:RH] "Dm" [=D=F=A]4 [=A=d=f]4 | [=d=f=a]8 z8 |
[V:LH] =D,,8 =A,,8 | =D,,16 |]
```
````

Important rendering rule: do not put a blank line after `K:` or inside the ABC tune. Some Markdown viewers treat a blank line as the end of the tune and display only the metadata.

## Header Order

Use this order unless a source requires more:

1. `X:` tune number.
2. `T:` title. Multiple `T:` lines are allowed.
3. `C:` composer when known.
4. `N:` short note when useful.
5. `M:` meter, such as `4/4`, `3/4`, `6/8`, or `C|`.
6. `Q:` tempo, such as `Q:1/4=100`.
7. `L:` default note length. Prefer `L:1/16` for converted piano scores.
8. `%%score` and `V:` declarations for multi-voice output.
9. `K:` key.
10. Music body on the next line with no blank line.

## Note Basics

- `C D E F G A B` are the lower octave around middle C.
- `c d e f g a b` are one octave higher.
- Apostrophes raise octaves: `c'`.
- Commas lower octaves: `C,`, `C,,`.
- Rests use `z`.
- Durations follow notes: `D2`, `D4`, `D/2`, `D3/2`.
- Accidentals: `^C` sharp, `_B` flat, `=F` natural. score2md emits explicit accidentals by default.
- Bar lines: `|`, repeat/section `||`, final `|]`.

## Simultaneous Notes

Use square brackets for notes that sound at the same time:

```abc
[=D=F=A]2 [=F=A=c]2 [=A=d=f]2 [=c=f=a]2 |
```

Keep accidentals attached to the affected notes:

```abc
[=C=E=G]4 [=A^c=e]2 [_B=d=f]2 |
```

For piano arpeggio-like density in a single voice, alternate stacked chords and moving shapes:

```abc
"Dm" [DFA] [FAc] [Adf] [cfa] [ad'f] [fad'] [dfa] [Adf] |
```

## Right Hand And Left Hand

Use voices when preserving piano hands or staves:

```abc
%%score {RH LH}
V:RH clef=treble name="Piano RH"
V:LH clef=bass name="Piano LH"
K:Gm
[V:RH] _B =D =C =D | _B _E =D _E |
[V:LH] =G,,2 =D,2 =G,2 =D,2 | =C,,2 =G,,2 =C,2 =G,,2 |]
```

Rules:

- Every `[V:RH]` or `[V:LH]` body line must have a matching `V:` declaration.
- `%%score {RH LH}` asks ABC renderers to display the voices together.
- Keep RH/LH durations measure-aligned. If one voice is silent, fill the gap with rests.
- Use `clef=bass` for LH when the viewer supports it, but do not rely on clef alone for playback.

## Grace Notes And Ties

Grace notes use braces before the main note:

```abc
{_e=f_e}=d2
```

Ties use a hyphen after the duration:

```abc
D4- D4 | [DFA]4- [DFA]4 |
```

When converting MusicXML, attach grace notes to the next main note in the same voice, including when the grace notes occur at the end of the previous measure.

## MusicXML Conversion Checklist

When converting `.mxl` or `.musicxml`:

1. Read title, composer, part names, meter, key, tempo, and divisions.
2. Preserve every measure in order.
3. Track `backup` and `forward` elements to separate voices correctly.
4. Treat `<chord/>` notes as the same onset as the previous note in that voice.
5. Aggregate same-onset same-duration notes into ABC chord stacks.
6. Convert rests to `z` with exact duration.
7. Preserve ties where practical.
8. Carry grace notes to the next non-grace event in the same voice.
9. Preserve repeat starts, repeat ends, first/second endings, key changes, and time changes at measure boundaries.
10. Use explicit accidentals for converted notes unless manually optimizing notation.
11. Verify no blank lines appear between `K:` and the end of the tune.

## Common Failure Modes

- Blank line after `K:`: tune metadata renders, but music does not.
- Extra outer Markdown fence copied into the file: viewer shows code instead of a play button.
- Unsupported Markdown attributes on the code fence: use ` ```abc ` only.
- Chord annotations or slash chords breaking a strict parser: remove chord names if needed and keep note stacks.
- Mismatched voice declarations: declare `V:RH` before using `[V:RH]`.
- Illegal or ambiguous accidentals: prefer explicit `=`, `_`, and `^`.
- Over-complex output from PDF/OCR: ask for MusicXML/MXL when exactness matters.

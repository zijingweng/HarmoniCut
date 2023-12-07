import os
import music21 as m21
import pandas as pd
import svgwrite

musicbox_notes = [53, 55, 60, 62, 64, 65, 67, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 93]
black = svgwrite.rgb(0, 0, 0)

# copied from notebook created by Frank Zalkow and Meinard Müller. 
def xml_to_list(xml):
    """Convert a music xml file to a list of note events

    Notebook: C1/C1S2_MusicXML.ipynb

    Args:
        xml (str or music21.stream.Score): Either a path to a music xml file or a music21.stream.Score

    Returns:
        score (list): A list of note events where each note is specified as
            ``[start, duration, pitch, velocity, label]``
    """

    if isinstance(xml, str):
        xml_data = m21.converter.parse(xml)
    elif isinstance(xml, m21.stream.Score):
        xml_data = xml
    else:
        raise RuntimeError('midi must be a path to a midi file or music21.stream.Score')

    score = []
    instruments = []

    for part in xml_data.parts:
        instrument = part.getInstrument().instrumentName
        instruments.append(instrument)

        for note in part.flatten().notes:
            if note.isChord:
                start = note.offset
                duration = note.quarterLength

                for chord_note in note.pitches:
                    pitch = chord_note.ps
                    volume = note.volume.realized
                    score.append([start, duration, pitch, volume, instrument])

            elif note.isNote:
                start = note.offset
                duration = note.quarterLength
                pitch = note.pitch.ps
                volume = note.volume.realized
                score.append([start, duration, pitch, volume, instrument])

    score = sorted(score, key=lambda x: (x[0], x[2]))
    return score, instruments

def draw_note(dwg, time, pitch):
    dwg.add(dwg.circle((str(40 + 8.2 * time)+'mm', str(6 + (29 - musicbox_notes.index(pitch)) * 2)+'mm'), 
                       '1.1mm', 
                       stroke=black, 
                       fill='none'))

#fn = os.path.join('Wintergatan Marble Machine modified.mxl')
fn = os.path.join('Super Mario Bros - Ground Theme.mxl')
xml_data = m21.converter.parse(fn).stripTies()
xml_list, instruments = xml_to_list(xml_data)

fn_out = os.path.join('notes.csv')
df = pd.DataFrame(xml_list, columns=['Start', 'Duration', 'Pitch', 'Velocity', 'Instrument'])
df.to_csv(fn_out, sep=',', quoting=2, float_format='%.3f')

print("Available instruments:", instruments)
#[time, pitch] with correct instruments
print("Note skipped:", sum(1 for note in xml_list if note[4] in ['Vibraphone (2)', 'Vibraphone', 'Violins 1', 'Violins 2', 'Violoncello', 'Grand Piano'] and note[2] not in musicbox_notes))
notes = [[note[0], note[2]] for note in xml_list if note[4] in ['Vibraphone (2)', 'Vibraphone', 'Violins 1', 'Violins 2', 'Violoncello', 'Grand Piano'] and note[2] in musicbox_notes]

# 0.656 cm / turn

fn_out = os.path.join('test.svg')
Xmax = str(40 + 8.2 * notes[-1][0] + 25)+'mm'
print('length: ', Xmax)

dwg = svgwrite.Drawing('test.svg', 
                       (Xmax, '70mm'), 
                       profile='tiny')
dwg.add(dwg.line(('0mm', '0mm'), 
                 (Xmax, '0mm'), 
                 stroke=black))
dwg.add(dwg.line(('0mm', '0mm'), 
                 ('0mm', '15mm'), 
                 stroke=black))
dwg.add(dwg.line(('0mm', '15mm'), 
                 ('15mm', '70mm'), 
                 stroke=black))
dwg.add(dwg.line(('15mm', '70mm'), 
                 (Xmax, '70mm'), 
                 stroke=black))
dwg.add(dwg.line((Xmax, '0mm'), 
                 (Xmax, '70mm'), 
                 stroke=black))
for note in notes:
    draw_note(dwg, note[0], note[1])

dwg.save()
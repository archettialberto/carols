"""One-time scan preparation. Requires PyMuPDF; the player does not."""
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
# Bounds are fractions of page width/height; bar lines are fractions of page width.
LAYOUTS = {
    'the-first-nowell': [
        (0, .135, .315, [.105,.290,.428,.565,.704,.842,.930]),
        (0, .325, .495, [.105,.281,.425,.565,.705,.842,.930]),
        (0, .515, .685, [.105,.290,.428,.565,.704,.842,.930]),
        (0, .705, .850, [.105,.282,.401,.483,.604,.691,.791,.875]),
    ],
    'jingle-bells': [
        (0, .185, .510, [.125,.292,.430,.556,.693,.832,.974]),
        (0, .585, .900, [.050,.239,.393,.541,.683,.832,.965]),
        (1, .135, .450, [.065,.320,.536,.750,.948]),
        (1, .555, .870, [.065,.266,.447,.627,.808,.956]),
        (2, .140, .450, [.065,.247,.418,.575,.748,.948,.985]),
        (2, .545, .850, [.065,.319,.472,.643,.826,.964]),
    ],
}
# Jingle's third page first system has six bars, 22–27: refine the actual boundaries.
LAYOUTS['jingle-bells'][4] = (2,.140,.450,[.065,.264,.414,.534,.679,.824,.970])

for slug, systems in LAYOUTS.items():
    path=ROOT/'data'/f'{slug}.json'
    song=json.loads(path.read_text())
    doc=fitz.open(ROOT/song['source_pdf'])
    song['systems']=[]
    measure=1
    for index,(page_index,y0,y1,xs) in enumerate(systems):
        page=doc[page_index]; w,h=page.rect.width,page.rect.height
        x0,x1=.025,.985
        clip=fitz.Rect(w*x0,h*y0,w*x1,h*y1)
        image=page.get_pixmap(matrix=fitz.Matrix(2,2),clip=clip)
        filename=f'{slug}-{index+1}.png'
        image.save(ROOT/'web'/'scores'/filename)
        song['systems'].append(dict(image='scores/'+filename,page=page_index+1,
            first_measure=measure,barlines=[round((x-x0)/(x1-x0),5) for x in xs],
            width=image.width,height=image.height))
        measure+=len(xs)-1
    assert measure-1==len(song['parts']['soprano']), (slug,measure)
    path.write_text(json.dumps(song,indent=2)+'\n')

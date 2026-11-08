"""Create standalone, offline, printable editions using the app's exact SVG renderer.
Run: python tools/digital_score.py
Optional PDF: python tools/digital_score.py --pdf (requires Playwright + Chromium).
"""
import argparse
import base64
import html
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from music import ROOT, load_songs, public
from tools.compact_score import compact_score


def digital_html(song):
    data=json.dumps({'song':public(song),'compact':compact_score(song)},ensure_ascii=False).replace('<','\\u003c')
    renderer=(ROOT/'web'/'notation.js').read_text()
    library=(ROOT/'web'/'vendor'/'abcjs-basic-6.7.2.min.js').read_text()
    title=html.escape(song['title'])
    # Victorian title face, embedded so the printable edition stays fully offline.
    font=base64.b64encode((ROOT/'web'/'fonts'/'im-fell-english.woff2').read_bytes()).decode()
    return f'''<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Christmas Carol Choir</title><style>
:root {{ --print-paper:#fff; --print-ink:#000; --print-muted:#000; }}  /* black on white for printing */
html {{ background:var(--print-paper); }}
@font-face {{ font-family:'IM Fell English'; src:url(data:font/woff2;base64,{font}) format('woff2'); }}
.edition-header {{ text-align:center; margin:0 0 10px; }}
.edition-header h1 {{ font:400 30px/1.1 'IM Fell English',Georgia,serif; margin:0 0 6px; }}
.edition-header p {{ margin:0; font:12px/1.4 Georgia,serif; color:var(--print-muted); }}

body {{ color:var(--print-ink); background:var(--print-paper); font-family:Georgia,serif; margin:0; }}
.page {{ position:relative; box-sizing:border-box; width:182mm; height:269mm; padding-bottom:12mm; margin:24px auto; break-after:page; }}
.page:last-child {{ break-after:auto; }}
.page-content {{ display:flow-root; }}
.line {{ break-inside:avoid; margin-bottom:14px; }}
.line svg {{ display:block; width:100%; height:auto; }}
.abcjs-container {{ display:block!important; padding:0!important; overflow:visible!important; }}
.abcjs-container svg {{ position:static!important; display:block!important; width:100%!important; height:auto!important; }}
.performance-note {{ font:11px/1.5 Georgia,serif; color:var(--print-muted); margin:8px 0 0; }}
.page-footer {{ position:absolute; left:0; right:0; bottom:0; display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr); align-items:center; gap:12px; padding-top:7px; border-top:1px solid var(--print-muted); color:var(--print-muted); font:9px/1.3 system-ui,sans-serif; }}
.page-footer .measure-range {{ text-align:right; }}
#print {{ display:block; margin:20px auto; padding:10px 16px; cursor:pointer; }}
@page {{ size:A4; margin:14mm; background:var(--print-paper); }}
* {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
@media print {{ .page {{ margin:0; }} #print {{ display:none; }} }}
</style></head><body>
<button id="print" onclick="window.print()">Stampa / Salva PDF</button><div id="edition"></div>
<script>{library}</script><script>{renderer}</script><script>
const data={data};
const voices=['soprano','alto','tenor','bass'];
if (data.song.backing_track) voices.push('organ_rh','organ_lh');  // printed accompaniment
const names={{soprano:'Soprano',alto:'Contralto',tenor:'Tenore',bass:'Basso',organ_rh:'Organo',organ_lh:' '}};
const edition=document.getElementById('edition');
function newPage() {{
 const page=document.createElement('section');page.className='page';
 const content=document.createElement('div');content.className='page-content';
 const footer=document.createElement('footer');footer.className='page-footer';
 page.append(content,footer);edition.append(page);
 return {{page,content,footer}};
}}
let current=newPage();
const pages=[current];
{{
 // Only the title heads the first page (internal copies carry no credits or tempo).
 const header=document.createElement('header');header.className='edition-header';
 header.innerHTML=`<h1>{title}</h1>`;
 current.content.append(header);
}}
window.editionViews=[];
for (const [index,section] of data.compact.sections.entries()) {{
 const line=document.createElement('section');line.className='line';
 line.dataset.firstMeasure=section.bars[0].measure;line.dataset.lastMeasure=section.bars.at(-1).measure;
 const target=document.createElement('div');line.append(target);current.content.append(line);
 window.editionViews.push(ScoreNotation.render(target,data.song,section.bars,voices,names,1060,undefined,{{lyricNumbers:section.lyric_numbers,measureNumbers:true,staffsep:42}}));
 if (index===data.compact.sections.length-1) {{
   const notes=[...data.compact.notes];
   for (const text of notes) {{
     const note=document.createElement('p');note.className='performance-note';note.textContent=text;line.append(note);
   }}

 }}
 const available=current.page.clientHeight-parseFloat(getComputedStyle(current.page).paddingBottom);
 if(current.content.getBoundingClientRect().height>available && current.content.children.length>1) {{
   current=newPage();pages.push(current);current.content.append(line);
 }}
 if(current.content.getBoundingClientRect().height>available) throw Error('Un sistema musicale supera l’area stampabile.');
}}
window.editionPages=pages.map((entry,index)=>{{
 const lines=entry.content.querySelectorAll('.line');
 const first=Number(lines[0].dataset.firstMeasure),last=Number(lines[lines.length-1].dataset.lastMeasure);
 const title=document.createElement('span');title.className='footer-title';title.textContent=data.song.title;
 const number=document.createElement('span');number.className='page-number';number.textContent=`${{index+1}} / ${{pages.length}}`;
 const measures=document.createElement('span');measures.className='measure-range';measures.textContent=`bb. ${{first}}–${{last}}`;
 entry.footer.append(title,number,measures);
 return {{page:index+1,total:pages.length,first,last}};
}});
window.editionReady=true;
</script></body></html>'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',action='store_true')
    args=parser.parse_args()
    paths=[]
    for song in load_songs():
        path=ROOT/'exports'/f"{song['id']}-digital.html"
        path.write_text(digital_html(song))
        paths.append(path)
        print(path.name)
    if args.pdf:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
            for path in paths:
                # Downloads are always the light edition, whatever the app's theme.
                page=browser.new_page(color_scheme='light')
                page.goto(path.as_uri())
                page.wait_for_function('window.editionReady === true')
                # Reject incomplete engraving before writing the printable edition.
                assert page.evaluate('editionViews.every(v => !v.visual.warnings && v.positions.every(n => n.x !== null))')
                assert page.evaluate('editionPages.every(p => p.first <= p.last)')
                output=path.with_suffix('.pdf')
                page.pdf(path=str(output),format='A4',print_background=True,prefer_css_page_size=True)
                page.close()
                print(output.name)
            browser.close()


if __name__=='__main__': main()

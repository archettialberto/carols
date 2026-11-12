"""Optional regression checks for SVG engraving, voice balance and printable editions.
Run against the server: python tests/notation_smoke.py http://localhost:8000
Requires Playwright and Chromium in the development environment.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

base=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8000'
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':900})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base);page.wait_for_function('!!performanceData');page.locator('#open-library').click();page.locator('#song-list .track-play[aria-current=true]').click();page.wait_for_function('!!digitalView')
    # Inspect the full printable editions with the same renderer. Reconstructing MIDI
    # from engraved ABC checks accidental state, tenor octave, durations and ties.
    for slug in sorted(f.stem for f in (Path(__file__).resolve().parents[1]/'data').glob('*.json')):
        edition=browser.new_page()
        edition.goto((Path(__file__).resolve().parents[1]/'exports'/f'{slug}-digital.html').as_uri())
        edition.wait_for_function('window.editionReady === true')
        # One header on page 1: the title only (internal copies: no credits, tempo or sources).
        assert edition.locator('h1').count()==1 and edition.locator('h1').inner_text()==edition.evaluate('data.song.title')
        assert edition.locator('.page').first.locator('.edition-header').count()==1
        assert edition.locator('.tempo, .credit, .credits, h2, .source').count()==0
        assert edition.evaluate("!('composer' in data.song) && !('arranger' in data.song) && !('sources' in data.song)")
        pagination=edition.evaluate('editionPages')
        assert edition.locator('.page-footer').count()==len(pagination)
        # Each system after the first is numbered with its real source measure.
        numbers=edition.evaluate("editionViews.map((v,i)=>[data.compact.sections[i].bars[0].measure,[...v.svg.querySelectorAll('.abcjs-bar-number')].map(e=>e.textContent)])")
        assert all(shown==([] if first==1 else [str(first)]) for first,shown in numbers),(slug,numbers)
        printed=[]
        for index,info in enumerate(pagination):
            footer=edition.locator('.page-footer').nth(index)
            assert footer.locator('.footer-title').inner_text()==edition.evaluate('data.song.title')
            assert footer.locator('.page-number').inner_text()==f"{index+1} / {len(pagination)}"
            assert footer.locator('.measure-range').inner_text()==f"bb. {info['first']}–{info['last']}"
            printed.extend(range(info['first'],info['last']+1))
        assert printed==list(range(1,edition.evaluate('data.compact.bars.length')+1))
        result=edition.evaluate(r'''() => {
          let notes=0;
          for (const view of editionViews) {
            if (view.visual.warnings) return {error:view.visual.warnings};
            const ink=view.svg.getBBox(), box=view.svg.viewBox.baseVal;
            if (ink.x+ink.width>box.width || ink.y+ink.height>box.height) return {error:'Clipped notation or lyrics'};
            if (view.positions.some(p=>p.x===null)) return {error:'A note/rest has no SVG anchor'};
            const parsedVoices=view.visual.lines.flatMap(line=>line.staff||[]).flatMap(staff=>staff.voices||[]);
            for(let vi=0;vi<4;vi++) {
              const printed=parsedVoices[vi].filter(n=>n.el_type==='note');
              const source=view.source.notes.filter(n=>n.voiceIndex===vi);
              if(printed.length!==source.length) return {error:'Printed note count differs'};
              for(let n=0;n<source.length;n++) {
                for(let row=0;row<source[n].lyrics.length;row++) {
                  const expected=source[n].lyrics[row]?.text||'';
                  const actual=(printed[n].lyric?.[row]?.syllable||'').replace(/^\d+\.\s*/,'').trim();
                  if(actual!==expected) return {error:'A stanza syllable is missing or shifted',voice:vi,note:n,row,actual,expected};
                }
              }
            }
            const tracks=view.visual.setUpAudio().tracks;
            const offset=view.source.notes[0].start;
            const expected=[[],[],[],[]], pending=[false,false,false,false];
            for (const note of view.source.notes) {
              if (note.pitch==='R' || note.voiceIndex>3) continue;  // choir parts; organ chords are checked for anchors only
              const match=note.pitch.match(/^([A-G])([#b]?)([0-8])$/);
              const midi=12*(Number(match[3])+1)+{C:0,D:2,E:4,F:5,G:7,A:9,B:11}[match[1]]+(match[2]==='#'?1:match[2]==='b'?-1:0);
              expected[note.voiceIndex].push({pitch:midi,start:(note.start-offset)/4,duration:(note.end-note.start)/4});
            }
            // ABCJS merges notated ties into sounding events. Use the original tied
            // performance bars to derive the matching merged sequence independently.
            const bars=data.compact.bars.filter(b=>b.start>=offset && b.start<view.source.notes.at(-1).end);
            for(let vi=0;vi<4;vi++) {
              const merged=[];let tied=false;
              for (const bar of bars) {
                let at=bar.start-offset;
                for(const n of bar.parts[voices[vi]]) {
                  if(n.pitch!=='R') {
                    const raw=expected[vi].find(e=>Math.abs(e.start-at/4)<1e-8);
                    if(tied) merged.at(-1).duration+=n.duration/4;
                    else merged.push({...raw});
                  }
                  tied=n.tie;at+=n.duration;
                }
              }
              const actual=tracks[vi].filter(n=>n.cmd==='note').map(n=>({pitch:n.pitch,start:n.start,duration:n.duration}));
              if(JSON.stringify(actual)!==JSON.stringify(merged)) return {error:'Engraved pitches/rhythm differ',voice:vi,actual,expected:merged};
              notes+=actual.length;
            }
          }
          return {notes,systems:editionViews.length};
        }''')
        assert 'error' not in result,(slug,result)
        print(slug,result)
        edition.close()
    # Click an actual SVG note and check that playback seeks to that onset.
    page.locator('#song').select_option(label='Jingle Bells');page.wait_for_function('!!digitalView')
    page.evaluate('seek(0,false)')
    target=page.locator('.system:visible .abcjs-note.abcjs-v0.abcjs-m1.abcjs-n0')
    # A beamed note's box includes empty space; abcjs resolves clicks by proximity.
    target.click(force=True);page.wait_for_timeout(70)
    assert page.evaluate('playing && Math.abs(currentBeat()-2)<.5')
    page.locator('#voice').select_option(label='Bassi in evidenza');page.wait_for_timeout(150)
    assert page.evaluate('emphasizedVoice==="bass" && selected.size===4')
    assert page.evaluate('voiceBuses.bass.gain.value > voiceBuses.soprano.gain.value*3.5')
    before=page.evaluate('currentBeat()')
    page.locator('#voice').select_option(label='Solo bassi');page.wait_for_timeout(100)
    assert page.evaluate('selected.size===1 && voiceBuses.soprano.gain.value<.01 && voiceBuses.bass.gain.value>.99')
    assert page.evaluate('currentBeat()')>before  # mix changes do not restart the timeline
    assert page.evaluate('digitalView.positions.every(p=>p.voice==="bass")')
    page.locator('#voice').select_option(label='Tutte le voci');page.wait_for_timeout(120)
    assert page.evaluate('voices.every(v=>Math.abs(voiceBuses[v].gain.value-1)<.01)')
    page.locator('#play').click()
    assert page.locator('details:not(#booklet)').count()==0
    assert page.locator('#download').count()==1
    assert page.locator('.system:visible svg').is_visible()
    for width in [320,390]:
        page.set_viewport_size({'width':width,'height':844})
        # The phone selection sheet holds the voice selector.
        page.locator('#selection-summary').click();page.locator('#voice').select_option(label='Bassi in evidenza');page.keyboard.press('Escape')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('.system:visible .lead-voice').count()>0
    assert not errors,errors
    browser.close()
print('PASS: every engraved pitch/rhythm and SVG anchor, tenor octave, shared-stanza engraving, note click, solo/emphasized/ensemble gains, uninterrupted playback, minimal controls, mobile')

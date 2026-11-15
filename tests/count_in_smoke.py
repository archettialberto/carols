"""Optional browser check: the count-in that opens every Play, the light PDF link and the installable app.
Run against an active server: python tests/count_in_smoke.py http://localhost:8000
The count-in follows the Web Audio clock; in headless Chromium without a sound device (e.g. WSL)
that clock can stall intermittently, so rerun before suspecting the app.
"""
import sys
from playwright.sync_api import sync_playwright

base=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8000'
frequency=lambda midi: 440*2**((midi-69)/12)
def ticks(meter):
    """Clicks of the count-in, as tools/recordings.py builds them for the playlists."""
    beats,unit=meter
    per_bar=beats//3 if unit==8 and beats%3==0 and beats>3 else beats
    return per_bar*(2 if per_bar<3 else 1)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    page=browser.new_page(viewport={'width':390,'height':844},color_scheme='light',has_touch=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'/#/brani');page.wait_for_function('songs.length > 0')
    def open_song(song_id):
        page.evaluate(f"location.hash = '#/spartito/{song_id}'")
        page.wait_for_function(f'song.id === "{song_id}" && !!digitalView')
    def cue():
        """Start playback and read the piano cue: its pitches, and the clicks before the music."""
        page.locator('#play').click()
        page.wait_for_function('playing && !!intro')
        result=page.evaluate('({freqs: sounding.map(h => h.frequency).sort((a, b) => a - b), clicks: Math.round((anchorTime - intro.ticks) / intro.spacing), beat: currentBeat(), position})')
        page.locator('#play').click(); page.wait_for_function('!playing && !starting')
        return result
    for song_id,pitches in [('jingle-bells',{'soprano':71,'alto':67,'tenor':62,'bass':55}),
                            ('the-first-nowell',{'soprano':66,'alto':61,'tenor':57,'bass':45})]:
        open_song(song_id)
        meter=page.evaluate('song.meter')
        # All voices: the chord of the four starting notes on the piano, then the metronome.
        page.evaluate('seek(0,false)')
        result=cue()
        assert all(abs(a-b)<.01 for a,b in zip(result['freqs'],sorted(frequency(m) for m in pitches.values()))),(song_id,result)
        assert result['clicks']==ticks(meter),(song_id,meter,result)
        assert result['beat']==0  # the clock waits during the count-in
        # A part alone (or in evidenza): only its own note, audible whatever the mix.
        for voice,midi in pitches.items():
            page.evaluate(f'setMode("{voice}")')
            assert abs(cue()['freqs'][0]-frequency(midi))<.01 and len(cue()['freqs'])==1,(song_id,voice)
        page.evaluate('setMode("all")')
    # Only a start from the beginning counts in: resuming mid-song goes on at once, with no cue.
    open_song('jingle-bells'); page.evaluate('setMode("lead:alto"); seek(32,false)')
    page.locator('#play').click(); page.wait_for_function('playing')
    assert page.evaluate('intro === null && !document.body.hasAttribute("data-intro")')
    assert page.evaluate('anchorTime - audio.currentTime < .2')  # no count-in delay
    page.locator('#play').click(); page.wait_for_function('!playing && !starting')
    # Transposition: the cue, the playback and the engraving shift together; a new song starts untransposed.
    page.evaluate('setMode("soprano"); seek(0,false)'); page.evaluate('setTranspose(2)')
    assert abs(cue()['freqs'][0]-frequency(73))<.01  # B4 + 2 semitones
    assert page.evaluate('digitalKey.endsWith(":2")')
    open_song('the-first-nowell')
    assert page.evaluate('transpose')==0 and page.locator('#transpose-value').text_content()=='Tono originale'
    # The PDF download is always the light edition, whatever the app theme.
    page.evaluate('appearance.set("dark")')
    link=page.locator('#download').get_attribute('href')
    assert link.endswith('-digital.pdf')
    response=page.request.get(base+'/'+link)
    assert response.ok and response.headers['content-type']=='application/pdf'
    assert page.request.get(base+'/'+link.replace('.pdf','-dark.pdf')).status==404
    # Installable on iPhone/Android: manifest, icons, fonts and revalidated static files.
    manifest=page.request.get(base+'/manifest.webmanifest')
    assert manifest.ok and manifest.json()['display']=='standalone'
    for asset in ['icons/apple-touch-icon.png','icons/icon-192.png','icons/icon-512.png','icons/icon-maskable-512.png','sw.js','icons.svg',
                  'fonts/im-fell-english.woff2','fonts/eb-garamond-latin.woff2','fonts/eb-garamond-italic-latin.woff2']:
        assert page.request.get(base+'/'+asset).ok,asset
    assert page.locator('link[rel=apple-touch-icon]').count()==1
    assert page.locator('meta[name=apple-mobile-web-app-capable]').get_attribute('content')=='yes'
    assert page.request.get(base+'/player.js').headers['cache-control']=='no-cache'
    assert not errors,errors
    browser.close()
print('PASS: piano count-in chords and single parts from the start only, metre-based clicks, held clock, no cue when resuming, transposition, light PDF link and PWA assets')

"""Optional browser check: starting-note keys and chords, fixed tones, PDF links and the installable app.
Run against an active server: python tests/starting_note_smoke.py http://localhost:8000
Releases follow the Web Audio clock; in headless Chromium without a sound device (e.g. WSL)
that clock can stall intermittently, so rerun before suspecting the app.
"""
import sys
from playwright.sync_api import sync_playwright

base=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8000'
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},color_scheme='light',has_touch=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base);page.wait_for_function('!!performanceData');page.locator('.song-card[aria-current=true]').click()
    assert page.locator('details').count()==0
    assert page.locator('#download').count()==1
    key=lambda voice: page.locator(f'.key[data-voice={voice}]')
    for title,pitches in [('Jingle Bells',{'soprano':71,'alto':67,'tenor':62,'bass':55}),
                         ('The First Nowell',{'soprano':66,'alto':61,'tenor':57,'bass':45})]:
        page.evaluate(f'document.getElementById("song").value = String(songs.findIndex(s => s.title === {title!r})); chooseSong()')
        # Preview a voice even when that voice is muted in the normal playback mix.
        page.evaluate('document.getElementById("voice").value = "bass"; document.getElementById("voice").onchange()')
        page.evaluate('seek(9,false)')
        for voice,midi in pitches.items():
            before=page.evaluate('position')
            key(voice).click()  # a trusted tap also unlocks Web Audio
            page.wait_for_function(f'previewNotes.has("{voice}")')
            expected=440*2**((midi-69)/12)
            actual=page.evaluate(f'previewNotes.get("{voice}").frequency')
            assert abs(actual-expected)<.01,(title,voice,actual,expected)
            assert key(voice).get_attribute('aria-pressed')=='true'
            assert not page.evaluate('playing')
            assert page.evaluate('position')==before
            # A tap still rings as a short cue, then ends on its own.
            # Released on the audio clock, which can lag wall time in a loaded headless browser.
            page.wait_for_function(f'!previewNotes.has("{voice}")',timeout=15000)
        # Piano-like chord: hold several keys together, release them independently.
        for voice in ('soprano','tenor','bass'): key(voice).dispatch_event('pointerdown')
        page.wait_for_function('previewNotes.size === 3')
        page.wait_for_timeout(2200)
        assert page.evaluate('previewNotes.size')==3  # holding sustains past the short cue
        key('tenor').dispatch_event('pointerup')
        page.wait_for_function('!previewNotes.has("tenor") && previewNotes.size === 2',timeout=15000)
        # Normal playback cancels held previews and resumes from the preserved position.
        page.locator('#play').click();page.wait_for_timeout(150)
        assert page.evaluate('playing && previewNotes.size === 0 && currentBeat() >= 9')
        page.locator('#play').click()
        for voice in ('soprano','bass'): key(voice).dispatch_event('pointerup')

    # Choir parts are always piano; there is no user-facing instrument selector.
    assert page.locator('#sound').count()==0
    page.evaluate('seek(2,false)');page.locator('#play').click();page.wait_for_timeout(350)
    assert page.evaluate('playing && sounding.length > 0')
    page.locator('#play').click()

    # Transposition: audio, keys and engraving shift together; each song starts untransposed.
    page.evaluate('document.getElementById("song").value = String(songs.findIndex(s => s.title === "Jingle Bells")); chooseSong()')
    page.evaluate('document.getElementById("transpose").value = "2"; document.getElementById("transpose").onchange()')
    assert page.evaluate('transpose')==2
    assert key('soprano').locator('small').inner_text()=='Do♯5'  # B4 + 2 semitones
    key('soprano').click(); page.wait_for_function('previewNotes.has("soprano")')
    assert abs(page.evaluate('previewNotes.get("soprano").frequency')-440*2**((73-69)/12))<.01
    assert page.evaluate('digitalView.visual && digitalKey.includes(":2:")')
    page.evaluate('document.getElementById("song").value = String(songs.findIndex(s => s.title === "The First Nowell")); chooseSong()')
    assert page.evaluate('transpose')==0 and page.locator('#transpose').input_value()=='0'
    # The PDF download is always the light edition, whatever the app theme.
    page.evaluate('appearance.set("dark")')
    link=page.locator('#download')
    assert link.get_attribute('href').endswith('-digital.pdf')
    response=page.request.get(base+'/'+link.get_attribute('href'))
    assert response.ok and response.headers['content-type']=='application/pdf'
    assert page.request.get(base+'/'+link.get_attribute('href').replace('.pdf','-dark.pdf')).status==404

    # Installable on iPhone/Android: manifest, icons and revalidated static files.
    manifest=page.request.get(base+'/manifest.webmanifest')
    assert manifest.ok and manifest.json()['display']=='standalone'
    for icon in ['icons/apple-touch-icon.png','icons/icon-192.png','icons/icon-512.png','icons/icon-maskable-512.png','sw.js','fonts/im-fell-english.woff2']:
        assert page.request.get(base+'/'+icon).ok,icon
    assert page.locator('link[rel=apple-touch-icon]').count()==1
    assert page.locator('meta[name=apple-mobile-web-app-capable]').get_attribute('content')=='yes'
    assert page.request.get(base+'/player.js').headers['cache-control']=='no-cache'
    assert not errors,errors
    browser.close()
print('PASS: starting-note keys and chords, muted-voice previews, cancellation, fixed piano voices, transposition, light PDF link and PWA assets')

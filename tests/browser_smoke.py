"""Optional UI checks: pip install playwright; playwright install chromium.
Run against an active server: python tests/browser_smoke.py http://localhost:8001
"""
import sys
from playwright.sync_api import sync_playwright

base=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8000'

def options(page):
    """Phones keep voices, stanzas and the other options in a sheet behind one button."""
    if page.locator('#options-button').is_visible() and page.evaluate('!document.body.dataset.sheet'):
        page.locator('#options-button').click()

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    errors=[]
    for width,height in ((320,568),(390,664),(768,1024),(1280,820)):
        context=browser.new_context(viewport={'width':width,'height':height},has_touch=width<600,color_scheme='light')
        page=context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(base)
        page.wait_for_function('songs.length > 0 && !!performanceData')
        # No home: the app opens on the playlists; the tabs are Playlist, Spartiti, PDF.
        assert page.evaluate('document.body.dataset.view')=='albums'
        assert page.locator('.tabs a').all_inner_texts()==['Playlist','Spartiti','PDF']
        assert page.locator('.tabs a[aria-current=page]').inner_text()=='Playlist'
        assert page.locator('.player-dock').is_hidden()
        assert page.title()=='Christmas Carol Choir' and page.locator('html').get_attribute('lang')=='it'
        assert ' '.join(page.locator('.brand').inner_text().split())=='🎄 Christmas Carol Choir'
        # Appearance: device → light → dark, the glyph follows, the choice survives a reload.
        assert page.locator('#theme').get_attribute('data-mode')=='system'
        assert page.locator('html').get_attribute('data-theme')=='light'
        page.emulate_media(color_scheme='dark'); page.wait_for_function('document.documentElement.dataset.theme === "dark"')
        page.locator('#theme').click()
        assert page.locator('html').get_attribute('data-theme')=='light' and page.locator('#theme use').get_attribute('href')=='icons.svg#sun'
        page.reload(); page.wait_for_function('songs.length > 0')
        assert page.locator('#theme').get_attribute('data-mode')=='light'
        page.locator('#theme').click()
        assert page.locator('html').get_attribute('data-theme')=='dark' and page.locator('#theme use').get_attribute('href')=='icons.svg#moon'
        page.locator('#theme').click(); page.emulate_media(color_scheme='light')
        page.wait_for_function('document.documentElement.dataset.theme === "light"')
        # Spartiti: one list in the choir's running order, the same rows as the playlists (number, tile, title, length).
        page.locator('.tabs a', has_text='Spartiti').click()
        page.wait_for_function('document.body.dataset.view === "library"')
        assert page.locator('#library-panel').is_visible()
        titles=page.locator('#song-list .song-title').all_text_contents()
        assert titles[0].startswith('We Wish') and titles[1].startswith('Hark') and {'Jingle Bells','The First Nowell'}<=set(titles)
        assert page.locator('#song-list .song-row').first.locator('.song-num, .song-art svg, .song-meta').count()==3
        assert page.locator('#song-list .song-row[aria-current] .song-title').inner_text()==titles[0]
        page.locator('#song-list .song-row', has_text='Jingle Bells').click()
        page.wait_for_function('song.title === "Jingle Bells" && !!digitalView')
        assert page.locator('#practice-panel').is_visible() and page.locator('.player-dock').is_visible()
        # The whole performance is one engraved line, always four staves; no starting-note keys or restart.
        assert page.locator('#score svg').count()==1 and page.locator('#score svg .abcjs-clef').count()>=4
        assert page.locator('.key, #stop, #restart, #previous-line, #next-line, #verse, #voice, #song').count()==0
        assert page.locator('#score svg .abcjs-lyric').count()==0  # the words are read from the sliding line
        # One light PDF download, no original scan.
        assert page.locator('#download').get_attribute('href').endswith('-digital.pdf')
        assert page.locator('[href^="songs/"]').count()==0
        # Phones: no vertical scrolling while practising, and no horizontal page scroll anywhere.
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        if width<=760:
            assert page.evaluate('document.documentElement.scrollHeight <= innerHeight + 1')
            assert page.locator('.appbar').is_hidden()  # the score keeps the whole height
        assert page.locator('#play').bounding_box()['height']>=44
        # Stanzas: one chip each with the opening words; the head shows the stanza being sung.
        options(page)
        assert page.locator('#verses .verse-chip').count()==3
        assert '“Dashing through the snow' in page.locator('#verses .verse-chip').first.inner_text()
        page.keyboard.press('Escape')
        # Syllables follow actual beat positions, including the delayed soprano entry.
        page.evaluate('seek(32,false)')
        assert page.locator('.syllable.current').count()==0  # soprano rests until beat 33.5
        # The words follow the voice heard: a tap puts a part in evidenza, a second isolates it.
        options(page); page.locator('#voices [data-voice=alto]').click()
        assert page.evaluate('emphasizedVoice')=='alto' and page.evaluate('lyricVoice()')=='alto'
        assert page.locator('.syllable.current').inner_text()=='Dash'
        page.locator('#voices [data-voice=alto]').click()
        assert page.evaluate('selected.size')==1 and page.evaluate('lyricVoice()')=='alto'
        assert page.locator('#voice-label').inner_text().startswith('Solo contralti')
        page.locator('#voices [data-voice=all]').click(); page.keyboard.press('Escape')
        # Play from the beginning counts in (piano note, then metronome) with the clock held, then the music runs.
        page.evaluate('seek(0,false)')
        page.locator('#play').click()
        page.wait_for_function('playing && document.body.hasAttribute("data-intro")', timeout=20000)
        assert page.evaluate('currentBeat() === 0 && sounding.length > 0')
        page.wait_for_function('playing && !document.body.hasAttribute("data-intro") && currentBeat() > .2', timeout=20000)
        assert page.evaluate('sounding.length > 0 || choirSources.length > 0')
        page.locator('#play').click(); page.wait_for_timeout(40)
        before=page.evaluate('position'); page.wait_for_timeout(80)
        assert page.evaluate('position')==before and page.evaluate('!playing && sounding.length === 0')
        # Resuming after a pause goes on at once: no second count-in.
        page.locator('#play').click(); page.wait_for_function('playing', timeout=20000)
        assert page.evaluate('intro === null') and not page.evaluate('document.body.hasAttribute("data-intro")')
        page.locator('#play').click(); page.wait_for_function('!playing && !starting')
        # Space plays and pauses, even with a clicked button still focused (it is not pressed too).
        options(page); page.locator('#slow').focus(); slow=page.locator('#slow').get_attribute('aria-pressed')
        page.keyboard.press(' '); page.wait_for_function('playing || starting', timeout=20000)
        page.keyboard.press(' '); page.wait_for_function('!playing && !starting')
        assert slow=='false' and page.locator('#slow').get_attribute('aria-pressed')==slow  # Lento is off by default
        # Transposition shifts the engraving and falls back to the piano for a recorded choir.
        options(page); page.locator('#transpose-up').click()
        assert page.evaluate('transpose')==1 and 'Pianoforte' in page.locator('#voice-label').inner_text()
        assert page.locator('#sound-choir').is_disabled()
        page.locator('#transpose-down').click()
        assert page.evaluate('transpose')==0 and page.locator('#transpose-value').inner_text()=='Tono originale'
        page.keyboard.press('Escape')
        # The First Nowell: all stanzas on one line; the head and the words follow the stanza.
        page.evaluate("location.hash = '#/spartito/the-first-nowell'"); page.wait_for_function('song.id === "the-first-nowell" && !!digitalView')
        page.evaluate('seek(77,false)')
        assert page.locator('#verse-now').inner_text()=='Strofa 2'
        assert page.locator('.syllable.current').inner_text()=='They'
        options(page); page.locator('#verses .verse-chip').nth(4).click(); page.keyboard.press('Escape')
        assert page.locator('#verse-now').inner_text()=='Strofa 5'
        page.evaluate('seek(position+2,false)')  # the soprano enters on beat 3 of the stanza
        assert page.locator('.syllable.current').inner_text()=='Then'
        if width>760:
            page.locator('#zoom-in').click(); assert page.evaluate('zoom > 1')
        # End all sounds and highlighting at the end of a run.
        page.evaluate('seek(performanceData.duration-.1,false)')
        page.locator('#play').click()
        page.wait_for_function('!playing && !starting', timeout=30000); page.wait_for_timeout(100)
        assert page.evaluate('sounding.length')==0 and page.locator('.syllable.current').count()==0
        # The back gesture returns to the song list and pauses the score.
        page.go_back(); page.go_back()
        page.wait_for_function('document.body.dataset.view === "library"')
        assert page.locator('#library-panel').is_visible() and page.locator('.player-dock').is_hidden()
        assert page.request.get(base+'/'+page.locator('#download').get_attribute('href')).ok
        assert page.request.get(base+'/songs/Jingle%20Bells.pdf').status==404  # scans are never served
        page.screenshot(path=f'/tmp/carols-{width}.png')
        context.close()
    assert not errors,errors
    browser.close()
print('PASS: 320/390/768/1280px, tabs without home, icon theme control, running-order rows, continuous four-staff line, '
      'voice taps and voice-specific lyrics, stanza chips, count-in, Space, Lento off, transposition with piano fallback, '
      'final silence, back gesture, light PDF only')

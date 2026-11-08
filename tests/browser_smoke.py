"""Optional UI checks: pip install playwright; playwright install chromium.
Run against an active server: python tests/browser_smoke.py http://localhost:8001
"""
import sys
from playwright.sync_api import sync_playwright

base=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8000'
def pick(page, selector, **option):
    """Choose from a select that may live in the phone selection sheet."""
    if not page.locator(selector).is_visible():
        page.locator('#selection-summary').click()
    page.locator(selector).select_option(**option)
    page.keyboard.press('Escape')

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    errors=[]
    for width in (320,390,768,1280):
        context=browser.new_context(viewport={'width':width,'height':844},has_touch=width<600,color_scheme='light')
        page=context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(base)
        page.wait_for_function('performanceData && !document.getElementById("play").disabled')
        # The song list is the home page; the practice view is one tap away.
        assert page.locator('#library-panel').is_visible() and page.locator('#practice-panel').is_hidden()
        assert page.locator('.player-dock').is_hidden() and page.locator('#library-back').is_hidden()
        assert page.locator('#language, #sound, #settings, #settings-button, .page-tabs').count()==0
        assert '✓' not in page.locator('#song-list').inner_text()
        page.locator('.song-card').first.click()
        assert page.locator('#voice option').evaluate_all('(nodes)=>nodes.map(n=>n.value)')==[
            'all','lead:soprano','lead:alto','lead:tenor','lead:bass','soprano','alto','tenor','bass']
        if width<=700:
            page.locator('#selection-summary').click()
            assert page.locator('#selection').bounding_box()['y'] < 40  # selection sheet opens from the top
            page.keyboard.press('Escape')
        assert page.title()=='Christmas Carol Choir'
        assert page.locator('html').get_attribute('lang')=='it'
        assert ' '.join(page.locator('h1').inner_text().split())=='🎄 Christmas Carol Choir'
        assert page.locator('#theme').get_attribute('data-mode')=='system'
        assert page.locator('html').get_attribute('data-theme')=='light'
        page.emulate_media(color_scheme='dark')
        page.wait_for_function('document.documentElement.dataset.theme === "dark"')
        page.locator('#theme').click()
        assert page.locator('html').get_attribute('data-theme')=='light'
        page.reload();page.wait_for_function('!!performanceData');page.locator('.song-card[aria-current=true]').click()
        assert page.locator('#theme').get_attribute('data-mode')=='light'  # explicit choice survives device preference and reload
        page.locator('#theme').click()
        assert page.locator('html').get_attribute('data-theme')=='dark'
        assert page.locator('.system:visible').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(29, 39, 35)'  # dark score paper
        page.locator('#library-back').click()
        assert page.locator('#library-panel').is_visible()
        assert page.locator('.player-dock').is_hidden()
        titles=page.locator('.song-title').all_text_contents()
        assert titles==sorted(titles,key=str.casefold) and {'Jingle Bells','The First Nowell'}<=set(titles)
        assert page.locator('#backing-filter, .filter-track').count()==0  # one list for every song
        assert page.locator('.song-detail').count()==0  # cards show icon and title only
        assert page.locator('.song-card[aria-current=true] .song-title').inner_text()==titles[0]
        page.get_by_role('button',name='The First Nowell',exact=False).click()
        assert page.locator('#song').input_value()==str(page.evaluate('songs.findIndex(s => s.title === "The First Nowell")'))
        assert page.locator('#practice-panel').is_visible()
        page.locator('#library-back').click()
        page.get_by_role('button',name='Jingle Bells',exact=False).click()
        assert page.locator('#song').input_value()==str(page.evaluate('songs.findIndex(s => s.title === "Jingle Bells")'))
        page.locator('#theme').click()
        page.emulate_media(color_scheme='light')
        page.wait_for_function('document.documentElement.dataset.theme === "light"')
        assert page.locator('.system:visible').count()==1
        assert page.locator('.system:visible svg').count()==1
        assert page.locator('details').count()==0
        # One light PDF download, no original scan, no lyric-voice or custom-mix controls.
        assert page.locator('#download').count()==1 and page.locator('#download').get_attribute('href').endswith('-digital.pdf')
        assert page.locator('#text-voice, #mix, #downloads, #lyrics-title, #score-hint, [href^="songs/"]').count()==0
        assert page.locator('#voice option[value=custom]').count()==0
        assert page.locator('.key:visible').count()==4
        assert page.locator('#verse option').count()==4
        assert page.locator('#verse option').nth(1).inner_text()=='Str. 1 · “Dashing through the snow”'
        # Play/restart on the left, starting-note keys on the right.
        assert page.locator('#play').bounding_box()['x'] < page.locator('.key').first.bounding_box()['x']
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#play').bounding_box()['height']>=44
        # Syllables follow actual beat positions, including the delayed soprano entry.
        page.evaluate('seek(32,false)')
        assert 'A' in page.locator('#lyric-rows').inner_text()
        assert page.locator('.syllable.current').count()==0  # soprano rests until beat 33.5
        # The words follow the voice being heard.
        pick(page,'#voice',label='Solo contralti')
        assert page.evaluate('selected.size')==1 and page.evaluate('lyricVoice()')=='alto'
        assert page.locator('.syllable.current').inner_text()=='Dash'
        pick(page,'#voice',label='Contralti in evidenza')
        assert page.evaluate('lyricVoice()')=='alto' and page.locator('.syllable.current').inner_text()=='Dash'
        pick(page,'#voice',label='Solo contralti')
        assert page.evaluate('activeSystem.clientHeight < 180')
        page.locator('#play').click()
        page.wait_for_timeout(400)
        assert page.evaluate('playing && audio.state === "running" && sounding.length > 0')
        assert page.locator('#focus').count()==0  # no fullscreen/focus mode
        if width<600:
            assert page.locator('.lyrics-panel').bounding_box()['y'] < 700
        page.locator('#play').click();page.wait_for_timeout(40)
        before=page.evaluate('position');page.wait_for_timeout(80)
        assert page.evaluate('position')==before
        assert page.locator('html').get_attribute('lang')=='it'
        assert 'Ascolta' in page.locator('#play').inner_text()
        assert 'Dashing' in page.locator('#lyric-rows').inner_text()  # sung text stays in its original language
        page.reload();page.wait_for_function('!!performanceData');page.locator('.song-card[aria-current=true]').click()
        assert page.locator('html').get_attribute('lang')=='it'
        # All verses use the original score systems and update both stanza number and words.
        pick(page,'#song',label='The First Nowell')
        assert page.locator('#verse option').count()==6
        page.evaluate('seek(77,false)')
        assert 'Strofa 2 di 5' in page.locator('#section-name').inner_text()
        assert page.locator('.syllable.current').inner_text()=='They'
        assert 'They looked up' in page.locator('#lyric-rows').inner_text()
        pick(page,'#verse',label='Str. 5 · “Then entered in those”')
        page.wait_for_function('performanceData.bars.length === 25 && performanceData.bars[0].verse === 5')
        page.evaluate('seek(2,false)')
        assert page.locator('.syllable.current').inner_text()=='Then'
        page.locator('#next-line').click()
        assert 'Rigo 2 di 4' in page.locator('#line-position').inner_text()
        page.locator('#zoom-in').click()
        assert page.evaluate('zoom > 1')
        # End all sounds and highlighting at the end of a run.
        page.evaluate('seek(performanceData.duration-.1,false)')
        page.locator('#play').click();page.wait_for_timeout(250)
        assert not page.evaluate('playing')
        assert page.evaluate('sounding.length')==0
        assert page.locator('.syllable.current').count()==0
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=f'/tmp/carols-{width}.png',full_page=True)
        assert page.request.get(base+'/'+page.locator('#download').get_attribute('href')).ok
        assert page.request.get(base+'/songs/Jingle%20Bells.pdf').status==404  # scans are never served
        assert page.request.get(base+'/api/performance/jingle-bells/99.json').status==404
        context.close()
    assert not errors,errors
    browser.close()
print('PASS: 320/390/768/1280px, fixed Italian UI, all/selected verses, voice-specific lyrics, beat highlighting, cropped staves, fixed piano audio, focused view, library-back navigation, downloads, final silence, alphabetical songs, icon theme control and live device changes')

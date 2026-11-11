"""Optional checks of the home page and the recording playlists (Playwright, active server):
python tests/playlist_smoke.py http://localhost:8001 [screenshot-dir]
"""
import sys
from playwright.sync_api import sync_playwright

base = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000'
shots = sys.argv[2] if len(sys.argv) > 2 else None
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
    errors = []
    for width, height in ((320, 568), (390, 664), (1280, 800)):
        page = browser.new_context(viewport={'width': width, 'height': height}, has_touch=width < 600).new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base)
        page.wait_for_function('document.querySelectorAll(".album-card").length === 9')
        assert page.locator('#home-panel').is_visible() and page.locator('#mini-player').is_hidden()
        assert page.locator('.home-title').all_text_contents() == ['Spartiti interattivi', 'Playlist', 'Genera PDF']
        assert page.locator('.home-detail').count() == 0
        if shots: page.screenshot(path=f'{shots}/home-{width}.png')
        # The PDF booklet is its own view from Home.
        page.locator('#open-booklet').click()
        page.wait_for_function('document.querySelectorAll("#booklet-list li").length > 10')
        assert page.locator('#booklet-panel').is_visible() and page.locator('.booklet-hint').count() == 0
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal page scroll'
        page.go_back()
        page.locator('#open-albums').click()
        names = ['Soprani', 'Contralti', 'Tenori', 'Bassi']
        assert page.locator('#albums-panel h2').all_text_contents() == ['Playlist completa', 'Playlist per voce']
        assert page.locator('#album-full svg.album').evaluate_all('n => n.map(s => s.getAttribute("aria-label"))') == ['Christmas Carols']
        assert page.locator('#album-list svg.album').evaluate_all('n => n.map(s => s.getAttribute("aria-label"))') == names + [f'{n} in evidenza' for n in names]
        # Christmas Carols: the whole choir, one plain track per song (no title, note or count-in).
        page.locator('.album-card').first.click()
        assert page.locator('#playlist-title').inner_text() == 'Christmas Carols'
        assert page.evaluate("[...document.querySelectorAll('.track-detail')].every(d => /^\\d+:\\d\\d$/.test(d.textContent))")
        page.go_back()
        if shots: page.screenshot(path=f'{shots}/albums-{width}.png', full_page=True)
        page.locator('.album-card').nth(7).click()  # Tenori in evidenza
        assert page.locator('#playlist-title').inner_text() == 'Tenori in evidenza'
        assert page.locator('#albums-back, #playlist-all, .playlist-hint, #playlist-tracks input').count() == 0
        titles = page.locator('.track-title').all_text_contents()
        assert titles == sorted(titles, key=str.casefold) and 'Joy to the World' in titles and 'Carol of the Bells' in titles
        page.locator('#playlist-play').click()
        page.wait_for_function('!document.getElementById("mini-player").hidden')
        assert page.locator('#mini-title').inner_text() == titles[0]
        assert page.locator('#mini-status').inner_text() == 'Tenori in evidenza'
        assert page.locator('#playlist-slow').count() == 0
        page.locator('#mini-next').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal page scroll'
        if shots: page.screenshot(path=f'{shots}/playlist-{width}.png', full_page=True)
        # Starting the interactive score pauses the recordings; the score has its own dock.
        page.locator('#home-button').click(); page.locator('#open-library').click()
        assert page.locator('#mini-player').is_hidden()
        page.locator('.song-card').first.click(); page.locator('#play').click()
        assert page.evaluate('Playlist.playing') is False
        page.go_back(); page.go_back()
        assert page.locator('#home-panel').is_visible() and page.locator('#mini-player').is_visible()
        # A song with recorded parts plays the choir in the score; another tempo or key falls back to piano.
        page.locator('#open-library').click(); page.locator('.song-card', has_text='Joy to the World').click()
        page.wait_for_function('song.id === "joy-to-the-world" && Object.keys(choirBuffers).length === 4', timeout=20000)
        assert page.evaluate("!$('sound-control').hidden && $('sound').value === 'choir'")
        page.locator('#play').click(); page.wait_for_timeout(400)
        assert page.evaluate('choirVoices.size') == 4
        assert page.locator('#tempo').count() == 0  # no bpm field: Lento is the only speed control
        page.evaluate("$('transpose').value = '2'; $('transpose').onchange()"); page.wait_for_timeout(300)
        assert page.evaluate('choirVoices.size') == 0 and 'Pianoforte' in page.locator('#summary-detail').inner_text()
        page.evaluate("$('transpose').value = '0'; $('transpose').onchange()"); page.wait_for_timeout(300)
        assert page.evaluate('choirVoices.size') == 4
        page.locator('#slow').click(); page.wait_for_timeout(2500)  # slowed choir, same voices
        assert page.evaluate('choirVoices.size') == 4 and page.locator('#slow').get_attribute('aria-pressed') == 'true'
        page.locator('#slow').click()
        page.context.close()
    assert not errors, errors
    browser.close()
print('PASS: three home choices without captions, PDF view, eight albums (solo and in evidenza), one track per song, Lento, '
      'mini player, history back, score/recording exclusivity, choir in the score with piano fallback at 320/390/1280px')

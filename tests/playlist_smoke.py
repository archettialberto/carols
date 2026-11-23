"""Optional checks of the playlists, the PDF view and the choir in the score (Playwright, active server):
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
        view = lambda name: page.wait_for_function(f'document.body.dataset.view === "{name}"')
        page.goto(base)
        page.wait_for_function('document.querySelectorAll(".album").length === 9')
        assert page.locator('#albums-panel').is_visible() and page.locator('#mini-player').is_hidden()
        names = ['Soprani', 'Contralti', 'Tenori', 'Bassi']
        # Every album is its cover alone (it carries the name): no captions, no visible headings.
        assert page.locator('#album-full svg.cover').evaluate_all('n => n.map(s => s.getAttribute("aria-label"))') == ['Christmas Carols']
        assert page.locator('#album-list svg.cover').evaluate_all('n => n.map(s => s.getAttribute("aria-label"))') == names + [f'{n} in evidenza' for n in names]
        assert page.evaluate("[...document.querySelectorAll('#albums-panel h1, #albums-panel h2')].every(h => h.matches('.sr-only') || [...h.children].every(c => c.matches('.sr-only')))")
        if shots: page.screenshot(path=f'{shots}/albums-{width}.png', full_page=True)
        # Christmas Carols: the whole choir, one plain track per song (no title, note or count-in).
        page.locator('.album').first.click(); view('playlist')
        assert page.locator('#playlist-title').inner_text() == 'Christmas Carols'
        assert page.evaluate("[...document.querySelectorAll('#playlist-tracks .song-meta')].every(d => /^\\d+:\\d\\d$/.test(d.textContent))")
        page.go_back(); view('albums')
        page.locator('.album').nth(7).click(); view('playlist')  # Tenori in evidenza
        assert page.locator('#playlist-title').inner_text() == 'Tenori in evidenza'
        titles = page.locator('#playlist-tracks .song-title').all_text_contents()
        assert titles[0].startswith('We Wish') and 'Joy to the World' in titles
        # The same rows as Spartiti, in a fixed order: no reordering.
        assert page.locator('#playlist-tracks li').first.locator('.song-num, .song-art svg, .song-meta').count() == 3
        assert page.locator('#playlist-tracks .grip').count() == 0
        page.locator('#playlist-play').click()
        page.wait_for_function('!document.getElementById("mini-player").hidden')
        assert page.locator('#mini-title').inner_text() == titles[0]
        assert page.locator('#mini-status').inner_text() == 'Tenori in evidenza'
        assert page.locator('#playlist-tracks .song-row[aria-current] .song-title').inner_text() == titles[0]
        page.locator('#mini-next').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal page scroll'
        if shots: page.screenshot(path=f'{shots}/playlist-{width}.png', full_page=True)
        # The PDF view: the same rows with tick boxes, select all, an action bar.
        page.locator('.tabs a', has_text='PDF').click(); view('booklet')
        assert page.locator('#booklet-list li').count() > 10 and page.locator('.make-bar').is_visible()
        assert page.locator('#booklet-make').is_disabled()
        page.locator('#booklet-list .song-check').first.check()
        assert page.locator('#booklet-status').inner_text() == '1 brano' and page.locator('#booklet-make').is_enabled()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal page scroll'
        # The playing playlist stays reachable in the lists; opening a score ends it.
        page.locator('.tabs a', has_text='Spartiti').click(); view('library')
        assert page.locator('#mini-player').is_visible()
        page.locator('#song-list .song-row').first.click(); view('practice')
        assert page.evaluate('Playlist.playing') is False and page.evaluate('Playlist.hasQueue') is False
        page.go_back(); view('library')
        assert page.locator('#mini-player').is_hidden()
        # A song with recorded parts plays the choir in the score; another key falls back to piano.
        page.locator('#song-list .song-row', has_text='Joy to the World').click()
        page.wait_for_function('song.id === "joy-to-the-world" && Object.keys(choirBuffers).length === 4', timeout=20000)
        page.locator('#play').click(); page.wait_for_function('choirVoices.size === 4', timeout=20000)
        if page.locator('#options-button').is_visible(): page.locator('#options-button').click()
        assert page.locator('#sound-control').is_visible() and page.locator('#sound-choir').get_attribute('aria-pressed') == 'true'
        page.locator('#transpose-up').click(); page.wait_for_function('choirVoices.size === 0', timeout=20000)
        if page.locator('#options-button').is_visible() and page.evaluate('!document.body.dataset.sheet'): page.locator('#options-button').click()
        assert 'Pianoforte' in page.locator('#voice-label').inner_text()
        page.locator('#transpose-down').click(); page.wait_for_function('choirVoices.size === 4', timeout=20000)
        if page.locator('#options-button').is_visible() and page.evaluate('!document.body.dataset.sheet'): page.locator('#options-button').click()
        page.locator('#slow').click(); page.wait_for_function('choirVoices.size === 4', timeout=30000)  # slowed choir, same voices
        assert page.locator('#slow').get_attribute('aria-pressed') == 'true'
        page.locator('#play').click()
        page.context.close()
    assert not errors, errors
    browser.close()
print('PASS: cover-only albums (solo and in evidenza), one track per song, shared rows in a fixed order, mini player, history back, '
      'PDF view, score/recording exclusivity, choir in the score with piano fallback and Lento at 320/390/1280px')

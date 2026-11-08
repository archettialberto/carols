/* Interface language is independent of the original sung lyrics. */
const messages = {
  it: {
    audioBlocked:'L’audio è bloccato dal browser: tocca di nuovo Ascolta, disattiva il silenzioso e alza il volume.',
    verseShort:'Str. {n}', downloadPDF:'Scarica il PDF dello spartito',
    transpose:'Trasposizione', semitones:'{n} semitoni', semitone:'{n} semitono', originalKey:'0 · originale',
    close:'Chiudi', changeSelection:'Cambia brano, strofa o voce',
    keyHint:'Tieni premuto per sostenere; premi più tasti per l’accordo.', firstNoteOf:'Prima nota: {voice} {pitch}',
    intro:'Introduzione', interlude:'Interludio', coda:'Coda', install:'Aggiungi alla schermata Home',
    firstNote:'Prima nota', playFirstNote:'Ascolta la prima nota', stopFirstNote:'Ferma la nota', downloads:'Scarica PDF',
    leadSoprano:'Soprani in evidenza', leadAlto:'Contralti in evidenza', leadTenor:'Tenori in evidenza', leadBass:'Bassi in evidenza',
    scoreVersion:'Spartito', digitalScore:'Digitale', scannedScore:'Scansione originale', digitalPDF:'PDF digitale', digitalHTML:'Spartito digitale stampabile',

    theme:'Aspetto', themeSystem:'Dispositivo', themeLight:'Chiaro', themeDark:'Scuro',
    navigation:'Navigazione', library:'Brani', backToLibrary:'Torna ai brani', rehearse:'Prova', verseCount:'{n} strofe', verseOne:'1 strofa', selectedSong:'Brano selezionato',
    lyricVoice:'Testo della voce', language:'Lingua', selection:'Brano e voci', song:'Brano', verse:'Strofa', allVerses:'Tutte le strofe',
    listen:'Ascolta', allVoices:'Tutte le voci', custom:'Mix personalizzato', mix:'Voci del mix',
    soprano:'Soprano', alto:'Contralto', tenor:'Tenore', bass:'Basso', soloSoprano:'Solo soprani', soloAlto:'Solo contralti', soloTenor:'Solo tenori', soloBass:'Solo bassi', loading:'Caricamento…',
    practice:'Spartito e testo', previousLine:'Rigo precedente', nextLine:'Rigo successivo',
    noteHint:'Tocca una nota per iniziare da lì.', scoreScroll:'Spartito: scorri orizzontalmente', scoreHint:'Tocca una battuta per iniziare da lì.',
    zoomOut:'Riduci spartito', zoomIn:'Ingrandisci spartito', summaryOptions:'Opzioni',
    measureStart:'Vai alla battuta', follow:'Scorri con la musica',
    markerNote:'Note e testo seguono la riproduzione. Nella scansione, la posizione del cursore è approssimativa.',
    about:'Trascrizione', playback:'Riproduzione', restart:'Ricomincia', tempo:'Tempo', ready:'Pronto',
    seek:'Posizione di riproduzione', play:'Ascolta', pause:'Pausa',
    measure:'Battuta {n}', stanza:'Strofa {n} di {total}', line:'Rigo {n} di {total}',
    chorus:'Ritornello', verseSection:'Strofa', return:'ripresa', finished:'fine',
    lyrics:'Testo · {stanza}', noLyrics:'Pausa', arranged:'arrangiamento di',
    original:'PDF originale', xml:'MusicXML', midi:'MIDI', openLine:'Vai al rigo {n}',
    selectVoice:'Scegli almeno una voce.', audioError:'Impossibile avviare l’audio: {error}',
    loadError:'Impossibile caricare i brani.', noScores:'Nessuno spartito disponibile.',
  },
};
// The practice interface is intentionally Italian-only; sung lyrics keep their
// original language because they come from each score, not this dictionary.
const language = 'it';
function t(key, values = {}) {
  return Object.entries(values).reduce((text, [name, value]) => text.replaceAll(`{${name}}`, value), messages[language][key] || key);
}
function translatePage() {
  document.documentElement.lang = language;
  document.querySelectorAll('[data-i18n]').forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll('[data-label]').forEach(el => el.setAttribute('aria-label', t(el.dataset.label)));
}

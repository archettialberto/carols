/* A small pool of synthesized instruments. Everything is generated with Web Audio:
   no samples, downloads or network. Each note returns a handle with stop()/release(). */
const Sounds = (() => {
  const list = ['piano', 'organ', 'choir', 'synth'];
  const waves = new WeakMap();

  function periodic(ctx, name) {
    let cache = waves.get(ctx);
    if (!cache) { cache = {}; waves.set(ctx, cache); }
    if (cache[name]) return cache[name];
    // Harmonic amplitudes, index = partial number.
    const spectra = {
      piano: [0, 1, .55, .32, .22, .12, .08, .05, .035, .02, .012],
      organ: [0, 1, .7, .35, .45, 0, .22, 0, .3, 0, 0, 0, .12, 0, 0, 0, .08],
    };
    const amps = spectra[name], real = new Float32Array(amps.length), imag = Float32Array.from(amps);
    return cache[name] = ctx.createPeriodicWave(real, imag);
  }

  function envelope(gain, kind, start, duration, level) {
    const end = start + duration, g = gain.gain;
    g.setValueAtTime(0, start);
    if (kind === 'piano') {
      g.linearRampToValueAtTime(level * 1.5, start + .005);
      g.setTargetAtTime(level * .35, start + .005, .35);
      g.setTargetAtTime(0, end, .06);
      return end + .35;
    }
    const attack = {organ:.012, choir:.07, synth:.015}[kind];
    const release = {organ:.04, choir:.12, synth:.04}[kind];
    const peak = start + Math.min(attack, duration / 3);
    g.linearRampToValueAtTime(level, peak);
    g.setValueAtTime(level, Math.max(peak, end - release * .3));
    g.setTargetAtTime(0, end - release * .3, release / 3);
    return end + release * 1.5;
  }

  function play(ctx, destination, {midi, start, duration, kind = 'piano', level = .11}) {
    const frequency = 440 * 2 ** ((midi - 69) / 12);
    const nodes = [], sources = [];
    const out = ctx.createGain(); out.connect(destination); nodes.push(out);
    const source = ctx.createOscillator(); sources.push(source); nodes.push(source);
    source.frequency.value = frequency;
    let stopAt;
    if (kind === 'choir') {
      // A sung "aah": sawtooth through vowel formants, with gentle delayed vibrato.
      source.type = 'sawtooth';
      const lfo = ctx.createOscillator(), depth = ctx.createGain();
      lfo.frequency.value = 5.2; depth.gain.setValueAtTime(0, start);
      depth.gain.linearRampToValueAtTime(frequency * .006, start + Math.min(.35, duration));
      lfo.connect(depth); depth.connect(source.frequency); sources.push(lfo); nodes.push(lfo, depth);
      [[800, 1, 8], [1150, .55, 11], [2900, .28, 14]].forEach(([centre, amp, q]) => {
        const band = ctx.createBiquadFilter(); band.type = 'bandpass'; band.Q.value = q; band.frequency.value = centre;
        const g = ctx.createGain(); g.gain.value = amp * 3.2;
        source.connect(band); band.connect(g); g.connect(out); nodes.push(band, g);
      });
      stopAt = envelope(out, kind, start, duration, level * .9);
    } else if (kind === 'synth') {
      source.type = 'triangle';
      source.connect(out); stopAt = envelope(out, kind, start, duration, level);
    } else {
      source.setPeriodicWave(periodic(ctx, kind));
      const tone = ctx.createBiquadFilter(); tone.type = 'lowpass'; nodes.push(tone);
      if (kind === 'piano') {
        // Bright hammer attack that mellows as the string decays.
        tone.frequency.setValueAtTime(Math.min(12000, frequency * 14), start);
        tone.frequency.setTargetAtTime(Math.min(5000, frequency * 4), start, .25);
      } else tone.frequency.value = 7000;
      source.connect(tone); tone.connect(out);
      stopAt = envelope(out, kind, start, duration, level * (kind === 'organ' ? .75 : 1));
    }
    for (const s of sources) s.start(start);
    for (const s of sources) s.stop(stopAt);
    const handle = {
      frequency, kind, onended:null,
      stop() { for (const s of sources) { try { s.stop(); } catch (_) {} } },
      // Let go of a held key: keep the envelope until `at` (possibly in the future), then fade.
      release(at = ctx.currentTime) {
        if (out.gain.cancelAndHoldAtTime) out.gain.cancelAndHoldAtTime(at); else out.gain.cancelScheduledValues(at);
        out.gain.setTargetAtTime(0, at, kind === 'piano' ? .08 : .05);
        for (const s of sources) { try { s.stop(at + .45); } catch (_) {} }
      },
    };
    source.onended = () => { nodes.forEach(n => { try { n.disconnect(); } catch (_) {} }); handle.onended?.(); };
    return handle;
  }
  return {list, play};
})();

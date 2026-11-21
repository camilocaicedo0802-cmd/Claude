/* Lógica del regalo. El contenido vive en contenido.js; aquí no hay nada que personalizar. */
(() => {
  'use strict';

  const R = window.REGALO || {};
  const OPC = window.REGALO_OPCIONES || {};
  const d = document;
  const raiz = d.documentElement;
  const $ = (s, c = d) => c.querySelector(s);
  const $$ = (s, c = d) => Array.from(c.querySelectorAll(s));
  const quieto = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  raiz.classList.add('js');

  // ── Utilidades ───────────────────────────────────────────────────
  const CORA_D = 'M50 86C20 62 4 44 4 27 4 13 15 4 27 4c9 0 18 5 23 14C55 9 64 4 73 4c12 0 23 9 23 23 0 17-16 35-46 59Z';
  const ICO = {
    play: '<path d="M8.5 5.2v13.6L19.5 12z"/>',
    pausa: '<path d="M7 5h3.6v14H7zM13.4 5H17v14h-3.6z"/>',
    micro: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3"/>',
    pin: '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11Z"/><circle cx="12" cy="10" r="2.3"/>',
    calendario: '<rect x="4" y="5.5" width="16" height="14" rx="2.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
    izq: '<path d="M14.5 6l-6 6 6 6"/>',
    der: '<path d="M9.5 6l6 6-6 6"/>',
    cerrar: '<path d="M6 6l12 12M18 6L6 18"/>',
    tijera: '<circle cx="6.5" cy="7" r="2.5"/><circle cx="6.5" cy="17" r="2.5"/><path d="M8.6 8.4L20 18M8.6 15.6L20 6"/>'
  };
  const ico = (n) => `<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">${ICO[n]}</svg>`;
  const lleno = (n) => `<svg viewBox="0 0 24 24" aria-hidden="true">${ICO[n]}</svg>`;
  const cora = () => `<svg class="cora" viewBox="0 0 100 90" aria-hidden="true"><path d="${CORA_D}"/></svg>`;

  function el(tag, cls, txt) {
    const e = d.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  /* Escribe `txt` en `nodo`; lo que va entre *asteriscos* queda resaltado en itálica. */
  function rico(nodo, txt) {
    String(txt == null ? '' : txt).split(/\*([^*]+)\*/).forEach((trozo, i) => {
      if (!trozo) return;
      nodo.append(i % 2 ? el('em', '', trozo) : trozo);
    });
    return nodo;
  }
  const elr = (tag, cls, txt) => rico(el(tag, cls), txt);
  const liso = (txt) => String(txt == null ? '' : txt).replace(/\*([^*]+)\*/g, '$1');
  const azar = (a, b) => a + Math.random() * (b - a);
  const css = (n) => getComputedStyle(raiz).getPropertyValue(n).trim();
  function vibrar(p) { try { if (navigator.vibrate) navigator.vibrate(p); } catch (e) { /* sin vibración */ } }

  const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function leerFecha(s) {
    const m = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(String(s || '').trim());
    return m ? { a: +m[1], m: +m[2], d: +m[3] } : null;
  }
  function fechaLarga(s) {
    const f = leerFecha(s);
    return f ? `${f.d} de ${MESES[f.m - 1]} de ${f.a}` : String(s || '');
  }
  function diasDesde(s) {
    const f = leerFecha(s);
    if (!f) return null;
    const h = new Date();
    return Math.round((Date.UTC(h.getFullYear(), h.getMonth(), h.getDate()) - Date.UTC(f.a, f.m - 1, f.d)) / 864e5);
  }
  function reloj(seg) {
    const s = Math.max(0, Math.floor(seg || 0));
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  }

  /* Corazoncitos que salen disparados desde el centro de `padre`. */
  function chispas(padre, n, rMin, rMax, ms = 1000) {
    if (quieto) return;
    const caja = el('span', 'chispas');
    caja.setAttribute('aria-hidden', 'true');
    for (let i = 0; i < n; i++) {
      const c = el('i');
      const ang = (i / n) * Math.PI * 2 + azar(-0.4, 0.4);
      const r = azar(rMin, rMax);
      c.style.setProperty('--tx', `${(Math.cos(ang) * r).toFixed(1)}px`);
      c.style.setProperty('--ty', `${(Math.sin(ang) * r - r * 0.25).toFixed(1)}px`);
      c.style.setProperty('--s', `${azar(8, 17).toFixed(1)}px`);
      c.style.setProperty('--g', `${azar(-35, 35).toFixed(0)}deg`);
      c.style.setProperty('--d', `${(ms * azar(0.75, 1.1)).toFixed(0)}ms`);
      caja.append(c);
    }
    padre.append(caja);
    setTimeout(() => caja.remove(), ms * 1.2 + 100);
  }

  // ── Textos sueltos y adornos ─────────────────────────────────────
  $$('[data-t]').forEach((n) => { n.textContent = ''; rico(n, R[n.dataset.t] || R[n.dataset.alt] || ''); });
  $$('[data-cora]').forEach((n) => { n.innerHTML = cora(); });
  $$('.flotantes').forEach((caja) => {
    const n = +caja.dataset.flotantes || 8;
    for (let i = 0; i < n; i++) {
      const c = el('i');
      const dur = azar(11, 20);
      c.style.setProperty('--x', `${azar(4, 94).toFixed(1)}%`);
      c.style.setProperty('--s', `${azar(7, 15).toFixed(1)}px`);
      c.style.setProperty('--o', azar(0.1, 0.3).toFixed(2));
      c.style.setProperty('--dx', `${azar(-40, 40).toFixed(0)}px`);
      c.style.setProperty('--d', `${dur.toFixed(1)}s`);
      c.style.setProperty('--r', `${(-azar(0, dur)).toFixed(1)}s`);
      caja.append(c);
    }
  });

  const pagina = $('#pagina');
  const sonidos = [];
  const soloUno = (a) => sonidos.forEach((x) => { if (x !== a && !x.paused) x.pause(); });

  // ── Portada ──────────────────────────────────────────────────────
  (() => {
    const foto = $('#portadaFoto');
    if (R.portada && R.portada.foto) foto.src = R.portada.foto;
    const meta = [R.de ? `De ${R.de}` : '', leerFecha(R.fechaInicio) ? fechaLarga(R.fechaInicio) : ''].filter(Boolean);
    $('#portadaMeta').textContent = meta.join(' · ');
  })();

  // ── Nuestra canción ──────────────────────────────────────────────
  const musica = (() => {
    const c = R.cancion || {};
    const seccion = $('#cancion');
    if (!c.archivo && !c.spotify) { seccion.hidden = true; return { sonar() {}, audio: null }; }

    const disco = $('#disco');
    const boton = $('#discoBoton');
    $('#discoFoto').src = c.foto || (R.portada && R.portada.foto) || '';
    const meta = [c.titulo, c.artista].filter(Boolean).join(' · ');
    $('#cancionMeta').textContent = meta;
    $('#cancionMeta').hidden = !meta;

    let audio = null;
    if (c.archivo) {
      audio = new Audio();
      audio.preload = 'none';
      audio.loop = true;
      audio.src = c.archivo;
      sonidos.push(audio);
      const pinta = () => {
        const suena = !audio.paused;
        disco.classList.toggle('disco--sonando', suena);
        boton.innerHTML = lleno(suena ? 'pausa' : 'play');
        boton.setAttribute('aria-label', suena ? 'Pausar nuestra canción' : 'Reproducir nuestra canción');
      };
      audio.addEventListener('play', () => { soloUno(audio); pinta(); });
      audio.addEventListener('pause', pinta);
      audio.addEventListener('error', () => { boton.hidden = true; disco.classList.remove('disco--sonando'); disco.classList.add('disco--adorno'); });
      boton.addEventListener('click', () => {
        if (audio.paused) { const p = audio.play(); if (p && p.catch) p.catch(() => {}); } else audio.pause();
      });
      pinta();
    } else {
      boton.hidden = true;
      disco.classList.add('disco--adorno');
    }

    const m = /open\.spotify\.com\/(?:intl-[a-z-]+\/)?(track|album|playlist|episode)\/([A-Za-z0-9]+)/.exec(c.spotify || '');
    if (m) {
      const caja = $('#cancionSpotify');
      caja.hidden = false;
      if (OPC.sinIncrustados) {
        const a = el('a', 'boton-claro', 'Escuchar en Spotify');
        a.href = `https://open.spotify.com/${m[1]}/${m[2]}`;
        a.target = '_blank';
        a.rel = 'noopener';
        caja.append(a);
      } else {
        const marco = d.createElement('iframe');
        marco.src = `https://open.spotify.com/embed/${m[1]}/${m[2]}?utm_source=generator`;
        marco.title = 'Nuestra canción en Spotify';
        marco.loading = 'lazy';
        marco.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
        caja.append(marco);
      }
    }

    return {
      audio,
      sonar() {
        if (!audio || c.sonarAlAbrir === false) return;
        const p = audio.play();
        if (p && p.catch) p.catch(() => {});
      }
    };
  })();

  // ── Galería ──────────────────────────────────────────────────────
  (() => {
    const g = R.galeria || {};
    const fotos = (g.fotos || []).filter((f) => f && f.src);
    const seccion = $('.galeria');
    if (!fotos.length) { seccion.hidden = true; return; }
    rico($('#galeriaTitulo'), g.titulo || 'Momentos que *no se borran*');

    const carrusel = $('#carrusel');
    const puntos = $('#fotoPuntos');
    const antes = $('#fotoAnterior');
    const despues = $('#fotoSiguiente');
    antes.innerHTML = ico('izq');
    despues.innerHTML = ico('der');

    const tarjetas = fotos.map((f, i) => {
      const fig = el('figure', 'foto');
      const img = el('img');
      img.src = f.src;
      img.alt = f.alt || '';
      img.loading = i < 2 ? 'eager' : 'lazy';
      img.decoding = 'async';
      img.draggable = false;
      fig.append(img, el('span', 'foto__n', `${i + 1} / ${fotos.length}`));
      carrusel.append(fig);
      puntos.append(el('i'));
      return fig;
    });

    let actual = -1;
    function marcar() {
      const centro = carrusel.scrollLeft + carrusel.clientWidth / 2;
      let mejor = 0;
      let dist = Infinity;
      tarjetas.forEach((t, i) => {
        const dd = Math.abs(t.offsetLeft + t.offsetWidth / 2 - centro);
        if (dd < dist) { dist = dd; mejor = i; }
      });
      if (mejor === actual) return;
      actual = mejor;
      $$('i', puntos).forEach((p, i) => p.classList.toggle('activo', i === actual));
      antes.disabled = actual === 0;
      despues.disabled = actual === tarjetas.length - 1;
    }
    function ir(i) {
      const t = tarjetas[Math.max(0, Math.min(tarjetas.length - 1, i))];
      carrusel.scrollTo({ left: t.offsetLeft - (carrusel.clientWidth - t.offsetWidth) / 2, behavior: quieto ? 'auto' : 'smooth' });
    }
    let cuadro = 0;
    carrusel.addEventListener('scroll', () => {
      if (cuadro) return;
      cuadro = requestAnimationFrame(() => { cuadro = 0; marcar(); });
    }, { passive: true });
    antes.addEventListener('click', () => ir(actual - 1));
    despues.addEventListener('click', () => ir(actual + 1));
    carrusel.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); ir(actual + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); ir(actual - 1); }
    });
    window.addEventListener('resize', marcar);
    marcar();
  })();

  // ── Carta ────────────────────────────────────────────────────────
  (() => {
    const c = R.carta || {};
    const parrafos = (c.parrafos || []).filter(Boolean);
    if (!parrafos.length) { $('.carta').hidden = true; return; }
    const cuerpo = $('#cartaCuerpo');
    if (c.saludo) cuerpo.append(el('p', 'carta__saludo aparece', liso(c.saludo)));
    parrafos.forEach((p) => cuerpo.append(elr('p', 'aparece', p)));
    if (c.despedida) cuerpo.append(elr('p', 'aparece', c.despedida));
    if (R.de) {
      const firma = el('p', 'carta__firma aparece');
      firma.append(el('span', '', R.de));
      firma.insertAdjacentHTML('beforeend', cora());
      cuerpo.append(firma, el('p', 'carta__raya aparece', `— ${R.de}`));
    }
  })();

  // ── Línea del tiempo ─────────────────────────────────────────────
  (() => {
    const r = R.recuerdos || {};
    rico($('#recuerdosTitulo'), r.titulo || 'Nuestra *línea del tiempo*');

    const dias = diasDesde(R.fechaInicio);
    const caja = $('.contador');
    const numero = $('#contadorNumero');
    if (dias == null || dias < 0) {
      caja.hidden = true;
    } else {
      const formato = (n) => String(Math.round(n));
      numero.textContent = formato(dias);
      $('#contadorRotulo').textContent = dias === 1 ? 'Día contigo' : 'Días contigo';
      $('#contadorDesde').textContent = `desde el ${fechaLarga(R.fechaInicio)}`;
      if (!quieto && 'IntersectionObserver' in window) {
        const ojo = new IntersectionObserver((es) => {
          if (!es.some((e) => e.isIntersecting)) return;
          ojo.disconnect();
          const t0 = performance.now();
          const dur = 1500;
          const paso = (t) => {
            const k = Math.min(1, (t - t0) / dur);
            numero.textContent = formato(dias * (1 - Math.pow(1 - k, 4)));
            if (k < 1) requestAnimationFrame(paso);
          };
          requestAnimationFrame(paso);
        }, { threshold: 0.6 });
        ojo.observe(caja);
      }
    }

    const inicio = $('#recuerdosInicio');
    if (r.lugarInicio) { inicio.innerHTML = ico('pin'); inicio.append(el('span', '', r.lugarInicio)); } else inicio.hidden = true;

    const linea = $('#linea');
    const momentos = (r.momentos || []).filter((m) => m && m.titulo);
    if (!momentos.length) linea.hidden = true;
    momentos.forEach((m) => {
      const li = el('li', 'momento aparece');
      const img = el('img', 'momento__foto');
      img.src = m.foto || (R.portada && R.portada.foto) || '';
      img.alt = '';
      img.loading = 'lazy';
      const cuerpo = el('div');
      if (m.fecha) {
        const f = el('p', 'momento__fecha');
        f.innerHTML = ico('calendario');
        f.append(el('span', '', fechaLarga(m.fecha)));
        cuerpo.append(f);
      }
      cuerpo.append(elr('h3', 'momento__titulo', m.titulo));
      if (m.texto) cuerpo.append(elr('p', 'momento__texto', m.texto));
      li.append(img, cuerpo);
      linea.append(li);
    });
  })();

  // ── Mensaje de voz ───────────────────────────────────────────────
  (() => {
    const v = R.voz || {};
    const caja = $('#voz');
    if (!v.archivo) return;
    caja.hidden = false;
    $('.voz__micro', caja).innerHTML = ico('micro');

    const ondas = $('#vozOndas');
    const boton = $('#vozBoton');
    const avance = $('#vozAvance');
    const tiempo = $('#vozTiempo');
    const N = 46;

    const audio = new Audio();
    audio.preload = 'metadata';
    audio.src = v.archivo;
    sonidos.push(audio);

    // Barras de arranque (parecen una voz) hasta que se lee el audio de verdad.
    let semilla = 7;
    const ruido = () => { semilla = (semilla * 16807) % 2147483647; return semilla / 2147483647; };
    let barras = [];
    function dibujar(picos) {
      if (!barras.length) {
        barras = picos.map(() => { const b = el('i'); ondas.append(b); return b; });
      }
      picos.forEach((h, i) => barras[i].style.setProperty('--h', Math.max(0.12, Math.min(1, h)).toFixed(3)));
    }
    dibujar(Array.from({ length: N }, (_, i) => 0.25 + 0.6 * Math.abs(Math.sin(i * 0.55)) * (0.5 + 0.5 * ruido())));

    // La forma real de la voz se lee cuando la tarjeta está por entrar en pantalla.
    const AC = window.AudioContext || window.webkitAudioContext;
    function leerOndas() {
      if (!AC || !window.fetch) return;
      fetch(v.archivo)
        .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('sin audio'))))
        .then((buf) => {
          const ctx = new AC();
          return new Promise((ok, mal) => ctx.decodeAudioData(buf, ok, mal)).then((ab) => {
            const datos = ab.getChannelData(0);
            const tramo = Math.floor(datos.length / N) || 1;
            const picos = [];
            for (let i = 0; i < N; i++) {
              let suma = 0;
              for (let j = i * tramo; j < (i + 1) * tramo; j += 8) suma += datos[j] * datos[j];
              picos.push(Math.sqrt(suma / (tramo / 8)));
            }
            const max = Math.max.apply(null, picos) || 1;
            dibujar(picos.map((p) => 0.12 + 0.88 * Math.pow(p / max, 0.7)));
            if (ctx.close) ctx.close();
          });
        })
        .catch(() => { /* se quedan las barras de arranque */ });
    }
    if ('IntersectionObserver' in window) {
      const ojo = new IntersectionObserver((es) => {
        if (!es.some((e) => e.isIntersecting)) return;
        ojo.disconnect();
        leerOndas();
      }, { rootMargin: '700px 0px' });
      ojo.observe(caja);
    } else {
      leerOndas();
    }

    let volver = false;
    let cuadro = 0;
    function pinta() {
      const dur = audio.duration && isFinite(audio.duration) ? audio.duration : 0;
      const p = dur ? Math.min(1, audio.currentTime / dur) : 0;
      const hasta = Math.round(p * N);
      barras.forEach((b, i) => b.classList.toggle('oida', i < hasta));
      avance.style.setProperty('--p', p.toFixed(4));
      const enReposo = audio.paused && audio.currentTime < 0.05;
      tiempo.textContent = reloj(enReposo ? dur : audio.currentTime);
      ondas.setAttribute('aria-valuenow', String(Math.round(p * 100)));
    }
    function bucle() { pinta(); cuadro = audio.paused ? 0 : requestAnimationFrame(bucle); }
    function estado() {
      const suena = !audio.paused;
      boton.innerHTML = lleno(suena ? 'pausa' : 'play');
      boton.setAttribute('aria-label', suena ? 'Pausar mensaje de voz' : 'Reproducir mensaje de voz');
      if (suena && !cuadro) bucle();
      pinta();
    }
    audio.addEventListener('play', () => {
      volver = volver || !!(musica.audio && !musica.audio.paused);
      soloUno(audio);
      estado();
    });
    audio.addEventListener('pause', estado);
    audio.addEventListener('loadedmetadata', pinta);
    audio.addEventListener('ended', () => {
      audio.currentTime = 0;
      estado();
      if (volver && musica.audio) { const p = musica.audio.play(); if (p && p.catch) p.catch(() => {}); }
      volver = false;
    });
    audio.addEventListener('error', () => { caja.hidden = true; });
    boton.addEventListener('click', () => {
      if (audio.paused) { const p = audio.play(); if (p && p.catch) p.catch(() => {}); } else audio.pause();
    });

    function buscar(x) {
      const r = ondas.getBoundingClientRect();
      const dur = audio.duration && isFinite(audio.duration) ? audio.duration : 0;
      if (!dur) return;
      audio.currentTime = Math.max(0, Math.min(0.999, (x - r.left) / r.width)) * dur;
      pinta();
    }
    let arrastra = false;
    ondas.addEventListener('pointerdown', (e) => { arrastra = true; buscar(e.clientX); });
    window.addEventListener('pointermove', (e) => { if (arrastra) buscar(e.clientX); });
    window.addEventListener('pointerup', () => { arrastra = false; });
    window.addEventListener('pointercancel', () => { arrastra = false; });
    ondas.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault();
      audio.currentTime = Math.max(0, Math.min((audio.duration || 0) - 0.1, audio.currentTime + (e.key === 'ArrowRight' ? 2 : -2)));
      pinta();
    });
    estado();
  })();

  // ── Mapa de lugares ──────────────────────────────────────────────
  (() => {
    const l = R.lugares || {};
    const puntos = (l.puntos || []).filter((p) => p && p.nombre);
    const seccion = $('.lugares');
    if (!puntos.length) { seccion.hidden = true; return; }
    rico($('#lugaresTitulo'), l.titulo || 'El mapa de *nuestra historia*');
    rico($('#lugaresTexto'), l.texto || '');

    const lista = $('#lugaresLista');
    const caja = $('.mapa');
    const conSitio = (p) => typeof p.lat === 'number' && typeof p.lng === 'number';
    let mapa = null;
    let marcadores = [];
    let hayTeselas = false;
    let activo = -1;

    const tarjetas = puntos.map((p, i) => {
      const li = el('li', 'aparece');
      const b = el('button', 'lugar');
      b.type = 'button';
      const cuerpo = el('span', 'lugar__cuerpo');
      const cabeza = el('span', 'lugar__cabeza');
      cabeza.append(el('span', 'lugar__nombre', liso(p.nombre)));
      if (p.cuando) cabeza.append(el('span', 'lugar__cuando', p.cuando));
      cuerpo.append(cabeza);
      if (p.texto) cuerpo.append(el('span', 'lugar__texto', liso(p.texto)));
      if (p.direccion) {
        const dir = el('span', 'lugar__dir');
        dir.innerHTML = ico('pin');
        dir.append(el('span', '', p.direccion));
        cuerpo.append(dir);
      }
      b.append(el('span', 'lugar__n', String(i + 1)), cuerpo);
      b.addEventListener('click', () => elegir(i, false));
      li.append(b);
      lista.append(li);
      return b;
    });

    function elegir(i, desdeMapa) {
      activo = i;
      tarjetas.forEach((t, k) => {
        t.classList.toggle('lugar--activo', k === i);
        t.setAttribute('aria-pressed', k === i ? 'true' : 'false');
      });
      caja.classList.add('mapa--tocado');
      marcadores.forEach((m, k) => {
        if (!m) return;
        const nodo = m.getElement();
        if (nodo) nodo.classList.toggle('pin--activo', k === i);
        m.setZIndexOffset(k === i ? 1000 : 0);
        if (k === i) m.openTooltip(); else m.closeTooltip();
      });
      const p = puntos[i];
      if (desdeMapa) {
        tarjetas[i].scrollIntoView({ block: 'nearest', behavior: quieto ? 'auto' : 'smooth' });
      } else if (mapa && conSitio(p)) {
        const r = caja.getBoundingClientRect();
        if (r.top < 0 || r.bottom > window.innerHeight) caja.scrollIntoView({ block: 'start', behavior: quieto ? 'auto' : 'smooth' });
        const meta = hayTeselas ? 12 : 5.5;
        mapa.flyTo([p.lat, p.lng], Math.max(mapa.getZoom(), meta), { duration: quieto ? 0 : 1.2 });
      }
    }

    function crear() {
      const sitios = puntos.filter(conSitio);
      if (!window.L || !sitios.length) { caja.hidden = true; return; }
      const L = window.L;
      const sinTeselas = !!OPC.sinTeselas;
      mapa = L.map('mapa', {
        zoomControl: true,
        scrollWheelZoom: false,
        dragging: !L.Browser.mobile,
        minZoom: 1,
        maxZoom: sinTeselas ? 8 : 17,
        zoomSnap: 0.25,
        maxBounds: [[-78, -220], [86, 220]],
        maxBoundsViscosity: 0.9
      });
      mapa.attributionControl.setPrefix(false);

      if (window.REGALO_TIERRA) {
        mapa.createPane('tierra').style.zIndex = 150;
        L.geoJSON({ type: 'Feature', properties: {}, geometry: window.REGALO_TIERRA }, {
          pane: 'tierra',
          interactive: false,
          style: { color: css('--costa'), weight: 1, fillColor: css('--tierra'), fillOpacity: 1 }
        }).addTo(mapa);
      }
      if (!sinTeselas) {
        const teselas = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
          subdomains: 'abcd',
          maxZoom: 20,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a>'
        });
        teselas.on('tileload', () => { hayTeselas = true; });
        teselas.on('tileerror', (e) => { if (e.tile) e.tile.style.visibility = 'hidden'; });
        teselas.addTo(mapa);
      } else {
        mapa.attributionControl.addAttribution('Natural Earth');
      }

      const forma = '<svg viewBox="0 0 32 42" aria-hidden="true"><path d="M16 40.5C16 40.5 2.5 25.8 2.5 15.5a13.5 13.5 0 0 1 27 0C29.5 25.8 16 40.5 16 40.5Z"/></svg>';
      marcadores = puntos.map((p, i) => {
        if (!conSitio(p)) return null;
        const m = L.marker([p.lat, p.lng], {
          icon: L.divIcon({ className: 'pin', html: `<span class="pin__cuerpo">${forma}<b>${i + 1}</b></span>`, iconSize: [32, 42], iconAnchor: [16, 41] }),
          title: liso(p.nombre),
          alt: liso(p.nombre),
          riseOnHover: true
        }).addTo(mapa);
        m.bindTooltip(liso(p.nombre), { direction: 'top', offset: [0, -42], className: 'pin-nombre', opacity: 1 });
        m.on('click', () => elegir(i, true));
        return m;
      });

      const limites = L.latLngBounds(sitios.map((p) => [p.lat, p.lng]));
      mapa.fitBounds(limites, { padding: [44, 44], maxZoom: sinTeselas ? 6 : 13, animate: false });
      if (activo >= 0) elegir(activo, true);
    }

    if ('IntersectionObserver' in window) {
      const ojo = new IntersectionObserver((es) => {
        if (!es.some((e) => e.isIntersecting)) return;
        ojo.disconnect();
        crear();
      }, { rootMargin: '500px 0px' });
      ojo.observe(caja);
    } else {
      crear();
    }
  })();

  // ── Cierre ───────────────────────────────────────────────────────
  (() => {
    const f = R.final || {};
    const foto = $('#cierreFoto');
    if (f.foto) foto.src = f.foto;
    else { $('.cierre__foto').hidden = true; $('.cierre').classList.add('cierre--sin-foto'); }
    $('#cierreFrase').textContent = liso(f.frase);
  })();

  // ── Última sorpresa: preguntas y vale ────────────────────────────
  (() => {
    const s = R.sorpresa || {};
    const preguntas = (s.preguntas || []).filter((q) => q && q.pregunta && (q.opciones || []).length);
    const tarjeta = $('.sorpresa');
    if (!s.vale && !preguntas.length) { tarjeta.hidden = true; return; }

    const caja = $('#juego');
    const escena = $('#juegoEscena');
    const abrirB = $('#sorpresaAbrir');
    const abrirT = $('#sorpresaAbrirTexto');
    const cerrarB = $('#juegoCerrar');
    cerrarB.innerHTML = ico('cerrar');

    const CLAVE = 'regalo:vale';
    let ganado = false;
    try { ganado = localStorage.getItem(CLAVE) === '1'; } catch (e) { /* sin memoria */ }
    const rotular = () => { abrirT.textContent = ganado ? 'Ver mi vale' : 'Descubrir la sorpresa'; };
    rotular();

    let espera = 0;
    function abrir() {
      caja.hidden = false;
      raiz.classList.add('fijo');
      pagina.inert = true;
      caja.scrollTop = 0;
      if (ganado || !preguntas.length) vale(); else pregunta(0);
      cerrarB.focus({ preventScroll: true });
    }
    function cerrar() {
      clearTimeout(espera);
      caja.hidden = true;
      raiz.classList.remove('fijo');
      pagina.inert = false;
      escena.replaceChildren();
      abrirB.focus({ preventScroll: true });
    }

    function pregunta(i) {
      const q = preguntas[i];
      const intro = elr('p', 'juego__intro', s.intro || 'Para descubrir mi última sorpresa tendrás que responder unas preguntas sobre nosotros.');
      const puntos = el('div', 'juego__puntos');
      puntos.setAttribute('aria-hidden', 'true');
      preguntas.forEach((_, k) => puntos.append(el('i', k < i ? 'hecha' : k === i ? 'activa' : '')));
      const hoja = el('div', 'pregunta tarjeta');
      hoja.append(el('p', 'rotulo', `Pregunta ${i + 1} de ${preguntas.length}`), elr('h2', 'pregunta__texto', q.pregunta));
      if (q.pista) hoja.append(elr('p', 'pregunta__pista', q.pista));
      const eco = el('div', 'juego__eco');
      eco.setAttribute('aria-live', 'polite');

      let resuelta = false;
      q.opciones.forEach((texto, k) => {
        const b = el('button', 'opcion', liso(texto));
        b.type = 'button';
        b.addEventListener('click', () => {
          if (resuelta || b.classList.contains('opcion--mal')) return;
          const bien = q.correcta === 'todas' || q.correcta == null || Number(q.correcta) === k;
          if (bien) {
            resuelta = true;
            b.classList.add('opcion--bien');
            eco.className = 'juego__eco';
            eco.innerHTML = `<span>¡Sí! ${cora()}</span>`;
            chispas(eco, 7, 28, 64, 900);
            vibrar(14);
            espera = setTimeout(() => (i + 1 < preguntas.length ? pregunta(i + 1) : logro()), quieto ? 600 : 1150);
          } else {
            b.classList.add('opcion--mal');
            b.setAttribute('aria-disabled', 'true');
            eco.className = 'juego__eco juego__eco--mal';
            eco.replaceChildren(el('span', '', 'Casi… inténtalo otra vez.'));
            vibrar([18, 50, 18]);
          }
        });
        hoja.append(b);
      });
      escena.replaceChildren(intro, puntos, hoja, eco);
    }

    function logro() {
      ganado = true;
      try { localStorage.setItem(CLAVE, '1'); } catch (e) { /* sin memoria */ }
      rotular();
      const bloque = el('div', 'logro');
      const titulo = el('h2', 'logro__titulo');
      rico(titulo, 'Lo *lograste*');
      titulo.insertAdjacentHTML('beforeend', cora());
      bloque.append(titulo, el('p', 'logro__texto', 'Esta era la última sorpresa que tenía preparada para ti.'));
      escena.replaceChildren(bloque);
      chispas(bloque, 18, 70, 190, 1600);
      vibrar([20, 60, 20, 60, 40]);
      espera = setTimeout(vale, quieto ? 1400 : 2600);
    }

    function vale() {
      const v = el('div', 'vale');
      const tijera = el('span', 'vale__tijera');
      tijera.innerHTML = ico('tijera');
      const texto = el('p', 'vale__texto');
      texto.innerHTML = cora();
      rico(texto, s.vale || '');
      v.append(tijera, el('p', 'rotulo rotulo--mini', 'Vale especial'), texto);
      if (R.de) v.append(el('p', 'vale__firma', `— ${R.de}`));
      const volver = el('button', 'boton-claro', 'Volver al regalo');
      volver.type = 'button';
      volver.addEventListener('click', cerrar);
      escena.replaceChildren(v, volver);
    }

    abrirB.addEventListener('click', abrir);
    cerrarB.addEventListener('click', cerrar);
    d.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !caja.hidden) cerrar(); });
  })();

  // ── Aparecer al hacer scroll ─────────────────────────────────────
  (() => {
    const piezas = $$('.aparece');
    if (quieto || !('IntersectionObserver' in window)) { piezas.forEach((p) => p.classList.add('visto')); return; }
    const ojo = new IntersectionObserver((es) => {
      es.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add('visto');
        ojo.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -7% 0px', threshold: 0.08 });
    piezas.forEach((p) => ojo.observe(p));
  })();

  // ── Puerta: el corazón que abre el regalo ────────────────────────
  (() => {
    const puerta = $('#puerta');
    const corazon = $('#corazon');
    const hueco = $('#puertaHueco');
    const latido = $('.corazon__latido', corazon);
    if (!puerta) return;

    const total = Math.max(2, Math.round(+R.toquesCorazon || 4));
    let toques = 0;
    let abriendo = false;

    raiz.classList.add('fijo');
    pagina.inert = true;
    window.scrollTo(0, 0);

    function colocar() {
      if (puerta.classList.contains('puerta--escena')) return;
      const p = puerta.getBoundingClientRect();
      const h = hueco.getBoundingClientRect();
      corazon.style.setProperty('--ix', `${(h.left + h.width / 2 - (p.left + p.width / 2)).toFixed(1)}px`);
      corazon.style.setProperty('--iy', `${(h.top + h.height / 2 - (p.top + p.height * 0.44)).toFixed(1)}px`);
    }
    colocar();
    requestAnimationFrame(() => requestAnimationFrame(() => puerta.classList.add('puerta--lista')));
    window.addEventListener('resize', colocar);
    window.addEventListener('load', colocar);
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(colocar);

    function abrir() {
      abriendo = true;
      musica.sonar();
      setTimeout(() => {
        window.scrollTo(0, 0);
        raiz.classList.remove('fijo');
        pagina.inert = false;
        pagina.classList.add('pagina--abierta');
        puerta.classList.add('puerta--abriendo');
        setTimeout(() => puerta.remove(), quieto ? 50 : 1400);
      }, quieto ? 0 : 560);
    }

    corazon.addEventListener('click', () => {
      if (abriendo) return;
      toques += 1;
      puerta.classList.add('puerta--escena');
      corazon.style.setProperty('--nivel', Math.min(1, toques / total).toFixed(3));
      latido.classList.remove('corazon__latido--golpe');
      void latido.offsetWidth;
      latido.classList.add('corazon__latido--golpe');
      chispas(corazon, 5 + toques, 80, 150, 1000);
      vibrar(toques >= total ? [16, 40, 30] : 12);
      if (toques >= total) abrir();
    });
  })();
})();

/* Group C: purely presentational behavior.
   This file never fetches, changes, estimates, or recomputes weather observations. */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const $ = (id) => document.getElementById(id);
    const root = document.documentElement;
    const hero = $('hero');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // The globe is a local illustrative asset; it never represents ERA5 results.
    // Presentation-only motion appears below; no climate values are computed.

    // Scroll-linked visual storytelling: these years and haze are a motion
    // metaphor for exploring the archive, NOT a plotted time series.
    if (!reduceMotion && hero && $('scroll-year')) {
      let raf = 0;
      function renderScroll() {
        raf = 0;
        const scrollLength = Math.max(1, hero.getBoundingClientRect().height * 0.84);
        const progress = Math.max(0, Math.min(1, window.scrollY / scrollLength));
        $('scroll-year').textContent = String(1940 + Math.round(86 * progress));
        hero.style.setProperty('--heat-intensity', String((progress * .28).toFixed(3)));
      }
      function onScroll() {
        if (!raf) raf = window.requestAnimationFrame(renderScroll);
      }
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
      renderScroll();
    }

    // Intersection Observer reveals. No-JS and reduced-motion users see
    // every section immediately.
    if (!reduceMotion && 'IntersectionObserver' in window) {
      const targets = document.querySelectorAll(
        '.intro-grid, .section-header, .stripe-legend, .stripes-surface, ' +
        '.result-grid, .chart-panel, .method-grid, .reproducibility, ' +
        '.source-grid, .timeline, .limits, .closing-flex'
      );
      const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: .075, rootMargin: '0px 0px -28px 0px' });
      targets.forEach(function (element) {
        element.classList.add('reveal');
        observer.observe(element);
      });
      root.classList.add('js-motion');
    }

    // The original renderer updates values using genuine cached results.
    // These classes only determine how hotter/cooler values are colored.
    const report = window.WEATHER_RESULTS;
    if (report && report.status === 'computed' &&
        Array.isArray(report.rates) && report.rates.length === 2 && report.difference) {
      const earlier = $('early-rate') && $('early-rate').closest('.result-card');
      const later = $('late-rate') && $('late-rate').closest('.result-card');
      const difference = $('diff-rate') && $('diff-rate').closest('.result-card');
      if (earlier) earlier.classList.add('is-cool');
      if (later) later.classList.add(report.rates[1].rate > report.rates[0].rate ? 'is-heat' : 'is-cool');
      if (difference) difference.classList.add(report.difference.observed_difference > 0 ? 'is-heat' : 'is-cool');
    }

    // One neutral slot for each year, 1940-2026. Optional year_stripes is a
    // display-only interface: the UI accepts only already verified precomputed
    // labels and colors; it does not derive anomalies or classify temperatures.
    const track = $('stripe-track');
    const readout = $('stripe-readout');
    const tooltip = $('stripe-tooltip');
    if (track && readout) {
      const startYear = 1940;
      const endYear = 2026;
      const count = endYear - startYear + 1;
      const safeColors = new Set([
        '#0B4F8A', '#2C99D6', '#BFE3F5', '#F8FAFC',
        '#F9B4AE', '#EB2F33', '#8E0F1E'
      ]);
      const verified = report && report.status === 'computed' &&
        Array.isArray(report.year_stripes) ? report.year_stripes : [];
      const byYear = new Map();
      verified.forEach(function (row) {
        if (row && Number.isInteger(row.year) && row.year >= startYear && row.year <= endYear &&
            typeof row.color === 'string' && safeColors.has(row.color.toUpperCase()) &&
            typeof row.label === 'string') {
          byYear.set(row.year, { color: row.color, label: row.label });
        }
      });
      const frag = document.createDocumentFragment();
      const elements = [];
      for (let year = startYear; year <= endYear; year++) {
        const span = document.createElement('span');
        span.className = 'stripe';
        span.setAttribute('aria-hidden', 'true');
        const entry = byYear.get(year);
        if (entry) {
          span.style.backgroundColor = entry.color;
          span.setAttribute('data-tone', 'verified');
        }
        elements.push(span);
        frag.appendChild(span);
      }
      track.appendChild(frag);
      let selected = startYear;
      function selectYear(year) {
        year = Math.max(startYear, Math.min(endYear, year));
        const prev = elements[selected - startYear];
        if (prev) prev.classList.remove('is-active');
        selected = year;
        elements[selected - startYear].classList.add('is-active');
        track.setAttribute('aria-valuenow', String(year));
        const entry = byYear.get(year);
        const text = entry ? entry.label : 'Annual color not available yet.';
        track.setAttribute('aria-valuetext', String(year) + '. ' + text);
        readout.querySelector('strong').textContent = String(year);
        readout.querySelector('span').textContent = text;
        if (tooltip) {
          $('stripe-tip-year').textContent = String(year);
          $('stripe-tip-label').textContent = text;
        }
      }
      function placeTooltip(clientX) {
        if (!tooltip) return;
        const surface = track.parentElement.getBoundingClientRect();
        const band = track.getBoundingClientRect();
        const localX = clientX - surface.left;
        const half = Math.min(119, Math.max(45, (surface.width - 24) / 2));
        tooltip.style.left = Math.min(surface.width - half, Math.max(half, localX)) + 'px';
        tooltip.style.top = (band.top - surface.top - 6) + 'px';
        tooltip.hidden = false;
      }
      function selectAtX(clientX) {
        const bounds = track.getBoundingClientRect();
        const fraction = Math.max(0, Math.min(1, (clientX - bounds.left) / bounds.width));
        selectYear(startYear + Math.min(count - 1, Math.floor(fraction * count)));
        placeTooltip(clientX);
      }
      track.addEventListener('pointermove', function (event) {
        if (event.pointerType === 'mouse' || event.buttons) selectAtX(event.clientX);
      });
      track.addEventListener('pointerdown', function (event) {
        selectAtX(event.clientX);
        track.focus({ preventScroll: true });
      });
      track.addEventListener('pointerleave', function () {
        if (tooltip) tooltip.hidden = true;
      });
      track.addEventListener('blur', function () {
        if (tooltip) tooltip.hidden = true;
      });
      track.addEventListener('keydown', function (event) {
        let year = selected;
        if (event.key === 'ArrowLeft') year--;
        else if (event.key === 'ArrowRight') year++;
        else if (event.key === 'Home') year = startYear;
        else if (event.key === 'End') year = endYear;
        else return;
        event.preventDefault();
        selectYear(year);
        const bounds = track.getBoundingClientRect();
        placeTooltip(bounds.left + (year - startYear + .5) * bounds.width / count);
      });
      selectYear(startYear);
    }

    // Download menu: the project data contract always exists. If and only if
    // genuine computed results are available, download their existing JSON.
    const dialog = $('download-dialog');
    const openDownload = $('download-data');
    const closeDownload = $('download-close');
    if (dialog && openDownload && closeDownload) {
      openDownload.addEventListener('click', function () {
        if (typeof dialog.showModal === 'function') dialog.showModal();
        else dialog.setAttribute('open', '');
      });
      closeDownload.addEventListener('click', function () { dialog.close(); });
      dialog.addEventListener('click', function (event) {
        if (event.target === dialog) dialog.close();
      });
      const exportButton = $('download-results');
      if (exportButton && report && report.status === 'computed') {
        exportButton.disabled = false;
        exportButton.addEventListener('click', function () {
          const payload = JSON.stringify(report, null, 2);
          const objectURL = URL.createObjectURL(new Blob([payload], { type: 'application/json' }));
          const anchor = document.createElement('a');
          anchor.href = objectURL;
          anchor.download = 'tirana_analysis_results.json';
          document.body.appendChild(anchor);
          anchor.click();
          anchor.remove();
          window.setTimeout(function () { URL.revokeObjectURL(objectURL); }, 1000);
        });
      }
    }

    // A copyable terminal block; no command is executed by the browser.
    const copy = $('copy-code');
    const code = $('method-code');
    if (copy && code) {
      copy.addEventListener('click', async function () {
        const content = code.textContent;
        let success = false;
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(content);
            success = true;
          } else {
            const text = document.createElement('textarea');
            text.value = content;
            text.style.position = 'fixed';
            text.style.opacity = '0';
            document.body.appendChild(text);
            text.select();
            success = document.execCommand('copy');
            text.remove();
          }
        } catch (error) { success = false; }
        copy.textContent = success ? 'COPIED' : 'SELECT CODE ABOVE';
      });
    }
  });
}());

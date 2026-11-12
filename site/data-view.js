
    document.addEventListener('DOMContentLoaded', () => {
      const el = (id) => document.getElementById(id);
      const svgNS = 'http://www.w3.org/2000/svg';
      const results = window.WEATHER_RESULTS && window.WEATHER_RESULTS.status === 'computed' ? window.WEATHER_RESULTS : null;
      const fmt = (x,d=2) => Number(x).toLocaleString('en-US', {minimumFractionDigits:d,maximumFractionDigits:d});
      const pct = (x) => fmt(x*100,2) + '%';
      const pp = (x) => (x>0?'+':'') + fmt(x*100,2) + ' pp';
      const degrees = (x) => (x>0?'+':'') + fmt(x,2) + '°C';
      const interval = (lo,hi,unit) => '[' + fmt(lo,2) + ', ' + fmt(hi,2) + '] ' + unit;
      const group = (parts) => `<svg viewBox="0 0 690 286" role="img" xmlns="${svgNS}" aria-label="${parts.title}">${parts.svg}</svg>`;
      function empty(label,desc) { return `<div class="empty-figure" role="status"><svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="14" fill="none" stroke="#0B1F3A" stroke-width="1.5" stroke-dasharray="3 3"/><path d="M20 11v10l7 4" fill="none" stroke="#0B1F3A" stroke-width="1.5"/></svg><strong>${label}</strong><p>${desc}</p></div>`; }
      const waiting = 'No real data has been entered. This chart will appear only after the offline analysis has run.';
      function installEmpty() { ['rate-chart','null-chart','tail-chart'].forEach(id => el(id).innerHTML=empty('Awaiting verified data',waiting)); }
      function renderRate(data) {
        const rates = data.rates, maxV = Math.max(.01,...rates.map(r=>r.ci_upper*1.28),...rates.map(r=>r.rate*1.25));
        const scale = x => 180 + 448*x/maxV;
        let shape = '';
        const ticks = 5;
        for(let t=0;t<=ticks;t++){let x=scale(maxV*t/ticks);shape+=`<line x1="${x}" y1="24" x2="${x}" y2="223" stroke="#DCE6EF"/><text x="${x}" y="245" text-anchor="middle" font-size="12" fill="#0B1F3A">${fmt(maxV*t/ticks*100,1)}%</text>`;}
        rates.forEach((r,i)=>{let y=85+i*96;shape+=`<text x="5" y="${y-6}" font-size="16" font-weight="700" fill="#0B1F3A">${r.period.replace('-', '–')}</text><text x="5" y="${y+15}" font-size="11" fill="#4E5F73">${r.hot_days} hot / ${r.valid_max_days} valid</text>`;
          shape+=`<line x1="${scale(r.ci_lower)}" x2="${scale(r.ci_upper)}" y1="${y}" y2="${y}" stroke="${i===1 && r.rate>rates[0].rate?'#EB2F33':'#2C99D6'}" stroke-width="9" stroke-linecap="round"/><circle cx="${scale(r.rate)}" cy="${y}" r="7" fill="${i===1 && r.rate>rates[0].rate?'#EB2F33':'#0B4F8A'}" stroke="#fff" stroke-width="2"/>`;
          shape+=`<text x="${scale(r.rate)}" y="${y-19}" fill="#0B1F3A" text-anchor="middle" font-size="12" font-weight="700">${pct(r.rate)}</text>`;
        });
        shape+=`<text x="403" y="277" font-size="12" fill="#4E5F73" text-anchor="middle">Share of observed June–August days</text>`;
        el('rate-chart').innerHTML=group({title:'Hot-day base rate for the two periods with 95 percent year-block bootstrap ranges',svg:shape});
        ['early','late'].forEach((name,i)=>{el(name+'-rate').textContent=pct(rates[i].rate);el(name+'-range').textContent=interval(rates[i].ci_lower*100,rates[i].ci_upper*100,'% · 95% range');});
        el('diff-rate').textContent=pp(data.difference.observed_difference);el('diff-range').textContent=interval(data.difference.ci_lower*100,data.difference.ci_upper*100,'pp · 95% range');
        const missing = rates.map(r=>r.missing_or_null_max_days || 0);
        el('coverage-note').textContent=`Observed counts: ${rates[0].hot_days} / ${rates[0].valid_max_days} days in 1961–1990; ${rates[1].hot_days} / ${rates[1].valid_max_days} in 1991–2020. Missing/null summer maxima: ${missing[0]} and ${missing[1]} days respectively.`;
        const d=data.difference;el('q1-conclusion').textContent = d.ci_lower > 0 || d.ci_upper < 0 ? 'The 95% year-block interval excludes zero; the gridded data support a difference.' : 'The 95% year-block interval includes zero. We cannot tell from this analysis whether the rate changed.';
      }
      function renderNull(data){
        const hist=data.permutation.histogram;
        if(!hist || !hist.counts || !hist.counts.length) { el('null-chart').innerHTML=empty('Histogram unavailable','Re-run the website export after generating permutation results.'); return; }
        const edges=hist.edges, counts=hist.counts, observed=data.permutation.observed_difference*100;
        const xMin=Math.min(edges[0],observed),xMax=Math.max(edges[edges.length-1],observed),diff=xMax-xMin||1;
        const sx=x=>46+(x-xMin)/diff*603, maxY=Math.max(...counts,1),sy=y=>224-y/maxY*171;
        let shape='<line x1="46" y1="224" x2="650" y2="224" stroke="#0B1F3A"/>';
        for(let i=0;i<counts.length;i++){const x=sx(edges[i]),w=Math.max(.3,sx(edges[i+1])-x-1);shape+=`<rect x="${x}" y="${sy(counts[i])}" width="${w}" height="${224-sy(counts[i])}" fill="#2C99D6"/>`;}
        for(let t=0;t<5;t++){let v=xMin+(xMax-xMin)*t/4;shape+=`<text x="${sx(v)}" y="246" text-anchor="middle" font-size="11" fill="#0B1F3A">${v>0?'+':''}${fmt(v,1)}</text>`;}
        shape+=`<line x1="${sx(observed)}" x2="${sx(observed)}" y1="27" y2="224" stroke="${observed>0?'#EB2F33':'#2C99D6'}" stroke-width="3"/><text x="${Math.min(575,Math.max(60,sx(observed)-12))}" y="17" font-size="12" fill="${observed>0?'#C21F27':'#0B4F8A'}">Observed</text>`;
        shape+=`<text x="346" y="275" text-anchor="middle" fill="#0B1F3A" font-size="12">Shuffled change, percentage points (late minus early)</text>`;
        el('null-chart').innerHTML=group({title:'Distribution of differences after 10,000 shuffles of whole summer-year labels; observed difference marked',svg:shape});
        el('shuffle-note').textContent=`Central 95% shuffle baseline: ${interval(data.permutation.null_ci_lower*100,data.permutation.null_ci_upper*100,'percentage points')}. Fraction at least as extreme as observed: ${interval(data.permutation.extreme_fraction_ci_lower*100,data.permutation.extreme_fraction_ci_upper*100,'% Monte Carlo range')} (estimate ${pct(data.permutation.extreme_fraction)}; not a climate-confidence interval).`;
      }
      function renderTail(data) {
        const changes=data.changes;const extent= Math.max(.5,...changes.flatMap(c=>[Math.abs(c.observed_change),Math.abs(c.ci_lower),Math.abs(c.ci_upper)]))*1.35;
        const sx=x=>345+x/extent*265;
        let shape='';
        for(let t=-2;t<=2;t++){const v=extent*t/2;shape+=`<line x1="${sx(v)}" x2="${sx(v)}" y1="22" y2="218" stroke="${t===0?'#0B1F3A':'#DCE6EF'}" stroke-dasharray="${t===0?'4 4':'0'}" stroke-width="${t===0?2:1}"/><text x="${sx(v)}" y="244" text-anchor="middle" font-size="11" fill="#0B1F3A">${v>0?'+':''}${fmt(v,1)}</text>`;}
        changes.forEach((c,i)=>{const y=80+i*96;shape+=`<text x="4" y="${y-12}" font-size="14" fill="#0B1F3A" font-weight="700">${i===0?'Mean daily max':'95th percentile'}</text><text x="4" y="${y+9}" font-size="11" fill="#4E5F73">${degrees(c.observed_change)}</text>`;shape+=`<line x1="${sx(c.ci_lower)}" x2="${sx(c.ci_upper)}" y1="${y}" y2="${y}" stroke="${c.observed_change>0?'#EB2F33':'#2C99D6'}" stroke-width="9" stroke-linecap="round"/><circle cx="${sx(c.observed_change)}" cy="${y}" r="7" fill="${c.observed_change>0?'#EB2F33':'#0B4F8A'}" stroke="#fff" stroke-width="2"/>`;});
        shape+='<text x="340" y="276" font-size="12" text-anchor="middle" fill="#0B1F3A">Temperature change (°C), 1991–2020 minus 1961–1990</text>';
        el('tail-chart').innerHTML=group({title:'Mean and 95th-percentile summer maximum shifts, with 95 percent whole-year bootstrap ranges',svg:shape});
        const labels=['mean-summary','tail-summary'];changes.forEach((c,i)=>{el(labels[i]).textContent=degrees(c.observed_change)+' · '+interval(c.ci_lower,c.ci_upper,'°C (95% range)');});
        const supported = changes.filter(c=>c.ci_lower>0||c.ci_upper<0).map(c=>c.metric.includes('p95')?'95th percentile':'mean');
        el('q2-conclusion').textContent=supported.length ? '95% bootstrap ranges exclude zero for: '+supported.join(' and ')+'.' : 'Both 95% year-block ranges include zero. We cannot tell from this analysis whether either shifted.';
      }
      const menu=el('menu-btn');menu.addEventListener('click',()=>{let open=el('site-nav').classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
      document.querySelectorAll('#site-nav a').forEach(a=>a.addEventListener('click',()=>{el('site-nav').classList.remove('open');menu.setAttribute('aria-expanded','false');}));
      if(results && Array.isArray(results.rates) && results.rates.length===2 && Array.isArray(results.changes) && results.changes.length===2 && results.permutation) {
        renderRate(results);renderNull(results);renderTail(results);
        el('top-status').classList.add('ready');el('top-status').setAttribute('aria-label','Analysis results loaded');el('status-label').textContent='Results from cache';
        el('hero-status').textContent='ANALYSIS COMPUTED FROM CACHED OBSERVATIONS';
        el('data-statement').textContent='All displayed observed results are generated from cached ERA5 data and a reproducible offline notebook. These are estimates with uncertainty, not predictions.';
        if(results.prediction && !results.prediction.includes('[')) { el('prediction-text').textContent=results.prediction; el('prediction-label').textContent='Pre-registered statement'; }
        else el('prediction-text').textContent='Sealed prediction not supplied in exported data.';
        if(results.generated_at)el('data-update').textContent='Exported '+results.generated_at;
      } else {installEmpty();}
    });
  
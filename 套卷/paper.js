/* 政治复盘中心 · 整卷模考引擎
 * 数据：data_papers.js 挂 window.PAPERS = [{k, kind:'x8'|'zt', name, sub, src, qs:[题]}]
 *   题：{no, t:'s'|'m'|'e', sj:'my'|'mz'|'xg'|'sg'|'sx'|'sz', stem, opts[4], ans, jx, ea(分析题参考答案), asks[](分析题设问), pg(书页)}
 * 本机记录（不与 1000 题的 pol_rec_v1 混，免得首页「已做」虚高）：
 *   pol_paper_v1       {卷k: [{ts, obj 选择得分, s 单选得分, m 多选得分, by:{sj:[得,满]}, dur 秒, ex:[5 道分析自估分]}]}
 *   pol_paper_rec_v1   {题id: {n, w, ok, pick, streak, ts}}   题id = 卷k-题号，如 x8-3-17
 *   pol_paper_draft_v1 {k, picks:{no:'AB'}, t0, lim}            未交卷草稿（刷新不丢，24 小时过期）
 *   pol_paper_essay_v1 {题id: 作答文字} · pol_paper_ex_v1 {题id: 自估分}
 * URL：?k=卷   ?k=卷&read=1 背题   ?wrong=1 跨卷错题重练
 */
(function(){
  const P = window.PAPERS || [];
  const SJ = {my:'马原',mz:'毛中特',xg:'习概',sg:'史纲',sx:'思法',sz:'时政'};
  const SJO = ['my','mz','xg','sg','sx','sz'];
  const KIND = {x8:{h:'肖八 · 2027 冲刺 8 套卷', d:'肖秀荣 11 月出的 8 套模拟卷。肖八的价值在<b>选择题</b>（时政与新提法），大题看答案划关键词、不背整段——大题背肖四。'},
                zt:{h:'真题 · 近 3 年', d:'2024 起习概单列，五科题号分布三年完全一致（单选 马4 毛2 习3 史4 思1 时2；多选 马5 毛1 习4 史3 思2 时2）。真题的价值是<b>看出题口径</b>：同一知识点肖八怎么问、真题怎么问。'}};
  const L = k => { try { return JSON.parse(localStorage.getItem(k)) || {}; } catch(e){ return {}; } };
  const S = (k,v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} };
  const K_LED='pol_paper_v1', K_REC='pol_paper_rec_v1', K_DR='pol_paper_draft_v1', K_ES='pol_paper_essay_v1', K_EX='pol_paper_ex_v1';
  let led = L(K_LED), rec = L(K_REC), essay = L(K_ES), exs = L(K_EX);
  const $ = s => document.querySelector(s), app = $('#app');
  const esc = s => String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const fmt = s => esc(s).replace(/\n/g,'<br>');
  const mmss = t => { t = Math.max(0, Math.round(t)); const h = Math.floor(t/3600), m = Math.floor(t%3600/60), s = t%60; return (h ? h+':' : '') + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0'); };
  const qid = (p, q) => p.k + '-' + q.no;
  const pts = q => q.t === 's' ? 1 : 2;
  const qp = new URLSearchParams(location.search);
  const crumb = `<div class="crumb"><a href="../index.html">← 政治复盘中心</a><a href="套卷.html">📝 全部套卷</a><a href="../题库/刷题.html">📚 1000 题</a></div>`;

  /* 解析着色（与刷题引擎同一套口径，简化版） */
  const HL = /(《[^》\n]{1,32}》)|((?:\d{4}(?:—|-|～|~|至)\d{2,4}|\d{4})年(?:\d{1,2}月)?(?:\d{1,2}日)?)|((?:[A-D](?:\s*[、，,和与及]\s*[A-D])*)\s*项?\s*(?:均)?(?:正确|符合题意|当选|入选|应选))|((?:[A-D](?:\s*[、，,和与及]\s*[A-D])*)\s*项?\s*(?:均)?(?:错误|不正确|不符合题意|不选|排除|说法错误|表述错误))|(本题选\s*[A-D]+|故(?:本题)?(?:正确答案为|选)\s*[A-D]+)|(根本|核心|实质|本质|首要|关键|基础|前提)|(“[^”\n]{2,12}”)|([（(][1-6][)）]|第[一二三四五六]，)/g;
  const CLS = [null,'kt','kt','km','kw','km','kw','kd','kn'];
  const hl = s => esc(s).replace(/【(名师点拨|点拨)】/g, '\u0001$1\u0002').replace(HL, (...m) => { for (let i=1;i<CLS.length;i++) if (m[i]) return `<span class="${CLS[i]}">${m[i]}</span>`; return m[0]; }).replace(/\n/g,'<br>').replace(/\u0001(.*?)\u0002/g, '<b class="kx">【$1】</b>');
  const NEG = /(不正确|错误的是|不属于|不包括|不符合|不是|并非|不能)/g;
  const stemH = s => fmt(s).replace(NEG, '<span class="neg">$1</span>');

  function best(k){ const r = led[k] || []; return r.length ? Math.max(...r.map(x => x.obj)) : null; }
  function last(k){ const r = led[k] || []; return r.length ? r[r.length-1] : null; }

  /* ================= 列表 ================= */
  function renderList(){
    const kinds = [...new Set(P.map(p => p.kind))];
    const wrongN = P.flatMap(p => p.qs.filter(q => q.t !== 'e' && isW(rec[qid(p,q)]))).length;
    let h = crumb + `<header><h1>整卷模考</h1><p class="sub">一套卷 = 单选 16 ＋ 多选 17（选择 50 分）＋ 分析 5 道（50 分）。选择题交卷自动判分并按科目拆账；分析题先自己写，再对照参考答案自估分。</p></header>`;
    h += `<section class="card"><h2>怎么用</h2><ol class="plan">
      <li><b>选择题限时做</b>：考场上选择题大约留 <b>50 分钟</b>（单选 1 分钟、多选 1.5 分钟左右），这里可开「⏱ 50 分钟」限时，到点自动交卷。</li>
      <li><b>交卷看拆账</b>：哪一科丢分最多，就回 1000 题刷那一科的错题；<b>时政丢分</b>回肖《形势与政策》。</li>
      <li><b>分析题</b>：先在框里写关键词（存本机），再点「参考答案」划要点、按 0–10 自估分，总分＝选择＋分析自估。</li>
      <li><b>错题重练</b>：所有套卷里做错、且还没连对 2 次的选择题，集中再做一遍。</li></ol>
      <p style="margin-top:10px"><a class="btn${wrongN?' pri':''}" href="套卷.html?wrong=1">🔁 套卷错题重练（${wrongN} 题）</a></p></section>`;
    for (const kd of kinds){
      const ps = P.filter(p => p.kind === kd), K = KIND[kd] || {h:kd, d:''};
      h += `<section class="card"><h2>${K.h}</h2><p class="lead">${K.d}</p><div class="plist">` + ps.map(p => {
        const r = led[p.k] || [], b = best(p.k), l = last(p.k);
        const exTot = l && l.ex ? l.ex.reduce((a,x) => a + (+x||0), 0) : null;
        const dr = L(K_DR); const going = dr.k === p.k && Date.now() - dr.t0 < 864e5;
        return `<div class="pc${r.length?' done':''}"><h3>${esc(p.name)}</h3><div class="meta">${esc(p.sub||'')} ${p.proof ? '<span class="pill green">文字已校对</span>' : '<span class="pill gold">识别稿 · 校对中</span>'}<br>` +
          (r.length ? `做过 <b>${r.length}</b> 次 · 选择最好 <b>${b}</b>/50 · 最近 <b>${l.obj}</b>/50${exTot!=null && l.ex.some(x=>x!=null&&x!=='') ? ` ＋ 分析自估 <b>${exTot}</b>` : ''}` : '还没做过') +
          (going ? `<br><span class="pill gold">有未交卷的草稿</span>` : '') + `</div>
          <div class="acts"><a class="btn sm pri" href="?k=${p.k}">${going ? '继续作答' : r.length ? '再做一遍' : '开始'}</a><a class="btn sm" href="?k=${p.k}&read=1">背题</a></div></div>`;
      }).join('') + `</div></section>`;
    }
    app.innerHTML = h;
  }

  /* ================= 作答 ================= */
  let cur = null;     // {p, picks, t0, lim, done, run, read}
  let timer = null;
  function startPaper(p, read){
    const dr = L(K_DR);
    const keep = !read && dr.k === p.k && Date.now() - dr.t0 < 864e5;
    cur = {p, picks: keep ? dr.picks || {} : {}, t0: keep ? dr.t0 : Date.now(), lim: keep ? dr.lim || 0 : 0, done: !!read, read: !!read, run: null, onlyW: false};
    document.title = p.name + ' · 整卷模考';
    renderPaper();
    if (!read) startTimer();
  }
  function saveDraft(){ if (!cur.done) S(K_DR, {k: cur.p.k, picks: cur.picks, t0: cur.t0, lim: cur.lim}); }

  function optsHTML(q){
    const pick = cur.picks[q.no] || '', ans = q.ans || '';
    return `<div class="opts">` + q.opts.map((o,i) => { const Lt = 'ABCD'[i]; let c = 'opt';
      if (cur.done){ c += ' lock'; const inA = ans.includes(Lt), inP = pick.includes(Lt);
        if (inA) c += (inP || cur.read) ? ' right' : ' miss'; else if (inP) c += ' wrong'; }
      else if (pick.includes(Lt)) c += ' sel';
      return `<button class="${c}" data-no="${q.no}" data-k="${Lt}"><span class="ol">${Lt}</span><span class="ot">${fmt(o)}</span></button>`; }).join('') + `</div>`;
  }
  function verdict(q){
    if (cur.read) return `<div class="verdict">答案 <b>${q.ans}</b></div>`;
    const pick = cur.picks[q.no] || '';
    if (!pick) return `<div class="verdict blank">未作答 · 答案 <b>${q.ans}</b></div>`;
    const ok = pick === q.ans;
    return `<div class="verdict ${ok?'ok':'bad'}">${ok?'答对了':'答错了'} · 答案 <b>${q.ans}</b> · 你选 <b>${pick}</b></div>`;
  }
  function cardHTML(q){
    const p = cur.p, show = cur.done;
    const ok = show && !cur.read && (cur.picks[q.no]||'') === q.ans;
    const r = rec[qid(p,q)];
    let h = `<div class="card qcard${ok?' okq':''}" id="q${q.no}"><div class="qmeta"><span class="qidx">${q.no}</span>` +
      (show ? `<span class="subj ${q.sj}">${SJ[q.sj]||''}</span>` : '') + `<span class="pill">${q.t==='s'?'单选 1 分':'多选 2 分'}</span>` +
      (show && r && r.n > 1 ? `<span class="pill ${r.ok?'green':'red'}">做过 ${r.n} 次 · ✘${r.w||0}</span>` : '') + `</div>` +
      `<div class="stem">${stemH(q.stem)}</div>` + optsHTML(q);
    if (show){
      h += verdict(q);
      if (q.jx) h += `<div class="jx"><div class="eh">📕 解析${q.jxsrc ? ' · 肖《讲真题》' : ''}</div>${hl(q.jx)}</div>`;
      else if (p.kind === 'zt') h += `<div class="src">《讲真题》没收这道题的解析（时政题，或提法已变的旧考点）。</div>`;
      if (q.pg) h += `<div class="src">题面：${esc(p.src||'')} P${q.pg}${q.jxsrc ? ' · 解析：' + esc(q.jxsrc) : ''}</div>`;
    }
    return h + `</div>`;
  }
  function essayHTML(q){
    const id = qid(cur.p, q), ex = exs[id];
    const open = cur.read;
    return `<div class="card qcard" id="q${q.no}"><div class="qmeta"><span class="qidx">${q.no}</span><span class="subj ${q.sj}">${SJ[q.sj]||''}</span><span class="pill">分析题 10 分</span></div>
      <div class="stem">${fmt(q.stem)}</div>` +
      (q.asks && q.asks.length ? `<ol class="ask-l">${q.asks.map(a => `<li>${esc(a)}</li>`).join('')}</ol>` : '') +
      `<textarea class="mine-ta" data-id="${id}" placeholder="先写关键词（存本机）：原理名 ＋ 材料里的对应句 ＋ 落脚点">${esc(essay[id]||'')}</textarea>
      <details class="eafold"${open?' open':''}><summary class="btn sm" style="margin-top:8px">📕 参考答案</summary>` +
      (q.ea ? `<div class="ea"><div class="eh">📕 参考答案 · 背的是要点句，不是材料</div>${hl(q.ea)}</div>` : `<div class="ea">本卷暂无官方公布的分析题参考答案。</div>`) +
      `</details><div class="erow">自估分 <input type="number" min="0" max="10" step="0.5" data-ex="${id}" value="${ex==null?'':ex}"> / 10
      <span class="note" style="margin:0">（对照要点：每答到一个要点约 2 分，原理名写对＋联系材料才给满）</span></div></div>`;
  }

  function scorePanel(){
    const run = cur.run; if (!run) return '';
    const p = cur.p, exTot = p.qs.filter(q => q.t === 'e').reduce((a,q) => a + (+exs[qid(p,q)]||0), 0);
    const exN = p.qs.filter(q => q.t === 'e' && exs[qid(p,q)] != null && exs[qid(p,q)] !== '').length;
    const rows = SJO.filter(s => run.by[s]).map(s => { const [g,f] = run.by[s]; const pc = f ? Math.round(100*g/f) : 0;
      return `<tr><td class="l"><span class="subj ${s}">${SJ[s]}</span></td><td>${g} / ${f}</td><td><div class="bar"><i style="width:${pc}%;background:${pc>=70?'var(--green)':pc>=50?'var(--gold)':'var(--red)'}"></i></div></td><td>${f-g ? '−'+(f-g) : '满分'}</td></tr>`; }).join('');
    const worst = SJO.filter(s => run.by[s]).sort((a,b) => (run.by[b][1]-run.by[b][0]) - (run.by[a][1]-run.by[a][0]))[0];
    const hist = (led[p.k]||[]).map((r,i) => `第 ${i+1} 次 ${new Date(r.ts).toLocaleDateString('zh-CN')}：<b>${r.obj}</b>/50（单选 ${r.s}/16 · 多选 ${r.m}/34 · 用时 ${mmss(r.dur)}）`).join('<br>');
    return `<section class="card" id="sum"><h2>成绩</h2><div class="score"><div class="big">${run.obj}<small> / 50 选择</small></div>
      <div>单选 <b>${run.s}</b>/16 · 多选 <b>${run.m}</b>/34 · 用时 <b>${mmss(run.dur)}</b><br>` +
      (exN ? `分析自估 <b>${exTot}</b>/50（已估 ${exN}/5 题）⟹ 全卷约 <b>${run.obj + exTot}</b> 分` : `分析题写完自估分后，这里会算出全卷总分`) +
      `</div></div><div class="gridwrap"><table class="by"><tr><th>科目</th><th>得分</th><th>得分率</th><th>丢分</th></tr>${rows}</table></div>` +
      (worst && run.by[worst][1] > run.by[worst][0] ? `<p class="note">丢分最多：<b>${SJ[worst]}</b>（−${run.by[worst][1]-run.by[worst][0]}）。${worst==='sz' ? '时政回肖《形势与政策》补。' : `回 <a href="../题库/刷题.html?p=${worst}&t=all&mode=wrong">1000 题 · ${SJ[worst]}错题本</a>。`}</p>` : '') +
      `<p class="act" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><button class="btn sm" id="onlyW">${cur.onlyW ? '显示全部题' : '只看错题'}</button><a class="btn sm" href="?k=${p.k}">再做一遍</a><a class="btn sm" href="套卷.html?wrong=1">🔁 套卷错题重练</a></p>
      <details><summary class="note" style="cursor:pointer">本卷历次成绩</summary><div class="hist">${hist}</div></details></section>`;
  }

  function gridHTML(){
    const p = cur.p;
    return p.qs.map(q => { let c = 'gi';
      if (q.t === 'e') c += ' e' + (essay[qid(p,q)] ? ' a' : '');
      else if (cur.done && !cur.read) c += (cur.picks[q.no] === q.ans) ? ' g' : ' r';
      else if (cur.picks[q.no]) c += ' a';
      return `<button class="${c}" data-go="${q.no}">${q.no}</button>`; }).join('');
  }
  function dockHTML(){
    const p = cur.p, n = p.qs.filter(q => q.t !== 'e' && cur.picks[q.no]).length, tot = p.qs.filter(q => q.t !== 'e').length;
    const segs = [[0,'不限时'],[3000,'⏱ 50 分钟'],[10800,'⏱ 3 小时']];
    return `<div id="dock"><span class="ttl">${esc(p.name)}${cur.read ? ' · 背题' : ''}</span>` +
      (cur.read ? '' : cur.done ? `<span class="cnt">已交卷 · 选择 <b>${cur.run ? cur.run.obj : '—'}</b>/50</span>` :
        `<span class="tm" id="tm">00:00</span><span class="cnt">已答 ${n}/${tot}</span>` +
        `<select id="lim" aria-label="限时">${segs.map(([v,t]) => `<option value="${v}"${cur.lim==v?' selected':''}>${t}</option>`).join('')}</select>` +
        `<button class="btn sm pri" id="sub">交卷</button>`) +
      `<button class="btn sm" id="gbtn">▦</button><div id="grid" hidden style="flex-basis:100%">${gridHTML()}</div></div>`;
  }

  function renderPaper(){
    const p = cur.p, S1 = p.qs.filter(q => q.t === 's'), M = p.qs.filter(q => q.t === 'm'), E = p.qs.filter(q => q.t === 'e');
    let h = crumb + `<header><h1>${esc(p.name)}</h1><p class="sub">${esc(p.sub||'')}${cur.read ? ' · 背题模式：答案与解析直接摊开' : ''}</p></header>` +
      (p.proof ? '' : `<p class="chkbar">⚠️ 这套卷的文字是扫描识别稿、还没逐字校对完，个别字可能有错（${p.kind === 'x8' ? '答案已与卷首答案速查表两路核对' : '答案取自试卷参考答案页'}，不受影响）。读着别扭的地方以纸质书为准。</p>`) + dockHTML();
    if (cur.done && !cur.read) h += scorePanel();
    h += `<div id="body" class="${cur.onlyW?'only-w':''}">`;
    if (S1.length) h += `<div class="sec-h">一、单项选择题</div><p class="sec-n">第 1–${S1.length} 题，每题 1 分，共 ${S1.length} 分。</p>` + S1.map(cardHTML).join('');
    if (M.length) h += `<div class="sec-h">二、多项选择题</div><p class="sec-n">第 ${M[0].no}–${M[M.length-1].no} 题，每题 2 分，共 ${M.length*2} 分。多选、少选均不得分。</p>` + M.map(cardHTML).join('');
    if (!cur.done) h += `<p style="margin:18px 0;text-align:center"><button class="btn pri" id="sub2">选择题交卷判分</button></p>`;
    if (E.length) h += `<div class="sec-h">三、材料分析题</div><p class="sec-n">第 ${E[0].no}–${E[E.length-1].no} 题，每题 10 分，共 50 分。选择题交不交卷都能先写这部分。</p>` + E.map(essayHTML).join('');
    h += `</div>`;
    app.innerHTML = h;
    bindPaper();
    tick();
  }
  function bindPaper(){
    const sub = () => submit(false);
    if ($('#sub')) $('#sub').onclick = sub;
    if ($('#sub2')) $('#sub2').onclick = sub;
    $('#gbtn').onclick = () => { const g = $('#grid'); g.hidden = !g.hidden; };
    if ($('#lim')) $('#lim').onchange = e => { cur.lim = +e.target.value; if (cur.lim) cur.t0 = Date.now(); saveDraft(); tick(); };
    if ($('#onlyW')) $('#onlyW').onclick = () => { cur.onlyW = !cur.onlyW; renderPaper(); $('#sum').scrollIntoView(); };
    app.onclick = e => {
      const g = e.target.closest('[data-go]'); if (g){ const el = $('#q' + g.dataset.go); if (el) el.scrollIntoView({behavior:'smooth', block:'start'}); return; }
      const b = e.target.closest('.opt'); if (!b || cur.done) return;
      const no = +b.dataset.no, q = cur.p.qs.find(x => x.no === no), k = b.dataset.k;
      let pk = cur.picks[no] || '';
      if (q.t === 's') pk = pk === k ? '' : k;
      else pk = pk.includes(k) ? pk.replace(k,'') : [...pk + k].sort().join('');
      if (pk) cur.picks[no] = pk; else delete cur.picks[no];
      b.parentNode.outerHTML = optsHTML(q);
      saveDraft(); refreshDock();
    };
    app.oninput = e => {
      const t = e.target;
      if (t.dataset.id){ essay[t.dataset.id] = t.value; S(K_ES, essay); }
      if (t.dataset.ex){ let v = t.value === '' ? null : Math.max(0, Math.min(10, +t.value)); if (v == null) delete exs[t.dataset.ex]; else exs[t.dataset.ex] = v; S(K_EX, exs);
        if (cur.run){ const r = (led[cur.p.k]||[]); if (r.length){ r[r.length-1].ex = cur.p.qs.filter(q=>q.t==='e').map(q => exs[qid(cur.p,q)] ?? null); S(K_LED, led); } } }
    };
    app.addEventListener('change', e => { if (e.target.dataset.ex && cur.run){ const s = $('#sum'); if (s) s.outerHTML = scorePanel(); const o = $('#onlyW'); if (o) o.onclick = () => { cur.onlyW = !cur.onlyW; renderPaper(); }; } });
  }
  function refreshDock(){
    const p = cur.p, n = p.qs.filter(q => q.t !== 'e' && cur.picks[q.no]).length, tot = p.qs.filter(q => q.t !== 'e').length;
    const c = $('#dock .cnt'); if (c && !cur.done) c.textContent = `已答 ${n}/${tot}`;
    const g = $('#grid'); if (g) g.innerHTML = gridHTML();
  }
  function startTimer(){ clearInterval(timer); timer = setInterval(tick, 1000); }
  function tick(){
    const el = $('#tm'); if (!el || cur.done) return;
    const used = (Date.now() - cur.t0) / 1000;
    if (cur.lim){ const left = cur.lim - used; el.textContent = '剩 ' + mmss(left); el.classList.toggle('warn', left < 300); if (left <= 0) submit(true); }
    else { el.textContent = mmss(used); el.classList.remove('warn'); }
  }
  function submit(auto){
    if (cur.done) return;
    const p = cur.p, ch = p.qs.filter(q => q.t !== 'e');
    const blank = ch.filter(q => !cur.picks[q.no]).length;
    if (!auto && blank && !confirm(`还有 ${blank} 道选择题没答，确定交卷？`)) return;
    clearInterval(timer);
    const by = {}; let s = 0, m = 0;
    ch.forEach(q => { const pk = cur.picks[q.no] || '', ok = pk === q.ans, f = pts(q);
      (by[q.sj] = by[q.sj] || [0,0])[1] += f; if (ok){ by[q.sj][0] += f; if (q.t === 's') s += f; else m += f; }
      const id = qid(p,q), r = rec[id] || {n:0, w:0, streak:0};
      r.n++; r.ok = ok; r.pick = pk; r.ts = Date.now(); if (ok) r.streak = (r.streak||0) + 1; else { r.w++; r.streak = 0; }
      rec[id] = r;
      if (window.PolUI && PolUI.logDaily) PolUI.logDaily(q.sj + '-paper-' + id, ok);
    });
    S(K_REC, rec);
    const run = {ts: Date.now(), obj: s + m, s, m, by, dur: Math.round((Date.now() - cur.t0)/1000), ex: p.qs.filter(q=>q.t==='e').map(q => exs[qid(p,q)] ?? null)};
    (led[p.k] = led[p.k] || []).push(run); S(K_LED, led);
    try { localStorage.removeItem(K_DR); } catch(e){}
    cur.done = true; cur.run = run;
    renderPaper(); window.scrollTo(0, 0);
    if (auto) alert('时间到，已自动交卷。');
  }

  /* ================= 跨卷错题重练（当场判） ================= */
  function isW(r){ return r && r.w > 0 && !(r.streak >= 2); }
  function renderWrong(){
    const list = P.flatMap(p => p.qs.filter(q => q.t !== 'e' && isW(rec[qid(p,q)])).map(q => ({p, q})));
    const picks = {};
    let h = crumb + `<header><h1>套卷错题重练</h1><p class="sub">所有套卷里做错过、且还没有连续做对 2 次的选择题，共 ${list.length} 题。点选即判（多选勾完点「提交」），连对 2 次自动出本。</p></header>`;
    if (!list.length) h += `<section class="card"><p class="empty">没有待清的错题 🎉 先去 <a href="套卷.html">做一套卷</a>。</p></section>`;
    h += list.map(({p,q}, i) => `<div class="card qcard" id="w${i}"><div class="qmeta"><span class="qidx">${i+1}</span><span class="subj ${q.sj}">${SJ[q.sj]}</span><span class="pill">${esc(p.name)} 第 ${q.no} 题</span><span class="pill red">错过 ${rec[qid(p,q)].w} 次</span></div>
      <div class="stem">${stemH(q.stem)}</div><div class="opts">${q.opts.map((o,j) => `<button class="opt" data-i="${i}" data-k="${'ABCD'[j]}"><span class="ol">${'ABCD'[j]}</span><span class="ot">${fmt(o)}</span></button>`).join('')}</div>
      ${q.t === 'm' ? `<p class="act" style="margin-top:10px"><button class="btn sm pri" data-subm="${i}">提交</button></p>` : ''}<div class="res"></div></div>`).join('');
    app.innerHTML = h;
    const judge = i => { const {p,q} = list[i], el = $('#w'+i), pk = picks[i] || '', ok = pk === q.ans, id = qid(p,q), r = rec[id];
      r.n++; r.ok = ok; r.pick = pk; r.ts = Date.now(); if (ok) r.streak = (r.streak||0)+1; else { r.w++; r.streak = 0; } S(K_REC, rec);
      if (window.PolUI && PolUI.logDaily) PolUI.logDaily(q.sj + '-paper-' + id, ok);
      el.querySelectorAll('.opt').forEach(b => { const k = b.dataset.k, inA = q.ans.includes(k), inP = pk.includes(k); b.classList.add('lock'); b.classList.remove('sel');
        if (inA) b.classList.add(inP ? 'right' : 'miss'); else if (inP) b.classList.add('wrong'); });
      const sb = el.querySelector('[data-subm]'); if (sb) sb.remove();
      el.querySelector('.res').innerHTML = `<div class="verdict ${ok?'ok':'bad'}">${ok?'答对了':'答错了'} · 答案 <b>${q.ans}</b>${ok && r.streak>=2 ? ' · 连对 2 次，出本' : ''}</div>` + (q.jx ? `<div class="jx"><div class="eh">📕 解析</div>${hl(q.jx)}</div>` : '');
      el.dataset.done = 1; };
    app.onclick = e => {
      const sb = e.target.closest('[data-subm]'); if (sb){ if (picks[sb.dataset.subm]) judge(+sb.dataset.subm); return; }
      const b = e.target.closest('.opt'); if (!b) return; const i = +b.dataset.i; if ($('#w'+i).dataset.done) return;
      const q = list[i].q, k = b.dataset.k;
      if (q.t === 's'){ picks[i] = k; judge(i); return; }
      let pk = picks[i] || ''; pk = pk.includes(k) ? pk.replace(k,'') : [...pk + k].sort().join(''); picks[i] = pk; b.classList.toggle('sel');
    };
  }

  /* ================= 入口 ================= */
  const k = qp.get('k'), p = P.find(x => x.k === k);
  if (qp.get('wrong')) renderWrong();
  else if (p) startPaper(p, qp.get('read') === '1');
  else renderList();
})();

/* 政治复盘中心 · 刷题引擎
 * 数据：各科 data_*.js 往 window.POL 里挂 {key,name,short,chapters:{ch:名},qs:[...]}
 * 题目字段：id, t(s单选/m多选/e分析), ch, no, page(书页), stem, opts[4], ans('A'|'ACD'|null),
 *          src(出处), jx(简析), db(点拨), ea(分析题参考答案), tag(时政储备题等), my(⚡秒杀/形象记忆，Claude 补写)
 * 记录：localStorage 'pol_rec_v1' = {id:{n:作答次数,ok:最近一次对错,w:累计错次,streak:连对次数,pick,ts}}
 */
(function(){
  const POL = window.POL || {};
  const KEY = 'pol_rec_v1', PREF = 'pol_pref_v1';
  const TYPES = {s:'单选',m:'多选',e:'分析题'};
  const load = k => { try { return JSON.parse(localStorage.getItem(k)) || {}; } catch(e){ return {}; } };
  const save = (k,v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} };
  let rec = load(KEY), pref = load(PREF);
  const $ = s => document.querySelector(s);
  const esc = s => String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const fmt = s => esc(s).replace(/\n/g,'<br>');

  const qp = new URLSearchParams(location.search);
  const st = {
    p: qp.get('p') || pref.p || 'my',
    t: qp.get('t') || pref.t || 's',
    ch: qp.get('ch') != null ? qp.get('ch') : (pref.ch != null ? String(pref.ch) : 'all'),
    mode: qp.get('mode') || 'seq',      // seq 顺序 / undone 未做 / wrong 错题 / rand 随机20
    view: qp.get('view') || pref.view || 'do', // do 做题 / read 背题
    i: 0, list: [], picked: new Set(), done: false
  };

  function allQs(){ return Object.values(POL).flatMap(S => S.qs.map(q => Object.assign(q,{_p:S.key}))); }
  function isWrong(q){ const r = rec[q.id]; return r && r.w > 0 && !(r.streak >= 2); }

  function buildList(){
    let qs;
    if (st.p === 'all') qs = allQs(); else qs = (POL[st.p] ? POL[st.p].qs.map(q=>Object.assign(q,{_p:st.p})) : []);
    qs = qs.filter(q => st.t === 'all' || q.t === st.t);
    if (st.ch !== 'all') qs = qs.filter(q => String(q.ch) === String(st.ch));
    if (st.mode === 'undone') qs = qs.filter(q => !rec[q.id]);
    if (st.mode === 'wrong') qs = qs.filter(isWrong);
    if (st.mode === 'rand') { qs = qs.slice(); for (let i=qs.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [qs[i],qs[j]]=[qs[j],qs[i]]; } qs = qs.slice(0,20); }
    st.list = qs;
  }

  function fillSelectors(){
    const ps = $('#selP'), cs = $('#selCh'), ts = $('#selT'), ms = $('#selMode');
    ps.innerHTML = Object.values(POL).map(S=>`<option value="${S.key}">${S.name}</option>`).join('') + `<option value="all">五科混刷</option>`;
    ps.value = st.p;
    ts.value = st.t; ms.value = st.mode;
    const S = POL[st.p];
    let opts = `<option value="all">全部章节</option>`;
    if (S) opts += Object.entries(S.chapters).map(([k,v])=>{
      const n = S.qs.filter(q=>String(q.ch)===k && (st.t==='all'||q.t===st.t)).length;
      return n ? `<option value="${k}">${v}（${n}）</option>` : '';
    }).join('');
    cs.innerHTML = opts; cs.value = st.ch; if (cs.value !== st.ch) { st.ch='all'; cs.value='all'; }
    cs.disabled = !S;
    $('#viewBtn').textContent = st.view === 'read' ? '📖 背题中' : '✏️ 做题中';
  }

  function savePref(){ pref = {p:st.p,t:st.t,ch:st.ch,view:st.view}; save(PREF,pref);
    const u = new URL(location.href); ['p','t','ch','mode','view'].forEach(k=>u.searchParams.set(k,st[k])); history.replaceState(null,'',u); }

  function stat(){
    const L = st.list, d = L.filter(q=>rec[q.id]).length, ok = L.filter(q=>rec[q.id] && rec[q.id].ok).length;
    const ch = L.filter(q=>q.t!=='e' && rec[q.id]);
    const acc = ch.length ? Math.round(100*ch.filter(q=>rec[q.id].ok).length/ch.length) : null;
    $('#bar').innerHTML = `共 <b>${L.length}</b> 题 · 已做 <b>${d}</b> · 正确率 <b>${acc==null?'—':acc+'%'}</b>`
      + (st.t==='s'?' <span class="note">（肖：单选 ≥70% 达标）</span>':st.t==='m'?' <span class="note">（肖：多选 50–55% 达标）</span>':'');
  }

  function render(){
    stat();
    const box = $('#q');
    if (!st.list.length){ box.innerHTML = `<div class="empty">${st.mode==='wrong'?'🎉 这个范围内没有错题了':'这个范围还没有题目'}</div>`; $('#nav').style.display='none'; return; }
    $('#nav').style.display='';
    st.i = Math.max(0, Math.min(st.i, st.list.length-1));
    const q = st.list[st.i], S = POL[q._p], r = rec[q.id];
    st.picked = new Set(); st.done = st.view === 'read';
    const tag = q.tag ? `<span class="pill gold">${esc(q.tag)}</span>` : '';
    const hist = r ? `<span class="pill ${r.ok?'green':'red'}">做过 ${r.n} 次${r.w?' · 错 '+r.w:''}</span>` : '';
    let h = `<div class="qmeta"><span class="pill purple">${S.short}</span><span class="pill">${esc(S.chapters[q.ch]||'')}</span><span class="pill blue">${TYPES[q.t]} ${q.no}</span><span class="pill">书 P${q.page}</span>${tag}${hist}</div>`;
    h += `<div class="stem">${fmt(q.stem)}</div>`;
    if (q.t !== 'e'){
      h += `<div class="opts">` + q.opts.map((o,k)=>{ const L='ABCD'[k]; return `<button class="opt" data-k="${L}"><span class="ol">${L}</span><span class="ot">${fmt(o)}</span></button>`; }).join('') + `</div>`;
      if (q.t === 'm') h += `<div class="act"><button class="btn pri" id="submit">提交（多选）</button></div>`;
    } else {
      h += `<div class="act"><button class="btn pri" id="showEa">看参考答案（先自己在纸上列要点）</button></div>`;
    }
    h += `<div id="ana"></div>`;
    box.innerHTML = h;
    box.querySelectorAll('.opt').forEach(b => b.onclick = () => pick(b.dataset.k));
    const sb = $('#submit'); if (sb) sb.onclick = () => judge();
    const se = $('#showEa'); if (se) se.onclick = () => showAnswer();
    if (st.view === 'read') showAnswer(true);
    $('#pos').textContent = `${st.i+1} / ${st.list.length}`;
    $('#prev').disabled = st.i===0; $('#next').disabled = st.i===st.list.length-1;
    renderGrid();
    window.scrollTo({top:0});
  }

  function pick(k){
    if (st.done) return;
    const q = st.list[st.i];
    if (q.t === 's'){ st.picked = new Set([k]); judge(); return; }
    st.picked.has(k) ? st.picked.delete(k) : st.picked.add(k);
    document.querySelectorAll('.opt').forEach(b => b.classList.toggle('sel', st.picked.has(b.dataset.k)));
  }

  function judge(){
    const q = st.list[st.i];
    if (!st.picked.size) return;
    const pickStr = [...st.picked].sort().join('');
    const ok = pickStr === q.ans;
    const r = rec[q.id] || {n:0,w:0,streak:0};
    r.n++; r.ok = ok; r.pick = pickStr; r.ts = Date.now();
    if (ok) r.streak = (r.streak||0)+1; else { r.w++; r.streak = 0; }
    rec[q.id] = r; save(KEY, rec);
    showAnswer(false, pickStr);
    stat(); renderGrid();
  }

  function showAnswer(readOnly, pickStr){
    const q = st.list[st.i]; st.done = true;
    if (q.t !== 'e'){
      document.querySelectorAll('.opt').forEach(b => {
        const k = b.dataset.k, inAns = q.ans.includes(k), inPick = pickStr && pickStr.includes(k);
        b.classList.add('lock');
        if (inAns) b.classList.add(inPick || readOnly ? 'right' : 'miss');
        else if (inPick) b.classList.add('wrong');
      });
      const sb = $('#submit'); if (sb) sb.remove();
    } else { const se = $('#showEa'); if (se) se.remove(); }
    let h = '';
    if (q.t !== 'e'){
      const ok = pickStr ? pickStr === q.ans : null;
      h += `<div class="verdict ${ok===null?'':ok?'ok':'bad'}">答案 <b>${q.ans}</b>${pickStr?` · 你选 <b>${pickStr}</b> ${ok?'✅':'❌'}`:''}</div>`;
    }
    if (q.my) h += `<div class="miao">${q.my}</div>`;
    if (q.t === 'e' && q.ea) h += `<div class="ea"><div class="eh">📕 参考答案（肖·解析分册）<span class="note">——大题要背的是这里的<b>要点句</b>，不是材料</span></div>${fmt(q.ea)}</div>`;
    if (q.jx) h += `<div class="jx"><div class="eh">📕 肖·简析</div>${fmt(q.jx)}</div>`;
    if (q.db) h += `<div class="db"><div class="eh">📌 肖·点拨</div>${fmt(q.db)}</div>`;
    if (q.src) h += `<div class="src">出处：${esc(q.src)}</div>`;
    if (q.t === 'e'){
      const r = rec[q.id];
      h += `<div class="act self">自评：<button class="btn sm" data-s="2">能默出要点</button><button class="btn sm" data-s="1">大致记得</button><button class="btn sm" data-s="0">还不会</button>${r?` <span class="note">上次：${['还不会','大致记得','能默出要点'][r.self||0]}</span>`:''}</div>`;
    }
    if (st.i < st.list.length-1) h += `<div class="act"><button class="btn pri" id="goNext">下一题 →</button></div>`;
    $('#ana').innerHTML = h;
    const gn = $('#goNext'); if (gn) gn.onclick = () => go(1);
    document.querySelectorAll('.self button').forEach(b => b.onclick = () => {
      const s = +b.dataset.s, r = rec[q.id] || {n:0,w:0,streak:0};
      r.n++; r.self = s; r.ok = s===2; r.ts = Date.now(); if (s===2) r.streak=(r.streak||0)+1; else { r.w++; r.streak=0; }
      rec[q.id] = r; save(KEY, rec); stat(); renderGrid(); go(1);
    });
  }

  function renderGrid(){
    const g = $('#grid'); if (!g || g.hidden) return;
    g.innerHTML = st.list.map((q,k)=>{ const r = rec[q.id]; const c = !r?'':r.ok?'g':'r';
      return `<button class="gi ${c} ${k===st.i?'cur':''}" data-k="${k}">${q.no}</button>`; }).join('');
    g.querySelectorAll('.gi').forEach(b => b.onclick = () => { st.i = +b.dataset.k; render(); });
  }

  function go(d){ st.i += d; render(); }

  function init(){
    if (!Object.keys(POL).length){ document.body.insertAdjacentHTML('beforeend','<p style="padding:20px">题库数据没有加载。</p>'); return; }
    if (st.p !== 'all' && !POL[st.p]) st.p = Object.keys(POL)[0];
    fillSelectors(); buildList(); savePref();
    const jump = qp.get('q'); if (jump){ const k = st.list.findIndex(q=>q.id===jump); if (k>=0) st.i=k; }
    render();
    $('#selP').onchange = e => { st.p = e.target.value; st.ch='all'; st.i=0; fillSelectors(); buildList(); savePref(); render(); };
    $('#selT').onchange = e => { st.t = e.target.value; st.i=0; fillSelectors(); buildList(); savePref(); render(); };
    $('#selCh').onchange = e => { st.ch = e.target.value; st.i=0; buildList(); savePref(); render(); };
    $('#selMode').onchange = e => { st.mode = e.target.value; st.i=0; buildList(); savePref(); render(); };
    $('#viewBtn').onclick = () => { st.view = st.view==='read'?'do':'read'; fillSelectors(); savePref(); render(); };
    $('#prev').onclick = () => go(-1); $('#next').onclick = () => go(1);
    $('#gridBtn').onclick = () => { const g=$('#grid'); g.hidden=!g.hidden; renderGrid(); };
    document.addEventListener('keydown', e => {
      if (e.target.tagName === 'SELECT') return;
      const k = e.key.toUpperCase();
      if ('ABCD'.includes(k) && k.length===1) pick(k);
      else if ('1234'.includes(k) && k.length===1) pick('ABCD'[+k-1]);
      else if (e.key==='Enter'){ const q=st.list[st.i]; if (q && q.t==='m' && !st.done) judge(); else if (st.done) go(1); }
      else if (e.key==='ArrowRight' && st.i<st.list.length-1) go(1);
      else if (e.key==='ArrowLeft' && st.i>0) go(-1);
    });
  }
  window.PolEngine = { init, rec: () => rec };
})();

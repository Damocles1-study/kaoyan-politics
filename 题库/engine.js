/* 政治复盘中心 · 刷题引擎 v2（四种刷法）
 * 数据：各科 data_*.js 往 window.POL 里挂 {key,name,short,chapters:{ch:名},qs:[...]}
 * 题目字段：id, t(s单选/m多选/e分析), ch, no, page(书页), stem, opts[4], ans('A'|'ACD'|null),
 *          src(出处), jx(简析), db(点拨), ea(分析题参考答案), tag(时政储备题等), my(⚡秒杀/形象记忆，Claude 补写)
 * 记录：localStorage 'pol_rec_v1' = {id:{n:作答次数,ok:最近一次对错,w:累计错次,streak:连对次数,pick,self,ts}}
 * 刷法 fm：one 逐题（一屏一题当场判） · flow 连刷（一页一组、每题当场判） · exam 模考（一组做完交卷再判，可限时）
 *          · read 背题（答案解析直接摊开）。模考未交卷的作答存 'pol_exam_v1'，刷新不丢。
 * URL 参数：p t ch mode(seq/undone/wrong/rand) fm(one/flow/exam/read) n(每组题数，0=整章) q(跳到题 id)；旧链接的 view=read 仍然有效
 */
(function(){
  const POL = window.POL || {};
  const KEY = 'pol_rec_v1', PREF = 'pol_pref_v1', DRAFT = 'pol_exam_v1';
  const TYPES = {s:'单选',m:'多选',e:'分析题'};
  const FMS = ['one','flow','exam','read'], SIZES = [10,20,30,50,0];
  const FM_TIP = {
    one:  '<b>逐题</b>：一屏一题，单选点了就判、多选勾完再提交，看完解析翻下一题。',
    flow: '<b>连刷 · 当场判</b>：一页一组往下刷，每题答完立刻出答案和解析，不用来回翻页。',
    exam: '<b>模考 · 交卷再判</b>：一组全部做完再统一批改，中途不提示对错；交卷后看得分、错题一键再练。',
    read: '<b>背题</b>：答案和解析直接摊开，一页一组快速过，适合二轮记忆和考前翻看。'
  };
  const load = k => { try { return JSON.parse(localStorage.getItem(k)) || {}; } catch(e){ return {}; } };
  const save = (k,v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} };
  let rec = load(KEY), pref = load(PREF);
  const $ = s => document.querySelector(s);
  const esc = s => String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const fmt = s => esc(s).replace(/\n/g,'<br>');
  const mmss = t => String(Math.floor(t/60)).padStart(2,'0') + ':' + String(t%60).padStart(2,'0');
  const sortStr = s => [...s].sort().join('');

  /* 自动着色（只作用于肖的简析 / 点拨 / 参考答案，一次扫描、互不嵌套）：
   * 《著作》与年份→紫  ·  「A、B 正确」→绿  ·  「C 错误」→红  ·  根本/核心/实质…→红
   * 短引号概念→蓝  ·  （1）（2）第一第二→金  ·  「易错 / 注意 / 不要混淆」→橙 */
  const TITLE = '最基本、最核心|根本属性|唯一特性|唯一源泉|唯一标准|本质属性|根本目的|根本原因|根本动力|根本途径|根本方法|根本特征|根本区别|根本问题|决定性|根本|核心|实质|本质|基石|精髓|灵魂|前提|基础|首要|关键';
  const HL = new RegExp(
    '(《[^》\\n]{1,32}》)' +
    '|((?:\\d{4}(?:—|-|～|~|至)\\d{2,4}|\\d{4})年(?:\\d{1,2}月)?(?:\\d{1,2}日)?)' +
    '|((?:[A-D](?:\\s*[、，,和与及]\\s*[A-D])*|[①②③④⑤](?:[①②③④⑤])*)\\s*项?\\s*(?:均)?(?:正确|符合题意|当选|入选|应选))' +
    '|((?:[A-D](?:\\s*[、，,和与及]\\s*[A-D])*|[①②③④⑤](?:[①②③④⑤])*)\\s*项?\\s*(?:均)?(?:错误|不正确|不符合题意|不选|排除|说法错误|表述错误|不合题意))' +
    '|(本题选\\s*[A-D①-⑤]+|因此[，,]?\\s*本题选\\s*[A-D]+)' +
    '|(' + TITLE + ')' +
    '|(“[^”\\n]{2,12}”)' +
    '|([（(][1-6][)）]|第[一二三四五六]，|首先，|其次，|再次，|最后，)' +
    '|(易错|易混|注意区分|不要混淆|需要注意|容易误选|陷阱)', 'g');
  const CLS = [null,'kt','kt','km','kw','km','kw','kd','kn','kx'];
  const hl = s => esc(s).replace(HL, (...m) => { for (let i=1;i<CLS.length;i++) if (m[i]) return `<span class="${CLS[i]}">${m[i]}</span>`; return m[0]; }).replace(/\n/g,'<br>');
  /* 题干：只在最后一句里标「题眼」，否定词标红，防止看漏「不正确的是」 */
  const NEG = /(不正确|错误的是|不属于|不包括|不符合|不是|并非|不能|无关|错误的有|不正确的有)/g;
  const ASK = /(这说明|这表明|说明了|表明|体现了|蕴含的(?:哲学)?(?:原理|哲理|道理)|启示是|启示有|在于|是因为|是指|主要是|根本原因|根本在于|关键在于|核心是|实质是|首要|根本|标志着|意味着)/g;
  function hlStem(s){
    s = String(s==null?'':s);
    let stmts = '';
    const ci = s.search(/\n\s*①/);
    if (ci >= 0) { stmts = s.slice(ci); s = s.slice(0, ci); }
    let cut = Math.max(s.lastIndexOf('。'), s.lastIndexOf('？'), s.lastIndexOf('！'), s.lastIndexOf('”'));
    if (cut < 0 || cut >= s.length-1) cut = Math.max(-1, s.length - 42);
    const head = s.slice(0, cut+1), tail = s.slice(cut+1);
    const t2 = esc(tail).replace(NEG,'<span class="neg">$1</span>').replace(ASK,'<span class="ask">$1</span>');
    return (esc(head) + t2 + esc(stmts)).replace(/\n/g,'<br>');
  }

  const qp = new URLSearchParams(location.search);
  let fm0 = qp.get('fm') || (qp.get('view') === 'read' ? 'read' : '') || pref.fm || (pref.view === 'read' ? 'read' : 'one');
  let n0 = +(qp.get('n') ?? pref.n ?? 20);
  const st = {
    p: qp.get('p') || pref.p || 'my',
    t: qp.get('t') || pref.t || 's',
    ch: qp.get('ch') != null ? qp.get('ch') : (pref.ch != null ? String(pref.ch) : 'all'),
    mode: qp.get('mode') || 'seq',      // 范围：seq 顺序 / undone 未做 / wrong 错题 / rand 随机打乱
    fm: FMS.includes(fm0) ? fm0 : 'one',
    n: SIZES.includes(n0) ? n0 : 20,
    timed: !!pref.timed,
    i: 0, g: 0, dir: 0, list: [], picked: new Set(), done: false,
    custom: null, onlyWrong: false, sess: null
  };

  function allQs(){ return Object.values(POL).flatMap(S => S.qs.map(q => Object.assign(q,{_p:S.key}))); }
  function isWrong(q){ const r = rec[q.id]; return r && r.w > 0 && !(r.streak >= 2); }

  function buildList(){
    if (st.custom){ const m = new Map(allQs().map(q => [q.id, q])); st.list = st.custom.map(id => m.get(id)).filter(Boolean); return; }
    let qs;
    if (st.p === 'all') qs = allQs(); else qs = (POL[st.p] ? POL[st.p].qs.map(q=>Object.assign(q,{_p:st.p})) : []);
    qs = qs.filter(q => st.t === 'all' || q.t === st.t);
    if (st.ch !== 'all') qs = qs.filter(q => String(q.ch) === String(st.ch));
    if (st.mode === 'undone') qs = qs.filter(q => !rec[q.id]);
    if (st.mode === 'wrong') qs = qs.filter(isWrong);
    if (st.mode === 'rand') { qs = qs.slice(); for (let i=qs.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [qs[i],qs[j]]=[qs[j],qs[i]]; } }
    st.list = qs;
  }
  const gsize = () => st.n || st.list.length || 1;
  const gcount = () => Math.max(1, Math.ceil(st.list.length / gsize()));
  const group = () => st.list.slice(st.g * gsize(), st.g * gsize() + gsize());

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
    document.querySelectorAll('#fmSeg button').forEach(b => { b.classList.toggle('on', b.dataset.f === st.fm); b.setAttribute('aria-selected', b.dataset.f === st.fm); });
    $('#selN').value = String(st.n); $('#selN').hidden = st.fm === 'one';
    $('#fmTip').innerHTML = FM_TIP[st.fm];
    $('#opts2').innerHTML = st.fm === 'exam' ? `<label><input type="checkbox" id="timed"${st.timed?' checked':''}> ⏱ 考场节奏限时（单选 1 分钟 · 多选 1.5 分钟，到时自动交卷）</label>` : '';
    $('#opts2').hidden = st.fm !== 'exam';
    const tm = $('#timed'); if (tm) tm.onchange = () => { st.timed = tm.checked; savePref(); tick(); };
  }

  function savePref(){ pref = {p:st.p,t:st.t,ch:st.ch,fm:st.fm,n:st.n,timed:st.timed}; save(PREF,pref);
    const u = new URL(location.href); ['p','t','ch','mode','fm','n'].forEach(k=>u.searchParams.set(k,st[k])); u.searchParams.delete('view'); u.searchParams.delete('q'); history.replaceState(null,'',u); }

  function stat(){
    const L = st.list, d = L.filter(q=>rec[q.id]).length;
    const ch = L.filter(q=>q.t!=='e' && rec[q.id]);
    const acc = ch.length ? Math.round(100*ch.filter(q=>rec[q.id].ok).length/ch.length) : null;
    let h = `共 <b>${L.length}</b> 题 · 已做 <b>${d}</b> · 正确率 <b>${acc==null?'—':acc+'%'}</b>`
      + (st.fm!=='one' && L.length ? ` · 分 <b>${gcount()}</b> 组` : '')
      + (st.t==='s'?' <span class="note">（肖：单选 ≥70% 达标）</span>':st.t==='m'?' <span class="note">（肖：多选 50–55% 达标）</span>':'');
    if (st.custom) h += `<div class="redo">🔁 错题再练 · ${L.length} 题<button class="btn sm" id="exitRedo">退出再练</button></div>`;
    $('#bar').innerHTML = h;
    const ex = $('#exitRedo'); if (ex) ex.onclick = () => { st.custom = null; st.g = 0; st.i = 0; st.sess = null; buildList(); render(); };
  }

  /* ---------- 通用片段 ---------- */
  function record(q, pick){
    const ok = pick === q.ans, r = rec[q.id] || {n:0,w:0,streak:0};
    r.n++; r.ok = ok; r.pick = pick; r.ts = Date.now();
    if (ok) r.streak = (r.streak||0)+1; else { r.w++; r.streak = 0; }
    rec[q.id] = r; save(KEY, rec); return ok;
  }
  function recordSelf(q, s){
    const r = rec[q.id] || {n:0,w:0,streak:0};
    r.n++; r.self = s; r.ok = s===2; r.ts = Date.now(); if (s===2) r.streak=(r.streak||0)+1; else { r.w++; r.streak=0; }
    rec[q.id] = r; save(KEY, rec);
  }
  function metaHTML(q, idx, hideHist){
    const S = POL[q._p], r = rec[q.id];
    const tag = q.tag ? `<span class="pill gold">${esc(q.tag)}</span>` : '';
    const hist = r && !hideHist ? `<span class="pill ${r.ok?'green':'red'}">做过 ${r.n} 次${r.w?' · 错 '+r.w:''}</span>` : '';
    return `<div class="qmeta">${idx?`<span class="qidx">${idx}</span>`:''}<span class="subj ${q._p}">${S.short}</span><span class="pill">${esc(S.chapters[q.ch]||'')}</span><span class="qno">${TYPES[q.t]} 第 ${q.no} 题</span><span class="pill">书 P${q.page}</span>${tag}${hist}</div>`;
  }
  /* res：null＝可作答（sel 为已勾选字母）；{pick}＝已判；{read:true}＝背题直接标答案 */
  function optsHTML(q, sel, res){
    const ans = q.ans || '';
    return `<div class="opts">` + q.opts.map((o,k)=>{ const L='ABCD'[k]; let c='opt';
      if (res){ c += ' lock'; const inA = ans.includes(L), inP = !!(res.pick && res.pick.includes(L));
        if (inA) c += (inP || res.read) ? ' right' : ' miss'; else if (inP) c += ' wrong'; }
      else if (sel && sel.includes(L)) c += ' sel';
      return `<button class="${c}" data-k="${L}"><span class="ol">${L}</span><span class="ot">${fmt(o)}</span></button>`; }).join('') + `</div>`;
  }
  function verdictHTML(q, pick, read){
    if (q.t === 'e') return '';
    if (read) return `<div class="verdict">答案 <b>${q.ans}</b></div>`;
    if (!pick) return `<div class="verdict blank">未作答 · 答案 <b>${q.ans}</b></div>`;
    const ok = pick === q.ans;
    return `<div class="verdict ${ok?'ok':'bad'}">${ok?'答对了':'答错了'} · 答案 <b>${q.ans}</b> · 你选 <b>${pick}</b></div>`;
  }
  function restHTML(q){
    let h = '';
    if (q.my) h += `<div class="miao">${q.my}</div>`;
    if (q.t === 'e' && q.ea) h += `<div class="ea"><div class="eh">📕 参考答案（肖·解析分册）<span class="note">——大题要背的是这里的<b>要点句</b>，不是材料</span></div>${hl(q.ea)}</div>`;
    if (q.jx) h += `<div class="jx"><div class="eh">📕 肖·简析</div>${hl(q.jx)}</div>`;
    if (q.db) h += `<div class="db"><div class="eh">📌 肖·点拨</div>${hl(q.db)}</div>`;
    if (q.jj) h += `<div class="jj"><div class="eh">📗 精讲原文 · ${esc(q.jj.p)}</div>${q.jj.h ? `<div class="jjh">${esc(q.jj.h)}</div>` : ''}${hl(q.jj.t)}`
      + (!q.jx && !q.db ? `<div class="note">书上这题只给了答案和出处，这是出处那一段的原文（本机识别，挑了与本题相关的句子，「……」处有删节）。</div>` : '') + `</div>`;
    if (q.lk) { const [u,tt] = q.lk.split('|'); h += `<a class="lk" href="../${u}">📖 本题知识点：${esc(tt)} →</a>`; }
    if (q.src) h += `<div class="src">出处：${esc(q.src)}（《精讲精练》页码 · 考点段落）</div>`;
    return h;
  }
  function selfHTML(q, chosen){
    const r = rec[q.id], L = ['还不会','大致记得','能默出要点'];
    return `<div class="act self">自评：` + [2,1,0].map(s => `<button class="btn sm${chosen===s?' pri':''}" data-s="${s}">${L[s]}</button>`).join('')
      + (chosen==null && r && r.self!=null ? ` <span class="note">上次：${L[r.self]}</span>` : '') + `</div>`;
  }
  function anim(el, cls){ if (!el) return; el.classList.remove('swap-l','swap-r','fade-in','shake'); void el.offsetWidth; el.classList.add(cls); }

  /* ---------- 逐题 ---------- */
  function renderOne(){
    stopTimer(); $('#list').innerHTML = ''; $('#sum').innerHTML = '';
    st.i = Math.max(0, Math.min(st.i, st.list.length-1));
    const q = st.list[st.i];
    st.picked = new Set(); st.done = false;
    let h = metaHTML(q) + `<div class="stem">${hlStem(q.stem)}</div>`;
    if (q.t !== 'e'){
      h += optsHTML(q, '', null);
      if (q.t === 'm') h += `<div class="act"><button class="btn pri" id="submit">提交（多选）</button></div>`;
    } else h += `<div class="act"><button class="btn pri" id="showEa">看参考答案（先自己在纸上列要点）</button></div>`;
    h += `<div id="ana"></div>`;
    const box = $('#q');
    box.innerHTML = `<article class="qcard">${h}</article>`;
    anim(box.firstChild, st.dir > 0 ? 'swap-l' : st.dir < 0 ? 'swap-r' : 'fade-in'); st.dir = 0;
    box.querySelectorAll('.opt').forEach(b => b.onclick = () => pick(b.dataset.k));
    const sb = $('#submit'); if (sb) sb.onclick = () => judge();
    const se = $('#showEa'); if (se) se.onclick = () => showAnswer();
    navOne(); renderGrid();
    const top = box.getBoundingClientRect().top; if (top < 0) box.scrollIntoView({block:'start'});
  }
  function navOne(){
    $('#nav').innerHTML = `<button class="btn" id="prev">← 上一题</button><div class="mid"><b>${st.i+1}</b> / ${st.list.length}</div><button class="btn" id="next">下一题 →</button>`;
    $('#prev').disabled = st.i===0; $('#next').disabled = st.i===st.list.length-1;
    $('#prev').onclick = () => go(-1); $('#next').onclick = () => go(1);
  }
  function pick(k){
    if (st.done) return;
    const q = st.list[st.i];
    if (q.t === 's'){ st.picked = new Set([k]); judge(); return; }
    st.picked.has(k) ? st.picked.delete(k) : st.picked.add(k);
    document.querySelectorAll('#q .opt').forEach(b => b.classList.toggle('sel', st.picked.has(b.dataset.k)));
  }
  function judge(){
    const q = st.list[st.i];
    if (!st.picked.size) return;
    const p = sortStr(st.picked);
    record(q, p); showAnswer(p);
    stat(); renderGrid();
  }
  function showAnswer(p){
    const q = st.list[st.i]; st.done = true;
    if (q.t !== 'e'){
      document.querySelectorAll('#q .opt').forEach(b => {
        const k = b.dataset.k, inA = q.ans.includes(k), inP = p && p.includes(k);
        b.classList.remove('sel'); b.classList.add('lock');
        if (inA) b.classList.add(inP ? 'right' : 'miss'); else if (inP) b.classList.add('wrong');
      });
      const sb = $('#submit'); if (sb) sb.remove();
    } else { const se = $('#showEa'); if (se) se.remove(); }
    let h = verdictHTML(q, p, false) + restHTML(q);
    if (q.t === 'e') h += selfHTML(q);
    if (st.i < st.list.length-1) h += `<div class="act"><button class="btn pri" id="goNext">下一题 →</button></div>`;
    const ana = $('#ana'); ana.innerHTML = h; ana.className = 'drop-in';
    if (p && p !== q.ans) anim($('#q .qcard'), 'shake');
    const gn = $('#goNext'); if (gn) gn.onclick = () => go(1);
    document.querySelectorAll('#q .self button').forEach(b => b.onclick = () => { recordSelf(q, +b.dataset.s); stat(); renderGrid(); go(1); });
  }
  function go(d){ const j = st.i + d; if (j < 0 || j >= st.list.length) return; st.dir = d; st.i = j; render(); }

  /* ---------- 连刷 / 模考 / 背题（一页一组） ---------- */
  function sessFor(G){
    const gkey = st.fm + '|' + G.map(q=>q.id).join(',');
    if (st.sess && st.sess.gkey === gkey) return st.sess;
    stopTimer();
    const s = {gkey, picks:{}, judged:{}, self:{}, submitted:false, t0:Date.now()};
    if (st.fm === 'exam'){ const d = load(DRAFT); if (d.gkey === gkey && Date.now()-d.t0 < 12*3600e3){ s.picks = d.picks || {}; s.t0 = d.t0; } }
    st.sess = s; return s;
  }
  function saveDraft(){ const s = st.sess; if (s && !s.submitted) save(DRAFT, {gkey:s.gkey, picks:s.picks, t0:s.t0}); }
  function cardHTML(q, k, s, G){
    const last = k === G.length-1;
    const more = last ? (st.g < gcount()-1 ? `<div class="act"><button class="btn sm" data-a="ngroup">下一组 →</button></div>` : '')
                      : `<div class="act"><button class="btn sm" data-a="next">下一题 ↓</button></div>`;
    let b = metaHTML(q, k+1, st.fm==='exam' && !s.submitted) + `<div class="stem">${hlStem(q.stem)}</div>`;
    if (st.fm === 'read'){
      if (q.t !== 'e') b += optsHTML(q, '', {read:true});
      b += verdictHTML(q, null, true) + restHTML(q);
    } else if (st.fm === 'flow'){
      const j = s.judged[q.id];
      if (q.t === 'e') b += j ? `<div class="drop-in">${restHTML(q)}${selfHTML(q, s.self[q.id])}</div>` + (s.self[q.id]!=null ? more : '')
                              : `<div class="act"><button class="btn pri" data-a="ea">看参考答案（先在纸上列要点）</button></div>`;
      else if (j != null) b += optsHTML(q, '', {pick:j}) + `<div class="drop-in">${verdictHTML(q, j, false)}${restHTML(q)}${more}</div>`;
      else b += optsHTML(q, s.picks[q.id]||'', null) + (q.t==='m' ? `<div class="act"><button class="btn pri" data-a="sub">提交（多选）</button></div>` : '');
    } else if (!s.submitted){
      b += q.t !== 'e' ? optsHTML(q, s.picks[q.id]||'', null) : `<p class="note">分析题不计分：先在纸上列要点，交卷后显示参考答案并自评。</p>`;
    } else if (q.t === 'e'){
      b += restHTML(q) + selfHTML(q, s.self[q.id]);
    } else {
      const pk = s.picks[q.id] || '', ok = pk === q.ans;
      b += optsHTML(q, '', {pick:pk}) + verdictHTML(q, pk, false)
        + (ok ? `<details class="ana-fold"><summary>答对了 · 展开解析</summary>${restHTML(q)}</details>` : restHTML(q));
    }
    const hide = st.fm === 'exam' && s.submitted && st.onlyWrong && (q.t === 'e' || (s.picks[q.id]||'') === q.ans);
    return `<article class="qcard bq${hide?' hidecard':''}" id="bq${k}" data-k="${k}">${b}</article>`;
  }
  function renderBatch(){
    $('#q').innerHTML = '';
    st.g = Math.max(0, Math.min(st.g, gcount()-1));
    const G = group(), s = sessFor(G), L = $('#list');
    L.innerHTML = G.map((q,k) => cardHTML(q, k, s, G)).join('');
    anim(L, 'fade-in');
    renderSum(); navBatch(); renderGrid();
    if (st.fm === 'exam' && !s.submitted) startTimer();
  }
  function reCard(k){ const G = group(), el = $('#bq'+k); if (el) el.outerHTML = cardHTML(G[k], k, st.sess, G); }
  function shakeIfWrong(k, q, p){ if (p !== q.ans) anim($('#bq'+k), 'shake'); }
  function afterChange(){ stat(); navBatch(); renderGrid(); }
  function scrollToCard(k){ const el = $('#bq'+k); if (!el) return; el.classList.remove('hidecard'); el.scrollIntoView({block:'start', behavior:'smooth'}); anim(el, 'fade-in'); el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash'); }

  function onListClick(e){
    const card = e.target.closest('.bq'); if (!card) return;
    const k = +card.dataset.k, G = group(), q = G[k], s = st.sess; if (!q || !s) return;
    const opt = e.target.closest('.opt'), a = e.target.closest('[data-a]'), sf = e.target.closest('.self button');
    const paint = () => card.querySelectorAll('.opt').forEach(b => b.classList.toggle('sel', (s.picks[q.id]||'').includes(b.dataset.k)));
    if (opt && !opt.classList.contains('lock')){
      const L = opt.dataset.k;
      if (st.fm === 'flow' && s.judged[q.id] == null){
        if (q.t === 's'){ s.judged[q.id] = L; record(q, L); reCard(k); shakeIfWrong(k, q, L); afterChange(); }
        else { const p = s.picks[q.id] || ''; s.picks[q.id] = sortStr(p.includes(L) ? p.replace(L,'') : p + L); paint(); }
      } else if (st.fm === 'exam' && !s.submitted){
        let p = s.picks[q.id] || '';
        if (q.t === 's') p = p === L ? '' : L; else p = p.includes(L) ? p.replace(L,'') : p + L;
        s.picks[q.id] = sortStr(p); paint(); saveDraft(); navBatch(); renderGrid();
      }
    } else if (a){
      const x = a.dataset.a;
      if (x === 'sub'){ const p = s.picks[q.id]; if (!p) return; s.judged[q.id] = p; record(q, p); reCard(k); shakeIfWrong(k, q, p); afterChange(); }
      else if (x === 'ea'){ s.judged[q.id] = 'e'; reCard(k); afterChange(); }
      else if (x === 'next') scrollToCard(k+1);
      else if (x === 'ngroup') goGroup(1);
    } else if (sf){ recordSelf(q, +sf.dataset.s); s.self[q.id] = +sf.dataset.s; reCard(k); afterChange(); }
  }

  function navBatch(){
    const nav = $('#nav'), G = group(), s = st.sess, gc = gcount();
    if (!s) return;
    if (st.fm === 'exam' && !s.submitted){
      const ch = G.filter(q => q.t !== 'e'), a = ch.filter(q => s.picks[q.id]).length;
      nav.innerHTML = `<div class="mid"><span class="tm" id="tm">⏱ 00:00</span><br>已答 <b>${a}</b> / ${ch.length}</div><button class="btn pri" id="hand">交卷批改</button>`;
      $('#hand').onclick = () => submitExam(false); tick(); return;
    }
    let mid;
    if (st.fm === 'exam') mid = `第 <b>${st.g+1}</b> / ${gc} 组<br>得分 <b>${s.score}</b> / ${s.total}`;
    else if (st.fm === 'flow'){ const d = G.filter(q => s.judged[q.id] != null).length; mid = `第 <b>${st.g+1}</b> / ${gc} 组<br>本组已做 <b>${d}</b> / ${G.length}`; }
    else mid = `第 <b>${st.g+1}</b> / ${gc} 组<br>${G.length} 题`;
    nav.innerHTML = `<button class="btn" id="gPrev"${st.g===0?' disabled':''}>← 上一组</button><div class="mid">${mid}</div><button class="btn" id="gNext"${st.g>=gc-1?' disabled':''}>下一组 →</button>`;
    $('#gPrev').onclick = () => goGroup(-1); $('#gNext').onclick = () => goGroup(1);
  }
  function goGroup(d){
    const j = st.g + d; if (j < 0 || j >= gcount()) return;
    const s = st.sess;
    if (st.fm === 'exam' && s && !s.submitted && Object.values(s.picks).some(Boolean) && !confirm('这一组还没交卷，切换会丢掉已选的答案。确定切换？')) return;
    if (st.fm === 'exam' && s && !s.submitted) { try { localStorage.removeItem(DRAFT); } catch(e){} }
    st.g = j; st.sess = null; st.onlyWrong = false; render();
    window.scrollTo({top:0, behavior:'smooth'});
  }

  /* 模考计时：不限时就正计时；限时按真题节奏倒计时，到 0 自动交卷 */
  let timerId = null;
  const limitSec = G => st.timed ? G.reduce((a,q) => a + (q.t==='s' ? 60 : q.t==='m' ? 90 : 0), 0) : 0;
  function startTimer(){ stopTimer(); timerId = setInterval(tick, 1000); tick(); }
  function stopTimer(){ if (timerId){ clearInterval(timerId); timerId = null; } }
  function tick(){
    const s = st.sess, el = $('#tm'); if (!s || s.submitted || !el || st.fm !== 'exam') return;
    const used = Math.floor((Date.now()-s.t0)/1000), lim = limitSec(group());
    if (lim){ const left = lim - used; el.textContent = '⏳ ' + mmss(Math.max(0, left)); el.classList.toggle('warn', left <= 60); if (left <= 0) submitExam(true); }
    else { el.textContent = '⏱ ' + mmss(used); el.classList.remove('warn'); }
  }
  function submitExam(auto){
    const s = st.sess, G = group(); if (!s || s.submitted) return;
    const ch = G.filter(q => q.t !== 'e'), blank = ch.filter(q => !s.picks[q.id]).length;
    if (!auto && blank && !confirm(`还有 ${blank} 题没答，未答按 0 分计。确定交卷？`)) return;
    stopTimer();
    let score = 0, total = 0, so = 0, sn = 0, mo = 0, mn = 0; const wrong = [];
    ch.forEach(q => {
      const w = q.t === 'm' ? 2 : 1, p = s.picks[q.id] || '', ok = p === q.ans; total += w;
      if (p) record(q, p);
      if (ok) score += w; else wrong.push(q.id);
      if (q.t === 's'){ sn++; if (ok) so++; } else { mn++; if (ok) mo++; }
    });
    Object.assign(s, {submitted:true, score, total, so, sn, mo, mn, wrong, auto, used:Math.floor((Date.now()-s.t0)/1000)});
    try { localStorage.removeItem(DRAFT); } catch(e){}
    st.onlyWrong = false; stat(); renderBatch();
    window.scrollTo({top:0, behavior:'smooth'});
  }
  function renderSum(){
    const box = $('#sum'), s = st.sess;
    if (st.fm !== 'exam' || !s || !s.submitted){ box.innerHTML = ''; return; }
    const acc = s.total ? Math.round(100*s.score/s.total) : 0, c = acc >= 70 ? 'green' : acc >= 50 ? 'gold' : 'red';
    box.innerHTML = `<section class="card drop-in"><h2>本组成绩</h2><div class="sum"><div class="ring" id="ring" style="--rc:var(--${c})"><span>${acc}%<small>得分率</small></span></div>
      <div class="info"><div class="big">${s.score} <span class="note">/ ${s.total} 分</span></div>
      ${[s.sn ? `单选 <b>${s.so}</b>/${s.sn}` : '', s.mn ? `多选 <b>${s.mo}</b>/${s.mn}` : '', `用时 <b>${mmss(s.used)}</b>${s.auto?'（到时自动交卷）':''}`].filter(Boolean).join(' · ')}
      <p class="note">按真题计分：单选 1 分、多选 2 分（少选多选都不得分）。肖的达标线：单选 ≥70%、多选 50–55%。</p>
      <div class="act">${s.wrong.length ? `<button class="btn pri" data-x="redo">🔁 错题再练（${s.wrong.length}）</button><button class="btn" data-x="only">${st.onlyWrong?'显示全部':'只看错题'}</button>` : '<span class="pill green">🎉 本组全对</span>'}${st.g < gcount()-1 ? '<button class="btn" data-x="next">下一组 →</button>' : ''}</div></div></div></section>`;
    requestAnimationFrame(() => requestAnimationFrame(() => { const r = $('#ring'); if (r) r.style.setProperty('--p', acc); }));
    box.querySelectorAll('[data-x]').forEach(b => b.onclick = () => {
      const x = b.dataset.x;
      if (x === 'redo'){ st.custom = s.wrong.slice(); st.g = 0; st.i = 0; st.sess = null; st.onlyWrong = false; buildList(); render(); window.scrollTo({top:0, behavior:'smooth'}); }
      else if (x === 'only'){ st.onlyWrong = !st.onlyWrong; renderBatch(); }
      else if (x === 'next') goGroup(1);
    });
  }

  /* ---------- 题号格 ---------- */
  function renderGrid(){
    const g = $('#grid'); if (!g || g.hidden) return;
    if (st.fm === 'one'){
      g.innerHTML = st.list.map((q,k)=>{ const r = rec[q.id]; const c = !r?'':r.ok?'g':'r';
        return `<button class="gi ${c} ${k===st.i?'cur':''}" data-k="${k}">${q.no}</button>`; }).join('');
      g.querySelectorAll('.gi').forEach(b => b.onclick = () => { const k = +b.dataset.k; st.dir = k > st.i ? 1 : k < st.i ? -1 : 0; st.i = k; render(); });
      return;
    }
    const G = group(), s = st.sess || {picks:{}, judged:{}};
    g.innerHTML = G.map((q,k) => { let c = '';
      if (st.fm === 'exam'){ if (!s.submitted) c = s.picks[q.id] ? 'a' : ''; else if (q.t !== 'e') c = (s.picks[q.id]||'') === q.ans ? 'g' : 'r'; }
      else if (st.fm === 'flow'){ const j = s.judged[q.id]; if (j != null) c = q.t === 'e' ? 'a' : j === q.ans ? 'g' : 'r'; }
      else { const r = rec[q.id]; c = !r ? '' : r.ok ? 'g' : 'r'; }
      return `<button class="gi ${c}" data-k="${k}" title="书上第 ${q.no} 题">${k+1}</button>`; }).join('');
    g.querySelectorAll('.gi').forEach(b => b.onclick = () => scrollToCard(+b.dataset.k));
  }

  function render(){
    stat();
    if (!st.list.length){
      stopTimer(); $('#list').innerHTML = ''; $('#sum').innerHTML = '';
      $('#q').innerHTML = `<div class="qcard empty">${st.mode==='wrong'?'🎉 这个范围内没有错题了':'这个范围还没有题目'}</div>`;
      $('#nav').style.display = 'none'; $('#grid').innerHTML = ''; return;
    }
    $('#nav').style.display = '';
    st.fm === 'one' ? renderOne() : renderBatch();
  }
  function reset(){ st.i = 0; st.g = 0; st.sess = null; st.custom = null; st.onlyWrong = false; }

  function init(){
    if (!Object.keys(POL).length){ document.body.insertAdjacentHTML('beforeend','<p style="padding:20px">题库数据没有加载。</p>'); return; }
    if (st.p !== 'all' && !POL[st.p]) st.p = Object.keys(POL)[0];
    fillSelectors(); buildList();
    const jump = qp.get('q'); if (jump){ const k = st.list.findIndex(q=>q.id===jump); if (k>=0){ st.i = k; st.g = Math.floor(k / gsize()); } }
    savePref();
    if (st.fm === 'exam') $('#grid').hidden = false;
    render();
    if (jump && st.fm !== 'one'){ const k = st.list.findIndex(q=>q.id===jump) - st.g*gsize(); if (k >= 0) setTimeout(() => scrollToCard(k), 350); }
    if (window.PolUI) PolUI.seg($('#fmSeg'));
    $('#list').addEventListener('click', onListClick);
    $('#selP').onchange = e => { st.p = e.target.value; st.ch='all'; reset(); fillSelectors(); buildList(); savePref(); render(); };
    $('#selT').onchange = e => { st.t = e.target.value; reset(); fillSelectors(); buildList(); savePref(); render(); };
    $('#selCh').onchange = e => { st.ch = e.target.value; reset(); buildList(); savePref(); render(); };
    $('#selMode').onchange = e => { st.mode = e.target.value; reset(); buildList(); savePref(); render(); };
    $('#selN').onchange = e => { const first = st.g * gsize(); st.n = +e.target.value; st.g = Math.floor(first / gsize()); st.sess = null; savePref(); render(); };
    document.querySelectorAll('#fmSeg button').forEach(b => b.onclick = () => {
      const f = b.dataset.f; if (f === st.fm) return;
      const s = st.sess;
      if (st.fm === 'exam' && s && !s.submitted && Object.values(s.picks).some(Boolean) && !confirm('模考还没交卷，切换刷法会丢掉已选的答案。确定切换？')) return;
      if (st.fm === 'one') st.g = Math.floor(st.i / gsize()); else if (f === 'one') st.i = st.g * gsize();
      st.fm = f; st.sess = null; st.onlyWrong = false; stopTimer();
      if (f === 'exam') $('#grid').hidden = false;
      fillSelectors(); savePref(); render();
    });
    $('#gridBtn').onclick = () => { const g = $('#grid'); g.hidden = !g.hidden; renderGrid(); if (!g.hidden) anim(g, 'fade-in'); };
    document.addEventListener('keydown', e => {
      if (/SELECT|INPUT|TEXTAREA/.test(e.target.tagName) || e.metaKey || e.ctrlKey || e.altKey) return;
      if (st.fm !== 'one'){
        if (e.key === 'ArrowRight') goGroup(1); else if (e.key === 'ArrowLeft') goGroup(-1);
        return;
      }
      const k = e.key.toUpperCase();
      if ('ABCD'.includes(k) && k.length===1) pick(k);
      else if ('1234'.includes(k) && k.length===1) pick('ABCD'[+k-1]);
      else if (e.key==='Enter'){ const q=st.list[st.i]; if (q && q.t==='m' && !st.done) judge(); else if (st.done) go(1); }
      else if (e.key==='ArrowRight') go(1);
      else if (e.key==='ArrowLeft') go(-1);
    });
    window.addEventListener('beforeunload', saveDraft);
  }
  window.PolEngine = { init, rec: () => rec };
})();

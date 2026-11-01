/* 政治复盘中心 · 主题切换（放在 <head> 里同步执行，抢在首屏绘制前定好主题，避免闪一下）
 * 三个主题：manga 日式漫画（默认，就是 style.css 本身）· notes 手绘学习笔记 · gallery 艺术画展
 * html[data-skin] 决定主题；画展再加 html[data-hall]：vg 星夜厅 / mu 金箔厅。样式全在 skin.css，
 * 画展的场景（WebGL 画面、螺旋仪、联动）在 gallery.js，只有进画展才加载。
 * 存在本机：pol_skin_v1 = {skin, hall:'auto'|'vg'|'mu', turn:换了几幅, still:静帧, tint:{manga:0-100, notes:0-100}}。
 * 背景色调 tint：0 就是样式表原样；大于 0 时按 TINT 表把纸面变量往暖黄方向插值，写在 html 的行内样式上，文字和六色同步压深保住对比度。
 * 右下角浮钮打开「阅读面板」：目录 · 主题 · 背景色 · 学习时长，读到哪都能点。
 * 学习时长 study_time.js 也由这里带进每一页。 */
(function(){
  var KEY = 'pol_skin_v1', root = document.documentElement;
  var me = document.currentScript, BASE = me ? me.src.replace(/[^\/]*$/, '') : 'assets/';
  var VER = '3';
  var SKINS = [
    {id:'manga',   name:'日式漫画', desc:'墨线分格 · 网点 · 红笔判卷'},
    {id:'notes',   name:'手绘笔记', desc:'方格本 · 胶带 · 荧光笔手写'},
    {id:'gallery', name:'艺术画展', desc:'走进流动的画里 · 螺旋仪转场'}
  ];
  /* 展品：f＝镜头停靠点 [x, y, 推近倍数]，读到新的一节镜头就移到下一个 */
  var ART = {
    vg: {
      who:'文森特·梵高', hallName:'星夜厅',
      head:[
        {id:'starry', t:'星月夜',        y:1889, at:'纽约现代艺术博物馆',   f:[[.5,.42,1],[.44,.3,1.35],[.84,.2,1.5],[.2,.55,1.4],[.62,.76,1.45]]},
        {id:'rhone',  t:'罗讷河上的星夜', y:1888, at:'巴黎奥赛博物馆',      f:[[.5,.48,1],[.56,.22,1.35],[.36,.52,1.45],[.42,.76,1.35],[.82,.82,1.5]]},
        {id:'almond', t:'杏花',          y:1890, at:'阿姆斯特丹梵高博物馆', f:[[.5,.45,1],[.48,.32,1.4],[.24,.58,1.4],[.76,.3,1.45]]},
        {id:'irises', t:'鸢尾花',        y:1889, at:'洛杉矶盖蒂中心',      f:[[.5,.5,1],[.4,.42,1.4],[.72,.46,1.4],[.2,.7,1.4],[.84,.3,1.5]]},
        {id:'wheat',  t:'麦田与柏树',     y:1889, at:'伦敦国家美术馆',      f:[[.5,.45,1],[.72,.34,1.4],[.44,.18,1.4],[.3,.76,1.4]]}
      ]
    },
    mu: {
      who:'阿尔丰斯·慕夏', hallName:'金箔厅',
      head:[
        {id:'seasons',   t:'四季',      y:1896, f:[[.5,.4,1],[.13,.28,1.55],[.38,.28,1.55],[.63,.28,1.55],[.87,.28,1.55]]},
        {id:'stones',    t:'宝石四联',   y:1900, f:[[.5,.34,1],[.13,.24,1.6],[.38,.24,1.6],[.63,.24,1.6],[.87,.24,1.6]]},
        {id:'moonstars', t:'月亮与星辰', y:1902, f:[[.5,.34,1],[.13,.22,1.6],[.38,.22,1.6],[.63,.22,1.6],[.87,.22,1.6]]}
      ]
    }
  };
  var FONTS = {
    notes: ['https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkai-regular.css',
            'https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkai-bold.css',
            'https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Long+Cang&display=swap'],
    gallery: ['https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400;1,500;1,700&family=Noto+Serif+SC:wght@400;700;900&display=swap']
  };

  /* 背景色调的终点（滑到 100 时的值），起点从样式表读 */
  var TINT = {
    manga: {
      light: {'--paper':'#f1e3b8','--card':'#f9eecb','--card-solid':'#f9eecb','--bg':'#ecdcae','--bg2':'#dfcd98',
        '--ink2':'#33302a','--muted':'#5c564a',
        '--accent-soft':'#f8d4c0','--green':'#126a30','--green-soft':'#d6e8bc','--blue':'#164f9f','--blue-soft':'#d5e0dc',
        '--purple':'#6c30a6','--purple-soft':'#e8d6dc','--red':'#b81e14','--red-soft':'#f8d2c0',
        '--gold':'#6f4c00','--gold-soft':'#f6d98a','--orange':'#a84400','--orange-soft':'#f8d6a8',
        '--k-w':'#b01f14','--k-d':'#164f96','--k-t':'#7030a6','--k-m':'#106a38','--k-x':'#a84400','--k-n-bg':'#ffd24f'},
      dark: {'--paper':'#241c0d','--card':'#2e2514','--card-solid':'#2e2514','--bg':'#382e1a','--bg2':'#443822'}
    },
    notes: {
      light: {'--paper':'#efe1b4','--card':'#f8edc8','--card-solid':'#f8edc8','--bg':'#eadbab','--bg2':'#decd99',
        '--ink2':'#3d3f45','--muted':'#55544d',
        '--accent-soft':'#f8d6c4','--green':'#0f6740','--green-soft':'#d8e8bc','--blue':'#1b5192','--blue-soft':'#d6e2da',
        '--purple':'#62309f','--purple-soft':'#e8d8dc','--red':'#a32419','--red-soft':'#f8d4c4',
        '--gold':'#6f4f00','--gold-soft':'#f6da8c','--orange':'#933e00','--orange-soft':'#f8d8ac',
        '--k-w':'#a32419','--k-d':'#1a5092','--k-t':'#642ea0','--k-m':'#0f6740','--k-x':'#933e00','--k-n-bg':'#ffd24f','--mk1':'#ffd64a'},
      dark: {'--paper':'#2c2b1b','--card':'#353422','--card-solid':'#353422','--bg':'#3d3c28','--bg2':'#48462f'}
    }
  };
  var TINT_STOPS = [{t:0, n:'标准'}, {t:30, n:'米黄'}, {t:60, n:'杏黄'}, {t:100, n:'羊皮'}];

  function load(){ try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e){ return {}; } }
  var st = load();
  if (!SKINS.some(function(s){ return s.id === st.skin; })) st.skin = 'manga';
  st.hall = st.hall || 'auto'; st.turn = st.turn || 0; st.still = !!st.still; st.tint = cleanTint(st.tint);
  function cleanTint(o){
    var r = {manga:0, notes:0}; o = o || {};
    ['manga','notes'].forEach(function(k){ var v = +o[k]; if (v > 0) r[k] = Math.min(100, Math.round(v)); });
    return r;
  }
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(st)); } catch(e){} }

  /* 自动选厅：做题、首页走星夜（有劲），讲义、背诵走金箔（安静）；翻页时像走进另一个展厅 */
  function pagePath(){ try { return decodeURIComponent(location.pathname); } catch(e){ return location.pathname; } }
  function hallNow(){
    if (st.hall === 'vg' || st.hall === 'mu') return st.hall;
    return /\/(讲义|背诵|大题)\//.test(pagePath()) ? 'mu' : 'vg';
  }
  function hash(s){ var h = 7; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return h; }
  function pick(list, salt){ return list[(hash(pagePath()) + st.turn + (salt || 0)) % list.length]; }
  function reduced(){ return window.matchMedia('(prefers-reduced-motion: reduce)').matches; }

  var loaded = {};
  function fonts(skin){
    if (loaded[skin] || !FONTS[skin]) return; loaded[skin] = 1;
    FONTS[skin].forEach(function(u){
      var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = u; l.crossOrigin = 'anonymous'; document.head.appendChild(l);
    });
  }
  /* 背景色调 */
  var tintVars = {}, tintBase = {};
  Object.keys(TINT).forEach(function(s){ ['light','dark'].forEach(function(m){ Object.keys(TINT[s][m]).forEach(function(v){ tintVars[v] = 1; }); }); });
  function isDark(){
    var t = root.getAttribute('data-theme');
    return t ? t === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function clearTint(){ Object.keys(tintVars).forEach(function(v){ root.style.removeProperty(v); }); }
  function rgb(h){
    h = h.replace('#', ''); if (h.length === 3) h = h.replace(/./g, '$&$&');
    return [0, 2, 4].map(function(i){ return parseInt(h.substr(i, 2), 16); });
  }
  function mix(a, b, t){
    var x = rgb(a), y = rgb(b);
    return '#' + x.map(function(c, i){ var v = Math.round(c + (y[i] - c) * t).toString(16); return v.length < 2 ? '0' + v : v; }).join('');
  }
  function tintEnds(){ return TINT[st.skin] ? TINT[st.skin][isDark() ? 'dark' : 'light'] : null; }
  /* 起点从样式表读：先清掉行内值再读，读过的按「主题＋深浅」记住，拖滑杆时不用反复重算样式 */
  function baseOf(){
    var key = st.skin + (isDark() ? '-d' : '-l');
    if (tintBase[key]) return tintBase[key];
    clearTint();
    var cs = getComputedStyle(root), b = {};
    Object.keys(tintEnds()).forEach(function(v){ b[v] = cs.getPropertyValue(v).trim(); });
    if (/^#/.test(b['--paper'])) tintBase[key] = b;
    return b;
  }
  function paintTint(){
    var t = st.tint[st.skin] || 0, ends = tintEnds();
    if (!t || !ends){ clearTint(); return; }
    var b = baseOf();
    Object.keys(tintVars).forEach(function(v){
      if (ends[v] && /^#[0-9a-f]{3,6}$/i.test(b[v])) root.style.setProperty(v, mix(b[v], ends[v], t / 100));
      else root.style.removeProperty(v);
    });
  }
  /* 定主题：只动 html 上的属性和变量，所以切换不用刷新、也不影响做题状态 */
  function paint(){ paintSkin(); paintTint(); }
  function paintSkin(){
    if (st.skin === 'manga'){ root.removeAttribute('data-skin'); root.removeAttribute('data-hall'); root.removeAttribute('data-gx-still'); root.style.removeProperty('--art'); return; }
    root.setAttribute('data-skin', st.skin);
    fonts(st.skin);
    if (st.skin === 'gallery'){
      var h = hallNow(), a = pick(ART[h].head);
      root.setAttribute('data-hall', h);
      root.style.setProperty('--art', 'url("' + BASE + 'skin/art/' + a.id + '.webp")');
      if (st.still || reduced()) root.setAttribute('data-gx-still', ''); else root.removeAttribute('data-gx-still');
    } else {
      root.removeAttribute('data-hall'); root.removeAttribute('data-gx-still'); root.style.removeProperty('--art');
    }
  }
  paint();
  /* 上一页走的是螺旋仪转场：首屏先停在合拢的光圈上，等 gallery.js 接手打开 */
  try {
    var go = +sessionStorage.getItem('gx_go') || 0;
    if (st.skin === 'gallery' && Date.now() - go < 4000 && !st.still && !reduced()) root.setAttribute('data-gx-arrive', '');
    sessionStorage.removeItem('gx_go');
  } catch(e){}

  /* ===== 给 gallery.js 用的接口 ===== */
  var gallery = null, galleryLoading = false;
  window.PolSkin = {
    ART:ART, BASE:BASE, st:st, hall:hallNow, pick:pick,
    turn:function(){ turn(); },
    register:function(g){ gallery = g; galleryLoading = false; if (st.skin === 'gallery') g.enter(); }
  };
  function syncGallery(){
    if (st.skin === 'gallery'){
      if (gallery) gallery.enter();
      else if (!galleryLoading){
        galleryLoading = true;
        var s = document.createElement('script'); s.src = BASE + 'gallery.js?v=' + VER;
        s.onerror = function(){ root.removeAttribute('data-gx-arrive'); root.setAttribute('data-gx-static', ''); };
        document.head.appendChild(s);
      }
    } else if (gallery) gallery.leave();
  }

  /* ===== DOM 就绪后：挂切换钮、展签 ===== */
  function esc(s){ return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function clean(){ document.querySelectorAll('.skin-plate,.skin-doodle').forEach(function(n){ n.remove(); }); }
  function decorate(){
    clean();
    if (st.skin === 'gallery'){
      var h = hallNow(), a = pick(ART[h].head), head = document.querySelector('.wrap header');
      if (head){
        var p = document.createElement('button'); p.type = 'button'; p.className = 'skin-plate';
        p.title = '换一幅';
        p.innerHTML = '<b>《' + esc(a.t) + '》</b><span>' + esc(ART[h].who) + ' · ' + a.y + (a.at ? ' · ' + esc(a.at) : '') + '</span><i>换一幅</i>';
        p.onclick = function(){ turn(); };
        head.appendChild(p);
      }
    }
    if (st.skin === 'notes'){
      var hd = document.querySelector('.wrap header');
      if (hd){ var d = document.createElement('i'); d.className = 'skin-doodle'; d.setAttribute('aria-hidden', 'true'); hd.appendChild(d); }
    }
    var tc = {manga:'#e2231a', notes:root.style.getPropertyValue('--paper') || '#f7f4ea', gallery: hallNow() === 'vg' ? '#0a1026' : '#f6eeda'}[st.skin];
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.content = tc;
    syncGallery();
  }
  function apply(fn){
    var go = function(){ fn(); paint(); decorate(); syncPanel(); save(); };
    if (document.startViewTransition && !reduced()){ root.classList.add('gx-vt'); var vt = document.startViewTransition(go); vt.ready.catch(function(){}); vt.finished.catch(function(){}).then(function(){ root.classList.remove('gx-vt'); }); } else go();
  }
  /* 换一幅不走整页转场：画面自己溶过去，只改展签 */
  function turn(){
    st.turn = (st.turn + 1) % 840; save();
    if (st.skin === 'gallery' && gallery){ paint(); decorate(); gallery.painting(); return; }
    paint(); decorate();
  }

  /* 阅读面板：右下角浮钮常驻，顶部「主题」钮打开的也是它 */
  var chip, panel, fab, opener, tocLinks = [], tintTimer;
  function esc2(s){ return esc(s).replace(/"/g, '&quot;'); }
  function syncPanel(){
    if (!panel) return;
    panel.querySelectorAll('[data-s]').forEach(function(b){
      var on = b.dataset.s === st.skin; b.classList.toggle('on', on); b.setAttribute('aria-checked', on ? 'true' : 'false');
    });
    panel.querySelectorAll('[data-h]').forEach(function(b){ b.classList.toggle('on', b.dataset.h === st.hall); });
    panel.querySelectorAll('[data-m]').forEach(function(b){ b.classList.toggle('on', (b.dataset.m === 'still') === st.still); });
    panel.querySelector('.skin-hall').hidden = st.skin !== 'gallery';
    var box = panel.querySelector('.dock-tint'), ends = tintEnds();
    box.hidden = !ends;
    if (ends) syncTint(box, ends);
  }
  function syncTint(box, ends){
    var t = st.tint[st.skin] || 0, r = box.querySelector('input'), stop = TINT_STOPS.filter(function(x){ return x.t === t; })[0];
    r.value = t;
    r.setAttribute('aria-valuetext', stop ? stop.n : t + '%');
    r.style.setProperty('--a', baseOf0(ends));
    r.style.setProperty('--b', ends['--paper']);
    box.querySelector('.dock-val').textContent = stop ? stop.n + (t ? '' : '（默认）') : '偏黄 ' + t + '%';
    box.querySelectorAll('[data-t]').forEach(function(b){ b.classList.toggle('on', +b.dataset.t === t); });
  }
  /* 滑杆的起点色：有缓存直接用，没缓存时读一次（只在面板打开时发生） */
  function baseOf0(ends){
    var b = tintBase[st.skin + (isDark() ? '-d' : '-l')];
    if (!b){ b = baseOf(); paintTint(); }
    return b['--paper'] || ends['--paper'];
  }
  function setTint(v){
    st.tint[st.skin] = Math.max(0, Math.min(100, Math.round(v)));
    paintTint();
    var m = document.querySelector('meta[name="theme-color"]');
    if (m && st.skin === 'notes') m.content = root.style.getPropertyValue('--paper') || '#f7f4ea';
    syncPanel();
    clearTimeout(tintTimer); tintTimer = setTimeout(save, 200);
  }
  function sections(){
    return [].slice.call(document.querySelectorAll('section.card[id]')).filter(function(s){ return s.querySelector('h2'); });
  }
  function fillToc(){
    var box = panel.querySelector('.dock-toc'), secs = sections();
    box.hidden = secs.length < 4;
    if (box.hidden){ tocLinks = []; return; }
    box.innerHTML = '<div class="dock-h">目录</div>' + secs.map(function(s){
      var h = s.querySelector('h2'), no = h.querySelector('.no'), all = h.textContent.trim();
      var txt = no ? all.slice(no.textContent.length).trim() : all;
      return '<a href="#' + esc2(s.id) + '">' + (no ? '<i>' + esc(no.textContent) + '</i>' : '') + esc(txt) + '</a>';
    }).join('');
    tocLinks = [].slice.call(box.querySelectorAll('a')).map(function(a, i){ return {a:a, s:secs[i]}; });
  }
  /* 读到哪一节就亮哪一节，并把它滚进目录的可视范围 */
  function markToc(){
    if (!tocLinks.length || panel.hidden) return;
    var line = innerHeight * .35, cur = tocLinks[0];
    tocLinks.forEach(function(x){ if (x.s.getBoundingClientRect().top <= line) cur = x; });
    tocLinks.forEach(function(x){ x.a.classList.toggle('on', x === cur); });
    var box = panel.querySelector('.dock-toc'), a = cur.a;
    if (a.offsetTop < box.scrollTop || a.offsetTop + a.offsetHeight > box.scrollTop + box.clientHeight)
      box.scrollTop = a.offsetTop - box.clientHeight / 2;
  }
  function fillTime(){
    var box = panel.querySelector('.dock-time'), T = window.PolTime;
    box.hidden = !T; if (!T) return;
    var s = T.stats();
    box.querySelector('summary').innerHTML = '<span>今日 <b>' + T.fmt(s.today) + '</b></span><span>累计 <b>' + T.fmt(s.total) + '</b></span><span>连续 <b>' + s.streak + ' 天</b></span>';
    var d = box.querySelector('details');
    if (d.open && !d.querySelector('u:hover,u:focus')) box.querySelector('.dock-tm').innerHTML = T.panel();
  }
  function place(){
    var r = fab.getBoundingClientRect(), gap = 10, bottom = innerHeight - r.top + gap;
    panel.style.bottom = bottom + 'px';
    panel.style.maxHeight = (innerHeight - bottom - 10) + 'px';
  }
  function toggle(open, from){
    panel.hidden = !open;
    fab.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (chip) chip.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open){ opener = from; fillToc(); fillTime(); syncPanel(); place(); markToc(); }
  }
  function build(){
    chip = document.createElement('button'); chip.type = 'button'; chip.className = 'skin-chip';
    chip.setAttribute('aria-haspopup', 'dialog'); chip.setAttribute('aria-expanded', 'false');
    chip.innerHTML = '<span aria-hidden="true">🎨</span> 主题';
    var host = document.querySelector('.wrap .sitebar') || document.querySelector('.wrap .crumb');
    if (host) host.appendChild(chip); else { chip.classList.add('solo'); document.body.appendChild(chip); }

    panel = document.createElement('div'); panel.className = 'skin-panel'; panel.hidden = true;
    panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', '阅读面板：目录、主题、背景色、学习时长');
    panel.innerHTML = '<div class="dock-time" hidden><details><summary></summary><div class="dock-tm"></div></details></div>'
      + '<nav class="dock-toc" aria-label="本页目录" hidden></nav>'
      + '<div class="dock-look">'
      + '<div class="dock-tint" hidden><div class="dock-h">背景色 <span class="dock-val"></span></div>'
      + '<input type="range" min="0" max="100" step="1" aria-label="背景偏黄程度">'
      + '<div class="dock-stops">' + TINT_STOPS.map(function(x){ return '<button type="button" data-t="' + x.t + '">' + x.n + '</button>'; }).join('') + '</div></div>'
      + '<div class="skin-opts" role="radiogroup" aria-label="主题">' + SKINS.map(function(s){
          return '<button type="button" role="radio" data-s="' + s.id + '" title="' + s.desc + '"><i class="skin-thumb t-' + s.id + '"' + (s.id === 'gallery' ? ' style="background-image:url(&quot;' + BASE + 'skin/art/starry.webp&quot;)"' : '') + '></i><b>' + s.name + '</b></button>';
        }).join('') + '</div>'
      + '<div class="skin-hall" hidden><span>展厅</span><button type="button" data-h="auto">自动</button><button type="button" data-h="vg">星夜</button><button type="button" data-h="mu">金箔</button><button type="button" class="skin-next">换一幅</button>'
      + '<span class="skin-brk">画面</span><button type="button" data-m="flow">流动</button><button type="button" data-m="still">静帧</button></div>'
      + '<p class="dock-note">只改样子，做题记录不受影响</p></div>';
    document.body.appendChild(panel);

    /* 有目录的页是「☰ 目录」，没有目录的页（刷题、答题卡）缩成不挡内容的小钮 */
    var hasToc = sections().length >= 4;
    fab = document.createElement('button'); fab.type = 'button'; fab.className = 'fab' + (hasToc ? '' : ' mini');
    fab.setAttribute('aria-haspopup', 'dialog'); fab.setAttribute('aria-expanded', 'false');
    fab.setAttribute('aria-label', hasToc ? '目录、主题、背景色' : '主题、背景色');
    fab.title = hasToc ? '目录 · 主题 · 背景色 · 学习时长' : '主题 · 背景色 · 学习时长';
    fab.textContent = hasToc ? '☰ 目录' : '🎨';
    document.body.appendChild(fab);

    chip.onclick = function(e){ e.stopPropagation(); toggle(panel.hidden, chip); };
    fab.onclick = function(e){ e.stopPropagation(); toggle(panel.hidden, fab); };
    panel.addEventListener('click', function(e){
      if (e.target.closest('.dock-toc a')){ toggle(false); return; }
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.s) apply(function(){ st.skin = b.dataset.s; });
      else if (b.dataset.t != null) setTint(+b.dataset.t);
      else if (b.dataset.h) apply(function(){ st.hall = b.dataset.h; });
      else if (b.dataset.m){ st.still = b.dataset.m === 'still'; paint(); syncPanel(); save(); if (gallery) gallery.motion(); }
      else if (b.classList.contains('skin-next')) turn();
    });
    panel.querySelector('.dock-tint input').addEventListener('input', function(e){ setTint(+e.target.value); });
    panel.querySelector('.dock-time details').addEventListener('toggle', function(){ fillTime(); });
    document.addEventListener('click', function(e){ if (!panel.hidden && !e.target.closest('.skin-panel,.skin-chip,.fab')) toggle(false); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && !panel.hidden){ toggle(false); if (opener) opener.focus(); } });
    /* 面板开着可以继续滚动：边读边调背景，目录跟着亮 */
    var ticking = false;
    window.addEventListener('scroll', function(){
      if (panel.hidden || ticking) return; ticking = true;
      requestAnimationFrame(function(){ ticking = false; markToc(); });
    }, {passive:true});
    window.addEventListener('resize', function(){ if (!panel.hidden) place(); });
    setInterval(function(){ if (!panel.hidden) fillTime(); }, 5000);
    /* 背诵模式的工具条会把浮钮顶上去，面板要跟着 */
    new MutationObserver(function(){ if (!panel.hidden) setTimeout(place, 320); }).observe(document.body, {attributes:true, attributeFilter:['class']});
    syncPanel();
  }
  function ready(){
    build(); decorate();
    var t = document.createElement('script'); t.src = BASE + 'study_time.js?v=' + VER; document.head.appendChild(t);
  }
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(){ paintTint(); syncPanel(); });
  if (document.readyState !== 'loading') ready(); else document.addEventListener('DOMContentLoaded', ready);
  window.addEventListener('storage', function(e){
    if (e.key !== KEY) return;
    var n = load(); st.skin = n.skin || 'manga'; st.hall = n.hall || 'auto'; st.turn = n.turn || 0; st.still = !!n.still; st.tint = cleanTint(n.tint);
    paint(); decorate(); syncPanel();
  });
})();

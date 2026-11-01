/* 政治复盘中心 · 主题切换（放在 <head> 里同步执行，抢在首屏绘制前定好主题，避免闪一下）
 * 三个主题：manga 日式漫画（默认，就是 style.css 本身）· notes 手绘学习笔记 · gallery 艺术画展
 * html[data-skin] 决定主题；画展再加 html[data-hall]：vg 星夜厅 / mu 金箔厅。样式全在 skin.css，
 * 画展的场景（WebGL 画面、螺旋仪、联动）在 gallery.js，只有进画展才加载。
 * 存在本机：pol_skin_v1 = {skin, hall:'auto'|'vg'|'mu', turn:换了几幅, still:静帧}。
 * 学习时长 study_time.js 也由这里带进每一页。 */
(function(){
  var KEY = 'pol_skin_v1', root = document.documentElement;
  var me = document.currentScript, BASE = me ? me.src.replace(/[^\/]*$/, '') : 'assets/';
  var VER = '2';
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

  function load(){ try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e){ return {}; } }
  var st = load();
  if (!SKINS.some(function(s){ return s.id === st.skin; })) st.skin = 'manga';
  st.hall = st.hall || 'auto'; st.turn = st.turn || 0; st.still = !!st.still;
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
  /* 定主题：只动 html 上的属性和变量，所以切换不用刷新、也不影响做题状态 */
  function paint(){
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
    var tc = {manga:'#e2231a', notes:'#f7f4ea', gallery: hallNow() === 'vg' ? '#0a1026' : '#f6eeda'}[st.skin];
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

  /* 切换面板 */
  var chip, panel;
  function syncPanel(){
    if (!panel) return;
    panel.querySelectorAll('[data-s]').forEach(function(b){
      var on = b.dataset.s === st.skin; b.classList.toggle('on', on); b.setAttribute('aria-checked', on ? 'true' : 'false');
    });
    panel.querySelectorAll('[data-h]').forEach(function(b){ b.classList.toggle('on', b.dataset.h === st.hall); });
    panel.querySelectorAll('[data-m]').forEach(function(b){ b.classList.toggle('on', (b.dataset.m === 'still') === st.still); });
    panel.querySelector('.skin-hall').hidden = st.skin !== 'gallery';
  }
  function build(){
    chip = document.createElement('button'); chip.type = 'button'; chip.className = 'skin-chip';
    chip.setAttribute('aria-haspopup', 'dialog'); chip.setAttribute('aria-expanded', 'false');
    chip.innerHTML = '<span aria-hidden="true">🎨</span> 主题';
    var host = document.querySelector('.wrap .sitebar') || document.querySelector('.wrap .crumb');
    if (host) host.appendChild(chip); else { chip.classList.add('solo'); document.body.appendChild(chip); }

    panel = document.createElement('div'); panel.className = 'skin-panel'; panel.hidden = true;
    panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', '切换主题');
    panel.innerHTML = '<div class="skin-ttl">换一个主题 <span>只改样子，做题记录不受影响</span></div>'
      + '<div class="skin-opts" role="radiogroup">' + SKINS.map(function(s){
          return '<button type="button" role="radio" data-s="' + s.id + '"><i class="skin-thumb t-' + s.id + '"' + (s.id === 'gallery' ? ' style="background-image:url(&quot;' + BASE + 'skin/art/starry.webp&quot;)"' : '') + '></i><b>' + s.name + '</b><small>' + s.desc + '</small></button>';
        }).join('') + '</div>'
      + '<div class="skin-hall" hidden><span>展厅</span><button type="button" data-h="auto">自动</button><button type="button" data-h="vg">星夜</button><button type="button" data-h="mu">金箔</button><button type="button" class="skin-next">换一幅</button>'
      + '<span class="skin-brk">画面</span><button type="button" data-m="flow">流动</button><button type="button" data-m="still">静帧</button></div>';
    document.body.appendChild(panel);

    function toggle(open){
      panel.hidden = !open; chip.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open){
        var r = chip.getBoundingClientRect(), w = panel.offsetWidth;
        panel.style.top = Math.max(8, r.bottom + 8) + 'px';
        panel.style.left = Math.max(10, Math.min(innerWidth - w - 10, r.right - w)) + 'px';
      }
    }
    chip.onclick = function(e){ e.stopPropagation(); toggle(panel.hidden); };
    panel.addEventListener('click', function(e){
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.s) apply(function(){ st.skin = b.dataset.s; });
      else if (b.dataset.h) apply(function(){ st.hall = b.dataset.h; });
      else if (b.dataset.m){ st.still = b.dataset.m === 'still'; paint(); syncPanel(); save(); if (gallery) gallery.motion(); }
      else if (b.classList.contains('skin-next')) turn();
    });
    document.addEventListener('click', function(e){ if (!panel.hidden && !e.target.closest('.skin-panel,.skin-chip')) toggle(false); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && !panel.hidden){ toggle(false); chip.focus(); } });
    window.addEventListener('scroll', function(){ if (!panel.hidden) toggle(false); }, {passive:true});
    syncPanel();
  }
  function ready(){
    build(); decorate();
    var t = document.createElement('script'); t.src = BASE + 'study_time.js?v=' + VER; document.head.appendChild(t);
  }
  if (document.readyState !== 'loading') ready(); else document.addEventListener('DOMContentLoaded', ready);
  window.addEventListener('storage', function(e){
    if (e.key !== KEY) return;
    var n = load(); st.skin = n.skin || 'manga'; st.hall = n.hall || 'auto'; st.turn = n.turn || 0; st.still = !!n.still;
    paint(); decorate(); syncPanel();
  });
})();

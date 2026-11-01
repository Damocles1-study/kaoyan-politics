/* 政治复盘中心 · 主题切换（放在 <head> 里同步执行，抢在首屏绘制前定好主题，避免闪一下）
 * 三个主题：manga 日式漫画（默认，就是 style.css 本身）· notes 手绘学习笔记 · gallery 艺术画展
 * html[data-skin] 决定主题；画展再加 html[data-hall]：vg 梵高厅 / mu 慕夏厅。样式全在 skin.css。
 * 存在本机：pol_skin_v1 = {skin, hall:'auto'|'vg'|'mu', turn:换了几幅}。 */
(function(){
  var KEY = 'pol_skin_v1', root = document.documentElement;
  var me = document.currentScript, BASE = me ? me.src.replace(/[^\/]*$/, '') : 'assets/';
  var SKINS = [
    {id:'manga',   name:'日式漫画', desc:'墨线分格 · 网点 · 红笔判卷'},
    {id:'notes',   name:'手绘笔记', desc:'方格本 · 胶带 · 荧光笔手写'},
    {id:'gallery', name:'艺术画展', desc:'梵高厅 · 慕夏厅 · 画框展签'}
  ];
  /* 展品：pos＝页眉里取景的焦点；tall＝竖幅，宽屏时挂在页面两侧的墙上 */
  var ART = {
    vg: {
      who:'文森特·梵高', en:'Vincent van Gogh',
      head:[
        {id:'starry',    t:'星月夜',       y:1889, at:'纽约现代艺术博物馆', pos:'50% 22%'},
        {id:'rhone',     t:'罗讷河上的星夜', y:1888, at:'巴黎奥赛博物馆',    pos:'50% 38%'},
        {id:'almond',    t:'杏花',         y:1890, at:'阿姆斯特丹梵高博物馆', pos:'55% 30%'},
        {id:'irises',    t:'鸢尾花',       y:1889, at:'洛杉矶盖蒂中心',    pos:'60% 40%'},
        {id:'wheat',     t:'麦田与柏树',    y:1889, at:'伦敦国家美术馆',    pos:'70% 42%'}
      ],
      tall:[
        {id:'cafe',      t:'夜间咖啡馆露台', y:1888, at:'奥特洛库勒-慕勒博物馆'},
        {id:'sunflower', t:'向日葵',       y:1888, at:'伦敦国家美术馆'}
      ]
    },
    mu: {
      who:'阿尔丰斯·慕夏', en:'Alphonse Mucha',
      head:[
        {id:'seasons',   t:'四季',       y:1896, pos:'50% 26%'},
        {id:'stones',    t:'宝石四联',    y:1900, pos:'50% 18%'},
        {id:'moonstars', t:'月亮与星辰',  y:1902, pos:'50% 12%'},
        {id:'zodiac',    t:'黄道十二宫',  y:1896, pos:'50% 42%'}
      ],
      tall:[
        {id:'spring',  t:'春（四季之一）',  y:1896},
        {id:'autumn',  t:'秋（四季之一）',  y:1896},
        {id:'summer',  t:'夏（四季之一）',  y:1896},
        {id:'winter',  t:'冬（四季之一）',  y:1896},
        {id:'ruby',    t:'红宝石',        y:1900},
        {id:'emerald', t:'祖母绿',        y:1900}
      ]
    }
  };
  var FONTS = {
    notes: ['https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkai-regular.css',
            'https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/lxgwwenkai-bold.css',
            'https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Long+Cang&display=swap'],
    gallery: ['https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;1,500;1,700&family=Noto+Serif+SC:wght@400;700;900&display=swap']
  };

  function load(){ try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e){ return {}; } }
  var st = load();
  if (!SKINS.some(function(s){ return s.id === st.skin; })) st.skin = 'manga';
  st.hall = st.hall || 'auto'; st.turn = st.turn || 0;
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(st)); } catch(e){} }

  /* 自动选厅：做题、首页走梵高（有劲），讲义、背诵走慕夏（安静）；两厅各看各的，翻页时像换展厅 */
  function pagePath(){ try { return decodeURIComponent(location.pathname); } catch(e){ return location.pathname; } }
  function hallNow(){
    if (st.hall === 'vg' || st.hall === 'mu') return st.hall;
    return /\/(讲义|背诵|大题)\//.test(pagePath()) ? 'mu' : 'vg';
  }
  function hash(s){ var h = 7; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return h; }
  function pick(list, salt){ return list[(hash(pagePath()) + st.turn + (salt || 0)) % list.length]; }
  function src(id){ return BASE + 'skin/art/' + id + '.webp'; }

  var loaded = {};
  function fonts(skin){
    if (loaded[skin] || !FONTS[skin]) return; loaded[skin] = 1;
    FONTS[skin].forEach(function(u){
      var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = u; l.crossOrigin = 'anonymous'; document.head.appendChild(l);
    });
  }
  /* 定主题：只动 html 上的属性和变量，所以切换不用刷新、也不影响做题状态 */
  function paint(){
    if (st.skin === 'manga'){ root.removeAttribute('data-skin'); root.removeAttribute('data-hall'); root.style.removeProperty('--art'); root.style.removeProperty('--art-pos'); root.style.removeProperty('--wall-art'); return; }
    root.setAttribute('data-skin', st.skin);
    fonts(st.skin);
    if (st.skin === 'gallery'){
      var h = hallNow(), a = pick(ART[h].head);
      root.setAttribute('data-hall', h);
      root.style.setProperty('--art', 'url("' + src(a.id) + '")');
      root.style.setProperty('--art-pos', a.pos || '50% 50%');
      root.style.setProperty('--wall-art', 'url("' + src('wall-vg') + '")');
    } else {
      root.removeAttribute('data-hall'); root.style.removeProperty('--art'); root.style.removeProperty('--art-pos'); root.style.removeProperty('--wall-art');
    }
  }
  paint();

  /* ===== DOM 就绪后：挂切换钮、展签、两侧墙上的画 ===== */
  function esc(s){ return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function plate(a, h){ return '<b>《' + esc(a.t) + '》</b><span>' + esc(ART[h].who) + ' · ' + a.y + (a.at ? ' · ' + esc(a.at) : '') + '</span>'; }
  function clean(){ document.querySelectorAll('.skin-plate,.skin-wall,.skin-doodle').forEach(function(n){ n.remove(); }); }
  function decorate(){
    clean();
    if (st.skin === 'gallery'){
      var h = hallNow(), a = pick(ART[h].head), head = document.querySelector('.wrap header');
      if (head){
        var p = document.createElement('button'); p.type = 'button'; p.className = 'skin-plate';
        p.title = '换一幅'; p.innerHTML = plate(a, h) + '<i>↻ 换一幅</i>';
        p.onclick = function(){ turn(); };
        head.appendChild(p);
      }
      /* 宽屏才有墙：两幅竖画分挂左右，可点开原图比例看（skin.css 里窄屏隐藏，图片也不会下载） */
      if (window.matchMedia('(min-width:1400px)').matches){
        var t = ART[h].tall;
        [['l', 0], ['r', 1]].forEach(function(x){
          var w = pick(t, x[1]), f = document.createElement('figure');
          f.className = 'skin-wall ' + x[0];
          f.innerHTML = '<img alt="' + esc(w.t) + '" loading="lazy" src="' + src(w.id) + '"><figcaption>' + plate(w, h) + '</figcaption>';
          document.body.appendChild(f);
        });
      }
    }
    if (st.skin === 'notes'){
      var hd = document.querySelector('.wrap header');
      if (hd){ var d = document.createElement('i'); d.className = 'skin-doodle'; d.setAttribute('aria-hidden', 'true'); hd.appendChild(d); }
    }
    var tc = {manga:'#e2231a', notes:'#f7f4ea', gallery: hallNow() === 'vg' ? '#14285a' : '#f3e7cf'}[st.skin];
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.content = tc;
  }
  function apply(fn){
    var go = function(){ fn(); paint(); decorate(); syncPanel(); save(); };
    if (document.startViewTransition && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) document.startViewTransition(go); else go();
  }
  function turn(){ apply(function(){ st.turn = (st.turn + 1) % 840; }); }

  /* 切换面板 */
  var chip, panel;
  function syncPanel(){
    if (!panel) return;
    panel.querySelectorAll('[data-s]').forEach(function(b){
      var on = b.dataset.s === st.skin; b.classList.toggle('on', on); b.setAttribute('aria-checked', on ? 'true' : 'false');
    });
    panel.querySelectorAll('[data-h]').forEach(function(b){ b.classList.toggle('on', b.dataset.h === st.hall); });
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
          return '<button type="button" role="radio" data-s="' + s.id + '"><i class="skin-thumb t-' + s.id + '"' + (s.id === 'gallery' ? ' style="background-image:url(&quot;' + src('starry') + '&quot;)"' : '') + '></i><b>' + s.name + '</b><small>' + s.desc + '</small></button>';
        }).join('') + '</div>'
      + '<div class="skin-hall" hidden><span>展厅</span><button type="button" data-h="auto">自动</button><button type="button" data-h="vg">梵高</button><button type="button" data-h="mu">慕夏</button><button type="button" class="skin-next">↻ 换一幅</button></div>';
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
      else if (b.classList.contains('skin-next')) turn();
    });
    document.addEventListener('click', function(e){ if (!panel.hidden && !e.target.closest('.skin-panel,.skin-chip')) toggle(false); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && !panel.hidden){ toggle(false); chip.focus(); } });
    window.addEventListener('scroll', function(){ if (!panel.hidden) toggle(false); }, {passive:true});
    syncPanel();
  }
  function ready(){ build(); decorate(); }
  if (document.readyState !== 'loading') ready(); else document.addEventListener('DOMContentLoaded', ready);
  window.addEventListener('storage', function(e){
    if (e.key !== KEY) return;
    var n = load(); st.skin = n.skin || 'manga'; st.hall = n.hall || 'auto'; st.turn = n.turn || 0;
    paint(); decorate(); syncPanel();
  });
})();

/* 政治复盘中心 · 各页共用：六色图例、背诵模式（关键词挖空遮挡）、目录浮钮、分段控件滑块 */
(function(){
  var LEG = '<span class="kw">红·必背结论</span><span class="kd">蓝·概念定义</span><span class="kt">紫·时间人物著作会议</span>'
          + '<span class="km">绿·方法论与做法</span><span class="kx">橙·易混易错</span><span class="kn">金·数字口诀</span>';
  var KW = '.kw,.kd,.kt,.km,.kx,.kn,u.k';
  var COLORS = [['kw','红·必背'],['kd','蓝·概念'],['kt','紫·时人著'],['km','绿·方法'],['kx','橙·易错'],['kn','金·数字']];
  function ready(fn){ document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }
  function load(k, d){ try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch(e){ return d; } }
  function save(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} }

  /* 分段控件：给 .seg 加一个跟着 .on 滑动的白色滑块（iOS Segmented Control 手感） */
  function seg(el){
    if (!el || el._seg) return; el._seg = 1;
    var th = document.createElement('span'); th.className = 'thumb'; el.insertBefore(th, el.firstChild);
    function place(anim){
      var b = el.querySelector('button.on');
      if (!b || !b.offsetWidth){ th.style.opacity = 0; return; }
      th.style.opacity = 1;
      if (!anim) th.style.transition = 'none';
      th.style.width = b.offsetWidth + 'px'; th.style.transform = 'translateX(' + b.offsetLeft + 'px)';
      if (!anim){ void th.offsetWidth; th.style.transition = ''; }
    }
    place(false); el.classList.add('ready');
    new MutationObserver(function(){ place(true); }).observe(el, {subtree:true, attributes:true, attributeFilter:['class']});
    if (window.ResizeObserver) new ResizeObserver(function(){ place(false); }).observe(el);
    else window.addEventListener('resize', function(){ place(false); });
  }
  window.PolUI = { seg: seg };

  /* 背诵模式：彩色关键词变成同色「挖空条」，点一下揭开；可按颜色筛选、随机遮一半、逐个揭开 */
  function recite(){
    var st = load('pol_recite_v2', null);
    if (!st){ st = {on: load('pol_hidekw', 0) == 1, colors: {kw:1,kd:1,kt:1,km:1,kx:1,kn:1}, half: 0}; }
    var els = [].slice.call(document.querySelectorAll(KW)).filter(function(el){
      return !el.closest('.legend,.rtool,.sitebar') && !el.parentElement.closest(KW);
    });
    if (!els.length) return null;
    els.forEach(function(el){ el._c = el.matches('u.k') ? 'kw' : (COLORS.filter(function(c){ return el.classList.contains(c[0]); })[0] || ['kw'])[0]; });
    var tool = null;

    function masked(){ return els.filter(function(el){ return el.classList.contains('rv'); }); }
    function count(){
      if (!tool) return;
      var m = masked(), s = m.filter(function(el){ return el.classList.contains('shown'); }).length;
      tool.querySelector('.cnt').innerHTML = '已揭开 <b>' + s + '</b> / ' + m.length;
      tool.querySelector('.bar i').style.width = (m.length ? 100 * s / m.length : 0) + '%';
    }
    function apply(){
      document.body.classList.toggle('recite', !!st.on);
      els.forEach(function(el){
        var on = st.on && st.colors[el._c] && (!st.half || el._half);
        el.classList.toggle('rv', !!on); el.classList.remove('shown');
      });
      if (st.on && !tool) buildTool(); else if (!st.on && tool){ tool.remove(); tool = null; }
      if (tool){
        tool.querySelectorAll('.chip[data-c]').forEach(function(b){ b.classList.toggle('on', !!st.colors[b.dataset.c]); });
        tool.querySelector('.half').classList.toggle('on', !!st.half);
      }
      var rb = document.getElementById('reciteBtn'); if (rb) rb.textContent = st.on ? '✓ 背诵中' : '🙈 背诵模式';
      count(); save('pol_recite_v2', st);
    }
    function reroll(){ els.forEach(function(el){ el._half = Math.random() < .5; }); }
    function next(){
      var m = masked().filter(function(el){ return !el.classList.contains('shown'); });
      if (!m.length) return;
      var el = m.filter(function(x){ return x.getBoundingClientRect().bottom > 80; })[0] || m[0];
      el.classList.add('shown'); count();
      var r = el.getBoundingClientRect();
      if (r.top < 70 || r.bottom > innerHeight - 170) el.scrollIntoView({block:'center', behavior:'smooth'});
    }
    function buildTool(){
      tool = document.createElement('div'); tool.className = 'rtool';
      tool.innerHTML = '<div class="row1">' + COLORS.map(function(c){ return '<button class="chip" data-c="' + c[0] + '" style="--mc:var(' + (c[0] === 'kn' ? '--gold' : '--k-' + c[0].slice(1)) + ')">' + c[1] + '</button>'; }).join('')
        + '<button class="chip half" style="--mc:var(--ink2)">🎲 随机遮一半</button></div>'
        + '<div class="row2"><span class="cnt"></span><span class="bar"><i></i></span>'
        + '<button class="btn sm pri" data-a="next">揭开下一个</button><button class="btn sm" data-a="all">全揭开</button>'
        + '<button class="btn sm" data-a="reset">重新遮住</button><button class="btn sm x" data-a="off">完成</button></div>';
      document.body.appendChild(tool);
      tool.addEventListener('click', function(e){
        var c = e.target.closest('.chip'), a = e.target.closest('[data-a]');
        if (c && c.dataset.c){ st.colors[c.dataset.c] = st.colors[c.dataset.c] ? 0 : 1; apply(); }
        else if (c){ st.half = st.half ? 0 : 1; if (st.half) reroll(); apply(); }
        else if (a){
          var k = a.dataset.a;
          if (k === 'next') next();
          else if (k === 'all'){ masked().forEach(function(el){ el.classList.add('shown'); }); count(); }
          else if (k === 'reset'){ if (st.half) reroll(); apply(); }
          else if (k === 'off'){ st.on = false; apply(); }
        }
      });
    }
    document.addEventListener('click', function(e){
      if (!st.on) return;
      var t = e.target.closest('.rv'); if (!t) return;
      e.preventDefault(); t.classList.toggle('shown'); count();
    });
    document.addEventListener('keydown', function(e){
      if (!st.on || /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
      if (e.key === 'n' || e.key === 'N' || e.key === 'j'){ next(); e.preventDefault(); }
    });
    reroll(); apply();
    return function(){ st.on = !st.on; apply(); };
  }

  ready(function(){
    // 1) 图例：页面里有 #legend 就填进去；讲义页没有就插在页眉后
    var lg = document.getElementById('legend');
    if (!lg && document.querySelector('.lec header')) {
      lg = document.createElement('div'); lg.id = 'legend';
      document.querySelector('.lec header').insertAdjacentElement('afterend', lg);
    }
    if (lg) { lg.className = 'legend'; lg.innerHTML = '<b>关键词颜色：</b>' + LEG + '<button class="btn sm recite-btn" id="reciteBtn">🙈 背诵模式</button>'; }

    // 2) 背诵模式（有图例的页才开放）
    if (lg) { var tog = recite(); var rb = document.getElementById('reciteBtn'); if (tog) rb.onclick = tog; else rb.remove(); }

    // 3) 目录浮钮（有 ≥4 个带 id 的卡片时出现）
    var secs = [].slice.call(document.querySelectorAll('section.card[id]'));
    if (secs.length >= 4) {
      var b = document.createElement('button'); b.className = 'fab'; b.textContent = '☰ 目录';
      var pop = document.createElement('div'); pop.className = 'tocpop'; pop.hidden = true;
      pop.innerHTML = secs.map(function(s){ var h = s.querySelector('h2'); return h ? '<a href="#'+s.id+'">'+h.textContent+'</a>' : ''; }).join('');
      document.body.appendChild(pop); document.body.appendChild(b);
      b.onclick = function(){ pop.hidden = !pop.hidden; };
      pop.onclick = function(e){ if (e.target.tagName === 'A') pop.hidden = true; };
      document.addEventListener('click', function(e){ if (!pop.hidden && !e.target.closest('.tocpop,.fab')) pop.hidden = true; });
    }

    // 4) 分段控件
    document.querySelectorAll('.seg').forEach(seg);

    // 5) 讲义 → 刷题：qlink 带上本节题号 ids 与回程地址 back，刷完一键回到这一节；节末显示完成度
    qlinks();
    window.addEventListener('pageshow', function(e){ if (e.persisted) qlinks(); restoreY(); });
    document.addEventListener('click', function(e){
      if (e.target.closest('a.qlink')) try { sessionStorage.setItem('pol_ret', JSON.stringify({f: location.pathname, y: Math.round(scrollY)})); } catch(err){}
    });
  });

  /* 「单选 19–20、23」→ ['sx-s-19','sx-s-20','sx-s-23']；「导论单选 7 题」这种整章链接返回 null */
  function qids(p, t, label){
    var m = label.match(/(?:单选|多选|分析题)\s*(.*)$/);
    if (!m || !/\d/.test(m[1]) || /题\s*$/.test(m[1])) return null;
    var ids = [];
    m[1].replace(/(\d+)\s*[–\-~～]\s*(\d+)|(\d+)/g, function(_, a, b, c){
      if (c) ids.push(+c); else for (var i = +a; i <= +b; i++) ids.push(i);
    });
    return ids.map(function(n){ return p + '-' + t + '-' + n; });
  }
  /* 从刷题页「回讲义原位」回来（后退）时，滚回点链接那一刻的位置——不靠浏览器自己恢复，跨页动画会把它弄丢 */
  function restoreY(){
    var nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
    var r = null; try { r = JSON.parse(sessionStorage.getItem('pol_ret')); } catch(e){}
    if (!r || r.f !== location.pathname || !(nav && nav.type === 'back_forward')) return;
    var go = function(){ window.scrollTo({top: r.y, behavior: 'instant'}); };
    go(); requestAnimationFrame(go); setTimeout(go, 120); setTimeout(go, 450);
  }
  function qlinks(){
    var boxes = document.querySelectorAll('.qlinks'); if (!boxes.length) return;
    var rec = load('pol_rec_v1', {}), file = decodeURIComponent(location.pathname.split('/').pop());
    var done = function(ids){ return ids.filter(function(id){ return rec[id]; }).length; };
    var badge = function(a, ids){
      var old = a.querySelector('.qdone'); if (old) old.remove();
      var d = done(ids); a.classList.toggle('all-done', d === ids.length);
      a.insertAdjacentHTML('beforeend', '<span class="qdone">' + (d === ids.length ? '✓' : d + '/' + ids.length) + '</span>');
    };
    boxes.forEach(function(box){
      var sec = box.closest('section[id]'), h2 = sec && sec.querySelector('h2');
      var back = '../讲义/' + file + (sec ? '#' + sec.id : '');
      var lab = h2 ? h2.textContent.replace(/^\s*\d+\s*/, '').trim().slice(0, 24) : '';
      var all = [], p0 = null, ch0 = null, mixed = false;
      box.querySelectorAll('a.qlink:not(.sect)').forEach(function(a){
        var u = new URL(a.getAttribute('href'), location.href), p = u.searchParams.get('p'), t = u.searchParams.get('t');
        var ids = qids(p, t, a.dataset.label || (a.dataset.label = a.textContent));
        u.searchParams.set('back', back); if (lab) u.searchParams.set('lab', lab);
        if (ids){ u.searchParams.set('ids', ids.join(',')); badge(a, ids); all = all.concat(ids); }
        if (p0 && p0 !== p) mixed = true; p0 = p; if (ch0 == null) ch0 = u.searchParams.get('ch');
        a.href = a.getAttribute('href').split('?')[0] + '?' + u.searchParams.toString();
      });
      // 一节有两种题型以上：再给一个「本节一起刷」
      var sa = box.querySelector('a.qlink.sect');
      if (all.length > 1 && box.querySelectorAll('a.qlink:not(.sect)').length > 1 && !mixed){
        if (!sa){ sa = document.createElement('a'); sa.className = 'qlink sect'; sa.textContent = '▶ 本节一起刷 · ' + all.length + ' 题'; box.appendChild(sa); }
        var q = new URLSearchParams({p: p0, t: 'all', ch: ch0, ids: all.join(','), back: back}); if (lab) q.set('lab', lab);
        sa.href = '../题库/刷题.html?' + q.toString(); badge(sa, all);
      }
    });
  }
})();

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
  });
})();

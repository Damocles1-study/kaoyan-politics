/* 政治复盘中心 · 各页共用：六色图例、目录浮钮、背诵自测（关键词遮挡） */
(function(){
  var LEG = '<span class="kw">红·必背结论</span><span class="kd">蓝·概念定义</span><span class="kt">紫·时间人物著作会议</span>'
          + '<span class="km">绿·方法论与做法</span><span class="kx">橙·易混易错</span><span class="kn">金·数字口诀</span>';
  function ready(fn){ document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }
  ready(function(){
    // 1) 图例：页面里有 #legend 就填进去；讲义页没有就插在页眉后
    var lg = document.getElementById('legend');
    if (!lg && document.querySelector('.lec header')) {
      lg = document.createElement('div'); lg.id = 'legend';
      document.querySelector('.lec header').insertAdjacentElement('afterend', lg);
    }
    if (lg) { lg.className = 'legend'; lg.innerHTML = '<b>关键词颜色：</b>' + LEG
      + ' <label style="margin-left:auto;white-space:nowrap"><input type="checkbox" id="hideKw"> 背诵自测（遮住彩色关键词）</label>'; }

    // 2) 背诵自测：遮住所有彩色关键词，点一下显示
    var KW = '.kw,.kd,.kt,.km,.kx,.kn,u.k';
    var hk = document.getElementById('hideKw');
    if (hk) {
      var on = false; try { on = localStorage.getItem('pol_hidekw') === '1'; } catch(e){}
      function apply(v){
        document.body.classList.toggle('hide-on', v);
        document.querySelectorAll(KW).forEach(function(el){
          if (el.closest('.legend')) return;
          el.classList.add('reveal'); el.classList.remove('shown');
        });
      }
      hk.checked = on; if (on) apply(true);
      hk.onchange = function(){ apply(hk.checked); try { localStorage.setItem('pol_hidekw', hk.checked ? '1' : '0'); } catch(e){} };
      document.addEventListener('click', function(e){
        if (!document.body.classList.contains('hide-on')) return;
        var t = e.target.closest(KW); if (t && !t.closest('.legend')) t.classList.toggle('shown');
      });
    }

    // 3) 目录浮钮（有 ≥4 个带 id 的卡片时出现）
    var secs = [].slice.call(document.querySelectorAll('section.card[id]'));
    if (secs.length >= 4) {
      var b = document.createElement('button'); b.className = 'fab'; b.textContent = '☰ 目录';
      var pop = document.createElement('div'); pop.className = 'tocpop'; pop.hidden = true;
      pop.innerHTML = secs.map(function(s){ var h = s.querySelector('h2'); return h ? '<a href="#'+s.id+'">'+h.textContent+'</a>' : ''; }).join('');
      document.body.appendChild(pop); document.body.appendChild(b);
      b.onclick = function(){ pop.hidden = !pop.hidden; };
      pop.onclick = function(e){ if (e.target.tagName === 'A') pop.hidden = true; };
    }
  });
})();

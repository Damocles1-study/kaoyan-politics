/* 学习时长：由 skin.js 带进每一页，三个主题共用。
 * 只算真在学的时间：页面在前台，且 5 分钟内有过滚动、点击或按键；多开标签不重复计。
 * 记在本机 pol_time_v1 = {"2026-11-01": 秒数}；统计页的导出 / 导入会一起搬。
 * 页面里放 <div id="stHome"></div> 就会显示完整面板（首页、统计页）。 */
(function(){
  if (window.PolTime) return;
  var K = 'pol_time_v1', LAST = 'pol_time_last', IDLE = 300000, TICK = 5000, input = Date.now();
  var WK = ['周日','周一','周二','周三','周四','周五','周六'];
  function pad(n){ return (n < 10 ? '0' : '') + n; }
  function day(d){ d = d || new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function load(){ try { return JSON.parse(localStorage.getItem(K)) || {}; } catch(e){ return {}; } }
  function save(o){ try { localStorage.setItem(K, JSON.stringify(o)); } catch(e){} }
  function active(){ return document.visibilityState === 'visible' && Date.now() - input < IDLE; }
  function tick(){
    var now = Date.now();
    if (active()){
      var last = 0; try { last = +localStorage.getItem(LAST) || 0; } catch(e){}
      var dt = Math.min(TICK, now - last);
      if (dt > 0){
        var o = load(), k = day(); o[k] = (o[k] || 0) + dt / 1000; save(o);
        try { localStorage.setItem(LAST, String(now)); } catch(e){}
      }
    }
    draw();
  }
  function fmt(s){
    var m = Math.floor(s / 60), h = Math.floor(m / 60); m %= 60;
    if (!h) return m + '分';
    return h + '时' + (m ? m + '分' : '');
  }
  function stats(){
    var o = load(), t = 0; Object.keys(o).forEach(function(k){ t += o[k]; });
    var streak = 0, d = new Date();
    if (!(o[day(d)] >= 60)) d.setDate(d.getDate() - 1);
    while (o[day(d)] >= 60){ streak++; d.setDate(d.getDate() - 1); }
    var week = 0, w = new Date(); for (var i = 0; i < 7; i++){ week += o[day(w)] || 0; w.setDate(w.getDate() - 1); }
    return {today:o[day()] || 0, total:t, streak:streak, week:week, map:o};
  }
  function panel(){
    var s = stats(), bars = '', max = 1800, ds = [], d = new Date(); d.setDate(d.getDate() - 13);
    for (var i = 0; i < 14; i++){ var k = day(d), v = s.map[k] || 0; ds.push([k, v, WK[d.getDay()]]); if (v > max) max = v; d.setDate(d.getDate() + 1); }
    ds.forEach(function(x, i){
      var pct = x[1] ? Math.max(4, x[1] / max * 100) : 0, txt = +x[0].slice(5, 7) + '/' + +x[0].slice(8) + ' ' + x[2] + ' ' + fmt(x[1]);
      bars += '<u class="' + (i === 13 ? 'td' : '') + '" tabindex="0" data-tip="' + txt + '" title="' + txt + '" aria-label="' + txt + '"><s style="height:' + pct + '%"></s></u>';
    });
    return '<div class="tm-p"><div class="tm-big">'
      + '<div class="hi"><b>' + fmt(s.today) + '</b><span>今日</span></div><div class="hi"><b>' + fmt(s.total) + '</b><span>累计</span></div>'
      + '<div><b>' + s.streak + ' 天</b><span>连续</span></div><div><b>' + fmt(s.week / 7) + '</b><span>近 7 天日均</span></div></div>'
      + '<div class="tm-chart"><div class="tm-bars">' + bars + '</div><div class="tm-foot"><span>' + +ds[0][0].slice(5, 7) + '/' + +ds[0][0].slice(8) + '</span><b class="tm-tip">近 14 天</b><span>今天</span></div></div>'
      + '<p class="tm-note">页面在前台才计时，5 分钟没操作自动暂停；只记在这台设备的这个浏览器里，换设备用统计页的导出 / 导入。</p></div>';
  }
  var chip, pop, home;
  function draw(){
    if (!chip) return;
    var s = stats(), idle = !active();
    chip.innerHTML = '<i>今日</i><b>' + fmt(s.today) + '</b><i class="tm-sep">累计</i><b>' + fmt(s.total) + '</b>';
    chip.classList.toggle('idle', idle);
    chip.title = idle ? '已暂停：页面不在前台，或 5 分钟没有操作' : '正在计时，点开看近 14 天';
    if (pop && !pop.hidden && !pop.querySelector('u:hover,u:focus')) pop.innerHTML = panel();
    if (home && !home.querySelector('u:hover,u:focus')) home.innerHTML = panel();
  }
  function place(){
    pop.style.top = Math.max(8, chip.getBoundingClientRect().bottom + 8) + 'px';
    pop.style.left = Math.max(10, Math.min(innerWidth - pop.offsetWidth - 10, chip.getBoundingClientRect().right - pop.offsetWidth)) + 'px';
  }
  function init(){
    chip = document.createElement('button'); chip.type = 'button'; chip.className = 'tm-chip';
    chip.setAttribute('aria-haspopup', 'dialog');
    var host = document.querySelector('.wrap .sitebar') || document.querySelector('.wrap .crumb');
    var sk = host && host.querySelector('.skin-chip');
    if (sk) host.insertBefore(chip, sk); else if (host) host.appendChild(chip); else { chip.classList.add('solo'); document.body.appendChild(chip); }
    pop = document.createElement('div'); pop.className = 'tm-pop'; pop.hidden = true; document.body.appendChild(pop);
    home = document.getElementById('stHome');
    chip.addEventListener('click', function(e){
      e.stopPropagation(); pop.hidden = !pop.hidden;
      if (!pop.hidden){ pop.innerHTML = panel(); place(); }
    });
    document.addEventListener('click', function(e){ if (!pop.hidden && !e.target.closest('.tm-pop')) pop.hidden = true; });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape') pop.hidden = true; });
    window.addEventListener('scroll', function(){ if (!pop.hidden) pop.hidden = true; }, {passive:true});
    function tip(e){
      var u = e.target.closest && e.target.closest('.tm-bars u'); if (!u) return;
      var t = u.closest('.tm-p').querySelector('.tm-tip'); if (t) t.textContent = u.dataset.tip;
    }
    document.addEventListener('pointerover', tip, {passive:true}); document.addEventListener('focusin', tip);
    tick(); setInterval(tick, TICK);
  }
  ['pointerdown','pointermove','keydown','wheel','touchstart','scroll'].forEach(function(ev){
    window.addEventListener(ev, function(){ input = Date.now(); }, {passive:true, capture:true});
  });
  document.addEventListener('visibilitychange', function(){ if (document.visibilityState === 'visible') input = Date.now(); tick(); });
  window.addEventListener('pagehide', tick);
  window.PolTime = {stats:stats, fmt:fmt, tick:tick, log:load,
    /* 导入：同一天取较大值，重复导入不会翻倍 */
    merge:function(m){ var o = load(); Object.keys(m || {}).forEach(function(k){ if (!(o[k] >= m[k])) o[k] = m[k]; }); save(o); draw(); }};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

/* 政治复盘中心 · 艺术画展的场景（只有进画展主题才加载，由 skin.js 注入）
 * 甲、画面：WebGL 把真迹当成可以走进去的世界——笔触沿自身纹理流动、油彩受光、景深虚实、水面倒影、溶解换画
 * 乙、前景：螺旋仪和光尘（2D canvas），转场时螺旋仪飞到屏幕中央合拢光圈
 * 丙、联动：滚动推镜、读到新一节镜头换位、星图导航、悬停模块换画、判题时光线回应
 * 没有 WebGL 时退回静态图（html[data-gx-static]）；减弱动效或选「静帧」时只画一帧。 */
(function(){
  var S = window.PolSkin; if (!S) return;
  var root = document.documentElement;
  function clamp(x, a, b){ return x < a ? a : x > b ? b : x; }
  function sstep(a, b, x){ var t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); }
  function damp(cur, to, k, dt){ return cur + (to - cur) * (1 - Math.exp(-k * dt)); }
  var coarse = window.matchMedia('(pointer:coarse)').matches || innerWidth < 760;

  var on = false, raf = 0, last = 0, lastInput = 0, T = 0, needFrame = true;
  var view = {
    scrollY:0, vel:0, depth:0, depthTo:0, px:0, py:0, ptx:0, pty:0, spin:0, flash:0,
    pulse:0, pulseTo:0, pulseKind:0, stop:0, stopCount:1, leaving:0, iris:1
  };
  function still(){ return root.hasAttribute('data-gx-still'); }
  function poke(){ lastInput = performance.now(); needFrame = true; }

  /* ===== 甲、画面 ===== */
  var VS = '#version 300 es\nin vec2 a;out vec2 v;void main(){v=a;gl_Position=vec4(a,0.,1.);}';
  var FS = [
  '#version 300 es','precision highp float;',
  'uniform sampler2D A,B;uniform vec2 R,camA,camB;uniform float apA,apB,zoomA,zoomB,T,mixv,flow,blur,water,rays,gold,wash,dim,flash,pulse,yaw,pitch,pxA,pxB;',
  'uniform vec2 ptr;uniform vec3 washC,pulseC;in vec2 v;out vec4 o;',
  'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
  'float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}',
  'float fbm(vec2 p){return .55*vn(p)+.3*vn(p*2.1+3.)+.15*vn(p*4.3+7.);}',
  'float lum(vec3 c){return dot(c,vec3(.3,.59,.11));}',
  /* 把屏幕点映射到画布：cover 铺满，再按镜头位置和推近倍数取景 */
  'vec2 mapst(vec2 p,float ap,vec2 cam,float z,float asp){float k=max(asp/ap,1.)*z;vec2 h=vec2(asp/(ap*k),1./k)*.5;vec2 c=clamp(cam,h,1.-h);return vec2(c.x+p.x/(ap*k),c.y-p.y/k);}',
  'vec3 tap(sampler2D t,vec2 st,float lod,float px){if(lod<.6)return textureLod(t,st,lod).rgb;float r=px*pow(2.,lod)*.7;return .25*(textureLod(t,st+vec2(r,.4*r),lod).rgb+textureLod(t,st+vec2(-.4*r,r),lod).rgb+textureLod(t,st+vec2(-r,-.4*r),lod).rgb+textureLod(t,st+vec2(.4*r,-r),lod).rgb);}',
  /* 流动：取大尺度亮度梯度的切线，让颜料顺着笔触走；两相位交替，避免越拉越长 */
  'vec3 flowed(sampler2D t,vec2 st,float lod,float px,float amp,out vec2 use){',
  ' float e=px*14.;float l=3.2;float gx=lum(textureLod(t,st+vec2(e,0.),l).rgb)-lum(textureLod(t,st-vec2(e,0.),l).rgb);float gy=lum(textureLod(t,st+vec2(0.,e),l).rgb)-lum(textureLod(t,st-vec2(0.,e),l).rgb);',
  ' vec2 g=vec2(gx,gy);float m=length(g);vec2 tg=vec2(-g.y,g.x)/(m+.03);',
  ' vec2 q=st*3.+vec2(T*.02,-T*.015);vec2 c=vec2(vn(q+vec2(0.,1.3))-vn(q-vec2(0.,1.3)),-(vn(q+vec2(1.3,0.))-vn(q-vec2(1.3,0.))));',
  ' vec2 f=(tg*smoothstep(.0,.12,m)+c*.7)*amp;',
  ' float ph=fract(T*.075);float ph2=fract(ph+.5);float w=abs(2.*ph-1.);',
  ' vec2 a=st+f*(ph-.5);vec2 b=st+f*(ph2-.5);use=mix(a,b,w);',
  ' return mix(tap(t,a,lod,px),tap(t,b,lod,px),w);}',
  /* 受光：亮度当高度算法线，光源跟着鼠标；颜料的厚度由此显出来 */
  'vec3 relight(sampler2D t,vec2 st,vec3 c,float px,vec2 p,float lod){',
  ' if(lod>2.2)return c;float e=px*1.6;float l=.7;',
  ' float hx=lum(textureLod(t,st+vec2(e,0.),l).rgb)-lum(textureLod(t,st-vec2(e,0.),l).rgb);float hy=lum(textureLod(t,st+vec2(0.,e),l).rgb)-lum(textureLod(t,st-vec2(0.,e),l).rgb);',
  ' vec3 n=normalize(vec3(-hx,hy,.17));vec3 L=normalize(vec3(ptr-p,.62));',
  ' float d=max(dot(n,L),0.);vec3 H=normalize(L+vec3(0.,0.,1.));float s=pow(max(dot(n,H),0.),34.);',
  ' float k=1.-smoothstep(.6,2.2,lod);return c*mix(1.,.72+.56*d,k)+s*.34*k*(c+.25);}',
  'vec3 scene(sampler2D t,vec2 p,float ap,vec2 cam,float z,float px,float asp,float lod0){',
  ' vec2 st=mapst(p,ap,cam,z,asp);',
  ' float lod=lod0;vec2 use;vec3 c=flowed(t,st,lod,px,flow,use);c=relight(t,use,c,px,p,lod);',
  /* 星光：亮处泛光并轻轻呼吸 */
  ' vec3 bl=textureLod(t,st,4.6).rgb;float tw=.75+.25*sin(T*1.3+vn(st*22.)*9.);c+=pow(max(bl-.42,0.),vec3(1.8))*1.5*tw;',
  /* 金箔：偏黄的地方有一道慢慢扫过的反光 */
  ' if(gold>.01){float y=smoothstep(.04,.2,c.r-c.b);float sp=pow(vn(st*640.+T*.15),9.)*1.5*(1.-smoothstep(.3,1.6,lod0));float bd=smoothstep(.1,.9,sin(dot(st,vec2(3.,2.))*4.-T*.32));c+=y*(sp*bd+.05*bd)*vec3(1.,.82,.45)*gold;}',
  ' return c;}',
  'void main(){',
  ' float asp=R.x/R.y;vec2 p=v*.5*vec2(asp,1.);',
  /* 透视：画面像一块微微转动的平面 */
  ' float w=1.+p.x*yaw+p.y*pitch;vec2 q=p/w;',
  /* 水面：地平线以下是这幅画的倒影，越近波纹越大 */
  ' float hz=-.5+.3*water;float under=0.;vec3 skyC=vec3(0.);',
  ' if(q.y<hz){float d=hz-q.y;under=1.;float rip=sin(d*90.-T*1.7+q.x*7.+3.*vn(q*vec2(6.,40.)+T*.2))*.0018*(1.+d*5.);q=vec2(q.x*(1.+d*.9)+rip,hz+d*1.25+rip*2.);}',
  /* 溶解换画：沿噪声烧开一道金边，画面同时转一点 */
  ' float s=sin(mixv*3.14159);float ang=s*.32*(1.-smoothstep(0.,.9,length(q)));float ca=cos(ang),sa=sin(ang);vec2 qr=mat2(ca,-sa,sa,ca)*q;',
  ' float dist=length(q);float lod0=blur*(.55+.9*smoothstep(.15,.85,dist))+under*(.3+(hz-p.y)*8.);',
  ' vec3 c=scene(A,qr,apA,camA,zoomA,pxA,asp,lod0);',
  ' if(mixv>.001){float n=fbm(q*3.2+T*.05);float m=smoothstep(n-.09,n+.09,mixv*1.36-.18);vec3 cb=scene(B,qr,apB,camB,zoomB,pxB,asp,lod0);float edge=m*(1.-m)*4.;c=mix(c,cb,m)+edge*vec3(1.,.74,.32)*.75;}',
  ' if(under>.5){float d=hz-p.y;float fres=smoothstep(0.,.42,d);c=c*mix(.96,.3,fres)*mix(vec3(1.),vec3(.8,.9,1.14),smoothstep(0.,.1,d))+vec3(.012,.026,.06)*fres;c+=exp(-d*46.)*vec3(.95,.84,.6)*.13;}',
  /* 光束：从左上斜下来的几道光，缓慢错动 */
  ' float a2=dot(p,vec2(.78,.62));float sh=.5+.5*sin(a2*9.+T*.09)*sin(a2*23.-T*.05);c+=sh*sh*rays*smoothstep(.9,-.5,p.y-p.x*.5)*vec3(1.,.9,.72);',
  /* 指针处多一点光 */
  ' float sp=exp(-dot(p-ptr,p-ptr)*5.);c*=1.+sp*.2;',
  ' float vg=smoothstep(1.05,.25,length(p*vec2(.92/max(asp,1.)*1.6,1.3)));',
  ' c=mix(c,washC,wash*(.5+.5*(1.-vg)));c*=dim*mix(.72,1.,vg);',
  ' c=mix(c,c*.55+pulseC*.45*lum(c)*2.+pulseC*.08,pulse);',
  ' c+=flash*vec3(1.,.84,.52)*(.28+.55*exp(-dot(p,p)*3.));',
  ' c+=(hash(gl_FragCoord.xy+fract(T)*7.)-.5)/90.;',
  ' o=vec4(c,1.);}'
  ].join('\n');

  var canvas, gl, prog, U = {}, texCache = {}, A = null, B = null, mix = 0, mixing = false, pendingId = null, glOK = true;
  function compile(type, src){ var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; }
  function initGL(){
    canvas = document.createElement('canvas'); canvas.id = 'gx-gl'; canvas.setAttribute('aria-hidden', 'true');
    document.body.insertBefore(canvas, document.body.firstChild);
    try {
      gl = canvas.getContext('webgl2', {antialias:false, alpha:false, powerPreference:'low-power'});
      if (!gl) throw new Error('no webgl2');
      prog = gl.createProgram();
      gl.attachShader(prog, compile(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FS));
      gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
      gl.useProgram(prog);
      var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 3,-1, -1,3]), gl.STATIC_DRAW);
      var loc = gl.getAttribLocation(prog, 'a'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      ['A','B','R','camA','camB','apA','apB','zoomA','zoomB','T','mixv','flow','blur','water','rays','gold','wash','dim','flash','pulse','yaw','pitch','pxA','pxB','ptr','washC','pulseC'].forEach(function(n){ U[n] = gl.getUniformLocation(prog, n); });
      gl.uniform1i(U.A, 0); gl.uniform1i(U.B, 1);
      canvas.addEventListener('webglcontextlost', function(e){ e.preventDefault(); fallback(); });
    } catch(e){ if (window.console) console.warn('[gallery]', e.message); fallback(); }
  }
  function fallback(){ glOK = false; root.setAttribute('data-gx-static', ''); if (canvas) canvas.style.display = 'none'; }
  function resize(){
    if (!canvas || !glOK) return;
    var w = innerWidth, h = innerHeight, d = Math.min(devicePixelRatio || 1, coarse ? 1 : 1.25);
    var cap = coarse ? 820 : 1680, k = Math.min(1, cap / (w * d));
    var cw = Math.round(w * d * k), ch = Math.round(h * d * k);
    if (canvas.width !== cw || canvas.height !== ch){ canvas.width = cw; canvas.height = ch; gl.viewport(0, 0, cw, ch); }
    needFrame = true;
  }
  function artUrl(id){ return S.BASE + 'skin/art/' + (coarse ? '' : 'hd/') + id + '.webp'; }
  function getTex(id, cb){
    var hit = texCache[id];
    if (hit && hit.tex){ cb(hit); return; }
    if (hit){ hit.wait.push(cb); return; }
    var c = texCache[id] = {wait:[cb]}, im = new Image();
    im.onload = function(){
      var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, im);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.MIRRORED_REPEAT);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.MIRRORED_REPEAT);
      c.tex = t; c.ap = im.naturalWidth / im.naturalHeight; c.px = 1 / im.naturalWidth; c.id = id;
      c.wait.forEach(function(f){ f(c); }); c.wait = [];
    };
    im.onerror = function(){ delete texCache[id]; };
    im.src = artUrl(id);
  }
  function artById(id){
    var hit = null;
    ['vg','mu'].forEach(function(h){ S.ART[h].head.forEach(function(a){ if (a.id === id) hit = a; }); });
    return hit;
  }
  /* 当前这张画的镜头 */
  var camA = {x:.5, y:.45, z:1.1}, camB = {x:.5, y:.45, z:1.1};
  function stopFor(a, i){ var f = a.f[i % a.f.length]; return {x:f[0], y:f[1], z:f[2]}; }
  function showPainting(id, instant){
    if (!glOK) return;
    if (A && A.id === id && !mixing) return;
    if (B && B.id === id) return;
    pendingId = id;
    getTex(id, function(t){
      if (pendingId !== id || !on) return;
      var a = artById(id), f = stopFor(a, view.stop);
      if (!A || instant){ A = t; camA = {x:f.x, y:f.y, z:f.z}; mix = 0; mixing = false; B = null; canvas.classList.add('on'); bind(); needFrame = true; return; }
      if (mixing){ A = B; camA = camB; }
      B = t; camB = {x:f.x, y:f.y, z:f.z}; mix = 0; mixing = true; view.flash = Math.max(view.flash, .16); bind(); poke();
    });
  }
  function bind(){
    if (A){ gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, A.tex); }
    if (B){ gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, B.tex); }
  }
  function hexRGB(s){ var m = /rgba?\(([^)]+)\)/.exec(s); if (m){ var p = m[1].split(',').map(parseFloat); return [p[0]/255,p[1]/255,p[2]/255]; } return [0,0,0]; }
  var washC = [0,0,0], isVG = true, focusAt = 0;
  function readHall(){
    isVG = S.hall() === 'vg';
    var cs = getComputedStyle(root), v = cs.getPropertyValue('--veil').trim().split(',').map(parseFloat);
    washC = v.length === 3 ? [v[0]/255, v[1]/255, v[2]/255] : [0,0,0];
  }
  function drawGL(dt){
    if (!A || !glOK) return;
    var r = view.depth, night = lum3(washC) < .4;
    var a = artById(A.id), f = stopFor(a, view.stop), lead = 1 + r * .22, kcam = still() ? 40 : 1.15;
    /* 推镜：越往下读越贴近；离开页面时退回全貌 */
    var tz = (r < .05 ? 1 : f.z) * lead, tx = r < .05 ? a.f[0][0] : f.x, ty = r < .05 ? a.f[0][1] : f.y + (view.scrollP - .5) * .05;
    camA.x = damp(camA.x, tx, kcam, dt); camA.y = damp(camA.y, ty, kcam, dt); camA.z = damp(camA.z, tz, kcam, dt);
    if (B){ var ab = artById(B.id), fb = stopFor(ab, view.stop); camB.x = damp(camB.x, r < .05 ? ab.f[0][0] : fb.x, kcam, dt); camB.y = damp(camB.y, r < .05 ? ab.f[0][1] : fb.y, kcam, dt); camB.z = damp(camB.z, (r < .05 ? 1 : fb.z) * lead, kcam, dt); }
    if (mixing){ mix = Math.min(1, mix + dt / (still() ? .01 : 1.9)); needFrame = true; if (mix >= 1){ A = B; camA = camB; B = null; mix = 0; mixing = false; bind(); } }
    var mv = mixing ? mix * mix * (3 - 2 * mix) : 0, leave = view.leaving;
    gl.uniform2f(U.R, canvas.width, canvas.height);
    gl.uniform2f(U.camA, camA.x, camA.y); gl.uniform1f(U.apA, A.ap); gl.uniform1f(U.zoomA, camA.z); gl.uniform1f(U.pxA, A.px);
    if (B){ gl.uniform2f(U.camB, camB.x, camB.y); gl.uniform1f(U.apB, B.ap); gl.uniform1f(U.zoomB, camB.z); gl.uniform1f(U.pxB, B.px); }
    gl.uniform1f(U.T, T); gl.uniform1f(U.mixv, mv);
    /* 笔触流动幅度：平时很轻，滚动时被带起来 */
    gl.uniform1f(U.flow, still() ? 0 : (isVG ? .012 : .0045) + Math.min(.022, Math.abs(view.vel) * .000018));
    /* 虚实：页眉处全清晰；读内容时背景退到焦外；要离开时重新清晰 */
    gl.uniform1f(U.blur, (r * (isVG ? 2.5 : 3.1)) * (1 - leave));
    gl.uniform1f(U.water, isVG ? (1 - sstep(0, .55, r)) : 0);
    gl.uniform1f(U.rays, isVG ? .035 : (night ? .05 : .13));
    gl.uniform1f(U.gold, isVG ? 0 : 1);
    gl.uniform1f(U.wash, (isVG ? r * .16 : r * (night ? .5 : .55)) * (1 - leave));
    gl.uniform1f(U.dim, (isVG ? 1 - r * .4 : (night ? 1 - r * .4 : 1)));
    gl.uniform1f(U.flash, view.flash); gl.uniform1f(U.pulse, view.pulse);
    gl.uniform3f(U.pulseC, view.pulseKind ? .36 : 1, view.pulseKind ? .44 : .82, view.pulseKind ? .7 : .42);
    gl.uniform3f(U.washC, washC[0], washC[1], washC[2]);
    gl.uniform1f(U.yaw, still() ? 0 : view.px * .1); gl.uniform1f(U.pitch, still() ? 0 : (view.py * .07 + Math.max(-.08, Math.min(.08, view.vel * .00003))));
    gl.uniform2f(U.ptr, view.px * .7 * (canvas.width / canvas.height), view.py * .5 + .05);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  function lum3(c){ return .3 * c[0] + .59 * c[1] + .11 * c[2]; }

  /* ===== 乙、前景：螺旋仪与光尘 ===== */
  var fx, ctx, sprite, motes = [], ring = null;
  function mkSprite(){
    var c = document.createElement('canvas'); c.width = c.height = 128;
    var g = c.getContext('2d'), r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    r.addColorStop(0, 'rgba(255,246,214,1)'); r.addColorStop(.12, 'rgba(255,222,150,.72)'); r.addColorStop(.4, 'rgba(255,190,90,.16)'); r.addColorStop(1, 'rgba(255,170,60,0)');
    g.fillStyle = r; g.fillRect(0, 0, 128, 128);
    g.globalCompositeOperation = 'lighter';
    var h = g.createLinearGradient(0, 64, 128, 64); h.addColorStop(0, 'rgba(255,220,150,0)'); h.addColorStop(.5, 'rgba(255,240,200,.85)'); h.addColorStop(1, 'rgba(255,220,150,0)');
    g.fillStyle = h; g.fillRect(0, 63, 128, 2);
    var v = g.createLinearGradient(64, 0, 64, 128); v.addColorStop(0, 'rgba(255,220,150,0)'); v.addColorStop(.5, 'rgba(255,240,200,.6)'); v.addColorStop(1, 'rgba(255,220,150,0)');
    g.fillStyle = v; g.fillRect(63, 24, 2, 80);
    return c;
  }
  function initFX(){
    fx = document.createElement('canvas'); fx.id = 'gx-fx'; fx.setAttribute('aria-hidden', 'true');
    document.body.insertBefore(fx, canvas ? canvas.nextSibling : document.body.firstChild);
    ctx = fx.getContext('2d'); sprite = mkSprite();
    for (var i = 0; i < (coarse ? 14 : 30); i++) motes.push({x:Math.random(), y:Math.random(), z:Math.random(), p:Math.random() * 6.28, s:.5 + Math.random()});
    /* 螺旋仪：每个环有自己的半径、宽度和转轴；环 0 是刻了度数的黄道带 */
    ring = [
      {r:1,    w:.052, ax:[.42,.1,.18],  sp:.05,  band:1},
      {r:.94,  w:.024, ax:[1.3,0,.5],    sp:-.17},
      {r:.86,  w:.03,  ax:[.2,1.25,0],   sp:.23},
      {r:.76,  w:.02,  ax:[1.57,.4,0],   sp:-.31},
      {r:.66,  w:.024, ax:[.8,-.9,.3],   sp:.41},
      {r:.52,  w:.016, ax:[-.6,.5,1],    sp:-.62}
    ];
    ring.forEach(function(q){ q.a = Math.random() * 6.28; });
    try { var sv = JSON.parse(sessionStorage.getItem('gx_ring') || 'null'); if (sv) ring.forEach(function(q, i){ q.a = sv[i] || q.a; }); } catch(e){}
  }
  function sizeFX(){
    if (!fx) return;
    var d = Math.min(devicePixelRatio || 1, 1.5);
    fx.width = Math.round(innerWidth * d); fx.height = Math.round(innerHeight * d); fx._d = d; needFrame = true;
  }
  /* 欧拉角转动一个点 */
  function rot(p, a){
    var x = p[0], y = p[1], z = p[2], c, s, t;
    c = Math.cos(a[0]); s = Math.sin(a[0]); t = y * c - z * s; z = y * s + z * c; y = t;
    c = Math.cos(a[1]); s = Math.sin(a[1]); t = x * c + z * s; z = -x * s + z * c; x = t;
    c = Math.cos(a[2]); s = Math.sin(a[2]); t = x * c - y * s; y = x * s + y * c; x = t;
    return [x, y, z];
  }
  var orb = {x:0, y:0, r:0, a:0};
  function orbTarget(){
    var w = innerWidth, h = innerHeight, margin = (w - 880) / 2;
    if (view.iris < 1 || view.leaving > 0) return {x:w / 2, y:h / 2, r:Math.min(w, h) * .3, a:1};
    if (margin >= 170) return {x:w - margin / 2, y:h * .7, r:Math.min(margin * .4, 140), a:isVG ? .8 : .78};
    /* narrow screens: rest in the hero's fade-out zone so it never sits on top of text; no hero, no orrery */
    var hero = document.querySelector('.wrap header');
    if (!hero) return {x:w - 60, y:-80, r:44, a:0};
    var bottom = hero.getBoundingClientRect().bottom - 46;
    return {x:w - 58, y:bottom, r:44, a:bottom < -60 ? 0 : .75};
  }
  function drawOrrery(dt){
    var t = orbTarget(), k = (view.iris < 1 || view.leaving > 0) ? 12 : 3.2;
    if (!orb.r){ orb.x = t.x; orb.y = t.y; orb.r = t.r; orb.a = t.a; }
    orb.x = damp(orb.x, t.x, k, dt); orb.y = damp(orb.y, t.y, k, dt); orb.r = damp(orb.r, t.r, k, dt); orb.a = damp(orb.a, t.a, 4, dt);
    if (orb.a < .02) return;
    var spin = still() ? 0 : 1 + view.spin + Math.abs(view.vel) * .004;
    ring.forEach(function(q){ q.a += q.sp * spin * dt; });
    var scrollRot = view.scrollY * .0006, tilt = [-.46 + view.py * .14, view.px * .18 + scrollRot * .4, .12], segs = [], N = coarse ? 48 : 72, dist = 3.4;
    var L = [-.5, -.65, .62], glints = [];
    ring.forEach(function(q, ri){
      var ax = [q.ax[0], q.ax[1] + q.a, q.ax[2]];
      for (var i = 0; i < N; i++){
        var a0 = i / N * 6.2832, a1 = (i + 1) / N * 6.2832;
        var p0 = rot(rot([Math.cos(a0) * q.r, 0, Math.sin(a0) * q.r], ax), tilt);
        var p1 = rot(rot([Math.cos(a1) * q.r, 0, Math.sin(a1) * q.r], ax), tilt);
        var nn = rot(rot([Math.cos(a0), .35, Math.sin(a0)], ax), tilt);
        var dot = (nn[0] * L[0] + nn[1] * L[1] + nn[2] * L[2]) / 1.06;
        var spec = Math.pow(Math.max(0, dot), 12);
        var z = (p0[2] + p1[2]) / 2, pr = dist / (dist - z);
        segs.push({x0:p0[0] * dist / (dist - p0[2]), y0:p0[1] * dist / (dist - p0[2]), x1:p1[0] * dist / (dist - p1[2]), y1:p1[1] * dist / (dist - p1[2]), z:z, w:q.w * pr, l:.3 + .5 * Math.max(0, dot) + .9 * spec, band:q.band && i % 6 === 0});
        if (spec > .82) glints.push({x:p0[0] * pr, y:p0[1] * pr, z:z, s:spec});
      }
    });
    segs.sort(function(a, b){ return a.z - b.z; });
    ctx.save(); ctx.translate(orb.x, orb.y); ctx.globalAlpha = orb.a; ctx.lineCap = 'round';
    var R = orb.r, drewCore = false;
    for (var i = 0; i < segs.length; i++){
      var g = segs[i];
      if (!drewCore && g.z > 0){ core(R); drewCore = true; }
      var fade = .5 + .5 * sstep(-1, 1, g.z), l = Math.min(1.25, g.l) * fade;
      /* 黄铜：暗处偏赭，亮处发白 */
      var cr = Math.min(255, 70 + 200 * l), cg = Math.min(255, 44 + 170 * l), cb = Math.min(255, 14 + 88 * l * l);
      ctx.strokeStyle = 'rgb(' + (cr | 0) + ',' + (cg | 0) + ',' + (cb | 0) + ')';
      ctx.lineWidth = Math.max(.6, g.w * R);
      ctx.beginPath(); ctx.moveTo(g.x0 * R, g.y0 * R); ctx.lineTo(g.x1 * R, g.y1 * R); ctx.stroke();
      if (g.band){ ctx.strokeStyle = 'rgba(30,18,4,.65)'; ctx.lineWidth = Math.max(.5, R * .004); var mx = (g.x0 + g.x1) / 2, my = (g.y0 + g.y1) / 2; ctx.beginPath(); ctx.moveTo(mx * R * .975, my * R * .975); ctx.lineTo(mx * R * 1.025, my * R * 1.025); ctx.stroke(); }
    }
    if (!drewCore) core(R);
    /* 闪光：环转到迎光的角度时亮一下，转场和判题时更盛 */
    ctx.globalCompositeOperation = isVG || lum3(washC) < .4 ? 'lighter' : 'source-over';
    var boost = 1 + view.flash * 5;
    glints.sort(function(a, b){ return b.s - a.s; });
    for (var j = 0; j < Math.min(7, glints.length); j += 2){
      var q = glints[j], s = R * (.2 + .34 * (q.s - .82) * 5) * Math.min(boost, 4.5);
      ctx.globalAlpha = orb.a * Math.min(1, (q.s - .8) * 5) * (q.z > 0 ? 1 : .35);
      ctx.drawImage(sprite, q.x * R - s / 2, q.y * R - s / 2, s, s);
    }
    ctx.restore();
  }
  function core(R){
    var g = ctx.createRadialGradient(-R * .05, -R * .06, 0, 0, 0, R * .17);
    if (isVG){ g.addColorStop(0, '#fff2bd'); g.addColorStop(.5, '#e9b73e'); g.addColorStop(1, '#6a4510'); }
    else { g.addColorStop(0, '#fff9ea'); g.addColorStop(.55, '#e7c98b'); g.addColorStop(1, '#8a6a30'); }
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, R * .13, 0, 6.2832); ctx.fill();
  }
  function drawMotes(dt){
    var w = innerWidth, h = innerHeight, night = isVG || lum3(washC) < .4;
    ctx.globalCompositeOperation = night ? 'lighter' : 'source-over';
    motes.forEach(function(m){
      if (!still()){ m.p += dt * .35; m.y -= dt * (.004 + m.z * .012); if (m.y < -.05) m.y += 1.1; }
      var py = (m.y - view.scrollY * (.00004 + m.z * .00016)) % 1.1; if (py < -.05) py += 1.1;
      var x = (m.x + Math.sin(m.p) * .008) * w + view.px * (6 + m.z * 26), y = py * h + view.py * (4 + m.z * 16);
      /* 近处的光尘大而虚，远处的小而实 */
      var s = 3 + m.z * m.z * 26 * m.s;
      ctx.globalAlpha = (night ? .5 : .55) * (.28 + .5 * (1 - m.z)) * (.55 + .45 * Math.sin(m.p * 2.3));
      ctx.drawImage(sprite, x - s / 2, y - s / 2, s, s);
    });
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  }
  function drawFX(dt){
    var d = fx._d || 1; ctx.setTransform(d, 0, 0, d, 0, 0); ctx.clearRect(0, 0, innerWidth, innerHeight);
    drawMotes(dt); drawOrrery(dt);
  }

  /* ===== 主循环：有动静 60 帧，读书时降到 24 帧，后台停 ===== */
  function loop(now){
    raf = requestAnimationFrame(loop);
    if (document.hidden) { last = now; return; }
    var idle = now - lastInput > 2500 && !mixing && view.iris >= 1 && !view.leaving;
    var gap = still() ? 0 : (idle ? (coarse ? 66 : 40) : 0);
    if (still() && !needFrame && view.iris >= 1 && !mixing) { last = now; return; }
    if (gap && now - last < gap) return;
    var dt = Math.min(.05, (now - last) / 1000 || .016); last = now;
    if (!still()) T += dt;
    needFrame = false;
    var y = window.scrollY;
    view.vel = damp(view.vel, (y - view.scrollY) / Math.max(dt, .008), 7, dt);
    view.scrollY = y;
    var hero = heroH();
    view.depthTo = Math.max(sstep(hero * .18, hero * .92, y), document.querySelector('.wrap header') ? 0 : .62);
    view.depth = still() ? view.depthTo : damp(view.depth, view.depthTo, 3.6, dt);
    var doc = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    view.scrollP = clamp(y / doc, 0, 1);
    view.px = damp(view.px, view.ptx, 2.4, dt); view.py = damp(view.py, view.pty, 2.4, dt);
    view.flash = damp(view.flash, 0, 2.6, dt); view.spin = damp(view.spin, view.leaving ? 20 : 0, view.leaving ? 5 : 1.5, dt);
    view.pulse = damp(view.pulse, 0, 2.3, dt);
    if (glOK) drawGL(dt);
    if (fx) drawFX(dt);
  }
  var heroCache = 0;
  function heroH(){ if (heroCache) return heroCache; var h = document.querySelector('.wrap header'); heroCache = h ? h.getBoundingClientRect().height + 80 : 260; return heroCache; }

  /* ===== 丙、联动 ===== */
  /* 换一幅 / 换厅 */
  function painting(){ if (!on) return; readHall(); var a = S.pick(S.ART[S.hall()].head); showPainting(a.id); heroCache = 0; poke(); }
  function flash(v){ view.flash = Math.max(view.flash, v); poke(); }
  function pulse(kind){ view.pulseKind = kind; view.pulse = kind ? .55 : .5; flash(kind ? .05 : .32); view.spin = kind ? 0 : 6; }
  function nextStop(){ view.stop = (view.stop + 1) % 997; poke(); }

  /* 星图：左边竖着一串星，每节一颗；当前这颗亮，线随阅读长 */
  var astro, astroItems = [], io, current = -1;
  function sections(){ return [].slice.call(document.querySelectorAll('.wrap > section.card')).filter(function(s){ return s.querySelector('h2'); }); }
  function buildAstro(){
    if (astro){ astro.remove(); astro = null; }
    if (io){ io.disconnect(); io = null; }
    var ss = sections(); astroItems = ss; current = -1;
    if (!ss.length) return;
    io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (e.isIntersecting) setCurrent(ss.indexOf(e.target)); });
    }, {rootMargin:'-42% 0px -55% 0px'});
    ss.forEach(function(s){ io.observe(s); });
    if (ss.length < 3) return;
    astro = document.createElement('nav'); astro.className = 'gx-astro'; astro.setAttribute('aria-label', '本页章节');
    astro.innerHTML = '<i class="gx-thread"><i></i></i>' + ss.map(function(s, i){
      var t = s.querySelector('h2').textContent.trim();
      return '<a href="#" data-i="' + i + '"><s></s><span>' + t.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span></a>';
    }).join('');
    astro.addEventListener('click', function(e){
      var a = e.target.closest('a'); if (!a) return; e.preventDefault(); e.stopPropagation();
      ss[+a.dataset.i].scrollIntoView({behavior:still() ? 'auto' : 'smooth', block:'start'});
    });
    document.body.appendChild(astro);
  }
  function setCurrent(i){
    if (i === current || i < 0) return;
    var first = current < 0; current = i; view.stop = i + 1;
    if (!first){ flash(.1); view.spin = Math.max(view.spin, 2.2); }
    poke();
    if (astro){
      astro.querySelectorAll('a').forEach(function(a, k){ a.classList.toggle('on', k === i); a.classList.toggle('past', k < i); });
      var as = astro.querySelectorAll('a'), th = astro.querySelector('.gx-thread i');
      if (as[i] && th) th.style.height = (as[i].offsetTop + 5) + 'px';
    }
  }

  /* 内容一节节从焦外浮出来 */
  var rio;
  var REV = '.wrap > section.card > *, .wrap > details.deep, .wrap > .qcard, .type, .steps > div, .card-mem, .wrap > .footer';
  function reveal(){
    if (rio) rio.disconnect();
    if (still()) { document.querySelectorAll('.gx-r').forEach(function(n){ n.classList.remove('gx-r','gx-in'); }); return; }
    rio = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('gx-in'); rio.unobserve(e.target); } });
    }, {rootMargin:'0px 0px -6% 0px', threshold:.02});
    document.querySelectorAll(REV).forEach(function(n){
      if (n.classList.contains('gx-seen')) return;
      n.classList.add('gx-seen','gx-r'); rio.observe(n);
    });
  }

  /* 标题逐字显影 */
  var h1Html = null;
  function splitTitle(){
    var h1 = document.querySelector('.wrap header h1'); if (!h1 || still()) return;
    if (h1Html === null) h1Html = h1.innerHTML;
    var n = 0;
    (function walk(el){
      [].slice.call(el.childNodes).forEach(function(c){
        if (c.nodeType === 3){
          var f = document.createDocumentFragment();
          Array.from(c.textContent).forEach(function(ch){
            if (/\s/.test(ch)){ f.appendChild(document.createTextNode(ch)); return; }
            var s = document.createElement('span'); s.className = 'gx-ch'; s.style.setProperty('--i', n++); s.textContent = ch; f.appendChild(s);
          });
          el.replaceChild(f, c);
        } else if (c.nodeType === 1 && c.tagName !== 'BR') walk(c);
      });
    })(h1);
  }
  function restoreTitle(){ var h1 = document.querySelector('.wrap header h1'); if (h1 && h1Html !== null){ h1.innerHTML = h1Html; h1Html = null; } }

  /* 首页模块：错落悬挂（砌体布局）＋ 倾斜光泽 ＋ 悬停换背景 */
  var MOD = {vg:['starry','wheat','rhone','almond','irises','wheat','rhone','starry','almond','irises','wheat'],
             mu:['seasons','stones','moonstars','seasons','stones','moonstars','seasons','stones','moonstars','seasons','stones']};
  var hoverT = 0, homeArt = null;
  function salon(){
    var box = document.querySelector('.types'); if (!box) return;
    var row = 6, gap = 26;
    [].forEach.call(box.children, function(c){
      c.style.gridRowEnd = 'auto';
      if (innerWidth < 720) return;
      c.style.gridRowEnd = 'span ' + Math.ceil((c.scrollHeight + gap) / row);
    });
  }
  function onMove(e){
    view.ptx = e.clientX / innerWidth * 2 - 1; view.pty = -(e.clientY / innerHeight * 2 - 1); poke();
    var c = e.target.closest && e.target.closest('.type,.face,.card-mem');
    if (c && !still()){
      var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      c.style.setProperty('--mx', (x * 100).toFixed(1) + '%'); c.style.setProperty('--my', (y * 100).toFixed(1) + '%');
      c.style.setProperty('--ry', ((x - .5) * 9).toFixed(2) + 'deg'); c.style.setProperty('--rx', ((.5 - y) * 7).toFixed(2) + 'deg');
    }
  }
  function onOver(e){
    var c = e.target.closest && e.target.closest('.types .type');
    if (!c || still()) return;
    clearTimeout(hoverT);
    hoverT = setTimeout(function(){
      var list = MOD[S.hall()], i = [].indexOf.call(c.parentNode.children, c), id = list[i % list.length];
      showPainting(id); homeArt = id; view.spin = Math.max(view.spin, 3);
    }, 170);
  }
  function onOut(e){
    if (!homeArt) return;
    var c = e.target.closest && e.target.closest('.types'), to = e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest('.types');
    if (c && !to){ clearTimeout(hoverT); hoverT = setTimeout(function(){ homeArt = null; painting(); }, 500); }
  }

  /* 判题、换题、翻卡：光线回应 */
  var mo;
  function watch(){
    if (mo) mo.disconnect();
    var w = document.querySelector('.wrap'); if (!w) return;
    var late = 0;
    mo = new MutationObserver(function(ms){
      var re = false, ok = false, bad = false, q = false;
      ms.forEach(function(m){
        [].forEach.call(m.addedNodes, function(n){
          if (n.nodeType !== 1) return;
          if (n.parentNode === w || (n.matches && n.matches('section.card'))) re = true;
          if (n.matches('.qcard') || (n.querySelector && n.querySelector('.qcard'))) q = true;
          if (n.matches('.verdict.ok') || n.querySelector('.verdict.ok')) ok = true;
          if (n.matches('.verdict.bad') || n.querySelector('.verdict.bad')) bad = true;
        });
      });
      if (bad) pulse(1); else if (ok) pulse(0); else if (q) nextStop();
      if (re){ clearTimeout(late); late = setTimeout(function(){ buildAstro(); reveal(); salon(); }, 120); }
    });
    mo.observe(w, {childList:true, subtree:true});
  }
  function onClick(e){
    var c = e.target.closest && e.target.closest('.fc,.seg button,.gi,.rate .btn');
    if (c){ flash(.07); view.spin = Math.max(view.spin, 1.6); if (c.matches('.fc,.rate .btn')) nextStop(); }
    /* 跨页转场 */
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || still()) return;
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target === '_blank' || a.hasAttribute('download')) return;
    var u; try { u = new URL(a.href, location.href); } catch(x){ return; }
    if (u.origin !== location.origin) return;
    if (u.pathname === location.pathname && u.search === location.search) return;
    e.preventDefault(); leaveTo(u.href);
  }
  function leaveTo(href){
    if (view.leaving) return;
    view.leaving = 1; view.iris = 0; flash(.28); poke();
    root.classList.add('gx-leaving');
    var iris = document.getElementById('gx-iris'); if (iris) { iris.classList.remove('open'); iris.classList.add('close'); }
    fx.classList.add('front');
    setTimeout(function(){
      try {
        sessionStorage.setItem('gx_go', String(Date.now()));
        sessionStorage.setItem('gx_ring', JSON.stringify(ring.map(function(q){ return q.a; })));
      } catch(x){}
      location.href = href;
    }, 460);
  }
  function arrive(){
    var iris = document.getElementById('gx-iris');
    if (!root.hasAttribute('data-gx-arrive')) { if (iris) iris.className = ''; return; }
    view.iris = 0; view.spin = 14; fx.classList.add('front');
    var opened = false;
    function open(){
      if (opened) return; opened = true;
      root.classList.add('gx-opening'); root.removeAttribute('data-gx-arrive');
      if (iris){ iris.classList.remove('shut'); iris.classList.add('open'); }
      flash(.24);
      setTimeout(function(){ view.iris = 1; fx.classList.remove('front'); poke(); }, 620);
      setTimeout(function(){ root.classList.remove('gx-opening'); if (iris) iris.className = ''; }, 1200);
    }
    if (iris) iris.classList.add('shut');
    var check = setInterval(function(){ if (A || !glOK){ clearInterval(check); open(); } }, 40);
    setTimeout(function(){ clearInterval(check); open(); }, 700);
  }
  function onShow(e){
    if (!e.persisted) return;
    /* 从往返缓存回来：把离开时的状态恢复 */
    view.leaving = 0; view.iris = 1; root.classList.remove('gx-leaving','gx-opening'); root.removeAttribute('data-gx-arrive');
    var iris = document.getElementById('gx-iris'); if (iris) iris.className = '';
    if (fx) fx.classList.remove('front');
    poke();
  }
  function onScroll(){ poke(); }
  function onResize(){ coarse = window.matchMedia('(pointer:coarse)').matches || innerWidth < 760; heroCache = 0; resize(); sizeFX(); salon(); }

  /* ===== 进出主题 ===== */
  var LISTEN = [['pointermove',onMove,true],['pointerover',onOver,true],['pointerout',onOut,true],['scroll',onScroll,true]];
  function enter(){
    readHall();
    if (on){ painting(); reveal(); return; }
    on = true;
    if (!canvas) initGL();
    if (canvas && glOK) canvas.style.display = '';
    if (!fx) initFX();
    fx.style.display = '';
    if (!document.getElementById('gx-iris')){ var iris = document.createElement('div'); iris.id = 'gx-iris'; iris.setAttribute('aria-hidden', 'true'); document.body.appendChild(iris); }
    root.classList.add('gx-on');
    resize(); sizeFX();
    arrive();
    var a = S.pick(S.ART[S.hall()].head);
    showPainting(a.id, true);
    view.scrollY = window.scrollY;
    LISTEN.forEach(function(l){ window.addEventListener(l[0], l[1], {passive:l[2]}); });
    window.addEventListener('resize', onResize);
    document.addEventListener('click', onClick);
    window.addEventListener('pageshow', onShow);
    splitTitle(); buildAstro(); reveal(); salon(); watch();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(salon);
    window.addEventListener('load', salon, {once:true});
    last = performance.now(); poke();
    if (!raf) raf = requestAnimationFrame(loop);
  }
  function leave(){
    if (!on) return; on = false;
    cancelAnimationFrame(raf); raf = 0;
    LISTEN.forEach(function(l){ window.removeEventListener(l[0], l[1]); });
    window.removeEventListener('resize', onResize);
    document.removeEventListener('click', onClick);
    window.removeEventListener('pageshow', onShow);
    if (canvas) { canvas.style.display = 'none'; canvas.classList.remove('on'); }
    if (fx) fx.style.display = 'none';
    if (astro){ astro.remove(); astro = null; }
    if (io) io.disconnect(); if (rio) rio.disconnect(); if (mo) mo.disconnect();
    document.querySelectorAll('.gx-r,.gx-seen').forEach(function(n){ n.classList.remove('gx-r','gx-in','gx-seen'); });
    [].forEach.call(document.querySelectorAll('.types > .type'), function(c){ c.style.gridRowEnd = ''; });
    restoreTitle();
    root.classList.remove('gx-on');
    A = null; B = null; mixing = false; mix = 0;
  }
  function motion(){ reveal(); if (still()) restoreTitle(); else if (h1Html === null) splitTitle(); poke(); needFrame = true; }

  S.register({enter:enter, leave:leave, painting:painting, motion:motion});
})();

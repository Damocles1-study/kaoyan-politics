# -*- coding: utf-8 -*-
"""三科夜背：从政治 / 408（术式408）/ 英语一（新版）三个中心抽可背内容，按晚排期，写 背诵/data_night.js。

    python3 _build/tools/build_night.py

数据源（都是兄弟仓库的现成文件，只读）：
  政治   背诵/cards.js · 背诵/哲学十六原理.html · 背诵/思法十四专题.html · 讲义/*.html 的 ✍️ 金框 · 秒杀/选择题秒杀.html 的帽子对照表
  408    ../../408/复盘中心/术式408/_src/NN.txt 的 :::domain / :::recall / :::trap ＋ _build/kpq/mn.txt 口诀 ＋ _build/plan.py 话目
  英语   ../../英语一/阅读复盘/新版/data_wordbank.js（词与作文句）＋ ../data_tricks_read.js（🔴 阅读套路）
  手写   _build/tools/night_hand.py（作文框架、答题骨架、肖四任务）
"""
import json, os, re, sys, html, datetime, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))          # 政治/复盘中心
BASE = os.path.normpath(os.path.join(ROOT, '..', '..'))          # 11408相关
S408 = os.path.join(BASE, '408', '复盘中心', '术式408')
SENG = os.path.join(BASE, '英语一', '阅读复盘')
sys.path.insert(0, HERE)
import night_hand as H

ONLINE_408 = 'https://damocles1-study.github.io/kaoyan-408/术式408/'
ONLINE_ENG = 'https://damocles1-study.github.io/kaoyan-english/'
START = datetime.date(2026, 11, 25)
NNIGHT = 25

def rd(p): return open(p, encoding='utf-8').read()
E = lambda s: html.escape(s, quote=False)
def plain(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()

# ───────────── 小型 JS 字面量解析（对象 / 数组 / 字符串拼接） ─────────────
def js_parse(src):
    i = 0; n = len(src)
    def ws():
        nonlocal i
        while i < n:
            if src[i] in ' \t\r\n': i += 1
            elif src.startswith('//', i): i = src.index('\n', i) if '\n' in src[i:] else n
            elif src.startswith('/*', i): i = src.index('*/', i) + 2
            else: break
    def string():
        nonlocal i
        q = src[i]; i += 1; out = []
        while src[i] != q:
            c = src[i]
            if c == '\\':
                nx = src[i+1]; i += 2
                out.append({'n': '\n', 't': '\t', 'u': None}.get(nx, nx) if nx != 'u' else chr(int(src[i:i+4], 16)))
                if nx == 'u': i += 4
                continue
            out.append(c); i += 1
        i += 1
        return ''.join(x for x in out if x is not None)
    def value():
        nonlocal i
        ws(); c = src[i]
        if c == '{':
            i += 1; o = {}
            while True:
                ws()
                if src[i] == '}': i += 1; return o
                if src[i] in '\'"': k = string()
                else:
                    m = re.match(r'[A-Za-z_$][\w$]*', src[i:]); k = m.group(0); i += len(k)
                ws(); assert src[i] == ':', src[i-30:i+30]; i += 1
                o[k] = value(); ws()
                if src[i] == ',': i += 1
        if c == '[':
            i += 1; a = []
            while True:
                ws()
                if src[i] == ']': i += 1; return a
                a.append(value()); ws()
                if src[i] == ',': i += 1
        if c in '\'"':
            s = string(); ws()
            while i < n and src[i] == '+':
                i += 1; ws(); s += string(); ws()
            return s
        m = re.match(r'-?\d+(\.\d+)?|true|false|null', src[i:])
        tok = m.group(0); i += len(tok)
        return {'true': True, 'false': False, 'null': None}.get(tok, float(tok) if '.' in tok else (int(tok) if tok[0] in '-0123456789' else tok))
    return value()

def js_array_after(s, marker):
    j = s.index(marker) + len(marker)
    j = s.index('[', j)
    # 找到配对的 ]：借解析器
    return js_parse(s[j:])

ITEMS = {}
def add(id, **kw):
    assert id not in ITEMS, id
    kw.setdefault('k', 'qa')
    txt = plain(kw.get('f', '') + ' ' + kw.get('b', '') + ' ' + kw.get('c', ''))
    if kw.get('row'):  est = 5 + len(txt) / 9
    elif kw['k'] == 'cz': est = 20 + len(txt) / 5.5
    else: est = 10 + len(txt) / 6
    kw['e'] = int(round(est))
    ITEMS[id] = kw
    return id

# ═════════════════════════════ 政治 ═════════════════════════════
def load_politics():
    P = {}
    s = rd(os.path.join(ROOT, '背诵', 'cards.js'))
    cards = json.loads(s[s.index('['):s.rindex(']') + 1])
    order = ['my', 'sg', 'mz', 'xg', 'sx']
    SUB = {'my': '马原', 'sg': '史纲', 'mz': '毛中特', 'xg': '习概', 'sx': '思法'}
    cards.sort(key=lambda c: (order.index(c['p']), c['ch'], int(c['id'].rsplit('-', 1)[1])))
    P['cards'] = []
    for c in cards:
        nm = os.path.basename(c['url'])[:-5]; sj, rest = nm.split('_', 1)
        rest = re.sub(r'第(\d+)_(\d+)章', r'第 \1–\2 章', rest); rest = re.sub(r'第(\d+)章', r'第 \1 章', rest)
        P['cards'].append(add('pc:' + c['id'], row=1, g=sj + ' · ' + rest, f=E(c['q']), b=E(c['a']),
                              u='../' + c['url']))
    # 哲学十六原理 / 思法十四专题
    def topic(fn, pre, tag):
        arr = js_array_after(rd(os.path.join(ROOT, '背诵', fn)), 'var P=')
        out = []
        for i, p in enumerate(arr):
            body = '<ol>' + ''.join('<li>%s</li>' % x for x in p['f']) + '</ol>' \
                   + '<p class="tip"><b>⚡ 什么材料调它：</b>%s</p>' % p['s']
            cue = ''.join('<span>%s</span>' % E(k) for k in p['kw'])
            out.append(add('%s%02d' % (pre, i + 1), k='cz', g=tag, f='%d. %s' % (i + 1, p['t']), c=cue, b=body,
                           u='../讲义/' + p['u']))
        return out
    P['ph'] = topic('哲学十六原理.html', 'pph', '34 题 · 十六原理')
    P['sf'] = topic('思法十四专题.html', 'psf', '37 题 · 思法十四专题')
    # 讲义 ✍️ 金框（史纲 / 毛中特 / 习概）
    def nat(f):
        return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', f)]
    for sub, tag in (('史纲', '36 题 · 史纲框架'), ('毛中特', '35 题 · 毛中特框架'), ('习概', '35 题 · 习概框架')):
        lst = []
        for f in sorted(glob.glob(os.path.join(ROOT, '讲义', sub + '_*.html')), key=lambda p: (0 if '导论' in p else 1, nat(os.path.basename(p)))):
            s = rd(f); fn = os.path.basename(f)
            for m in re.finditer(r'<div class="mem">(.*?)</div>', s, re.S):
                inner = m.group(1).strip()
                t = re.match(r'<b>(.*?)</b>\s*(<br>)?', inner, re.S)
                title = re.sub(r'^分析题框架[：:]\s*', '', plain(t.group(1))) if t else sub + '框架'
                body = inner[t.end():] if t else inner
                # 找所在 section 的 id，便于跳回
                sec = None
                for sm in re.finditer(r'<section class="card" id="(d\d+)"', s[:m.start()]): sec = sm.group(1)
                body = re.sub(r'href="(?!https?:|#|\.\./)', 'href="../讲义/', body)
                lst.append(add('pm:%s:%d' % (fn[:-5], len(lst)), k='cz', g=tag, f=E(title), b=body,
                               u='../讲义/' + fn + ('#' + sec if sec else '')))
        P['mem_' + sub] = lst
    # 帽子对照表
    s = rd(os.path.join(ROOT, '秒杀', '选择题秒杀.html'))
    P['hat'] = {}
    for sec in re.findall(r'<section class="card">(.*?)</section>', s, re.S):
        h = plain(re.search(r'<h2>(.*?)</h2>', sec).group(1))
        rows = re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td></tr>', sec, re.S)
        if '对照' not in h and '易混' not in h: continue
        key = h[:2]
        P['hat'][key] = []
        grp = None
        for part in re.split(r'(<h3>.*?</h3>)', sec):
            if part.startswith('<h3>'): grp = plain(part); continue
            for q, a in re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td></tr>', part, re.S):
                P['hat'][key].append(add('ph:%s:%d' % (key, len(P['hat'][key])), row=1,
                                         g=re.sub(r'（.*?）', '', h) + (' · ' + grp if grp else ''), f=q, b=a, u='../秒杀/选择题秒杀.html'))
    # 八类干扰项
    sec = re.search(r'<h2>八类干扰项.*?</h2>(.*?)</section>', s, re.S).group(1)
    parts = re.split(r'<h3>(.*?)</h3>', sec)
    li = []
    for k in range(1, len(parts), 2):
        first = re.search(r'<(?:div|p)[^>]*>(.*?)</(?:div|p)>', parts[k + 1], re.S)
        li.append('<li><span class="kw">%s</span><br><span class="sm">%s</span></li>' % (plain(parts[k]), first.group(1) if first else ''))
    add('pf:8trap', k='cz', g='选择题 · 秒杀', f='八类干扰项（按出现频率排）', c='绝对化 · 主宾颠倒 · 头衔错配 · 答非所问 · 范围 · 程度 · 时间人物 · 唯心信号',
        b='<ul class="nol">' + ''.join(li) + '</ul>', u='../秒杀/选择题秒杀.html')
    for fid, title, cue, body in H.POL_FRAME:
        add('pf:' + fid, k='cz', g='分析题 · 答题骨架', f=title, c=E(cue), b=body, u='../大题/分析题答题法.html')
    return P

# ═════════════════════════════ 408 ═════════════════════════════
MATHSYM = {r'\log': 'log', r'\dots': '…', r'\cdots': '⋯', r'\times': '×', r'\cdot': '·', r'\le': '≤', r'\ge': '≥',
           r'\lfloor': '⌊', r'\rfloor': '⌋', r'\lceil': '⌈', r'\rceil': '⌉', r'\to': '→', r'\infty': '∞'}
def math(s):
    s = re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}', r'(\1)/(\2)', s)
    s = re.sub(r'C_\{?(\w+)\}?\^\{?(\w+)\}?', r'C<sub>\1</sub><sup>\2</sup>', s)
    s = re.sub(r'(?<=\w)\\log', lambda m: ' \\log', s)
    for k in sorted(MATHSYM, key=len, reverse=True): s = s.replace(k, MATHSYM[k])
    s = re.sub(r'([⌊⌈])\s+', r'\1', s); s = re.sub(r'\s+([⌋⌉])', r'\1', s)
    s = re.sub(r'\^\{([^{}]*)\}', r'<sup>\1</sup>', s); s = re.sub(r'\^(\w)', r'<sup>\1</sup>', s)
    s = re.sub(r'_\{([^{}]*)\}', r'<sub>\1</sub>', s); s = re.sub(r'_(\w)', r'<sub>\1</sub>', s)
    s = s.replace('-', '−')
    return '<i class="m">%s</i>' % s
def inline408(s):
    keep = []
    def stash(x): keep.append(x); return '\0%d\0' % (len(keep) - 1)
    s = re.sub(r'`([^`\n]+)`', lambda m: stash('<code>' + E(m.group(1)) + '</code>'), s)
    s = re.sub(r'\$([^$\n]+)\$', lambda m: stash(math(m.group(1))), s)
    s = E(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'==(.+?)==', r'<span class="r">\1</span>', s)
    s = re.sub(r'~~(.+?)~~', r'<span class="bl">\1</span>', s)
    s = re.sub(r'!!(.+?)!!', r'<span class="g">\1</span>', s)
    s = re.sub(r'__(.+?)__', r'<em>\1</em>', s)
    s = re.sub(r'_\{(.+?)\}', r'<sub>\1</sub>', s)
    s = re.sub(r'\^\{(.+?)\}', r'<sup>\1</sup>', s)
    s = re.sub(r'\[\[(\d\d)(?:#[^|\]]*)?\|([^\]]+)\]\]', r'\2', s)
    s = re.sub(r'\[\[(\d\d)[^\]]*\]\]', r'第 \1 话', s)
    s = re.sub(r'\[([^\]\n]+)\]\(([^)\s]+)\)', r'\1', s)
    s = re.sub('\0(\\d+)\0', lambda m: keep[int(m.group(1))], s)
    return s
def block408(txt):
    out = []; ul = []
    for line in txt.strip().split('\n'):
        line = line.rstrip()
        if re.match(r'\s*[-*] ', line): ul.append('<li>%s</li>' % inline408(re.sub(r'^\s*[-*] ', '', line))); continue
        if ul: out.append('<ul>' + ''.join(ul) + '</ul>'); ul = []
        if line.strip(): out.append('<p>%s</p>' % inline408(line.strip()))
    if ul: out.append('<ul>' + ''.join(ul) + '</ul>')
    return ''.join(out)

MN_EP = {'罗马数字组合': '00', '反例排除': '00', 'Cache地址划分': '31', 'IEEE754': '18', '中断三分': '23', '哈夫曼树': '07',
 '哈夫曼': '07', '系统调用': '23', 'inode': '35', '拥塞窗口': '49', '拥塞控制': '49', 'CPI': '16', '补码真值': '17', 'TLB': '33',
 '设备层次': '40', '符号扩展': '17', '带宽口径': '38', '主频周期': '16', '标志位双线': '17', '二级页表': '32', '孩子兄弟': '07',
 'B树': '13', '组相联': '31', '数据冒险': '22', '中断分工': '23', '多级页表地址': '33', '停等利用率': '43', 'TCP序号': '48',
 '排序特性对比': '15', '出栈序列': '04', 'AVL': '08', '堆': '15', '奈氏香农': '42', '滑动窗口': '43', '端口协议表': '50',
 '页式地址转换': '32', '快排划分': '14', '发送窗口': '49', '寻址方式': '19', '缺页处理': '34', 'NAT': '46', '小端': '18',
 '三态转换': '25', '磁盘调度': '37', '设备独立性': '40', '交换机自学习': '44', 'Dijkstra表': '10', 'DMA三阶段': '39',
 '路由聚合': '45', '中断隐指令': '39', '位图': '36', '中断向量表': '39', '银行家安全性': '29', '关键路径': '11', 'RTT账本': '50',
 'ARP': '46', '突发传送': '38', '窗口上限': '43', '网络地址': '45', '浮点先看阶码': '18', '芯片数': '30', '最短帧长': '44',
 'Dijkstra': '10', '混合索引': '35', '冲突域广播域': '44', '散列ASL': '12', '循环次数': '01', '度数方程': '06', '交叉编址': '30',
 '互斥四准则': '27', '时钟中断': '26', '特权指令': '23', '自陷': '23', 'Kruskal': '10', '完全二叉树': '06', '生产者消费者': '28',
 '饥饿与老化': '26', '多级反馈队列': '26', '距离向量': '47', 'DNS查询': '50', '线性探测': '12', '边界对齐': '18', '工作集': '34'}
MN_NAME = {'罗马数字组合': 'Ⅰ Ⅱ Ⅲ 组合选择题', '反例排除': '「一定 / 可能」类选项', 'IEEE754': 'IEEE 754', '哈夫曼': '哈夫曼 WPL',
           'B树': 'B 树', 'TCP序号': 'TCP 序号', '散列ASL': '散列 ASL', 'DNS查询': 'DNS 递归与迭代', 'Dijkstra表': 'Dijkstra 手算表',
           'RTT账本': 'RTT 账本', 'Cache地址划分': 'Cache 地址划分', 'DMA三阶段': 'DMA 三阶段'}

def load_408():
    plan = rd(os.path.join(S408, '_build', 'plan.py'))
    eps = {e[0]: dict(vol=int(e[1]), subj=e[2], title=e[3]) for e in re.findall(r"E\('(\d\d)',(\d+),'([^']*)','([^']*)'", plan)}
    SUBJ = {'ds': '数构', 'co': '组原', 'os': 'OS', 'net': '网络'}
    C = {k: dict(dom=[], rec=[], trap=[], mn=[]) for k in eps}
    for ep in sorted(eps):
        s = rd(os.path.join(S408, '_src', ep + '.txt'))
        meta = eps[ep]; tag = '第 %d 话 · %s' % (int(ep), meta['title'])
        url = ONLINE_408 + 'ep%s.html' % ep
        for m in re.finditer(r'^:::(domain|recall|trap)([^\n]*)\n(.*?)^:::\s*$', s, re.S | re.M):
            kind, arg, body = m.group(1), m.group(2).strip(), m.group(3)
            if kind == 'domain':
                heads = [plain(inline408(h)).rstrip('：:') for h in re.findall(r'\*\*([^*]+?)[：:]\*\*', body)]
                cue = ' · '.join(E(h) for h in heads) if heads else '说出本话的要点'
                C[ep]['dom'].append(add('cd:%s' % ep, g=('总览' if ep == '00' else SUBJ[meta['subj'].split(',')[0]]) + ' · 领域展开', f=E(tag), c=cue,
                                        b=block408(body), u=url))
            elif kind == 'recall':
                C[ep]['rec'].append(add('cr:%s:%d' % (ep, len(C[ep]['rec'])), g=tag, f=inline408(arg), b=block408(body), u=url))
            else:
                C[ep]['trap'].append(add('ct:%s:%d' % (ep, len(C[ep]['trap'])), g=tag + ' · 陷阱', f=inline408(arg), b=block408(body), u=url))
    for line in rd(os.path.join(S408, '_build', 'kpq', 'mn.txt')).split('\n'):
        if line.startswith('//') or '|' not in line: continue
        k, v = [x.strip() for x in line.split('|', 1)]
        key = k[1:] if k.startswith('T') and k[1:] in MN_EP and k not in MN_EP else k
        ep = MN_EP[key]
        name = MN_NAME.get(key, key)
        C[ep]['mn'].append(add('cm:' + k, g='口诀 · 第 %d 话' % int(ep), f=E(name), b='<p>%s</p>' % inline408(v), u=ONLINE_408 + 'ep%s.html' % ep))
    return eps, C

# ═════════════════════════════ 英语 ═════════════════════════════
def load_english():
    s = rd(os.path.join(SENG, '新版', 'data_wordbank.js'))
    d = json.loads(s[s.index('{'):s.rstrip().rstrip(';').rindex('}') + 1])
    G = {}
    def word(prefix, it, tag):
        ex = it['ex'][0] if it.get('ex') else None
        back = '<span class="gl">%s</span>' % E(it['gl'] or it.get('ox') or '')
        if ex and re.search('[A-Za-z]', ex[0]):
            back += '<span class="ex">%s <i>%s %s</i></span>' % (E(ex[0]), ex[1], E(ex[2]))
        front = '<span class="w">%s</span>' % E(it['w']) + (' <span class="ipa">%s</span>' % E(it['ipa']) if it.get('ipa') else '')
        return add(prefix + it['w'], row=1, g=tag, f=front, b=back)
    must = d['b']['must']['groups']
    G['words'] = [word('ew:', it, '必会词 · 熟词僻义') for it in must[1]['items']]
    G['att'] = []
    seen = set()
    for key in ('att', 'emo'):
        for g in d['b'][key]['groups']:
            for it in g['items']:
                if not (it.get('gl') or '').strip() or it['w'] in seen: continue
                seen.add(it['w'])
                G['att'].append(word('ea:', it, ('态度词 · ' if key == 'att' else '情绪词 · ') + g['name']))
    # 可套句：只取「中文意思 ⟹ 说明 可套：例句」齐全、骨架不太长的，按年份均匀抽
    cand = []
    PICK = [0, 1, 3, 15, 16, 20, 22, 27, 29, 47, 59, 72, 76, 82, 98, 117, 119, 120, 121, 126, 129, 131, 162, 181, 203, 221, 266, 343]
    allit = d['b']['essay']['groups'][0]['items']
    for it in [allit[i] for i in PICK]:
        gl = it.get('gl') or ''
        m = re.search(r'可套[：:]\s*(.+?)(?:（|$|　)', gl)
        if '⟹' not in gl or not m or len(it['w']) > 105: continue
        zh = gl.split('⟹')[0].strip().rstrip('。')
        exs = m.group(1).strip()
        if not re.search('[A-Za-z]{3}', exs): print('SENT SKIP', it['w']); continue
        ex0 = it['ex'][0][0] if it.get('ex') else ''
        if re.search('[A-Za-z]{3}', ex0) and len(ex0) > len(exs): exs = ex0
        cand.append((it.get('y') or 0, re.sub(r'^骨架[：:]', '', it['w']), zh, exs))
    pick = cand
    G['sent'] = []
    for y, w, zh, exs in pick:
        G['sent'].append(add('es:%d:%s' % (y, w[:40]), g='作文可套句 · %d 真题' % y, f=E(zh),
                             b='<p class="en"><b>%s</b></p><p class="en sm">例：%s</p>' % (E(w), E(exs))))
    # 🔴 阅读套路（取最基础的前 28 张）
    tr = js_array_after(rd(os.path.join(SENG, 'data_tricks_read.js')), 'window.TRICK_READ =')
    G['trick'] = []
    for t in [x for x in tr if x.get('tier') == '🔴'][:14]:
        body = '<p><b>%s</b></p><p>%s</p>' % (t['title'], t['flow']) + ('<p class="tip">%s</p>' % t['tmpl'] if t.get('tmpl') else '')
        body = re.sub(r'<a [^>]*>(.*?)</a>', r'\1', body)
        cue = ' / '.join(E(x) for x in (t.get('trig') or [])[:3])
        G['trick'].append(add('et:' + t['id'], g='阅读套路 · ' + t['qt'], f=E(t['qt']) + ' 怎么做？', c=('信号：' + cue) if cue else '', b=body,
                              u=ONLINE_ENG + '新版/套路库_阅读.html'))
    G['essay'] = [add('ee:' + eid, k='cz', g='作文框架', f=title, c=E(cue), b=body) for eid, title, cue, body in H.ESSAY]
    return G

# ═════════════════════════════ 排期 ═════════════════════════════
def chunk(lst, sizes):
    out = []; i = 0
    for s in sizes: out.append(lst[i:i + s]); i += s
    assert i == len(lst), (i, len(lst))
    return out
def even(lst, k):
    n = len(lst); return [lst[n * i // k: n * (i + 1) // k] for i in range(k)]
def by_group(lst, k):
    """按 g（章）切成 k 份，尽量不把一章拆开。"""
    total = len(lst); out = []; cur = []; target = total / k
    for idx, it in enumerate(lst):
        cur.append(it)
        nxt = lst[idx + 1] if idx + 1 < len(lst) else None
        done = sum(len(x) for x in out) + len(cur)
        boundary = nxt is None or ITEMS[nxt]['g'] != ITEMS[it]['g']
        if len(out) < k - 1 and boundary and done >= target * (len(out) + 1) - 6:
            out.append(cur); cur = []
    out.append(cur)
    while len(out) < k: out.append([])
    return out

def main():
    P = load_politics(); eps, C = load_408(); G = load_english()
    nights = []
    for i in range(NNIGHT):
        d = START + datetime.timedelta(days=i)
        nights.append(dict(n=i + 1, d=d.isoformat(), secs=[], tasks=[]))
    def sec(n, s, t, ids, hk=False, note='', mode=None):
        if not ids: return
        x = dict(s=s, t=t, ids=list(ids))
        if hk: x['hk'] = 1
        if note: x['note'] = note
        if mode: x['mode'] = mode
        nights[n - 1]['secs'].append(x)

    # ── 一轮 N1–N14 ──
    ph = P['ph']; sf = P['sf']; msg = P['mem_史纲']; mmz = P['mem_毛中特']; mxg = P['mem_习概']
    po_frames = {n: [] for n in range(1, 15)}
    for n in range(1, 9): po_frames[n] += ph[2 * (n - 1): 2 * n]
    for n, g in zip(range(1, 7), chunk(msg, [2, 2, 2, 2, 2, len(msg) - 10])): po_frames[n] += g
    for n, g in zip(range(7, 10), chunk(mmz, [2, 2, len(mmz) - 4])): po_frames[n] += g
    for n, g in zip(range(9, 15), chunk(sf, [2, 2, 2, 3, 2, 3])): po_frames[n] += g
    for n, g in zip(range(10, 15), even(mxg, 5)): po_frames[n] += g
    extra = {1: ['pf:8trap', 'pf:PF34'], 2: ['pf:PF4Q'], 4: ['pf:PFJM'], 5: ['pf:PF36'], 8: ['pf:PF35'], 9: ['pf:PF37']}
    hats = P['hat']; hat_night = {3: '马原', 6: '史纲', 9: '毛中', 12: '习概', 14: '思法'}
    cards = by_group(P['cards'], 14)
    # 408 话目分组
    EPN = [['00', '01', '02', '03'], ['04', '05', '06'], ['07', '08', '09'], ['10', '11', '12', '13'], ['14', '15', '16'],
           ['17', '18', '19'], ['20', '21', '22'], ['23', '24', '25', '26'], ['27', '28', '29'], ['30', '31', '32'],
           ['33', '34', '35', '36'], ['37', '38', '39', '40'], ['41', '42', '43', '44', '45'], ['46', '47', '48', '49', '50', '51']]
    assert sorted(sum(EPN, [])) == sorted(eps)
    words = even(G['words'], 14); sents = G['sent']; tricks = even(G['trick'], 14)
    att = G['att']; attn = chunk(att, [len(att) // 5] * 4 + [len(att) - 4 * (len(att) // 5)])
    for n in range(1, 15):
        sec(n, 'po', '分析题框架 · 合上能说出关键词', extra.get(n, []) + po_frames[n])
        if n in hat_night: sec(n, 'po', '帽子对照 · 专治「头衔错配」', next(v for k, v in hats.items() if k.startswith(hat_night[n])))
        sec(n, 'po', '选择题背诵卡 · ' + subjs(cards[n - 1]), cards[n - 1])
        grp = EPN[n - 1]
        sec(n, 'cs', '领域展开 · 每话的一页纸', [i for e in grp for i in C[e]['dom']])
        sec(n, 'cs', '合上自测 · 说出来再点开', [i for e in grp for i in C[e]['rec']])
        sec(n, 'cs', '陷阱 · 最容易丢分的那一句', [i for e in grp for i in C[e]['trap']])
        sec(n, 'cs', '口诀', [i for e in grp for i in C[e]['mn']])
        sec(n, 'en', '作文框架', [G['essay'][n - 1]['id'] if isinstance(G['essay'][n - 1], dict) else G['essay'][n - 1]] + sents[2 * (n - 1): 2 * n])
        sec(n, 'en', '阅读套路', tricks[n - 1])
        if n <= 5: sec(n, 'en', '态度词 · 情绪词（选项高频）', attn[n - 1])
        sec(n, 'en', '必会词', words[n - 1])

    # ── 二轮 N15–N21：同样的东西再过一遍，一轮标了「记住」的自动收起 ──
    allpo = ['pf:8trap', 'pf:PF34', 'pf:PF4Q', 'pf:PFJM', 'pf:PF35', 'pf:PF36', 'pf:PF37'] + ph + msg + mmz + sf + mxg
    allcards = P['cards']
    allhat = sum(hats.values(), [])
    allc408 = [i for e in sorted(eps) for i in C[e]['rec'] + C[e]['trap'] + C[e]['mn']]
    alldom = [i for e in sorted(eps) for i in C[e]['dom']]
    allen = G['essay'] + G['sent']
    for k, n in enumerate(range(15, 22)):
        sec(n, 'po', '分析题框架 · 二轮（直接合上自测）', even(allpo, 7)[k], hk=True, mode='test')
        sec(n, 'po', '帽子对照 · 二轮', even(allhat, 7)[k], hk=True)
        sec(n, 'po', '选择题背诵卡 · 二轮', by_group(allcards, 7)[k], hk=True)
        sec(n, 'cs', '领域展开 · 二轮', even(alldom, 7)[k], mode='test')
        sec(n, 'cs', '自测 · 陷阱 · 口诀 · 二轮', even(allc408, 7)[k], hk=True)
        sec(n, 'en', '作文 · 二轮', even(allen, 7)[k], hk=True, mode='test')
        sec(n, 'en', '态度词与必会词 · 二轮', even(att + G['words'], 7)[k], hk=True)

    # ── 冲刺 N22–N24 ──
    sec(22, 'po', '34 题 · 十六原理全过', ['pf:PF34'] + ph, mode='test')
    sec(22, 'en', '作文可套句 · 前半（中文提示，说出英文）', G['sent'][:14], hk=True, mode='test')
    sec(22, 'cs', '陷阱 · 43 个全过', [i for e in sorted(eps) for i in C[e]['trap']], mode='test')
    sec(23, 'po', '37 题 · 思法十四专题全过', ['pf:PF37'] + sf, mode='test')
    sec(23, 'po', '35 / 36 题 · 骨架', ['pf:PF35', 'pf:PF36', 'pf:PF4Q'], mode='test')
    sec(23, 'en', '作文可套句 · 后半', G['sent'][14:], hk=True, mode='test')
    sec(23, 'cs', '口诀 · 84 条全过', [i for e in sorted(eps) for i in C[e]['mn']], hk=True, mode='test')
    sec(24, 'po', '考前一晚 · 选择题与卷面', ['pf:8trap', 'pf:PF34', 'pf:PFJM'], mode='test')
    nights[23]['secs'].append(dict(s='po', t='一轮二轮里还标着「没记住 / 模糊」的政治条目', dyn='po', ids=[]))
    sec(24, 'en', '考前一晚 · 小作文七类信', [G['essay'][i] for i in (13, 3, 4, 5, 6, 7, 8, 9)], mode='test')
    sec(24, 'en', '考前一晚 · 大作文骨架与句型', [G['essay'][i] for i in (0, 1, 2, 10, 11, 12)], mode='test')
    nights[23]['secs'].append(dict(s='en', t='还标着「没记住 / 模糊」的英语条目', dyn='en', ids=[]))
    sec(25, 'cs', '考前一晚 · 52 话领域展开全过', alldom, mode='test')
    nights[24]['secs'].append(dict(s='cs', t='还标着「没记住 / 模糊」的 408 条目', dyn='cs', ids=[]))

    # ── 任务与每晚标题 ──
    for nt in nights:
        md = nt['d'][5:]
        if md in H.TASKS: nt['tasks'] = H.TASKS[md]
    PH = {}
    for nt in nights:
        n = nt['n']
        nt['ph'] = '一轮' if n <= 14 else '二轮' if n <= 21 else '冲刺' if n <= 24 else '考前夜'
    TITLES = {22: '冲刺 · 34 题原理 ＋ 408 陷阱', 23: '冲刺 · 37 题专题 ＋ 408 口诀', 24: '政治英语考前一晚', 25: '408 考前一晚'}
    for nt in nights:
        n = nt['n']
        if n in TITLES: nt['title'] = TITLES[n]; continue
        if n <= 14:
            grp = EPN[n - 1]
            nt['title'] = '政治 %s ｜ 408 第 %d–%d 话 ｜ 英语 %s' % (subjs(cards[n - 1]), int(grp[0]), int(grp[-1]), plain(ITEMS[G['essay'][n - 1]]['f']).replace(' · ', ''))
        else:
            nt['title'] = '二轮第 %d / 7 晚：三科再过一遍，一轮标了「记住」的自动收起' % (n - 14)
    for nt in nights:
        nt['est'] = int(round(sum(ITEMS[i]['e'] * (0.6 if s.get('hk') else 1) for s in nt['secs'] for i in s['ids']) / 60))
    # 每晚每科分钟数，打印出来调平
    for nt in nights:
        per = {}
        for s in nt['secs']:
            per[s['s']] = per.get(s['s'], 0) + sum(ITEMS[i]['e'] * (0.6 if s.get('hk') else 1) for i in s['ids'])
        print('N%02d %s %-4s %3d′  ' % (nt['n'], nt['d'][5:], nt['ph'], nt['est']) +
              '  '.join('%s %2d′/%d' % (k, int(v // 60), sum(len(s['ids']) for s in nt['secs'] if s['s'] == k)) for k, v in per.items()), nt['title'])
    used = {i for nt in nights for s in nt['secs'] for i in s['ids']}
    print('items', len(ITEMS), 'unused', len(set(ITEMS) - used), sorted(set(ITEMS) - used)[:10])
    out = dict(start=START.isoformat(), exam='2026-12-19', nights=nights, items=ITEMS,
               subj=dict(po='政治', cs='408', en='英语'), task_note=H.TASK_NOTE, built=datetime.date.today().isoformat())
    js = '/* 由 _build/tools/build_night.py 生成，别手改 */\nwindow.NIGHT=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(os.path.join(ROOT, '背诵', 'data_night.js'), 'w', encoding='utf-8').write(js)
    print('wrote', len(js) // 1024, 'KB')

def subjs(ids):
    out = []
    for i in ids:
        sj = ITEMS[i]['g'].split(' · ')[0]
        if sj not in out: out.append(sj)
    return '、'.join(out)

def hats_get(hats, pre):
    return next(v for k, v in hats.items() if k.startswith(pre))

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""三科夜背：从政治 / 408 / 英语一三个中心抽「真题里考的、能直接背的」内容，按晚排期，写 背诵/data_night.js。

    python3 _build/tools/build_night.py

数据源（兄弟仓库的现成文件，只读）：
  政治  背诵/哲学十六原理.html · 思法十四专题.html · 讲义/*.html 的 ✍️ 金框 · 套卷/data_papers.js（2024–2026 真题大题）· 秒杀/选择题秒杀.html 帽子表
  408   ../../408/复盘中心/练习系统/data_{ds,co,os,net}.js 的真题选择题：罗马数字题与「正确/错误的是」拆成逐条判断句，概念题取「题干 → 答案」
  英语  ../../英语一/阅读复盘/新版/data_wordbank.js（高频词、选项词、态度词、作文范文短语）· 20xx_翻译_*.html（划线句、采分点、参考译文）
  手写  _build/tools/night_hand.py（政治四类大题模板、英语作文完整模板、肖四任务）
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
    if kw.get('row'):  est = 4 + len(plain(kw.get('f', ''))) / 10 + len(plain(kw.get('b', ''))) / 25
    elif kw['k'] == 'cz': est = 20 + len(txt) / 5.5
    else: est = 10 + len(txt) / 6
    kw['e'] = int(round(est))
    ITEMS[id] = kw
    return id

# ═════════════════════════════ 政治 ═════════════════════════════
def kw_chain(body, n=7):
    ks = [plain(m.group(2)) for m in re.finditer(r'<span class="(kw|kd|km)">(.*?)</span>', body)]
    ks = [k for k in ks if 1 < len(k) <= 30]
    return ' → '.join(E(k) for k in ks[:n])

def load_politics():
    P = {}
    # 通用模板
    P['tpl'] = {}
    for tid, title, frame, body in H.POL_TPL:
        P['tpl'][tid] = add('pt:' + tid, k='cz', g='大题模板', f=title, c='<b>框架：</b>' + E(frame), b=body, u='../大题/分析题答题法.html')
    # 十六原理 / 思法十四专题：框架 ＝ 关键词；完整背法 ＝ 原文全部条目
    def topic(fn, pre, tag):
        arr = js_array_after(rd(os.path.join(ROOT, '背诵', fn)), 'var P=')
        out = []
        for i, p in enumerate(arr):
            body = '<ol>' + ''.join('<li>%s</li>' % x for x in p['f']) + '</ol>' \
                   + '<p class="sig"><b>材料里出现这些就用它：</b>%s</p>' % p['s']
            out.append(add('%s%02d' % (pre, i + 1), k='cz', g=tag, f='%d. %s' % (i + 1, p['t']),
                           c='<b>框架：</b>' + ' → '.join(E(k) for k in p['kw']), b=body, u='../讲义/' + p['u']))
        return out
    P['ph'] = topic('哲学十六原理.html', 'pph', '34 题 · 马原原理')
    P['sf'] = topic('思法十四专题.html', 'psf', '37 题 · 思法专题')
    # 讲义 ✍️ 金框：史纲 / 毛中特 / 习概
    def nat(f): return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', f)]
    for sub, tag in (('史纲', '36 题 · 史纲'), ('毛中特', '35 题 · 毛中特'), ('习概', '35 题 · 习概')):
        lst = []
        for f in sorted(glob.glob(os.path.join(ROOT, '讲义', sub + '_*.html')), key=lambda p: (0 if '导论' in p else 1, nat(os.path.basename(p)))):
            s = rd(f); fn = os.path.basename(f)
            for m in re.finditer(r'<div class="mem">(.*?)</div>', s, re.S):
                inner = m.group(1).strip()
                t = re.match(r'<b>(.*?)</b>\s*(<br>)?', inner, re.S)
                title = re.sub(r'^分析题框架[：:]\s*', '', plain(t.group(1))) if t else sub
                body = inner[t.end():] if t else inner
                body = re.sub(r'\s*([②③④⑤⑥⑦⑧])', r'<br>\1', body)
                sec = None
                for sm in re.finditer(r'<section class="card" id="(d\d+)"', s[:m.start()]): sec = sm.group(1)
                body = re.sub(r'href="(?!https?:|#|\.\./)', 'href="../讲义/', body)
                lst.append(add('pm:%s:%d' % (fn[:-5], len(lst)), k='cz', g=tag, f=E(title), c='<b>框架：</b>' + kw_chain(body),
                               b=body, u='../讲义/' + fn + ('#' + sec if sec else '')))
        P['mem_' + sub] = lst
    # 真题大题 2024–2026（34–37 题；38 题是当年时政，不背）
    s = rd(os.path.join(ROOT, '套卷', 'data_papers.js'))
    papers = json.loads(s[s.index('=') + 1:].strip().rstrip(';'))
    SJ = {'my': '马原', 'mz': '毛中特 ＋ 习概', 'xg': '毛中特 ＋ 习概', 'sg': '史纲', 'sx': '思法'}
    P['zt'] = {}
    for yk in ('zt-2024', 'zt-2025', 'zt-2026'):
        pap = next(x for x in papers if x['k'] == yk); y = int(yk[3:])
        for q in pap['qs']:
            if q['t'] != 'e' or q['no'] == 38: continue
            asks = ''.join('<p class="sm">%s</p>' % E(a) for a in q.get('asks', []))
            if q.get('ea'):
                back = ''.join('<p>%s</p>' % E(x) for x in q['ea'].split('\n') if x.strip())
                back = '<p class="tip"><b>官方参考答案</b></p>' + back
            else:
                back = '<p class="tip"><b>2026 年无官方答案，以下为按教材整理的答题骨架</b></p>' + ''.join('<p>%s</p>' % x for x in q['mk'].get('g', []))
            P['zt'].setdefault(q['no'], []).append(add('pz:%d:%d' % (y, q['no']), g='%d 年真题第 %d 题 · %s' % (y, q['no'], SJ.get(q['sj'], '')),
                                                    f='%d 年第 %d 题（%s）' % (y, q['no'], SJ.get(q['sj'], '')), c=asks, b=back,
                                                    u='../套卷/套卷.html?k=%s&read=1#q%d' % (yk, q['no'])))
    # 选择题帽子对照表（硬知识）
    s = rd(os.path.join(ROOT, '秒杀', '选择题秒杀.html'))
    P['hat'] = []
    for sec in re.findall(r'<section class="card">(.*?)</section>', s, re.S):
        h = plain(re.search(r'<h2>(.*?)</h2>', sec).group(1))
        if '对照' not in h and '易混' not in h: continue
        grp = None
        for part in re.split(r'(<h3>.*?</h3>)', sec):
            if part.startswith('<h3>'): grp = plain(part); continue
            for q, a in re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td></tr>', part, re.S):
                P['hat'].append(add('ph:%d' % len(P['hat']), row=1, g=re.sub(r'（.*?）', '', h) + (' · ' + grp if grp else ''),
                                    f=q, b=a, u='../秒杀/选择题秒杀.html'))
    return P

# ═════════════════════════════ 408 ═════════════════════════════
S408DATA = os.path.join(BASE, '408', '复盘中心', '练习系统')
SUBJ408 = [('data_ds.js', '数据结构'), ('data_co.js', '组成原理'), ('data_os.js', '操作系统'), ('data_net.js', '计算机网络')]
def strip(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()
def keep_inline(s): return re.sub(r'<(?!/?(b|sub|sup|i)\b)[^>]+>', '', s).strip()
def pieces(h):
    h = re.sub(r'<pre.*?</pre>', '', h, flags=re.S)
    h = re.sub(r'</tr>|<br\s*/?>|</li>|</p>', '。', h)
    h = re.sub(r'</t[dh]>', ' ｜ ', h)
    t = strip(h)
    return [x.strip(' ｜') for x in re.split(r'(?<=[。；;])', t) if len(x.strip(' ｜')) > 3]
def load_408():
    TF, CON = [], []
    for fn, subj in SUBJ408:
        s = rd(os.path.join(S408DATA, fn))
        m = re.search(r'\w+_DATA\s*=\s*\[', s)
        arr = js_parse(s[m.end() - 1:])
        for q in arr:
            if not q.get('exam') or q.get('type') != 'choice': continue
            st = q['stem']; y = q['exam']; ch = q.get('ch')
            tag = '%d 真题 · %s 第 %s 章' % (y, subj, ch)
            head = re.split(r'[ⅠⅡⅢⅣ]\s*[.．、]', st.replace('<br>', ' '))[0]
            head = strip(re.sub(r'【[^】]*】', '', head)); head = re.sub(r'[（(]\s*[)）]', '', head).strip().rstrip('。')
            rom = bool(re.search(r'[ⅠⅡ]\s*[.．、]', st))
            tfq = bool(re.search(r'(正确|错误|不正确)的(是|有)', head))
            NOISE = re.compile(r'^(一致|综上|⇒|⟹|📌|⭐|🔗|⚠️|🐍|✅|本题|这道)|值得|[：:]。$|选\s*[A-D]\s*[（(，,。]|^(因此|故|所以)?[，,]?\s*(选项\s*[A-D]|说法\s*[ⅠⅡⅢⅣ]|[ⅠⅡⅢⅣ]\s*)\s*(错误|正确|错|对)[。；;]?$')
            book_p = [x for x in pieces(q.get('book', '')) if not NOISE.search(x)]
            cl_p = [x for x in pieces(q.get('claude', '')) if not NOISE.search(x)]
            if rom or (tfq and not q.get('fig') and '<table' not in st):
                if len(head) > 70 or q.get('fig') or q.get('code'): continue
                neg = bool(re.search(r'(错误|不正确)的', head))
                if rom:
                    items = re.findall(r'([ⅠⅡⅢⅣⅤⅥ])\s*[.．、]\s*(.*?)(?=<br>|$|\s[ⅠⅡⅢⅣⅤⅥ]\s*[.．、])', st)
                    insel = set(c for c in q['opts'][ord(q['ans']) - 65] if c in 'ⅠⅡⅢⅣⅤⅥ')
                    keys = [(r, it, r in insel) for r, it in items]
                else:
                    keys = [(chr(65 + i), o, chr(65 + i) == q['ans']) for i, o in enumerate(q['opts'])]
                for r, it, sel in keys:
                    it = keep_inline(it)
                    if not strip(it) or re.fullmatch(r'[\d\s.,，、]+', strip(it)): continue
                    hit = (lambda x: r in x) if rom else (lambda x: re.search(r'(选项\s*%s|%s\s*(项|选项|错误|正确|错|对|中|的|✔|✘|✓|✗)|%s[.．、，,：:])' % (r, r, r), x))
                    why = [x for x in book_p if hit(x)] or [x for x in cl_p if hit(x)][:1]
                    why = E(' '.join(dict.fromkeys(why[:2])))
                    if len(why) > 170: why = why[:168] + '…'
                    if tfq:
                        truth = (not sel) if neg else sel
                        ctx = re.sub(r'[，,]?\s*(则)?\s*(在)?下列[^，,。]*?(叙述|说法|描述|选项|结论)?中?[，,]?\s*(正确|错误|不正确)的(是|有)$', '', head).strip('，, ')
                        tp = re.search(r'关于(.+?)的(叙述|说法|描述)', head)
                        g2 = ctx if (ctx and not ctx.startswith('下列')) else ('关于' + tp.group(1).strip() if tp else '')
                        g2 = (g2 + '，判断对错') if g2 else '判断对错'
                        f = it
                        verdict = '<b class="ok">✔ 对</b>' if truth else '<b class="ng">✘ 错</b>'
                    else:
                        truth = sel
                        g2 = head + '？'
                        f = it
                        verdict = '<b class="ok">✔ 是</b>' if truth else '<b class="ng">✘ 不是</b>'
                    TF.append((subj, ch, y, add('cj:%s:%s' % (q['id'] + fn[5:7], r), row=1, g=tag + ' ｜ ' + g2, f=f,
                                                b=verdict + (' <span class="why">%s</span>' % why if why else ''))))
                continue
            # 概念题：题干 → 答案
            o = q['opts']
            if q.get('fig') or q.get('code') or '<table' in st or '<pre' in st: continue
            if any(re.search(r'\d', x) for x in o) and not all(re.search(r'[一-鿿]', x) for x in o): continue
            if max(len(strip(x)) for x in o) > 34: continue
            sq = strip(re.sub(r'【[^】]*】', '', st)); sq = re.sub(r'[（(]\s*[)）]', '', sq).strip()
            if len(sq) > 90 or len(re.findall(r'\d', sq)) > 4: continue
            why = E(' '.join(pieces(q.get('book', ''))[:2]))[:180]
            CON.append((subj, ch, y, add('cq:%s%s' % (q['id'], fn[5:7]), row=1, g=tag, f=E(sq),
                                         b='<b>%s</b>' % E(strip(o[ord(q['ans']) - 65])) + (' <span class="why">%s</span>' % why if why else ''))))
    order = [x[1] for x in SUBJ408]
    key = lambda t: (order.index(t[0]), t[1] or 0, t[2])
    TF.sort(key=key); CON.sort(key=key)
    return [t[3] for t in TF], [t[3] for t in CON]

# ═════════════════════════════ 英语 ═════════════════════════════
def load_english():
    s = rd(os.path.join(SENG, '新版', 'data_wordbank.js'))
    d = json.loads(s[s.index('{'):s.rstrip().rstrip(';').rindex('}') + 1])
    G = {}
    seen = set()
    def word(it, tag, need_gl=True):
        w = it['w']
        if w.lower() in seen: return None
        if need_gl and not (it.get('gl') or '').strip(): return None
        seen.add(w.lower())
        exs = [e for e in (it.get('ex') or []) if re.search('[A-Za-z]{3}', e[0])][:1]
        back = '<span class="gl">%s</span>' % E(it.get('gl') or it.get('ox') or '')
        for e in exs:
            back += '<span class="ex">%s <i>%s %s</i></span>' % (E(e[0]), e[1], E(e[2]))
        cnt = ' <span class="cnt">%d 篇</span>' % it['no'] if it.get('no') else ''
        return add('ew:' + w, row=1, g=tag, f='<span class="w">%s</span>%s' % (E(w), cnt), b=back)
    def grp(key, gi, tag, need_gl=True):
        return [x for x in (word(it, tag, need_gl) for it in d['b'][key]['groups'][gi]['items']) if x]
    G['att'] = []
    for key, lab in (('att', '态度词（态度题四个选项基本从这里出）'), ('emo', '情绪词（选项高频）')):
        for gi, g in enumerate(d['b'][key]['groups']):
            G['att'] += grp(key, gi, lab + ' · ' + g['name'])
    G['opt'] = grp('opt', 0, '选项 / 题干高频词（按出现篇数排）') + grp('optph', 0, '选项高频短语', need_gl=False)
    G['body'] = grp('must', 0, '阅读正文高频词（按真题篇数排）')
    # 作文范文短语（称呼 / 落款 / 连接 / 常用搭配）
    G['ephr'] = []
    eseen = set()
    for it in d['b']['essay']['groups'][2]['items']:
        if it['w'] in eseen: continue
        eseen.add(it['w'])
        ex = it['ex'][0][0] if it.get('ex') else ''
        G['ephr'].append(add('ep:' + it['w'], row=1, g='作文范文短语 · %s' % (it.get('tag') or ''), f='<span class="w">%s</span>' % E(it['w']),
                             b='<span class="gl">%s</span>' % E(it['gl']) + ('<span class="ex">%s</span>' % E(ex) if ex else '')))
    # 翻译：每年 5 句，考点句式 ＋ 原句 → 采分片段与译法 ＋ 参考译文
    G['tr'] = []
    for f in sorted(glob.glob(os.path.join(SENG, '20*_翻译_*.html')), reverse=True):
        y = int(os.path.basename(f)[:4]); s = rd(f)
        if y < 2012: continue
        for blk in re.split(r'<div class="sent"', s)[1:]:
            qn = re.search(r'<span class="qn">(\d+)</span>', blk) or re.search(r'<div class="qn">\((\d+)\)', blk)
            kd = re.search(r'<span class="kaodian">(.*?)</span>', blk) or re.search(r'<div class="qn">[^<]*?考点[：:]\s*(.*?)</div>', blk)
            sdiv = re.search(r'<div class="src">(.*?)</div>', blk, re.S)
            src = None
            if sdiv and '<img' not in sdiv.group(1):
                us = re.findall(r'<u>(.*?)</u>', sdiv.group(1), re.S)
                src = re.match(r'(.*)', us[0] if len(us) == 1 else sdiv.group(1), re.S)
            img = re.search(r'<img class="strip" src="([^"]+)"', blk)
            if not (qn and (src or img)): continue
            front = '<span class="en">%s</span>' % keep_inline(src.group(1)) if src else '<img class="strip" src="%s" alt="%d 年第 %s 题原卷句条" loading="lazy">' % (ONLINE_ENG + img.group(1), y, qn.group(1))
            pts = re.findall(r'<div class="en2">(.*?)</div><div class="how">(.*?)</div>', blk, re.S)
            ref = re.search(r'<div class="refzh">(.*?)</div>', blk, re.S)
            back = '<ul class="pts">' + ''.join('<li><span class="en">%s</span> → %s</li>' % (keep_inline(a), keep_inline(b)) for a, b in pts) + '</ul>'
            if ref: back += '<p class="ref"><b>参考译文：</b>%s</p>' % keep_inline(re.split(r'<br\s*/?>', ref.group(1))[0])
            G['tr'].append(add('etr:%d:%s' % (y, qn.group(1)), g='%d 翻译 第 %s 题' % (y, qn.group(1)),
                               c=('<b>句式：</b>' + E(plain(kd.group(1)))) if kd else '',
                               f=front, b=back,
                               u=ONLINE_ENG + os.path.basename(f)))
    G['essay'] = [add('ee:' + eid, k='cz', g='作文模板', f=title, c='<b>结构：</b>' + E(frame), b=body) for eid, title, frame, body in H.ESSAY]
    return G

# ═════════════════════════════ 排期 ═════════════════════════════
def even(lst, k):
    n = len(lst); return [lst[n * i // k: n * (i + 1) // k] for i in range(k)]
def chunk(lst, sizes):
    out = []; i = 0
    for s in sizes: out.append(lst[i:i + s]); i += s
    assert i == len(lst), (i, len(lst))
    return out

def main():
    P = load_politics(); TF, CON = load_408(); G = load_english()
    nights = [dict(n=i + 1, d=(START + datetime.timedelta(days=i)).isoformat(), secs=[], tasks=[]) for i in range(NNIGHT)]
    def sec(n, s, t, ids, hk=False):
        if not ids: return
        x = dict(s=s, t=t, ids=list(ids))
        if hk: x['hk'] = 1
        nights[n - 1]['secs'].append(x)

    # ── 一轮 N1–N14：全部内容各过一遍 ──
    T = P['tpl']; ph, sf = P['ph'], P['sf']; msg, mmz, mxg = P['mem_史纲'], P['mem_毛中特'], P['mem_习概']
    tpl = {n: [] for n in range(1, 15)}
    tpl[1].append(T['T34']); tpl[2].append(T['T36']); tpl[8].append(T['T35']); tpl[9].append(T['T37'])
    for n in range(1, 9): tpl[n] += ph[2 * (n - 1): 2 * n]
    for n, g in zip(range(1, 8), chunk(msg, [2, 2, 2, 2, 2, 2, len(msg) - 12])): tpl[n] += g
    for n, g in zip(range(8, 11), chunk(mmz, [2, 2, len(mmz) - 4])): tpl[n] += g
    for n, g in zip(range(9, 15), chunk(sf, [2, 2, 2, 3, 2, 3])): tpl[n] += g
    for n, g in zip(range(11, 15), even(mxg, 4)): tpl[n] += g
    zt = {1: P['zt'][34][0:1], 2: P['zt'][34][1:2], 3: P['zt'][34][2:3], 4: P['zt'][36][0:1], 5: P['zt'][36][1:2], 6: P['zt'][36][2:3],
          7: P['zt'][35][0:1], 8: P['zt'][35][1:2], 9: P['zt'][35][2:3], 10: P['zt'][37][0:1], 11: P['zt'][37][1:2], 12: P['zt'][37][2:3]}
    hats = even(P['hat'], 14)
    tf = even(TF, 14); con = even(CON, 14)
    tr = even(G['tr'], 14)
    words = even(G['att'] + G['opt'] + G['body'], 14)
    essay = {1: ['ESS1'], 2: ['LTR0'], 3: ['LTR1'], 4: ['LTR2'], 5: ['LTR3'], 6: ['LTR4'], 7: ['ESS2'], 8: ['LTR5'], 9: ['LTR6'],
             10: ['LTR7'], 11: ['ESS1'], 12: ['LTR0'], 13: ['ESS2'], 14: ['LTR1']}
    ephr = even(G['ephr'], 14)
    for n in range(1, 15):
        sec(n, 'po', '大题：框架 ＋ 完整背法', tpl[n])
        sec(n, 'po', '真题大题原题 ＋ 答案', zt.get(n, []))
        sec(n, 'po', '选择题：易混提法与帽子', hats[n - 1])
        sec(n, 'cs', '真题判断句：这句话对不对', tf[n - 1])
        sec(n, 'cs', '真题概念题：题干 → 答案', con[n - 1])
        sec(n, 'en', '作文模板', ['ee:' + e for e in essay[n]])
        sec(n, 'en', '作文范文短语', ephr[n - 1])
        sec(n, 'en', '翻译真题：句式 ＋ 采分点译法', tr[n - 1])
        sec(n, 'en', '阅读 / 完形高频词（真题原句）', words[n - 1])

    # ── 二轮 N15–N21：每晚合并一轮的两晚，一轮标了「记住」的自动收起 ──
    for j in range(7):
        n = 15 + j
        a, b = 2 * j + 1, 2 * j + 2
        sec(n, 'po', '大题框架再背一遍（合上自测）', tpl[a] + tpl[b])
        for s_, t_ in (('po', '政治选择题'), ('cs', '408 判断句与概念题'), ('en', '英语翻译与单词')):
            ids = [i for x in (a, b) for sc in nights[x - 1]['secs'] if sc['s'] == s_ and not sc['t'].startswith(('大题', '作文模板')) for i in sc['ids']]
            if ids: nights[n - 1]['secs'].append(dict(s=s_, t='%s：一轮第 %d、%d 晚里标了没记住 / 模糊的' % (t_, a, b), ids=ids, wk=1))
        sec(n, 'en', '作文模板', ['ee:' + e for e in (['ESS1', 'LTR0'], ['LTR1', 'LTR2'], ['LTR3', 'LTR4'], ['ESS2', 'LTR5'], ['LTR6', 'LTR7'], ['ESS1', 'ESS2'], ['LTR0', 'LTR1'])[j]])

    # ── 冲刺 N22–N24（政治英语），N25（408） ──
    sec(22, 'po', '34 题：十六原理全背', [T['T34']] + ph)
    sec(23, 'po', '37 题：思法十四专题全背', [T['T37']] + sf)
    sec(23, 'po', '36 题：史纲框架全背', [T['T36']] + msg)
    sec(24, 'po', '35 题：毛中特 ＋ 习概框架', [T['T35']] + mmz + mxg, hk=True)
    nights[23]['secs'].append(dict(s='po', t='一轮二轮里还标着「没记住 / 模糊」的政治条目', dyn='po', ids=[]))
    sec(22, 'en', '小作文七类全背', ['ee:LTR%d' % i for i in range(8)])
    sec(22, 'en', '大作文两类全背', ['ee:ESS1', 'ee:ESS2'])
    sec(24, 'en', '作文模板最后一遍', ['ee:ESS1', 'ee:ESS2', 'ee:LTR0'])
    nights[23]['secs'].append(dict(s='en', t='还标着「没记住 / 模糊」的英语条目', dyn='en', ids=[]))
    sec(25, 'cs', '真题概念题全过', CON, hk=True)
    nights[24]['secs'].append(dict(s='cs', t='还标着「没记住 / 模糊」的 408 判断句与概念题', dyn='cs', ids=[]))

    for nt in nights:
        md = nt['d'][5:]
        if md in H.TASKS: nt['tasks'] = H.TASKS[md]
        n = nt['n']
        nt['ph'] = '一轮' if n <= 14 else '二轮' if n <= 21 else '冲刺' if n <= 24 else '考前夜'
    def subjs(ids):
        out = []
        for i in ids:
            sj = ITEMS[i]['g'].split(' 第')[0].split(' · ')[-1] if i.startswith('cj') or i.startswith('cq') else ''
            if sj and sj not in out: out.append(sj)
        return '、'.join(out)
    TITLES = {22: '冲刺：34 题十六原理 ＋ 作文全部模板', 23: '冲刺：37 题思法 ＋ 36 题史纲', 24: '政治英语考前一晚', 25: '408 考前一晚'}
    for nt in nights:
        n = nt['n']
        if n in TITLES: nt['title'] = TITLES[n]
        elif n <= 14:
            po = '、'.join(dict.fromkeys(ITEMS[i]['g'].split(' · ')[-1] for i in tpl[n] if not i.startswith('pt:')))
            nt['title'] = '政治 %s ｜ 408 %s ｜ 英语 %s' % (po, subjs(tf[n - 1] + con[n - 1]), plain(ITEMS['ee:' + essay[n][0]]['f']).split(' · ')[-1].split('（')[0])
        else:
            nt['title'] = '二轮：大题框架再背 ＋ 一轮第 %d、%d 晚标了没记住 / 模糊的' % (2 * n - 29, 2 * n - 28)
        nt['est'] = int(round(sum(ITEMS[i]['e'] * (0.6 if s.get('hk') else 0.3 if s.get('wk') else 1) for s in nt['secs'] for i in s['ids']) / 60))
    for nt in nights:
        per = {}
        for s in nt['secs']:
            per[s['s']] = per.get(s['s'], 0) + sum(ITEMS[i]['e'] * (0.6 if s.get('hk') else 0.3 if s.get('wk') else 1) for i in s['ids'])
        print('N%02d %s %-3s %3d′ ' % (nt['n'], nt['d'][5:], nt['ph'], nt['est']) +
              '  '.join('%s %2d′/%d' % (k, int(v // 60), sum(len(s['ids']) for s in nt['secs'] if s['s'] == k)) for k, v in per.items()), nt['title'][:60])
    used = {i for nt in nights for s in nt['secs'] for i in s['ids']}
    print('items', len(ITEMS), 'unused', len(set(ITEMS) - used), sorted(set(ITEMS) - used)[:8])
    print('408 判断句', len(TF), '概念题', len(CON), '| 翻译', len(G['tr']), '词', len(G['att'] + G['opt'] + G['body']), '| 政治模板', len(ph) + len(sf) + len(msg) + len(mmz) + len(mxg) + 4)
    out = dict(start=START.isoformat(), exam='2026-12-19', nights=nights, items=ITEMS,
               subj=dict(po='政治', cs='408', en='英语'), task_note=H.TASK_NOTE, built=datetime.date.today().isoformat())
    js = '/* 由 _build/tools/build_night.py 生成，别手改 */\nwindow.NIGHT=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(os.path.join(ROOT, '背诵', 'data_night.js'), 'w', encoding='utf-8').write(js)
    print('wrote', len(js) // 1024, 'KB')

if __name__ == '__main__':
    main()

# 整卷数据：work/papers_raw.json（parse_papers.py 输出）＋ notes/papers_fix.json（逐题人工校对）→ 套卷/data_papers.js
# notes/papers_fix/<卷>.json 逐题校对 ＋ global.json 全局形近字表 [[原, 改], …]（在逐题校对之后套用）
# 逐题格式：{卷k: {题号: {"字段": [[原文, 改为], ...] 或 "=整段新文本"}}}
#   字段：stem / A B C D / jx / ea / ans；原文找不到会打印 FIX MISS
import json, os, re, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(B)
CN = '一二三四五六七八'
# 2024 起五科题号分布三年一致（README「已知事实」）
def subj(no):
    if no <= 16: return 'my' if no <= 4 else 'mz' if no <= 6 else 'xg' if no <= 9 else 'sg' if no <= 13 else 'sx' if no == 14 else 'sz'
    if no <= 33: return 'my' if no <= 21 else 'mz' if no == 22 else 'xg' if no <= 26 else 'sg' if no <= 29 else 'sx' if no <= 31 else 'sz'
    return {34: 'my', 35: 'xg', 36: 'sg', 37: 'sx', 38: 'sz'}[no]

def clean(s):
    s = s or ''
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'(?<=[一-鿿，。、；：“”（）])[ \t]+(?=[一-鿿，。、；：“”（）])', '', s)
    s = s.replace('“ ', '“').replace(' ”', '”')
    # 识别时被当成缩进而断开的行：上一行不是句末就并回去
    s = re.sub(r'(?<![。！？”：；）)])\n(?![（(][1-6一二三]|第[一二三四五六]|[①②③④⑤]|材料\s*[1-6一二三]|摘|【)', '', s)
    s = re.sub(r'\s*三、\s*材料分析题.*$', '', s, flags=re.S)
    s = re.sub(r'(?<=[）)])\s*(材料\s*[1-6一二三四])(?=\s*\n)', r'\n\1', s)
    s = re.sub(r'(^|\n)(材料\s*[1-6一二三四])\s*(?=[^\n])', r'\1\2\n', s)
    return s.strip()

def asks_of(stem):
    """末尾从（1）起的那几行是设问；设问折行的续行并回上一问"""
    lines = stem.split('\n')
    idx = [i for i, l in enumerate(lines) if re.match(r'^\s*[（(]1[)）]', l)]
    if not idx: return stem.strip(), []
    i = idx[-1]; asks = []
    for l in lines[i:]:
        if re.match(r'^\s*[（(][1-4][)）]', l) or not asks: asks.append(l.strip())
        else: asks[-1] += l.strip()
    return '\n'.join(lines[:i]).strip(), asks

# ---- 秒杀笔记 ＋ 知识点 ＋ 口诀：notes/paper_notes/<卷>.json ----
# {题号: {m 秒杀, x 形象理解, k 口诀, n 新口径, lk 1|2|3(取自动候选第几名)|"讲义/xx.html#dN"|0(不挂)}}；分析题 {g:[每问骨架], p 卷面要点, k, n, lk}
NOTE_FIELDS = ('m', 'x', 'k', 'n', 'g', 'p')
def sec_titles():
    import glob, html as H
    T = {}
    for f in glob.glob(f'{ROOT}/讲义/*.html'):
        src = open(f, encoding='utf-8').read(); rel = '讲义/' + os.path.basename(f)
        for sid, body in re.findall(r'<section class="card" id="(d\d+)">(.*?)</section>', src, re.S):
            h = re.search(r'<h2>(.*?)</h2>', body, re.S)
            if h: T[f'{rel}#{sid}'] = re.sub(r'^\d+', '', H.unescape(re.sub(r'<[^>]+>', '', h.group(1))).strip())
    return T
TITLES = None; AUTO = None; NOTES = None
def load_notes():
    global TITLES, AUTO, NOTES
    TITLES = sec_titles()
    a = f'{B}/work/paper_lk_auto.json'; AUTO = json.load(open(a)) if os.path.exists(a) else {}
    NOTES = {}; D = f'{B}/notes/paper_notes'
    for f in sorted(os.listdir(D)) if os.path.isdir(D) else []:
        if f.endswith('.json'): NOTES.setdefault(f[:-5], {}).update(json.load(open(f'{D}/{f}')))
def lk_of(k, no, v):
    if v == 0: return None
    if isinstance(v, str):
        u = v if v.startswith('讲义/') else '讲义/' + v
        if '.html' not in u: u = u.replace('#', '.html#')
        if u not in TITLES: print('BAD LK', k, no, v); return None
        return u + '|' + TITLES[u]
    c = AUTO.get(f'{k}:{no}') or []
    i = (v or 1) - 1
    return (c[i][0] + '|' + TITLES.get(c[i][0], c[i][1])) if i < len(c) else None
def attach(k, qs):
    N = NOTES.get(k, {})
    for q in qs:
        n = N.get(str(q['no']))
        if n is None: continue
        mk = {f: n[f] for f in NOTE_FIELDS if n.get(f)}
        if mk: q['mk'] = mk
        lk = lk_of(k, q['no'], n.get('lk'))
        if lk: q['lk'] = lk
        if n.get('lk2'):
            l2 = lk_of(k, q['no'], n['lk2'])
            if l2: q['lk2'] = l2

# ---- 押题卷：notes/yati/<yt-N>.json ----
# {k, name, sub, qs:[{no, from:"my-s-45"} | {no, t, stem, opts, ans, jx, src:"自编"} | 分析题 {no, t:"e", stem, asks, ea, src}，以上都可带 m/x/k/n/lk}]}
def pool():
    P1 = {}
    for p in ['my', 'mz', 'xg', 'sg', 'sx']:
        s = open(f'{ROOT}/题库/data_{p}.js', encoding='utf-8').read(); i = re.search(r'POL\.\w+\s*=', s).end()
        d = json.JSONDecoder().raw_decode(s[i:].lstrip())[0]
        for q in d['qs']: P1[q['id']] = (d['short'], q)
    return P1
TN = {'s': '单选', 'm': '多选', 'e': '分析题'}
def yati():
    D = f'{B}/notes/yati'
    if not os.path.isdir(D): return []
    P1 = pool(); out = []
    for f in sorted(os.listdir(D)):
        if not f.endswith('.json'): continue
        Y = json.load(open(f'{D}/{f}')); qs = []
        for y in Y['qs']:
            no = y['no']
            if y.get('from'):
                short, q = P1[y['from']]
                fs = f"1000 题 · {short}{TN[q['t']]} {q['no']}" + (f"（P{q['page']}）" if q.get('page') else '')
                if q['t'] == 'e':
                    st, asks = asks_of(clean(q['stem']))
                    d = {'no': no, 't': 'e', 'sj': subj(no), 'stem': st, 'asks': asks, 'ea': clean(q.get('ea') or ''), 'from': y['from'], 'fsrc': fs}
                    if no < 34 or not asks: print('YT ESSAY BAD', Y['k'], no, y['from'])
                else:
                    d = {'no': no, 't': q['t'], 'sj': subj(no), 'stem': q['stem'], 'opts': list(q['opts']), 'ans': q['ans'],
                         'jx': (q.get('jx') or '') + ('\n【名师点拨】' + q['db'] if q.get('db') else ''), 'from': y['from'], 'fsrc': fs}
                    if q['t'] != {True: 's', False: 'm'}[no <= 16]: print('YT TYPE MISMATCH', Y['k'], no, y['from'])
                    if not d['jx'] and q.get('jj'): d['jx'] = q['jj']['t']
                    if q.get('my') and not y.get('m'): y = dict(y, m=q['my'])
                if q.get('lk') and not y.get('lk'): d['lk'] = q['lk']
            else:
                d = {'no': no, 't': y['t'], 'sj': subj(no), 'stem': y['stem'], 'fsrc': y.get('src', '自编')}
                if y['t'] != 'e': d.update(opts=y['opts'], ans=y['ans'], jx=y['jx'])
                else: d.update(asks=y['asks'], ea=y['ea'])
            mk = {fl: y[fl] for fl in NOTE_FIELDS if y.get(fl)}
            if mk: d['mk'] = mk
            if y.get('lk'):
                lk = lk_of(Y['k'], no, y['lk'])
                if lk: d['lk'] = lk
            qs.append(d)
        assert [q['no'] for q in qs] == list(range(1, 39)), (Y['k'], [q['no'] for q in qs])
        for q in qs:
            if q['t'] != 'e': assert q['ans'] and len(q['opts']) == 4 and all(q['opts']) and (len(q['ans']) == 1) == (q['t'] == 's'), (Y['k'], q['no'])
        out.append({'k': Y['k'], 'kind': 'yt', 'name': Y['name'], 'sub': Y['sub'], 'src': '押题卷', 'proof': True, 'qs': qs})
        print(Y['k'], len(qs), 'from1000', sum(1 for q in qs if q.get('from')), 'self', sum(1 for q in qs if not q.get('from')))
    return out

def main():
    load_notes()
    raw = json.load(open(f'{B}/work/papers_raw.json'))
    zt = f'{B}/work/papers_zt.json'
    if os.path.exists(zt): raw.update(json.load(open(zt)))
    fx = {}; FD = f'{B}/notes/papers_fix'
    for f in sorted(os.listdir(FD)) if os.path.isdir(FD) else []:
        if f.endswith('.json') and f != 'global.json': fx.update(json.load(open(f'{FD}/{f}')))
    G = json.load(open(f'{FD}/global.json')) if os.path.exists(f'{FD}/global.json') else []
    def g(s):
        for a, b in G: s = re.sub(a[3:], b, s) if a.startswith('re:') else s.replace(a, b)
        return s
    JZ = json.load(open(f'{B}/work/jzt.json')) if os.path.exists(f'{B}/work/jzt.json') else {}
    out = []
    for k in sorted(raw, key=lambda k: (k[:2] != 'x8', k)):
        P = raw[k]; F = fx.get(k, {}); qs = []
        RQ = P['qs']
        # 第 34 题参考答案并进了第 33 题解析（「三、材料分析题 34.参考答案」那行没切开）
        q33 = next((q for q in RQ if q['no'] == 33), None); q34 = next((q for q in RQ if q['no'] == 34), None)
        if q33 and q34 and not q34.get('ea'):
            m = re.search(r'\s*三、\s*材料分析题\s*\S{0,3}\s*[.．]?\s*参考答案\s*', q33.get('jx', ''))
            if m: q34['ea'] = q33['jx'][m.end():]; q33['jx'] = q33['jx'][:m.start()]
        # 下一题的「N.答案 X 简析…」被并进上一题解析（题号行没识别出来）：切回去
        for i in range(len(RQ) - 1):
            q1, q2 = RQ[i], RQ[i + 1]
            if q1['t'] == 'e' or q2['t'] == 'e' or q2.get('jx'): continue
            m = re.search(r'(?<=[。）)])\s*%d\s*[.．]\s*[［\[【]?\s*答{1,2}[案察]?\s*[】\]]?\s*[A-D]{0,4}\s*[（(]?简析[)）]?\s*' % q2['no'], q1.get('jx', ''))
            if m: q2['jx'] = q1['jx'][m.end():]; q1['jx'] = q1['jx'][:m.start()]
        for q in P['qs']:
            no = q['no']; f = F.get(str(no), {})
            d = {'no': no, 't': q['t'], 'sj': subj(no), 'stem': q.get('stem', ''), 'pg': q.get('pg')}
            if q['t'] != 'e':
                d['opts'] = list(q.get('opts') or ['', '', '', ''])
                d['ans'] = q.get('ans', ''); d['jx'] = q.get('jx', '')
                j = JZ.get(k[3:] + '-' + str(no)) if k.startswith('zt') else None
                if j and not d['jx']:   # 真题解析取自《讲真题》解析分册（时政题它不收）
                    d['jx'] = re.sub(r'^.{0,3}?(试题简析|试题筒析)\s*', '', j['jx']) + ('\n【名师点拨】' + j['db'] if j['db'] else ''); d['jxsrc'] = '讲真题解析分册 P%d' % j['pg']
            else: d['ea'] = q.get('ea', '')
            # 先统一清洗＋全局形近字，再套逐题校对（这样校对的「原文」与 dump_paper.py 看到的一致）
            d['stem'] = g(clean(d['stem']))
            if 'opts' in d: d['opts'] = [g(clean(o)) for o in d['opts']]; d['jx'] = g(clean(d['jx'])).replace('\n\n', '\n')
            else: d['ea'] = g(clean(d['ea']))
            for fld, ch in f.items():
                key, idx = (('opts', 'ABCD'.index(fld)) if fld in 'ABCD' and len(fld) == 1 else (fld, None))
                cur = d[key][idx] if idx is not None else d.get(key, '')
                if isinstance(ch, str) and ch.startswith('='): cur = ch[1:]
                else:
                    for a, b in ch:
                        if a in cur: cur = cur.replace(a, b, 1)
                        elif b in cur: pass   # 全局表已经改好了
                        else: print('FIX MISS', k, no, fld, a)
                if idx is not None: d[key][idx] = cur
                else: d[key] = cur
            if q['t'] == 'e': d['stem'], d['asks'] = asks_of(d['stem'])
            qs.append(d)
        if k.startswith('x8'):
            n = int(k.split('-')[1])
            meta = {'k': k, 'kind': 'x8', 'name': f'肖八 · 第{CN[n-1]}套', 'sub': f'2027 考研政治冲刺 8 套卷（{CN[n-1]}）', 'src': '肖八试题册'}
        else:
            y = k.split('-')[1]
            meta = {'k': k, 'kind': 'zt', 'name': f'{y} 年真题', 'sub': f'{y} 年全国硕士研究生招生考试思想政治理论', 'src': '近 3 年真题试卷'}
        meta['proof'] = bool(F.get('_done'))
        attach(k, qs)
        meta['qs'] = qs; out.append(meta)
        bad = [q['no'] for q in qs if q['t'] != 'e' and (not q['ans'] or not all(q['opts']) or not q['jx'])]
        bade = [q['no'] for q in qs if q['t'] == 'e' and (not q['ea'] or not q['asks'])]
        print(k, len(qs), 'incomplete', bad, 'essay', bade)
    out += yati()
    miss = [f"{p['k']}:{q['no']}" for p in out for q in p['qs'] if not q.get('mk')]
    nolk = [f"{p['k']}:{q['no']}" for p in out for q in p['qs'] if not q.get('lk') and q['sj'] != 'sz']
    print('notes missing', len(miss), miss[:20]); print('no lk (non-sz)', len(nolk), nolk[:20])
    js = '/* 由 _build/tools/build_papers.py 生成，别手改；校对写进 _build/notes/papers_fix/ */\nwindow.PAPERS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(f'{ROOT}/套卷/data_papers.js', 'w').write(js)
    print('wrote', len(js), 'bytes')

main()

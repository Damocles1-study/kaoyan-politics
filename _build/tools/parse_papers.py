# 肖八（试题册＋解析册）与近 3 年真题的 OCR → 结构化题目
# 输入：_build/ocr/<书>.txt（ocr_vote.py 投票后的 <书>__vote.txt 优先）
# 输出：_build/work/papers_raw.json  {卷k: {name, qs:[{no,t,stem,opts,ans,jx,ea,asks,pg}]}}
import re, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ocrlines import load, rows
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8}

def src(name):
    v = f'{B}/ocr/{name}__vote.txt'
    return v if os.path.exists(v) else f'{B}/ocr/{name}.txt'

def page_rows(P, pg):
    """一页 → [(x0, y0, text)]：同一行的几块按 x 拼接；去页眉页码"""
    R = rows(P[pg], tol=9)
    out = []
    for z in R:
        x0, y0, x1, y1, t = z
        if out and abs((y0 + y1) / 2 - out[-1][3]) < 9:
            gap = x0 - out[-1][4]
            out[-1][2] += (' ' if gap > 12 else '') + t
            out[-1][4] = x1
        else:
            out.append([x0, y0, t, (y0 + y1) / 2, x1])
    res = []
    for x0, y0, t, ym, x1 in out:
        if ym < 68 and ('套卷' in t or 'ZUZ' in t or '答案及解析' in t or '讲真题' in t or '部分' in t or len(t) < 4): continue
        if ym > 930 and re.fullmatch(r'[\d\s•.·]{1,4}', t): continue
        res.append((x0, y0, t.strip()))
    return res

def joinlines(lines):
    """[(x0,text)] → 段落文本：缩进或以 ①（1）材料 开头的行另起一段，其余直接接上"""
    if not lines: return ''
    left = sorted(x for x, _ in lines)[max(0, len(lines) // 5 - 1)]
    s = ''
    for i, (x, t) in enumerate(lines):
        newp = i > 0 and (x - left > 22 or re.match(r'^(①|②|③|④|⑤|[（(][1-6一二三][)）]|材料\s*[1-6一二三四]|【材料)', t))
        if i == 0: s = t
        elif newp: s += '\n' + t
        else:
            sep = ' ' if (re.search(r'[A-Za-z0-9]$', s) and re.match(r'^[A-Za-z0-9]', t)) else ''
            s += sep + t
    return s

OPT = re.compile(r'(?:(?<![A-Za-z0-9])|^)([A-D])\s*[.．。、,，·]\s*')
QNO = re.compile(r'^(\d{1,2})\s*[.．、,，。]\s*')

def split_opts(t):
    ms = list(OPT.finditer(t))
    return [(m.group(1), t[m.end():(ms[i + 1].start() if i + 1 < len(ms) else len(t))].strip()) for i, m in enumerate(ms)]

def parse_test(book, title_re, keyfn):
    P = load(src(book))
    papers = {}; cur = None; q = None; sec = None
    def flush():
        nonlocal q
        if q is None: return
        if q['_o']:
            q['opts'] = [joinlines(q['_o'].get(L, [])) for L in 'ABCD']
        q['stem'] = joinlines(q['_s'])
        del q['_s'], q['_o'], q['_last']
        cur['qs'].append(q); q = None
    for pg in sorted(P):
        PR = page_rows(P, pg)
        body = [x for x, y, t in PR if y > 70]
        pmin = min(body) if body else 0
        xs = sorted(body); pmed = xs[len(xs) // 2] if xs else 0
        for x0, y0, t in PR:
            m = re.search(title_re, t)
            if m and y0 > 80 and y0 < 200:
                flush(); k = keyfn(m)
                cur = papers.setdefault(k, {'qs': [], 'pg0': pg}); sec = None; continue
            if cur is None: continue
            if re.match(r'^一、\s*单项选择', t): sec = 's'; continue
            if re.match(r'^二、\s*多项选择', t): flush(); sec = 'm'; continue
            if re.match(r'^三、\s*材料分析', t): flush(); sec = 'e'; continue
            if sec is None: continue
            mq = QNO.match(t)
            exp = (cur['qs'][-1]['no'] + 1 if cur['qs'] else 1) if q is None else q['no'] + 1
            hit = mq and (int(mq.group(1)) == exp or (exp >= 10 and mq.group(1) == str(exp)[-1] and x0 - pmin < 14))
            # 题号被装订线吃掉：上一题四个选项已齐（分析题除外），这一行顶格且不是选项 ⟹ 新题
            lost = (not hit and q is not None and sec != 'e' and q['t'] != 'e' and len(q['_o']) == 4 and x0 < pmed - 10
                    and not OPT.match(t) and q['_last'] == 'D' and exp <= 33)
            if hit or lost:
                flush()
                body_t = t[mq.end():] if hit else re.sub(r'^[^\u4e00-\u9fff“《0-9]+', '', t)
                q = {'no': exp, 't': sec, 'pg': pg + 1, '_s': [(x0 + 30, body_t)], '_o': {}, '_last': 's'}
                if lost: q['lostno'] = 1
                continue
            if q is None: continue
            if q['t'] != 'e' and OPT.match(t):
                for L, ot in split_opts(t):
                    q['_o'].setdefault(L, []).append((x0, ot)); q['_last'] = L
                continue
            if q['_last'] == 's': q['_s'].append((x0, t))
            else: q['_o'][q['_last']].append((x0 + 40, t))
    flush()
    return papers

AQ = re.compile(r'^(\d{1,2})\s*[.．、,，。]?\s*[［\[【(（]?\s*(?:答案|签案|答業|答桌|答察|答棄|[答签啓].|.案)\s*[】\]）)]?\s*[，,:：]?\s*([A-Da-dcC]{1,4})(?![a-z])')
EQ = re.compile(r'^(\d{1,2})\s*[.．、,，。]?\s*[【\[（(]?\s*参考答案\s*[】\]）)]?\s*')
JXHEAD = re.compile(r'^[（(【]?\s*(?:简析|简标|窗析|筒析|简折|简新|简|商析|節析)\s*[)）】]?\s*')

def parse_ans(book, title_re, keyfn):
    P = load(src(book))
    out = {}; cur = None; q = None; grid = None
    def flush():
        nonlocal q
        if q is None: return
        txt = joinlines(q['_l'])
        if q['t'] == 'e': cur[q['no']] = {'ea': txt}
        else: cur[q['no']] = {'ans': q['ans'], 'jx': JXHEAD.sub('', txt, count=1)}
        q = None
    for pg in sorted(P):
        PR = []
        for x0, y0, t in page_rows(P, pg):
            parts = re.split(r'(?<=[。）)])\s*(?=\d{1,2}\s*[.．、]\s*[［\[【]?\s*(?:答|签|啓|.案))', t)
            PR += [(x0, y0, parts[0])] + [(x0 - 30, y0, p_) for p_ in parts[1:]]
        for x0, y0, t in PR:
            m = re.search(title_re, t)
            if m and 80 < y0 < 200:
                flush(); cur = out.setdefault(keyfn(m), {}); grid = cur.setdefault('_grid', []); continue
            if cur is None: continue
            ma = AQ.match(t); me = EQ.match(t)
            exp = (q['no'] + 1) if q else 1
            if not ma and q and q['t'] == 'c' and exp <= 33:
                m2 = re.match(r'^[^\u4e00-\u9fff]{0,4}(?:答案|签案|答業)\s*([A-Da-dc]{1,4})\b', t)
                if m2: ma = type('M', (), {'group': lambda self, i, a=m2, e=exp: str(e) if i == 1 else a.group(1), 'end': lambda self, a=m2: a.end()})()
            if not me and q and exp >= 34 and exp <= 38:
                m3 = re.match(r'^[^\u4e00-\u9fff]{0,4}[【\[（(]?\s*参考答案\s*[】\]）)]?\s*', t)
                if m3 and (q['t'] == 'e' or exp == 34): me = type('M', (), {'group': lambda self, i, e=exp: str(e), 'end': lambda self, a=m3: a.end()})()
            if grid is not None and not ma:
                if re.fullmatch(r'[\dA-Dc\s.．]+', t) or '答案速' in t or '选择题' in t:
                    grid.append(t); continue
            if ma: grid = None
            if ma and 1 <= int(ma.group(1)) <= 33:
                flush()
                q = {'no': int(ma.group(1)), 't': 'c', 'ans': re.sub(r'[^A-D]', '', ma.group(2).upper()), '_l': []}
                rest = t[ma.end():].strip()
                if rest: q['_l'].append((x0 + 30, rest))
                continue
            if not me and q and q['t'] == 'e' and 34 <= exp <= 38:
                m4 = re.match(r'^(\d{2})\s*[.．、]\s*', t)
                if m4 and int(m4.group(1)) == exp: me = m4
            if me and 34 <= int(me.group(1)) <= 38:
                flush(); q = {'no': int(me.group(1)), 't': 'e', '_l': []}
                rest = t[me.end():].strip()
                if rest: q['_l'].append((x0 + 30, rest))
                continue
            if q is not None:
                if q['t'] == 'c' and not q['ans'] and re.fullmatch(r'[A-Da-dc]{1,4}', t.strip()):
                    q['ans'] = t.strip().upper(); continue
                q['_l'].append((x0, t))
    flush()
    for k, A in out.items():
        toks = re.findall(r'\d{1,2}|[A-D]{1,4}', ' '.join(A.pop('_grid', [])).replace('c', 'C'))
        g = {}; last = 0; i = 0
        while i < len(toks):
            t = toks[i]
            if t.isdigit(): n = int(t); i += 1
            else: n = last + 1
            if i < len(toks) and not toks[i].isdigit() and 1 <= n <= 33:
                g[n] = toks[i]; last = n; i += 1
        A['_g'] = g
    return out

if __name__ == '__main__':
    T = r'冲刺\s*[8⑧]\s*套卷\s*[（(]([一二三四五六七八])[)）]'
    tests = parse_test('八套卷_试题册', T, lambda m: 'x8-%d' % CN[m.group(1)])
    anss = parse_ans('八套卷_解析册', T + r'.{0,3}答案', lambda m: 'x8-%d' % CN[m.group(1)])
    res = {}
    for k in sorted(tests):
        qs = tests[k]['qs']; A = anss.get(k, {})
        G = A.get('_g', {})
        for q in qs:
            a = A.get(q['no'], {})
            q.update(a)
            if q['t'] != 'e':
                g = G.get(q['no'])
                if g and q.get('ans') and g != q['ans']: q['ansconf'] = [q['ans'], g]
                if not q.get('ans') and g: q['ans'] = g
                if q['t'] == 's' and q.get('ans') and len(q['ans']) != 1: q['ansconf'] = [q['ans'], g]
        res[k] = {'qs': qs}
        print(k, 'qs', len(qs), 'types', ''.join(q['t'] for q in qs), 'ans', sum(1 for q in qs if q.get('ans')), 'grid', len(A.get('_g', {})), 'conf', [(q['no'], q['ansconf']) for q in qs if q.get('ansconf')], 'nojx', [q['no'] for q in qs if q['t'] != 'e' and not q.get('jx')], 'ea', sum(1 for q in qs if q.get('ea')),
              'badopts', [q['no'] for q in qs if q['t'] != 'e' and (len(q.get('opts', [])) != 4 or not all(q['opts']))])
    json.dump(res, open(f'{B}/work/papers_raw.json', 'w'), ensure_ascii=False, indent=1)

# ---------------- 近 3 年真题（一本里依次是 2024 试题 / 答案 / 2025 试题 / 答案 / 2026 试题 / 答案） ----------------
def parse_zt():
    P = load(src('近3年真题试卷'))
    seg = {}; cur = None
    for pg in sorted(P):
        R = page_rows(P, pg)
        head = ' '.join(t for x, y, t in R[:3] if y < 170)
        m = re.search(r'(20\d\d)\s*年全国硕士研究生招生考试', head)
        if m: cur = (m.group(1), 'a' if '参考答案' in head else 'q')
        if cur: seg.setdefault(cur, []).append(pg)
    out = {}
    for (y, kind), pgs in sorted(seg.items()):
        if kind != 'q': continue
        sub = {p: P[p] for p in pgs}
        # 复用肖八的切题逻辑：第一页的大标题当作卷名
        tests = _parse_test_pages(sub)
        qs = tests['qs']
        A = _parse_zt_ans({p: P[p] for p in seg.get((y, 'a'), [])})
        for q in qs:
            a = A.get(q['no'], {}); q.update(a)
        out['zt-' + y] = {'qs': qs}
        print('zt-' + y, 'qs', len(qs), ''.join(q['t'] for q in qs), 'ans', sum(1 for q in qs if q.get('ans')), 'ea', sum(1 for q in qs if q.get('ea')),
              'badopts', [q['no'] for q in qs if q['t'] != 'e' and (len(q.get('opts', [])) != 4 or not all(q['opts']))])
    return out

def _parse_test_pages(P):
    """parse_test 的单卷版：不认卷名，直接从「一、单项选择题」开始"""
    cur = {'qs': []}; q = None; sec = None
    def flush():
        nonlocal q
        if q is None: return
        if q['_o']: q['opts'] = [joinlines(q['_o'].get(L, [])) for L in 'ABCD']
        q['stem'] = joinlines(q['_s']); del q['_s'], q['_o'], q['_last']
        cur['qs'].append(q); q = None
    for pg in sorted(P):
        PR = page_rows(P, pg)
        xs = sorted(x for x, y, t in PR); pmed = xs[len(xs) // 2] if xs else 0
        for x0, y0, t in PR:
            if re.match(r'^一、\s*单项选择', t): sec = 's'; continue
            if re.match(r'^二、\s*多项选择', t): flush(); sec = 'm'; continue
            if re.match(r'^三、\s*材料分析', t): flush(); sec = 'e'; continue
            if sec is None: continue
            mq = QNO.match(t)
            exp = (cur['qs'][-1]['no'] + 1 if cur['qs'] else 1) if q is None else q['no'] + 1
            hit = mq and int(mq.group(1)) == exp
            if not hit and exp == 1 and re.match(r'^1\s*[.．]', t): hit = True; mq = re.match(r'^1\s*[.．]\s*', t)
            lost = (not hit and q is not None and sec != 'e' and q['t'] != 'e' and len(q['_o']) == 4 and x0 < pmed - 10
                    and not OPT.match(t) and q['_last'] == 'D' and exp <= 33)
            if hit or lost:
                flush()
                body_t = t[mq.end():] if hit else re.sub(r'^[^一-鿿“《0-9]+', '', t)
                q = {'no': exp, 't': sec, 'pg': pg + 1, '_s': [(x0 + 30, body_t)], '_o': {}, '_last': 's'}
                continue
            if q is None: continue
            if q['t'] != 'e' and OPT.match(t):
                for L, ot in split_opts(t): q['_o'].setdefault(L, []).append((x0, ot)); q['_last'] = L
                continue
            if q['_last'] == 's': q['_s'].append((x0, t))
            else: q['_o'][q['_last']].append((x0 + 40, t))
    flush()
    return cur

def _parse_zt_ans(P):
    out = {}; txt = []; ess = None; cur = None
    for pg in sorted(P):
        for x0, y0, t in page_rows(P, pg):
            if re.match(r'^三、\s*材料分析', t): ess = True; continue
            if not ess:
                for n, a in re.findall(r'(\d{1,2})\s*[.．,，]\s*([A-Da-d0cC]{1,4})(?![一-鿿])', t):
                    a = a.upper().replace('0', 'D')
                    if 1 <= int(n) <= 33: out[int(n)] = {'ans': a}
                continue
            m = re.match(r'^(3[4-8])\s*[.．、]\s*', t)
            if m: cur = int(m.group(1)); out[cur] = {'_l': [(x0 + 30, t[m.end():])]}; continue
            if cur and not re.search(r'材料分析题参考答案将于', t): out[cur]['_l'].append((x0, t))
    for k, v in out.items():
        if '_l' in v: out[k] = {'ea': joinlines(v.pop('_l'))}
    return out

# ---------------- 讲真题解析分册：按【年份-题号】标签取 2024–2026 的逐题简析与名师点拨 ----------------
def parse_jzt(years=('2024', '2025', '2026')):
    P = load(src('讲真题_解析分册'))
    out = {}; cur = None
    TAG = re.compile(r'答案\s*([A-Da-dc]{1,4})?\s*[【\[［(（]\s*(20\d\d)\s*[-—一–]\s*(\d{1,2})\s*[】\]］)）]')
    def flush():
        nonlocal cur
        if cur and cur['y'] in years:
            txt = joinlines(cur['_l'])
            txt = re.sub(r'^\s*(试题简析|试题筒析|试题简新)\s*', '', txt)
            txt = re.sub(r'\s*(考点定位|老点定位|考点定位》).*$', '', txt, flags=re.S)
            m = re.search(r'\s*名师点拨[》>]?\s*', txt)
            jx, db = (txt[:m.start()], txt[m.end():]) if m else (txt, '')
            out[(cur['y'], cur['no'])] = {'ans': cur['ans'], 'jx': jx.strip(), 'db': db.strip(), 'pg': cur['pg']}
        cur = None
    for pg in sorted(P):
        for x0, y0, t in page_rows(P, pg):
            t = re.sub(r'^[马毛习史思新纲原]\s*(?=\d{1,3}\s*[.．、]?\s*答)', '', t)
            if re.match(r'^第[一二三四五六]部分', t): continue
            m = TAG.search(t)
            if m and re.match(r'^\s*\d{1,3}\s*[.．、]?\s*答', t):
                flush()
                cur = {'y': m.group(2), 'no': int(m.group(3)), 'ans': re.sub(r'[^A-D]', '', (m.group(1) or '').upper().replace('C', 'C')), '_l': [], 'pg': pg + 1}
                rest = t[m.end():].strip()
                if rest: cur['_l'].append((x0 + 30, rest))
                continue
            if cur is None: continue
            if re.match(r'^(第[一二三四五六七八九十]+章|\d{2,3}\s+[A-D]{1,4}\s+\d)', t): flush(); continue
            if re.fullmatch(r'[马毛习史思新纲原]{1,2}', t.strip()): continue
            if re.search(r'公众号|考研小星球|网盘|包邮|无水印|草稿', t): continue
            t = re.sub(r'\d{0,5}\s*考研政治\s*讲真题\s*[，,›•\s]*解析分册', '', t)
            if not t.strip(): continue
            cur['_l'].append((x0, t))
    flush()
    return out

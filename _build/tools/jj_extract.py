"""给书上「只有答案＋出处、一个字解析都没有」的题，按出处（「精讲 P122 考点15」）从精讲精练识别文字里抽考点原文。

  python3 jj_extract.py            抽段落 → 选句 → 写 _build/notes/jj.json（构建脚本读它，挂成题目的「📗 精讲原文」）
  python3 jj_extract.py dump ID…   打印这些题的题面＋考点段落（句子编号），供人工挑句

整段考点原文只存本地 _build/work/jj_blocks.json（不推 GitHub），公开的只有挑出来的几句。
挑句写在 _build/notes/jj_pick.json：{题id: "0,3-5"}（句子编号，可用区间）或 {题id: {"t": "整段手写替换"}}；
没挑过的题用自动选句（按与题干、正确选项的字面重合度），保持原文顺序，删去处用「……」。
识别形近字错写进 _build/notes/jj_ocrfix.json（{错: 对}，对全部摘录生效）。
"""
import json, re, sys, collections
R = '/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/'
OFF = 6            # 文件序号 − 印刷页码
LIMIT = 360        # 摘录上限（字）

OCRFIX = json.load(open(R + '_build/notes/ocr_fix.json', encoding='utf-8'))
OCRFIX.update(json.load(open(R + '_build/notes/ocr_fix_static.json', encoding='utf-8')))
OCRFIX = dict(sorted(OCRFIX.items(), key=lambda kv: -len(kv[0])))
def fix(s):
    for a, b in OCRFIX.items(): s = s.replace(a, b)
    return s

pages = {}
cur = None
for l in open(R + '_build/ocr/精讲精练.txt', encoding='utf-8'):
    if l.startswith('##FILE'):
        cur = int(re.search(r'p_(\d+)', l).group(1)); pages[cur] = []; continue
    p = l.rstrip('\n').split('\t')
    if len(p) == 2: pages[cur].append(p[1].strip())

HEAD = re.compile(r'^[（(J【\[]?\s*考点\s*[（(]?\s*(\d{1,3})')
STOP = re.compile(r'^(经典真[题題]|仿真模拟[题題]|[一二三]、\s*(单项|多项)选择)')
JUNK = re.compile(r'^(\d{1,3}|\d{0,3}\s*2027\s*考研政治知识点精讲精练.*|第[一二三四五六七八九十]+章.*|第[一二三四五]部分.*|.{0,2})$')   # 页眉页脚

def lines_from(idx, start):
    """从 idx 页第 start 行起往后读，跨页续读，最多 3 页。"""
    out = []
    for k in range(idx, idx + 3):
        ls = pages.get(k, [])
        for i, t in enumerate(ls[start if k == idx else 0:]):
            if out and (HEAD.match(t) or STOP.match(t) or re.fullmatch(r'考点\s*(tips)?', t)): return out
            if JUNK.match(t): continue
            out.append(t)
    return out

def find_block(P, N):
    """N 为考点号（int）或 'tips'。识别有时把「考点」和号码拆成两行，这里合回一行。"""
    for idx in [P + OFF, P + OFF - 1, P + OFF + 1, P + OFF + 2, P + OFF - 2]:
        ls = pages.get(idx, [])
        for i, t in enumerate(ls):
            if N == 'tips':
                if re.match(r'^考点\s*tips', t): return ['考点 tips'] + lines_from(idx, i + 1)
                continue
            m = HEAD.match(t)
            if m and int(m.group(1)) == N:
                return lines_from(idx, i)
            if t == '考点' and i + 2 < len(ls) and ls[i + 1] == str(N):
                return [f'考点{N} {ls[i + 2]}'] + lines_from(idx, i + 3)
    return None

TAGS = re.compile(r'\s*[（(]?\s*(高频|重要|重点|重难点|重型|重鹽|重點)?\s*[/◎]*\s*(真[题題期]\s*[\d/ ]*\d)?\s*[)）]?\s*$')
def clean_line(t):
    t = re.sub(r'^(\d{1,2}|[网码昭圖町司]|\d?】|[A-Z])\s+(?=[\u4e00-\u9fff“《（\d])', '· ', t)   # 识别坏掉的圈码
    return t

def join(ls):
    """返回 (考点标题, 正文)。标题行尾的「重要 / 真题 2019」类标签去掉。"""
    if ls[0] == '考点 tips': ls = ls[:1] + [t for t in ls[1:]]
    h = TAGS.sub('', re.sub(r'^[（(J【\[]\s*', '', ls[0])).strip()
    h = re.sub(r'\s*[（(《“”]\s*[真重高].{0,8}$', '', h)
    h = re.sub(r'^考点\s*[（(]?\s*(\d+)\s*', r'考点\1 ', h)
    s = ''
    for t in ls[1:]:
        if re.fullmatch(r'[（(]?\s*(高频|重要|重点)?[/◎\s]*真[题題期路][\d/ ]*[)）]?', t): continue
        t = re.sub(r'[（(《]\s*(重[\u4e00-\u9fff]|真[题題期路]\s*[\d/ ]+|高频)[)）]?\s*$', '', t)
        t = clean_line(TAGS.sub('', t) if len(t) < 30 else t)
        if re.match(r'^([①-⑳]|· |\(?\d{1,2}[.．、)）]|（\d{1,2}）|[一二三四五六七八九十]、)', t) and s: s += '\n'
        s += t
    return h, s

def bg(s):
    s = re.sub(r'[^一-鿿]', '', s); return collections.Counter(s[i:i+2] for i in range(len(s) - 1))

def select(text, q):
    if len(text) <= LIMIT: return text
    ans = set(q['ans'])
    good = bg(''.join(o for L, o in zip('ABCD', q['opts']) if L in ans))
    key = bg(q['stem']) + good + good + bg(''.join(q['opts']))
    sents = [s for s in re.split(r'(?<=[。；！？\n])', text) if s.strip()]
    sc = []
    for i, s in enumerate(sents):
        b = bg(s); n = sum(b.values()) or 1
        v = sum((b & key).values()) / n ** 0.5
        for o in q['opts']:                  # 句子里原样出现某个选项的核心词，强加分
            o = re.sub(r'[^\u4e00-\u9fff]', '', o)
            if len(o) >= 3 and o[:6] in s: v += 6
        sc.append((v, i))
    keep, tot = set(), 0
    for v, i in sorted(sc, reverse=True):
        if tot + len(sents[i]) > LIMIT: continue
        keep.add(i); tot += len(sents[i])
    out, last = '', -1
    for i in sorted(keep):
        if i != last + 1: out += '……'
        out += sents[i]; last = i
    if last != len(sents) - 1: out += '……'
    return out

def parse_src(src):
    src = re.sub(r'\s+', ' ', src or '')
    m = re.search(r'P\s*(\d{1,3})', src)
    n = re.search(r'考点\s*(\d{1,3})', src.replace('2027', ''))
    if not n and 'tips' in src: return (int(m.group(1)) if m else None, 'tips')
    return (int(m.group(1)) if m else None, int(n.group(1)) if n else None)

def split(body):
    return [x for x in re.split(r'(?<=[。；！？\n])', body) if x.strip()]

def pick(sents, spec):
    idx = set()
    for part in str(spec).split(','):
        part = part.strip()
        if not part: continue
        a, _, b = part.partition('-')
        idx.update(range(int(a), int(b or a) + 1))
    out, last = '', -1
    for i in sorted(idx):
        if i != last + 1: out += '……'
        out += sents[i]; last = i
    if last != len(sents) - 1: out += '……'
    return out

def load_qs():
    qs = []
    for p in ['my', 'mz', 'xg', 'sg', 'sx']:
        s = open(R + f'题库/data_{p}.js', encoding='utf-8').read()
        qs += json.loads(re.search(r'=(\{.*\});?\s*$', s, re.S).group(1))['qs']
    return qs

if __name__ == '__main__':
    strip = lambda h: re.sub(r'<[^>]+>', '', h or '').strip()
    qs = load_qs(); by = {q['id']: q for q in qs}
    if len(sys.argv) > 1 and sys.argv[1] == 'dump':
        B = json.load(open(R + '_build/work/jj_blocks.json', encoding='utf-8'))
        for i in sys.argv[2:]:
            q = by[i]; b = B.get(i)
            print(f"### {i} 答{q['ans']} | {q['stem']}")
            for L, o in zip('ABCD', q['opts']): print(f"  {L}.{o}")
            if not b: print('  （无考点段落）', q.get('src')); continue
            print(f"  【{b['p']} {b['h']}】")
            for n, x in enumerate(split(b['body'])): print(f"  [{n}] {x.strip()}")
        sys.exit()
    blocks, miss = {}, []
    for q in qs:
        if q['t'] == 'e' or strip(q.get('jx')) or strip(q.get('db')): continue
        P, N = parse_src(q.get('src'))
        blk = find_block(P, N) if P and N else None
        if not blk: miss.append((q['id'], q.get('src'))); continue
        h, body = join(blk)
        blocks[q['id']] = {'p': f'P{P}', 'h': fix(h), 'body': fix(body)}
    json.dump(blocks, open(R + '_build/work/jj_blocks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    try: PICK = json.load(open(R + '_build/notes/jj_pick.json', encoding='utf-8'))
    except FileNotFoundError: PICK = {}
    try: OF = json.load(open(R + '_build/notes/jj_ocrfix.json', encoding='utf-8'))
    except FileNotFoundError: OF = {}
    res = {}
    for i, b in blocks.items():
        sp = PICK.get(i)
        if sp == '': continue                # 段落与本题不对口：不挂原文
        if isinstance(sp, dict): t = sp['t']
        elif sp is not None: t = pick(split(b['body']), sp)
        else: t = select(b['body'], by[i])
        h = b['h']
        for a, c in OF.items(): t = t.replace(a, c); h = h.replace(a, c)
        t = re.sub(r'拓展与点[拨玻][、，,”“《\s]*', '（拓展）', t)
        t = re.sub(r'^(……)?·\s*', r'\1', t)
        res[i] = {'p': b['p'], 'h': h, 't': t.strip('\n'), 'auto': sp is None}
    for i, sp in PICK.items():               # 书上找不到考点段落、整段手写的
        if i not in res and isinstance(sp, dict): res[i] = {'p': sp.get('p', ''), 'h': sp.get('h', ''), 't': sp['t'], 'auto': False}
    json.dump(res, open(R + '_build/notes/jj.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('抽到', len(res), '人工挑句', sum(1 for v in res.values() if not v['auto']), '缺', len(miss))
    for m in miss: print('  ', m)

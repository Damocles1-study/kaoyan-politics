import fitz, re, json, collections
SRC='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/教材_去水印/1000题_试题分册.pdf'
S='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
PARTS=['my','mz','xg','sg','sx']
d=fitz.open(SRC)
NOISE=[r'^第[一二三四五]部分.{0,40}(单项选择题|多项选择题|材料分析题)\s*$', r'考研政治\s*1000题', r'^.{0,8}(单选|多选|分析)\s*$', r'^\s*\d{1,3}\s*$', r'^第[一二三四五]部分\s*$',
       r'^(马克思主义基本原理|毛泽东思想和中国特色社会主义理论体系概论|习近平新时代中国特色社会主义思想概论|中国近现代史纲要|思想道德与法治)\s*$']
CN='一二三四五六七八九十'
def cnnum(s):
    s=s.replace('十','X')
    if s=='X': return 10
    if s.startswith('X'): return 10+CN.index(s[1])+1
    if s.endswith('X'): return (CN.index(s[0])+1)*10
    if 'X' in s: a,b=s.split('X'); return (CN.index(a)+1)*10+CN.index(b)+1
    return CN.index(s)+1
GAPS=[]
qs=[]; part=-1; typ=None; ch=0; chname='导论'; cur=None; expect=1
def flush():
    global cur
    if cur: qs.append(cur); cur=None
def page_lines(p):
    L=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            t=''.join(s['text'] for s in l['spans']).strip()
            x0,y0,x1,y1=l['bbox']
            if not t or x0>545: continue
            if l['dir'][1]!=0: continue
            L.append(((y0+y1)/2,x0,t))
    L.sort()
    rows=[]
    for ym,x0,t in L:
        if rows and abs(ym-rows[-1][0])<6: rows[-1][1].append((x0,t))
        else: rows.append([ym,[(x0,t)]])
    out=[]
    for ym,items in rows:
        for x0,t in sorted(items): out.append(t)
    return out
for pi in range(5,d.page_count):
    for line in page_lines(d[pi]):
        l=line.strip()
        if not l: continue
        if any(re.search(n,l) for n in NOISE): continue
        m=re.match(r'^([一二三])、\s*(单项选择题|多项选择题|材料分析题)',l)
        if m:
            flush(); typ={'单项选择题':'single','多项选择题':'multi','材料分析题':'essay'}[m.group(2)]
            if typ=='single': part+=1
            ch=0; chname='导论'; expect=1; continue
        m=re.match(r'^(导论)\s*(.*)$',l) if len(l)<40 else None
        if m and (cur is None or cur.get('opts') is not None and len(cur['opts'])>=4 or typ=='essay' and cur is None):
            flush(); ch=0; chname=('导论 '+m.group(2)).strip(); continue
        m=re.match(r'^第([一二三四五六七八九十]+)章\s*(.*)$',l)
        if m and len(l)<50:
            flush(); ch=cnnum(m.group(1)); chname=m.group(2).strip(); continue
        m=re.match(r'^(\d{1,3})\s*([.．、,，]?)\s*(\D.*)$',l)
        complete = cur is None or (typ!='essay' and len(cur['opts'])>=4) or typ=='essay'
        ok=False
        if m and complete:
            n=int(m.group(1)); sep=m.group(2)
            if n==expect and (sep or typ!='essay'): ok=True
            elif sep and n==expect+1: ok=True; GAPS.append((PARTS[part],typ,expect)); expect=n
        if ok:
            m=re.match(r'^(\d{1,3})\s*[.．、,，]?\s*(.*)$',l)
            flush(); cur={'part':PARTS[part],'type':typ,'ch':ch,'chname':chname,'no':expect,'stem':m.group(2),'opts':[] if typ!='essay' else None,'page':pi-4}
            expect+=1; continue
        if cur is None: continue
        if typ!='essay':
            # split possible multiple options in one line
            want='ABCD'[len(cur['opts'])] if len(cur['opts'])<4 else None
            if want and re.match(rf'^{want}\s*[.．,，、]',l):
                pieces=[]; rest=l
                while True:
                    want='ABCD'[len(cur['opts'])+len(pieces)] if len(cur['opts'])+len(pieces)<4 else None
                    m2=re.match(rf'^{want}\s*[.．,，、]\s*',rest) if want else None
                    if not m2: break
                    rest=rest[m2.end():]
                    nxt='ABCD'[len(cur['opts'])+len(pieces)+1] if len(cur['opts'])+len(pieces)<3 else None
                    m3=re.search(rf'{nxt}\s*[.．,，]',rest) if nxt else None
                    if m3: pieces.append(rest[:m3.start()].strip()); rest=rest[m3.start():]
                    else: pieces.append(rest.strip()); rest=''; break
                cur['opts']+=pieces; continue
            if cur['opts']: cur['opts'][-1]+=l
            else: cur['stem']+=('\n' if re.match(r'^[①②③④⑤⑥]',l) else '')+l
        else:
            cur['stem']+='\n'+l
flush()
print('GAPS',GAPS)
json.dump(qs,open(S+'/work/questions.json','w'),ensure_ascii=False,indent=0)
c=collections.Counter((q['part'],q['type']) for q in qs)
for k in sorted(c,key=lambda k:(PARTS.index(k[0]),k[1])): print(k,c[k])
bad=[q for q in qs if q['type']!='essay' and len(q['opts'])!=4]
print('bad opts',len(bad)); [print(q['part'],q['type'],q['no'],q['opts'][:4],q['stem'][-60:]) for q in bad[:15]]
cc=collections.Counter((q['part'],q['type'],q['ch']) for q in qs)
print(sorted(cc.items(),key=lambda x:(PARTS.index(x[0][0]),x[0][1],x[0][2])))

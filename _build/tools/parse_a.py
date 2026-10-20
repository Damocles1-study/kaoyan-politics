import re, json, collections, sys
sys.path.insert(0,'/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/tools')
import ocrlines
S='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
P=ocrlines.load(S+'/ocr/1000题_解析分册.txt')
PARTS=['my','mz','xg','sg','sx']
CN='一二三四五六七八九十'
def cnnum(s):
    if s=='十': return 10
    if s.startswith('十'): return 10+CN.index(s[1])+1
    if s.endswith('十'): return (CN.index(s[0])+1)*10
    if '十' in s: a,b=s.split('十'); return (CN.index(a)+1)*10+CN.index(b)+1
    return CN.index(s)+1
def noise(z):
    t=z[4]
    if z[1]<50 and ('1000' in t or '部分' in t or '解析分册' in t or '选择题' in t or '分析题' in t): return True
    if z[1]>935 and re.fullmatch(r'[\d\s•.]{1,4}',t): return True
    if re.fullmatch(r'.{0,8}[·•，,.\-]?\s*(单选|多选|分析)',t): return True
    if re.fullmatch(r'第[一二三四五]部分',t): return True
    if re.fullmatch(r'(马克思主义基本原理|毛泽东思想和中国特色社会主义理论体系概论|习近平新时代中国特色社会主义思想概论|中国近现代史纲要|思想道德与法治)[•·]?',t): return True
    if '题目考查知识点' in t or '页码＋考点' in t or '页码+考点' in t: return True
    return False
ANS=re.compile(r'^(\d{1,3}|[TIlOS]\d{0,2})\s*[.．、,，]?\s*答\s*[\u4e00-\u9fff]\s*[：:]?\s*([A-DАВСＡＢＣＤ\s、,]{1,9})\s*(.*)$')
NORM=str.maketrans({'А':'A','В':'B','С':'C','Ａ':'A','Ｂ':'B','Ｃ':'C','Ｄ':'D'})
TAGS={}
items=[]; part=-1; typ=None; ch=0; cur=None; field=None; expect=1; LOG=[]
def flush():
    global cur
    if cur: items.append(cur); cur=None
for pi in sorted(P):
    if pi<5: continue
    L=[z for z in ocrlines.two_col(P[pi]) if not noise(z)]
    for z in L:
        t=z[4].strip()
        t=re.sub(r'^(\d?)[Oo](?=\s*[.．]?\s*答)',lambda m:m.group(1)+'0',t)
        t=re.sub(r'^(\d)[Oo](\d)',r'\g<1>0\2',t)
        m=re.match(r'^([一二三])、\s*(单项选择题|多项选择题|材料分析题)',t)
        if m:
            flush(); typ={'单项选择题':'s','多项选择题':'m','材料分析题':'e'}[m.group(2)]
            if typ=='s': part+=1
            ch=0; expect=1; field=None; continue
        if typ is None: continue
        if re.fullmatch(r'导\s*论',t): flush(); ch=0; continue
        m=re.fullmatch(r'第([一二三四五六七八九十]+)章',t)
        if m: flush(); ch=cnnum(m.group(1)); continue
        if re.fullmatch(r'(时政储备题|考点拓展题)',t):
            ym=(z[1]+z[3])/2
            for zz in L:
                if abs((zz[1]+zz[3])/2-ym)<12 and zz[0]<z[0] and ANS.match(zz[4].strip()): TAGS[(pi,zz[0],zz[1])]=t
            continue
        if typ!='e':
            m=ANS.match(t)
            if m:
                flush()
                n=m.group(1); n=int(n) if n.isdigit() else -1
                if n!=expect: LOG.append((PARTS[part],typ,expect,n,pi))
                if expect-3<=n<=expect+6 and n>0: expect=n
                a=''.join(sorted(set(c for c in m.group(2).translate(NORM) if c in 'ABCD')))
                rest=m.group(3).strip()
                cur={'part':PARTS[part],'t':typ,'ch':ch,'no':expect,'ans':a,'src':'','jx':'','db':'','tag':'','pdfp':pi}
                cur['_k']=(pi,z[0],z[1])
                if '时政储备' in rest: cur['tag']='时政储备题'
                if '考点拓展' in rest: cur['tag']='考点拓展题'
                expect+=1; field=None; continue
        else:
            m=re.match(r'^(\d{1,2})\s*[.．、]\s*(.*)$',t)
            if m and int(m.group(1))==expect and z[0]<(560 if z[0]>=505 else 130):
                flush(); cur={'part':PARTS[part],'t':'e','ch':ch,'no':expect,'ea':m.group(2),'src':'','jx':'','db':'','tag':'','ans':None,'pdfp':pi}
                expect+=1; field='ea'; continue
        if cur is None: continue
        m=re.match(r'^(出处|简析|点拨|解析|提示)\s*(.*)$',t)
        if m:
            field={'出处':'src','简析':'jx','解析':'jx','点拨':'db','提示':'db'}[m.group(1)]
            cur[field]+=('\n' if cur[field] else '')+m.group(2); continue
        if field is None: field='jx'
        # paragraph break heuristic: line indented ~2 chars more than column base
        base = 545 if z[0]>=505 else 135
        sep='\n' if z[0]>base+25 else ''
        cur[field]+=sep+t
flush()
for q in items:
    k=q.pop('_k',None)
    if k in TAGS: q['tag']=TAGS[k]
json.dump(items,open(S+'/work/answers.json','w'),ensure_ascii=False,indent=0)
c=collections.Counter((q['part'],q['t']) for q in items)
for k in sorted(c,key=lambda k:(PARTS.index(k[0]),k[1])): print(k,c[k])
print('numlog',len(LOG),LOG[:40])
print('noans',[ (q['part'],q['t'],q['no']) for q in items if q['t']!='e' and not q['ans']][:20])

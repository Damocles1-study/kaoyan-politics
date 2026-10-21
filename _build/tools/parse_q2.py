import re, json, collections, sys
sys.path.insert(0,'/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/tools')
import ocrlines
S='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
P=ocrlines.load(S+'/ocr/1000题_试题分册_dual.txt')
PARTS=['my','mz','xg','sg','sx']
CN='一二三四五六七八九十'
def cnnum(s):
    if s=='十': return 10
    if s.startswith('十'): return 10+CN.index(s[1])+1
    if s.endswith('十'): return (CN.index(s[0])+1)*10
    if '十' in s: a,b=s.split('十'); return (CN.index(a)+1)*10+CN.index(b)+1
    return CN.index(s)+1
def noise(t,z):
    if z[1]<45 and ('1000' in t or '部分' in t or '试题分册' in t): return True
    if z[1]>930 and re.fullmatch(r'\d{1,3}',t): return True
    if (z[1]<60 or z[1]>925) and re.fullmatch(r'[\d\s:：.>›»》]{1,8}',t): return True
    if '考研政治' in t and '1000' in t: return True
    if z[0]>930: return True  # 侧边页签
    if re.fullmatch(r'.{0,8}[·•，,.\-]?(单选|多选|分析)',t): return True
    if re.fullmatch(r'(马克思主义基本原理|毛泽东思想和中国特色社会主义理论体系概论|习近平新时代中国特色社会主义思想概论|中国近现代史纲要|思想道德与法治)',t): return True
    return False
def bookp(i):
    return i-4 if i<=63 else i+1 if i<=111 else i+5 if i<=148 else i+8
qs=[]; part=-1; typ=None; ch=0; chname=''; cur=None; expect=1; LOG=[]
def flush():
    global cur
    if cur: qs.append(cur); cur=None
OPT=re.compile(r'([A-D])\s*[.．,，、·]\s*')
def add_opts(text):
    # text starts with expected letter; may hold several options
    while True:
        k=len(cur['opts'])
        if k>=4: return text
        m=re.match(rf'^{"ABCD"[k]}(?:\s*[.．,，、·]\s*|\s*(?=[\u4e00-\u9fff“《①]))',text)
        if not m: return text
        text=text[m.end():]
        if k<3:
            m2=re.search(rf'\s{"ABCD"[k+1]}\s*[.．,，、·]|(?<=[^A-Za-z]){"ABCD"[k+1]}\s*[.．,，、]|\s{"ABCD"[k+1]}(?=[\u4e00-\u9fff“《①])',text)
            if m2:
                cur['opts'].append(text[:m2.start()].strip()); text=text[m2.start():].strip(); continue
        cur['opts'].append(text.strip()); return ''
for pi in sorted(P):
    if pi<5: continue
    L0=[z for z in ocrlines.rows(P[pi]) if not noise(z[4],z)]
    L=[]
    for z in L0:
        if L and re.fullmatch(r'\W*\d{1,3}\W*',L[-1][4]) and abs((L[-1][1]+L[-1][3])/2-(z[1]+z[3])/2)<10 and z[0]>L[-1][0]:
            p=L.pop(); num=re.search(r'\d{1,3}',p[4]).group(0)
            z=(p[0],min(p[1],z[1]),z[2],max(p[3],z[3]),num+'.'+re.sub(r'^[•·\s]+','',z[4]))
        L.append(z)
    if not L: continue
    minx=min(z[0] for z in L)
    ox=sorted(z[0] for z in L if re.match(r'^[AC]\s*[.．,，、·]',z[4]))
    optx=ox[len(ox)//2] if ox else None
    for zi,z in enumerate(L):
        t=z[4]
        nx=L[zi+1][0] if zi+1<len(L) else None
        m=re.match(r'^([一二三])、\s*(单项选择题|多项选择题|材料分析题)',t)
        if m:
            flush(); typ={'单项选择题':'s','多项选择题':'m','材料分析题':'e'}[m.group(2)]
            if typ=='s' and expect>1: part+=1
            ch=0; chname='导论'; expect=1; continue
        mp=re.match(r'^第([一二三四五])部分\W*$',t)
        if mp and z[1]>70:
            flush(); part=CN.index(mp.group(1)); typ='s'; ch=0; chname='导论'; expect=1; continue
        if typ is None: continue
        m=re.match(r'^导\s*论\s*(.*)$',t)
        if m and len(t)<40 and z[0]<minx+40:
            flush(); ch=0; chname='导论'; continue
        m=re.match(r'^第([一二三四五六七八九十]+)章\s*(.*)$',t)
        if m and len(t)<60 and z[0]<minx+40:
            flush(); ch=cnnum(m.group(1)); chname=m.group(2).strip(); continue
        m=re.match(r'^(\d{1,3})\s*([.．、,，]?)\s*(.*)$',t)
        if not m and typ!='e' and ((nx is not None and 25<=nx-z[0]<120) or (optx is not None and z[0]<optx-22)):
            m=re.match(r'^([0-9TIlOoSsg]{1,3})\s*([.．、,，])\s*(.*)$',t)
            if m and not re.search(r'\d',m.group(1)[-1:]+'0'): m=None
        if m and not m.group(1).isdigit(): m=type('MM',(),{'group':lambda self,i,_m=m:_m.group(i) if i!=1 else '0'})()
        if m: m=type('M',(),{'group':lambda self,i,_m=m:{1:_m.group(1),2:_m.group(3),3:_m.group(2)}[i]})()
        complete = cur is None or typ=='e' or len(cur['opts'])>=4
        okq=False
        if m and complete and m.group(2) and (m.group(3) or not re.match(r'^[\d年月日万亿多余个%]',m.group(2))):
            n=int(m.group(1))
            if typ!='e' and ((nx is not None and nx-z[0]>=25 and nx-z[0]<120) or (optx is not None and z[0]<optx-22)): okq=True
            elif n==expect or (n==expect+1 and re.match(r'^\d{1,3}\s*[.．、]',t)): okq=True
        if okq:
            if n!=expect: LOG.append((PARTS[part],typ,expect,n,t[:20]))
            if typ=='e' and n!=expect: pass
            flush(); cur={'part':PARTS[part],'t':typ,'ch':ch,'chname':chname,'no':expect,'ocrn':n,'stem':m.group(2),'opts':[] if typ!='e' else None,'page':bookp(pi)}
            expect+=1; continue
        if cur is None: continue
        if typ!='e':
            k=len(cur['opts'])
            if k<4 and re.match(rf'^{"ABCD"[k]}\s+(?=[\u4e00-\u9fff①②③④“《（(])',t):
                t=t[0]+'.'+t[1:].lstrip()
            if k<4 and re.match(rf'^{"ABCD"[k]}\s*[.．,，、·]',t):
                rest=add_opts(t)
                if rest: cur['opts'][-1]+=rest
                continue
            if cur['opts']: cur['opts'][-1]+=t
            else: cur['stem']+=('\n' if re.match(r'^[①②③④⑤⑥]',t) else '')+t
        else:
            brk = re.match(r'^(材料\s*\d|[（(]\s*\d\s*[)）]|\d\s*[)）]|结合材料)',t) or z[0]<minx+40
            cur['stem']+=('\n' if brk else '')+t
flush()
json.dump(qs,open(S+'/work/questions2.json','w'),ensure_ascii=False,indent=0)
c=collections.Counter((q['part'],q['t']) for q in qs)
for k in sorted(c,key=lambda k:(PARTS.index(k[0]),k[1])): print(k,c[k])
bad=[q for q in qs if q['t']!='e' and len(q['opts'])!=4]
print('bad opts',len(bad)); [print(q['part'],q['t'],q['no'],q['page'],q['opts'],q['stem'][-50:]) for q in bad[:20]]
def align(L,N):
    k=len(L); NEG=-10**9
    # dp[i][a]: best score assigning q_i number a (1..N)
    dp=[[NEG]*(N+2) for _ in range(k)]; bk=[[0]*(N+2) for _ in range(k)]
    for i in range(k):
        best=NEG; barg=0
        for a in range(1,N+1):
            if i==0: prevbest,parg=(0,0) if a>=1 else (NEG,0)
            else:
                # best over b<a, with consecutive bonus
                prevbest,parg=best,barg
                if dp[i-1][a-1]>NEG and dp[i-1][a-1]+0.3>prevbest: prevbest,parg=dp[i-1][a-1]+0.3,a-1
            if i>0 and a-1>=1 and dp[i-1][a-1]>best: best,barg=dp[i-1][a-1],a-1
            if i>0 and a==1: prevbest=NEG
            if prevbest==NEG: continue
            # remaining must fit
            if N-a < k-1-i: continue
            dp[i][a]=prevbest+(1 if L[i]['ocrn']==a else 0); bk[i][a]=parg
    a=max(range(1,N+1),key=lambda x:dp[k-1][x]); res=[0]*k
    for i in range(k-1,-1,-1): res[i]=a; a=bk[i][a]
    return res
TOT={('my','s'):184,('my','m'):212,('mz','s'):56,('mz','m'):59,('xg','s'):93,('xg','m'):127,('sg','s'):129,('sg','m'):122,('sx','s'):66,('sx','m'):100}
for k,N in TOT.items():
    L=[q for q in qs if (q['part'],q['t'])==k]
    for q,a in zip(L,align(L,N)): q['no']=a
json.dump(qs,open(S+'/work/questions2.json','w'),ensure_ascii=False,indent=0)
seen=collections.defaultdict(list)
for q in qs: seen[(q['part'],q['t'])].append(q['no'])
for k,v in TOT.items():
    have=seen[k]; print(k,'missing',sorted(set(range(1,v+1))-set(have)),'dups',[n for n,c in collections.Counter(have).items() if c>1],'extra',[n for n in have if n>v])

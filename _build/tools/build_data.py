import json, re, collections
S='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build'
OUT='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/题库/'
Q=json.load(open(S+'/work/questions2.json')); A=json.load(open(S+'/work/answers.json'))
amap={(a['part'],a['t'],a['no']):a for a in A}
FIX=json.load(open('/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/notes/manual_fix.json'))
MY={}
import glob
for _f in sorted(glob.glob('/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/notes/my_*.json')):
    MY.update(json.load(open(_f,encoding='utf-8')))   # my_notes.json(马原导论+ch1) + my_ch2.json … 每章一份
META={'my':('马克思主义基本原理','马原'),'mz':('毛泽东思想和中国特色社会主义理论体系概论','毛中特'),
      'xg':('习近平新时代中国特色社会主义思想概论','习概'),'sg':('中国近现代史纲要','史纲'),'sx':('思想道德与法治','思法')}
def fix(s):
    if not s: return s
    s=re.sub(r'(?<![自感错直知视听发察警睡幻味嗅触先后不])觉(?=的|中央|员|组织|和国家|内|章|风|委|史|纪|对|最|政|代会|旗|性|和人民|领导|建|校|课)',r'党',s)
    for a,b in [('我困','我国'),('中困','中国'),('困家','国家'),('困情','国情'),('困际','国际'),('家图情','家国情'),('中图式','中国式'),
                ('图家','国家'),('祖图','祖国'),('图际','国际'),('图情','国情'),('发杨','发扬'),('昂杨','昂扬'),('弘杨','弘扬'),('宣杨','宣扬'),
                ('入们','人们'),('⋯•','……'),('•…','……'),('⋯','…')]:
        s=s.replace(a,b)
    s=re.sub(r'中图(?=共产党|特色|人民|梦|化|近现代|革命|社会|的|式|古代|传统)','中国',s)
    return s
def LECT_ALL():
    # 讲义登记表：科目 → {章号: 讲义路径}。新写一章就在这里加一行
    return {'my':{0:'讲义/马原_导论与第1章.html',1:'讲义/马原_导论与第1章.html',2:'讲义/马原_第2章.html'}}
def tail(s):
    s=re.sub(r'\s*\d{0,3}2027\s*(考研政治\s*1000\s*题\W*)?[:：]?\s*$','',s)
    s=re.sub(r'小2027$','',s)
    return s
def clean_field(s,lead):
    s=(s or '').strip()
    s=re.sub(r'^[）)\]】|:：\s]+','',s)
    s=re.sub(r'(P\s*\d+)\s*[）)\]】|]','\\1 ',s)
    if lead: s=re.sub(r'^参考答[一-鿿][）)]?\s*','',s)
    return fix(s.strip())
CH={'my':['导论','世界的物质性及发展规律','实践与认识及其发展规律','人类社会及其发展规律','资本主义的本质及规律','资本主义的发展及其趋势','社会主义的发展及其规律','共产主义崇高理想及其最终实现'],
 'mz':['导论 马克思主义中国化时代化的历史进程与理论成果','毛泽东思想及其历史地位','新民主主义革命理论','社会主义改造理论','社会主义建设道路初步探索的理论成果','中国特色社会主义理论体系的形成发展','邓小平理论','“三个代表”重要思想','科学发展观'],
 'xg':['导论','新时代坚持和发展中国特色社会主义','以中国式现代化全面推进中华民族伟大复兴','坚持党的全面领导','坚持以人民为中心','全面深化改革开放','推动高质量发展','社会主义现代化建设的教育、科技、人才战略','发展全过程人民民主','全面依法治国','建设社会主义文化强国','以保障和改善民生为重点加强社会建设','建设社会主义生态文明','维护和塑造国家安全','建设巩固国防和强大人民军队','坚持“一国两制”和推进祖国完全统一','中国特色大国外交和推动构建人类命运共同体','全面从严治党'],
 'sg':['导论','进入近代后中华民族的磨难与抗争','不同社会力量对国家出路的早期探索','辛亥革命与君主专制制度的终结','中国共产党成立和中国革命新局面','中国革命的新道路','中华民族的抗日战争','为建立新中国而奋斗','中华人民共和国的成立与中国社会主义建设道路的探索','改革开放与中国特色社会主义的开创和发展','中国特色社会主义进入新时代'],
 'sx':['导论 担当复兴大任 成就时代新人','领悟人生真谛 把握人生方向','追求远大理想 坚定崇高信念','继承优良传统 弘扬中国精神','明确价值要求 践行价值准则','遵守道德规范 锤炼道德品格','学习法治思想 提升法治素养']}
# insert manual-only questions
have={f"{q['part']}-{q['t']}-{q['no']}" for q in Q}
for qid in FIX:
    if qid not in have:
        p,t,n=qid.split('-'); Q.append({'part':p,'t':t,'ch':4,'chname':'','no':int(n),'stem':'','opts':[],'page':18})
Q.sort(key=lambda q:(['my','mz','xg','sg','sx'].index(q['part']),q['t'],q['no']))
for q in Q:
    a=amap.get((q['part'],q['t'],q['no']))
    if q['t']!='e' and a: q['ch']=max(q['ch'],a['ch'])
chnames=collections.defaultdict(dict)
for q in Q:
    if q['t']!='e' and q['chname']: chnames[q['part']].setdefault(q['ch'],q['chname'])
# 解析 chapter vs 试题 chapter agreement
dis=[(q['part'],q['t'],q['no'],q['ch'],amap[(q['part'],q['t'],q['no'])]['ch']) for q in Q if q['t']!='e' and (q['part'],q['t'],q['no']) in amap and amap[(q['part'],q['t'],q['no'])]['ch']!=q['ch']]
print('chapter disagreements',len(dis),dis[:12])
data=collections.defaultdict(list)
for q in Q:
    if q['t']=='e': continue
    k=(q['part'],q['t'],q['no']); a=amap.get(k)
    qid=f"{q['part']}-{q['t']}-{q['no']}"
    stem,opts=q['stem'],q['opts']
    if qid in FIX: stem,opts=FIX[qid]['stem'],FIX[qid]['opts']
    item={'id':qid,'t':q['t'],'ch':q['ch'],'no':q['no'],'page':q['page'],'stem':tail(fix(stem.strip())),'opts':[tail(fix(o.strip())) for o in opts],
          'ans':a['ans'] if a else '', 'src':clean_field(a['src'],0) if a else '','jx':clean_field(a['jx'],0) if a else '',
          'db':clean_field(a['db'],0) if a else '','tag':a['tag'] if a else ''}
    if qid in MY: item['my']=MY[qid]
    data[q['part']].append(item)
qe={(q['part'],q['no']):q for q in Q if q['t']=='e'}
MISSING={'my':'P60–64','xg':'P113–116','sg':'P154–156','sx':'P177 之后'}
for a in A:
    if a['t']!='e': continue
    q=qe.get((a['part'],a['no']))
    qid=f"{a['part']}-e-{a['no']}"
    stem=fix(q['stem'].strip()) if q else ''
    has_q=bool(q) and bool(re.search(r'[（(]\s*1\s*[)）]',stem))
    if not has_q:
        stem=(stem+'\n\n' if stem else '')+f"⚠️ 这份 1000 题 PDF 缺了本题后半部分（{MISSING.get(a['part'],'')}），材料和设问请对照纸质书；参考答案是完整的，从答案的 (1)(2) 能反推出设问。"
    item={'id':qid,'t':'e','ch':99,'no':a['no'],'page':q['page'] if q else 0,'stem':stem,'opts':None,'ans':None,'ea':clean_field(a['ea'],1),
          'src':'','jx':clean_field(a['jx'],0),'db':clean_field(a['db'],0),'tag':a['tag']}
    if qid in MY: item['my']=MY[qid]
    data[a['part']].append(item)
# ---- 讲义 ↔ 题目：解析每份讲义每节的 qlink，把「本题知识点」登记回题目 ----
import os, html as _h
ROOT='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/'
LK={}
for lf in sorted(set(v for d in LECT_ALL().values() for v in d.values())):
    src=open(ROOT+lf,encoding='utf-8').read()
    for sm in re.finditer(r'<section class="card" id="(d\d+)">(.*?)</section>',src,re.S):
        sid,body=sm.group(1),sm.group(2)
        h2=re.search(r'<h2>(.*?)</h2>',body,re.S)
        title=_h.unescape(re.sub(r'<[^>]+>','',h2.group(1))).strip() if h2 else sid
        for a in re.finditer(r'<a class="qlink" href="\.\./题库/刷题\.html\?p=(\w+)&(?:amp;)?t=([sme])&(?:amp;)?ch=(\d+)[^"]*">([^<]*)</a>',body):
            pp,tt,ch,label=a.group(1),a.group(2),int(a.group(3)),a.group(4)
            if re.search(r'\d+\s*题\s*$',label) or not re.search(r'\d',label):
                nos=[x['no'] for x in data[pp] if x['t']==tt and x['ch']==ch]
            else:
                nos=[]
                for r in re.finditer(r'(\d+)\s*[–\-~～]\s*(\d+)|(\d+)',label):
                    if r.group(3): nos.append(int(r.group(3)))
                    else: nos+=list(range(int(r.group(1)),int(r.group(2))+1))
            for n in nos: LK.setdefault(f'{pp}-{tt}-{n}',f'{lf}#{sid}|{title}')
nlk=0
for p in data:
    for x in data[p]:
        if x['id'] in LK: x['lk']=LK[x['id']]; nlk+=1
print('knowledge links',nlk)
tot=0
for p,(name,short) in META.items():
    chs={k:(f"第{k}章 {v}" if k else v) for k,v in enumerate(CH[p])}
    chs[99]='材料分析题'
    used=sorted(set(x['ch'] for x in data[p]))
    for u in used:
        if u not in chs: chs[u]=f'第{u}章'
    chs={k:chs[k] for k in sorted(chs) if k in used}
    obj={'key':p,'name':name,'short':short,'chapters':chs,'qs':data[p]}
    js='window.POL=window.POL||{};\nPOL.'+p+'='+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n'
    open(OUT+f'data_{p}.js','w',encoding='utf-8').write(js)
    c=collections.Counter(x['t'] for x in data[p]); tot+=len(data[p])
    print(p,short,dict(c),'chapters',list(chs.values()))
    noans=[x['id'] for x in data[p] if x['t']!='e' and not x['ans']]
    if noans: print('  NOANS',noans)
print('total',tot)

# ---- meta.js：首页用的轻量目录（章名、各题型题号区间、讲义登记、秒杀笔记数）----
LECT=LECT_ALL()
def ranges(nums):
    nums=sorted(nums); out=[]
    for n in nums:
        if out and n==out[-1][1]+1: out[-1][1]=n
        else: out.append([n,n])
    return out
meta={}
for p,(name,short) in META.items():
    chs={}
    for x in data[p]:
        c=chs.setdefault(x['ch'],{'s':[],'m':[],'e':[],'my':0})
        c[x['t']].append(x['no']); c['my']+=1 if x.get('my') else 0
    chnames={k:(f"第{k}章 {v}" if k else v) for k,v in enumerate(CH[p])}; chnames[99]='材料分析题'
    meta[p]={'name':name,'short':short,'ch':[{'ch':k,'name':chnames.get(k,''),'s':ranges(v['s']),'m':ranges(v['m']),'e':ranges(v['e']),
             'ns':len(v['s']),'nm':len(v['m']),'ne':len(v['e']),'my':v['my'],'lect':LECT.get(p,{}).get(k,'')} for k,v in sorted(chs.items())]}
open(OUT+'meta.js','w',encoding='utf-8').write('window.POLMETA='+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+';\n')
print('meta.js',len(json.dumps(meta,ensure_ascii=False)))

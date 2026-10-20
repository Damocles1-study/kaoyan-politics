import re
def load(path):
    pages={}; cur=None
    for l in open(path,encoding='utf-8'):
        l=l.rstrip('\n')
        if l.startswith('##FILE'):
            cur=int(re.search(r'p_(\d+)\.png',l).group(1)); pages[cur]=[]; continue
        if cur is None or '\t' not in l: continue
        a,t=l.split('\t',1)
        try: x0,y0,x1,y1=map(int,a.split())
        except: continue
        pages[cur].append((x0,y0,x1,y1,t.strip()))
    return pages
def rows(lines,tol=7):
    L=sorted(lines,key=lambda z:((z[1]+z[3])/2,z[0]))
    out=[]
    for z in L:
        ym=(z[1]+z[3])/2
        if out and abs(ym-out[-1][0])<tol: out[-1][1].append(z)
        else: out.append([ym,[z]])
    res=[]
    for ym,zs in out:
        res+=sorted(zs,key=lambda z:z[0])
    return res
def two_col(lines,mid=440):
    full=[z for z in lines if (z[0]<250 and z[2]>600) or re.match(r'^([一二三]、\s*(单项|多项|材料)|第[一二三四五]部分)',z[4])]
    cuts=sorted(set([0]+[ (z[1]+z[3])//2 for z in full]+[1001]))
    res=[]
    for a,b in zip(cuts,cuts[1:]):
        band=[z for z in lines if a<=(z[1]+z[3])/2<b and z not in full]
        hdr=[z for z in full if (z[1]+z[3])//2==a]
        res+=hdr
        res+=sorted([z for z in band if z[0]<mid],key=lambda z:(z[1],z[0]))
        res+=sorted([z for z in band if z[0]>=mid],key=lambda z:(z[1],z[0]))
    return res

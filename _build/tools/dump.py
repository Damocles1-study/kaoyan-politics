# 用法：python3 dump.py my 2   → 紧凑打印某科某章全部选择题（写讲义 / 秒杀笔记前通读用）
import json,sys
p,ch=sys.argv[1],int(sys.argv[2])
s=open(f'/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/题库/data_{p}.js').read()
for x in json.loads(s.split('=',2)[2].rstrip().rstrip(';'))['qs']:
    if x['ch']!=ch or x['t']=='e': continue
    stem=x['stem'].replace('\n',' ')
    stem=stem if len(stem)<=150 else '…'+stem[-140:]
    print(f"[{x['id']}] {stem} | "+' / '.join(f"{'ABCD'[i]}.{x['opts'][i][:40]}" for i in range(4))+f" || {x['ans']} || {(x['jx'] or x['db'])[:120]}")

"""把一份补丁 JSON 合并进 notes：
  {"pick": {题id: 挑句}, "ocrfix": {错: 对}, "my": {"file": "my_xg.json", "notes": {题id: 秒杀}}}
用法：python3 merge_notes.py 补丁.json
（中文直接写在 heredoc 里会撞编码问题，所以补丁一律先落成文件。）"""
import json, sys
N = '/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/_build/notes/'

def merge(fn, upd):
    try: d = json.load(open(N + fn, encoding='utf-8'))
    except FileNotFoundError: d = {}
    d.update(upd)
    json.dump(d, open(N + fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return len(d)

p = json.load(open(sys.argv[1], encoding='utf-8'))
if 'pick' in p: print('jj_pick', merge('jj_pick.json', p['pick']))
if 'ocrfix' in p: print('jj_ocrfix', merge('jj_ocrfix.json', p['ocrfix']))
if 'my' in p: print(p['my']['file'], merge(p['my']['file'], p['my']['notes']))

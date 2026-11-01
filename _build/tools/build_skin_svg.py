#!/usr/bin/env python3
"""主题用的小矢量：笔记页眉的铅笔涂鸦、慕夏厅的花格墙纸和四角卷草。生成到 assets/skin/，由 skin.css 引用。
用法：python3 _build/tools/build_skin_svg.py"""
import os, random
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'skin')
os.makedirs(OUT, exist_ok=True)
random.seed(1219)
def j(v, a=.7): return round(v + random.uniform(-a, a), 1)
def wob(points, a=.7):
    """折线抖一抖再用二次曲线连起来，像手画的"""
    pts = [(j(x, a), j(y, a)) for x, y in points]
    d = f'M{pts[0][0]} {pts[0][1]}'
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i+1][0]) / 2, (pts[i][1] + pts[i+1][1]) / 2
        d += f'Q{pts[i][0]} {pts[i][1]} {round(mx,1)} {round(my,1)}'
    return d + f'L{pts[-1][0]} {pts[-1][1]}'
def path(d, w=1.7): return f'<path d="{d}" fill="none" stroke="#000" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'

# 页眉涂鸦：星星、弯箭头、对勾、几道小闪光
star = 'M18 6L21.5 17L33 17.5L24 24.5L27.5 36L18 29L8.5 36L12 24.5L3 17.5L14.5 17Z'
arrow = wob([(48, 36), (55, 16), (70, 13), (83, 24)]) + wob([(75, 25), (84, 25), (82, 15)], .4)
tick = wob([(92, 28), (98, 37), (112, 13)], .4)
sparks = ''.join(path(f'M{x} {y}l{dx} {dy}', 1.4) for x, y, dx, dy in [(38, 7, 3, -4), (42, 13, 5, -1), (37, 2, 1, -2)])
open(os.path.join(OUT, 'doodle-head.svg'), 'w').write(
  f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 118 44">{path(star)}{path(arrow)}{path(tick, 2.2)}{sparks}</svg>\n')

# 慕夏厅墙纸：菱形花格 + 小花，极淡
G = '#a98a48'
open(os.path.join(OUT, 'lattice.svg'), 'w').write(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><g fill="none" stroke="{G}" stroke-opacity=".3" stroke-width="1">
<path d="M60 0C78 22 98 42 120 60C98 78 78 98 60 120C42 98 22 78 0 60C22 42 42 22 60 0Z"/>
<path d="M60 44c6 6 10 10 16 16c-6 6-10 10-16 16c-6-6-10-10-16-16c6-6 10-10 16-16Z"/>
<path d="M60 44c-2-8 0-14 0-20M60 76c2 8 0 14 0 20M44 60c-8 2-14 0-20 0M76 60c8-2 14 0 20 0"/></g>
<g fill="{G}" fill-opacity=".32"><circle cx="60" cy="60" r="3.2"/><circle cx="0" cy="0" r="3"/><circle cx="120" cy="0" r="3"/><circle cx="0" cy="120" r="3"/><circle cx="120" cy="120" r="3"/></g></svg>
''')

# 卡片四角的卷草（一笔鞭线 + 两片叶 + 一朵小花）；另外三角靠翻转
C = '#b08d44'
corner = (f'<g fill="none" stroke="{C}" stroke-width="1.5" stroke-linecap="round">'
  '<path d="M2 38C2 16 16 2 38 2"/><path d="M8 34C9 20 20 9 34 8"/><path d="M14 14C20 20 22 26 18 30C14 33 11 29 14 26"/></g>'
  f'<g fill="{C}"><path d="M14 14C10 12 8 8 9 4C13 5 16 9 14 14Z"/><path d="M14 14C12 10 8 8 4 9C5 13 9 16 14 14Z" opacity=".7"/><circle cx="24" cy="12" r="1.7"/><circle cx="12" cy="24" r="1.7"/></g>')
for name, t in {'tl': '', 'tr': 'translate(40 0) scale(-1 1)', 'bl': 'translate(0 40) scale(1 -1)', 'br': 'translate(40 40) scale(-1 -1)'}.items():
    open(os.path.join(OUT, f'corner-{name}.svg'), 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><g transform="{t}">{corner}</g></svg>\n')
print('ok')

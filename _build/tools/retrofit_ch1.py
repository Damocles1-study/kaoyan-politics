# -*- coding: utf-8 -*-
# 一次性脚本：把第 1 章讲义翻新成新版式（编号徽章、qlinks、彩色关键词）
import re
p='/Users/zyx/Downloads/新威考研-资料/11408相关/政治/复盘中心/讲义/马原_导论与第1章.html'
s=open(p,encoding='utf-8').read()
s=s.replace('多选 10–13、19–21','多选 10–13、18–21')
s=re.sub(r'<h2>(\d+)\. ([^<]+)</h2>',r'<h2><span class="no">\1</span>\2</h2>',s)
s=re.sub(r'<p>🔗 (.*?)</p>',r'<div class="qlinks">🔗 \1</div>',s)
s=re.sub(r'\s*<p class="lead">图例：.*?</p>','',s,flags=re.S)
KEEP={'考点骨架','三个头衔一定要分清','唯物主义物质观的三种形态','唯心主义两种形态','意识的起源','意识的本质','意识的能动作用四条',
 '主观能动性与客观规律性的统一','联系的四个特点','系统观念','发展的实质','同一性与斗争性','同一性的作用','斗争性的作用','普遍性与特殊性',
 '主要矛盾与次要矛盾、矛盾的主要方面与次要方面','内因与外因','三个概念','量变与质变的关系','辩证否定观四句话','否定之否定','辩证思维方法',
 '唯物辩证法本质上是批判的、革命的','主观辩证法与客观辩证法','七种思维能力','运动与静止','自然界与人类社会的区别','怎么读这一页',
 '产生条件三件套','创立者','鲜明特征','当代价值','三大组成部分','直接理论来源','自然科学前提'}
def rb(m):
    t=m.group(1)
    return m.group(0) if (t in KEEP or t.startswith('分析题框架')) else '<span class="kw">%s</span>' % t
i=s.index('<section class="card" id="d0">')
head,body=s[:i],s[i:]
body=re.sub(r'<b>([^<]{1,40})</b>',rb,body)
def purple(seg):
    seg=re.sub(r'(《[^》<]{1,30}》)',r'<span class="kt">\1</span>',seg)
    seg=re.sub(r'(?<!\d)(1[89]\d\d(?:–1[89]\d\d)?)(?=[《年 ])',r'<span class="kt">\1</span>',seg)
    return seg
parts=re.split(r'(<[^>]+>)',body)
inside_kt=False; out=[]
for x in parts:
    if x.startswith('<'):
        out.append(x)
    else:
        out.append(purple(x))
body=''.join(out)
# 已经在 kw 里的《》不重复包
body=body.replace('<span class="kw"><span class="kt">','<span class="kt"><span class="kt">')
body=body.replace('<table>\n<tr><th>问法</th><th>答案</th></tr>','<table class="onepage">\n<tr><th>问法</th><th>答案</th></tr>')
s=head+body
s=s.replace('· 知识讲解 · 马克思主义基本原理</div>','· 知识讲解 · 马克思主义基本原理 · <a href="马原_第2章.html">第2章 →</a></div>')
open(p,'w',encoding='utf-8').write(s)
print(s.count('class="kw"'),s.count('class="kt"'),s.count('class="no"'))

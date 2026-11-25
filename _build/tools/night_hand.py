# -*- coding: utf-8 -*-
"""夜背页的手写内容：英语作文框架、政治答题骨架、肖四任务。
被 build_night.py 导入。值是 HTML，挖空用六色类名（kw 红必背 / kd 蓝概念 / km 绿方法 / kt 紫时间 / kn 金数字 / kx 橙易错），
「合上自测」时这些词会被遮住，点一下揭开。
"""

def K(s):  return '<span class="kw">%s</span>' % s
def D(s):  return '<span class="kd">%s</span>' % s
def M(s):  return '<span class="km">%s</span>' % s
def X(s):  return '<span class="kx">%s</span>' % s
def N(s):  return '<span class="kn">%s</span>' % s

def ul(*xs): return '<ul>' + ''.join('<li>%s</li>' % x for x in xs) + '</ul>'
def ol(*xs): return '<ol>' + ''.join('<li>%s</li>' % x for x in xs) + '</ol>'
def tip(s):  return '<p class="tip">%s</p>' % s
def en(s):   return '<p class="en">%s</p>' % s

# ───────────────────────── 英语作文 ─────────────────────────
# 每条：id, 标题, 线索（自测时露出来的提示）, 正文
ESSAY = [
 ('E01', '大作文 · 三段骨架（图画 / 漫画）', '描述 → 解读 → 评论；160–200 词',
  ol('<b>第一段 描述（约 50 词）</b>：画面里谁在做什么 ＋ ' + K('把图上的字整句译出来') + '。',
     '<b>第二段 解读（约 70 词）</b>：这幅画想说什么 ＋ 两三条理由或一个例子。' + X('题眼几乎都在「两样东西的对照」里') + '：两句话、一句话和画面、一句话和表。',
     '<b>第三段 评论（约 50 词）</b>：我的态度 ＋ 一两条做法；图上没画的原因用 ' + K('may / might') + ' 说，别说死。')
  + en(K('As is vividly depicted in the cartoon') + ', … . ' + K('Below the picture reads the caption') + ': “…”')
  + en(K('The cartoon conveys a thought-provoking message') + ': … .')
  + en(K('In light of the above') + ', ' + K('it is high time that we') + ' took action to … .')
  + tip('站内 19 年作文复盘的结论：图上的字是什么结构，文章就怎么搭；背熟的「现成联想」先回画面核对一遍再用。')),

 ('E02', '大作文 · 第一段描图句', '画面 → 人物动作 → 图注',
  en(K('In the cartoon above') + ', ' + D('a young man is sitting on a bench') + ', ' + D('staring at his phone') + ', while … .')
  + en(K('What strikes us most is that') + ' … .')
  + en(K('The caption') + ' “…” ' + K('makes the point even clearer') + '.')
  + en('Two people are talking: one says “…”, ' + K('while the other replies') + ', “…”.')
  + ul('人物用 ' + M('现在进行时') + '（is sitting / are climbing）；图注用 ' + M('reads / says') + '。',
       X('只描述画上有的东西') + '：没画工厂就别写 factories，没画结局就别写 finally。',
       '对白题先 ' + K('整句译出，反问句别译成真疑问') + '。')),

 ('E03', '图表作文 · 描述与原因', '总述 → 走势与交叉 → 解释差别',
  en(K('The table / bar chart above illustrates') + ' the changes in … ' + K('from 2015 to 2025') + '.')
  + en(K('As can be seen') + ', the number of … ' + D('rose sharply from') + ' 20 ' + D('to') + ' 60, ' + K('while') + ' that of … ' + D('remained stable at around') + ' 100.')
  + en(K('Several factors may account for') + ' this trend. ' + K('For one thing') + ', … . ' + K('For another') + ', … .')
  + ul('只写 ' + K('走势与交叉') + '，不要把十二个数全念一遍；单位要译准（每百户 ≠ 每百人）。',
       X('原因要解释「不一样」') + '：收入提高能解释三样都涨，解释不了为什么两样停住——它只能当共同背景（2025 真题教训）。',
       '升：rise / climb / increase sharply；降：drop / decline / fall；平：level off / remain stable。')),

 ('E04', '小作文 · 建议信', '目的 → 两三条建议 → 希望采纳',
  en('Dear …,')
  + en(K('I am writing to offer some suggestions on') + ' … .')
  + en(K('To begin with') + ', … . ' + K('In addition') + ', … . ' + K('Last but not least') + ', … .')
  + en(K('I hope you will find these suggestions practical') + ', and ' + K('I am looking forward to seeing improvements') + ' in … .')
  + en('Yours sincerely,<br>Li Ming')
  + tip('每条建议一个动词开头（set up / extend / provide），后面跟一句理由，最好是写信人亲身经历。')),

 ('E05', '小作文 · 道歉信', '道歉 → 原因 → 补救 → 再道歉',
  en(K('I am writing to express my sincere apology for') + ' … .')
  + en(K('The reason is that') + ' … , ' + K('which I did not expect') + '.')
  + en(K('To make up for') + ' the inconvenience, ' + K('I would like to') + ' … . ' + K('Would that be convenient for you?'))
  + en(K('Once again, please accept my apology') + '. ' + K('I hope for your understanding') + '.')
  + tip(X('补救措施必须具体') + '（时间、怎么做），阅卷看的是「解决问题」，不是认错的次数。')),

 ('E06', '小作文 · 邀请信', '邀请 → 时间地点内容 → 请回复',
  en(K('I am writing to invite you to') + ' … , ' + K('which will be held in') + ' … ' + K('on') + ' … .')
  + en('The event will … . ' + K('Your presence will be') + ' a great encouragement to us.')
  + en(K('It would be a great honor if you could') + ' … .')
  + en(K('Please let me know at your earliest convenience') + ' whether you can come.')
  + tip('时间、地点、活动内容、对方要做什么，四件事一件不能少；对教授用 It would be a great honor，对朋友用 I’d love you to come。')),

 ('E07', '小作文 · 感谢信', '感谢 → 具体帮了什么 → 影响 → 回报',
  en(K('I am writing to extend my heartfelt gratitude for') + ' … .')
  + en(K('Without your help, I could not have') + ' … .')
  + en(K('What impressed me most was') + ' … .')
  + en(K('I would be more than happy to return the favor') + ' if you ever … .')
  + tip('感谢要落到 ' + K('一件具体的事') + '；虚拟语气 could not have done 是加分点。')),

 ('E08', '小作文 · 通知', '标题 → 目的 → 时间地点内容 → 报名 → 落款',
  '<p class="en" style="text-align:center"><b>Notice</b></p>'
  + en(K('To enrich') + ' students’ campus life, ' + K('the Students’ Union will hold') + ' … ' + K('in') + ' … ' + K('on') + ' … .')
  + en('The activity ' + K('consists of') + ' … . ' + K('All') + ' … ' + K('are welcome to') + ' take part.')
  + en(K('Those interested please sign up') + ' … ' + K('before') + ' … .')
  + en('<span style="float:right">Students’ Union</span><br>')
  + ul(X('通知要有标题，落款写组织名，不写 Dear、不写 Yours sincerely') + '；用第三人称。',
       '题目若要求「写一封邮件告知」，那就是信，不是通知——' + K('看清体裁') + '。')),

 ('E09', '小作文 · 申请 / 推荐', '申请：岗位 → 资格 → 期待；推荐：人 → 理由',
  en(K('I am writing to apply for') + ' the position of … ' + K('advertised') + ' on … .')
  + en(K('I believe I am qualified for') + ' this position ' + K('for the following reasons') + '. First, … . Second, … .')
  + en(K('I would appreciate it if you could give me an interview') + '.')
  + en(K('I would like to recommend') + ' … ' + K('to you') + '. ' + D('He is not only') + ' … ' + D('but also') + ' … .')
  + tip('资格写两条：一条能力（major / experience），一条性格（responsible / patient），都要配一个事实。')),

 ('E10', '小作文 · 咨询 / 投诉', '询问：问题清单 → 感谢；投诉：事实 → 影响 → 要求',
  en(K('I am writing to inquire about') + ' … . ' + K('I would be grateful if you could tell me') + ' … .')
  + en(K('I am writing to complain about') + ' … . ' + K('To make matters worse') + ', … .')
  + en(K('I would appreciate it if') + ' you could ' + K('look into this matter') + ' and … .')
  + en(K('Thank you for your time and consideration') + '.')
  + tip('投诉信 ' + X('语气克制') + '：说事实、说影响、提具体要求（refund / replace / apologize），不骂人。')),

 ('E11', '大作文 · 第二段论证句', '承上 → 两三条原因或一个例子',
  en(K('There are several reasons for this phenomenon') + '. ' + K('To begin with') + ', … . ' + K('Furthermore') + ', … .')
  + en(K('The significance of') + ' … ' + K('can never be overestimated') + '.')
  + en(K('A case in point is') + ' … , who … .')
  + en(K('It is not that') + ' … , ' + K('but that') + ' … .')
  + tip('一条原因 ＝ 一个观点句 ＋ 一句解释或例子；三条写不满就两条写透，' + X('别堆连接词') + '。')),

 ('E12', '大作文 · 第三段结尾句', '态度 → 做法 → 收束',
  en(K('From what has been discussed above, we may safely draw the conclusion that') + ' … .')
  + en(K('Only in this way can we') + ' … .')
  + en(K('It is high time that') + ' we ' + D('took') + ' effective measures to … .')
  + en(K('As the saying goes') + ', “' + D('Actions speak louder than words') + '.”')
  + tip('Only … can we 是部分倒装；It is high time that 后面用 ' + X('过去式') + '（took），不是 take。')),

 ('E13', '高分句型 · 五个现成结构', '强调 · 倒装 · 让步 · 比较 · 虚拟',
  en(K('It is') + ' persistence ' + K('that') + ' makes the difference.　（强调句）')
  + en(K('Not until') + ' we lose it ' + K('do we realize') + ' its value.　（倒装）')
  + en(K('Admittedly') + ', … . ' + K('However') + ', … .　（先让一步再转）')
  + en(K('The more') + ' we read, ' + K('the more') + ' we understand.　（比较）')
  + en(K('Were it not for') + ' your help, I ' + K('would') + ' still be … .　（虚拟）')
  + tip('全文用上两三个就够；每个都要配本题的内容，硬塞模板会被判「套作」。')),

 ('E14', '小作文 · 格式铁律', '称呼 · 落款 · 字数 · 名字',
  ul('称呼：认识的人 ' + K('Dear Professor Smith,') + '；不认识 ' + K('Dear Sir or Madam,') + '（逗号）。',
     '首段第一句说 ' + K('写信目的') + '（I am writing to …）；末段 ' + K('期待回复 / 再次感谢') + '。',
     '落款：' + K('Yours sincerely,') + ' 另起一行写 ' + X('题目给的名字（Li Ming），绝不写自己的真名') + '，也不写地址。',
     '字数约 ' + N('100') + ' 词，三段：目的一段、正文一段、结尾一段。',
     '题目里每个要点（要写的两三件事）' + X('逐条都要写到') + '，漏一点扣一档。')),
]

# ───────────────────────── 政治答题骨架 ─────────────────────────
POL_FRAME = [
 ('PF34', '34 题马原 · 固定三段', '点名原理 → 展开原理 → 落到材料',
  ol(K('点名原理') + '：「材料体现了……原理。」一句话。',
     K('展开原理') + '：把原理卡的红色关键句写成 2–4 句。',
     K('落到材料') + '：「材料中××的做法，正是……的体现／要求我们……」，每条原理配一句材料。')
  + tip('一问写 2–3 个原理，每个一段，' + K('原理在前、材料在后') + '，分点编号。')),

 ('PF4Q', '四种设问 · 四种开头', '为什么 / 如何理解 / 怎么做 / 体现什么原理',
  ul('「为什么」「原因」：' + K('理论依据 · 历史依据 · 现实依据') + '。',
     '「如何理解」「意义」：' + K('是什么（含义、地位）· 为什么重要 · 落到材料') + '。',
     '「怎么做」「要求 / 启示」：' + K('原理（方法论）· 分点做法，每点「要……」开头 · 落到材料主体') + '。',
     '「体现了什么原理」：' + K('点名原理 · 展开内容 · 材料哪句对应哪一点') + '。')),

 ('PF35', '35 题毛中特 ＋ 习概 · 三条逻辑', '为什么：历史 · 理论 · 实践；意义：地位 · 内涵 · 意义',
  ul('「为什么」：' + K('历史逻辑') + '（过去怎么走过来的）· ' + K('理论逻辑') + '（马克思主义原理、党的理论）· ' + K('实践逻辑') + '（今天的任务和形势）。',
     '「怎么理解 / 意义」：写 ' + K('地位 · 内涵 · 意义') + '，意义按 ' + D('对党、对国家、对民族、对世界') + ' 分层。',
     '材料几乎都是当年时政大会 ⟹ ' + X('最终以 12 月的肖四为准') + '，这里只背骨架。')),

 ('PF36', '36 题史纲 · 为什么能', '背景 → 事件 → 意义；「为什么能」三件套',
  ul('一般设问：' + K('背景 → 事件 → 意义 / 原因 / 经验') + '；时间、人物、会议要准。',
     '「为什么能 / 为什么说」常落到：' + K('中国共产党的领导 · 人民群众的支持 · 马克思主义的指导') + '。',
     '「为什么改良 / 旧式革命走不通」：' + D('没有先进阶级领导、没有科学理论、没有发动群众') + '。')),

 ('PF37', '37 题思法 · 三段 ＋ 青年落脚', '是什么 → 关系 / 意义 → 青年怎么做',
  ol(K('是什么') + '：概念、地位（调十四专题的第一句）。',
     K('关系 / 意义') + '：两者怎么联系、为什么重要。',
     K('青年怎么做') + '：结尾一定落到「' + K('新时代青年应当……') + '」，挑 2–3 句落脚句，再配一句材料。')
  + tip('万能落脚：立志做' + K('有理想、敢担当、能吃苦、肯奋斗') + '的新时代好青年；把' + K('小我融入大我') + '。')),

 ('PFJM', '卷面规范 · 这些就是采分点', '分点 · 关键词前置 · 原理加材料 · 宁多勿少',
  ul(K('分点编号') + '：每问 3–5 点，一点一段；阅卷找关键词，不读文章。',
     K('关键词前置') + '：每段第一句就是教材原话，后面再解释、再结合材料。',
     K('原理 ＋ 材料都要有') + '：只写一样只能拿一半。',
     K('宁多勿少') + '：不倒扣分，没把握的相关原理也可以写（别写错的）。',
     '每问 ' + N('150–250') + ' 字，写满答题区约 2/3。')),
]

# 肖四 / 套卷任务（纸质书，夜背页只给勾选）
TASKS = {
 '12-11': ['肖四第 1 套：34–38 题，每问划出 3–5 个关键词，合上书说一遍'],
 '12-12': ['肖四第 2 套：34–38 题关键词'],
 '12-13': ['肖四第 3 套：34–38 题关键词'],
 '12-14': ['肖四第 4 套：34–38 题关键词'],
 '12-15': ['肖四第 1、2 套：只看设问，默写每问的第一句'],
 '12-16': ['肖四第 3、4 套：只看设问，默写每问的第一句'],
 '12-17': ['肖四四套的 38 题（时政）：每套背 3 个关键词句'],
 '12-18': ['肖四四套 34–37 题：每问只看首句，最后过一遍'],
}
TASK_NOTE = '肖四一般在 12 月上旬出。还没到手的晚上，换成套卷页里肖八的分析题骨架（交卷后显示），同样只划关键词、不背整段。'

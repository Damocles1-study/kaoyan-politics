# -*- coding: utf-8 -*-
"""夜背页的手写内容（只放能直接背、直接写上卷面的东西）：
  POL_TPL   政治 34–37 题通用答题模板（框架 ＋ 整段可套的话）
  ESSAY     英语一作文完整模板（小作文七类 ＋ 大作文两类），空格处填本题内容
  TASKS     肖四纸质书任务
挖空用六色类名：kw 红（必背）· kd 蓝 · km 绿 · kn 金。合上自测时这些词被遮住。
"""

def K(s): return '<span class="kw">%s</span>' % s
def D(s): return '<span class="kd">%s</span>' % s
def M(s): return '<span class="km">%s</span>' % s
def p(s): return '<p>%s</p>' % s
def en(s): return '<p class="en">%s</p>' % s
B = '＿＿'

# ───────────── 政治：四道大题的通用模板 ─────────────
# (id, 标题, 框架, 正文)
POL_TPL = [
 ('T34', '34 题马原 · 答题模板', '点名原理 → 原理内容 → 材料对应 → 方法论',
  p('<b>（1）点名：</b>' + K('材料体现了' + B + '原理') + '（一问一般写 2–3 个原理，每个原理一段）。')
  + p('<b>（2）原理内容：</b>' + K(B + '原理认为') + '：……（把该原理的完整背法写 2–4 句）。')
  + p('<b>（3）材料对应：</b>' + K('材料中' + B + '，正是' + B + '的体现') + '；' + K('材料中' + B + '说明了' + B) + '。')
  + p('<b>（4）方法论：</b>' + K('这要求我们') + '坚持' + B + '，做到' + B + '。')
  + p('<b>高频原理的方法论句（直接接在第 4 步）：</b>'
      '矛盾 → ' + M('坚持两点论和重点论的统一，具体问题具体分析') + '；'
      '量变质变 → ' + M('重视量的积累，抓住时机促成质变，坚持适度原则') + '；'
      '辩证否定 → ' + M('取其精华、去其糟粕，守正创新') + '；'
      '实践与认识 → ' + M('坚持实践第一，在实践中检验和发展真理') + '；'
      '规律与能动性 → ' + M('尊重客观规律，充分发挥主观能动性，一切从实际出发') + '；'
      '联系 → ' + M('用联系的观点看问题，坚持系统观念，统筹兼顾') + '；'
      '发展 → ' + M('用发展的眼光看问题，支持新事物的成长') + '；'
      '人民群众 → ' + M('坚持以人民为中心，走群众路线') + '。')),

 ('T35', '35 题毛中特 ＋ 习概 · 答题模板', '为什么：历史 · 理论 · 实践；意义：党 · 国家 · 民族 · 世界；怎么做：方向 · 动力 · 保障',
  p('<b>「为什么 / 必然性」：</b>'
    '① ' + K('从历史逻辑看') + '：' + B + '是总结党和人民百年奋斗' + K('历史经验') + '得出的结论……'
    '② ' + K('从理论逻辑看') + '：' + B + '是' + K('马克思主义基本原理同中国具体实际相结合、同中华优秀传统文化相结合') + '的产物……'
    '③ ' + K('从实践逻辑看') + '：' + B + '是应对' + K('世界百年未有之大变局') + '、推进' + K('中国式现代化') + '、实现' + K('中华民族伟大复兴') + '的必然要求。')
  + p('<b>「意义 / 如何理解」：</b>'
    '① ' + K('对党') + '：丰富和发展了马克思主义（党的创新理论）……'
    '② ' + K('对国家') + '：为' + B + '提供了根本遵循 / 强大动力……'
    '③ ' + K('对民族') + '：为实现中华民族伟大复兴' + B + '……'
    '④ ' + K('对世界') + '：为解决人类问题贡献了' + K('中国智慧和中国方案') + '。')
  + p('<b>「怎么做」：</b>'
    '① ' + K('坚持党的全面领导') + '（根本保证）；'
    '② ' + K('坚持以人民为中心') + '（根本立场）；'
    '③ ' + K('全面深化改革、扩大开放') + '（根本动力）；'
    '④ 结合设问写 2–3 条具体举措，每条「要……」开头。')),

 ('T36', '36 题史纲 · 答题模板', '背景 → 原因 → 意义 / 经验',
  p('<b>「为什么能 / 为什么成功」三件套：</b>'
    '① ' + K('中国共产党的坚强领导') + '（有了主心骨、正确路线）；'
    '② ' + K('人民群众的广泛支持') + '（人民是历史的创造者）；'
    '③ ' + K('马克思主义的科学指导') + '（理论同中国实际相结合）。'
    '再加一条材料里的具体原因（统一战线 / 武装斗争 / 实事求是 / 自我革命）。')
  + p('<b>「历史意义」三层：</b>'
    '① 对' + K('中国革命 / 建设 / 改革') + '本身：标志着' + B + '，开辟了' + B + '；'
    '② 对' + K('中华民族') + '：' + B + '（独立、解放、站起来 / 富起来 / 强起来）；'
    '③ 对' + K('世界') + '：' + B + '（鼓舞被压迫民族、贡献中国方案）。')
  + p('<b>「为什么旧路走不通」：</b>' + D('农民阶级、地主阶级洋务派、资产阶级维新派与革命派') + '都'
    + K('没有科学理论指导、没有先进阶级领导、没有充分发动群众') + '，'
    + K('不能完成反帝反封建的历史任务') + '。')),

 ('T37', '37 题思法 · 答题模板', '是什么 → 为什么重要 / 关系 → 青年怎么做',
  p('<b>（1）是什么：</b>' + K(B + '是……') + '（写该专题的概念与地位，取专题卡第一句）。')
  + p('<b>（2）关系 / 意义：</b>' + K(B + '与' + B + '相互联系、相互促进') + '；' + K('对个人') + '……' + K('对社会 / 国家') + '……')
  + p('<b>（3）青年怎么做（必写，3 句）：</b>'
      '新时代青年应当' + K('坚定理想信念，把小我融入大我') + '；'
      + K('自觉践行社会主义核心价值观') + '，' + K('勤学、修德、明辨、笃实') + '；'
      + K('立志做有理想、敢担当、能吃苦、肯奋斗的新时代好青年') + '，在' + B + '中' + K('贡献青春力量') + '。')),
]

# ───────────── 英语：完整作文模板 ─────────────
# 小作文 ≈ 100 词；Li Ming 是题目指定署名，照题目写
S = '_____'
ESSAY = [
 ('LTR0', '小作文 · 通用书信骨架', '称呼 → 目的 → 正文要点 → 结尾 → 落款',
  en('Dear ' + S + ',')
  + en(K('I am writing to') + ' ' + S + '（目的：offer some suggestions on / express my sincere apology for / invite you to / inquire about …）.')
  + en(K('To begin with') + ', ' + S + '. ' + K('In addition') + ', ' + S + '. ' + K('Last but not least') + ', ' + S + '.')
  + en(K('I would appreciate it if you could') + ' ' + S + '. ' + K('Thank you for your time and consideration') + '.')
  + en(K('Yours sincerely,') + '<br>Li Ming')),

 ('LTR1', '小作文 · 建议信', '目的 → 两三条建议 → 希望采纳',
  en('Dear ' + S + ',')
  + en(K('Learning that') + ' ' + S + ', ' + K('I am writing to offer some suggestions') + ' ' + K('which I hope will be of help') + '.')
  + en(K('First and foremost') + ', ' + K('it would be advisable to') + ' ' + S + ', ' + K('so that') + ' ' + S + '. '
       + K('Furthermore') + ', ' + S + ' ' + K('should be') + ' ' + S + ', ' + K('which will') + ' ' + S + '. '
       + K('Finally') + ', ' + K('it might be a good idea to') + ' ' + S + '.')
  + en(K('I hope you will find these suggestions practical and helpful') + ', and ' + K('I am looking forward to seeing improvements') + ' in ' + S + '.')
  + en('Yours sincerely,<br>Li Ming')),

 ('LTR2', '小作文 · 道歉信', '道歉 → 原因 → 补救 → 再道歉',
  en('Dear ' + S + ',')
  + en(K('I am writing to express my sincere apology for') + ' ' + S + '.')
  + en(K('The reason is that') + ' ' + S + ', ' + K('which I did not expect at all') + '. '
       + K('To make up for') + ' ' + K('the inconvenience I have caused') + ', ' + K('I would like to') + ' ' + S + '. '
       + K('Would it be convenient for you if') + ' ' + S + '? ' + K('Please let me know at your earliest convenience') + '.')
  + en(K('Once again, please accept my apologies') + '. ' + K('I hope for your understanding') + '.')
  + en('Yours sincerely,<br>Li Ming')),

 ('LTR3', '小作文 · 邀请信', '邀请 → 时间地点内容 → 期待回复',
  en('Dear ' + S + ',')
  + en(K('On behalf of') + ' ' + S + ', ' + K('I am writing to invite you to') + ' ' + S + ', ' + K('which will be held in') + ' ' + S + ' ' + K('on') + ' ' + S + '.')
  + en(K('The event aims to') + ' ' + S + '. ' + K('It would be a great honor if you could') + ' ' + S + ', '
       + K('since your expertise in') + ' ' + S + ' ' + K('will be of great value to') + ' ' + S + '.')
  + en(K('Please let me know whether you are available') + ' ' + K('at your earliest convenience') + '. ' + K('We are looking forward to your presence') + '.')
  + en('Yours sincerely,<br>Li Ming')),

 ('LTR4', '小作文 · 感谢信', '感谢 → 具体帮了什么 → 影响 → 回报',
  en('Dear ' + S + ',')
  + en(K('I am writing to extend my heartfelt gratitude for') + ' ' + S + '.')
  + en(K('Without your help, I could not have') + ' ' + S + '. ' + K('What impressed me most was') + ' ' + S + ', '
       + K('which has greatly benefited me') + '. ' + K('I would be more than happy to return the favor') + ' ' + K('if you ever') + ' ' + S + '.')
  + en(K('Thank you again for') + ' ' + S + '. ' + K('I am looking forward to seeing you again') + '.')
  + en('Yours sincerely,<br>Li Ming')),

 ('LTR5', '小作文 · 通知', '标题 → 目的 → 时间地点内容 → 报名 → 落款',
  '<p class="en" style="text-align:center"><b>' + K('Notice') + '</b></p>'
  + en(K('In order to') + ' ' + S + ', ' + K('the Students’ Union will hold') + ' ' + S + ' ' + K('in') + ' ' + S + ' ' + K('from') + ' ' + S + ' ' + K('to') + ' ' + S + ' ' + K('on') + ' ' + S + '.')
  + en(K('The activity consists of') + ' ' + S + '. ' + K('All') + ' ' + S + ' ' + K('are warmly welcome to') + ' ' + K('take part') + '. '
       + K('Those who are interested please sign up with') + ' ' + S + ' ' + K('before') + ' ' + S + '.')
  + '<p class="en" style="text-align:right">' + K('Students’ Union') + '<br>' + S + '（日期）</p>'),

 ('LTR6', '小作文 · 申请 / 求职信', '申请 → 资格两条 → 请求面试',
  en('Dear ' + S + ',')
  + en(K('I am writing to apply for') + ' ' + K('the position of') + ' ' + S + ' ' + K('advertised') + ' ' + S + '.')
  + en(K('I believe I am qualified for the position for the following reasons') + '. ' + K('First') + ', ' + S + '（专业 / 经验）. '
       + K('Second') + ', ' + S + '（性格 / 能力）, ' + K('which will enable me to') + ' ' + S + '.')
  + en(K('I would appreciate it if you could give me an interview') + '. ' + K('Thank you for your consideration') + '.')
  + en('Yours sincerely,<br>Li Ming')),

 ('LTR7', '小作文 · 咨询 / 投诉 / 推荐', '咨询：问题；投诉：事实 → 影响 → 要求；推荐：对象 → 理由',
  en(K('I am writing to inquire about') + ' ' + S + '. ' + K('I would be grateful if you could tell me') + ' ' + S + '.')
  + en(K('I am writing to complain about') + ' ' + S + '. ' + K('To make matters worse') + ', ' + S + '. '
       + K('I would appreciate it if you could look into this matter') + ' ' + K('and') + ' ' + S + '（refund / replace / apologize）.')
  + en(K('I would like to recommend') + ' ' + S + ' ' + K('to you') + '. ' + K('It is not only') + ' ' + S + ' ' + K('but also') + ' ' + S + '.')),

 ('ESS1', '大作文 · 图画作文（160–200 词）', '描述 → 解读 → 原因 → 建议 / 结论',
  en(K('As is vividly depicted in the cartoon') + ', ' + S + '（谁在做什么）. '
     + K('Below the picture reads the caption') + ': “' + S + '”（图上的字整句译出）. '
     + K('The cartoon conveys a thought-provoking message') + ': ' + S + '.')
  + en(K('There are several reasons for this phenomenon') + '. ' + K('To begin with') + ', ' + S + '. '
       + K('Furthermore') + ', ' + S + '. ' + K('A case in point is') + ' ' + S + ', ' + K('who') + ' ' + S + '. '
       + K('The significance of') + ' ' + S + ' ' + K('can never be overestimated') + '.')
  + en(K('From what has been discussed above, we may safely draw the conclusion that') + ' ' + S + '. '
       + K('It is high time that we took effective measures to') + ' ' + S + '. '
       + K('Only in this way can we') + ' ' + S + '.')),

 ('ESS2', '大作文 · 图表作文（160–200 词）', '总述 → 走势与交叉 → 原因 → 结论',
  en(K('The table / bar chart above illustrates') + ' ' + K('the changes in') + ' ' + S + ' ' + K('from') + ' ' + S + ' ' + K('to') + ' ' + S + '. '
     + K('As can be seen') + ', ' + S + ' ' + K('rose sharply from') + ' ' + S + ' ' + K('to') + ' ' + S + ', '
     + K('while') + ' ' + S + ' ' + K('remained stable at around') + ' ' + S + '.')
  + en(K('Several factors may account for this trend') + '. ' + K('For one thing') + ', ' + S + '. ' + K('For another') + ', ' + S + '. '
       + K('What is more') + ', ' + S + '.')
  + en(K('In light of the above') + ', ' + K('it is reasonable to predict that') + ' ' + S + ' ' + K('will continue in the years to come') + '. '
       + K('Therefore') + ', ' + K('it is essential for us to') + ' ' + S + '.')),
]

TASKS = {
 '12-11': ['肖四第 1 套 34–38 题：每问划出关键句，合上书按「框架 → 关键句」说一遍'],
 '12-12': ['肖四第 2 套 34–38 题关键句'],
 '12-13': ['肖四第 3 套 34–38 题关键句'],
 '12-14': ['肖四第 4 套 34–38 题关键句'],
 '12-15': ['肖四第 1、2 套：只看设问，默写每问第一句'],
 '12-16': ['肖四第 3、4 套：只看设问，默写每问第一句'],
 '12-17': ['肖四四套 38 题（时政）：每套背 3 句'],
 '12-18': ['肖四四套 34–37 题：每问首句最后过一遍'],
}
TASK_NOTE = '肖四没到手的晚上，用套卷页肖八的分析题骨架代替。'

# 政治复盘中心（2027 考研）

纯静态网站，离线可跑、无外部依赖。线上：<https://damocles1-study.github.io/kaoyan-politics/>

## 目录

| 路径 | 内容 |
|---|---|
| `index.html` | 首页：倒计时、分值地图、模块入口、章节总表（读 `题库/meta.js` ＋ 本机记录动态生成）、60 天计划 |
| `题库/刷题.html` ＋ `engine.js` | 1000 题刷题引擎。URL 参数：`p`(my/mz/xg/sg/sx/all) `t`(s/m/e/all) `ch` `mode`(seq/undone/wrong/rand) `view`(do/read) `q`(跳到题 id) |
| `题库/data_*.js` | 五科题库（`window.POL.<科>`），**由 `_build/tools/build_data.py` 生成，别手改** |
| `题库/meta.js` | 首页 / 统计页用的轻量目录（章名、题号区间、讲义登记、秒杀笔记数） |
| `题库/统计.html` | 按科按章正确率、错题本入口、记录导出 / 导入（换设备用） |
| `讲义/` | 每章知识讲解（自编）。登记到 `build_data.py` 的 `LECT` 后首页总表自动出链接 |
| `秒杀/选择题秒杀.html` | 八类干扰项 ＋ 马原易混提法表 |
| `大题/分析题答题法.html` | 五道大题套路、设问模板、卷面规范、必背清单（勾选存本机） |
| `assets/style.css` | 共享样式（批注体系 `.key/.mine/.trap/.bg/.link/.img/.miao/.mem` ＋ 大题三层 `.think/.paper/.notekeep`） |
| `_build/` | 题库构建管线（见下） |

## 本机记录（localStorage）

- `pol_rec_v1`：`{题id: {n 作答次数, ok 最近对错, w 累计错次, streak 连对次数, pick, self(分析题自评), ts}}`；**连对 2 次自动出错题本**。
- `pol_pref_v1`：上次的科目 / 题型 / 章节 / 视图。`pol_memo_v1`：大题必背清单勾选。

## 重建题库

```bash
python3 _build/tools/build_data.py
```

- 输入：`_build/work/questions2.json`（试题）＋ `answers.json`（解析）＋ `_build/notes/manual_fix.json`（人工转录的坏页题）＋ `_build/notes/my_notes.json`（⚡秒杀笔记，**每写一章就往这里加**，键＝题 id）。
- 从头再来：`ocr_book.py`（本机 Vision OCR，走 `osascript -l JavaScript ocr.js`，Swift 工具链坏了别用 swiftc）→ `dual.py`（试题双源择优）→ `parse_q2.py` → `parse_a.py` → `build_data.py`。
- `_build/ocr/`、`_build/work/` 是整本书的识别文字，**只留本地，不推 GitHub**（.gitignore）。

## 已知事实

- 1000 题：五科 1148 道选择（马原 184+212 / 毛中特 56+59 / 习概 93+127 / 史纲 129+122 / 思法 66+100）＋ 15 道分析题。答案逐题对齐、零缺号。
- 试题 PDF 原本缺 12 页（马原分析 P60–64、习概分析 P113–116、史纲分析 P154–156），对应分析题只有答案。
- 书 P18（马原单选 122–130）原扫描糊掉，9 题人工看图转录。
- 真题 2024–2026 题型分布三年一致：单选 马4 毛2 习3 史4 思1 时2；多选 马5 毛1 习4 史3 思2 时2；分析 34 马 / 35 毛+习 / 36 史 / 37 思 / 38 时政。

题目与解析版权归原作者，本站仅供个人复习，如有侵权联系即删。

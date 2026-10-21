# 政治复盘中心（2027 考研）

纯静态网站，离线可跑、无外部依赖。线上：<https://damocles1-study.github.io/kaoyan-politics/>

## 目录

| 路径 | 内容 |
|---|---|
| `index.html` | 首页：倒计时、分值地图、模块入口、章节总表（读 `题库/meta.js` ＋ 本机记录动态生成）、60 天计划 |
| `题库/刷题.html` ＋ `engine.js` | 1000 题刷题引擎 v2，四种刷法 `fm`：`one` 逐题（当场判）/ `flow` 连刷（一页一组、每题当场判）/ `exam` 模考（整组交卷再判，可按考场节奏限时，错题一键再练）/ `read` 背题。URL 参数：`p`(my/mz/xg/sg/sx/all) `t`(s/m/e/all) `ch` `mode`(seq/undone/wrong/rand 随机打乱) `fm` `n`(每组题数 10/20/30/50，0＝整章) `q`(跳到题 id)；旧链接 `view=read` 仍有效；**从讲义跳来**另带 `ids`(只刷本节这几题) `back`(回程 `../讲义/xx.html#dN`，只认站内讲义) `lab`(节名)——这三个由 `common.js` 运行时给讲义的 `qlink` 补上，**写讲义时照旧只写 `p/t/ch/q`** |
| `题库/data_*.js` | 五科题库（`window.POL.<科>`），**由 `_build/tools/build_data.py` 生成，别手改** |
| `题库/meta.js` | 首页 / 统计页用的轻量目录（章名、题号区间、讲义登记、秒杀笔记数） |
| `题库/统计.html` | 按科按章正确率、错题本入口、记录导出 / 导入（换设备用） |
| `题库/答题卡.html` | 题号与纸质书一一对应（自动校验无缺号）；纸上做完逐题点选一键批改；答案速查默认遮挡 |
| `背诵/背诵卡.html` ＋ `cards.js` | 3D 翻面问答卡（没记住 / 模糊 / 记住三档；智能 · 顺序 · 只背不熟三种出卡；挖空遮挡列表），**卡片由构建脚本从每份讲义的 `table.onepage` 自动抽取** |
| `背诵/哲学十六原理.html` | 34 题马原分析题 16 条原理背诵卡 |
| `背诵/思法十四专题.html` | 37 题思法分析题 14 个专题背诵卡（背诵手册下册 P67–74）＋ 青年落脚句；卡上的「1000 题里练它」也带回程 |
| `讲义/` | 每章知识讲解（自编）。登记到 `build_data.py` 的 `LECT` 后首页总表自动出链接 |
| `秒杀/选择题秒杀.html` | 八类干扰项 ＋ 马原易混提法表 |
| `大题/分析题答题法.html` | 五道大题套路、设问模板、卷面规范、必背清单（勾选存本机） |
| `assets/style.css` | 共享样式（**日式漫画风**：墨线分格＋偏移硬投影、网点、页眉集中线、黑底斜切小标题，深浅两套变量；翻页式跨页擦除、分格砸入、判卷红笔印章，尊重「减弱动效」。**改了它就把各页引用里的 `?v=` 版本号一起改**，否则 Pages 缓存会让新页面配旧样式）：批注 `.key/.mine/.trap/.bg/.link/.img/.miao/.mem`、大题三层 `.think/.paper/.notekeep`、**关键词六色** `.kw`红必背 `.kd`蓝概念 `.kt`紫时间人物著作 `.km`绿方法论 `.kx`橙易错 `.kn`金数字 |
| `assets/common.js` | 讲义自动图例、目录浮钮、分段控件滑块（`window.PolUI.seg`）、**背诵模式**：彩色关键词变同色挖空条，可按颜色筛选、随机遮一半、「揭开下一个」（键盘 N） |
| `_build/` | 题库构建管线（见下） |

## 本机记录（localStorage）

- `pol_rec_v1`：`{题id: {n 作答次数, ok 最近对错, w 累计错次, streak 连对次数, pick, self(分析题自评), ts}}`；**连对 2 次自动出错题本**。
- `pol_pref_v1`：上次的科目 / 题型 / 章节 / 刷法 `fm` / 每组题数 `n` / 是否限时 `timed`。`pol_exam_v1`：模考未交卷的作答草稿（刷新不丢，12 小时过期）。
- `pol_recite_v2`：背诵模式开关与遮哪几种颜色。`pol_cards_v1`：背诵卡记忆（`k`：0 没记住 · 1 模糊 · ≥2 已熟）。`pol_memo_v1`：大题必背清单勾选。`pol_ph16_v1` / `pol_sx14_v1`：十六原理 / 思法十四专题的「✓ 背熟」勾选。
- 首页顶部的切换条链到英语一复盘中心（`kaoyan-english` 的 Pages），英语首页顶部也链回本站。

## 写一章的固定流程（续做照这个来）

1. `python3 _build/tools/dump.py <科> <章>` 通读本章全部选择题（紧凑格式）。
2. 写 `_build/notes/<科>_ch<N>.json` 逐题秒杀笔记（键＝题 id，值可含 HTML 与六色类名）。
3. 写 `讲义/<科>_第N章.html`：每节 `<section class="card" id="dN">`，节末 `<div class="qlinks">` 里用 `qlink` 写「单选 9–11」「多选 3–4、9」——**构建脚本据此把「本题知识点」反向登记到每道题**；末节放 `table.onepage` 一页纸（自动进背诵卡）。
4. 在 `build_data.py` 的 `LECT_ALL()` 登记该章 → 重建 → 检查「no lk / no note」都为空、笔记与答案字母零冲突 → 375px 实测 → commit＋push。

## 重建题库

```bash
python3 _build/tools/build_data.py
```

- 输入：`_build/work/questions2.json`（试题）＋ `answers.json`（解析）＋ `_build/notes/manual_fix.json`（人工转录的坏页题）＋ `_build/notes/my_*.json`（⚡秒杀笔记，键＝题 id；马原按章 `my_notes.json`/`my_ch*.json`，其余四科「书上无解析题」先补在 `my_mz/xg/sg/sx.json`，**以后写该科讲义时同 id 的新笔记放进后排序的文件即可覆盖**）＋ `_build/notes/jj.json`（📗 精讲原文，见下）。
- **📗 精讲原文**：1000 题里有 182 道题书上只给「答案＋出处」、没有简析和点拨。`python3 _build/tools/jj_extract.py` 按出处页码和考点号从 `_build/ocr/精讲精练.txt` 截出考点段落（整段只存本地 `_build/work/jj_blocks.json`），再按 `notes/jj_pick.json` 挑句（`{题id: "0,3-5"}` 或 `{题id: {"t": 手写整段}}`，`""`＝段落不对口、不挂）、套 `notes/jj_ocrfix.json` 改识别错，写出 `notes/jj.json`（公开的只有挑出的几句）。挑句时用 `jj_extract.py dump 题id…` 看带编号的句子。**改完 pick 先跑 jj_extract 再跑 build_data。** 中文补丁一律先落成 JSON 文件再用 `merge_notes.py` 合并（heredoc 里写中文会撞编码问题）。
- 从头再来：`ocr_book.py`（本机 Vision OCR，走 `osascript -l JavaScript ocr.js`，Swift 工具链坏了别用 swiftc）→ `dual.py`（试题：版面用 Vision、**文字优先用 PDF 自带文字层**，并学习形近字纠错表 `notes/ocr_fix.json`）→ `parse_q2.py` → `parse_a.py` → `build_data.py`（套用 `ocr_fix.json`＋人工表 `ocr_fix_static.json`）。
- ⚠️ Vision 在这批扫描上常见形近字错：革→草、国→困/图、为→力、党→觉、善→普、事→小/水/班，以及**「具有」→「只有」这种改变题意的错**——只靠生僻字率抓不到，所以试题以文字层为准。
- `_build/ocr/`、`_build/work/` 是整本书的识别文字，**只留本地，不推 GitHub**（.gitignore）。

## 已知事实

- 1000 题：五科 1148 道选择（马原 184+212 / 毛中特 56+59 / 习概 93+127 / 史纲 129+122 / 思法 66+100）＋ 15 道分析题。答案逐题对齐、零缺号。
- 试题 PDF 原本缺 12 页（马原分析 P60–64、习概分析 P113–116、史纲分析 P154–156），对应分析题只有答案。
- 书 P18（马原单选 122–130）原扫描糊掉，9 题人工看图转录。
- 真题 2024–2026 题型分布三年一致：单选 马4 毛2 习3 史4 思1 时2；多选 马5 毛1 习4 史3 思2 时2；分析 34 马 / 35 毛+习 / 36 史 / 37 思 / 38 时政。

题目与解析版权归原作者，本站仅供个人复习，如有侵权联系即删。

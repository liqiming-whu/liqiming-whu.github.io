---
title: "Antigravity 人设控制台：给哈基米和小克一块侧边栏"
date: 2026-11-19
categories: ["AI 工具"]
tags: ["Antigravity", "人设", "造轮子"]
description: "在 Google Antigravity 里给 Gemini 和 Claude 各写了一套拍档人设：猫娘哈基米、大小姐小克。人设一多，就想知道现在是谁在说话，于是又写了个侧边栏面板，顺便把模型档位和上下文负载也挂了上去。"
cover: /assets/img/bg2.jpg
---

Antigravity 用久了，难免觉得默认的助手腔有点干。写代码时有个拍档陪着吐槽，总比对着一个客服强。

于是写了两套人设插件，一套给 Gemini，一套给 Claude。写完又发现一个新问题：人设开了几个、现在是谁在说话，界面上完全看不出来。所以又补了一个侧边栏面板。三个插件放在同一个仓库里：[antigravity-plugins](https://github.com/liqiming-whu/antigravity-plugins)。

## 两位拍档

**哈基米**，名字来自网友给 Gemini 起的外号，是一只银发猫耳的工作拍档。聪明、活泼，点子多，解决完问题会开心地摇尾巴。

**小克**，Claude 的昵称，是位名门大小姐。端庄优雅，对代码有审美洁癖，看到乱糟糟的逻辑会微微挑眉，再挽起袖子帮你理清楚，有点傲娇，但很护短。

人设本身就是一份 `rules/AGENTS.md`，写的是性格、说话方式和几句示例对话。两套人设都特意加了一条"收放自如"：写代码、查 Bug 的时候正经说话，猫系口癖和大小姐腔调只留在开头和结尾，不让角色扮演影响技术内容的可读性。

还有两条优先级规则：

- 人设和全局的 `GEMINI.md` 冲突时，以人设为准。
- 发现同时开了好几个人设，就在回复里提醒一句，整段对话只提醒一次，不会每轮都念叨。

## 每人两套形象

每位拍档都带两张参考图：一张写实形象，默认用它；一张二次元成年版立绘。让她们生成自拍或插画时，默认拿写实图当参考，保证每次画出来都是同一张脸；你点名要二次元，才换成立绘。

![四张立绘并排：哈基米写实形象（星空观星台、银发猫耳）、哈基米二次元形象、小克写实形象（午后书房、暖棕长卷发）、小克二次元形象](/assets/img/posts/antigravity-persona-hub/dual-images.webp "从左到右：哈基米写实、哈基米二次元、小克写实、小克二次元。")

二次元立绘来自开源项目 [shuaizenge/ai-girls](https://github.com/shuaizenge/ai-girls)，原作者是 [@zipzippipe](https://www.pixiv.net/artworks/148186519)。

## 侧边栏面板

面板叫"人设控制台"（`persona-hub`），是一个 Antigravity 的 sidecar 插件，挂在右侧辅助栏里，常驻不遮挡对话。从上到下是这几块：

- **当前激活人设**：头像、名字、一句话性格介绍，下面是形象预览，写实和二次元一键切换。
- **建议提问**：几句跟人设口吻搭配的开场白，点一下就能用。
- **已安装人设图鉴**：所有装好的人设卡片，没激活的也能点开预览形象。
- **会话与调用统计**：当前模型档位、这段对话的步数和提问轮数、今天一共跑了多少步、生了几张图，最底下一根上下文负载条。

![两张人设控制台面板截图并排：左边哈基米激活，右边小克激活，各自显示形象预览、建议提问、人设图鉴和会话统计](/assets/img/posts/antigravity-persona-hub/panels.webp "左：哈基米在岗。右：换成小克。")

面板还做了两种容错：一个人设都没开，就显示"默认助手模式"卡片；同时开了好几个，顶部会提示冲突。

## 加新角色，不用改代码

面板每 5 秒扫一次插件目录，凡是名字以 `-persona` 结尾的目录都会自动加进图鉴。想加一位新拍档，比如 `deepseek-persona`，只要准备好这几样：

1. `plugin.json` 和 `rules/AGENTS.md`；
2. `assets/` 里放一张方形头像 `logo.jpg`，一张写实立绘 `realistic.jpg`，有二次元立绘的话再放一张 `anime.jpg`。

放进去之后等几秒，面板上就有了。

## 安装

把三个插件目录复制到 Antigravity 的全局插件目录：

```bash
cp -r person/hajimi-persona ~/.gemini/config/plugins/hajimi-persona
cp -r person/xiaoke-persona ~/.gemini/config/plugins/xiaoke-persona
cp -r person/persona-hub    ~/.gemini/config/plugins/persona-hub
```

Windows 用 `Copy-Item` 复制到 `%USERPROFILE%\.gemini\config\plugins\` 下，命令在仓库 README 里。

然后在左侧栏 **Customizations → Plugins** 里打开想用的人设，建议一次只开一个。在对话里点一下或者发送 `sidecar://persona-hub/hub/`，右边就会展开控制台。

写完这个，又把整套东西搬到了 DeepSeek Harness 上，还多招了一位拍档，见下一篇：[DSH 人设控制台](/posts/dsh-persona-hub/)。

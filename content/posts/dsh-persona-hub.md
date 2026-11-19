---
title: "DSH 人设控制台：哈基米和小克搬进 DeepSeek Harness，顺便招了条小鲸鱼"
date: 2026-11-19
categories: ["AI 工具"]
tags: ["DeepSeek Harness", "人设", "造轮子"]
description: "上一篇在 Antigravity 里写的人设控制台，这次搬到了 DeepSeek Harness 上，改成原生插件：多了一位自称“本鱼”的鲸鱼娘，面板接上了 token 级的上下文统计，还内置了一个用人话管理人设的 Skill。"
cover: /assets/img/bg6.jpg
---

[上一篇](/posts/antigravity-persona-hub/)在 Antigravity 里给哈基米和小克做了一块侧边栏。同样的东西，DeepSeek Harness（下面简称 DSH）上也想要一份；而且 Gemini 和 Claude 都有了拍档，DeepSeek 自己没有，说不过去。

于是重写了一遍，改成 DSH 的原生插件：[dsh-persona-hub](https://github.com/liqiming-whu/dsh-persona-hub)，TypeScript 写的，现在是 1.5.6 版。

## 新拍档：小鲸鱼

**小鲸鱼**，DeepSeek 鲸鱼娘，形象来自 DeepSeek 那条蓝鲸，自称"本鱼"。沉静、擅长深度推理，有点得意自己的脑瓜，偶尔冒个泡偷个小懒。遇到难题就说"哼哼，这题有点深度，看本鱼潜下去摸清底细"；看到一段循环写得太费，会说"数据量大了以后肯定要呛水"。

和哈基米、小克一样，写代码的时候她正经说话，"本鱼"只在开头结尾冒个头。

![小鲸鱼两张形象并排：左边写实形象，深墨蓝长发，身后是全息蓝鲸和发光水母的深海研究室；右边二次元形象，海蓝长发、鲸鳍耳，穿蓝白女仆装](/assets/img/posts/dsh-persona-hub/xiaojingyu-dual.webp "小鲸鱼：写实深海研究员（默认）和二次元鲸鱼娘女仆。")

插件里内置三位：哈基米、小克、小鲸鱼。每位都有写实和二次元两套形象，二次元立绘同样来自 [shuaizenge/ai-girls](https://github.com/shuaizenge/ai-girls)。

## 面板：左边快捷切换，右边常驻

DSH 的插件可以同时往几个地方挂界面，所以这一版分成了三处：

- **左侧栏**：底部一张"当前启用角色"卡片，最多 4 个快捷人设，点一下就换人。
- **右侧栏**：完整的控制台面板，作为独立标签页常驻，和对话区并排，能拖宽，也能全屏。
- **设置页**：能看到实时注入的完整 System Prompt，人设到底给模型塞了什么，一目了然。

![人设控制台右栏面板：小鲸鱼正在使用，下面是形象预览、三句建议提问、三张人设卡片的图鉴，最底下是会话统计和上下文负载条](/assets/img/posts/dsh-persona-hub/panel-xiaojingyu.webp#small "小鲸鱼在岗时的完整面板。")

面板内容和 Antigravity 版大体一样：当前人设、双形象切换、建议提问、人设图鉴、会话统计。不同的是：

- 图鉴里每张卡片都带"启用"按钮，不用再去设置里翻开关；右上角还有一个"切回标准助手"。
- 统计换成了 DSH 自己的数据，上下文负载能精确到 token。截图里那段对话已经 153 轮、693.6k / 1048.6k tokens，用掉了 66%，可见我跟本鱼聊了多久。
- 最底下多了一枚"时间来源"徽标，后面细说。

点开没启用的人设卡片，可以先预览形象，不会真的切换：

![两张面板截图并排：左边预览哈基米，右边预览小克，都显示"预览中（未启用）"，当前在用的仍是小鲸鱼](/assets/img/posts/dsh-persona-hub/panels-preview.webp "预览哈基米（左）和小克（右），实际在岗的还是小鲸鱼。")

## 时间：不硬依赖环境上下文插件

人设里有不少跟日期有关的内容，比如纪念日、"今天几号"，模型得一直能看到准确的时间才行。

我另有一个 [dsh-environment-context](https://github.com/liqiming-whu/dsh-environment-context) 插件专门往对话里注入时间、天气这些环境信息。可人设控制台不能硬依赖它，没装的人照样得有时间可用。所以控制台自带一段时间提示词，每 10 秒探测一次环境上下文插件的状态：

| 场景 | 谁来注入时间 |
| :--- | :--- |
| 环境上下文在线，且正在注入时间 | 环境上下文，控制台保持安静，不重复注入 |
| 环境上下文在线，但关掉了时间注入 | 控制台兜底 |
| 环境上下文没装或已停用 | 控制台兜底 |
| 探测失败 | 控制台兜底，宁可重复也不丢时间 |

设置里可以切换三档：`auto`（环境上下文优先）、`always`（始终自己注入）、`off`（关闭）。时间注入和人设开关是分开的，就算把人设停掉、切回标准助手，时间照样注入。

面板底部那枚徽标，显示的就是现在由谁在提供时间。

## 人设管理 Skill

插件里还内置了一个 `persona-assistant` Skill，加载之后，可以直接用人话管理人设：

- **创建**：按 DSH 的标准结构生成 `plugin.json`、`AGENTS.md`、头像和参考图。
- **导入**：从本地目录或 GitHub 仓库导入，有 `gh` 就用 `gh repo clone`，没有就退回 `git clone`，还能认出凭据缺失的常见报错。
- **移植**：把 Antigravity 版的人设改写成 DSH 版。原来写死的图片绝对路径换成 `{{REALISTIC_IMAGE_PATH}}`、`{{SECONDARY_IMAGE_PATH}}` 占位符，注入时再解析成本机路径；原来点名某个生图子智能体的写法，改成"当前会话可用的生图能力"这类中性说法。
- **验证和删除**：给出可以直接跑的检查命令，看有没有残留的占位符、硬编码路径、缺失的图片，再给出安全的删除步骤。

上一篇那种 Antigravity 版的人设，交给它就能搬到 DSH 上来。

## 加新角色

在 `~/.dsh/personas/` 下新建一个以 `-persona` 结尾的目录，放进 `plugin.json`、`AGENTS.md` 和头像、立绘，再在设置页打开"自动扫描外部人设插件目录"，就会出现在图鉴里。不想手动建，就让 `persona-assistant` 代劳。

## 安装

推荐直接装 Release 里打好的包，不用在本机构建：

```bash
dsh plugin --profile desktop add https://github.com/liqiming-whu/dsh-persona-hub/releases/download/v1.5.6/dsh-persona-hub-1.5.6.tgz --trust-lockfile
```

桌面应用的 profile 叫 `desktop`，`dsh web` 用的是 `web`。装好后重启 DSH，再硬刷新一下页面；之后切换人设、改开关都是即时生效。

目前面向 DSH 0.2.x。想让回复里的 `dsh-ui` 卡片也渲染出来，可以再装一个 [dsh-genui](https://github.com/omdsh-dev/dsh-genui)。

从 Antigravity 到 DSH，Gemini、Claude、DeepSeek 三家总算都有拍档了。下一个轮到谁，看哪家先来招惹我。

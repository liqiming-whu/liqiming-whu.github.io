---
title: "comfyui-skills：教 AI 搭 ComfyUI 工作流、写 Krea 2 提示词"
date: 2026-11-06
categories: ["AI 工具"]
tags: ["ComfyUI", "Agent Skills", "提示词"]
description: "玩 ComfyUI 最烦的不是出图，是连节点、找模型、调提示词。于是把这些经验整理成 6 个 Skill：搭工作流、测性能、写 Krea 2 提示词、做 LoRA 训练集，还有两个专画巨构场景的。"
cover: /assets/img/bg10.jpg
---

![ComfyUI Skills 介绍卡片：发光的节点连成一个 C 字，右边是几张示例出图](/assets/img/posts/comfyui-skills/intro-card.webp)

玩 ComfyUI 的人大概都有同感：出图本身很快，慢的是出图之前。新模型出来，要找对 checkpoint、文本编码器和 VAE，再照着别人的截图一根一根连节点；连好了，提示词又得从头摸索，同一段话换个模型，效果天差地别。

这些活我反复干了很多遍，后来干脆把经验整理成 Skill，让 Codex 这类编程 Agent 来干，这就是 [comfyui-skills](https://github.com/liqiming-whu/comfyui-skills)。9 月中旬公开，现在有 6 个 Skill、48 份工作流。

## 六个 Skill

| Skill | 干什么 |
| --- | --- |
| `comfyui-workflow` | 创建、修改、迁移和校验 ComfyUI 工作流 |
| `comfyui-performance-monitor` | 记录工作流耗时，以及显卡、软件版本、缓存等测试条件 |
| `krea2-prompt-engineering` | 写和调 Krea 2 的提示词 |
| `krea2-lora-training` | 做 LoRA 训练集、检查 caption、评估检查点 |
| `krea2-megastructure-prompts` | 巨构、巨兽、超尺度场景提示词 |
| `moss-image-megastructure-prompts` | 给 MOSS-Image 写巨构场景的 Caption 或 Layout |

每个 Skill 是一个独立目录，用哪个装哪个。

## 搭工作流：comfyui-workflow

这个 Skill 让 Agent 能直接产出可以拖进 ComfyUI 画布的工作流 JSON，也能改现有的、把旧工作流迁到新模型上。

模板目录里放了 48 份工作流：36 份覆盖 SD、SDXL、FLUX、Wan、LTXV、混元视频、音频、3D 这些常见任务，另外 12 份是迁进来的新模型示例，包括 Krea 2 的 RAW 和 Turbo、4K 放大、训练数据生成、Flux2-klein、Qwen-Image 2.1 编辑和 Z-Image。

两条我觉得最重要的规矩：

- **以本机的 ComfyUI 为准。** 节点的输入参数会随版本变，Agent 改工作流前要先查目标实例的 `/object_info`，而不是凭记忆写。
- **只做 UI 工作流。** 需要 API 格式时，在 ComfyUI 里打开、跑通，再用"导出（API）"导出，不让 Agent 自己手搓 API JSON。

改完还可以用自带的脚本做一遍结构检查：

```bash
python skills/comfyui-workflow/scripts/workflow_tool.py validate workflow.json
```

这个 Skill 是在 [LingyiChen-AI/comfyui-workflow-skill](https://github.com/LingyiChen-AI/comfyui-workflow-skill) 的基础上改的，补上了 Krea 2、FLUX.2 klein、Qwen Edit、Z-Image 这些新模型的资料，也写了一份模型推荐：截至 9 月，文生图默认 Krea 2，图像编辑看 FLUX.2 klein 和 Qwen-Image 2.1，显存紧张用 Z-Image，视频用 MiniMax H3。

## 写提示词：krea2-prompt-engineering

这是我花时间最多的一个。Krea 2 和 SD 时代的模型很不一样，它更像在读一段画面描述，而不是在解析一张 tag 权重表。所以与其写：

```text
masterpiece, best quality, young woman, slim, realistic, 8k
```

不如像跟人描述画面那样写：

```text
A young adult woman stands facing the camera in a softly lit hotel corridor. Her figure is slender overall...
```

做了不少对照实验之后，我把各种调法的效果排了个序：

| 优先级 | 调什么 | 说明 |
| --- | --- | --- |
| 1 | 语序与层级 | 最想要的东西放在前面、放在主句里 |
| 2 | 一次只改一处 | 改两处就说不清是哪处起的作用 |
| 3 | 承载句 | 比如描述服装的那一句，常常决定局部形态能不能画出来 |
| 4 | 具体用词 | 有用，但语序没摆对时换词基本看不出差别 |
| 5 | 换个说法再说一遍 | 能加强，但不一定加得均匀 |
| 6 | `(word:1.3)` 括号权重 | 对 Krea 2 基本不像以前那样起作用 |

语序带来的差别，比后面几项大一个数量级。

另外还收了一套东方仙宫场景的提示词引擎，仙宫、瑶池、南天门、月宫这类场景，从景别、尺度到人物造型都有现成的组装方法。素材来自 B 站的 **是古手梨花sama**，感谢作者分享。

## 炼 LoRA：krea2-lora-training

训练 LoRA，图片和 caption 的质量决定一半。这个 Skill 带了一个只读的检查脚本，会逐张核对：

- 图片和 caption 是否一一对应，图片能不能正常解码；
- caption 是不是 UTF-8，触发词有没有写对、写全；
- caption 里写的画幅比例和图片实际比例对不对得上；
- 左右方向是否写反了（镜像翻转过的图特别容易出错）。

```bash
python scripts/lint_captions.py "<数据集目录>" --trigger "<触发词>" --strict
```

练出来以后，还可以通过 ComfyUI 的 API 批量跑固定的测试提示词，对比不同步数的检查点、加不加触发词的差别，比手动一张张试省事得多。当然，检查全部通过也只能说明数据集没有低级错误，人物像不像、练得好不好，还是得看图。

## 画巨构

最后两个是专门画巨构场景的：倒悬的城市、比山还高的塔、悬在云里的建筑。

- `krea2-megastructure-prompts` 整理自 B 站作者 [黑鹤001](https://space.bilibili.com/515231056) 的分享，我只做了接入 Codex 的适配，创作方法和 30 条示例提示词都保持原样。
- `moss-image-megastructure-prompts` 是给 MOSS-Image 用的。普通场景写一段自然语言 Caption 就够了；遇到"两座塔尖相对、中间只留一条缝"这种需要精确位置的构图，就改写成带坐标的 Layout。

画巨构的诀窍其实就一个：找一个尺度参照物，比如一只热气球、一艘船，交代它和巨构的大小关系，大的感觉就出来了。

## 安装

Linux / macOS：

```bash
git clone https://github.com/liqiming-whu/comfyui-skills.git
mkdir -p ~/.codex/skills
cp -r comfyui-skills/skills/comfyui-workflow ~/.codex/skills/
```

Windows（PowerShell）：

```powershell
git clone https://github.com/liqiming-whu/comfyui-skills.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse comfyui-skills\skills\comfyui-workflow "$env:USERPROFILE\.codex\skills\"
```

需要哪个 Skill 就复制哪个目录，记得复制整个目录，不要只拷 `SKILL.md`。装好后开个新会话就能用。

顺带一提，分辨率按索引轮换的小节点我单独放在了 [comfyui-resolution-by-index](https://github.com/liqiming-whu/comfyui-resolution-by-index)，批量出不同尺寸的图时很方便。

## 彩蛋

![网络梗图：几位科技公司掌门人穿着侍者制服，站在一家西式餐厅里](/assets/img/posts/comfyui-skills/butlers.webp "图文无关，网上看到的梗图，单纯觉得有意思。")

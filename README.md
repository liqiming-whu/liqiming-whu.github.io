# Venusleeyous

一个不太聪明的年轻人的博客：生信、Python、Linux，以及折腾它们时踩过的坑。

线上地址：<https://blog.venuslee.top>（GitHub Pages 镜像：<https://liqiming-whu.github.io>）

## 写一篇新文章

```bash
python build.py new my-new-post        # 生成 content/posts/my-new-post.md
```

打开这个文件，改好开头的信息，正文用 Markdown 写：

```yaml
---
title: 文章标题
date: 2026-11-01
categories: [python]        # 第一个分类会显示在列表上；可选：生信、python、终端与环境、AI 工具、AI 排行榜、没事瞎写的
tags: [pandas, 造轮子]       # 写具体的工具或主题；新标签记得加到 site.yaml 的 tag_groups 里归类
# source: 转载              # 转载的文章加上这一行，会显示一个小标记
description: 一句话介绍，显示在卡片和搜索结果里
cover: /assets/img/bg5.jpg  # 封面图，放在 public/assets/img/
draft: true                 # 写完删掉这一行就会发布
---
```

写完推送到 `main`，GitHub Actions 会自动构建并发布，首页、归档、分类、标签、搜索和 RSS 都会自动更新。

AI 排行榜文章使用 `categories: ["AI 排行榜"]`，会自动收录到导航中的「AI 排行榜」栏目，按日期从新到旧排列。

### 可以用的特殊写法

- 代码块：照常用 ```` ```python ```` 这样的写法，会自动高亮并带「复制」按钮。
- `~~删除线~~`
- 选项卡（比如同一个命令的 GitHub 版和 Gitee 版）：

  ```html
  <div class="tabs">
  <div class="tab-item" data-label="通过 git 安装">

  这里照常写 Markdown

  </div>
  <div class="tab-item" data-label="通过 gitee 安装">

  另一个选项

  </div>
  </div>
  ```

## 在文章里加图片

图片统一放在 `public/assets/img/posts/<文章 slug>/` 下，一篇文章一个文件夹。用下面的命令导入，会自动压缩成 WebP（最宽 1600px）、放进对应文件夹，并打印出 Markdown 写法：

```bash
pip install pillow                       # 只在本地导入图片时需要
python build.py img ~/Downloads/梗图.png my-post boss-meme
```

然后把打印出来的那行贴进文章：

```markdown
![图片描述，给读屏软件和加载失败时看](/assets/img/posts/my-post/boss-meme.webp "图注，显示在图片下方，可省略")
```

单独占一段的图片会显示成带图注的居中大图，点击可以看原图。手机截图、界面截图这类不需要占满整栏的，在路径末尾加 `#small`，会显示成窄图：

```markdown
![插件界面](/assets/img/posts/my-post/screenshot.webp#small "图注")
```

## 改网站上的文字

首页介绍、各页面标题、分类说明和颜色、标签分组、友链等都在 `site.yaml` 里，「关于」页正文在 `content/about.md`，「项目」页的数据在 `content/projects.yaml`（新项目照格式加一条，`since`/`updated` 填首次和最近提交的年月）。页面结构在 `templates/`，样式和脚本在 `public/assets/`。

## 本地预览

```bash
pip install -r requirements.txt
python build.py serve       # 打开 http://localhost:8000
```

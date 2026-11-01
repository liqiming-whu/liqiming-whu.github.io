---
title: "大幅度提升终端使用体验——zsh安装与配置"
date: 2021-04-01
categories: ["终端与环境"]
tags: ["zsh", "oh-my-zsh"]
description: "如果你没用过zsh，那么你需要这篇文章，如果你没用过oh-my-zsh，那你更需要这篇文章。如果你不用oh-my-zsh，那没事了。"
cover: /assets/img/bg6.jpg
---

## 学习Linux从zsh的安装与配置开始

### 1.安装zsh

```bash
sudo apt install zsh  # 以ubuntu为例
```

或者[通过源码安装](http://zsh.sourceforge.net/Arc/source.html)

如果没有root权限，通过源码安装，下载解压之后：

- 首先配置zsh，自定义安装路径

`./configure --prefix=$HOME/.local`

- 然后编译

`make -j4`

- 检查编译是否成功

`make check`

- 如果没有编译错误，则安装zsh

`make install -j4`

### 2.将zsh设置为默认shell

如果使用root权限安装的zsh，直接终端运行`chsh -s $(which zsh)`即可。

如果没有root权限，通过源码安装zsh的话，则解决方法是在每次打开终端时执行`exec <zsh-path>`来替代当前的shell。在文件`.bash_profile`中加入：

`[ -f $HOME/.local/bin/zsh ] && exec $HOME/.local/bin/zsh -l`

如果上述两种方法都不能修改默认shell，安装 oh-my-zsh，安装时会自动切换shell成zsh。

### 3.安装oh-my-zsh

ArchLinux用户直接`yay -S oh-my-zsh-git`，然后`cp /usr/share/oh-my-zsh/zshrc ~/.zshrc`就完了。

<div class="tabs">
<div class="tab-item" data-label="通过curl安装">

`sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`

</div>
<div class="tab-item" data-label="通过wget安装">

`sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`

</div>
</div>

如果上述方法出现问题，可以按照下面的方法进行：

<div class="tabs">
<div class="tab-item" data-label="通过git安装">

```bash
cd ~ && \
git clone https://github.com/ohmyzsh/ohmyzsh.git && \
mv ohmyzsh .oh-my-zsh && \
cp .oh-my-zsh/templates/zshrc.zsh-template ~/.zshrc
```

</div>
<div class="tab-item" data-label="通过gitee安装">

```
cd ~ && \
git clone https://gitee.com/lu_x/ohmyzsh.git && \
mv ohmyzsh .oh-my-zsh && \
cp .oh-my-zsh/templates/zshrc.zsh-template ~/.zshrc
```

</div>
</div>

### 4.配置oh-my-zsh

vim .zshrc，切换ZSH_THEME，可以在[这里](https://github.com/ohmyzsh/ohmyzsh/wiki/Themes)预览。

想要隐藏用户名，`export DEFAULT_USER="<user-name>"`

### 5.插件配置

在.zshrc中找到plugins=(git)，其中加入以下插件：

```bash
plugins=(
  git
  extract  # 一个命令 `x` 解压全部压缩文件
  z  # cd的加强版，到达任意到过的位置，模糊匹配
  rand-quote  # 随机名言，命令quote
  gitignore  # 提供一条 gi 命令，用来查询 gitignore 模板 gi python > .gitignore
  cp  # 提供一个 cpv 命令，这个命令使用 rsync 实现带进度条的复制功能
  vi-mode  # vim输入模式
  safe-paste  # 往 zsh 粘贴脚本时，它不会被立刻运行
  colored-man-pages  # 给你带颜色的 man 命令
  zsh-syntax-highlighting  # 指令高亮
  zsh-autosuggestions  # 命令自动提示，方向键补全
)
```

其中插件zsh-syntax-highlighting和zsh-autosuggestions需要单独下载，方法如下：

<div class="tabs">
<div class="tab-item" data-label="通过git安装">

```bash
# 下载zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
# 下载zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-autosuggestions.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

</div>
<div class="tab-item" data-label="通过gitee安装">

```bash
# 下载zsh-syntax-highlighting
git clone https://gitee.com/gulei666/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
# 下载zsh-autosuggestions
git clone https://gitee.com/githubClone/zsh-autosuggestions.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

</div>
</div>

### 6.主题配置

修改后的主题文件已经保存在github仓库,可直接下载使用：

下载`mytheme.zsh-theme.txt`，重命名`mytheme.zsh-theme`于`~/.oh-my-zsh/themes`，在`~/.zshrc`中声明`ZSH_THEME="mytheme"`,然后`source ~/.zshrc`

<div class="tabs">
<div class="tab-item" data-label="通过git安装">

```bash
git clone https://github.com/liqiming-whu/memorandum && \
cp memorandum/mytheme.zsh-theme.txt ~/.oh-my-zsh/themes/mytheme.zsh-theme && \
vim ~/.zshrc && \
source ~/.zshrc
```

</div>
<div class="tab-item" data-label="通过gitee安装">

```
git clone https://gitee.com/liqiming_whu/memorandum && \
cp memorandum/mytheme.zsh-theme.txt ~/.oh-my-zsh/themes/mytheme.zsh-theme && \
vim ~/.zshrc && \
source ~/.zshrc
```

</div>
</div>

---

当然你也可以自行配置主题，以下是我自己的配置过程：

### 7.自定义主题

默认的主题robbyrussel不显示用户名，自定义主题可以修改使其显示用户名

终端输入：

```bash
cd ~/.oh-my-zsh/themes
vim robbyrussell.zsh-theme
```

可以看到：

```bash
local ret_status="%(?:%{$fg_bold[green]%}➜ :%{$fg_bold[red]%}➜ )"
PROMPT='${ret_status} %{$fg[cyan]%}%c%{$reset_color%} $(git_prompt_info)'

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg_bold[blue]%}git:(%{$fg[red]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%} "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[blue]%}) %{$fg[yellow]%}✗"
ZSH_THEME_GIT_PROMPT_CLEAN="%{$fg[blue]%})"
```

PROMPT就是设置显示的用户名  
​由于oh_my_zsh时常会有版本更新，为了避免我们修改的跟更新的版本有冲突，建议不要修改robbyrussell.zsh-theme，而是将其拷贝出来，命名为自己的主题文件，比如叫做mytheme.zsh-theme，然后只对mytheme-theme进行修改。

```bash
cp robbyrussell.zsh-theme mytheme.zsh-theme
```

修改后将 ~/.zshrc 中的`ZSH_THEME="robbyrussell"`改为`ZSH_THEME="mytheme"`

#### 参考设置

```bash
PROMPT='%{$fg[green]%}%m@%{$fg[magenta]%}%(?..%?%1v)%n:%{$reset_color%}%{$fg[cyan]%}%~#'
```

```bash
PROMPT='%{$fg_bold[red]%}-> %{$fg_bold[green]%}%p%{$fg[cyan]%}%d %{$fg_bold[blue]%}$(git_prompt_info)%{$fg_bold[blue]%}% %{$reset_color%}~#:'
```

```bash
PROMPT='%{$fg_bold[red]%}-> %{$fg_bold[green]%}%p%{$fg[cyan]%}%d %{$fg_bold[blue]%}$(git_prompt_info)%{$fg_bold[blue]%}% %{$fg[magenta]%}%(?..%?%1v)%{$reset_color%}~#: '
```

```bash
PROMPT='%{$fg_bold[red]%}-> %{$fg_bold[magenta]%}%n%{$fg_bold[cyan]%}@%{$fg[green]%}%m %{$fg_bold[green]%}%p%{$fg[cyan]%}%~ %{$fg_bold[blue]%}$(git_prompt_info)%{$fg_bold[blue]%}% %{$fg[magenta]%}%(?..%?%1v)%{$fg_bold[blue]%}? %{$fg[yellow]%}# '
```

```bash
%T 系统时间（时：分)
%* 系统时间（时：分：秒）
%D 系统日期（年-月-日）
%n 你的用户名
%B - %b 开始到结束使用粗体打印
%U - %u 开始到结束使用下划线打印
%d 你目前的工作目录
%~ 你目前的工作目录相对于～的相对路径
%M 计算机的主机名
%m 计算机的主机名（在第一个句号之前截断）
%l 你当前的tty
%n 登录名
```

#### 修改mytheme.zsh-theme文件

修改这一行：

`PROMPT='${ret_status}%{$fg[magenta]%}%n@%{$fg[green]%}%m %{$fg[cyan]%}%c%{$reset_color%} $(git_prompt_info)'`

文件全部内容：

```bash
local ret_status="%(?:%{$fg_bold[green]%}➜ :%{$fg_bold[red]%}➜ )"
PROMPT='${ret_status}%{$fg[magenta]%}%n@%{$fg[green]%}%m %{$fg[cyan]%}%c%{$reset_color%} $(git_prompt_info)'
ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg_bold[blue]%}git:(%{$fg[red]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%} "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[blue]%}) %{$fg[yellow]%}✗"
ZSH_THEME_GIT_PROMPT_CLEAN="%{$fg[blue]%})"
```

### 8.随机主题

在 `~/.zshrc` 文件中设置主题为 `random` 即可开启随机主题，每次打开新的终端的时候，zsh 都会随机使用一个主题。

`ZSH_THEME="random"`

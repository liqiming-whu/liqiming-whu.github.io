---
title: "配置你的vim，让它成为能用的编辑器"
date: 2021-03-31
categories: ["linux"]
tags: ["原创"]
description: "很多服务器上的至今仍然装着vim7，没有基本的配置，vim是很难用的，经常会遇到空格和tab混用的问题。使用vim，需要先从配置开始。"
cover: /assets/img/bg2.jpg
---

## 学习Linux，从vim配置开始：

~~不会真有人不配置就用vim吧，不会吧~~

### 1.使用vim-plug管理vim插件

把vim-plug安装在~/.vim/autoload/

```bash
curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

由于github处于骑墙状态有时候没法连接，所以：

<div class="tabs">
<div class="tab-item" data-label="通过git安装">

```bash
git clone https://github.com/junegunn/vim-plug && \
mkdir -p ~/.vim/autoload && \
cp vim-plug/plug.vim ~/.vim/autoload
```

</div>
<div class="tab-item" data-label="通过gitee安装">

```bash
git clone https://gitee.com/chenxinliang123/vim-plug && \
mkdir -p ~/.vim/autoload && \
cp vim-plug/plug.vim ~/.vim/autoload
```

</div>
</div>

### 2.重命名vimrc.txt为.vimrc于~/

这里可以clone我的配置：

<div class="tabs">
<div class="tab-item" data-label="通过git">

```bash
git clone https://github.com/liqiming-whu/memorandum && \
cp memorandum/vimrc.txt ~/.vimrc
```

</div>
<div class="tab-item" data-label="通过gitee">

```bash
git clone https://gitee.com/liqiming_whu/memorandum && \
cp memorandum/vimrc.txt ~/.vimrc
```

</div>
</div>

### 3.安装插件

```bash
# vim:
:PlugStatus # 查看插件信息
:PlugInstall # 安装插件，首先在.vimrc中声明
:PlugClean # 卸载插件，首先在.vimrc中删除
:PlugUpgrade # 升级
```

### 4.安装依赖

```bash
sudo apt install universal-ctags nodejs clangd
sudo pip install flake8
```

### 5.安装yarn

去yarn官网查看[安装说明](https://yarn.bootcss.com/docs/install/#debian-stable)

```bash
# archlinux:
sudo pacman -S yarn
# ubuntu:
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update && sudo apt install yarn
# 如果报错，执行以下命令后重新安装(wsl-ubuntu18.04好像会报错)
sudo apt remove cmdtest
sudo apt remove gpg
sudo apt install gnupg1
```

### 6.安装主题配色

我们要把主题配色复制到指定位置才能生效。

```bash
mkdir ~/.vim/colors
cp ~/.vim/plugged/onedark.vim/colors/onedark.vim ~/.vim/colors
cp ~/.vim/plugged/onedark.vim/autoload/onedark.vim ~/.vim/autoload
```

### 7.复制.vimrc, .vim, .config至/root

为了让root也可以使用vim配置，直接粗暴的复制过去就完了。

```bash
sudo cp ~/.vimrc  /root
sudo cp -r ~/.vim  /root
sudo cp -r ~/.config  /root
```

---

### 8.我的.vimrc文件

需要vim > 8.0才能用

```
" vim plug插件管理
call plug#begin('~/.vim/plugged')

Plug 'joshdick/onedark.vim' " 配色方案
colorscheme onedark
" 安装:
" mkdir ~/.vim/colors
" cp ~/.vim/plugged/onedark.vim/colors/onedark.vim ~/.vim/colors
" cp ~/.vim/plugged/onedark.vim/autoload/onedark.vim ~/.vim/autoload

Plug 'vim-airline/vim-airline' " 状态栏
Plug 'vim-airline/vim-airline-themes' " 状态栏主题
let g:airline_theme='onedark'

" Plug 'Yggdroot/indentLine' " 缩进标线,开启后不方便复制
" let g:indentLine_color_term = 239
" let g:indentLine_char_list = ['|', '¦', '┆', '┊']

Plug 'preservim/nerdtree' " 文件管理器 F2
" autocmd vimenter * NERDTree " 打开文件自动打开HERDTree,建议关闭
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) &&
    \ !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | endif
map <F2> :NERDTreeToggle<CR>
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") &&
    \ b:NERDTree.isTabTree()) | q | endif
" 上面我们设置了自动打开NERDTree，(直接输入vim会打开NERDTree)，打开一个目录也
" 会打开NERDTree，当文件都关闭只有NERDTree时自动退出。
" 设置快捷键F2来自由切换打开或者关闭NERDTree。
Plug 'Yggdroot/LeaderF', { 'do': './install.sh' } " 需要安装universal-ctags
noremap <F3> :LeaderfFunction!<CR>
let g:Lf_HideHelp = 1
let g:Lf_UseCache = 0
let g:Lf_UseVersionControlTool = 0
let g:Lf_IgnoreCurrentBufferName = 1
let g:Lf_WindowPosition = 'popup' " vim >=8.1
let g:Lf_WindowPosition = 'popup' " vim >=8.1
let g:Lf_PreviewResult = {'Function':0, 'BufTag': 0}

Plug 'neoclide/coc.nvim', {'branch': 'release'} " 补全插件 vim > 8.1
let g:coc_global_extensions = ['coc-json', 'coc-clangd', 'coc-cmake',
    \ 'coc-css', 'coc-java', 'coc-python', 'coc-snippets', 'coc-xml',
    \ 'coc-markdownlint','coc-highlight']
" :CocInstall coc-json coc-css 安装插件
" :CocUninstall coc-css 卸载插件
" :CocList extensions 插件列表

Plug 'hrp/EnhancedCommentify' " 注释，快捷键<leader>x, <leader>c
let g:EnhCommentifyRespectIndent = 'Yes'
let g:EnhCommentifyPretty = 'Yes'

Plug 'luochen1990/rainbow' " 彩虹括号
let g:rainbow_active = 1

Plug 'Raimondi/delimitMate' " 补全括号
au FileType python let b:delimitMate_nesting_quotes = ['"']

Plug 'docunext/closetag.vim' " 补全 HTML/XML 标签
let g:closetag_html_style=1

" Plug 'dense-analysis/ale' " 代码检测 vim > 8.0
" 需要代码检测工具的支持：pip install flake8
" let &runtimepath.=',~/.vim/plugged/ale'
" let g:ale_sign_column_always = 0 " 一般需要实时检查，默认关闭
" let g:ale_lint_on_save = 1 " save file auto check
" let g:ale_lint_on_text_changed = 0 " for ale_lint_on_save = 1
" let g:ale_lint_on_enter = 0 " for ale_lint_on_save = 1
" map <F5> :ALEToggle \| echo 'g:ale_enabled =' g:ale_enabled<CR>
" F5开启/关闭静态检测
" let g:ale_echo_msg_error_str = 'Error'
" let g:ale_echo_msg_warning_str = 'Warning'
" let g:ale_echo_msg_format = '[%linter%] %s [%severity%]'

call plug#end()

filetype plugin indent on
syntax enable
syntax on

" When vimrc is edited, reload it
autocmd! BufWritePost ~/.vimrc source ~/.vimrc

" 首先设置 mapleader，后面键盘映射随时要用
" 基本上所有自定义的快捷键都以这个字符打头，比如映射`,w`为`:w`
let mapleader = ","
let g:mapleader = ","

" 不兼容 Vi，最大限度使用新特性
set nocompatible

" 写入文件时，不做备份
set nobackup
set nowritebackup

" 不用交换文件
set noswapfile

" 保存文件的快捷键
nmap <leader>w :w!<CR>
nmap <leader>q :q!<CR>

" 移除 Windows 文件结尾的 `^M`
noremap <leader>m :%s/<C-V><C-M>//ge<CR>

" 重新打开文件时，恢复上一次游标位置
set viewoptions=cursor  " 只记住游标
au BufWinLeave ?* mkview
au VimEnter ?* silent loadview

" 检测文件编码时，优先考虑 UTF-8
set fileencodings=utf-8,gb2312,gb18030,gbk,ucs-bom,cp936,big5,latin1
set enc=utf8
set fencs=utf8,gbk,gb2312,gb18030
" 不同平台，设置不同的行尾符，即 EOL
" 注意：在 Mac 平台，也是 unix 优先；自 OS X 始，行尾符与 Unix 一致，
"      都是 `\n` 而不是 `\r`
if has("win32")
    set fileformats=dos,unix,mac
else
    set fileformats=unix,mac,dos
endif

" 在断行、合并(join)行时，针对多字节字符（比如中文）的优化处理
set formatoptions+=mM

" 采用 C 风格的缩进，适用于大多数语言
" 细节调整见下面的 `cinoptions`
" 你也可以尝试 smartindent 和 autoindent
set cindent

" 细节调整，主要为了适应 Google C++ Style
" t0: 函数返回类型声明不缩进
" g0: C++ "public:" 等声明缩进一个字符
" h1: C++ "public:" 等声明后面的语句缩进一个字符
" N-s: C++ namespace 里不缩进
" j1: 合理的缩进 Java 或 C++ 的匿名函数，应该也适用于 JS
set cinoptions=t0,g1,h1,N-s,j1

" 让制表符智能一些
set smarttab
" 先设置缺省情况，然后根据不同文件类型再次重新设置
set expandtab | set tabstop=4 | set shiftwidth=4  " Python, CSS, etc.

" 对 C/C++ 等，制表符和缩进都是两个空格
au FileType c,cpp,html,htmldjango,lua,javascript,nsis
    \ set expandtab | set tabstop=2 | set shiftwidth=2

" Makefile 必须保留制表符，且习惯上占八个空格
au FileType make set noexpandtab | set tabstop=8 | set shiftwidth=8

" 对 C/C++/Python/Vim 80列限制
au FileType c,cpp,python,vim set textwidth=79 | set colorcolumn=80
" 设定了宽度限制，画一条竖线以警示

" 通常代码不需折行，前面有些语言设置了宽度限制就更不需要了。
" 实际操作下来，纯文本、Markdown、XML 等比较需要折行，因为它们常常一行太长了
au FileType text,markdown,html,xml set wrap
" 折行时，以单词为界，以免切断单词
set linebreak
" 折行后的后续行，使用与第一行相同的缩进
set breakindent  " vim > 8.0

" 即使在终端，也尽量启用鼠标(设置此项后不能右键粘贴，所以注释掉了）
" if has("mouse") | set mouse=a | endif

" 显示输入中的命令，对 gqq/gcc 这种多个字符的命令特别有用
set showcmd
" 下面几个不解释，自行查看帮助
set scrolloff=7
set wildmenu
set wildmode="list:longest"
set ruler
" 命令行高度为两行
set cmdheight=2

" 显示行号
set number
" 为方便复制，用<F6>开启/关闭行号显示:
nnoremap <F6> :set nonumber!<CR>:set foldcolumn=0<CR>
set lazyredraw
" 切换缓存时不用保存
set hidden
" 输入模式下，退格键可以退一切字符
set backspace=eol,start,indent
set whichwrap+=<,>,h,l

set cursorline  " 光标横线
set cursorcolumn  " 光标竖线

" 高亮不想要的空格，比如行尾
" See [http://vim.wikia.com/wiki/Highlight_unwanted_spaces]
highlight ExtraWhitespace ctermbg=red guibg=red
match ExtraWhitespace /\s\+$/
autocmd BufWinEnter * match ExtraWhitespace /\s\+$/
autocmd InsertEnter * match ExtraWhitespace /\s\+\%#\@<!$/
autocmd InsertLeave * match ExtraWhitespace /\s\+$/
autocmd BufWinLeave * call clearmatches() " for performance

" 搜索时忽略大小写（incsearch)，如果搜索模式里有大写字母，就不再忽略大小写（smartcase）
set ignorecase
set smartcase
" 即时显示匹配结果（incsearch），并高亮所有结果（hlsearch）
set incsearch
set hlsearch
map <silent> <leader><CR> :nohlsearch<CR>

" 替换时，缺省启用g标志，即，同一行里的所有匹配都会被替换
set gdefault

" 设置粘贴模式快捷建
set pastetoggle=<F7>
```

另有vim7可用版本，软件版本比较旧的服务器可用

```
call plug#begin('~/.vim/plugged')

Plug 'joshdick/onedark.vim'
colorscheme onedark
" mkdir ~/.vim/colors
" cp ~/.vim/plugged/onedark.vim/colors/onedark.vim ~/.vim/colors
" cp ~/.vim/plugged/onedark.vim/autoload/onedark.vim ~/.vim/autoload

Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
let g:airline_theme='onedark'

" Plug 'Yggdroot/indentLine'
" let g:indentLine_color_term = 239
" let g:indentLine_char_list = ['|', '¦', '┆ ', '┊ ']

Plug 'preservim/nerdtree/'
" autocmd vimenter * NERDTree
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) &&
    \ !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | endif
map <F2> :NERDTreeToggle<CR>
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") &&
    \ b:NERDTree.isTabTree()) | q | endif

Plug 'hrp/EnhancedCommentify'
let g:EnhCommentifyRespectIndent = 'Yes'
let g:EnhCommentifyPretty = 'Yes'

Plug 'luochen1990/rainbow'
let g:rainbow_active = 1

Plug 'Raimondi/delimitMate'
au FileType python let b:delimitMate_nesting_quotes = ['"']

Plug 'docunext/closetag.vim'
let g:closetag_html_style=1

call plug#end()

filetype plugin indent on
syntax enable
syntax on

autocmd! BufWritePost ~/.vimrc source ~/.vimrc

let mapleader = ","
let g:mapleader = ","

set nocompatible

set nobackup
set nowritebackup

set noswapfile

nmap <leader>w :w!<CR>
nmap <leader>q :q!<CR>

noremap <leader>m :%s/<C-V><C-M>//ge<CR>

set viewoptions=cursor
au BufWinLeave ?* mkview
au VimEnter ?* silent loadview

set fileencodings=utf-8
set enc=utf8
set fencs=utf8

set fileformats=unix,mac,dos

set formatoptions+=mM

set cindent

set smarttab
set expandtab | set tabstop=4 | set shiftwidth=4

au FileType c,cpp,html,htmldjango,lua,javascript,nsis
    \ set expandtab | set tabstop=2 | set shiftwidth=2

au FileType make set noexpandtab | set tabstop=8 | set shiftwidth=8

au FileType c,cpp,python,vim set textwidth=79 | set colorcolumn=80

au FileType text,markdown,html,xml set wrap
set linebreak
" set breakindent

set showcmd
set scrolloff=7
set wildmenu
set wildmode="list:longest"
set ruler
set cmdheight=2

set cursorline
set cursorcolumn

set number
nnoremap <F6> :set nonumber!<CR>:set foldcolumn=0<CR>
set lazyredraw
set hidden
set backspace=eol,start,indent
set whichwrap+=<,>,h,l

highlight ExtraWhitespace ctermbg=red guibg=red
match ExtraWhitespace /\s\+$/
autocmd BufWinEnter * match ExtraWhitespace /\s\+$/
autocmd InsertEnter * match ExtraWhitespace /\s\+\%#\@<!$/
autocmd InsertLeave * match ExtraWhitespace /\s\+$/
autocmd BufWinLeave * call clearmatches()

set ignorecase
set smartcase
set incsearch
set hlsearch
map <silent> <leader><CR> :nohlsearch<CR>

set gdefault

set pastetoggle=<F7>
```

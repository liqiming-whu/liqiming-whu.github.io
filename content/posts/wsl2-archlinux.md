---
title: "在WSL2中安装ArchLinux并进行本地化配置"
date: 2021-04-09
categories: ["windows"]
tags: ["转载"]
description: "微软商店没有ArchLinux官方版本的WSL，不过我们可以使用LxRunOffline安装。"
cover: /assets/img/bg3.jpg
---

## 启用WSL

用管理员打开powershell输入：

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```

## 升级为WSL2的必要条件

- 对于x64的系统要求win10版本为**1903** 或者更高
- win + R 输入 `winver`查看版本

## 启用虚拟平台

用管理员打开powershell输入

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

**执行完毕后重启**。

**需要在BIOS中开启虚拟化，Intel CPU开启VT选项，AMD CPU开启SVM选项。**

## 下载Linux内核升级包

下载地址：

> <https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi>

下载完成后双击安装。

## 将WSL2设置为默认版本

用管理员打开powershell输入

```powershell
wsl --set-default-version 2
```

到这里WSL就安装好了，下面安装ArchLinux。

## 安装LxRunOffline

下载地址：

> <https://github.com/DDoSolitary/LxRunOffline/releases>

选择最新版下载，解压后将LxRunOffline.exe放入任意一个path文件夹下（比如C:/Windows/System32）。也可以把LxRunOffline.exe的目录添加到环境变量中。

当前最新版为[LxRunOffline-v3.5.0-msvc.zip](https://github.com/DDoSolitary/LxRunOffline/releases/download/v3.5.0/LxRunOffline-v3.5.0-msvc.zip) 。

## 下载Archlinux

下载地址：<https://mirrors.tuna.tsinghua.edu.cn/archlinux/iso/latest/>

找到[archlinux-bootstrap-2021.04.01-x86_64.tar.gz](https://mirrors.tuna.tsinghua.edu.cn/archlinux/iso/latest/archlinux-bootstrap-2021.04.01-x86_64.tar.gz) 。

## 安装archlinux到WSL2

命令1：

```powershell
LxRunOffline i -n <自定义名称> -f <Arch镜像位置> -d <安装系统的位置> -r root.x86_64
```

比如：

```
LxRunOffline i -n ArchLinux -f C:\Users\19146\Downloads\archlinux-bootstrap-2021.04.01-x86_64.tar.gz -d C:\Users\19146\ArchLinux -r root.x86_64
```

命令2：

```
wsl --set-version <名称> 2
```

比如：

```
wsl --set-version ArchLinux 2
```

## 进入系统

命令：

```powershell
wsl -d <你的archlinux名字>
```

比如:

```powershell
wsl -d ArchLinux
```

在这里我们就进入了archlinux内部，然后以下操作在archlinux中进行

删除`/etc/resolv.conf`文件，让archlinux自己生成resolve.conf文件

执行命令

```shell
rm /etc/resolv.conf
```

重新启动Archlinux

```powershell
exit
```

执行上述命令后会退出arch,回到powershell,然后在powershell中执行

```powershell
wsl --shutdown <你的archlinux名字>
```

比如：

```powershell
wsl --shutdown ArchLinux
```

然后再次进入Arch：

```powershell
wsl -d ArchLinux
```

## 添加清华源

### 使用vim

安装vim：

```shell
pacman -S vim
```

编辑pacman配置文件：

```shell
vim /etc/pacman.conf
```

在文件末尾添加：

```sh
[archlinuxcn]
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch
```

然后退出，编辑镜像源列表：

```shell
vim /etc/pacman.d/mirrolist
```

将China的源注释去掉（选择部分即可）

### 不会用vim的可以用资源管理器打开

~~很难相信有人居然不会用vim~~

在Arch中执行：

```powershell
cd /etc/
explorer.exe .
```

注意后面的点，执行这条命令后会用windows的文件管理器打开/etc目录，然后找到pacman.conf，在这个文件最后加入

```shell
[archlinuxcn]
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinuxcn/$arch
```

然后进入下一级目录`pacman.d`,编辑里面的mirrolist文件，将China的源注释去掉。

### 安装pacman-key

然后回到ArchLinux，执行：

```shell
pacman -Syy
pacman-key --init
pacman-key --populate
pacman -Sy archlinuxcn-keyring
```

**Archwiki提示：**

> **注意：** 如果`pacman-key --init`运行时系统没有足够的熵，可能会需要很长时间。请在目标机器上安装 [haveged](https://wiki.archlinux.org/index.php/Haveged) 或 [rng-tools](https://wiki.archlinux.org/index.php/Rng-tools)。然后在用 root 权限执行`pacman-key --init` 前[启动](https://wiki.archlinux.org/index.php/Start) `haveged.service`。

```shell
pacman -Syu haveged
systemctl start haveged
systemctl enable haveged
```

如果`pacman -S archlinuxcn-keyring 报错`，删除gnupg，重建密钥：

```shell
rm -rf /etc/pacman.d/gnupg
pacman-key --init
pacman-key --populate archlinux
pacman-key --populate archlinuxcn
```

## 配置sudo

安装一些常用软件：

```shell
pacman -S base base-devel vim git wget python
```

给当前的root设置密码：

```shell
passwd
```

**Archwiki提示：**

> **警告：** `/etc/sudoers`格式错误会导致sudo不可用。**必须**使用`visudo`编辑该文件防止出错。
>
> `visudo`调用的默认编辑器是`vi`。官方仓库里的 sudo 编译时开启了`--with-env-editor`，会采用环境变量 `VISUAL` 和 `EDITOR`的设置。如果设置了`VISUAL` 就不会使用`EDITOR`。
>
> 如果要临时使用其他编辑器，在该命令前加上`EDITOR`环境变量即可。例如，要使用 `nano`，用root运行以下命令：
>
> ```shell
> EDITOR=nano visudo
> ```
>
> 要永久设置编辑器，请查看 [定义本地环境变量](https://wiki.archlinux.org/index.php/Environment_variables#Defining_variables).
>
> 系统级的设置可以把编辑器设置到 `/etc/sudoers`。以 `nano` 为例，使用`visudo`打开该文件，加入以下内容：
>
> ```shell
> # Defaults specification
> # Reset environment by default
> Defaults      env_reset
> # Set default EDITOR to vim, and do not allow visudo to use EDITOR/VISUAL.
> Defaults      editor=/usr/bin/nano, !env_editor
> ```

使用vim作为编辑器，就需要在 `/etc/sudoers`中加入：

```shell
# Defaults specification
# Reset environment by default
Defaults      env_reset
# Set default EDITOR to vim, and do not allow visudo to use EDITOR/VISUAL.
Defaults      editor=/usr/bin/vim, !env_editor
```

或者直接`ln -s /bin/vim /bin/vi`。

执行`visudo`，将`/etc/sudoers`中的`wheel ALL=(ALL) ALL`那一行前面的注释去掉：

```shell
visudo
```

## 设置语言，安装字体

编辑`locale.gen`：

```shell
vim /etc/locale.gen
```

取消下面两行的注释：

```shell
en_US.UTF-8 UTF-8
zh_CN.UTF-8 UTF-8
```

如果不取消`en_US.UTF-8 UTF-8`前面的注释，你就会发现终端无法正常显示中文。

设置语言：

```shell
echo 'LANG=zh_CN.UTF-8' > /etc/locale.conf
```

生成语言配置：

```shell
locale-gen 
```

安装字体配置工具：

```shell
pacman -S fontconfig
```

安装字体：

```shell
pacman -S ttf-dejavu wqy-zenhei wqy-microhei
```

刷新字体缓存：

```shell
fc-cache
```

## 设置使用普通用户登录Archlinux

新建一个普通用户并设置密码：

```shell
useradd -m -G wheel -s /bin/bash <用户名>
passwd <用户名>
```

查看当前用户id：

```shell
id -u <用户名>
```

退出ArchLinux：

```shell
exit
```

在powershell中执行

```powershell
lxrunoffline su -n <你的archlinux名字> -v <账户id>
```

运行linux：

```powershell
wsl -d ArchLinux # wsl -d <你的archlinux名字>
```

## 卸载

输入指令：

```powershell
LxRunOffline ui -n ArchLinux # LxRunOffline ui -n <你的archlinux名字>
```

## 安装Windows Terminal

在微软商店搜索`Windows Terminal`，安装后打开，就会发现下拉菜单有ArchLinux选项卡，不用每次执行`wsl -d ArchLinux`进入系统了。

---

## 参考文献

> [在WSL2中安装ArchLinux](https://www.cnblogs.com/kainhuck/p/13835833.html)

> [sudo pacman -S archlinuxcn-keyring 报错](https://blog.csdn.net/qq_30151813/article/details/89555259)

> [Archwiki: pacman (简体中文)](https://wiki.archlinux.org/index.php/Pacman_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)/Package_signing_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87))

> [Archwiki: Sudo (简体中文)](https://wiki.archlinux.org/index.php/Sudo_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87))

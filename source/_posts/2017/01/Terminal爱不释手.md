---
title: Terminal爱不释手
id: loving-the-terminal-msys2
tags:
  - 终端
  - 编译
categories:
  - 强化
date: 2017-01-23 15:40:41
---
<img src="/2017/01/23/24/terminal-icon.png" width=450px alt="Terminal" title="终端">
Terminal终端又方便又好用，可惜在Windows8.1平台上不提供。这次就安装了MSys2，实现Windows上的Linux环境。
<!--more-->

当时安装Git for Windows的时候，一路下一步的过程中注意到了一个选项

![安装过程中的选项](snipaste-170123_00-43-54-008.jpg "安装过程中的选项")

当时也没在意什么是MinTTY，什么是MSYS2。只是特别感謝安装完之后出来的Git Bash，这个神奇的小终端。

根据 [Git for Windows Wiki页面](https://github.com/msysgit/msysgit/wiki) 的说明

> *   _msysGit_ – is the name of this project, a _build environment_ to develop (i.e. _not_ to use) Git for Windows, which releases the official binaries
> *   _MinGW_ – is a minimalist development environment for native Microsoft Windows applications (think: GCC to compile native Win32 applications).
> *   _MSYS_ – is a minimal POSIX emulation layer providing a Bourne Shell command line interpreter system. It is used by the MinGW project (and others), was forked _in the past_ from Cygwin (think: a minimal POSIX emulation layer on top of the Win32 API)
> *   _Cygwin_ – a Linux like environment, which was used in the past to build Git for Windows, nowadays has no relation to msysGit
> *   _MSys2_ – is another fork of Cygwin with the same idea as MSYS, but it is kept up-to-date with Cygwin and it comes with a package management system called _Pacman_ (calling `pacman -Syu` will update all of the installed packages to their newest versions). MSys2 is the basis for the upcoming [successor of msysGit](https://git-for-windows.github.io/)

这里还有很长的一段故事，关于分清MinGW MSYS Cygwin之间的关系。按照我的理解，这三个都可以用于在Windows下模拟Linux环境，都附带个MinTTY终端。MinGW可以直接编译Windows应用软件 生成exe文件，所以也被用在Code::Blocks等工具上 作为默认编译器。它还有个MinGW-w64，提供64位和32位的编译能力。而MSYS则是在MinGW的基础上提供了更多的库和工具。

MSys2 另一方面，指出是融合了Cygwin和MSYS的特性，提供一个一键安装包，提供pacman库管理工具，捆绑了MinGW+MinGW64+MSYS。很适合不使用Cygwin的人群(

既然有shell了，就可以替代掉Windows上丑到爆而且不太好用的cmd了。Terminal默认是bash，我切换成了更加强大的zsh。再施以[oh-my-zsh](https://github.com/robbyrussell/oh-my-zsh)，配上个好看的皮肤，美观的字体。

![oh my zsh加持下的终端](snipaste-170123_15-08-04-519.jpg "oh my zsh加持下的终端")

再像Git Bash一样 给Windows桌面的右键菜单上添加一个项目，快捷启动

```
HKEY_CLASSES_ROOT\Directory\background\shell\
```

这里是桌面右键菜单的设置位置，使用注册表编辑器浏览到这里，或者干脆写一个reg文件。我使用[O&amp;O RegEditor](https://www.oo-software.com/en/ooregeditor)这个免费的小软件，提供了地址栏功能。微软什么时候能在自家的注册表编辑器上添加导航器或者地址栏功能···

新建一个文件夹 比方叫**MSYS Shell**，然后添加一个子文件夹叫**command**

在这里的Default栏中添加执行路径，比如我写上**C:\msys64\msys2_shell.cmd -mingw64**。后面的mingw64也可以换成msys mingw之类的，参照安装程序在开始菜单中生成的快捷方式来填写。

* * *

不过在这之前，别忘了切换到使用终端的目的是替换掉原先的cmd以及在Powershell中的一些操作，把Git Bash更加通用化。首先来安装git

1.  更新软件包

    ```
    pacman  – needed -Sy bash pacman pacman-mirrors msys2-runtime
    pacman -Su
    ```

    不过在墙内直接运行的话，可能会有密钥失效的提示。这时候挂个代理就行，或者可能需要参照[这里](https://github.com/Alexpux/MSYS2-packages/issues/393)尝试一下。[这里](http://blog.csdn.net/jiutianhe/article/details/47608651)也提供了一些国内能用的源。

2.  安装基础软件包(可选)

    ```
    pacman -S base-devel
    ```

    刚使用终端的时候，会发现连最常见的tar命令等都没有，在base包里，可以选择安装上这些。

    ```
    $ pacman -S base-devel
    :: 共有 54 组员在组 base-devel 中：
    :: 软件库 msys
        1) asciidoc  2) autoconf  3) autoconf2.13  4) autogen  5) automake-wrapper
        6) automake1.10  7) automake1.11  8) automake1.12  9) automake1.13
        10) automake1.14  11) automake1.15  12) automake1.6  13) automake1.7
        14) automake1.8  15) automake1.9  16) bison  17) diffstat  18) diffutils
        19) dos2unix  20) file  21) flex  22) gawk  23) gdb  24) gettext
        25) gettext-devel  26) gperf  27) grep  28) groff  29) help2man
        30) intltool  31) lemon  32) libtool  33) libunrar  34) m4  35) make
        36) man-db  37) pacman  38) pactoys-git  39) patch  40) patchutils  41) perl
        42) pkg-config  43) pkgfile  44) quilt  45) rcs  46) scons  47) sed
        48) swig  49) texinfo  50) texinfo-tex  51) ttyrec  52) unrar  53) wget
        54) xmlto
    ```

    不过全部安装的话 体积也不小···

3.  安装git

    ```
    pacman -Sl | grep git
    ```

    通过这个命令可以看到 msys提供了git包 直接安装就好。pacman是个包管理软件，所以能够自动处理软件依赖这些事务

    ```
    pacman -S git
    ```

    可得100MB+呢···

4.  安装gcc

    ```
    pacman -S mingw-w64-x86_64-toolchain
    pacman -S mingw-w64-i686-toolchain
    ```

    上面是64位 下面是32位的包，选一个就好。

    ```
    $ pacman -S mingw-w64-x86_64-toolchain
    :: 共有 17 组员在组 mingw-w64-x86_64-toolchain 中：
    :: 软件库 mingw64
        1) mingw-w64-x86_64-binutils  2) mingw-w64-x86_64-crt-git
        3) mingw-w64-x86_64-gcc  4) mingw-w64-x86_64-gcc-ada
        5) mingw-w64-x86_64-gcc-fortran  6) mingw-w64-x86_64-gcc-libgfortran
        7) mingw-w64-x86_64-gcc-libs  8) mingw-w64-x86_64-gcc-objc
        9) mingw-w64-x86_64-gdb  10) mingw-w64-x86_64-headers-git
        11) mingw-w64-x86_64-libmangle-git  12) mingw-w64-x86_64-libwinpthread-git
        13) mingw-w64-x86_64-make  14) mingw-w64-x86_64-pkg-config
        15) mingw-w64-x86_64-tools-git  16) mingw-w64-x86_64-winpthreads-git
        17) mingw-w64-x86_64-winstorecompat-git
    ```

    不过注意这是所有的包，选择安装binutils gcc，需要debug的话再选上gdb就行。安装也包含g++，依赖都会帮你处理好，不过下载体积挺大的···

* * *

**基础工作到这里就基本完成了！**

在意识到这个Terminal可以运行exe文件之后，想到了给shell加上PATH变量，让它更加方便顺手。

不论是.bashrc或者.zshrc之类的环境文件，添加`export PATH="/c/.../...":"/d/.../...":$PATH`注意到/c代表C盘，项目用冒号分隔，使用引号包起内容 避免空格歧义，PATH和后面的等号之间没有空格。

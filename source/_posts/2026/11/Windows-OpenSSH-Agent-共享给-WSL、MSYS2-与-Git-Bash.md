---
title: Windows OpenSSH Agent 共享给 WSL、MSYS2 与 Git Bash
id: share-windows-ssh-agent
date: 2026-11-09T19:38:09+08:00
tags:
categories:
  - 折腾
updated: 2026-11-09T21:59:17+08:00
---
用 Windows 的时候注意到一个奇怪的现象，我在 PowerShell 中使用 `ssh-add` 添加了一个私钥。过段时间因为这个私钥没有用了，我就把私钥文件给删除了。但是重启系统却发现它对应的公钥还在 `ssh-add -L` 中。

这件事本身不算问题，只是说明密钥确实被 agent 托管了。那么既然私钥都由 Windows OpenSSH 的 agent 来管理，这台设备上其他使用 SSH Key 的应用都通过它来认证就很合理。这里共享的是 agent 提供的签名能力，不需要把私钥再复制到每个环境里。

<!-- more -->

这篇文章记录一下目前在用的版本。Git Bash 直接使用 Windows OpenSSH，MSYS2 和 WSL2 则保留各自原生的 SSH，只把 agent 请求转发给 Windows。后面也顺便记录试过的替代方案。

如果想要现成方案，可以直接用 [masahide/OmniSSHAgent](#omnisshagent)。它的架构和我这套基本一致，架构图我就直接拿来用了。

![OmniSSHAgent Connection Architecture](https://raw.githubusercontent.com/masahide/OmniSSHAgent/v1.0.0/docs/images/omnisshagent-connection-diagram.svg)

那段时间为了这件事陆续写了几篇日记：

- [2025-08-24](https://obsidian.kokomi.me/Diary/2025-08-24) 使用 Windows OpenSSH agent 统一管理密钥，并通过 `socat + npiperelay` 共享给 WSL2。
- [2025-08-26](https://obsidian.kokomi.me/Diary/2025-08-26) 将 Windows 的 `.ssh` 目录只读挂载到 WSL2，以共享 SSH 配置。
- [2025-09-05](https://obsidian.kokomi.me/Diary/2025-09-05) 排查 MSYS2 rsync 与 Windows SSH 的兼容问题，并记录原生 SSH 和 agent 桥接的用法。
- [2025-09-12](https://obsidian.kokomi.me/Diary/2025-09-12) 探索 MSYS2 共用 Windows agent，以及使用 systemd socket 按连接启动转发进程。
- [2026-07-01](https://obsidian.kokomi.me/Diary/2026-07-01) 排查 rsync 调用 Windows 版 SSH 导致的错误，改为指定 MSYS2 原生 SSH。
- [2026-10-31](https://obsidian.kokomi.me/Diary/2026-10-31) 在 Windows 与 WSL 共享 SSH 配置的基础上，为 WSL 单独启用连接复用。

## Windows OpenSSH

当时发现重启并不会清空 `ssh-agent` 里已经加载的密钥，搜索文档找到了 [Key-Based Authentication in OpenSSH for Windows | Microsoft Learn](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement#user-key-generation)。作为 Windows 服务运行的 `ssh-agent` 会持久保存添加进去的密钥，删除原文件并不会把它从 `ssh-agent` 中移除，需要用 `ssh-add -d` 删除。

微软的建议是添加完私钥之后，直接删掉源文件，利用系统的 SSH Agent 来提供私钥。找到一个讨论帖 [ssh-agent: permanent loaded ssh-key storage · Issue #1487 · PowerShell/Win32-OpenSSH](https://github.com/PowerShell/Win32-OpenSSH/issues/1487)，了解到微软会把密钥放在注册表的 `HKEY_CURRENT_USER\Software\OpenSSH\Agent\Keys`，使用 DPAPI 加密，和 Windows 用户的安全上下文关联。

至于这么存安不安全，我说不好，但我正需要一个类似 Apple Keychain 那种通过 `ssh-add --apple-use-keychain` 加进去就不用反复输密码的管理器，反倒喜欢这种加入私钥后可以删除原文件的行为。

但是注意在 Windows 上其实有两种 OpenSSH：

- 通过添加 Windows 可选功能安装的，位于 `C:/Windows/System32/OpenSSH/`，我这台设备上记录到的版本是 `OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2`
- 能用 winget 安装的 [PowerShell/Win32-OpenSSH](https://github.com/PowerShell/Win32-OpenSSH)，位于 `C:/Program Files/OpenSSH/`，当前版本是 `OpenSSH_for_Windows_10.0p2 Win32-OpenSSH-GitHub, LibreSSL 4.2.0`

我选择 GitHub 上的版本，后面用到的 winssh-pageant 也要求这一版。并不是所有 agent 转发都要求安装它，但同一台设备上装了多份 SSH，最好先确认到底调用了哪份。

```shell
winget install --id Microsoft.OpenSSH.Preview --exact
Get-Command ssh, ssh-add -All
ssh -V
Get-CimInstance Win32_Service -Filter "Name='ssh-agent'" |
    Select-Object State, StartMode, PathName
```

服务需要启动，并设置为自动运行。这两行在管理员 PowerShell 中执行：

```shell
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent
```

然后回到自己平时使用的用户会话添加密钥：

```shell
ssh-add "$HOME/.ssh/id_ed25519"
ssh-add -L
```

后面所有桥接的终点都是 Windows named pipe `\\.\pipe\openssh-ssh-agent`。Windows OpenSSH 本身就认识这个接口，MSYS2 和 Linux 的原生 SSH 则通过 `SSH_AUTH_SOCK` 找 Unix socket。另外，MSYS2 用的是 Cygwin socket，和 WSL2 里真正的 Linux socket 不是一回事，不能混用。需要解决的就是这段接口转换。

```text
Git Bash  → Windows ssh.exe → Windows OpenSSH agent → \\.\pipe\openssh-ssh-agent
MSYS2 ssh → MSYS2 socket    → ~/.ssh/agent/s.a0arHYrszR.local.793.ILNFXIIt7t
WSL2 ssh  → Linux socket    → ~/.ssh/agent/s.a0arHYrszR.agent.dnIAX3Td2I
```

## Git Bash

Git for Windows 其实附带了一份 OpenSSH，通常在安装目录的 `usr/bin/ssh.exe`。不能因为是在 Git Bash 中执行，就认为调用的一定是 Windows OpenSSH。

我这里选择直接用 `C:/Program Files/OpenSSH/ssh.exe`，它能直接连接 Windows agent，不需要额外起转发进程，也不依赖给 Git Bash 设置 `SSH_AUTH_SOCK`。

在 Git Bash 中可以先检查：

```shell
type -a ssh ssh-add
ssh -V
git config --show-origin --get core.sshCommand
```

最后一条没有输出也正常，表示没有设置这个 Git 配置。想明确指定 Git 使用 Windows OpenSSH，可以这样配置：

```shell
git config --global core.sshCommand '"C:/Program Files/OpenSSH/ssh.exe"'
```

## MSYS2

MSYS2 能直接调用 Windows 的 EXE，但用它工具链构建出来的程序不行。

一个例子就是 Windows 并没有原生 rsync，好在 MSYS2 提供了一个，但它是基于 MSYS2 OpenSSL 编译的。
之前遇到过 rsync 提示 `connection unexpectedly closed` 和 `Suppressing signal 30 to win32 process`。排查下来，rsync 调用的 `ssh` 解析到了 Windows 版本。MSYS2 的 rsync 配合 MSYS2 的 SSH，才能避免进程通信问题。

所以得保留 MSYS2 原生 OpenSSH，让它的 `SSH_AUTH_SOCK` 接到 Windows 那边。那么就需要有一个工具来把 Windows 的 pipe 转换成 Linux 的 socket。一番搜索发现了 [albertony/npiperelay](https://github.com/albertony/npiperelay) 这个桥接工具。

它的文档上刚好有一段教你如何连接至 Windows SSH Agent，我调整之后变成这样，让 Bash Profile 去加载它。

```shell
#!/usr/bin/env sh

# Git Bash 也有 MSYSTEM，用 os-release 区分。
if ! grep -qx 'ID=msys2' /etc/os-release 2>/dev/null; then
  return
fi

export SSH_AUTH_SOCK="/tmp/run/ssh-agent.sock"

if [ -S "$SSH_AUTH_SOCK" ]; then
  if socat -u OPEN:/dev/null UNIX-CONNECT:"$SSH_AUTH_SOCK" >/dev/null 2>&1; then
    return
  fi
  rm -f "$SSH_AUTH_SOCK"
fi

mkdir -p /tmp/run

(setsid socat \
  UNIX-LISTEN:"$SSH_AUTH_SOCK",umask=007,fork \
  EXEC:"npiperelay-msys2.exe -ei -s //./pipe/openssh-ssh-agent",nofork \
  &) >/dev/null 2>&1
```

这里相比文档里的示例改了几处：

1. 限定只能在 MSYS2 中运行，因为 Git Bash 不需要启动 Socket Relay。
2. 用 `[ -S "$SSH_AUTH_SOCK" ]` 判断目标文件存在，再尝试连接，连接不可用时判定为已失效并重新建立。比直接调用 `ss` 能少一些系统调用。

然后是 `npiperelay-msys2.exe`，这是用 MSYS2 里的 Golang 从源码构建的版本。原因还是它需要基于 MSYS2 的 OpenSSL，给 WSL 用的普通 Windows 构建不能直接照搬到这个组合里，会出现：

```text
copy from stdin to pipe failed: read /dev/stdin: The parameter is incorrect.
```

这个错误发生在 socat 和 npiperelay 之间的标准输入通信上，是 Golang 抛出来的错误，还没到 SSH 认证那一步。

## WSL2

WSL2 也可以直接调用 `ssh.exe`，但我需要 Linux OpenSSH 的 ControlMaster 连接复用。于是这里和 MSYS2 一样，保留原生 SSH，只共享 Windows agent。

早期用过 `socat + npiperelay` 放到 profile 里后台启动，但当我开多个 Shell Session 的时候，它们之间会产生冲突。`socat` 也会时不时地无法自动停止。

后来改成了 systemd 用户 socket。systemd 自己监听 Unix socket，连接进来后才启动一个 npiperelay，连接结束后转发进程退出。这样 WSL 里不需要常驻一个 socat，也不用由每个新 shell 判断是否要启动监听。

这里使用 [albertony/npiperelay](https://github.com/albertony/npiperelay) 的普通 Windows 构建，和前面 MSYS2 使用的构建分开。可以在 Windows 中安装：

```shell
winget install --id albertony.npiperelay --exact
```

在 WSL 创建两个文件：

```ini title="~/.config/systemd/user/named-pipe-ssh-agent.socket"
[Unit]
Description=SSH Agent provided by Windows named pipe

[Socket]
ListenStream=%t/ssh/ssh-agent.sock
FileDescriptorName=ssh
SocketMode=0600
DirectoryMode=0700
Accept=yes

[Install]
WantedBy=sockets.target
```

```ini title="~/.config/systemd/user/named-pipe-ssh-agent@.service"
[Unit]
Description=Proxy to Windows SSH Agent

[Service]
ExecStart=/mnt/c/Users/%u/AppData/Local/Microsoft/WinGet/Links/npiperelay.exe -ei -s '//./pipe/openssh-ssh-agent'
StandardInput=socket
```

这里 `Accept=yes` 和 service 文件名里的 `@` 是配套的。每个被接受的连接启动一个 service 实例，`StandardInput=socket` 把已经接通的 socket 交给 npiperelay，再由它连接 named pipe。npiperelay 不负责自己监听 Linux socket，好处是它不用常驻。

`%t` 对应用户运行时目录，通常是 `/run/user/1000`，所以 unit 里不用写死 uid。socket 和目录的权限分别设成 `0600`、`0700`，限制其他 Linux 用户访问。`-ei` 让 npiperelay 在标准输入结束后退出，`-s` 是它针对 named pipe 的 EOF 处理选项，沿用项目的 SSH agent 转发用法。

然后启用 socket，并让 shell 使用相同的路径：

```shell
systemctl --user daemon-reload
systemctl --user enable --now named-pipe-ssh-agent.socket
export SSH_AUTH_SOCK="${SSH_AUTH_SOCK:-${XDG_RUNTIME_DIR%/}/ssh/ssh-agent.sock}"
```

就能在 `ssh-add -L` 的输出里看到 Windows 管理的私钥，最后把 `export` 那行加入自己的 shell 启动文件。

## PuTTY

对于 PuTTY 系的 Pageant，使用 `winget install NathanBeals.WinSSH-Pageant` 安装了 [ndbeals/winssh-pageant](https://github.com/ndbeals/winssh-pageant) 来打通二者。注意它需要 GitHub 版本的 OpenSSH for Windows。

它的方向是把 Pageant 客户端的请求转给 Windows OpenSSH agent。密钥仍然用 Windows 的 `ssh-add` 添加，不需要再导入一份到 Pageant。安装程序会把它配置成登录时自动启动，PuTTY、WinSCP 等支持 Pageant 的客户端就能使用这份密钥。

## Synology Rsync

这个其实和 Windows OpenSSH 关系不大，但我不想为它单开一篇，也就顺便写在这。

前面提到的在 Windows 上使用 MSYS2 的 rsync 报错，还有一层来自 Synology。之前遇到普通 SSH 登录正常，但只要远端命令以 `rsync` 开头就提示 `Permission denied`，也出现过 `rsync service is no running (code 43)`。

这个问题和本地选错 SSH 是两件事。我的情况是在 DSM 中开启 rsync 服务后解决的，具体记录在 [2025-09-05 MSYS2 的 rsync 上传到 Synology 报错 | 涼果笔记](https://obsidian.kokomi.me/Diary/2025-09-05)

当时有个很直接的对照实验，同一台主机执行 `rsync` 失败，改成 `true;rsync` 却能成功：

```shell
ssh.exe enihsyou.synology.me 'rsync'
ssh.exe enihsyou.synology.me 'true;rsync'
```

这说明认证已经通过，差别出在远端执行命令的阶段。继续用 IDA 逆向排查，发现 Synology 自带的 sshd 对 rsync 命令有额外处理。

除了使用 WSL2 提供的 rsync 以外，一个解决办法是指定使用 MSYS2 的 SSH：

```shell
rsync -e /usr/bin/ssh enihsyou.synology.me:.bashrc .
```

另一个更简单、一劳永逸的办法就是去 Synology 管理页面开启 rsync 服务。

## OmniSSHAgent

如果不想维护 MSYS2 和 Pageant 的桥接，又可以接受后台持续运行一个托盘程序，可以尝试 [masahide/OmniSSHAgent](https://github.com/masahide/OmniSSHAgent)。它有一篇 [文章](https://github.com/masahide/OmniSSHAgent/blob/v1.0.0/docs/why-omnisshagent-is-being-redesigned.md) 解释了这个项目为什么会被重写，遇到的问题和我基本一样。

默认的 `windows-openssh` 后端继续使用 Windows 服务保存密钥和签名，OmniSSHAgent 提供 Pageant、Cygwin/MSYS2 兼容接口。
WSL2 则交给同一作者的 [masahide/pipeferry](https://github.com/masahide/pipeferry)。它把 WSL2 的 Linux Unix socket 转发到 Windows named pipe，可以独立连接 Windows OpenSSH agent，并不要求先运行 OmniSSHAgent。Windows 侧（包括我这里的 Git Bash）仍然直接用 Windows OpenSSH。

不过它的运行方式和我的 WSL 配置略有不同：Pipeferry 安装的是常驻的 `pipeferry-ssh-agent.service`，由 Linux 端进程自己监听 socket，再为连接启动 Windows 端桥接进程；我这边由 systemd 的 `.socket` 监听，使用 `Accept=yes` 按连接启动 `npiperelay.exe`。

这两个项目都实际试用过，但试完后我还是切回了前面的配置。主要是我不想再挂一个托盘图标，而且前面这套交给 systemd 和 profile 的配置已经够用。

---
title: macOS内存盘备份老大难问题
date: 2019-02-04 02:53:16
id: 48
tags:
  - macOS
  - RAMDisk
categories:
  - 折腾
  - 优化
---
内容接上一篇[创建内存盘](/2018/10/08/47/)的文章。

在有了开机自动创建内存盘的(基础)功能之后，
果果屡次遭遇了注销、重启导致还在内存盘中的文件丢失。

虽然大部分是说重要也不重要，说不重要也懒得再费流量的下载文件，没有来得及转移和消费它们，
而且放置在内存盘中的文件应该有朝生夕灭的觉悟，重要的不可再生的文件不应该放置于此。

这回我们就来探究一下如何在macOS下自动备份内存盘，并在创建时恢复之前状态。
<!--more-->

---
## tl;dr

我在Gist上放了一份，你也可以直接跳转到[最后](#整合创建脚本)

<script src="https://gist.github.com/enihsyou/d8217414c720398333f4cbe33703220f.js"></script>

---

通过Google搜索关键词*macOS backup RamDisk*，没有什么有价值的结果，
那就只能自己动手。

最初的入口，是Apple官方给出的一份讲述[如何使用磁盘工具创建磁盘镜像][1]的文档，\
其中关于*从磁盘或连接的设备创建磁盘映像*似乎很有吸引力，
因为我们就是需要从创建出来的内存盘磁盘设备中创建出镜像文件。

可是细看和实践发现，创建设备镜像：\
一是需要选择到设备而不是APFS容器\
二是需要先卸载(unmount)对应设备，不然会提示设备忙

但是文档中也指了一条明路，那就是从文件夹创建镜像。

本文不会对*磁盘工具*(*Disk Utility*)的界面操作进行详细描述，主要介绍与之相对应的命令行。

## 关键词 `hdiutil create`

在*Terminal.app*中使用`man`打开*hdiutil*的文档[^1]，可以看到它有一个叫*create*的命令。

冗长的英文介绍就不再赘述，简单来说，create命令可以从设备中、指定文件夹或者以指定大小创建一个dmg镜像。

其中有 *-srcdevice* 和 *-srcfolder* 两个参数吸引眼球，分别是从文件夹和设备中创建镜像，我们分别来看看。

我们先建立一个用于测试的内存盘，设备位置在disk5

    image-path      : ram://838860
    shadow-path     : <none>
    icon-path       : /System/Library/PrivateFrameworks/DiskImages.framework/Resources/CDiskImage.icns
    image-type      : 读/写
    system-image    : false
    blockcount      : 838860
    blocksize       : 512
    writeable       : TRUE
    autodiskmount   : false
    removable       : TRUE
    image-encrypted : false
    mounting user   : enihsyou
    mounting mode   : <unknown>
    process ID      : 70907
    /dev/disk4	GUID_partition_scheme
    /dev/disk4s1	7C3457EF-0000-11AA-AA11-00306543ECAC
    /dev/disk5	EF57347C-0000-11AA-AA11-00306543ECAC
    /dev/disk5s1	41504653-0000-11AA-AA11-00306543ECAC	/Volumes/Test

### `hdiutil create -srcdevice`

srcdevice需要个设备号作为参数，比如 *disk5* */dev/disk5* 就是很好的例子。
但是注意不能是*disk5s1*，因为它不是个设备，在Disk Utility也能看到对它的创建操作是灰色不可选定的。

我们执行命令：

    $ hdiutil create -srcdevice /dev/disk5 test.dmg
    hdiutil: create failed - 资源忙

悲剧的事情发生了，它提示资源忙，这是因为这个设备还在挂载状态，需要先将它卸载。
可以通过Disk Utility，选择卷宗然后点卸载，也可以键入`hdiutil detach disk5`来执行卸载[^2]。

再次执行操作就没问题啦

    $ hdiutil create -srcdevice /dev/disk5 test.dmg
    正在准备映像引擎…
    正在读取整个磁盘（Apple_APFS：0）…
    ............................................................................
       (CRC32 $C3008C9B：整个磁盘（Apple_APFS：0）)
    正在添加资源…
    ............................................................................
    已耗时：765.768ms
    文件大小：173576623 字节，校验和：CRC32 $B557037F
    已处理扇区：838784，已压缩 413584
    速度：263.7M 字节/秒
    节省：59.6%
    created: /Volumes/RAM/test.dmg

---
如果多次执行同样命令时可能遇到错误提示

    hdiutil: create failed - 文件已经存在

原因如上所述，只需要在命令后添加`-ov`参数即可，意思是覆盖已存在的文件。

### `hdiutil create -srcfolder`

另一个可用的参数是srcfolder，它需要个文件夹路径作为参数。

    $ hdiutil create -srcfolder Cache test.dmg
    ............................................................................
    created: /Volumes/RAM/test.dmg

这个文件夹参数可以是任意目录，但是会需要有读取权限。

---
那么我想，*/Volumes/Test*就是个文件夹，能不能直接把它备份呢？行的

    $ sudo hdiutil create -srcfolder /Volumes/Test test.dmg -ov
    ............................................................................
    created: /Volumes/RAM/test.dmg

注意这里去要使用`sudo`来执行命令，如果不添加会需要鉴权，使用TouchId或者输入密码。
而sudo可以提前提供权限，而且生成的文件还是以自己的用户名义创建的（非root）。

以上两个命令就是所需的创建备份镜像的工具，考虑到操作的连贯性，不用每次先卸载再挂载
srcfolder选项更适合本次脚本。

## 关键词 `asr restore`

已经有镜像了，那么如何还原它呢。

在官方文档上指出可以使用*asr*工具来还原镜像。

*asr restore*就是这么一个命令，\
它需要一个镜像文件作为source\
一个文件夹路径作为target\
同时为了恢复，还需要添加上`--erase`flag，文档中说这是个必填项

整合起来就像这样
```bash
asr restore --source test.dmg --target /Volumes/Test --erase
```

正当你满心欢喜地准备执行时，却发现它丢出了个error

    $ asr restore --source test的副本.dmg --target /Volumes/Test --erase
    	Validating target...done
    	Validating source...done
    Could not find any scan information. The source image needs to be imagescanned before it can be restored.

意思是说没有扫描（校验）过的镜像不允许被当作还原源，那么有以下两个解决方案。

### `asr imagescan`

先把镜像扫描一遍。

实际上如果你通过Disk Utility执行还原操作时，会发现它也进行了一次扫描操作

    正在从“test.dmg”恢复到“容器“disk5””
    
    正在验证目标…
    完成
    正在验证来源…
    完成
    未能找到任何扫描信息。在可以恢复之前，源映像需要进行映像扫描。 <-- 这里
    需要扫描映像。将恢复为已装载的磁盘映像。
    正在验证目标…
    完成
    正在验证来源…
    完成
    正在验证大小…
    完成
    正在恢复
    正在验证  
    正在反转目标宗卷…
    完成
    Restored target device is /dev/disk5s1.
    
    操作成功。

原因是当我们使用`hdiutil create`创建镜像时，它是不带校验信息的。
可以手动通过imagescan执行校验

命令很简单

    $ asr imagescan --source test.dmg
    Block checksum: ....10....20....30....40....50....60....70....80....90....100
    Reordering:     ....10....20....30....40....50....60....70....80....90....100
    successfully scanned image "/Volumes/RAM/test.dmg"

但时时刻刻关心磁盘占用的用户会发现，执行这个命令会导致整个镜像文件被全部读取再压缩写入。
虽然写后的文件体积有所缩小，但是对于若干GB体积文件还是占用写入时间，而且这都是浪费SSD磁盘寿命的行为。

其实在后台，这个命令不仅会执行校验，还会将文件内容重新排序和压缩，这样导致生成的体积变小了许多。

当然还有一个`--nostream`参数可以防止重新写入的进行，节省磁盘操作，但远不及下面的方式。

### `--noverify`

如果在restore时直接指定让它不进行校验那就最棒啦，因为整个镜像都是我们创建的，很信任它。
这个参数就能达成目的。把它附加在restore命令后即可。

    $ asr restore --source test.dmg --target /Volumes/Test --erase --noverify
    	Validating target...done
    	Validating source...done
    	Erase contents of /dev/disk5s1 (/Volumes/Test)? [ny]: y
    	Retrieving scan information...done
    	Validating sizes...nx_kernel_mount:1455: : checkpoint search: largest xid 5, best xid 5 @ 1
    done
    	Restoring  ....10....20....30....40....50....60....70....80....90....100
    	Inverting target volume...done
    	Restored target device is /dev/disk5s1.
    	Remounting target volume...done

顺便可以加上`--noprompt`来跳过确认操作的过程。

再去查看，整个文件夹结构包括隐藏文件夹都已经恢复了。

## 其他注意事项

### 关机自动执行

macOS Mojave想要像众多Linux发行版一样，让脚本在关机时自动执行，我至今没有找到办法。

搜索过的关键词有
- macOS shutdown script
- macOS shutdown hook
- macOS run script on logout

相关可能有效的结果有
- [Offset on Github]
- [LogoutHook]
- [launchd + signal trap]

但始终我没有成功过。

### 定时自动执行

那么就只能使用低一级的笨办法，定时备份。
它对比关机备份的有一个好处，就是即便强制关机的话也能保留最近的记录。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>local.randisk.backup</string>
	<key>Program</key>
	<string>/Users/enihsyou/.dotfiles/macOS/backupRamDisk.sh</string>
	<key>StandardErrorPath</key>
	<string>/tmp/local.randisk.backup.stderr</string>
	<key>StandardOutPath</key>
	<string>/tmp/local.randisk.backup.stdout</string>
	<key>StartInterval</key>
	<integer>43200</integer>
</dict>
</plist>
```

类似这样的文件，你可以用*Launch Control*图形化界面来创建任务。

其中的43200秒间隔相当于12小时，因为我不需要太频繁地备份。

## 整合创建脚本

现在我们有了备份文件，创建内存盘的脚本会需要相应的修改，比如

- 检测备份文件是否存在，如果存在就还原镜像
- 检测内存盘是否已加载，如果是的话就加载它即可\
  这是因为如果用户选择了logout而不是shutdown，脚本会在login时再次执行，导致重复创建的错误\
  同时用户logout时会将挂载的内存盘卸载，这都是不希望的。\
  为此，还需要将这个脚本分别在*Global Daemon*和*Global Agent*两个地方都设置\
  一个在开机执行，创建内存盘；一个在登录执行，恢复先前已卸载的磁盘设备。

```bash
DISKNAME=${2-RAM}
BASE=/Volumes/$DISKNAME
[[ -e $BASE ]] && exit 0

# If already created RAMDisk, just mount it. 
DEVICE_IDENTIFIER=`diskutil info $DISKNAME | sed -n -E 's/^.*Device Identifier:.*(disk.*[0-9]).*/\1/p'`
if [[ -n $DEVICE_IDENTIFIER ]]; then
    hdiutil mountvol $DEVICE_IDENTIFIER
    exit 0
fi

# Backup location
IMAGE_LOCATION=${3-"/Users/enihsyou/Library/RAM.dmg"}
if [ -e $IMAGE_LOCATION ]; then
  asr restore --source $IMAGE_LOCATION --target $BASE --erase --noverify --noprompt
else
  mkdir # create temp directories
fi
```

---

相反备份脚本就更容易写了

```bash
DISKNAME=${1-RAM}
IMAGE_LOCATION=${2-"/Users/enihsyou/Library/RAM.dmg"}
DISK_LOCATION=/Volumes/${DISKNAME}

sudo hdiutil create -srcfolder $DISK_LOCATION $IMAGE_LOCATION -ov
sudo chown enihsyou $IMAGE_LOCATION
```

注意这里的最后一行，它的作用是把产出文件的所有者改为自己。\
这是因为备份脚本需要以root权限执行，如果不加这个似乎会在还原时出权限问题，如果读者有进展请告知我。

[^1]:
    这里解释下为何使用Terminal.app打开而不是美好的iTerm2

    如果你曾经在Terminal.app中输入`man`命令
    或者点按TouchBar上的ℹ︎键打开过man page\
    你会发现Terminal.app的*Man Page*主题意外地好看，而且界面渲染效率更高（简单说就是更流畅）\
    那么如何利用iTerm2的ℹ︎键跳转到Terminal.app中呢，
    查找文档以后发现只需要修改\
    iTerm2 > Advanced > General > Command to view man pages 为 `open x-man-page://%@ &`即可。

[^2]:
    顺带提下如何反向操作，也就是装载

    在Disk Utility里选择已卸载的磁盘，点装载即可\
    通过命令行可以键入`hdiutil attach /dev/disk5`来完成\
    注意这时使用*disk5*或者*disk5s1*都是可以的，因为卸载对象实际上是disk5s1。

[1]: https://support.apple.com/zh-cn/guide/disk-utility/create-a-disk-image-dskutl11888/mac
[Offset on Github]: https://github.com/aysiu/offset
[LogoutHook]: https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CustomLogin.html
[launchd + signal trap]: https://github.com/freedev/macosx-script-boot-shutdown

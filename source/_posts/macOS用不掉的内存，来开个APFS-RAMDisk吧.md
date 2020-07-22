---
title: macOS用不掉的内存，来开个APFS RAMDisk吧
date: 2018-10-08 14:11:03
tags:
  - macOS
  - RAMDisk
  - Chrome
id: 47
categories:
  - 折腾
  - 优化
---

既然有32GB的内存，那么为何不利用起来呢🤪开个内存盘吧

顺便把傻大粗的 Chrome 缓存移动过去。（比软连接更完美的解决方案）

<!--more-->

---

果果新入了台2018年款2.6G 32G版的MacBook Pro💻

<blockquote class="twitter-tweet" data-lang="zh-cn" align="center"><p lang="zh" dir="ltr">好耶💖<br>果果加入水果家族<br>接下来的几年 MBP请多关照 <a href="https://t.co/re8tIUsrYm">pic.twitter.com/re8tIUsrYm</a></p>&mdash; 九条热果（期间限定） (@enihsyou) <a href="https://twitter.com/enihsyou/status/1033241965511331846?ref_src=twsrc%5Etfw">2018年8月25日</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

也算是正式进入没有16GB以上活不下去阵营啦。

根据调教躺在寝室里的前任开发机的经验，辛苦的作为主力开发机的话，每天将会承受上百GB的写入量，顿时心疼之心悠然而生

毕竟是不可更换硬件设备的MBP呀，还是爱惜点好，那么我们一起来开个RAMDisk吧～

本文包括创建HFS+内存盘、创建APFS内存盘、移动Chrome默认缓存目录、开机自动创建内存盘等内容😉

## 简单创建内存盘

Google大法真滴不简单，掏出关键词[一丢进去](http://lmgtfy.com/?q=macOS+ramdisk)，第一条就是[有效的结果](https://www.tekrevue.com/tip/how-to-create-a-4gbs-ram-disk-in-mac-os-x/)

### 创建个磁盘镜像

看上面怎么说，嗯嗯嗯，有几行代码，可以创建4GB的内存盘
即便是不太懂英语的程序员也能根据代码知道大概做的什么吧）

```bash
diskutil erasevolume HFS+ 'RAM Disk' `hdiutil attach -nomount ram://8388608`
```

我们来分析这段小小的魔法代码
从最里面（最右边）开始看，两个反引号包起来的语句是从内存创建镜像

这里面的 _8388608_ 在下面有解释，
是通过 `4096 * 2048` 得来的。

这里就有疑问了，为什么是4096和2048。

4096就不用解释了吧，=`4 * 1024`就是我们需要创建的内存盘的大小in Megabytes

2048呢，其实是`1024 * 2`，1024是 1MB = 1024KB，在这里换算；
  2呢，其实是`1024 / 512`算来的，
  这里的1024又是，对的你猜到啦 1KB = 1024B，
  然后512是[BlockSize](https://en.wikipedia.org/wiki/Block_(data_storage)，512字节为一块

总体合起来就是 `4 * 1024 * 1024 * (1024 / 512)`

---

然后`attach --nomount`是什么呢
查看帮助文档可以看到这些输出

    $ hdiutil attach -help
    hdiutil attach: attach disk image
    Usage:  hdiutil attach <image>
      Mount options:
          -mount required|optional|suppressed  mount volumes?
          -nomount            same as -mount suppressed
          -mountpoint <path>  mount at <path> instead of inside /Volumes
          -mountroot <path>   mount volumes on <path>/<volname>
          -mountrandom <path> mount volumes on <path>/<random>
意思大致是，nomount就是不mount🙃

---

然后你就能在磁盘工具里看到新创建的磁盘了，
我们创建一个4GB的看看

    $ hdiutil attach -nomount ram://$(( 4 * 1024 * 1024 * 1024 / 512 ))
    /dev/disk4

![](刚创建的4GB内存盘镜像.png)
嗯，确实是4GB

### 格式化磁盘
仔细看这里的卷宗类型，写的是*未初始化*，翻译成Windows的话来说就是硬盘为格式化
  那么我们来给它手动格式化吧
 
打开磁盘工具，选择新创建的内存盘（一般叫做*Apple 读/写 Media*）
  选择抹掉，格式使用默认的*MacOS 扩展（日志式）*
  再取个好听的名字，就大功告成啦
 
然后你就能在Finder里看到自己的内存盘啦
体验一下速度～

![Blackmagic Disk Speed Test, 3GB file, HFS+ Disk](HFS%20Speed%20Test.png)

足够满意了吧

> 当然如果在这里选择APFS格式的话，会报错，提示无法完成
![](直接点击APFS.png)
但是过程中，它先给你创建了个HFS+格式的分区，也算是达成了目标吧😅
可是到了这里，也无法继续转为APFS格式了，只能eject重新开始

### 兄弟，这里有个🔧

Google出来的第一个网页结果里面有个App，地址在这
http://bogner.sh/wp-content/uploads/2012/12/RAMDiskCreator.app_.zip

可以直接创建HFS+格式的内存盘呢，巨方便的

## 听说APFS挺好用的呢

那么能不能更给力一点呢

Apple退出了APFS，转为SSD优化，复制（克隆文件）超快，读写提升
  听上去很适合我们坐火箭的RAM Disk
  （也很适合折腾

新镜像需要初始化，以GPT分区表初始化，用命令行来完成就好啦
```bash
diskutil partitionDisk $DISK_ID GPT APFS "$DISKNAME" 0
```
这里的DISK_ID就是上面创建的内存镜像，类似与`/dev/disk4`这种文件
  DISKNAME则是想要取的名字

运行结果如下

    $ diskutil partitionDisk `hdiutil attach -nomount ram://8388608` GPT APFS "RAM" 0
    Started partitioning on disk4
    Unmounting disk
    Creating the partition map
    Waiting for partitions to activate
    Formatting disk4s2 as APFS with name RAM
    Mounting disk
    Finished partitioning on disk4
    /dev/disk4 (disk image):
       #:                       TYPE NAME                    SIZE       IDENTIFIER
       0:      GUID_partition_scheme                        +4.3 GB     disk4
       1:                        EFI EFI                     209.7 MB   disk4s1
       2:                 Apple_APFS Container disk5         4.1 GB     disk4s2

> diskutil的其他操作请自行学习哈，有内存盘可以自由做实验～

再体验一下速度～

![Blackmagic Disk Speed Test, 3GB file, APFS Disk](APFS%20Speed%20Test.png)


## 移动缓存文件夹

浏览器什么的都是Cache大户，特别是你 Chrome

### 移动 Chrome 默认缓存目录到内存盘

按照以往在Windows上的经验，首先找到缓存文件夹的文字，删除之，再在RAM Disk中创建新的缓存文件夹，
使用`ln -s` (or `mklink /D` on Windows) 把原始位置和内存盘位置连在一起，

网上已经有很多做法示例啦，这里就简单列出几个

```bash
cd /Volumes/RAM

mkdir -p Cache/Chrome

rm -rf ~/Library/Caches/Google

ln -s /Volumns/RAM/Library/Caches/Google ~/Library/Caches/Google
```

可是这种创建硬链接的方法有点小问题，比如如果没有创建对应文件夹，链接起点就会不可用
  而且每次都得运行这几行

---

这里呢，我来提供一个更完美的方案

在Windows上有个Cent Browser，我使用它是因为它能关闭DirectWrite，配合MacType可以提供很棒的字体渲染

在Cent Browser中，有一个设置，可以直接指定缓存目录。这可是程序级别的设置，不受硬链接限制。

去 chrome://version 看了启动的命令行，得知是一个`--disk-cache-dir`运行配置。

那简单呀，先在macOS上通过Terminal 加上命令行参数启动Chrome试试。

果然成功了，那么有几个方法。

1. 每次都用Terminal启动（太傻了
2. 直接修改Chrome的应用图标快捷方式，给它添加一个启动参数（修改应用程序，不可取
3. 创建一个自动操作，启动Chrome（太烦
4. 给Chrome的plist添加个配置

这里的重点是第四条，通过种种Google，
  得知有这么一个文件`~/Library/Preferences/com.google.Chrome.plist`
  Chrome会读取这个配置文件
  
可以通过下面这个来查看配置文件的内容（注意Plist文件是二进制编码，
即便使用[QuickLook插件](https://github.com/anthonygelibert/QLColorCode)能够查看，但也只能用专用工具编辑
```bash
defaults read com.google.Chrome
```

那么怎么编辑呢，果果来告诉你😇
```bash
defaults write com.google.Chrome DiskCacheDir /Volumes/RAM/Cache/Chrome
```

然后～ Chrome就会自动使用这个目录啦，甚至不需要移动旧的。

而且如果这个目录不存在，它直接不创建缓存文件

---
给 FireFox 也移动一下吧～

### 移动 Firefox 默认缓存目录到内存盘
根据Google出来，[这里](https://ccm.net/faq/40745-firefox-how-to-change-the-location-of-the-temporary-files-folder)的说明
  把大象放进冰箱只要几步
  
1. 在Firefox中打开 [about:config](about:config)
2. 找到 *browser.cache.disk.parent_directory* 这个键
3. 修改为想要的目录
4. 关上冰箱门（重启浏览器）

## 我想开机就享有速度

合起来的版本在Gist这里

<script src="https://gist.github.com/enihsyou/95811e7d3835a74cbb6dc80cddc9a994.js"></script>

那么创建一个自动操作App 然后开机启动？

NoNoNo
  我们用Global Agent

可以用Xcode，用LaunchControl等等工具，
  创建一个Plist，放到`/Library/LaunchAgents/local.ramdisk.plist`。
  内容大概如下
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>local.ramdisk</string>
	<key>Program</key>
	<string>/Users/enihsyou/.dotfiles/macOS/craeteRamDisk.sh</string>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>
```
其实就是在系统启动的时候，执行这个sh文件

---
\* Works on masOS 10.14 Mojave

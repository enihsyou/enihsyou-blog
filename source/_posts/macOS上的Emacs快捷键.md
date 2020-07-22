---
title: macOS上的Emacs快捷键
date: 2020-07-22 11:05:12
id: 49
tags:
  - macOS
categories:
  - 折腾
  - 效率
---

很多地方就是抄抄官网的快捷键列表就能取个 “macOS还有这些你不知道的快捷键！” 的标题。

但你知道macOS也能使用类似Bash上用的快捷键来操作文本么😃，甚至还能自定义。
别光被标题的Emacs吓到，操作极为舒适，特别在你交换Control(⌃)与Caps Lock(⇪)键之后。

<!--more-->

## 自带组合

其实快捷键列表这东西有好多途径可以获得

- 官方文档 https://support.apple.com/zh-cn/HT201236
- 知乎问题 https://www.zhihu.com/question/20021861
- CMD软件 https://www.mediaatelier.com/CheatSheet/
- 键盘贴膜 http://jcpal.com.cn/CN/ProductList23d0.html

这些快捷键是系统全局可用的，这就是macOS相比Windows的一大优势，
只要快捷键没有被覆盖，那么在各个软件可输入文字的地方都可以使用。

官方文档里其实已经很全面了，不过眼尖的用户可能会注意到 *文稿快捷键* 一节有一些Control开头的操作，
没错 他们就是本文的重点啦，**Emacs快捷键**。

这里把它们中一些常用的抽出来方便阅读：

| Key                          | Description                |
|------------------------------|----------------------------|
| {% kbd Ctrl %} + {% kbd f %} | 向前移动一个字符                   |
| {% kbd Ctrl %} + {% kbd b %} | 向后移动一个字符                   |
| {% kbd Ctrl %} + {% kbd a %} | 移至行或段落的开头                  |
| {% kbd Ctrl %} + {% kbd e %} | 移至行或段落的末尾                  |
| {% kbd Ctrl %} + {% kbd p %} | 上移一行                       |
| {% kbd Ctrl %} + {% kbd n %} | 下移一行                       |
| {% kbd Ctrl %} + {% kbd d %} | 删除插入点右边的字符。也可以使用 Fn-Delete |
| {% kbd Ctrl %} + {% kbd h %} | 删除插入点左边的字符。也可以使用 Delete 键  |
| {% kbd Ctrl %} + {% kbd k %} | 删除插入点与行或段落末尾处之间的文本         |
| {% kbd Ctrl %} + {% kbd o %} | 在插入点后新插入一行                 |

你可以用下面这段可编辑文字尝试一下🤓
<pre contenteditable="true">
Lorem Ipsum is simply dummy text of the printing and typesetting industry.
Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
when an unknown printer took a galley of type and scrambled it
to make a type specimen book.

Lorem Ipsum，也称乱数假文或者哑元文本，是印刷及排版领域所常用的虚拟文字。
由于曾经一台匿名的打印机刻意打乱了一盒印刷字体从而造出一本字体样品书，
Lorem Ipsum从西元15世纪起就被作为此领域的标准文本使用。
</pre>
不过由于是在浏览器中，可能会和其他快捷键冲突，列表中的不一定全都有效。
但你也可以打开一个文本编辑器(TextEdit.app)尝试尝试，这个肯定没问题。

## 终端组合

不论是Bash还是Zsh，你的常用终端也有不少自带的快捷键。

你可以在这些地方找到一些Cheatsheet
- https://github.com/fliptheweb/bash-shortcuts-cheat-sheet
- https://kapeli.com/cheat_sheets/Bash_Shortcuts.docset/Contents/Resources/Documents/index

除了Shell自带的以外你还能通过 `bind` `bindkey` 添加自定义快捷键，这里不展开了。

可是似乎有点太多了，比如移动光标这个简单的操作就有那么多。
![Bash中移动光标的操作](https://github.com/fliptheweb/bash-shortcuts-cheat-sheet/raw/master/moving_cli.png?raw=true)

| Key                          | Description    |
|------------------------------|----------------|
| {% kbd Ctrl %} + {% kbd f %} | **向前移动一个字符**   |
| {% kbd Ctrl %} + {% kbd b %} | **向后移动一个字符**   |
| {% kbd Ctrl %} + {% kbd a %} | **移至行或段落的开头**  |
| {% kbd Ctrl %} + {% kbd e %} | **移至行或段落的末尾**  |
| {% kbd Ctrl %} + {% kbd d %} | **删除插入点右边的字符** |
| {% kbd Ctrl %} + {% kbd h %} | **删除插入点左边的字符** |
| {% kbd Ctrl %} + {% kbd u %} | 删除到行首          |
| {% kbd Ctrl %} + {% kbd k %} | **删除到行尾**      |
| {% kbd Alt %} + {% kbd b %}  | 向前移动一个单词       |
| {% kbd Alt %} + {% kbd f %}  | 向后移动一个单词       |
| {% kbd Ctrl %} + {% kbd w %} | 向前删除到词首        |
| {% kbd Alt %} + {% kbd d %}  | 向后删除到词尾        |
| {% kbd Ctrl %} + {% kbd y %} | 把之前删除掉的文本粘贴回来     |

这里我把和macOS自带对快捷键一致的命令用粗体标示出来了。 \
可以看到有不少相似点，比如他们都是使用 {% kbd Ctrl %} + {% kbd a %} 移动到行首。 \
但是也增加了一些新的常用操作，比如{% kbd Alt %} + {% kbd b %} 移动到单词边界，这对命令编辑很有帮助。


## 自定义组合

但能不能更强一点！
当然能！比如把他们俩结合起来，让全系统都能拥有流畅的文本编辑体验。

很久以前我在寻找快捷键列表时知道了macOS一定程度上支持Emacs按键
也在互联网角落中搜索到了一篇很棒的[列表](https://www.hcs.harvard.edu/~jrus/site/system-bindings.html)。

当时就在想右边的代码是什么，能不能自定义？
最近我终于找到它的更多信息了。

文章表格右边的`Computerese`翻译过来叫计算机行话，或者说机器话，其实就是一些函数名。
可以在Apple文档的[NSStandardKeyBindingResponding](https://developer.apple.com/documentation/appkit/nsstandardkeybindingresponding)中找到，基本上读方法名就知道具体做什么的（🍎超长方法名的好处）。

接下来就是要知道写在哪和如何写了。
搜索互联网，GitHub网友又给出了答案。

- https://github.com/ttscoff/KeyBindings
- https://gist.github.com/trusktr/1e5e516df4e8032cbc3d

基本做法就几步

1. 创建或打开 `~/Library/KeyBindings/DefaultKeyBinding.dict` 文件
2. 贴入 https://github.com/ttscoff/KeyBindings/blob/master/DefaultKeyBinding.dict 的内容
3. 修改里面的内容以符合自己的需求
4. 修改会生效在重启或新开应用上

这里我给出一个我自己的配置，包含如下功能

| Key                                                   | Description        |
|-------------------------------------------------------|--------------------|
| {% kbd Ctrl %} + {% kbd f %}                          | 向前移动一个字符           |
| {% kbd Ctrl %} + {% kbd b %}                          | 向后移动一个字符           |
| {% kbd Ctrl %} + {% kbd a %}                          | 移至行或段落的开头          |
| {% kbd Ctrl %} + {% kbd e %}                          | 移至行或段落的末尾          |
| {% kbd Ctrl %} + {% kbd Shift %} + {% kbd a %}        | 选择到行或段落的开头         |
| {% kbd Ctrl %} + {% kbd Shift %} + {% kbd e %}        | 选择到行或段落的末尾         |
| {% kbd Ctrl %} + {% kbd p %}                          | 移动到上一行             |
| {% kbd Ctrl %} + {% kbd n %}                          | 移动到下一行             |
| {% kbd Ctrl %} + {% kbd d %}                          | 删除插入点右边的字符         |
| {% kbd Ctrl %} + {% kbd h %}                          | 删除插入点左边的字符         |
| {% kbd Ctrl %} + {% kbd u %}                          | 删除插入点与行或段落开头处之间的文本 |
| {% kbd Ctrl %} + {% kbd k %}                          | 删除插入点与行或段落末尾处之间的文本 |
| {% kbd Ctrl %} + {% kbd o %}                          | 在插入点后新插入一行         |
| {% kbd Option %} + {% kbd o %}                        | 在下面开启新的一行          |
| {% kbd Option %} + {% kbd Shift %} + {% kbd o %}      | 在上面开启新的一行          |
| {% kbd Command %} + {% kbd Enter %}                   | 在下面开启新的一行          |
| {% kbd Command %} + {% kbd Shift %} + {% kbd Enter %} | 在上面开启新的一行          |
| {% kbd Ctrl %} + {% kbd w %}                          | 向前删除到词首            |
| {% kbd Option %} + {% kbd d %}                        | 向后删除到词尾            |
| {% kbd Option %} + {% kbd y %}                        | 拷贝一行或一段            |
| {% kbd Ctrl %} + {% kbd y %}                          | 把之前删除掉的文本粘贴回来      |
| {% kbd Option %} + {% kbd w %}                        | 选择一个单词             |
| {% kbd Option %} + {% kbd s %}                        | 选择一整个行或段落          |
| {% kbd Option %} + {% kbd 1 %}                        | 设置一个标记             |
| {% kbd Option %} + {% kbd 2 %}                        | 跳转到这个标记            |

<code
  data-gist-id="1e0be087d316dd74779f9f0b9020bf12"
  data-gist-caption="DefaultKeyBinding.dict"
  data-gist-line="47-83"
  style="padding: inherit"></code>

更详细的说明文档可以参看🍎文档（又来）

https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/TextDefaultsBindings/TextDefaultsBindings.html

## 交换按键

Mac键盘，或者说几乎所有键盘布局，都把Ctrl(Control)键放置在了左下角。
当然还有一些笔记本会让Fn键占据左下角的位置，把Ctrl挤开。
个人极力吐槽这种配置，不能盲按。

不过在我把Ctrl和CapsLock键交换位置以后，世界变了🤯

小拇指按Ctrl键的体验比左手掌侧面按的体验好太多了！

那么大个CapsLock键却不怎么使用（除了在Mac上切换中英文输入法）简直是浪费。

![macOS改变键盘布局](macOS-change-keyboard-layout.png)

macOS下你可以在 `系统偏好设置 | 键盘 | 修饰键` 中将大写锁定键与Control键交换。
Windows下可以使用 CapsLock+ 或者[改注册表](https://xiaoh.me/2016/02/24/switch-capslock-ctrl/)


<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/gist-embed@1.0.4/dist/gist-embed.min.js"></script>

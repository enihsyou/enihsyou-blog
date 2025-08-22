---
title: 用Python来写各种各样的排序算法 (Part.1)
id: python-sorting-algorithms-part-1
tags:
  - Python
  - 算法
  - 随机数
categories:
  - 编程
date: 2016-06-01 13:10:00
---

刚开始学习Python的时候，就想着如何高效地完成计算。凭借着Python易懂的语法规则和清晰的思路展示，他成了我进行算法初步试验的不二选择。
<!--more-->

# 准备工作

首先当然是需要学会基础的Python语法啦，按照官方文档，各处教程零零散散的也有，完整课程的也有，利用起空闲时间学习。学习曲线很平缓，而且成就感很高，对初学者特别友好。

其次，我们需要一个能够编辑和运行Python文件的工具，我现在在Windows平台上用着[Python3.5](https://www.python.org/ "Python3.5")，虽然Python2和Python3.x的语法有些许差别，但编程重要的是思想，编程语言只是我们的工具，就像中文英语一样，都能表达我们的意思。对于IDE，安装完Python后自动赠送一个IDLE，不过我喜欢用Jetbrains家的[Pycharm](https://www.jetbrains.com/pycharm/ "Pycharm")。主要因为她特别智能，能够满足我对一个IDE的几乎全部要求。

接下来就只需要一些时间和开动脑筋了。

# 获取知识

从[wikipedia](https://en.wikipedia.org/wiki/Sorting_algorithm "Sorting algorithm")上我们可以知道有好多好多有效的算法，这些都是人类的智慧结晶呐。
从文档中我们可以知道: 对算法效率的评判手段有 用[大O符号](https://en.wikipedia.org/wiki/Big_O_notation "大O符号")标记的时间复杂度，**空间复杂度**; **稳定性**; **数据操作频率** 这几个概念。当然复杂度越低，算法的效率越高; 稳定性可以保证数据的相对顺序不被改变; 而数据操作频率 则是对要排序的数据操作了多少次。
一般而言，理想情况下排序算法的性能是$latex O(n)$，当然这只是理想，平均来说最高的能达到 $latex O (n \log n)$ 的性能，最坏是 $latex O(n^2)$。对于额外空间使用率来说，最好的能实现原地排序，即不需要额外空间，而有些算法却需要大小为 $latex n$ 的额外空间，这对于大量的数据来说可不是个好消息。

常见的有:

*   [冒泡排序](https://zh.wikipedia.org/wiki/%E6%8F%92%E5%85%A5%E6%8E%92%E5%BA%8F "冒泡排序") Bubble sort
*   [选择排序](https://zh.wikipedia.org/wiki/%E9%80%89%E6%8B%A9%E6%8E%92%E5%BA%8F "选择排序") Selection sort
*   [插入排序](https://zh.wikipedia.org/wiki/%E6%8F%92%E5%85%A5%E6%8E%92%E5%BA%8F "插入排序") Insertion sort
*   [堆排序](https://zh.wikipedia.org/wiki/%E5%A0%86%E6%8E%92%E5%BA%8F "堆排序") Heap sort
*   [归并排序](https://zh.wikipedia.org/wiki/%E5%BD%92%E5%B9%B6%E6%8E%92%E5%BA%8F "归并排序") Merge sort
*   [快速排序](https://zh.wikipedia.org/wiki/%E5%BF%AB%E9%80%9F%E6%8E%92%E5%BA%8F "快速排序") Quick sort
*   [希尔排序](https://zh.wikipedia.org/wiki/%E5%B8%8C%E5%B0%94%E6%8E%92%E5%BA%8F "希尔排序") Shell sort
*   [桶排序](https://zh.wikipedia.org/wiki/%E6%A1%B6%E6%8E%92%E5%BA%8F "桶排序") Bucket sort
*   ···

这些后面都会有提到哟 てへぺろ(•ω<)

# 生成随机数据

知道了基础的信息，掌握了基本技能之后就该开始真刀真枪地干了！

## 随机数列表

首先我们需要一个由随机数组成的数组列表。最简单直接地，Python官方标准库中有个叫[random](https://docs.python.org/3/library/random.html "random")的用来生成随机数的库，很明显就是为我们准备的。在我们需要她的时候只需要简单地`import random`就行。现在初始阶段，只是简单地需要一些随机正整数，强大的Python提供了[列表推导式](https://docs.python.org/3.5/tutorial/datastructures.html#list-comprehensions "列表推导式")来实现一行生成一个列表的功能。我们创建一个名为`generate_list`的函数来完成这个经常会被调用的操作。

```python
import random
def generate_list(number):
    """生成由`number`个 范围在[0, number)的元素组成的列表"""
    return [random.randrange(number) for _ in range(number)]
```
很简单的一行就能生成我们需要的数组了，当然效率在数目小的时候还是能够接受的，有挺大的优化空间的。

## 计时器

然后我们需要一个统计执行时间的小函数
有了随机数生成器，接下来还需要一个小秒表。在手上掐着一块表的方式肯定不现实，我们有计算机这么个强大的工具为什么不去使用呢！刚好Python官方也有一个库叫[time](https://docs.python.org/3/library/time.html#time.perf_counter "time")赶紧的`import time`. 这里面还有一些关于计时器如何选择的讨论，我们使用平台上精度最高的`time.perf_counter`.

同时为了将这个计时器应用到每个算法函数上:

*   可以将计时器装饰到每个算法上
*   可以在计时器函数上调用所有算法
*   可以让算法函数调用这个计时器

我认为第一个会更方便些，就是你了！

```python
import time
def count_time(func):
    """计时器装饰器"""
    def _deco(data):
        start_time = time.perf_counter()
        result = func(data)
        end_time = time.perf_counter()
        print("执行时间:", end_time - start_time)
        return result
    return _deco
```
这小家伙现在已经能够统计时间了，虽然改进的地方有很多，我们以后再来改进它。

* * *

准备工作完成后，接下来就是正戏了！

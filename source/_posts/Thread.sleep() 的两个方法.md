---
title: Thread.sleep() 的两个方法
date: 2018-05-09 21:27:01
tags: 
    - Java
categories:
  - 编程
id: 44
---

## 线程休眠的多种方法

当想要让当前进程暂时歇个几百毫秒，肯定见过 `Thread.sleep(long)` 方法。在各种模拟线程长时间工作的代码中时常见到。不过我看到他们有好几个变体

```java
public class Thread implements Runnable {
    public static native Thread currentThread();
    public static native void sleep(long millis) throws InterruptedException;
    public static void sleep(long millis, int nanos) throws InterruptedException;
}

public enum java.util.concurrent.TimeUnit {
    public void sleep(long timeout) throws InterruptedException;
}

// 让当前线程休眠3秒
TimeUnit.SECONDS.sleep(3);
Thread.currentThread().sleep(3000);
Thread.sleep(3000);
```

<!--more-->

### Thread.sleep(long) 和 Thread.currentThread()
`Thread.sleep(long)` 这个方法在JDK源码里可以看到它添加了 `native` 修饰符，说明是用平台相关代码实现的。其中参数是个毫秒数，比如填入 *3000* 毫秒代表 *3* 秒。不过因为是个整数，所以这个方法的精度是毫秒级。

如果想要精确到小数点后9位的纳秒级别，就得用`Thread.sleep(long, int)`方法啦，给第一个参数（毫秒数）填入*0*，再写纳秒数就行。

不过本文重点是 `Thread.currentThread().sleep(long)` 与 `Thread.sleep(long)` 两个方法的区别。

### 两者区别

结论是「**没有区别**」，甚至当使用 `Thread.currentThread()` 获得当前进程的引用后，再调用它的 *sleep(long)* 方法，聪明的IDE还会给个warning，提示说
> Static member 'java.lang.Thread.sleep(long)' accessed via instance reference

意思就是使用了实例对象访问静态方法。通常这么做是不必要的，因为没有对象也能通过引用类 来调用静态方法😂

### 现代化写法 java.util.concurrent.TimeUnit

这里还有个更快捷的**现代化**方法，就是使用 `TimeUnit.SECONDS.sleep(long)`，它是java.util.concurrent包里的类，在JDK1.5中加入。

`TimeUnit`是个枚举类直接点取它的枚举类型，有从 *NANOSECONDS* 、*MICROSECONDS* 一直到 *HOUR* 、 *DAYS* 的各类枚举定义。然后调用sleep就好。

不过语句从后往前读，比如 `TimeUnit.MILLISECONDS.sleep(30)` 意思是，**休息30毫秒个时间单位** 


参考: [Stack Overflow](https://stackoverflow.com/questions/3325942/thread-currentthread-sleeptime-v-s-thread-sleeptime)


## Bonus
有时候想要看编译后反编译的代码，不论是Java还是Kotlin，IntelliJ都能在你点击.class文件之后进行反编译。不过有时候无法触发，这是因为这个class在编译的时候没有写包名啦😂  如果是自己写的测试类，随便加一个就好

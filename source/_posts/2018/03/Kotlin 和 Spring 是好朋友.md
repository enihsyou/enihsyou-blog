---
id: kotlin-and-spring-are-good-friends
title: Kotlin 和 Spring 是好朋友
date: 2018-03-30 13:15:47
tags:
  - Kotlin
  - Java
  - Spring Boot
categories:
  - 编程
---

[Spring Framework](https://spring.io/blog/2017/01/04/introducing-kotlin-support-in-spring-framework-5-0)从5.0开始加入了完整的Kotlin语言支持~使用Kotlin DSL风格的构建语法，能切实感受到Java语言缺失的那份开发的快感。配合上免配置的Spring Boot框架，更是如虎添翼。

当然即便经过了从2016年到2018年的不断融合，Kotlin和Spring的结合依然还存在不少需要注意的地方。这篇文章主要列出果子开发中跳的坑，以及摸索(Google)出的解决方案。

<!--more-->
# Domain类

作为保存数据资源最基础的POJO对象，Kotlin中的`data class`可谓是满足了常见的那些根本不想写的功能。

一个常见的POJO需要getter、setter、equals、hashCode、toString方法，在没有IDE功能之前，get和set方法都是手写的；
然后各大IDE推出了快速创建getter、setter的功能，这项功能在宇宙级IDE IntelliJ IDEA中肯定提供，快捷键是<kbd>Alt</kbd>+<kbd>Insert</kbd>(<kbd>Cmd</kbd>+<kbd>N</kbd> on macOS)。但美中不足的是，如果修改了类的定义，比如添加或者删除了类的成员变量，这些方法需要手动相应修改；
现在Kotlin将这种操作简化成一个关键词`data class`，不仅不需要手写POJO方法，而且在类成员定义发生变化的时候，完全不需要更新代码！

比如这是一个找回密码的令牌类
```kotlin
typealias TokeType = String

@Entity
data class TokenDomain(
    @Id
    val token: TokenType,
    val expirationDate: LocalDateTime,
    var isUsed: Boolean
) {
    val isExpired get() = expirationDate <= LocalDateTime.now()
}
```

这段代码不仅使用了`data class`来设置数据类，而且使用了`typealias`语句声明一个[类型别名](https://www.kotlincn.net/docs/reference/type-aliases.html)。
类型别名能在IDE的类型提示中以注释的形式展示出来，更直观。

可以注意到Kotlin的类型定义十分适合需要大量DTO、VO的地方，简单几行便能创建一个类型安全还具有高度可读性的数据类。

反观Java选手，提供相同功能的Java类，则需要至少3倍的代码量。
对比之下 可读性下降到无法直视的地步。
```java
@Entity
class TokenDomain {
    @Id
    private String token;
    private LocalDateTime expirationDate;
    boolean isUsed;

    boolean isExpired() {
        return LocalDateTime.now().isAfter(expirationDate);
    }

    public TokenDomain(){}
    
    public TokenDomain(final String token, final LocalDateTime expirationDate, final boolean isUsed) {
        this.token = token;
        this.expirationDate = expirationDate;
        this.isUsed = isUsed;
    }

    public String getToken() {
        return token;
    }

    public void setToken(final String token) {
        this.token = token;
    }

    public LocalDateTime getExpirationDate() {
        return expirationDate;
    }

    public void setExpirationDate(final LocalDateTime expirationDate) {
        this.expirationDate = expirationDate;
    }

    public boolean isUsed() {
        return isUsed;
    }

    public void setUsed(final boolean used) {
        isUsed = used;
    }
    
    @Override
    public String toString() {
        return "TokenDomain{token='" + token + '\'' + ", expirationDate=" + expirationDate + ", isUsed=" + isUsed + '}';
    }

    @Override
    public boolean equals(final Object object) {
        if (this == object)
            return true;
        if (object == null || getClass() != object.getClass())
            return false;
        if (!super.equals(object))
            return false;

        final TokenDomain that = (TokenDomain) object;

        if (isUsed != that.isUsed)
            return false;
        if (token != null ? !token.equals(that.token) : that.token != null)
            return false;
        if (expirationDate != null ? !expirationDate.equals(that.expirationDate) : that.expirationDate != null)
            return false;

        return true;
    }

    @Override
    public int hashCode() {
        int result = super.hashCode();
        result = 31 * result + (token != null ? token.hashCode() : 0);
        result = 31 * result + (expirationDate != null ? expirationDate.hashCode() : 0);
        result = 31 * result + (isUsed ? 1 : 0);
        return result;
    }
}
```
如果还需要加上`@Nullable` `@NotNull`等null类型标记，更体现Kotlin的优越性。

所以Kotlin语言对于大型项目的开发和维护可是一副五星装备！

而且作为用在Kotlin上的代码注释`KDoc`相比`JavaDoc`来讲，编写舒适度也有十足提升。
它支持**Markdown**语法，顺带的也能使用`[]()`语法来引用函数参数、函数名的超链接。
`@return` `@param`标签也有相同的写法，完全没有学习成本。


# 构造器和依赖注入

Kotlin类支持主从构造器，主构造器可以放在类名后的括号里直接申明，就如同上面`data class`里class后面的括号。
申明继承也是使用 `:` 完成的。
使用Spring 依赖注入框架，配合上Kotlin可以有很漂亮的代码

比如这是一个Controller，需要注入一个Service。可以使用的方式有
- 设置一个类型为`Service?`的域，然后设置 `@Autowired` 注解
    ```kotlin
    class AccountController{
        @Autowired
        private var accountService: AccountService?
    }
    ```
    这样操作以后每次调用都需要判断null

- 使用`lateinit var`声明一个类型为`Service`的域，然后设置`@Autowired` 注解
    ```kotlin
    class AccountController{
        @Autowired
        private lateinit var accountService: AccountService
    }

    ```
    这样使用至少不用判断null了，可是它还是个`var`在代码高亮的时候可能会不好看

- 在类的构造器上直接声明`val servie: Service`，不需要注解！
    ```kotlin
    class AccountController(
        private val accountService: AccountService
    )
    ```
    这样既没有可变性，又没有可空性，简直完美😝

# 单例和Object Expression

Java中的单例模式比较废代码，在Kotlin中只需要object一个标注就行。

比如下面是一个关于密码的帮助类
```kotlin
/**密码相关的帮助类*/
object PasswordUtil {

    private val passwordEncoder = BCryptPasswordEncoder()

    /**
     * 对比纯文本未加密形式的[rawPassword]和数据库中已编码的[encodedPassword]
     * @param rawPassword 密码的原始格式
     * @param encodedPassword 数据库中加密过的密码
     * @exception BadCredentialsException 如果未通过验证则抛出异常
     */
    fun checkEquality(rawPassword: UserPassword, encodedPassword: UserPassword) {
        if (!passwordEncoder.matches(rawPassword, encodedPassword))
            throw BadCredentialsException()
    }

    fun encodePassword(password: UserPassword): String {
        return passwordEncoder.encode(password)
    }
}
```
在Kotlin中调用这个类的方法只需要使用类名即可，不需要获取到`INSTANCE`实例类似的方法。
可是在在Java中调用Kotlin代码，则需要先通过获取`INSTANCE`实例，再进行操作。

# Gradle

如果你使用Gradle，请往下阅读
根据Gradle新版本(4.0+)的文档，有几个比较大的变化。

1. Gradle plugins DSL
    还记得`build.gradle`默认生成的代码头上会有一段
    ```groovy
    buildscript {
        repositories {
            xxx
        }
        dependencies {
            classpath 'xxxxxx'
        }
    }
    apply plugin: xxx
    ```
    这段代码是应用Gradle plugin老旧的方法。

    如果使用plugins DSL，可以变成短短的样子。
    比如这是Kotlin + Spring Boot常用的插件组合
    ```groovy
    plugins {
        id "org.springframework.boot" version "2.0.1.RELEASE"
        id "io.spring.dependency-management" version "1.0.5.RELEASE"
        id "org.jetbrains.kotlin.jvm" version "1.2.40"
        id "org.jetbrains.kotlin.plugin.spring" version "1.2.40"
        id "org.jetbrains.kotlin.plugin.jpa" version "1.2.40"
        id "org.jetbrains.dokka" version "0.9.16"
    }
    ```
    DSL写法的一个不足是，它的版本号是字面量，以字符串的形式卸载代码里。并不能使用之前常见的作法，将版本号作为变量使用。

2. compile -> implementation

    在新版本的Gradle上，如果你曾经运行过 `Tasks > help > dependencies` ，能看到compile部分被加上了Deprecated的标记
    > compile - Dependencies for source set 'main' (deprecated, use 'implementation ' instead).

    那他们为什么要这么做呢。

    原因是在你打包的项目中，compile会把你的文件和你引用的包一起暴露给引用者。而implementation就不会。

    不过作为开发者的你确实想要暴露给外一个组件呢，比如编写的项目包含有一个名叫`project_api`的组件，或者它是个`project_library`的库组件。
    这时候只需要使用`api`标记。
    ```groovy
    plugins {
        id 'java-library'
    }
    dependencies {
        api 'xxxxx'
    }
    ```

    注意这里使用了一个叫 *java-library* 的插件，有了它才能使用api标记，不然代码提示里的 `apiElements` 并不是你需要的。

    ---
    那么如果跟上时代呢

    其实很简单，只需把`compile`一键替换成`implentation`即可！

    其实还有，将`runtime`替换成`runtimeOnly`；`testCompile`替换成`testImplementation`。
    将像暴露给外的组件使用`api`标记。

3. Fat jar，打包可执行的Kotlin项目

    我们分发项目成果的时候都希望简单一些，如果能直接打包一个jar丢过去，对方就能运行了那便是坠好的。
    Spring Boot 的插件提供了一个叫 `bootJar` 的任务，可以很好的完成目标任务。它在`Tasks > build > bootJar`下面，
    会将生成的jar文件放到`builds/libs`下面，直接使用`Java -jar`运行就好。因为所有的依赖项都在一个jar包里，所以体积会有点大。

    如果没有使用Spring Boot呢，那就只能自己手动操作。
    为jar任务添加一个打包操作即可。[参考来源](https://stackoverflow.com/a/44202463)
    ```groovy
    jar {
        from {
            configurations.compileClasspath.collect { it.isDirectory() ? it : zipTree(it) }
        }
    }
    ```


# 常见问题
## 写了Controller方法，却不能在Spring MVC Panel看到接口定义

如果是Java，请注意自己写的类和方法是不是`public`的。
如果是Kotlin，似乎现在的版本暂时还看不到。

## 设置了301转发，第二次修改之后永远看不到更改变化

可能你是浏览器301缓存的受害者，果子曾经在nginx上为一个域名设置了301转发，可是第一次设置错误。
使用Chrome浏览器打开发现不对，再次修改nginx配置文件却一直等不到生效。多次debug也失效

鸡汁的我选择用 **隐身模式** 打开，验证设置是正确的。
然后搜索啊搜索，最后发现是Chrome浏览器的301缓存的锅，而且这个缓存是近乎永久的🌚
参见[大佬们的讨论](https://stackoverflow.com/questions/9130422/how-long-do-browsers-cache-http-301s)得出解决方案如下

1. 打开 chrome://net-internals/ （或者 about://net-internals/ ）
2. 点击右上角黑色的向下的小箭头▼
3. 选择清除缓存 **Clear cache**
4. 大功告成

## 为什么我在Kotlin下面没有一些代码提示

IntelliJ IDEA的Spring插件，主要是面向Java平台的，
在Kotlin语境下就看不到比如Spring Data Repository的语法提示；
也没有JPA的图标和语法检查。

这都是以后期望厂家跟进修复的功能

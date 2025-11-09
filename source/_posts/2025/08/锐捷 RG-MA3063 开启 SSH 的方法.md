---
title: 锐捷 RG-MA3063 开启 SSH 的方法
id: enable-ssh-for-rg-ma3063
date: 2025-08-12T13:51:05+08:00
updated: 2025-11-09T18:01:03+08:00
tags:
  - 网络
categories:
  - 折腾
---

即便设置了桥接模式，锐捷 RG-MA3063 内建的 DNSmasq 依然会劫持 DNS 请求，导致解析局域网 DHCP 注册的主机名时灵时不灵。
互联网上对设备解锁 SSH 的方法好多都放在 Paywall 后面藏着掖着，其实只需要访问 `/__factory_verify_mode__` 端点就能免刷机开启 SSH 和 Telnet 服务。

<!-- more -->

{% note success "TL;DR" %}

节约时间先列答案，后文再述过程原因

```shellsession
$ curl http://192.168.10.1/__factory_verify_mode__
$ ssh 192.168.10.1 -l admin -o HostKeyAlgorithms=+ssh-rsa -o StrictHostKeyChecking=no
admin@192.168.10.1's password: wifi@cmcc
```

{% endnote %}

## 怪事起因

我的主路由器 **ASUS RT-AX86U** 在局域网用 DNSmasq 提供 DHCP 和 DNS 服务，这样可以用主机名获取 DNS 解析。
从淘宝办理的低价移动千兆宽带附带一个 **锐捷 RG-MA3063** 无线路由器，之前想着它的 EasyMesh 和华硕的不兼容也就吃灰好久。
但后来房间角落信号不好，就把它掏出来改到桥接模式当个 AP 使用，没想到它的无线性能意外地强过华硕😅。

![Network Topology](network-topology.png)
这是我的网络拓扑图（使用 [Isoflow | Network Diagrams](https://isoflow.io/) 绘制并截图），设备流量链路是这样： `Ruijie RG-MA3063 <=> ASUS RT-AX86U <=> HUAWEI HN8546X6-30 <=> Internet` 。

但局域网 DHCP 主机名 DNS 解析时灵时不灵，表现起来就是：

- 上次 `ping dhcphost` 还是通的，下次就不行
- 查询 IPv6 的 DNS 服务器地址不行，但通过 IPv4 就可以
- 使用 `nslookup -vc` 以 TCP 连接可以，用 UDP 就不行
- 不经过 RG-MA3063 的设备一切正常

另外在路由器和终端设备抓包发现几个奇怪现象：

- 观测到会往 `114.114.114.114` 发 DNS 请求，可我整个链路没有设置过这个 DNS 地址
- 抓包看到的 DNS 请求来源是一个不认识的 IPv6 地址，猜测是中间的桥接路由器的地址
- 还把上级网络的 DNS 后缀丢了，本来主机带后缀的全名是 `ps5.home.kokomi.site`，现在变成 `ps5.lan` 发往上游 DNS

以及下挂设备虽然处于 `192.168.9.0/24` 网段，在没设置静态路由的情况下，但居然能直接访问 `192.168.10.1` 这个地址（锐捷路由的默认管理 IP）。

至于如何定位是这个设备的原因，以及开启 SSH 后如何解决这个问题，可以跳转 [2025-08-12 | 局域网 DHCP 主机名 DNS 解析时灵时不灵 | 涼果笔记](https://obsidian.kokomi.me/Diary/2025-08-12#%E5%B1%80%E5%9F%9F%E7%BD%91-dhcp-%E4%B8%BB%E6%9C%BA%E5%90%8D-dns-%E8%A7%A3%E6%9E%90%E6%97%B6%E7%81%B5%E6%97%B6%E4%B8%8D%E7%81%B5)。

## 参考信息

在动手前查了很多网页和教程，但大部分都难以访问，但还是有部分有价值的内容。

- [锐捷MA3063 信号相当强，59元入手刷机openwrt 冲！哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1QQ4y1M7td/) 刷机教程，操作太糙了，还得买 TTL 高风险拆机刷机，Pass
- [锐捷MA3063系列中国移动定制版免拆开启ssh、删除插件、解除锁网限制(更新全版本通用)-OPENWRT专版-恩山无线论坛 - Powered by Discuz!](https://www.right.com.cn/forum/thread-8377493-1-1.html) 恩山的信息向来封闭，我没有权限访问
  - [【转载】新版锐捷MA3063开启SSH方法 - 厂商技术专区 - 通信人家园 - Powered by C114](https://www.txrjy.com/thread-1352289-1-1.html) 但好在有好人转载了，注册回帖就能下载「新版锐捷 MA3063 开启 SSH 方法」。里面介绍了一种往隐藏路径构造请求来打开开发者模式的方式，见 [埋点脚本注入](#埋点脚本注入)。
- [锐捷RG-MA3063另类的 开启SSH 原机openwrt 刷机 做集客AP 拆机 交换机 - 数码罗记](https://godsun.pro/blog/rui-jie-rg-ma3063) 这里不同于恩山的内容，独立提供了进入工厂模式的新方法，[一键开启开发者模式](#一键开启开发者模式) 懒人无感开启 SSH，并且提供了解密的关键密码。对我提供了极大的帮助

解锁后会发现 Openwrt 版本非常古老，但有人尝试过刷机又或者编译，可以看看：

- [ipq50xx: Support for IPQ5018 MP03.5-c1 | GitHub hzyitc/openwrt-redmi-ax3000](https://github.com/hzyitc/openwrt-redmi-ax3000/issues/59)
- [中移RAX3000Q路由器解锁telnet/ssh及使用内置的OpenWrt](https://blog.imlk.top/posts/rax3000q-get-shell/)

## 设备信息

在介绍之前先看看我手头的设备是否和你相同，未来固件版本保不齐会失效。
不过很神奇的，每个地方显示的版本号都不一样 😅

```txt title="管理页面 - 设备详细信息"
设备型号： RG-MA3063
硬件版本： 1.00
软件版本： MA_2.1(3)
```

```make title="/etc/rj_issues"
System description      : RG-MA3063-<wuhu3-cmcc-sh>
System hardware version : 2.00
System software version : MA_2.1(3)B6P13, Release(10211501)
Build time              : 2023/09/15 01:04:23
```

```txt title="OpenWrt LuCI"
Software: MA_1.1(1) / Model: RG-MA3063 / Vendor: Ruijie

Model:            Qualcomm Technologies, Inc. IPQ5018/AP-MP03.5-C1
Firmware Version:	OpenWrt Chaos Calmer 15.05.1 6f77ae728+r49254 / LuCI OW_5_0_PJ6_S9 branch (0.12.1)
Kernel Version:  	4.4.60
```

## 操作流程

### 通过网络连接到设备

我为 RT-AX86U 的 LAN 分配到 `192.168.9.0/24` 网段，RG-MA3063 自动 DHCP 到了 `192.168.9.6` 这个 IPv4 地址。用它可以访问到锐捷的管理页面。

然而日常使用中发现，如果 RT-AX86U 的 DHCP 出问题不工作了，处于桥接模式的 RG-MA3063 居然会用它的 DHCP 给（有线、无线）连接到它的设备分配地址，经常导致一众小 IoT 设备拿到了 `192.168.10.0/24` 子网的 IP，只能断网重启。
所以通过这一现象，如果连接到它的 Wi-Fi，其实也可以用 `192.168.10.1` 这个地址访问到它 🤣

{% note info 至于为什么，剧透一下是分配了两个 IP 到同一张网卡上 %}

```shellsession title="Dual IPv4 on One Interface"
# ip -4 addr show br-lan
13: br-lan: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    inet 192.168.9.6/24 brd 192.168.9.255 scope global br-lan
       valid_lft forever preferred_lft forever
    inet 192.168.10.1/24 brd 192.168.10.255 scope global br-lan
       valid_lft forever preferred_lft forever
```

{% endnote %}

> 另外如果你的路由器上有开启了 TProxy 的 MerlinClash，并且遇到局域网内跨网段访问不通的问题，可以看看我的解决方案 [2025-08-09 | Merlin Clash 的 TProxy IPTables 影响局域网内跨子网访问 | 涼果笔记](https://obsidian.kokomi.me/Diary/2025-08-09#merlin-clash-%E7%9A%84-tproxy-iptables-%E5%BD%B1%E5%93%8D%E5%B1%80%E5%9F%9F%E7%BD%91%E5%86%85%E8%B7%A8%E5%AD%90%E7%BD%91%E8%AE%BF%E9%97%AE)

## 进入工厂模式开启远程访问

B 站播放最高的视频教你如何拆机接 TTL 刷机，本着「刷机有风险」的观念，最好不刷机。好在互联网还是有简单些的方法的

### 一键开启开发者模式

这个方法来自数码罗记文章，操作非常简单，浏览器打开 [`http://192.168.10.1/__factory_verify_mode__`](http://192.168.10.1/__factory_verify_mode__)，记得替换成你的设备 IP

> 猜测是通过解包固件找到的这个路由，
> 从固件解包来看，这个路由实际是在触发由 `/eweb/api/handler.lua` 调用 `/etc/init.d/factory_mode_cfg.sh enable` 的指令

返回 `{"result": "Pass"}` 就算成功，甚至都不需要去网页登录。
现在防火墙会允许来自局域网对 SSH、FTP、Telnet 端口的访问，但**不会** 打开 8088 （OpenWrt LuCI）端口

> 数码罗记的文章说 *联网后会被禁止 SSH 登录* ，但实测并不会。
> 不用断网哦，连着网有问题还能问问 AI

### 埋点脚本注入

这个方法来自恩山论坛，需要先在浏览器网页登录，再进入开发者工具控制台输入

```javascript
fetch("http://192.168.10.1/api/v1/lua/DevelopMode/develop_mode_set", { method: "POST", body: JSON.stringify({ developMode: "1" }) });
```

上面 [一键开启开发者模式](#一键开启开发者模式) 只会打开 22 端口访问，这个可以一并打开 8088 端口访问。

> 从源码分析来看，这个路由实际是在触发 `/eweb/script/DevelopMode.lua` 调用 `/etc/init.d/dev_port_config.sh enable` 的指令。

### ~~狂点版本号~~

这个方法也是来自数码罗记文章，不过从 `/eweb/script/Upgrade.lua` 的注释来看，2023.06.20 开始不再提供强制升级功能，所以应该失效了

- 登录路由器后台
- 进入 `系统设置 > 系统升级 > 本地升级`
- 疯狂点击设备型号 5 次以上 - 开启强制升级！
- 接着狂戳当前版本 5 次 - 开启开发者模式！

## 远程连入

上面的操作开启了 SSH 和 Telnet 服务，可以尝试连接了。

不过设备的 dropbear 版本还停留在 `v2019.78` 并且只支持 RSA 算法，所以现代设备 SSH 过去前需要配置一些兼容性选项。不然会遇到 `no matching host key type found. Their offer: ssh-rsa`、`send_pubkey_test: no mutual signature algorithm` 等错误

SSH 和 Telnet 使用用户名 `admin` 密码 `wifi@cmcc`

```shellsession
$ ssh 192.168.10.1 -l admin -o "HostKeyAlgorithms +ssh-rsa"
admin@192.168.10.1's password: wifi@cmcc

BusyBox v1.30.1 () built-in shell (ash)

     MM           NM                    MMMMMMM          M       M
   $MMMMM        MMMMM                MMMMMMMMMMM      MMM     MMM
  MMMMMMMM     MM MMMMM.              MMMMM:MMMMMM:   MMMM   MMMMM
MMMM= MMMMMM  MMM   MMMM       MMMMM   MMMM  MMMMMM   MMMM  MMMMM'
MMMM=  MMMMM MMMM    MM       MMMMM    MMMM    MMMM   MMMMNMMMMM
MMMM=   MMMM  MMMMM          MMMMM     MMMM    MMMM   MMMMMMMM
MMMM=   MMMM   MMMMMM       MMMMM      MMMM    MMMM   MMMMMMMMM
MMMM=   MMMM     MMMMM,    NMMMMMMMM   MMMM    MMMM   MMMMMMMMMMM
MMMM=   MMMM      MMMMMM   MMMMMMMM    MMMM    MMMM   MMMM  MMMMMM
MMMM=   MMMM   MM    MMMM    MMMM      MMMM    MMMM   MMMM    MMMM
MMMM$ ,MMMMM  MMMMM  MMMM    MMM       MMMM   MMMMM   MMMM    MMMM
  MMMMMMM:      MMMMMMM     M         MMMMMMMMMMMM  MMMMMMM MMMMMMM
    MMMMMM       MMMMN     M           MMMMMMMMM      MMMM    MMMM
     MMMM          M                    MMMMMMM        M       M
       M
 ---------------------------------------------------------------
   For those about to rock... (Chaos Calmer, 6f77ae728+r49254)
 ---------------------------------------------------------------
root@OpenWrt:/#
```

我建议登录后立即添加 SSH 密钥对，并把连接信息记录在自己的 `~/.ssh/config` 上免得以后重复输入。
注意使用的客户端密钥对也得是 RSA 算法的，ed25519 无法使用。

```ssh-config title="~/.ssh/config"
Host 192.168.10.1
  User admin
  HostKeyAlgorithms +ssh-rsa
  PubkeyAcceptedAlgorithms +ssh-rsa
```

> 在 /etc/shadow 中密码记录为 `admin:$1$G.w1Kd/c$OxHqp4GMbBQ9UY2KRulmg/:18815:0:99999:7:::`。
> 这密码也就是数码罗记提到了，不然还真猜不到。
> 好在就算不知道也还有后路，进入 OpenWrt 后台可以改。

## 进入后台

执行 [埋点脚本注入](#埋点脚本注入) 或者登录上去手动 `/etc/init.d/dev_port_config.sh enable` 开启开发者模式后， [`192.168.10.1:8088`](http://192.168.10.1:8088) 便能访问 OpenWrt LuCI 界面了。使用用户名 `root` 和 *任意* 密码登入。空密码都行，其实直接点登录就行。

{% note warning %}
不要点击 `System > Startup`，会回到非开发者模式
{% endnote %}

到此拿到了 OpenWrt 后台就属于获得了最高权限。

## 后续操作

路由器是个 Overlay 文件系统，对 ROM 的变更重启并不会重置，并且恢复出厂可以治疗大部分毛病，随意折腾。
我的目标是 [关闭 DNS 劫持](#关闭%20DNS%20劫持)，有高级需求的可以参考其他刷机教程。

### 添加 SSH 密钥登录

```shell
vi /etc/dropbear/authorized_keys
chmod 0600 /etc/dropbear/authorized_keys
```

也可以在 OpenWrt LuCI 后台操作，注意公钥得是 RSA 算法的。

### 停止每两分钟 ping 一次 `baidu.com`

爱好观察日志的我发现，每隔几分钟有一个对 `www.baidu.com` 的 DNS 请求，是 `/sbin/status_collect.sh` 在干活，禁用之

```shell
/etc/init.d/rg_status_collect stop
/etc/init.d/rg_status_collect disable
```

### 禁用对内的防火墙

删除阻挡我们登入 SSH / OpenWrt 的防火墙规则，下次重启不用再解锁一遍。
在 `/etc/config/rg_firewall` 文件中，删除 `dev_no_wan_ping`、`dev_no_8088` 等条目。

原文件都有哪些内容见 [2025-08-12 | 局域网 DHCP 主机名 DNS 解析时灵时不灵 | 涼果笔记](https://obsidian.kokomi.me/Diary/2025-08-12#%E5%B1%80%E5%9F%9F%E7%BD%91-dhcp-%E4%B8%BB%E6%9C%BA%E5%90%8D-dns-%E8%A7%A3%E6%9E%90%E6%97%B6%E7%81%B5%E6%97%B6%E4%B8%8D%E7%81%B5)

### 关闭 DNS 劫持

在 `/etc/config/rg_firewall` 中删掉几条 `dnsv4_hijack` 的规则。或者直接执行下面这段

```shell
iptables  -t nat -D PREROUTING -i br-lan -p udp -m udp --dport 53 -j DNAT --to-destination 192.168.10.1
ip6tables -t nat -D PREROUTING -i br-lan -p udp -m udp --dport 53 -j DNAT --to-destination fe80::e25d:54ff:fe7c:7f4

ebtables -t broute -D BROUTING -p IPv4 --ip-proto udp --ip-dport 53 -j dnat --to-dst E0:5D:54:7C:07:F4 --dnat-target ACCEPT
ebtables -t broute -D BROUTING -p IPv6 --ip6-proto udp --ip6-dport 53 -j dnat --to-dst E0:5D:54:7C:07:F4 --dnat-target ACCEPT
```

然而好景不长，删掉的规则定时、重启都会重新添加回来，也包括删掉的 DNS 服务器部分，肯定是有进程在动手脚。

找啊找没头绪，我都跟着路径找到 `OpenWrt Chaos Calmer 15.05.1 6f77ae728+r49254` 版本的 `netifd - 2015-12-16-245527193e90906451be35c2b8e972b8712ea6ab` 包的源代码这段 [netifd/interface-ip.c at 245527193e90906451be35c2b8e972b8712ea6ab · openwrt/netifd](https://github.com/openwrt/netifd/blob/245527193e90906451be35c2b8e972b8712ea6ab/interface-ip.c#L1176)。但结合设备上的配置，OpenWrt 固件部分是没动的，代码怎么看怎么没问题。

就在想要放弃转为写启动脚本删规则的时候，执行了一下 `strings /sbin/rg_mng | grep hijack` 发现很多关键字。再打开 IDA 反编译看一波逻辑，防火墙规则里 DNS 劫持的部分确实是它加的！看了下其他逻辑，我也不想要，直接就是一个禁止启动 😠

```shell
/etc/init.d/rg_mng stop
/etc/init.d/rg_mng disable
```

{% note info %}
这么操作后 `/etc/config/rg_firewall` 文件内容未来不会被复写，需要再手动去把已经生成的规则删了。
不过注意不要把 `web_hijack` 这条规则删了，否则会导致无法从内网访问管理页面
{% endnote %}

不过始终没有找到谁往 `/var/resolv.conf.auto` 里加的 114.114.114.114，不过作为个桥接路由，不连到它的 DNS 服务器上管它呢。
调用 `ubus call dnsmasq metrics` 看看，应该不再有新的 dns_queries 了，局域网内通过 DHCP 注册的 DNS 记录也能正常查询了 💖

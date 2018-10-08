---
title: Ubuntu 18.04 × 网易云音乐
date: 2018-08-24 16:00:35
tags:
  - Ubuntu
  - 网易云
id: 46
categories:
  - 折腾
---

很高兴在[官网](https://music.163.com/#/download)上看到网易云音乐提供Linux的二进制安装包。
有deepin15和ubuntu16.04两个选项，且都是64位版本的。我是Ubuntu18.04，想想看应该没问题

迫不及待下载安装！

<!--more-->

## 安装
下载就不用教了吧。
点击上面的官网超链接，点击Linux（注意需要启用JavaScript哦）选择Ubuntu16.04版本就会自动下载啦

```bash
cd ~/Downloads/
sudo dpkg -i netease-cloud-music_1.1.0_amd64_ubuntu.deb 

sudo apt install -f
```
简单解释一下每一行

- 第一行切换到文件下载目录，我这默认下载路径是用户目录下的Downloads文件夹
- 第二行，安装deb二进制安装包
    在这里可能会很多包依赖的错误，暂时忽略它
- 第三行，一个`-f`参数用来修复依赖错误～

## 无法启动

安装完了当然是找到应用程序图标点击启动呀！
可是肿么点了之后没反应呢？？？

上网一搜，关键词 *Ubuntu 18.04 网易云 打不开*
马上就有简书的答案解决问题，链接参照：https://www.jianshu.com/p/116bf1a1a36d

第一个`--no-sandbox`，加了无效，跳过


第二个`sudo`，加了能用…
但你一个音乐播放器居然需要root权限，是不是太过火啦，慎用

第三个玄学方法。还真能用，先点开应用程序，再点右上角-电源按钮。
对，就那个“取消-重启-关机”三个按钮的60秒界面。
这时候应该能看到网易云音乐从背景中一跃而出…

## 配置失效

玄学方法虽好，但有个严重的问题！
配置文件不保存

具体表现就是，每次重启动网易云的时候，都会回到未登录状态，且所有设置都回归出厂设置

想找找看log文件，没找到…

那就用Terminal运行`netease-cloud-music`命令

      netease-cloud-music                
    [0824/153835.432001:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: UPDATE cookies SET last_access_utc=? WHERE creation_utc=?
    [0824/153835.432102:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: UPDATE cookies SET last_access_utc=? WHERE creation_utc=?

    [0824/153835.432516:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: DELETE FROM cookies WHERE creation_utc=?
    [0824/153835.432562:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: DELETE FROM cookies WHERE creation_utc=?

    [0824/153835.432676:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: INSERT INTO cookies (creation_utc, host_key, name, value, encrypted_value, path, expires_utc, secure, httponly, firstpartyonly, last_access_utc, has_expires, persistent, priority) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    [0824/153835.441225:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: INSERT INTO cookies (creation_utc, host_key, name, value, encrypted_value, path, expires_utc, secure, httponly, firstpartyonly, last_access_utc, has_expires, persistent, priority) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)

    [0824/153835.683974:ERROR:connection.cc(1963)] DOMStorageDatabase sqlite error 14, errno -2: unable to open database file, sql: -- sqlite3_open()
    [0824/153835.684027:ERROR:dom_storage_database.cc(180)] Unable to open DOM storage database at /home/enihsyou/.cache/netease-cloud-music/Cef/Cache/Local Storage/orpheus_orpheus_0.localstorage error: sql::Connection has no connection.
    [0824/153835.847974:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: UPDATE cookies SET last_access_utc=? WHERE creation_utc=?
    [0824/153835.848087:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: UPDATE cookies SET last_access_utc=? WHERE creation_utc=?
    [0824/153835.848119:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: INSERT INTO cookies (creation_utc, host_key, name, value, encrypted_value, path, expires_utc, secure, httponly, firstpartyonly, last_access_utc, has_expires, persistent, priority) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    [0824/153836.102480:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: UPDATE cookies SET last_access_utc=? WHERE creation_utc=?
    [0824/153836.102536:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: INSERT INTO cookies (creation_utc, host_key, name, value, 
    [0824/153836.102671:ERROR:connection.cc(1963)] Cookie sqlite error 8, errno 0: attempt to write a readonly database, sql: INSERT INTO cookies (creation_utc, host_key, name, value, encrypted_value, path, expires_utc, secure, httponly, firstpartyonly, last_access_utc, has_expires, persistent, priority) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    08-24, 15:38:36 [Error  ] [                          0] [base]::WriteTestFile() failed! , path: "/home/enihsyou/.cache/netease-cloud-music/StorageCache/webdata/file/disc_data"

为了数据展现，删减了重复的一部分。
但重点大家也能看到，**readonly database**, **unable to open storage database at ...**

然后去这个路径看看，里面是的几个文件夹是归属于root的，肯定不能写入呀

    sudo chown -R enihsyou:enihsyou /home/enihsyou/.cache/netease-cloud-music/

执行这个就修复了问题啦，注意把enihsyou换成自己的用户名，还有修改对应路径。总之把文件夹权限改对来即可～

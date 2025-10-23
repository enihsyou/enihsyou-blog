---
title: 投入Hexo框架的怀抱(･ω´･ )
id: embracing-hexo-framework
date: 2017-05-18 19:40:42
tags: 
  - 网站
  - WordPress
  - Hexo
  - 美化
categories:
  - 强化
---
![Hexo](hexo-logo-avatar-transparent-background.png)

[Hexo](https://hexo.io/zh-cn/)是个博客框架，通过解析markdown写作的文档，生成静态HTML网页，以超快的速度著称。

在网上找文章的时候，时常见到博主炫酷的主题，超快的加载速度，
一般在页脚都会注明使用的框架和主题。就比如果现在用的，Hexo框架+NexT主题。

以前的WordPress版本还活着呢，在左边**[旧家](https://enihsyou.wordpress.com/)**页面里。当做以往的记忆啦(･ω´･ )

<!--more-->

# 构建Hexo框架
Hexo的官网有详细的[使用教程](https://hexo.io/zh-cn/docs/)
我就是按照教程一步步走的，验证了教程的完备性
## 安装Node.js 和 Git
其中的Git完全是程序员必备，Node.js只需要去官网下一个安装包即可，然后就是一键的`npm install -g hexo-cli`，当然当然首先需要cd到目标文件夹里去。
## 初始化Hexo
Hexo的命令也是很常见的格式，init代表初始化，server代表服务器，generate代表生成结果文件…

简单到我们只需要四行 就能完成初始化，并在localhost:4000下启动网站。
```bash
$ hexo init enihsyou.com
$ cd enihsyou.com
$ npm install
$ hexo server
```
## 安装主题
我选择了[NexT](http://theme-next.iissnan.com/)主题，还有[Material](https://material.viosey.com/)主题做备选。
一个是简洁风，另一个是Material风，各有各的特色，前后调换了几次 最终选择了NexT.Muse主题

安装方式也是简单直接，先切换到主题文件夹(themes)文件夹，然后运行下列命令
```bash
$ cd enihsyou.com/themes
$ git clone https://github.com/iissnan/hexo-theme-next themes/next
```

接下来只需要把网站配置文件的主题修改就好啦：
{% codeblock lang:yaml "_config.yml" %}
theme: next
{% endcodeblock %}
## 配置主题
### 给名字加上注音
HTML有个`<ruby>`标签，可以用来给文字加注音。
比如我的九条涼果就可以写成
```html
<ruby>
    九<rp>(</rp><rt>Ku</rt><rp>)</rp>
    条<rp>(</rp><rt>jō</rt><rp>)</rp>
    涼<rp>(</rp><rt>Ryō</rt><rp>)</rp>
    果<rp>(</rp><rt>ka</rt><rp>)</rp>
</ruby>
```
其中`<rp>`标签会在浏览器不支持注音标记的时候，显示出来；`<rt>`标签是注音内容，如果不支持注音，则显示在同一行。
### 设置友情链接
友链代表着关系，怎么能没有几个朋友呢 显得多孤单

NexT主题就提供了侧边栏中显示友链的功能，找到侧边栏设置部分，就在它的下面。
`links_layout: block`可以理解为单行显示，`inline`就是内联显示，像文本一样。
使用YAML语法 直接写在links里面就行
```yaml
# Blog rolls
links_title: 友情链接
links_layout: block
#links_layout: inline
links:
  梦与狂想的王国: https://applehan.org/
  251(猫C) aka 电酱！: http://251.9cmsound.com/
  淺夏の部屋: http://sennatsu.com/
```
### 设置社交链接
也在侧边栏设置那那块，上面social块，用键值对存放链接地址，下面social_icons块 给每一个键设置图标。用的FontAwesome图标，像豆瓣 知乎这种国内社区就不全面了。
```yaml
# Social Links
# Key is the link label showing to end users.
# Value is the target link (E.g. GitHub: https://github.com/iissnan)
social:
  GitHub: https://github.com/enihsyou
  Twitter: https://twitter.com/enihsyou
  微博: http://weibo.com/enihsyou
  豆瓣: https://douban.com/people/104858749
  知乎: https://www.zhihu.com/people/enihsyou
  Google+: https://plus.google.com/u/0/108566891153597019822
  Youtube: https://www.youtube.com/channel/UCvOYzUvke259Dfkj74m8ogg
  About.me: https://about.me/enihsyou
  Bangumi: https://bgm.tv/user/kacyan
  Last.fm: https://www.last.fm/user/guoka
  Steam: https://steamcommunity.com/id/enihsyou
  Email: mailto://haruto@enihsyou.com
  Telegram: https://telegram.me/enihsyou
  QQ: tencent://message/?uin=1131626817&site=enihsyou.com&menu=yes

# Social Links Icons
# Icon Mapping:
#   Map a menu item to a specific FontAwesome icon name.
#   Key is the name of the item and value is the name of FontAwesome icon. Key is case-senstive.
#   When an globe mask icon presenting up means that the item has no mapping icon.
social_icons:
  enable: true
  # Icon Mappings.
  # KeyMapsToSocialItemKey: NameOfTheIconFromFontAwesome
  GitHub: github
  Twitter: twitter
  微博: weibo
  豆瓣:
  知乎:
  Google+: google-plus
  Youtube: youtube-play
  About.me:
  Bangumi: smile-o
  Last.fm: lastfm
  Steam: steam
  Email: envelope-o
  Telegram: telegram
  QQ: qq
```
其中QQ聊天协议，可以用简单的形式：`tencent://message/?uin=<QQ号>`
像我这种没有特别需求都只在QQ上呆着的，望着满世界青年都在用微信，内心是矛盾的。

### 利用公共CDN加速访问
网页要加载许多脚本，这时候就该利用互联网大腿的公共CDN加快速度。
这里有几个栗子：
* [百度静态资源公共库](https://cdn.code.baidu.com) 百度家的测速文件
* [七牛云CDN](https://staticfile.org)
* [BootCDN](https://bootcdn.cn) 这里的库文件比较新
* [Google](https://developers.google.com/speed/libraries/) 国内当然不能用啦

我随便选择了一些填进去
```yaml
# Script Vendors.
# Set a CDN address for the vendor you want to customize.
# For example
#    jquery: https://ajax.googleapis.com/ajax/libs/jquery/2.2.0/jquery.min.js
# Be aware that you should use the same version as internal ones to avoid potential problems.
# Please use the https protocol of CDN files when you enable https on your site.
vendors:
  # Internal path prefix. Please do not edit it.
  _internal: lib

  # Internal version: 2.1.3
  jquery: https://apps.bdimg.com/libs/jquery/2.1.3/jquery.min.js

  # Internal version: 2.1.5
  # See: http://fancyapps.com/fancybox/
  fancybox: https://apps.bdimg.com/libs/fancybox/2.1.5/jquery.fancybox.min.js
  fancybox_css: https://apps.bdimg.com/libs/fancybox/2.1.5/jquery.fancybox.min.css

  # Internal version: 1.0.6
  # See: https://github.com/ftlabs/fastclick
  fastclick: https://apps.bdimg.com/libs/fastclick/1.0.0/fastclick.min.js

  # Internal version: 1.9.7
  # See: https://github.com/tuupola/jquery_lazyload
  lazyload: https://apps.bdimg.com/libs/jquery-lazyload/1.9.5/jquery.lazyload.min.js

  # Internal version: 1.2.1
  # See: http://VelocityJS.org
  velocity: https://cdn.bootcss.com/velocity/1.2.1/velocity.min.js

  # Internal version: 1.2.1
  # See: http://VelocityJS.org
  velocity_ui: https://cdn.bootcss.com/velocity/1.2.1/velocity.ui.min.js

  # Internal version: 0.7.9
  # See: https://faisalman.github.io/ua-parser-js/
  ua_parser: https://cdn.bootcss.com/UAParser.js/0.7.9/ua-parser.min.js

  # Internal version: 4.6.2
  # See: http://fontawesome.io/
  fontawesome: https://cdn.bootcss.com/font-awesome/4.7.0/css/font-awesome.min.css

  # Internal version: 1
  # https://www.algolia.com
  algolia_instant_js:
  algolia_instant_css:

  # Internal version: 1.0.0
  # https://github.com/hustcc/canvas-nest.js
  canvas_nest: https://cdn.bootcss.com/canvas-nest.js/1.0.1/canvas-nest.min.js
```

# 替换WordPress
保留旧家的记忆，把WordPress移动到子目录去，操作也不复杂
我启用了WordPress的多站点功能，需要修改`wp-config.php`文件
```php
$home = 'https://'.$_SERVER['HTTP_HOST'].'/wordpress'; #获取当前访问的域名
$siteurl = 'https://'.$_SERVER['HTTP_HOST'].'/wordpress';
define('WP_HOME', $home);
define('WP_SITEURL', $siteurl);

/** WordPress目录的绝对路径。 */
if ( !defined('ABSPATH') )
    define('ABSPATH', dirname(__FILE__) . '/wordpress');
```
注意到那几个添加上去的`/wordpress`，然后移动WordPress到子文件夹即可

# 部署文件
Hexo提供一键式的部署功能，不过不太适合我
只能用另一种手动的方式，把生成的文件放到服务器上就可以了
```bash
hexo generate
```
这行命令会在根下的public文件夹生成网站文件，打包移动到网站目录覆盖替换。

* * *

你果今晚失恋了呢，上次真心还是5年前呢吧～

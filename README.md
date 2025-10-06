# Source for Personal Blog Site

[![本项目使用 EdgeOne Pages 部署](https://cdnstatic.tencentcs.com/edgeone/pages/deploy.svg)](https://console.cloud.tencent.com/edgeone/pages/new?repository-url=https%3A%2F%2Fgithub.com%2Fenihsyou%2Fenihsyou-blog)

## How to Compose New Hexo Post

每篇 post 有三个属性，定义了文件叫什么：

- `title`: 作为属性出现在 front-matter 上，是文章的人类可读标题，允许任意字符
- `slug`: 作为文件名体现在路径上，受文件系统可用字符限制，是 title 的简化写法
- `id`: 是 front-matter 的属性，作为文章的标识符，出现在永久链接中，只允许 URL 安全字符
- `date`: 文件的创建实现，年和月的信息体现在路径上，精确到秒的时间体现在 date 属性上

Hexo 帮我们做了许多工作，比如新建文章时把 title 转换为 slug，所以 `hexo new` 不需要额外参数。

本博客文章的 title 部分经常出现非 ASCII 字符，虽然在文件名上使用没什么问题，但出现在 URL
中会被转义成难以阅读的形式，`id` 属性就是人为地定义一个固定链接地址段，作为文章的唯一标识。

所以新建一篇文章只需这样做:

```shell
pnpm exec hexo new --id my-new-post 我新建的文章
```

## 构建发布

```shell
pnpm exec hexo generate
```

可以忽略在 `.njk` 文件中发生的 `` Unable to call `next_url`, which is undefined or falsey `` 错误。

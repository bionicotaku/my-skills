# Img Downloader

这是一个用于网页图片批量下载的本地 skill。它面向“按页面顺序保存主内容图片”这个场景，适合 Telegraph 页面、漫画阅读页、图集页，以及图片来源混杂但最终都要落地到本地文件夹的页面。

这个 skill 不追求做通用解析器。它的工作方式是：针对当前页面临时写一个 Python 提取脚本，抽出有序图片 URL 列表，再复用仓库里的下载脚本完成真正的下载。

## 这个 skill 做什么

- 输入一个网页 URL
- 优先直接抓取 HTML 并提取主内容图片
- 保留页面顺序
- 将图片 URL 转成绝对地址
- 对完全相同的 URL 去重，但保留首次出现顺序
- 默认把页面 URL 作为图片下载请求的 `Referer`
- 把文件保存到 `~/Downloads/<folder-name>/`
- 下载后的文件按 `0`、`1`、`2`… 顺序命名
- 如果普通抓取拿不到可靠图片列表，再回退到 `agent-browser`

## 依赖

- `python3`
- 标准库即可完成临时 extractor
- 本 skill 自带脚本：`scripts/download_images.py`
- 浏览器兜底时依赖 `agent-browser`

## 基本流程

1. 创建一个临时工作目录
2. 在临时目录里写一个只针对当前页面的 Python extractor
3. 抓取网页并提取主内容图片 URL
4. 规范化为绝对 URL，并按首次出现顺序去重
5. 为输出目录决定一个简短、可读的名字
6. 把最终图片 URL 列表写到临时文件
7. 调用下载脚本，把图片保存到 `~/Downloads/<folder-name>`
8. 检查退出码，判断是全成功、部分成功还是失败
9. 如果普通抓取失败，再回退到 `agent-browser`
10. 结束前删除临时脚本、临时 URL 列表和临时目录

## 下载行为

- 默认下载主内容图片，不包含明显的 logo、头像、图标、广告、追踪像素或无关缩略图
- 如果用户明确要求“下载页面里所有图片”，再放宽过滤
- 图片文件名从 `0` 开始顺序编号
- 扩展名由下载脚本根据 URL 或响应头推断

## 下载脚本

这个 skill 的下载阶段统一调用：

```bash
python3 {baseDir}/scripts/download_images.py --input /tmp/image-urls.txt --output-dir ~/Downloads/<folder-name> --referer <page-url>
```

如果确实不需要 `Referer`，也可以不传：

```bash
python3 {baseDir}/scripts/download_images.py --input /tmp/image-urls.txt --output-dir ~/Downloads/<folder-name>
```

输入文件支持两种格式：

- JSON 数组
- 每行一个 URL 的纯文本

## 退出码约定

- `0`：全部下载成功
- `2`：部分成功，有图片下载失败，必须向用户报告失败数量或失败摘要
- 其他非零：失败

## 适合的场景

- 下载一篇文章里的全部插图
- 下载漫画 / 长图阅读页里的图片序列
- 下载图集页面的主图
- 下载需要保持页面顺序的混合来源图片

## 相关文件

- [SKILL.md](/Users/evan/Documents/my-skills/img-downloader/SKILL.md)
- [scripts/download_images.py](/Users/evan/Documents/my-skills/img-downloader/scripts/download_images.py)

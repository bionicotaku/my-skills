---
name: img-downloader
description: 将网页正文中的主要图片下载到一个专用本地目录。适用于某个文章页面、漫画阅读页等页面里的图片保存到本地的场景。输入是页面 URL；输出是一组图片文件。
---

# 图片下载器

用尽量少的依赖按页面顺序下载网页正文中的主要图片。提取器应保持按页面临时定制，而真正的下载阶段统一复用这个 skill 自带的下载脚本。

## 工作流

1. 创建一个临时工作目录，并在其中写入临时 Python 提取脚本。
2. 用这个临时脚本抓取目标页面。
3. 使用适配该页面的标准库解析逻辑，提取有序图片 URL 列表。
4. 默认优先选择页面正文图片。除非用户明确要求抓取页面中的全部图片，否则排除明显属于站点装饰层的内容，例如 logo、头像、图标、广告、追踪像素或无关缩略图。
5. 把图片 URL 规范化为绝对 URL，并在保留首次出现顺序的前提下去重。
6. 自行决定 Downloads 下的子目录名，通常取自页面标题或一个简短且清洗过的标签。
7. 把最终图片 URL 列表保存到临时文件。
8. 运行 `python3 {baseDir}/scripts/download_images.py`，传入该列表和输出目录，并默认把页面 URL 作为 `--referer`。
9. 显式检查下载脚本结果。把退出码 `0` 视为完全成功，退出码 `2` 视为部分成功且必须告知用户，其他非零退出码都视为失败。
10. 如果直接抓取或下载失败，原因可能是页面拦截访问、HTML 不完整、CDN 拒绝请求，或者图片 URL 需要浏览器上下文，此时使用 `agent-browser` skill 打开页面，提取同样有序的图片列表，再重新运行下载器。
11. 如果浏览器回退仍然失败，就停止并告诉用户原因。
12. 结束前手动删除临时提取脚本、临时图片列表文件和临时工作目录，除非用户要求为了调试保留它们。

## 规则

- 临时脚本中只使用 Python 标准库和系统工具。
- 不要在这个 skill 里内置通用提取器。执行时按页面现写提取器。
- 严格保留页面中的图片顺序，以页面实际渲染顺序或源码中可信顺序为准。
- 默认优先保留正文主图片。除非用户明确要求抓取页面中的全部图片，否则不要包含明显的导航、品牌装饰、头像、广告、分析追踪或其他装饰性资源。
- 把图片 URL 规范化为绝对 URL，并在保留首次出现顺序的前提下按精确匹配去重。
- 输出文件按顺序从 `0` 开始命名。
- 保存到 `~/Downloads` 下的专用子目录中，不要散落成单独文件。
- 调用内置下载器时使用 `python3 {baseDir}/scripts/download_images.py`，不要依赖当前工作目录的相对路径。
- 除非有明确理由，否则默认把源页面 URL 作为 `--referer` 传入。
- 重试次数保持有界。优先一次正常尝试，必要时一次浏览器回退，然后停止。
- 始终检查下载器退出码。退出码 `0` 表示完全成功，`2` 表示部分成功且有一个或多个文件下载失败，其他任意非零值都表示失败。
- 无论成功还是失败，结束前都要手动清理临时提取脚本、临时 URL 列表文件和临时工作目录，除非这些文件为了调试需要保留，或者用户明确要求保留。
- 如果使用了浏览器回退，结束前关闭浏览器状态。
- 报告具体阻塞原因，例如 `image CDN 返回 403`、`页面 HTML 中不包含图片 URL` 或 `浏览器快照无法暴露图片源地址`。

## 直接抓取路径

优先先走直接抓取路径，因为它更简单也更快。

临时提取器的典型模式如下：

```python
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser

url = TARGET_URL
html = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "ignore")

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(urljoin(url, src))

parser = Parser()
parser.feed(html)
Path(sys.argv[1]).write_text(json.dumps(parser.images, ensure_ascii=False, indent=2), encoding="utf-8")
```

根据实际站点调整解析器。有些页面会把图片 URL 放在 JSON 数据块、`srcset`、懒加载属性或脚本标签里。临时脚本要针对页面定制，不要试图把它做成通用方案。必要时增加页面专属过滤逻辑，让结果只包含正文主图片序列，而不是页面上的所有 `img` 标签。

## 浏览器回退

在以下情况下使用 `agent-browser`：

- 页面返回的 HTML 被拦截或不完整；
- 图片只会在客户端渲染后出现；
- CDN 请求需要浏览器会话状态；
- 或者直接提取无法恢复最终有序的图片 URL。

建议流程：

1. `agent-browser open <url>`
2. 等待网络空闲或正文内容加载完成
3. 检查快照、DOM 或元素属性，收集最终有序图片 URL
4. 规范化 URL，保留正文主图片，并在保持顺序的前提下按精确匹配去重
5. 把该有序列表写入临时文件
6. 运行 `python3 {baseDir}/scripts/download_images.py --input <temp-file> --output-dir ~/Downloads/<folder-name> --referer <page-url>`
7. 完成后执行 `agent-browser close --all`

如果回退方案仍然无法产出可信的有序列表，就直接停止，不要循环尝试。

## 输出目录命名

选择一个简短且易读的目录名。合理默认值包括：

- 页面标题；
- 文章 slug；
- 站点名加标题；
- 或者在没有可用名称时使用 `downloaded-images-YYYYMMDD-HHMMSS`。

只做本地文件系统所需的最小限度清洗。

## 内置脚本

下载阶段使用 `{baseDir}/scripts/download_images.py`。

优先通过 `python3 {baseDir}/scripts/download_images.py` 调用它，这样 skill 不会依赖当前工作目录。

### 输入

脚本接受以下两种输入之一：

- 图片 URL 的 JSON 数组；
- 或者每行一个 URL 的纯文本文件。

### 命令

```bash
python3 {baseDir}/scripts/download_images.py --input /tmp/image-urls.txt --output-dir ~/Downloads/<folder-name> --referer <page-url>
```

如果你有明确理由不把页面 URL 作为 referer 发送，也可以使用这个变体：

```bash
python3 {baseDir}/scripts/download_images.py --input /tmp/image-urls.txt --output-dir ~/Downloads/<folder-name>
```

### 退出码

- `0`：全部图片下载成功
- `2`：部分成功；有一张或多张图片下载失败，必须告诉用户失败数量
- 其他非零值：失败

## 成功标准

- 输出目录存在于 `~/Downloads` 下
- 文件按 `0`、`1`、`2`……命名，并带有推断出的扩展名
- 对于完全成功，下载得到的文件数量要与提取出的图片列表长度一致
- 对于部分成功，用户要拿到目标目录路径和明确的失败摘要
- 除非出于调试目的刻意保留，否则所有临时提取器、URL 列表和工作目录产物都已清理

---
name: img-downloader
description: Download the main content images from a web page into a dedicated local folder. Use when a user wants the images from a URL saved locally, especially for article pages, manga/comic readers, galleries, or other image-heavy pages. Input is a page URL; output is an ordered image set saved under `~/Downloads/<folder-name>` with sequential filenames.
---

# Img Downloader

Download a page's main content images in page order with minimal dependencies. Keep the extractor ad hoc and page-specific, but reuse the bundled downloader for the actual file downloads.

## Workflow

1. Create a temporary working directory and write a temporary Python extractor script inside it.
2. Fetch the target page with that temporary script.
3. Extract the ordered image URL list with standard-library parsing tailored to that page.
4. Prefer the page's main content images. Exclude obvious site chrome such as logos, avatars, icons, ads, trackers, or unrelated thumbnails unless the user explicitly asked for every page image.
5. Normalize image URLs to absolute URLs and deduplicate them while preserving first-seen order.
6. Decide a Downloads subfolder name yourself, usually from the page title or a short sanitized label.
7. Save the final image URL list to a temporary file.
8. Run `python3 {baseDir}/scripts/download_images.py` with that list and output folder, passing the page URL as `--referer` by default.
9. Check the downloader result explicitly. Treat exit code `0` as full success, exit code `2` as partial success that must be reported to the user, and any other non-zero exit as failure.
10. If direct fetching or downloading fails because the page blocks access, the HTML is incomplete, the CDN rejects requests, or the image URLs require browser context, use the `agent-browser` skill to open the page and extract the same ordered image list, then run the downloader again.
11. If browser fallback also fails, stop and tell the user why.
12. Before finishing, manually delete the temporary extractor script, the temporary image-list file, and the temporary working directory unless the user asked to keep them for debugging.

## Rules

- Use only Python standard library and system tools in temporary scripts.
- Do not bundle a universal extractor in this skill. Write the extractor per page at execution time.
- Preserve page order exactly as rendered or as found in the source for that page.
- Prefer main content images by default. Do not include obvious navigation, branding, avatar, advertisement, analytics, or other decorative page assets unless the user explicitly asks for every image on the page.
- Normalize image URLs to absolute URLs and deduplicate exact matches while preserving first occurrence order.
- Rename output files sequentially starting at `0`.
- Save into a dedicated subfolder under `~/Downloads`, not loose files.
- Invoke the bundled downloader as `python3 {baseDir}/scripts/download_images.py`, not via a cwd-dependent relative path.
- Pass the source page URL as the default `--referer` unless there is a specific reason not to.
- Keep retries bounded. Prefer one normal attempt, one browser fallback if needed, then stop.
- Always inspect the downloader exit code. Exit code `0` means full success, `2` means partial success with one or more failed downloads, and any other non-zero exit means failure.
- Manually clean up temporary extractor scripts, temporary URL-list files, and temporary working directories before finishing, whether the attempt succeeded or failed, unless they are needed for debugging or the user asked to keep them.
- If browser fallback was used, close browser state before finishing.
- Report concrete blockers, for example `403 from image CDN`, `page HTML contains no image URLs`, or `browser snapshot could not reveal image sources`.

## Direct fetch path

Prefer the direct path first because it is simpler and faster.

Typical pattern for the temporary extractor:

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

Adjust the parser for the actual site. For some pages, image URLs are in JSON blobs, `srcset`, lazy-load attributes, or script tags. Tailor the temporary script to the page instead of trying to make it generic. If needed, add page-specific filtering so the result contains the main content image sequence rather than every `img` tag on the page.

## Browser fallback

Use `agent-browser` when:

- the page returns blocked or incomplete HTML,
- images only appear after client-side rendering,
- CDN requests need browser session state,
- or direct extraction cannot recover the final ordered URLs.

Suggested flow:

1. `agent-browser open <url>`
2. wait for network idle or the main content
3. inspect snapshot / DOM / attributes to collect the final ordered image URLs
4. normalize URLs, keep the main content images, and deduplicate exact matches while preserving order
5. write that ordered list to a temp file
6. run `python3 {baseDir}/scripts/download_images.py --input <temp-file> --output-dir ~/Downloads/<folder-name> --referer <page-url>`
7. `agent-browser close --all` when done

If fallback still cannot produce a trustworthy ordered list, stop instead of looping.

## Output folder naming

Choose a short readable folder name. Good defaults:

- page title,
- article slug,
- site name plus title,
- or `downloaded-images-YYYYMMDD-HHMMSS` if nothing usable exists.

Sanitize only as much as needed for the local filesystem.

## Bundled script

Use `{baseDir}/scripts/download_images.py` for the download phase.

Prefer invoking it via `python3 {baseDir}/scripts/download_images.py` so the skill does not depend on the current working directory.

### Input

The script accepts either:

- a JSON array of image URLs, or
- a plain text file with one URL per line.

### Command

```bash
python3 {baseDir}/scripts/download_images.py --input /tmp/image-urls.txt --output-dir ~/Downloads/<folder-name> --referer <page-url>
```

If you have a specific reason not to send the page URL as a referer, this variant is also allowed:

```bash
python3 {baseDir}/scripts/download_images.py --input /tmp/image-urls.txt --output-dir ~/Downloads/<folder-name>
```

### Exit codes

- `0`: all images downloaded successfully
- `2`: partial success; one or more images failed and the user must be told how many failed
- other non-zero: failure

## Success criteria

- output folder exists under `~/Downloads`
- files are named `0`, `1`, `2`, ... with inferred extensions
- for full success, downloaded file count matches the extracted image list length
- for partial success, the user gets the destination folder plus a concrete failure summary
- all temporary extractor, URL-list, and working-directory artifacts are cleaned up unless intentionally kept for debugging

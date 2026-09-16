from pathlib import Path
from urllib.parse import urlparse, unquote
import hashlib
import mimetypes
import re
import urllib.request

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / 'content'
IMAGES = ROOT / 'images'
REMOTE = IMAGES / '_remote'
REMOTE.mkdir(parents=True, exist_ok=True)

IMG_SRC_RE = re.compile(r'(<img\b[^>]*\bsrc=["\'])([^"\']+)(["\'][^>]*>)', re.I)

def candidate_local(src: str, html_path: Path) -> Path:
    clean = unquote(src.split('#')[0].split('?')[0])
    return (html_path.parent / clean).resolve()

def local_from_images_subpath(src: str):
    if 'images/' in src:
        sub = src.split('images/', 1)[1].split('#')[0].split('?')[0]
        return '../images/' + sub
    return None

def extension_fallback(local: Path):
    exts = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']
    for ext in exts:
        alt = local.with_suffix(ext)
        if alt.exists():
            return alt
    return None

def rel_from_content(local: Path):
    return '../' + local.relative_to(ROOT).as_posix()

def remote_name(url: str, content_type: str = ''):
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if not suffix or len(suffix) > 8:
        suffix = mimetypes.guess_extension(content_type.split(';')[0].strip()) or '.img'
        if suffix == '.jpe':
            suffix = '.jpg'
    h = hashlib.sha1(url.encode('utf-8')).hexdigest()[:16]
    stem = re.sub(r'[^a-zA-Z0-9_-]+', '_', Path(parsed.path).stem or 'remote')[:50]
    return f'{stem}_{h}{suffix}'

def download_remote(url: str):
    # Map vitalik.ca/limo image URLs to bundled images first
    mapped = local_from_images_subpath(url)
    if mapped:
        local = (CONTENT / mapped).resolve()
        if local.exists():
            return mapped
        alt = extension_fallback(local)
        if alt:
            return rel_from_content(alt)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
            ctype = r.headers.get('content-type', '')
        name = remote_name(url, ctype)
        out = REMOTE / name
        out.write_bytes(data)
        return '../images/_remote/' + name
    except Exception as e:
        print('REMOTE_FAIL', url, type(e).__name__, e)
        return url

changed = 0
missing_after = []
remote_after = []
for html_path in CONTENT.glob('*.html'):
    s = html_path.read_text(encoding='utf-8', errors='replace')
    def repl(m):
        prefix, src, suffix = m.groups()
        new_src = src
        if src.startswith('data:'):
            return m.group(0)
        if src.startswith('//'):
            new_src = download_remote('https:' + src)
        elif src.startswith(('http://', 'https://')):
            new_src = download_remote(src)
        else:
            mapped = local_from_images_subpath(src)
            if mapped:
                new_src = mapped
            local = candidate_local(new_src, html_path)
            if not local.exists():
                alt = extension_fallback(local)
                if alt:
                    new_src = rel_from_content(alt)
        return prefix + new_src + suffix
    ns = IMG_SRC_RE.sub(repl, s)
    if ns != s:
        html_path.write_text(ns, encoding='utf-8')
        changed += 1

# final audit
for html_path in CONTENT.glob('*.html'):
    s = html_path.read_text(encoding='utf-8', errors='replace')
    for _, src, _ in IMG_SRC_RE.findall(s):
        if src.startswith(('http://', 'https://', '//')):
            remote_after.append((html_path.name, src))
        elif not src.startswith('data:'):
            local = candidate_local(src, html_path)
            if not local.exists():
                missing_after.append((html_path.name, src, str(local)))

print('pages_changed', changed)
print('missing_after', len(missing_after))
for row in missing_after[:50]:
    print('MISSING', row)
print('remote_after', len(remote_after))
for row in remote_after[:50]:
    print('REMOTE', row)
print('remote_downloaded', len(list(REMOTE.glob('*'))))

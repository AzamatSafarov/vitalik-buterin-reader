from pathlib import Path
import re, html, json
import markdown as mdlib

SRC = Path(__file__).resolve().parent / 'source_posts'
OUT = Path(__file__).resolve().parent
CONTENT = OUT / 'content'
DATA = OUT / 'data'
CONTENT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

THEME_RULES = [
    ('Voting and democracy', ['voting','vote','democracy','quadratic','election','maci','plutocracy']),
    ('Governance and institutions', ['governance','institution','institutions','coordination','legitimacy','collusion','power','alignment','daos','dao','bullveto']),
    ('Validation and trust models', ['validation','trust','validator','validators','51%','fault','casper','pos','proof of stake','decentralization']),
    ('Network states and crypto cities', ['network state','networkstates','cities','societies','plurality','crypto cities']),
    ('Privacy, identity, ZK', ['privacy','identity','biometric','zk','snark','stark','proof of personhood','soulbound','stealth']),
    ('Ethereum protocol', ['ethereum','layer','sharding','verkle','rollup','l2','blob','eip','gas','casper']),
    ('Economics and public goods', ['public goods','funding','markets','quadratic funding','gitcoin','revenue','economics','token']),
    ('Philosophy and politics', ['philosophy','political','culture','free speech','balance of power','copyleft']),
]

core_files = {
    'voting2.md', 'voting3.md', 'plutocracy.md', 'voting.md', 'philosophy.md',
    'trust.md', 'legitimacy.md', 'limits.md', 'networkstates.md', 'daos.md',
    'cities.md', 'plurality.md', 'openness_and_verifiability.md', 'societies.md',
    'balance_of_power.md', 'biometric.md', 'collusion.md', 'coordination.md',
    'institutions.md', 'coordination_problems.md', '99_fault_tolerant.md',
    'cbc_casper.md', 'pos_design.md'
}

def parse_post(path: Path):
    raw = path.read_text(encoding='utf-8', errors='replace')
    meta = {}
    body_lines = []
    for line in raw.splitlines():
        m = re.match(r'^\[([^\]]+)\]:\s*<>\s*\((.*)\)\s*$', line)
        if m:
            meta[m.group(1).strip().lower()] = m.group(2).strip()
        else:
            body_lines.append(line)
    title = meta.get('title') or re.sub(r'[_-]+',' ',path.stem).strip().title()
    date = meta.get('date','').replace('/','-')
    cats = [c.strip() for c in meta.get('category','').split(',') if c.strip()]
    body = '\n'.join(body_lines).strip()
    return raw, body, title, date, cats

posts = []
for p in sorted(SRC.glob('*.md')):
    raw, body, title, date, cats = parse_post(p)
    lower = (title + ' ' + p.stem + ' ' + body[:5000]).lower()
    themes = [theme for theme, keys in THEME_RULES if any(k.lower() in lower for k in keys)]
    if not themes:
        themes = ['Other']
    if date:
        yyyy, mm, dd = date.split('-')
        canonical = f'https://vitalik.eth.limo/general/{yyyy}/{mm}/{dd}/{p.stem}.html'
    else:
        canonical = f'https://github.com/vbuterin/blog/blob/main/posts/{p.name}'
    text_plain = re.sub(r'<[^>]+>', ' ', body)
    text_plain = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text_plain)
    text_plain = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text_plain)
    text_plain = html.unescape(re.sub(r'\s+', ' ', text_plain)).strip()
    posts.append({
        'file': p.name,
        'slug': p.stem,
        'title': title,
        'date': date or 'undated',
        'categories': cats,
        'themes': themes,
        'canonical': canonical,
        'excerpt': text_plain[:560],
        'word_count': len(text_plain.split()),
        'featured': p.name in core_files,
    })

slug_to_page = {post['slug']: f"content/{post['slug']}.html" for post in posts}

def preprocess_markdown(body: str):
    body = re.sub(r'(!\[[^\]]*\]\()(?:(?:\.\./)+)(images/[^)]+)(\))', r'\1https://vitalik.eth.limo/\2\3', body)
    body = re.sub(r'(<img[^>]+src=["\'])(?:(?:\.\./)+)(images/[^"\']+)(["\'])', r'\1https://vitalik.eth.limo/\2\3', body)
    def repl_link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith('../../../') or href.startswith('../../../../'):
            parts = [x for x in href.split('/') if x not in ['..','.']]
            joined = '/'.join(parts)
            if re.match(r'\d{4}/\d{2}/\d{2}/[^/]+\.html', joined):
                slug = joined.rsplit('/',1)[-1].replace('.html','')
                if slug in slug_to_page:
                    return f'[{label}]({slug}.html)'
                return f'[{label}](https://vitalik.eth.limo/general/{joined})'
            if joined.startswith('images/'):
                return f'[{label}](https://vitalik.eth.limo/{joined})'
        return m.group(0)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', repl_link, body)

CSS = """
:root{--bg:#f6f3ea;--paper:#fffdfa;--card:#ffffff;--text:#151515;--muted:#66635c;--line:#ded8c8;--soft:#8d877a;--accent:#c96442;--blue:#386b8f;--green:#68745c;--yellow:#d6a63d;--shadow:rgba(20,20,19,.08)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.56}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}.wrap{max-width:1180px;margin:0 auto;padding:28px 24px 50px}.hero{background:linear-gradient(135deg,#fffdf8,#f8efe8);border:1px solid var(--line);border-radius:28px;padding:28px;box-shadow:0 18px 55px var(--shadow)}h1{font-family:Georgia,'Times New Roman',serif;font-size:42px;line-height:1.08;font-weight:500;margin:0 0 10px}h2{font-family:Georgia,'Times New Roman',serif;font-size:28px;font-weight:500;margin:34px 0 14px}h3{margin:0 0 8px}.lead{font-size:17px;color:var(--muted);max-width:920px}.stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.pill{border:1px solid var(--line);background:#fff;border-radius:999px;padding:7px 11px;color:var(--muted);font-size:13px}.grid{display:grid;grid-template-columns:310px 1fr;gap:18px;margin-top:22px}.panel{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:16px;box-shadow:0 12px 34px var(--shadow);position:sticky;top:18px;align-self:start}.content{min-width:0}.search{width:100%;padding:12px 14px;border:1px solid var(--line);border-radius:14px;background:#fff;font-size:14px}.filter{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.btn{border:1px solid var(--line);background:#fff;border-radius:999px;padding:7px 10px;font-size:12px;cursor:pointer;color:var(--muted)}.btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px;margin:0 0 12px;box-shadow:0 8px 28px var(--shadow)}.card.featured{border-left:5px solid var(--accent)}.meta{font-size:12px;color:var(--soft);display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}.tag{display:inline-block;background:#f0eadc;border:1px solid #e1dac8;border-radius:999px;padding:3px 7px;font-size:11px;color:#4a463f}.tag.theme{background:#eef4ee;color:#3f583a}.excerpt{font-size:13.5px;color:var(--muted)}.article{max-width:900px;margin:0 auto;background:var(--paper);border:1px solid var(--line);border-radius:26px;padding:30px;box-shadow:0 14px 40px var(--shadow)}.article h1{font-size:40px}.article h2{font-size:26px;border-top:1px solid var(--line);padding-top:22px}.article img{max-width:100%;height:auto}.article blockquote{border-left:4px solid var(--accent);padding:8px 16px;margin:16px 0;background:#fff8f4;color:#3f3b35}.article code{background:#eee8da;padding:2px 5px;border-radius:6px}.article pre{overflow:auto;background:#1e1e1e;color:#f2f2f2;padding:14px;border-radius:14px}.back{display:inline-block;margin-bottom:18px}.note{background:#fff8f4;border:1px solid #ead4c8;border-left:5px solid var(--accent);border-radius:16px;padding:12px 14px;color:var(--muted)}
@media(max-width:900px){.grid{grid-template-columns:1fr}.panel{position:static}.wrap{padding:16px}.article{padding:18px}h1{font-size:34px}}
"""

# pages
for post in posts:
    raw, body, title, date, cats = parse_post(SRC / post['file'])
    body = preprocess_markdown(body)
    html_body = mdlib.markdown(body, extensions=['extra','tables','fenced_code'])
    tags = ''.join(f'<span class="tag theme">{html.escape(t)}</span>' for t in post['themes']) + ''.join(f'<span class="tag">{html.escape(c)}</span>' for c in cats)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)} — Vitalik Reader</title><style>{CSS}</style></head><body><div class="wrap"><a class="back" href="../index.html">← Index</a><article class="article"><h1>{html.escape(title)}</h1><div class="meta"><span>{html.escape(date or 'undated')}</span><span>{post['word_count']} words</span><a href="{html.escape(post['canonical'])}">original</a><a href="https://github.com/vbuterin/blog/blob/main/posts/{html.escape(post['file'])}">GitHub source</a></div><div>{tags}</div><div class="note">Local reading copy generated from Vitalik Buterin's official GitHub blog repository. Use the original/GitHub links for citation verification.</div>{html_body}</article></div></body></html>'''
    (CONTENT / f"{post['slug']}.html").write_text(page, encoding='utf-8')

posts.sort(key=lambda x: (not x['featured'], x['date'], x['title']))
posts_json = json.dumps(posts, ensure_ascii=False)
all_themes = sorted({t for p in posts for t in p['themes']})
featured = [p for p in posts if p['featured']]
featured_cards = ''.join(f'<div class="card featured"><h3><a href="content/{html.escape(p["slug"])}.html">{html.escape(p["title"])}</a></h3><div class="meta"><span>{html.escape(p["date"])}</span><span>{p["word_count"]} words</span></div><p class="excerpt">{html.escape(p["excerpt"])}</p></div>' for p in sorted(featured, key=lambda x:x['title']))
index = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Vitalik Buterin Reader — Governance, Statehood, Voting</title><style>{CSS}</style></head><body><div class="wrap"><section class="hero"><h1>Vitalik Buterin Reader</h1><p class="lead">Локальная читательская версия корпуса работ Виталика Бутерина: governance, blockchain voting, validation, legitimacy, network states, DAOs, privacy и cryptography. Собрано из официального GitHub-репозитория <code>vbuterin/blog</code>; оригинальные ссылки сохранены для цитирования.</p><div class="stats"><span class="pill">📚 {len(posts)} posts</span><span class="pill">⭐ {len(featured)} key texts</span><span class="pill">🔎 search/filter</span><span class="pill">🧭 для книги и статьи про voting</span></div></section><div class="grid"><aside class="panel"><h3>Поиск</h3><input id="q" class="search" placeholder="governance, voting, legitimacy…"><h3 style="margin-top:16px">Темы</h3><div id="themes" class="filter"></div><h3 style="margin-top:16px">Быстрые кластеры</h3><p class="excerpt"><b>Для voting article:</b> voting2, voting3, plutocracy, trust, philosophy.</p><p class="excerpt"><b>Для книги:</b> networkstates, cities, institutions, legitimacy, plurality, societies.</p><button class="btn" onclick="showFeatured()">Показать key texts</button><button class="btn" onclick="resetFilters()">Сбросить</button></aside><main class="content"><h2>Ключевые тексты</h2>{featured_cards}<h2>Все работы</h2><div id="count" class="meta"></div><div id="list"></div></main></div></div><script>const posts={posts_json}; const themes={json.dumps(all_themes, ensure_ascii=False)}; let activeTheme=''; let featuredOnly=false; const q=document.getElementById('q'), list=document.getElementById('list'), count=document.getElementById('count'), themeBox=document.getElementById('themes'); function esc(s){{return String(s||'').replace(/[&<>"']/g,m=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[m]))}} function makePill(t){{const b=document.createElement('button'); b.className='btn'; b.textContent=t; b.onclick=()=>{{activeTheme=activeTheme===t?'':t; featuredOnly=false; render();}}; return b;}} themes.forEach(t=>themeBox.appendChild(makePill(t))); function card(p){{return `<div class="card ${{p.featured?'featured':''}}"><h3><a href="content/${{p.slug}}.html">${{esc(p.title)}}</a></h3><div class="meta"><span>${{esc(p.date)}}</span><span>${{p.word_count}} words</span><a href="${{p.canonical}}">original</a><a href="https://github.com/vbuterin/blog/blob/main/posts/${{p.file}}">GitHub</a></div><div>${{p.themes.map(t=>`<span class="tag theme">${{esc(t)}}</span>`).join(' ')}} ${{p.categories.map(t=>`<span class="tag">${{esc(t)}}</span>`).join(' ')}}</div><p class="excerpt">${{esc(p.excerpt)}}</p></div>`}} function render(){{document.querySelectorAll('#themes .btn').forEach(b=>b.classList.toggle('active', b.textContent===activeTheme)); const term=q.value.toLowerCase(); let arr=posts.filter(p=>(!activeTheme||p.themes.includes(activeTheme))&&(!featuredOnly||p.featured)&&(!term||(p.title+' '+p.excerpt+' '+p.themes.join(' ')+' '+p.categories.join(' ')).toLowerCase().includes(term))); arr.sort((a,b)=>(b.featured-a.featured)||String(b.date).localeCompare(String(a.date))||a.title.localeCompare(b.title)); count.textContent=`${{arr.length}} / ${{posts.length}}`; list.innerHTML=arr.map(card).join('');}} function showFeatured(){{featuredOnly=true; activeTheme=''; render();}} function resetFilters(){{featuredOnly=false; activeTheme=''; q.value=''; render();}} q.addEventListener('input',()=>{{featuredOnly=false;render();}}); render();</script></body></html>'''
(OUT / 'index.html').write_text(index, encoding='utf-8')
(DATA / 'posts.json').write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'README.md').write_text(f'''# Vitalik Buterin Reader

Local static reader generated from the official `vbuterin/blog` GitHub repository.

- Posts downloaded: {len(posts)}
- Generated: 2026-09-15_223757 RTZ
- Entry point: `index.html`
- Generated article pages: `content/`
- Working source corpus: `{SRC}`

## Citation discipline

Use the original URL or GitHub source link on each page for citation verification. This reader is a local navigation and reading aid, not a canonical publication source.
''', encoding='utf-8')
print(OUT)
print('posts', len(posts), 'pages', len(list(CONTENT.glob('*.html'))))

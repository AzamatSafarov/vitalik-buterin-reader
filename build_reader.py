from pathlib import Path
import re
import html
import json
import shutil
import markdown as mdlib

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'source_posts'
OFFICIAL_REPO = Path('C:/Users/akuta/vbuterin-blog-source')
OFFICIAL_IMAGES = OFFICIAL_REPO / 'images'
OUT = ROOT
CONTENT = OUT / 'content'
DATA = OUT / 'data'
IMAGES = OUT / 'images'
CONTENT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

THEME_RULES = [
    ('Voting and democracy', ['voting', 'vote', 'democracy', 'quadratic', 'election', 'maci', 'plutocracy']),
    ('Governance and institutions', ['governance', 'institution', 'institutions', 'coordination', 'legitimacy', 'collusion', 'power', 'alignment', 'daos', 'dao', 'bullveto']),
    ('Validation and trust models', ['validation', 'trust', 'validator', 'validators', '51%', 'fault', 'casper', 'pos', 'proof of stake', 'decentralization']),
    ('Network states and crypto cities', ['network state', 'networkstates', 'cities', 'societies', 'plurality', 'crypto cities']),
    ('Privacy, identity, ZK', ['privacy', 'identity', 'biometric', 'zk', 'snark', 'stark', 'proof of personhood', 'soulbound', 'stealth']),
    ('Ethereum protocol', ['ethereum', 'layer', 'sharding', 'verkle', 'rollup', 'l2', 'blob', 'eip', 'gas', 'casper']),
    ('Economics and public goods', ['public goods', 'funding', 'markets', 'quadratic funding', 'gitcoin', 'revenue', 'economics', 'token']),
    ('Philosophy and politics', ['philosophy', 'political', 'culture', 'free speech', 'balance of power', 'copyleft']),
]

CORE = {
    'voting2.md': 'Voting: blockchain as bulletin board; privacy and coercion limits',
    'voting3.md': 'Coin voting, plutocracy, vote-buying, non-coin governance',
    'plutocracy.md': 'DPoS, cartels, concentrated validators and plutocracy',
    'voting.md': 'Blockchain governance as coordination rather than pure algorithm',
    'philosophy.md': 'Independent validation, full nodes, default-to-chaos/failure',
    'trust.md': 'Trust models: 1-of-1, N/2-of-N, 1-of-N',
    'legitimacy.md': 'Legitimacy as higher-order acceptance and social coordination',
    'limits.md': 'Limits of cryptoeconomics and Schneider critique',
    'networkstates.md': 'Network states and crypto political forms',
    'daos.md': 'DAOs are not corporations; why decentralization matters',
    'cities.md': 'Crypto cities and municipal blockchain governance',
    'plurality.md': 'Plurality philosophy and governance beyond one center',
    'openness_and_verifiability.md': 'Full-stack openness and verifiability',
    'societies.md': 'Plural societies / post-national experiments',
    'balance_of_power.md': 'Balance of power and anti-centralization logic',
    'biometric.md': 'Proof of personhood, identity, privacy and capture risks',
    'collusion.md': 'Collusion, coordination and anti-collusion mechanisms',
    'coordination.md': 'Coordination as good and bad political technology',
    'institutions.md': 'What counts as an institution',
    'coordination_problems.md': 'Engineering security through coordination problems',
    '99_fault_tolerant.md': 'High fault tolerance and validator assumptions',
    'cbc_casper.md': 'Casper finality and validator faults',
    'pos_design.md': 'Proof-of-stake design philosophy',
}

FOCUS = {
    'Для статьи о голосовании': ['voting2.md', 'voting3.md', 'plutocracy.md', 'trust.md', 'philosophy.md', 'legitimacy.md'],
    'Для главы о post-Westphalian governance': ['networkstates.md', 'cities.md', 'institutions.md', 'plurality.md', 'societies.md', 'daos.md'],
    'Для validator independence': ['philosophy.md', 'trust.md', '99_fault_tolerant.md', 'cbc_casper.md', 'pos_design.md', 'plutocracy.md'],
    'Для legitimacy / social layer': ['legitimacy.md', 'voting.md', 'coordination.md', 'coordination_problems.md', 'limits.md'],
}

CSS = '''
:root{--bg-sidebar:#F0EDE9;--bg-main:#F9F8F6;--bg-hover:#E8E4DF;--bg-card:#FFFFFF;--text-primary:#1A1A1A;--text-secondary:#333333;--text-muted:#777777;--text-faint:#AAAAAA;--border:#E0DCD7;--border-light:#EDEAE5;--accent:#8B6F47;--accent-dim:#B8946A;--radius:8px;--sidebar-width:340px;--font-serif:Georgia,"Times New Roman",serif;--font-sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;--font-mono:"SF Mono",Monaco,"Cascadia Code",monospace;--cat-yellow:#D4A017;--cat-red:#E57373;--cat-purple:#9575CD;--cat-blue:#4DB6AC;--cat-green:#81C784}*{margin:0;padding:0;box-sizing:border-box}body{font-family:var(--font-sans);background:var(--bg-main);color:var(--text-primary);line-height:1.6;overflow:hidden;height:100vh}.app{display:flex;height:100vh;width:100vw}.sidebar{width:var(--sidebar-width);min-width:var(--sidebar-width);background:var(--bg-sidebar);border-right:1px solid var(--border);overflow-y:auto;height:100vh;flex-shrink:0;display:flex;flex-direction:column}.sidebar::-webkit-scrollbar{width:5px}.sidebar::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}.sidebar-header{padding:20px 18px 16px;flex-shrink:0}.logo{display:flex;align-items:center;gap:10px;text-decoration:none;margin-bottom:3px}.logo-icon{width:32px;height:32px;background:var(--accent);border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:16px;font-family:var(--font-serif);font-weight:bold;color:#fff;flex-shrink:0}.logo-title{font-family:var(--font-serif);font-size:17px;font-weight:700;color:var(--text-primary)}.logo-subtitle{font-size:12px;color:var(--text-muted);margin-top:2px;margin-left:42px}.search-box{position:relative;margin:14px 0 10px}.search-box input{width:100%;padding:10px 12px 10px 36px;background:#fff;border:1px solid var(--border);border-radius:var(--radius);color:var(--text-primary);font-size:13px}.search-icon{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--text-faint);font-size:14px}.stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0}.stat{background:#fff;border:1px solid var(--border-light);border-radius:10px;padding:8px}.stat-num{font-size:18px;font-weight:800;color:var(--accent)}.stat-label{font-size:11px;color:var(--text-muted)}.filters{padding:0 18px 16px;border-bottom:1px solid var(--border)}.filter-title{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--text-faint);margin:12px 0 7px}.chip{display:inline-flex;margin:3px 3px 3px 0;border:1px solid var(--border);background:#fff;border-radius:999px;padding:5px 8px;font-size:11px;color:var(--text-muted);cursor:pointer}.chip.active{background:var(--accent);color:#fff;border-color:var(--accent)}.nav-list{padding:12px 10px 24px;overflow-y:auto}.nav-item{display:block;padding:10px 9px;border-radius:10px;text-decoration:none;color:var(--text-secondary);cursor:pointer;border:1px solid transparent;margin-bottom:4px}.nav-item:hover,.nav-item.active{background:var(--bg-hover);border-color:var(--border)}.nav-title{font-size:13px;font-weight:650;line-height:1.28}.nav-meta{font-size:11px;color:var(--text-muted);margin-top:4px}.star{color:var(--cat-yellow);margin-right:4px}.main{flex:1;height:100vh;overflow-y:auto;padding:34px 44px}.main::-webkit-scrollbar{width:8px}.main::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}.hero{max-width:1040px;margin:0 auto 24px;background:var(--bg-card);border:1px solid var(--border);border-radius:18px;padding:28px;box-shadow:0 4px 18px rgba(0,0,0,.04)}h1{font-family:var(--font-serif);font-size:42px;line-height:1.12;font-weight:500;margin-bottom:10px}h2{font-family:var(--font-serif);font-size:28px;font-weight:500;margin:30px 0 12px}h3{font-size:16px;margin:16px 0 8px}.lead{font-size:16px;color:var(--text-muted);max-width:880px}.quick-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;max-width:1040px;margin:0 auto 24px}.quick-card{background:#fff;border:1px solid var(--border);border-radius:14px;padding:14px}.quick-card h3{margin:0 0 6px;font-size:14px}.quick-card a{display:block;font-size:13px;margin:4px 0;color:var(--blue)}.reader{max-width:900px;margin:0 auto;background:var(--bg-card);border:1px solid var(--border);border-radius:18px;padding:34px 42px;box-shadow:0 4px 18px rgba(0,0,0,.04)}.reader h1{font-size:40px}.reader h2{border-top:1px solid var(--border-light);padding-top:22px}.reader p,.reader li{font-size:16px;color:var(--text-secondary)}.reader blockquote{border-left:4px solid var(--accent);padding:10px 18px;margin:18px 0;background:#FBF8F2;color:var(--text-secondary)}.reader img{max-width:100%;height:auto;border-radius:10px}.reader pre{overflow:auto;background:#222;color:#f8f8f2;padding:14px;border-radius:12px}.reader code{font-family:var(--font-mono);background:#EEE8DA;border-radius:5px;padding:2px 5px}.meta-row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 16px}.pill{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--border);background:#fff;border-radius:999px;padding:5px 9px;font-size:12px;color:var(--text-muted)}.tag{display:inline-block;background:#F3EEE4;border-radius:999px;padding:3px 8px;font-size:11px;color:#5e5547;margin:2px}.tag.theme{background:#EEF4EE;color:#4E6646}.notice{border-left:4px solid var(--accent);background:#FFF8F4;border-radius:10px;padding:12px 14px;color:var(--text-muted);font-size:13px;margin:14px 0 20px}.cards{max-width:1040px;margin:0 auto}.card{background:#fff;border:1px solid var(--border);border-radius:14px;padding:14px;margin-bottom:10px;cursor:pointer}.card:hover{background:#FFFCF5}.card.featured{border-left:5px solid var(--accent)}.excerpt{font-size:13px;color:var(--text-muted);margin-top:6px}.topbar{display:flex;gap:8px;align-items:center;margin-bottom:16px}.btn{border:1px solid var(--border);background:#fff;border-radius:999px;padding:7px 10px;color:var(--text-muted);cursor:pointer}.btn:hover{background:var(--bg-hover)}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}@media(max-width:820px){body{overflow:auto;height:auto}.app{display:block;height:auto}.sidebar{width:100%;min-width:0;height:auto;max-height:55vh}.main{height:auto;padding:20px}.reader{padding:22px}h1{font-size:32px}}
'''

JS = '''
let POSTS=[]; let activeTheme=''; let featuredOnly=false; let activeSlug='';
const $=id=>document.getElementById(id);
function esc(s){return String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));}
function filtered(){const term=($('search').value||'').toLowerCase(); return POSTS.filter(p=>(!activeTheme||p.themes.includes(activeTheme))&&(!featuredOnly||p.featured)&&(!term||(p.title+' '+p.excerpt+' '+p.themes.join(' ')+' '+p.categories.join(' ')).toLowerCase().includes(term))).sort((a,b)=>(b.featured-a.featured)||String(b.date).localeCompare(String(a.date))||a.title.localeCompare(b.title));}
function renderList(){const arr=filtered(); $('count').textContent=`${arr.length} / ${POSTS.length}`; $('navList').innerHTML=arr.map(p=>`<div class="nav-item ${p.slug===activeSlug?'active':''}" data-slug="${esc(p.slug)}"><div class="nav-title">${p.featured?'<span class="star">★</span>':''}${esc(p.title)}</div><div class="nav-meta">${esc(p.date)} · ${p.word_count} words</div></div>`).join(''); document.querySelectorAll('.nav-item').forEach(el=>el.addEventListener('click',()=>openPost(el.dataset.slug))); document.querySelectorAll('.chip').forEach(c=>c.classList.toggle('active', c.dataset.theme===activeTheme));}
function renderCards(){const arr=filtered(); $('homeCards').innerHTML=arr.slice(0,60).map(p=>`<div class="card ${p.featured?'featured':''}" data-slug="${esc(p.slug)}"><h3>${p.featured?'★ ':''}${esc(p.title)}</h3><div class="meta-row"><span class="pill">${esc(p.date)}</span><span class="pill">${p.word_count} words</span>${p.themes.map(t=>`<span class="tag theme">${esc(t)}</span>`).join('')}</div><div class="excerpt">${esc(p.excerpt)}</div></div>`).join(''); document.querySelectorAll('.card[data-slug]').forEach(el=>el.addEventListener('click',()=>openPost(el.dataset.slug)));}
function renderThemes(){const themes=[...new Set(POSTS.flatMap(p=>p.themes))].sort(); $('themes').innerHTML=themes.map(t=>`<button class="chip" data-theme="${esc(t)}">${esc(t)}</button>`).join(''); document.querySelectorAll('.chip').forEach(b=>b.addEventListener('click',()=>{activeTheme=activeTheme===b.dataset.theme?'':b.dataset.theme; featuredOnly=false; renderList(); renderCards();}));}
async function openPost(slug){const p=POSTS.find(x=>x.slug===slug); if(!p)return; activeSlug=slug; renderList(); const res=await fetch(`content/${slug}.html`); const text=await res.text(); const doc=new DOMParser().parseFromString(text,'text/html'); const article=doc.querySelector('.reader')||doc.querySelector('article')||doc.body; $('main').innerHTML=article.outerHTML; history.replaceState(null,'',`#${slug}`); $('main').scrollTop=0;}
function showHome(){activeSlug=''; history.replaceState(null,'',location.pathname); renderList(); $('main').innerHTML=document.getElementById('homeTemplate').innerHTML; renderCards();}
function showFeatured(){featuredOnly=true; activeTheme=''; renderList(); renderCards();}
function resetFilters(){featuredOnly=false; activeTheme=''; $('search').value=''; renderList(); renderCards();}
async function init(){const res=await fetch('data/posts.json'); POSTS=await res.json(); $('totalPosts').textContent=POSTS.length; $('featuredCount').textContent=POSTS.filter(p=>p.featured).length; renderThemes(); $('search').addEventListener('input',()=>{featuredOnly=false;renderList();renderCards();}); $('homeBtn').addEventListener('click',showHome); $('featuredBtn').addEventListener('click',showFeatured); $('resetBtn').addEventListener('click',resetFilters); showHome(); if(location.hash.length>1){openPost(location.hash.slice(1));}}
init().catch(err=>{console.error(err); $('main').innerHTML='<div class="reader"><h1>Loading error</h1><p>'+esc(err.message)+'</p></div>';});
'''

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
    return raw, '\n'.join(body_lines).strip(), title, date, cats

def collect_posts():
    posts=[]
    for p in sorted(SRC.glob('*.md')):
        raw, body, title, date, cats = parse_post(p)
        lower=(title+' '+p.stem+' '+body[:5000]).lower()
        themes=[theme for theme,keys in THEME_RULES if any(k.lower() in lower for k in keys)] or ['Other']
        if date:
            y,m,d=date.split('-'); canonical=f'https://vitalik.eth.limo/general/{y}/{m}/{d}/{p.stem}.html'
        else:
            canonical=f'https://github.com/vbuterin/blog/blob/main/posts/{p.name}'
        text_plain=re.sub(r'<[^>]+>',' ',body)
        text_plain=re.sub(r'!\[[^\]]*\]\([^)]*\)',' ',text_plain)
        text_plain=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',text_plain)
        text_plain=html.unescape(re.sub(r'\s+',' ',text_plain)).strip()
        posts.append({'file':p.name,'slug':p.stem,'title':title,'date':date or 'undated','categories':cats,'themes':themes,'canonical':canonical,'excerpt':text_plain[:560],'word_count':len(text_plain.split()),'featured':p.name in CORE,'note':CORE.get(p.name,'')})
    return posts

def preprocess(body: str):
    body=re.sub(r'(!\[[^\]]*\]\()(?:(?:\.\./)+)(images/[^)]+)(\))', r'\1../\2\3', body)
    body=re.sub(r'(<img[^>]+src=["\'])(?:(?:\.\./)+)(images/[^"\']+)(["\'])', r'\1../\2\3', body)
    def repl(m):
        label,href=m.group(1),m.group(2)
        if href.startswith('../../../') or href.startswith('../../../../'):
            parts=[x for x in href.split('/') if x not in ['..','.']]
            joined='/'.join(parts)
            if re.match(r'\d{4}/\d{2}/\d{2}/[^/]+\.html', joined):
                slug=joined.rsplit('/',1)[-1].replace('.html','')
                return f'[{label}](../index.html#{slug})'
            if joined.startswith('images/'):
                return f'[{label}](../{joined})'
        return m.group(0)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', repl, body)

posts=collect_posts()
# Copy images locally
if OFFICIAL_IMAGES.exists():
    if IMAGES.exists():
        shutil.rmtree(IMAGES)
    shutil.copytree(OFFICIAL_IMAGES, IMAGES)

for post in posts:
    raw, body, title, date, cats = parse_post(SRC/post['file'])
    body=preprocess(body)
    html_body=mdlib.markdown(body, extensions=['extra','tables','fenced_code'])
    tags=''.join(f'<span class="tag theme">{html.escape(t)}</span>' for t in post['themes']) + ''.join(f'<span class="tag">{html.escape(c)}</span>' for c in cats)
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)} — Vitalik Reader</title><link rel="stylesheet" href="../styles.css"></head><body><div class="main" style="height:auto;overflow:visible"><article class="reader"><h1>{html.escape(title)}</h1><div class="meta-row"><span class="pill">{html.escape(post['date'])}</span><span class="pill">{post['word_count']} words</span><a class="pill" href="{html.escape(post['canonical'])}">original</a><a class="pill" href="https://github.com/vbuterin/blog/blob/main/posts/{html.escape(post['file'])}">GitHub source</a></div><div>{tags}</div><div class="notice">Reading copy generated from the official GitHub repository. Use original/GitHub links for citation verification.</div>{html_body}</article></div></body></html>'''
    (CONTENT/f'{post["slug"]}.html').write_text(page, encoding='utf-8')

# Sort newest first for data; featured display handled by JS
posts_sorted=sorted(posts, key=lambda p: (p['date'] if p['date']!='undated' else '0000-00-00'), reverse=True)
(DATA/'posts.json').write_text(json.dumps(posts_sorted, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT/'styles.css').write_text(CSS, encoding='utf-8')
(OUT/'app.js').write_text(JS, encoding='utf-8')
quick_html=''.join(f'<div class="quick-card"><h3>{html.escape(cluster)}</h3>' + ''.join(f'<a href="#" data-open="{html.escape(fname[:-3])}">{html.escape(next((p["title"] for p in posts if p["file"]==fname), fname))}</a>' for fname in files if any(p['file']==fname for p in posts)) + '</div>' for cluster,files in FOCUS.items())
index=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Vitalik Buterin Reader — Governance, Statehood, Voting</title><link rel="stylesheet" href="styles.css"></head><body><div class="app"><aside class="sidebar"><div class="sidebar-header"><a class="logo" id="homeBtn" href="#"><span class="logo-icon">V</span><span class="logo-title">Vitalik Reader</span></a><div class="logo-subtitle">governance · voting · statehood</div><div class="search-box"><span class="search-icon">⌕</span><input id="search" placeholder="поиск по работам"></div><div class="stats"><div class="stat"><div class="stat-num" id="totalPosts">0</div><div class="stat-label">работ</div></div><div class="stat"><div class="stat-num" id="featuredCount">0</div><div class="stat-label">ключевых</div></div></div></div><div class="filters"><div class="filter-title">Темы</div><div id="themes"></div><div class="filter-title">Действия</div><button class="chip" id="featuredBtn">★ key texts</button><button class="chip" id="resetBtn">сбросить</button><div class="filter-title">Счётчик</div><div class="nav-meta" id="count"></div></div><nav class="nav-list" id="navList"></nav></aside><main class="main" id="main"></main></div><template id="homeTemplate"><section class="hero"><h1>Vitalik Buterin Reader</h1><p class="lead">Удобная локальная/публичная версия корпуса Виталика Бутерина для работы над статьями о blockchain voting, validator independence, trust models, legitimacy, network states и post-Westphalian governance. Корпус собран из официального GitHub-репозитория <code>vbuterin/blog</code>; каждая страница сохраняет ссылку на original и GitHub source.</p><div class="meta-row"><span class="pill">📚 175 posts</span><span class="pill">🖼️ локальные изображения</span><span class="pill">🔎 поиск и фильтры</span><span class="pill">🧭 фокус для книги</span></div></section><section class="quick-grid">{quick_html}</section><section class="cards"><h2>Все работы</h2><div id="homeCards"></div></section></template><script src="app.js"></script><script>document.addEventListener('click',e=>{{const a=e.target.closest('[data-open]'); if(a){{e.preventDefault(); openPost(a.dataset.open);}}}})</script></body></html>'''
(OUT/'index.html').write_text(index, encoding='utf-8')
print('built', OUT)
print('posts', len(posts), 'pages', len(list(CONTENT.glob('*.html'))), 'images', len(list(IMAGES.rglob('*'))) if IMAGES.exists() else 0)

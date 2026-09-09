import urllib.request, re, xml.etree.ElementTree as ET, csv, json, os

url = 'https://docs.google.com/spreadsheets/d/1HhgyEjFA4WvfpVTErI-YcNp9aEby91HY3Zy45rWqSgE/gviz/tq?tqx=out:csv&sheet=GFHF39-159'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
csv_data = urllib.request.urlopen(req).read().decode('utf-8')

# save csv
out_dir = 'Drawing/GF/GFHF39-159 (выполнено)'
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'GFHF39-159.csv'), 'w', encoding='utf-8') as f:
    f.write(csv_data)

reader = csv.reader(csv_data.splitlines())
rows = list(reader)
headers = rows[0]
headers[0] = 'Model'

db = {}
for row in rows[1:]:
    if not row or not row[0]: continue
    model = row[0]
    db[model] = {}
    for i, h in enumerate(headers[1:], 1):
        db[model][h] = row[i]

with open(os.path.join(out_dir, 'gfhf_db.json'), 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=4, ensure_ascii=False)

def fetch_svg(gist_id):
    raw_url = f'https://gist.githubusercontent.com/landbool/{gist_id}/raw'
    req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
    svg_data = urllib.request.urlopen(req).read().decode('utf-8')
    return svg_data, raw_url

svg1, url1 = fetch_svg('0dde9f34f2e205cbb9a8396026c38de1')
svg2, url2 = fetch_svg('c9dbd334718f1e32302ee1eeb9f83d84')

print(f"Headers: {headers}")
print(f"Models: {list(db.keys())}")

def analyze(svg_data, name, out_filename):
    print(f'--- {name} ---')
    root = ET.fromstring(svg_data)
    print('viewBox:', root.attrib.get('viewBox'))
    
    rects = []
    paths_count = 0
    
    for el in root.iter():
        tag = el.tag.split('}')[-1]
        if tag == 'rect' and el.attrib.get('fill') == 'white':
            x = float(el.attrib['x'])
            y = float(el.attrib['y'])
            w = float(el.attrib['width'])
            h = float(el.attrib['height'])
            cx = x + w/2
            cy = y + h/2
            rects.append({'cx': cx, 'cy': cy, 'x': x, 'y': y, 'w': w, 'h': h, 'el': el})
        elif tag == 'path' and el.attrib.get('fill') == 'black':
            paths_count += 1
            
    print(f'White rects: {len(rects)}, Black paths: {paths_count}')
    
    # Sort rects by cy then cx for visual mapping? No, just keep index.
    
    g_params = ET.Element('g', id='parameters')
    for i, r in enumerate(rects):
        print(f'{i}: cx={r["cx"]:.2f}, cy={r["cy"]:.2f}')
        text = ET.Element('text', {
            'data-param': f'P{i}',
            'x': str(r['cx']),
            'y': str(r['cy']),
            'font-size': '26',
            'text-anchor': 'middle',
            'dominant-baseline': 'central',
            'font-family': 'Arial',
            'fill': 'red'
        })
        text.text = str(i)
        g_params.append(text)
        
    root.append(g_params)
    
    with open(os.path.join('scratch', out_filename), 'wb') as f:
        f.write(ET.tostring(root))

os.makedirs('scratch', exist_ok=True)
analyze(svg1, 'SVG1', 'GFHF39-89_numbered.svg')
analyze(svg2, 'SVG2', 'GFHF99-159_numbered.svg')


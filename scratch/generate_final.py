import urllib.request, re, xml.etree.ElementTree as ET, csv, json, os

url = 'https://docs.google.com/spreadsheets/d/1HhgyEjFA4WvfpVTErI-YcNp9aEby91HY3Zy45rWqSgE/gviz/tq?tqx=out:csv&sheet=GFHF39-159'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
csv_data = urllib.request.urlopen(req).read().decode('utf-8')

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
        if i < len(row):
            db[model][h] = row[i]
        else:
            db[model][h] = ''

with open(os.path.join(out_dir, 'gfhf_db.json'), 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=4, ensure_ascii=False)

def fetch_svg(gist_id):
    raw_url = f'https://gist.githubusercontent.com/landbool/{gist_id}/raw'
    req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
    svg_data = urllib.request.urlopen(req).read().decode('utf-8')
    return svg_data

svg1 = fetch_svg('0dde9f34f2e205cbb9a8396026c38de1')
svg2 = fetch_svg('c9dbd334718f1e32302ee1eeb9f83d84')

def analyze_and_calibrate(svg_data, name, out_filename):
    root = ET.fromstring(svg_data)
    viewBox = root.attrib.get('viewBox')
    
    rects = []
    paths_count = 0
    
    # Need to correctly parse the namespaces and keep the SVG intact.
    # ET can mess up namespaces, so we should register them.
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
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
            
    # Remove black paths
    parent_map = {c: p for p in root.iter() for c in p}
    for el in root.iter():
        tag = el.tag.split('}')[-1]
        if tag == 'path' and el.attrib.get('fill') == 'black':
            parent_map[el].remove(el)
            
    rows_y = []
    def get_row(cy):
        for r in rows_y:
            if abs(r - cy) < 20: return r
        rows_y.append(cy)
        return cy
        
    rects.sort(key=lambda r: (get_row(r['cy']), r['cx']))
    
    g_params = ET.Element('g', id='parameters')
    mapping = {}
    for i, r in enumerate(rects):
        p_name = f"P{i}"
        mapping[i] = p_name
        
        text = ET.Element('text', {
            'data-param': p_name,
            'x': str(r['cx']),
            'y': str(r['cy']),
            'font-size': '26',
            'text-anchor': 'middle',
            'dominant-baseline': 'central',
            'font-family': 'Noto Sans JP',
            'fill': 'black'
        })
        text.text = p_name
        g_params.append(text)
        
    root.append(g_params)
    
    out_path = os.path.join(out_dir, out_filename)
    with open(out_path, 'wb') as f:
        f.write(ET.tostring(root, encoding='utf-8', xml_declaration=True))
        
    return viewBox, len(rects), paths_count, mapping

vb1, r1, p1, m1 = analyze_and_calibrate(svg1, 'SVG1', 'GFHF39-89.svg')
vb2, r2, p2, m2 = analyze_and_calibrate(svg2, 'SVG2', 'GFHF99-159.svg')

print(f"SVG1 viewBox: {vb1}, White rects: {r1}, Black paths: {p1}")
print(f"SVG2 viewBox: {vb2}, White rects: {r2}, Black paths: {p2}")
print(f"Headers: {headers[1:]}")
print(f"Models: {list(db.keys())}")

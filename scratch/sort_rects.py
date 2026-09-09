import xml.etree.ElementTree as ET

svg_data = open('scratch/GFHF39-89_numbered.svg', 'r', encoding='utf-8').read()
root = ET.fromstring(svg_data)
rects = []
for el in root.iter():
    tag = el.tag.split('}')[-1]
    if tag == 'rect' and el.attrib.get('fill') == 'white':
        x = float(el.attrib['x'])
        y = float(el.attrib['y'])
        w = float(el.attrib['width'])
        h = float(el.attrib['height'])
        cx = x + w/2
        cy = y + h/2
        rects.append({'cx': cx, 'cy': cy, 'x': x, 'y': y, 'w': w, 'h': h})

rows = []
def get_row(cy):
    for r in rows:
        if abs(r - cy) < 20: return r
    rows.append(cy)
    return cy

rects.sort(key=lambda r: (get_row(r['cy']), r['cx']))

print('Sorted visual order:')
for i, r in enumerate(rects):
    print(f"{i}: cx={r['cx']:.2f}, cy={r['cy']:.2f}")

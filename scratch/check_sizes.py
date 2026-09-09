import xml.etree.ElementTree as ET

svg_data = open('scratch/GFHF39-89_numbered.svg', 'r', encoding='utf-8').read()
root = ET.fromstring(svg_data)
for el in root.iter():
    tag = el.tag.split('}')[-1]
    if tag == 'rect' and el.attrib.get('fill') == 'white':
        print(f"w={el.attrib['width']}, h={el.attrib['height']}")

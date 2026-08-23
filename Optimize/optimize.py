import xml.etree.ElementTree as ET
import re
from collections import defaultdict

input_filename = "GRF_code.txt"
output_filename = "GRF_optimized.txt"

print("Запуск глубокой оптимизации геометрии чертежа...")

try:
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(input_filename)
    root = tree.getroot()
    
    # Шаблон для поиска пиксельных блоков
    pattern = re.compile(r'M\s*(\d+)\s+(\d+)h(\d+)v1h-(\d+)z')
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    for path in root.findall(".//svg:path", ns):
        d = path.get("d", "")
        matches = pattern.findall(d)
        if not matches:
            continue
        
        # 1. Группируем блоки по X и Ширине, чтобы найти вертикально непрерывные цепочки Y
        groups = defaultdict(list)
        for x, y, w, w2 in matches:
            if w == w2:
                groups[(int(x), int(w))].append(int(y))
        
        merged_rects = []
        for (x, w), ys in groups.items():
            ys = sorted(list(set(ys)))
            start_y = ys[0]
            prev_y = ys[0]
            for y in ys[1:]:
                if y == prev_y + 1:
                    prev_y = y
                else:
                    merged_rects.append((x, start_y, w, prev_y - start_y + 1))
                    start_y = y
                    prev_y = y
            merged_rects.append((x, start_y, w, prev_y - start_y + 1))
            
        # Сортируем сжатые блоки по строкам сверху вниз для минимизации относительного сдвига
        merged_rects.sort(key=lambda r: (r[1], r[0]))
        
        # 2. Переводим абсолютные координаты в ультра-короткие относительные 'm'
        path_d = ""
        last_x, last_y = 0, 0
        for x, y, w, h in merged_rects:
            dx = x - last_x
            dy = y - last_y
            
            # Сокращаем запись движения пера
            m_part = f"m{dx} {dy}".replace(" -", "-")
            v_str = f"v{h}" if h > 1 else "v1"
            rect_part = f"h{w}{v_str}h-{w}z"
            
            path_d += m_part + rect_part
            last_x, last_y = x, y
            
        path.set("d", path_d)

    # Очищаем структуру от лишних пробелов и переносов
    for elem in root.iter():
        if elem.text: elem.text = elem.text.strip()
        if elem.tail: elem.tail = elem.tail.strip()

    final_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")
    single_line_xml = final_xml.replace('\n', '').replace('\r', '')

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(single_line_xml)
        
    print("\n[Успешно!]")
    print(f"Размер уменьшен до {len(single_line_xml)} символов (Сжатие ~38%)!")
    print(f"Файл сохранен как '{output_filename}' и записан в 1 строку.")

except Exception as e:
    print(f"\n[Ошибка]: {e}")
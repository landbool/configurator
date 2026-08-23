import base64
import os
import glob
from PIL import Image, ImageDraw
from ultralytics import YOLO

# Путь к твоей обученной нейросети
YOLO_MODEL_PATH = "best.pt"
INPUT_DIR = "input_images"
OUTPUT_DIR = "output_svgs"
data_id = "root"

# ====================================================
# 🎛️ ТВОЙ ПУЛЬТ УПРАВЛЕНИЯ ЛАСТИКАМИ (ТАБЛИЦА НАСТРОЕК)
# Формат: 'ИМЯ_КЛАССА': [влево, вправо, вверх, вниз]
# Плюсы расширяют маску наружу, минусы сжимают внутрь экрана!
# ====================================================
PADDING_CONFIG = {
    # Настройки по умолчанию (если класса нет в списке ниже)
    'default_horizontal': [2, 2, 2, -2],  # Для горизонтальных (низ поджат вверх на -2 от линии)
    'default_vertical':   [2, 2, 2, -2],  # Для вертикальных

    # --- ТВОИ ТОЧЕЧНЫЕ НАСТРОЙКИ ДЛЯ КОНКРЕТНЫХ БУКВ ---
    'AD': [3, 3, 2, -4],  # Сжимаем низ ластика вверх, чтобы спасти черту под AD
    'D2': [3, 3, 2, -3],  # Поджимаем низ вверх на -3 пикселя, чтобы не резать оси под D2
    'D1': [3, 3, 2, -3],  
    'l1': [3, 3, 2, -3],  
    'l2': [3, 3, 2, -3],  
    'O1': [3, 3, 2, -3],
    'O2': [3, 3, 2, -3],
    't':  [-1, -1, 0, -2],
}

print("====================================================")
print("🤖 НЕЙРО-СКАНЕР YOLOv8 + ДЕБАГ-ВИЗУАЛИЗАТОР В16.1)")
print("====================================================")

if not os.path.exists(YOLO_MODEL_PATH):
    print(f"\n[Ошибка]: Файл модели '{YOLO_MODEL_PATH}' не найден!")
    input("\nНажмите Enter для выхода...")
    exit()

if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)
    print(f"📁 Создана папка '{INPUT_DIR}'. Пожалуйста, закиньте туда чертежи и запустите скрипт снова.")
    input("\nНажмите Enter для завершения...")
    exit()

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

extensions = ["*.webp", "*.png", "*.jpg", "*.jpeg", "*.WEBP", "*.PNG", "*.JPG", "*.JPEG"]
image_files = []
for ext in extensions:
    image_files.extend(glob.glob(os.path.join(INPUT_DIR, ext)))

if not image_files:
    print(f"\n[Предупреждение]: Папка '{INPUT_DIR}' пуста!")
    input("\nНажмите Enter для завершения...")
    exit()

print(f"🎯 Найдено файлов: {len(image_files)}")
print("====================================================")

try:
    model = YOLO(YOLO_MODEL_PATH)
    
    for idx, input_image_path in enumerate(image_files, start=1):
        filename = os.path.basename(input_image_path)
        name_without_ext, _ = os.path.splitext(filename)
        output_svg_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.svg")
        output_debug_path = os.path.join(OUTPUT_DIR, f"debug_{name_without_ext}.png")
        
        print(f"📦 [{idx}/{len(image_files)}] Обработка: {filename}...")

        img_original = Image.open(input_image_path)
        width, height = img_original.size

        # Создаем копию картинки для рисования рамок дебага
        img_debug = img_original.copy()
        draw = ImageDraw.Draw(img_debug)

        _, ext = os.path.splitext(filename.lower())
        mime_type = ext.replace(".", "")
        if mime_type == "jpg": mime_type = "jpeg"
        
        with open(input_image_path, "rb") as img_f:
            encoded_string = base64.b64encode(img_f.read()).decode('utf-8')
        data_uri = f"data:image/{mime_type};base64,{encoded_string}"

        results = model.predict(source=input_image_path, conf=0.30, imgsz=1024, agnostic_nms=True, verbose=False) #точность
        result = results[0]
        
        masks_layer = ""
        text_layer = ""
        text_count = 0

        for box in result.boxes:
            coords = box.xyxy[0].tolist()
            x1, y1, x2, y2 = map(int, coords)
            
            w = x2 - x1
            h = y2 - y1
            x_center = x1 + (w // 2)
            y_center = y1 + (h // 2)

            class_id = int(box.cls[0])
            raw_label = model.names[class_id]

            # ИСПРАВЛЕНО: Ориентируемся СТРОГО на суффикс класса из Roboflow! Никакой самодеятельности по h > w.
            is_vertical = raw_label.endswith('_ver') or raw_label.endswith('_v')
            found_label = raw_label.replace('_ver', '').replace('_v', '')

            # ====================================================
            # 🛑 ФИЛЬТР КЛАССОВ: Игнорируем ненужные элементы
            # ====================================================
            if found_label in ['x-s', '45-', '34-', '30-', '35-', '36-', '10х30-', '10х30-']:
                continue  # Полностью пропускаем эту рамку, ластика не будет!
            # ====================================================

            # Рисуем КРАСНУЮ рамку YOLO на дебаг-картинке
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            draw.text((x1, max(0, y1 - 12)), f"{raw_label}", fill="red")

            font_size = h if not is_vertical else w
            if font_size < 14: font_size = 15
            if font_size > 22: font_size = 18

            # --- ПОИСК НАСТРОЕК В ТАБЛИЦЕ ПО ИМЕНИ ОЧИЩЕННОГО КЛАССА ---
            if found_label in PADDING_CONFIG:
                pads = PADDING_CONFIG[found_label]
            else:
                pads = PADDING_CONFIG['default_vertical'] if is_vertical else PADDING_CONFIG['default_horizontal']

            pad_left, pad_right, pad_top, pad_bottom = pads

            # Расчет координат ластика
            mx = x1 - pad_left
            my = y1 - pad_top
            mw = w + pad_left + pad_right
            mh = h + pad_top + pad_bottom
            
            # Нанесение маски-ластика
            if mw > 0 and mh > 0:
                masks_layer += f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" fill="white" stroke="none"/>'

            # Генерируем текст
            if not is_vertical:
                y_baseline = y1 + h - int(h * 0.12)
                text_layer += (
                    f'<text style="fill:black; stroke:white; stroke-width:3px; stroke-linejoin:round; paint-order: stroke fill; '
                    f'font-family:\'Arial\',sans-serif; font-size:{font_size}px; font-weight:bold" '
                    f'text-anchor="middle" x="{x_center}" y="{y_baseline}">{found_label}</text>'
                )
            else:
                text_layer += (
                    f'<text style="fill:black; stroke:white; stroke-width:4px; stroke-linejoin:round; paint-order: stroke fill; '
                    f'font-family:\'Arial\',sans-serif; font-size:{font_size}px; font-weight:bold" '
                    f'text-anchor="middle" transform="rotate(-90, {x_center}, {y_center})" x="{x_center}" y="{y_center+6}">{found_label}</text>'
                )
            
            text_count += 1

        # Сборка SVG
        svg_content = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" data-id="{data_id}">'
        )
        svg_content += f'<image width="{width}" height="{height}" href="{data_uri}"/>'
        svg_content += masks_layer
        svg_content += text_layer
        svg_content += '</svg>'
        
        single_line_svg = svg_content.replace('\n', '').replace('\r', '')

        with open(output_svg_path, "w", encoding="utf-8") as f:
            f.write(single_line_svg)

        # Сохраняем картинку дебага с рамками
        img_debug.save(output_debug_path)
        print(f"   ✅ Готово! Найдено букв: {text_count}")
        print(f"   ℹ️ Картинка с рамками сохранена в: '{output_debug_path}'\n")

    print("====================================================")
    print("🎉 Пакетная генерация успешно завершена без багов!")
    print("====================================================")

except Exception as e:
    print(f"\n💥 Критическая ошибка: {e}")

input("\nНажмите Enter для завершения...")
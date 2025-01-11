
import os
import time
import csv
import pytesseract
from PIL import Image
import easyocr

# 1. Adjust this folder path to point to your images directory
IMAGES_FOLDER = "screenshots_Mario Kart - Super Circuit (Europe)_20250111_1311_87ae2cf2"

def main():
    # 2. Collect image paths (png/jpg/jpeg)
    image_paths = [
        os.path.join(IMAGES_FOLDER, f)
        for f in os.listdir(IMAGES_FOLDER)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    # 3. Initialize EasyOCR reader (English example; add more languages as needed)
    easyocr_reader = easyocr.Reader(['en'])

    # Data storage
    results = []
    tesseract_times = []
    easyocr_times = []

    # 4. Run Tesseract on each image
    for img_path in image_paths:
        start_time = time.time()
        text_tess = pytesseract.image_to_string(Image.open(img_path))
        elapsed_tess = (time.time() - start_time) * 1000  # ms
        tesseract_times.append(elapsed_tess)

        # Store result
        results.append([
            os.path.basename(img_path),
            "Tesseract",
            f"{elapsed_tess:.2f}",
            text_tess.strip()
        ])

    # 5. Run EasyOCR on each image
    for img_path in image_paths:
        start_time = time.time()
        text_easy = easyocr_reader.readtext(img_path, detail=0)
        elapsed_easy = (time.time() - start_time) * 1000  # ms
        easyocr_times.append(elapsed_easy)

        # Join text segments found by EasyOCR
        recognized_text = " ".join(text_easy).strip()

        # Store result
        results.append([
            os.path.basename(img_path),
            "EasyOCR",
            f"{elapsed_easy:.2f}",
            recognized_text
        ])

    # 6. Write results to a CSV file
    with open("ocr_results.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["image_name", "ocr_engine", "time_ms", "recognized_text"])
        writer.writerows(results)

    # 7. Print average processing times
    avg_tesseract_time = sum(tesseract_times) / len(tesseract_times) if tesseract_times else 0
    avg_easyocr_time = sum(easyocr_times) / len(easyocr_times) if easyocr_times else 0
    print(f"Average time (Tesseract): {avg_tesseract_time:.2f} ms")
    print(f"Average time (EasyOCR): {avg_easyocr_time:.2f} ms")

if __name__ == "__main__":
    main()

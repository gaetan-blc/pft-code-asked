import os
import time
import csv
from paddleocr import PaddleOCR

IMAGES_FOLDER = "screenshots_Mario Kart - Super Circuit (Europe)_20250111_1311_87ae2cf2"

def main():
    # 1. Collect image paths (png/jpg/jpeg)
    image_paths = [
        os.path.join(IMAGES_FOLDER, f)
        for f in os.listdir(IMAGES_FOLDER)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    # 2. Initialize PaddleOCR (English example; set "lang='en'")
    # For additional languages, see PaddleOCR docs.
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  

    results = []
    processing_times = []

    # 3. Run PaddleOCR on each image
    for img_path in image_paths:
        start_time = time.time()
        # Returns a list of lists. Each sub-list contains detection info + text + confidence
        ocr_result = ocr.ocr(img_path, cls=True)
        elapsed_ms = (time.time() - start_time) * 1000
        processing_times.append(elapsed_ms)

        # Concatenate all recognized text segments
        recognized_text = []
        for region in ocr_result:
            for line in region:
                # line[1] is tuple (text, confidence)
                recognized_text.append(line[1][0])
        recognized_text = " ".join(recognized_text).strip()

        # Store result
        results.append([
            os.path.basename(img_path),
            f"{elapsed_ms:.2f}",
            recognized_text
        ])

    # 4. Write results to a CSV file
    with open("paddleocr_results.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["image_name", "time_ms", "recognized_text"])
        writer.writerows(results)

    # 5. Print average processing time
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        print(f"Average processing time (PaddleOCR): {avg_time:.2f} ms")

if __name__ == "__main__":
    main()

from PIL import Image
import numpy as np
import os
import time


folder_path = "./renders"
for filename in os.listdir(folder_path):
    if filename.endswith("_mask.png"):
        image_path = os.path.join(folder_path, filename)
        image = Image.open(image_path).convert("L")
        image_data = np.array(image)

        unique_values, counts = np.unique(image_data, return_counts=True)

        print(f"\nProcessing {filename}")
        print("Unique Pixel Values and Their Counts:")
        for value, count in zip(unique_values, counts):
            print(f"Value: {value}, Count: {count}")

        expected_values = {0, 10, 20}
        actual_values = set(unique_values)

        if actual_values.issubset(expected_values):
            print("✅ The mask contains only the expected pixel values.")
        else:
            print("❌ Unexpected pixel values found!")
            time.sleep(10)
            break

print("\n")
print("All masks contain only the expected pixel values.")
time.sleep(10)
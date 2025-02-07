from PIL import Image
import numpy as np
import os
import time


def threshold_mask(pixel_array):
    pixel_array[(pixel_array < 10)] = 0
    pixel_array[(pixel_array >= 10) & (pixel_array <= 19)] = 10
    pixel_array[(pixel_array >= 20) & (pixel_array <= 29)] = 20
    return pixel_array


def process_segmentation_masks(folder):
    print("Refining the masks to be pixel perfect...")
    time.sleep(5)
    for file_name in os.listdir(folder):
        if file_name.endswith("mask.png"):
            file_path = os.path.abspath(os.path.join(folder, file_name))
            image = Image.open(file_path).convert("L")
            image_array = np.array(image)

            print(f"\nProcessing {file_name}")
            
            unique_values, counts = np.unique(image_array, return_counts=True)
            print(f"Before Thresholding: {dict(zip(unique_values, counts))}")

            thresholded_array = threshold_mask(image_array)
            thresholded_image = Image.fromarray(thresholded_array.astype(np.uint8))
            thresholded_image.save(file_path)

            unique_values, counts = np.unique(thresholded_array, return_counts=True)
            print(f"After Thresholding: {dict(zip(unique_values, counts))}")
            
    print("\nProcess complete.")
    time.sleep(10)


if __name__ == "__main__":
    renders_folder = "renders"
    process_segmentation_masks(renders_folder)
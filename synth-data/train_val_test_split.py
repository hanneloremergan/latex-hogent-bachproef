import os
import time
import shutil
import random


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def copy_files(indices, src_dir, dest_img_dir, dest_annot_dir):
    for idx in indices:
        render_file = os.path.join(src_dir, f"render_{idx}.png")
        mask_file = os.path.join(src_dir, f"render_{idx}_mask.png")
        dest_img = os.path.join(dest_img_dir, f"img_{idx}.png")
        dest_mask = os.path.join(dest_annot_dir, f"img_{idx}.png")
        shutil.copy2(render_file, dest_img)
        shutil.copy2(mask_file, dest_mask)


def main():
    base_dir = os.getcwd()
    
    renders_dir = os.path.join(base_dir, "renders")
    hdri_dir = os.path.join(base_dir, "assets", "hdri")
    datasets_dir = os.path.join(base_dir, "datasets")
    
    train_dir, val_dir, test_dir, trainannot_dir, valannot_dir, testannot_dir = [
    os.path.join(datasets_dir, folder) for folder in ["train", "val", "test", "trainannot", "valannot", "testannot"]
    ]

    for d in [datasets_dir, train_dir, val_dir, test_dir, trainannot_dir, valannot_dir, testannot_dir]:
        create_dir(d)
    
    num_files = len(os.listdir(renders_dir))
    print(f"Total number of render outputs (images + masks): {num_files}")
    num_groups = len(os.listdir(hdri_dir))
    print(f"Total number of HDRIs: {num_groups}")
    group_size = num_files // num_groups // 2
    print(f"Number of rendered images/masks per HDRI: {group_size}")
    
    print("\nStarting process...")
    time.sleep(5)
    
    print("Copying and splitting renders into train, validation, and test datasets...")
    for group in range(num_groups):
        group_start = group * group_size
        indices = list(range(group_start, group_start + group_size))
        random.shuffle(indices)
        
        num_train = int(group_size * 0.70)
        num_val = int(group_size * 0.15)
        
        train_indices = indices[:num_train]
        val_indices = indices[num_train:num_train + num_val]
        test_indices = indices[num_train + num_val:]
        
        copy_files(train_indices, renders_dir, train_dir, trainannot_dir)
        copy_files(val_indices, renders_dir, val_dir, valannot_dir)
        copy_files(test_indices, renders_dir, test_dir, testannot_dir)
    
    print("\nProcess complete.")
    time.sleep(10)


if __name__ == "__main__":
    main()

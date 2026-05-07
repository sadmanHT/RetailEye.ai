import os
import shutil
from pathlib import Path
from typing import Union, Dict, List

def fix_and_merge_datasets(
    dataset1_path: Union[str, Path],
    dataset2_path: Union[str, Path],
    output_path: Union[str, Path],
    person_idx1: int,
    person_idx2: int
) -> None:
    """
    Merges two YOLO format datasets into a single output dataset folder.
    - Rewrites label files to only keep the person class, mapped to class index 0.
    - Discards labels of any other classes.
    - Skips images/labels that do not contain any person.
    - Preserves train, valid (or val), and test splits.
    - Prints a summary of the merged datasets.

    Args:
        dataset1_path: Path to the first YOLO dataset.
        dataset2_path: Path to the second YOLO dataset.
        output_path: Path where the merged dataset should be saved.
        person_idx1: The class index of 'person' in dataset 1.
        person_idx2: The class index of 'person' in dataset 2.
    """
    dataset1_path = Path(dataset1_path)
    dataset2_path = Path(dataset2_path)
    output_path = Path(output_path)

    # YOLO datasets usually use these split folder names
    splits = ["train", "val", "valid", "test"]

    # Keep track of counts per split
    summary_counts: Dict[str, int] = {split: 0 for split in splits}

    # Helper function to process a single dataset
    def process_dataset(ds_path: Path, person_idx: int, prefix: str):
        for split in splits:
            images_dir = ds_path / "images" / split
            labels_dir = ds_path / "labels" / split

            # Some datasets structure splits top-level: dataset/train/images and dataset/train/labels
            if not images_dir.exists():
                images_dir = ds_path / split / "images"
                labels_dir = ds_path / split / "labels"

            if not images_dir.exists() or not labels_dir.exists():
                continue

            # Ensure output directories exist
            out_images_dir = output_path / "images" / split
            out_labels_dir = output_path / "labels" / split
            out_images_dir.mkdir(parents=True, exist_ok=True)
            out_labels_dir.mkdir(parents=True, exist_ok=True)

            # Process all labels in this split
            for label_file in labels_dir.glob("*.txt"):
                with open(label_file, "r") as f:
                    lines = f.readlines()

                # Filter lines where the class index matches the dataset's person index
                person_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    class_id = int(parts[0])
                    if class_id == person_idx:
                        # Remap to zero
                        person_lines.append(f"0 {' '.join(parts[1:])}\n")

                # If there are no person annotations in this image, skip it
                if not person_lines:
                    continue

                # Find the corresponding image file (could be jpg, png, jpeg, etc.)
                image_files = list(images_dir.glob(f"{label_file.stem}.*"))
                if not image_files:
                    continue
                image_file = image_files[0] # Take the first match

                # To prevent naming collisions, prepend the dataset prefix
                new_stem = f"{prefix}_{label_file.stem}"
                out_label_file = out_labels_dir / f"{new_stem}.txt"
                out_image_file = out_images_dir / f"{new_stem}{image_file.suffix}"

                # Write the updated label
                with open(out_label_file, "w") as f:
                    f.writelines(person_lines)

                # Copy the image if it doesn't exist
                if not out_image_file.exists():
                    shutil.copy2(image_file, out_image_file)

                # Update stats
                summary_counts[split] += 1

    print("Starting dataset merge...")
    
    # Process both datasets
    process_dataset(dataset1_path, person_idx1, prefix="ds1")
    process_dataset(dataset2_path, person_idx2, prefix="ds2")

    # Print summary
    print("\n--- Dataset Merge Summary ---")
    total_images = 0
    for split, count in summary_counts.items():
        if count > 0:
            print(f"{split.capitalize()}: {count} images containing persons")
            total_images += count
    
    if total_images == 0:
        print("No images with the person class were found in the provided splits.")
    else:
        print(f"Total merged images: {total_images}")
    print(f"Merged dataset saved to: {output_path}")

if __name__ == "__main__":
    # Example usage:
    # fix_and_merge_datasets(
    #     dataset1_path="data/raw/dataset_A",
    #     dataset2_path="data/raw/dataset_B",
    #     output_path="data/processed/merged_retail_dataset",
    #     person_idx1=0,  # 'person' is class 0 in dataset A
    #     person_idx2=14  # 'person' is class 14 in dataset B
    # )
    pass

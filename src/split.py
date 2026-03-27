import os
import shutil
import random

SOURCE = "../dataset"
DEST = "../dataset_split"

classes = ["real_aug", "suspicious"]
split_ratio = 0.8

for cls in classes:
    files = os.listdir(f"{SOURCE}/{cls}")
    random.shuffle(files)

    split = int(len(files) * split_ratio)

    train_files = files[:split]
    val_files = files[split:]

    for t in ["train", "val"]:
        os.makedirs(f"{DEST}/{t}/{cls}", exist_ok=True)

    for f in train_files:
        shutil.copy(f"{SOURCE}/{cls}/{f}", f"{DEST}/train/{cls}/{f}")

    for f in val_files:
        shutil.copy(f"{SOURCE}/{cls}/{f}", f"{DEST}/val/{cls}/{f}")
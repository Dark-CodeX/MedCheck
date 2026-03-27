import cv2
import numpy as np
import os
import random
from tqdm import tqdm

RAW_DIR = "../dataset/raw"
NORM_DIR = "../dataset/normalized"
REAL_OUT = "../dataset/real_aug"
FAKE_OUT = "../dataset/suspicious"

os.makedirs(NORM_DIR, exist_ok=True)
os.makedirs(REAL_OUT, exist_ok=True)
os.makedirs(FAKE_OUT, exist_ok=True)

# -----------------------------------
# 1. NORMALIZATION (RESIZE + PAD)
# -----------------------------------
def resize_with_padding(img, size=224):
    h, w = img.shape[:2]
    scale = size / max(h, w)
    nh, nw = int(h * scale), int(w * scale)

    img_resized = cv2.resize(img, (nw, nh))

    canvas = np.zeros((size, size, 3), dtype=np.uint8)
    y_offset = (size - nh) // 2
    x_offset = (size - nw) // 2

    canvas[y_offset:y_offset+nh, x_offset:x_offset+nw] = img_resized
    return canvas


# -----------------------------------
# 2. REALISTIC FAKE GENERATOR
# -----------------------------------
def realistic_fake(img):
    img = img.copy()
    h, w = img.shape[:2]

    choice = random.choice([
        "print_defect",
        "lighting_issue",
        "perspective_distortion",
        "partial_damage",
        "low_quality_reprint"
    ])

    if choice == "print_defect":
        for _ in range(random.randint(1,3)):
            x1 = random.randint(0, w-60)
            y1 = random.randint(0, h-60)
            patch = img[y1:y1+60, x1:x1+60]

            patch = cv2.GaussianBlur(patch, (7,7), 0)
            patch = cv2.convertScaleAbs(patch, alpha=1.2, beta=20)
            img[y1:y1+60, x1:x1+60] = patch

    elif choice == "lighting_issue":
        overlay = np.zeros_like(img)
        cv2.circle(overlay, (w//2, h//2),
                   random.randint(50,120), (50,50,50), -1)
        img = cv2.add(img, overlay)

    elif choice == "perspective_distortion":
        pts1 = np.float32([[0,0],[w,0],[0,h],[w,h]])
        shift = 10
        pts2 = np.float32([
            [random.randint(0,shift), random.randint(0,shift)],
            [w-random.randint(0,shift), random.randint(0,shift)],
            [random.randint(0,shift), h-random.randint(0,shift)],
            [w-random.randint(0,shift), h-random.randint(0,shift)]
        ])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        img = cv2.warpPerspective(img, M, (w, h))

    elif choice == "partial_damage":
        for _ in range(3):
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            x2 = x1 + random.randint(20, 100)
            y2 = y1 + random.randint(5, 20)
            cv2.rectangle(img, (x1,y1), (x2,y2), (200,200,200), -1)

    elif choice == "low_quality_reprint":
        img = cv2.GaussianBlur(img, (5,5), 0)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), random.randint(5,30)]
        _, encimg = cv2.imencode('.jpg', img, encode_param)
        img = cv2.imdecode(encimg, 1)

    return img


# -----------------------------------
# 3. REAL AUGMENTATION
# -----------------------------------
def augment_real(img):
    img = img.copy()

    # rotation
    angle = random.uniform(-10, 10)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
    img = cv2.warpAffine(img, M, (w, h))

    # brightness/contrast
    alpha = random.uniform(0.9, 1.1)
    beta = random.randint(-10, 10)
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    # flip
    if random.random() > 0.5:
        img = cv2.flip(img, 1)

    return img


# -----------------------------------
# 4. PIPELINE
# -----------------------------------
real_count = 0
fake_count = 0
norm_count = 0

files = os.listdir(RAW_DIR)

for i, file in enumerate(tqdm(files)):
    path = os.path.join(RAW_DIR, file)
    img = cv2.imread(path)

    if img is None:
        continue

    # Step 1: Normalize RAW → save
    norm = resize_with_padding(img, 224)
    cv2.imwrite(f"{NORM_DIR}/norm_{i}.jpg", norm)
    norm_count += 1

    # Step 2: Save original as real
    cv2.imwrite(f"{REAL_OUT}/real_{i}_0.jpg", norm)
    real_count += 1

    # Step 3: Augment real (3 copies)
    for j in range(3):
        aug = augment_real(norm)
        cv2.imwrite(f"{REAL_OUT}/real_{i}_{j+1}.jpg", aug)
        real_count += 1

    # Step 4: Generate fake (2 copies)
    for k in range(2):
        fake = realistic_fake(norm)
        cv2.imwrite(f"{FAKE_OUT}/fake_{i}_{k}.jpg", fake)
        fake_count += 1


print("Normalized:", norm_count)
print("Real:", real_count)
print("Fake:", fake_count)
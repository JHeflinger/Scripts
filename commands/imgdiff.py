"""
author: Jason Heflinger
description: Compares the differences between 2 given images
"""

import sys
import subprocess
from PIL import Image, ImageChops
import matplotlib.pyplot as plt
import os

def compare_images(img_path1, img_path2):
    if not os.path.exists(img_path1):
        print(f"Error: File not found -> {img_path1}")
        return
    if not os.path.exists(img_path2):
        print(f"Error: File not found -> {img_path2}")
        return
    img1 = Image.open(img_path1).convert("RGB")
    img2 = Image.open(img_path2).convert("RGB")
    if img1.size != img2.size:
        print("Warning: Images have different sizes, resizing the second image to match the first.")
        img2 = img2.resize(img1.size)
    diff = ImageChops.difference(img1, img2)
    diff_pixels = sum(1 for x in range(diff.width) for y in range(diff.height)
                      if diff.getpixel((x, y)) != (0, 0, 0))
    total_pixels = diff.width * diff.height
    difference_ratio = diff_pixels / total_pixels * 100
    print(f"Different pixels: {diff_pixels}/{total_pixels} ({difference_ratio:.2f}%)")
    fig, axes = plt.subplots(3, 1, figsize=(4, 8))
    axes[0].imshow(img1)
    axes[0].set_title("Ground Truth")
    axes[1].imshow(img2)
    axes[1].set_title("My Truth")
    axes[2].imshow(diff)
    axes[2].set_title("Difference")
    for ax in axes:
        ax.axis("off")
    plt.show()

if (len(sys.argv) == 3):
    compare_images(sys.argv[1], sys.argv[2])
else:
    print("Incorrect usage. Corrent usage is:")
    print("\timgdiff <image_path_1> <image_path_2>")

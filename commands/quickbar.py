"""
author: Jason Heflinger
description: Puts all inputted arguments onto a histogram 
"""

import sys
import math
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python quickbar.py <num1> <num2> <num3> ...")
        sys.exit(1)
    try:
        values = [float(arg) for arg in sys.argv[1:]]
    except ValueError:
        print("Error: All arguments must be numbers.")
        sys.exit(1)
    bin_size = int(len(sys.argv) / 10.0)
    min_val = min(values)
    max_val = max(values)
    start = math.floor(min_val / bin_size) * bin_size
    end = math.ceil(max_val / bin_size) * bin_size
    bins = list(range(int(start), int(end) + bin_size, bin_size))
    plt.figure()
    plt.hist(values, bins=bins)
    plt.title(f"Value Distribution (bin size = {bin_size})")
    plt.xlabel("Value range")
    plt.ylabel("Count")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

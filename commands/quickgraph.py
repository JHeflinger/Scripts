"""
author: Jason Heflinger
description: Puts all inputted arguments onto a graph 
"""

import sys
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python quickgraph.py <num1> <num2> <num3> ...")
        sys.exit(1)
    try:
        values = [float(arg) for arg in sys.argv[1:]]
    except ValueError:
        print("Error: All arguments must be numbers.")
        sys.exit(1)
    x = list(range(len(values)))
    plt.figure()
    plt.plot(x, values, marker='o')
    plt.title("Input Values Plot")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

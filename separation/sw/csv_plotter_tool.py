#Use this to plot a series of columns and show them next to each other
#Pipe the input in as a csv
#Matplotlib is great :(

import matplotlib.pyplot as plt
from pexpect import EOF  # type: ignore

def plot(column: list[float]) -> None:
    x = list(range(len(column)))
    plt.plot(x, column)


if __name__ == "__main__":
    line = ""
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    data = [list(map(float, line.split(","))) for line in lines]
    columns: list[list[float]] = list(zip(*data)) #type: ignore
    
    for (i, column) in enumerate(columns, start=1):
        plt.subplot(len(columns), 1, i)
        plot(column)

    plt.show()
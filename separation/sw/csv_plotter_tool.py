#Use this to plot a series of columns and show them next to each other
#Pipe the input in as a csv
#Matplotlib is great :(

import matplotlib.pyplot as plt  # type: ignore

def plot(column: list[float]) -> None:
    x = list(range(len(column)))
    plt.plot(x, column)


if __name__ == "__main__":
    line = ""
    lines = []
    while True:
        line = input()
        if line != "END":
            lines.append(line)
        else:
            break

    data = [list(map(float, line.split(","))) for line in lines]
    columns: list[list[float]] = list(zip(*data)) #type: ignore
    
    for (i, column) in enumerate(columns, start=1):
        plt.subplot(len(columns), 1, i)
        plot(column)

    plt.show()
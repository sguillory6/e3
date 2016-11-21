from random import normalvariate

# Will extract items from a sorted list according to a normal distribution, useful for building up snapshots
data = [line.strip().split(" ") for line in open("repo_sizes.txt", 'r')]


def normal_choice(data):
    mean = (len(data) - 1) / 2
    stddev = len(data) / 1
    while True:
        index = int(normalvariate(mean, stddev) + 0.5)
        if 0 <= index < len(data):
            return data[index]


for _ in range(20):
    print normal_choice(data)[0].replace("\t", " ")

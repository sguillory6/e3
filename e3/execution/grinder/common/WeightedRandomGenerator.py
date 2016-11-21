import random


def weighted_choice(weights):
    """
    Choose an index based on the index's weight
    :param weights: a list of weights
    :type weights: list(int)
    :return: a number between 0 and len(weights) - 1
    :rtype: int
    """
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i

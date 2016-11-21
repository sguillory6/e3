import numpy as np
import scipy.stats as stats

# Will extract itemts from a sorted list according to a power law distribution, useful for building up snapshots
data = [line.strip().split(" ") for line in open("repo_sizes.txt", 'r')]


def truncated_power_law(a, m):
    x = np.arange(1, m + 1, dtype='float')
    pmf = 1 / x ** a
    pmf /= pmf.sum()
    return stats.rv_discrete(values=(range(1, m + 1), pmf))


a, m = 0.5, len(data)
d = truncated_power_law(a=a, m=m)

sample = d.rvs(size=10)
print "Size,RepoId,Index"
for s in sample:
    print "%s,%s" % (data[s][0].replace("\t", ","), s)

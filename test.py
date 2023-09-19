x = 45
N = [20, 5, 35]

buff = []

for i in range(min(N)):
    for n in N:
        buff.append([x-n, 1])
    
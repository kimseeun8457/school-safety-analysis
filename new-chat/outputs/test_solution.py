from solution import solution


test_cases = [
    ([[1, 2], [2, 3], [2, 1]], 4, 4, 2),
    ([[1, 2], [2, 3], [2, 1]], 1, 7, 0),
    ([[3, 3], [3, 3]], 7, 1, 6),
    ([[3, 3], [3, 3]], 6, 1, -1),
]

print(f"{'info':<28} {'n':>3} {'m':>3} {'result':>7}")
for info, n, m, expected in test_cases:
    result = solution(info, n, m)
    print(f"{str(info):<28} {n:>3} {m:>3} {result:>7}")

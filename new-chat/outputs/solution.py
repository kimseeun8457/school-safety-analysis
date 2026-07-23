def solution(info, n, m):
    INF = float("inf")
    # dp[a]: A의 흔적이 a일 때 가능한 B의 최소 흔적
    dp = [INF] * n
    dp[0] = 0

    for a_trace, b_trace in info:
        next_dp = [INF] * n

        for a_total in range(n):
            b_total = dp[a_total]
            if b_total == INF:
                continue

            # B가 현재 물건을 훔치는 경우
            next_dp[a_total] = min(next_dp[a_total], b_total + b_trace)

            # A가 현재 물건을 훔치는 경우
            next_a_total = a_total + a_trace
            if next_a_total < n:
                next_dp[next_a_total] = min(next_dp[next_a_total], b_total)

        dp = next_dp

    for a_total, b_total in enumerate(dp):
        if b_total < m:
            return a_total

    return -1
if __name__ == "__main__":
    test_cases = [
        ([[1, 2], [2, 3], [2, 1]], 4, 4),
        ([[1, 2], [2, 3], [2, 1]], 1, 7),
        ([[3, 3], [3, 3]], 7, 1),
        ([[3, 3], [3, 3]], 6, 1),
    ]

    print("info, n, m, result")
    for info, n, m in test_cases:
        result = solution(info, n, m)
        print(info, n, m, result)

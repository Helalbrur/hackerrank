# Find the Runner-Up Score!  
# Difficulty : Easy
# Track      : Basic Data Types
# Tags       : 
# Solved on  : 2026-05-14
# Attempt    : #1
# HackerRank : https://www.hackerrank.com/challenges/1374/problem

if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())
    f = -101
    s = -101
    for x in arr:
        if x > f:
            s = f
            f = x
        elif x > s and x < f:
            s = x
    print(s)

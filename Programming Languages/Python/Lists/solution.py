# Lists
# Difficulty : Easy
# Track      : Basic Data Types
# Tags       : 
# Solved on  : 2026-05-14
# Attempt    : #1
# HackerRank : https://www.hackerrank.com/challenges/7888/problem

if __name__ == '__main__':
    N = int(input())
    arr = list()
    for _ in range(N):
        parts = input().split()
        cmd = parts[0]
        if cmd == 'append':
            a = int(parts[1])
            arr.append(a)
        elif cmd == 'print':
            print(arr)
        elif cmd == 'insert':
            a = int(parts[1])
            if a > len(arr):
                continue
            b = int(parts[2])
            arr.insert(a,b)
        elif cmd =='sort':
            if not arr:
                continue
            arr.sort()
        elif cmd == 'pop':
            if not arr:
                continue
            l = len(arr)-1
            arr.pop(l)
        elif cmd == 'remove':
            if not arr:
                continue
            arr.remove(int(parts[1]))
        elif cmd =='reverse':
            if not arr:
                continue
            arr.reverse()

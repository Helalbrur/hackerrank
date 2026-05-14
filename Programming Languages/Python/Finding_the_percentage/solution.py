# Finding the percentage
# Difficulty : Easy
# Track      : Basic Data Types
# Tags       : 
# Solved on  : 2026-05-14
# Attempt    : #1
# HackerRank : https://www.hackerrank.com/challenges/1377/problem

if __name__ == '__main__':
    n = int(input())
    student_marks = {}
    for _ in range(n):
        name, *line = input().split()
        scores = list(map(float, line))
        student_marks[name] = scores
    query_name = input()
    result = sum(student_marks[query_name]) / len(student_marks[query_name])
    print(f"{result:.2f}")

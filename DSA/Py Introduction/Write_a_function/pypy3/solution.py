# Write a function
# Difficulty : Medium
# Track      : Introduction
# Tags       : 
# Solved on  : 2026-05-14
# Attempt    : #1
# HackerRank : https://www.hackerrank.com/challenges/22727/problem

def is_leap(year):
    leap = False
    
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                leap = True 
        else:
            leap = True
        
    return leap


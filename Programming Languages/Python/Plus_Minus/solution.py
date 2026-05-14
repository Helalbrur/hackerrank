# Plus Minus
# Difficulty : Easy
# Track      : Warmup
# Tags       : 
# Solved on  : 2026-05-14
# Attempt    : #1
# HackerRank : https://www.hackerrank.com/challenges/8654/problem

#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'plusMinus' function below.
#
# The function accepts INTEGER_ARRAY arr as parameter.
#

def plusMinus(arr):
    n = len(arr)
    pm = {'plus' : 0, 'minus':0,'zero':0}
    for x in arr:
        if x > 0:
            pm['plus']+=1
        elif x < 0:
            pm['minus']+=1
        else:
            pm['zero']+=1
            
    for key,value in pm.items():
        ratio = value / n
        print(f"{ratio:.6f}")

if __name__ == '__main__':
    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    plusMinus(arr)

# Python If-Else
# Difficulty : Easy
# Track      : Introduction
# Tags       : 
# Solved on  : 2026-05-14
# Attempt    : #1
# HackerRank : https://www.hackerrank.com/challenges/22447/problem

#!/bin/python3

import math
import os
import random
import re
import sys



if __name__ == '__main__':
    n = int(input().strip())
    if n%2 == 1:
        print("Weird")
    elif n > 20:
        print("Not Weird")
    elif n > 5:
        print("Weird")
    else:
        print("Not Weird")

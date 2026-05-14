// Day 21: Generics
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17174/problem


template <class T>
/**
*    Name: printArray
*    Print each element of the generic vector on a new line. Do not return anything.
*    @param A generic vector
**/

// Write your code here
    void printArray(vector<T> v){
        for(T a: v){
            cout<<a<<"\n";
        }
    }


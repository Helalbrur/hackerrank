// Day 14: Scope
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17167/problem



	// Add your code here

    Difference(vector<int> v){
        this->elements=v;
    }
    void computeDifference(){
        sort(elements.begin(),elements.end());
        maximumDifference=abs(elements[elements.size()-1]-elements[0]);
        
    }


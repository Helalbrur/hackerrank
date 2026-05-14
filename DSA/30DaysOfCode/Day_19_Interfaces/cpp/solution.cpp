// Day 19: Interfaces
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17172/problem


class Calculator : public AdvancedArithmetic {
public:
    int divisorSum(int n) {
        int root=sqrt(n);
        int sum=0;
        for(int i=1;i<=root;i++){
            if(n%i==0){
                sum+=i;
                if(n/i!=i){
                    sum+=n/i;
                }
            }
        }
        return sum;
        
    }
};


// Day 17: More Exceptions
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17170/problem



//Write your code here
class MyException : public exception {
   const char * what () const throw () {
      return "n and p should be non-negative";
   }
};
class Calculator{
    public:
        Calculator(){

        }
        int power(int n,int p){
            if(n<0 || p<0){
                throw MyException();
            } 
            int r=1;
            while(p){
                r=r*n;
                p--;
            }
            return r;
            
        }

};


// Day 10: Binary Numbers
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/19001/problem

#include <bits/stdc++.h>

using namespace std;



int main()
{
    int n;
    cin >> n;
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    int c=0;
    bool ok=true;
    int cnt=0;
    while(n){
        int t=n&1;
        if(ok==true ){
            if(t==1) c++;
           else {
               ok=false;
               c=0;

           }
        }else if(t){
            ok=true;
            c++;
        }
        cnt=max(cnt,c);
        n=n>>1;
    }
    cout<<cnt<<endl;
    return 0;
}

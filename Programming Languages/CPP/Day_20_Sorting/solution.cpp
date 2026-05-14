// Day 20: Sorting
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/19055/problem

#include <bits/stdc++.h>

using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for(int a_i = 0; a_i < n; a_i++){
    	cin >> a[a_i];
    }
    int sw=0;
    for(int i=0;i<n;i++){
        for(int j=0;j<n-1;j++){
            if(a[j]>a[j+1]){
                int temp=a[j];
                a[j]=a[j+1];
                a[j+1]=temp;
                sw++;
            }
        }
        if(sw==0){
            break;
        }
    }
    cout<<"Array is sorted in "<<sw<<" swaps.\n";
    cout<<"First Element: "<<a[0]<<"\n";
    cout<<"Last Element: "<<a[n-1]<<"\n";
    
    return 0;
}

// Day 18: Queues and Stacks
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17171/problem

#include <iostream>
#include <stack>
#include <queue>
using namespace std;

class Solution {
    public :
        Solution(){
            
        }
        stack<char> st;
        queue<char> q;
        void pushCharacter(char c){
            st.push(c);
        }
        void enqueueCharacter(char c){
            q.push(c);
        }
        char popCharacter(){

            char c=st.top();
            st.pop();
            return c;
        }
        char dequeueCharacter(){
            char c=q.front();
            q.pop();
            return c;
        }



};


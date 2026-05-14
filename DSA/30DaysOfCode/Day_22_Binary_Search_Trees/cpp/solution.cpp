// Day 22: Binary Search Trees
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17175/problem



		int getHeight(Node* root){
            if(root==NULL) return -1;
            return max(getHeight(root->left)+1,getHeight(root->right)+1);
            
        }
        


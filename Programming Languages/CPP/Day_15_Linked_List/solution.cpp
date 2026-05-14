// Day 15: Linked List
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17168/problem



      Node* insert(Node *head,int data)
      {
          Node *temp=new Node(data);
          if(head==NULL){
               
               head=temp;
          }else{
             Node *start=head; 
            while(start->next)
            {
                start=start->next;
            }
            start->next=temp;
          }
          return head;
      }


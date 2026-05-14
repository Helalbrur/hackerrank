// Print the Elements of a Linked List
// Difficulty : Easy
// Track      : Linked Lists
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/1082/problem



// Complete the printLinkedList function below.

/*
 * For your reference:
 *
 * SinglyLinkedListNode {
 *     int data;
 *     SinglyLinkedListNode* next;
 * };
 *
 */
void printLinkedList(SinglyLinkedListNode* head) {

    while(head)
    {
        cout<<head->data<<endl;
        head=head->next;
    }
}


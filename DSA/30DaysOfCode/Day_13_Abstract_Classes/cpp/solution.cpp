// Day 13: Abstract Classes
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17166/problem


class MyBook: public Book{
    public:
        int price;
        MyBook(string title,string author,int price):Book(title,author){
            this->price=price;
        }
        void display(){
            cout<<"Title: "<<this->title<<"\n";
            cout<<"Author: "<<this->author<<"\n";
            cout<<"Price: "<<this->price<<"\n";
        }
};
// Write your MyBook class here

    //   Class Constructor
    //   
    //   Parameters:
    //   title - The book's title.
    //   author - The book's author.
    //   price - The book's price.
    //
    // Write your constructor here
    
    
    //   Function Name: display
    //   Print the title, author, and price in the specified format.
    //
    // Write your method here
    
// End class


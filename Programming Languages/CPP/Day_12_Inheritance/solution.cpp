// Day 12: Inheritance
// Difficulty : Easy
// Track      : 30 Days of Code
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/17165/problem



class Student :  public Person{
	private:
		vector<int> testScores;  
	public:
            Student(string firstName,string lastName,int Id,vector<int>& scores):Person(firstName,lastName,Id){
                
                this->testScores=scores;
            }
        /*	
        *   Class Constructor
        *   
        *   Parameters:
        *   firstName - A string denoting the Person's first name.
        *   lastName - A string denoting the Person's last name.
        *   id - An integer denoting the Person's ID number.
        *   scores - An array of integers denoting the Person's test scores.
        */
        // Write your constructor here

        /*	
        *   Function Name: calculate
        *   Return: A character denoting the grade.
        */
        // Write your function here

        char calculate(){
            int total=0;
            int n=testScores.size();
            int avg=0;
            for(int a:testScores){
                total+=a;
            }
            char r;
            avg=total/n;
            if(avg>=90){
                r='O';
            }else if(avg>=80){
                r='E';
            }else if(avg>=70){
                r='A';
            }else if(avg>=55){
                r='P';
            }else if(avg>=40){
                r='D';
            }else{
                r='T';
            }
            return r;
        }
};


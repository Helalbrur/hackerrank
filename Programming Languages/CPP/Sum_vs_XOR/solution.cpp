// Sum vs XOR
// Difficulty : Easy
// Track      : Bit Manipulation
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/25113/problem

#include <bits/stdc++.h>

using namespace std;

string ltrim(const string &);
string rtrim(const string &);

// Complete the sumXor function below.
long sumXor(long n) {
   long cnt=0;
   while(n){
       cnt+= n & 1 ? 0 : 1;
       n=n>>1;
       
   }
   return pow(2,cnt);
    
}

int main()
{
    ofstream fout(getenv("OUTPUT_PATH"));

    string n_temp;
    getline(cin, n_temp);

    long n = stol(ltrim(rtrim(n_temp)));

    long result = sumXor(n);

    fout << result << "\n";

    fout.close();

    return 0;
}

string ltrim(const string &str) {
    string s(str);

    s.erase(
        s.begin(),
        find_if(s.begin(), s.end(), not1(ptr_fun<int, int>(isspace)))
    );

    return s;
}

string rtrim(const string &str) {
    string s(str);

    s.erase(
        find_if(s.rbegin(), s.rend(), not1(ptr_fun<int, int>(isspace))).base(),
        s.end()
    );

    return s;
}

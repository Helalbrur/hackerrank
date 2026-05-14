// Recursive Digit Sum
// Difficulty : Medium
// Track      : Recursion
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/35933/problem

#include <bits/stdc++.h>
#include <iterator>

using namespace std;

vector<string> split_string(string);

// Complete the superDigit function below.
int superDigit(string n, int k) {
    if(n.length()==1 && k==1) return n[0]-'0';
    int64_t sum=0;
    string a;
    for(long int i=0;i<n.length();i++){
        sum+=n[i]-'0';
    }
    sum*=k;
    if(sum<10){
        return sum;
    }
    while(sum){
        a+=sum%10+'0';
        sum=sum/10;
    }
    reverse(a.begin(),a.end());
    return superDigit(a, 1);
            
}


int main()
{
    ofstream fout(getenv("OUTPUT_PATH"));

    string nk_temp;
    getline(cin, nk_temp);

    vector<string> nk = split_string(nk_temp);

    string n = nk[0];

    int k = stoi(nk[1]);

    int result = superDigit(n, k);

    fout << result << "\n";

    fout.close();

    return 0;
}

vector<string> split_string(string input_string) {
    string::iterator new_end = unique(input_string.begin(), input_string.end(), [] (const char &x, const char &y) {
        return x == y and x == ' ';
    });

    input_string.erase(new_end, input_string.end());

    while (input_string[input_string.length() - 1] == ' ') {
        input_string.pop_back();
    }

    vector<string> splits;
    char delimiter = ' ';

    size_t i = 0;
    size_t pos = input_string.find(delimiter);

    while (pos != string::npos) {
        splits.push_back(input_string.substr(i, pos - i));

        i = pos + 1;
        pos = input_string.find(delimiter, i);
    }

    splits.push_back(input_string.substr(i, min(pos, input_string.length()) - i + 1));

    return splits;
}

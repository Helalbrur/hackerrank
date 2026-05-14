// Plus Minus
// Difficulty : Easy
// Track      : Warmup
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/8654/problem

'use strict';

process.stdin.resume();
process.stdin.setEncoding('utf-8');

let inputString = '';
let currentLine = 0;

process.stdin.on('data', function(inputStdin) {
    inputString += inputStdin;
});

process.stdin.on('end', function() {
    inputString = inputString.split('\n');

    main();
});

function readLine() {
    return inputString[currentLine++];
}

/*
 * Complete the 'plusMinus' function below.
 *
 * The function accepts INTEGER_ARRAY arr as parameter.
 */

function plusMinus(arr) {
    var pm = {'plus':0,'minus':0,'zero':0};
    arr.forEach((n)=>{
        if (n > 0){
            pm['plus']++;
        }
        else if(n < 0){
            pm['minus']++;
        }
        else{
            pm['zero']++;
        }
    });
    const n = arr.length;
    for(const [key,value] of Object.entries(pm)){
        const ratio = value / n;
        console.log(ratio.toFixed(6));
    }
}

function main() {
    const n = parseInt(readLine().trim(), 10);

    const arr = readLine().replace(/\s+$/g, '').split(' ').map(arrTemp => parseInt(arrTemp, 10));

    plusMinus(arr);
}

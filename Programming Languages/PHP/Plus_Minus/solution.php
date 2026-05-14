// Plus Minus
// Difficulty : Easy
// Track      : Warmup
// Tags       : 
// Solved on  : 2026-05-14
// Attempt    : #1
// HackerRank : https://www.hackerrank.com/challenges/8654/problem

<?php

/*
 * Complete the 'plusMinus' function below.
 *
 * The function accepts INTEGER_ARRAY arr as parameter.
 */

function plusMinus($arr) {
    $pm = [
        'plus'=>0,
        'minus'=>0,
        'zero'=>0
    ];
    $cnt = 0;
    foreach($arr as $n){
        if ( $n > 0){
            $pm['plus']++;
        }
        else if($n < 0){
            $pm['minus']++;
        }
        else{
            $pm['zero']++;
        }
        $cnt++;
    }
    
    //var_dump($pm);
    foreach($pm as $key=>$val){
        echo number_format($val/$cnt,6)."\n";
    }
}

$n = intval(trim(fgets(STDIN)));

$arr_temp = rtrim(fgets(STDIN));

$arr = array_map('intval', preg_split('/ /', $arr_temp, -1, PREG_SPLIT_NO_EMPTY));

plusMinus($arr);

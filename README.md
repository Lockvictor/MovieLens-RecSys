# MovieLens-RecSys
UserBasedCF and ItemBasedCF tested on MovieLens 1M dataset.<br>
基于Movielens-1M数据集实现的UserBasedCF和ItemBasedCF推荐算法

## Introduction
Implementation of UserCF and ItemCF algorithm.<br>
The programs are tested on Movielens 1M dataset. You can download this dataset by this link [ml-1m.zip](http://files.grouplens.org/datasets/movielens/ml-1m.zip).<br>
The recommendation result is evaluated by Precision, Recall, Coverage and Popularity.

## How to run
1. Put the "ml-1m" folder in the directory MovieLens-RecSys.
2. Simply run command:
```shell
python usercf.py
```
if you are in Linux, the following command is preferred:
```shell
python usercf.py > run.log 2>&1 &
```
This command will let the program run in back stage and run.log will record all outputs of the program.

## Attention
In UserBasedCF,the program will generate a big matrix which comsumes a lot of memories (about 2.2GB in my computer). So make sure that your computer have enough memories to run the program.
ItemBasedCF doesn't have the problem of memories, but the evaluation process is very slow. I haven't found out the reason for now...

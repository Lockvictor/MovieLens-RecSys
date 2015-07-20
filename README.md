# MovieLens-RecSys
Recommender System algorithm based on MovieLens 1M dataset
基于Movielens-1M数据集实现的UserCF和ItemCF推荐算法

### Introduction
Realisation of basic UserCF and ItemCF algorithm.
The programs are tested on Movielens 1M dataset. You can download this dataset by this link [ml-1m.zip](http://files.grouplens.org/datasets/movielens/ml-1m.zip).
The result is evaluated by Precision, Recall, Coverage and Popularity.

### How to run
1. Put the "ml-1m" folder in the directory MovieLens-RecSys.
2. Simply run command:
```shell
python usercf.py
```
or if you are in Linux:
```shell
python usercf.py > run.log 2>&1 &
```
This command will allow the program to run in back stage and run.log will record all outputs of the program.

### Attention
The program will generate a big matrix which comsume a lot of memeries (about 2.2GB for UserCF in my computer). So make sure that your computer have enough memeries to run the program.
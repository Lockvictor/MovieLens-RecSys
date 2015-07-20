#-*- coding: utf-8 -*-
'''
Created on 2015-06-22

@author: Lockvictor
'''
import sys, random, math, operator

random.seed(0)

class UserCF():
    ''' UserCF TopN recommendation '''
    def __init__(self):
        self.trainset = {}
        self.testset = {}

        self.simUserNum = 20
        self.recMovieNum = 10

        self.userSimMatrix = {}
        self.moviePopularity = {}
        self.allMovieCount = 0

        print >> sys.stderr, 'Similar user number = %d' % self.simUserNum
        print >> sys.stderr, 'Recommended movie number = %d' % self.recMovieNum

    @staticmethod
    def _LoadFile(filename):
        ''' load a file, return a generator. '''
        fp = open(filename, 'r')
        for i,line in enumerate(fp):
            yield line.strip('\r\n')
            if i%100000 == 0:
                print >> sys.stderr, 'loading %s(%s)' % (filename, i)
        fp.close()
        print >> sys.stderr, 'load %s succ' % filename

    def GenerateTrainTestSet(self, filename, pivot=0.7):
        ''' load rating data and split it to training set and test set '''
        trainset_len = 0
        testset_len = 0
        for line in self._LoadFile(filename):
            user, movie, rating, timestamp = line.split('::')
            # split the data by pivot
            if (random.random() < pivot):
                self.trainset.setdefault(user,{})
                self.trainset[user][movie] = int(rating)
                trainset_len += 1
            else:
                self.testset.setdefault(user,{})
                self.testset[user][movie] = int(rating)
                testset_len += 1
        print >> sys.stderr, 'split training set and test set succ'
        print >> sys.stderr, 'train set = %s' % trainset_len
        print >> sys.stderr, 'test set = %s' % testset_len

    def CalUserSimilarity(self):
        ''' calculate user similarity matrix '''
        # build inverse table for item-users
        # key=movieID, value=list of userIDs who have seen this movie
        print >> sys.stderr, 'building movie-users inverse table...'
        movie2users = dict()
        for user,movies in self.trainset.iteritems():
            for movie in movies:
                # inverse table for item-users
                if movie not in movie2users:
                    movie2users[movie] = set()
                movie2users[movie].add(user)
                # count item popularity at the same time
                if movie not in self.moviePopularity:
                    self.moviePopularity[movie] = 0
                self.moviePopularity[movie] += 1
        print >> sys.stderr, 'build movie-users inverse table succ'

        # save the total movie number, which will be used in evaluation
        self.allMovieCount = len(movie2users)
        print >> sys.stderr, 'total movie number = %d' % self.allMovieCount

        usersim_mat = self.userSimMatrix
        # count co-rated items between users
        print >> sys.stderr, 'building user co-rated movies matrix...'
        for movie,users in movie2users.iteritems():
            for u in users:
                for v in users:
                    if u == v: continue
                    usersim_mat.setdefault(u,{})
                    usersim_mat[u].setdefault(v,0)
                    usersim_mat[u][v] += 1
        print >> sys.stderr, 'build user co-rated movies matrix succ'

        # calculate similarity matrix 
        print >> sys.stderr, 'calculating user similarity matrix...'
        simfactor_count = 0
        PRINT_STEP = 2000000
        for u,related_users in usersim_mat.iteritems():
            for v,count in related_users.iteritems():
                usersim_mat[u][v] = count / math.sqrt(len(self.trainset[u])*len(self.trainset[v]))
                simfactor_count += 1
                if simfactor_count % PRINT_STEP == 0:
                    print >> sys.stderr, 'calculating user similarity factor(%d)' % simfactor_count
        print >> sys.stderr, 'calculate user similarity matrix(similarity factor) succ'
        print >> sys.stderr, 'Total similarity factor number = %d' %simfactor_count

    def Recommend(self, user):
        ''' Find K similar users and recommend N movies. '''
        K = self.simUserNum
        N = self.recMovieNum
        rank = dict()
        watched_movies = self.trainset[user]

        # v=similar user, wuv=similarity factor
        for v, wuv in sorted(self.userSimMatrix[user].items(), key = operator.itemgetter(1), reverse=True)[0:K]:
            for movie in self.trainset[v]:
                if movie in watched_movies:
                    continue
                # predict the user's "interest" for each movie
                rank.setdefault(movie,0)
                rank[movie] += wuv
        # return the N best movies
        return sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]

    def Evaluate(self):
        ''' return precision, recall, coverage and popularity '''
        print >> sys.stderr, 'Evaluation start...'
        N = self.recMovieNum
        #  varables for precision and recall 
        hit = 0
        rec_count = 0
        test_count = 0
        # varables for coverage
        all_rec_movies = set() 
        # varables for popularity
        popular_sum = 0

        for user in self.trainset:
            test_movies = self.testset.get(user, {})
            rec_movies = self.Recommend(user)
            for movie, interest_factor in rec_movies:
                if movie in test_movies:
                    hit += 1
                all_rec_movies.add(movie)
                popular_sum += math.log(1 + self.moviePopularity[movie])
            rec_count += N
            test_count += len(test_movies)

        precision = hit / (1.0*rec_count)
        recall = hit / (1.0*test_count)
        coverage = len(all_rec_movies) / (1.0*self.allMovieCount)
        popularity = popular_sum / (1.0*rec_count)
        print >> sys.stderr, 'precision=%.4f\trecall=%.4f\tcoverage=%.4f\tpopularity=%.4f' % (precision, recall, coverage, popularity)

if __name__ == '__main__':
    ratingfile = 'ml-1m/ratings.dat'
    usercf = UserCF()
    usercf.GenerateTrainTestSet(ratingfile)
    usercf.CalUserSimilarity()
    usercf.Evaluate()

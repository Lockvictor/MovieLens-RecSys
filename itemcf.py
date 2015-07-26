#-*- coding: utf-8 -*-
'''
Created on 2015-06-22

@author: Lockvictor
'''
import sys, random, math, operator

random.seed(0)

class ItemBasedCF():
    ''' TopN recommendation - ItemBasedCF '''
    def __init__(self):
        self.trainset = {}
        self.testset = {}

        self.simMovieNum = 20
        self.recMovieNum = 10

        self.movieSimMatrix = {}
        self.moviePopularity = {}
        self.allMovieCount = 0

        print >> sys.stderr, 'Similar movie number = %d' % self.simMovieNum
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

    def CalMovieSimilarity(self):
        ''' calculate user similarity matrix '''
        print >> sys.stderr, 'counting movies number and popularity...'
        for user,movies in self.trainset.iteritems():
            for movie in movies:
                # count item popularity 
                if movie not in self.moviePopularity:
                    self.moviePopularity[movie] = 0
                self.moviePopularity[movie] += 1
        print >> sys.stderr, 'count movies number and popularity succ'

        # save the total number of movies
        self.allMovieCount = len(self.moviePopularity)
        print >> sys.stderr, 'total movie number = %d' % self.allMovieCount

        itemsim_mat = self.movieSimMatrix
        # count co-rated users between items
        print >> sys.stderr, 'building co-rated users matrix...'
        for user,movies in self.trainset.iteritems():
            for m1 in movies:
                for m2 in movies:
                    if m1 == m2: continue
                    itemsim_mat.setdefault(m1,{})
                    itemsim_mat[m1].setdefault(m2,0)
                    itemsim_mat[m1][m2] += 1
        print >> sys.stderr, 'build co-rated users matrix succ'

        # calculate similarity matrix 
        print >> sys.stderr, 'calculating movie similarity matrix...'
        simfactor_count = 0
        PRINT_STEP = 2000000
        for m1,related_movies in itemsim_mat.iteritems():
            for m2,count in related_movies.iteritems():
                itemsim_mat[m1][m2] = count / math.sqrt(self.moviePopularity[m1]*self.moviePopularity[m2])
                simfactor_count += 1
                if simfactor_count % PRINT_STEP == 0:
                    print >> sys.stderr, 'calculating movie similarity factor(%d)' % simfactor_count
        print >> sys.stderr, 'calculate movie similarity matrix(similarity factor) succ'
        print >> sys.stderr, 'Total similarity factor number = %d' %simfactor_count

    def Recommend(self, user):
        ''' Find K similar movies and recommend N movies. '''
        K = self.simMovieNum
        N = self.recMovieNum
        rank = dict()
        watched_movies = self.trainset[user]

        for movie in watched_movies:
            for related_movie,w in sorted(self.movieSimMatrix[movie].items(), key=operator.itemgetter(1), reverse=True)[0:K]:
                if related_movie in watched_movies:
                    continue
                rank.setdefault(related_movie,0)
                rank[related_movie] += w
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

        i = 0
        for user in self.trainset:
            i += 1
            if i % 500 == 0:
                print >> sys.stderr, 'recommended for %s users' % i
            test_movies = self.testset.get(user, {})
            rec_movies = self.Recommend(user)
            for movie,w in rec_movies:
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
    itemcf = ItemBasedCF()
    itemcf.GenerateTrainTestSet(ratingfile)
    itemcf.CalMovieSimilarity()
    itemcf.Evaluate()

import sys
from collections import defaultdict
import re
import random
import math


def train_bigram(phonDict, k = 0):
    #loops through data and stores all counts
    #totalCounts stores counts of all phonemes, biCounts stores counts of all bigrams
    trainf = open(phonDict)
    totalCounts = defaultdict(lambda: 0)
    biCounts = defaultdict(lambda: defaultdict(lambda: 0))
    for line in trainf:
        #split each line into separate phonemes, get rid of the first token which is not a phoneme,
        #  and add '#' as first and last elements
        line = line.strip() + " #"
        phons = re.split(' ', line)
        phons[0] = "#"
        for i in range(len(phons)-1):
            totalCounts[phons[i]] += 1
            biCounts[phons[i]][phons[i+1]] += 1
    trainf.close()

    #biGram stores the relative frequency of each bigram
    #computes relative frequency estimates by looping through all possible bigrams
    #if k=1, then there is Laplace smoothing
    biGram = defaultdict(lambda: {})
    for phon1 in totalCounts:
        for phon2 in totalCounts:
            biGram[phon1][phon2] = float(biCounts[phon1][phon2] + k)/(totalCounts[phon1] + k*len(totalCounts))
    
    return biGram


def train_trigram(phonDict, k = 0):
    #loops through data and stores all counts
    #totalCounts stores counts of all phonemes, biCounts stores counts of all bigrams,
    #  and triCounts stores counts of all trigrams
    trainf = open(phonDict)
    totalCounts = defaultdict(lambda: 0)
    biCounts = defaultdict(lambda: 0)
    triCounts = defaultdict(lambda: defaultdict(lambda: 0))
    for line in trainf:
        #split each line into separate phonemes, get rid of the first token which is not a phoneme,
        #  and add '#' as the first two and the last elements
        line = line.strip() + " #"
        phons = re.split(' ', line)
        phons[0] = "#"
        phons.insert(0, "#")
        for i in range(len(phons)-2):
            totalCounts[phons[i]] += 1
            bigram = (phons[i], phons[i+1])
            biCounts[bigram] += 1
            triCounts[bigram][phons[i+2]] += 1
    trainf.close()

    #triGram stores the relative frequency of each trigram
    #computes relative frequency estimates by looping through all possible trigrams
    #if k=1, then there is Laplace smoothing
    triGram = defaultdict(lambda: {})
    for phon1 in totalCounts:
        for phon2 in totalCounts:
            for phon3 in totalCounts:
                if float(triCounts[(phon1, phon2)][phon3] + k) == 0.0:
                    triGram[(phon1, phon2)][phon3] = 0.0
                else:
                    triGram[(phon1, phon2)][phon3] = float(triCounts[(phon1, phon2)][phon3] + k)/(biCounts[(phon1, phon2)] + k*(len(totalCounts)^2))

    return triGram

    
def make_bigrams(phonDict):
    #get parameters
    biGram = train_bigram(phonDict)
    
    #print 25 random 'words'
    #for each phoneme (current), generate a random float, go through all possible following phonemes,
    #  subtract the probability of each bigram from the random float, and when it goes
    #  below zero that phoneme is selected as the next one (is added to word and becomes current)
    #when a '#' is selected, the full word is printed
    for i in range(25):
        word = "#"
        current = ""
        while current is not "#":
            rand = random.uniform(0,1)
            if current == "":
                current = "#"
            for each in biGram[current]:
                rand -= biGram[current][each]
                if rand < 0.0:
                    current = each
                    break
            word += " " + current
        print word


def make_trigrams(phonDict):
    #get parameters
    triGram = train_trigram(phonDict)
    
    #print 25 random 'words'
    #for each bigram (current), generate a random float, go through all possible following phonemes,
    #  subtract the probability of each trigram from the random float, and when it goes
    #  below zero that phoneme is selected as the next one (is added to word and becomes current[1])
    #when a '#' is selected, the full word is printed
    for i in range(25):
        word = "# #"
        current = ("", "")
        while current[1] is not "#":
            rand = random.uniform(0,1)
            if current[1] == "":
                current = ("#", "#")
            for each in triGram[current]:
                rand -= triGram[current][each]
                if rand < 0.0:
                    current = (current[1], each)
                    break
            word += " " + current[1]
        print word


def smooth_bi(phonDict, test):
    #get smoothed model
    biGram = train_bigram(phonDict, 1)

    #for each word, print word and probability
    #to find probability, each word is split into separate phonemes with '#' added as first and
    #  last elements, and the probability of each bigram consisting of the phoneme before + current
    #  is transformed into a log probability and added together
    #log_sum is the sum of all log probabilities, N is number of phonemes plus number of words
    testf = open(test)
    log_sum = 0.0
    N = 0
    for word in testf:
        word = word.strip()
        sentence = word + "\t"
        word = "# " + word + " #"
        phons = re.split(' ', word)
        N += len(phons) - 1
        probability = 0.0
        for i in range(1, len(phons)):
            probability += math.log(biGram[phons[i-1]][phons[i]], 2)
        log_sum += probability
        sentence += str(2**(probability))
        print sentence
    testf.close()

    #print perplexity
    perplexity = 2**(log_sum*(float(-1)/N))
    print "The perplexity of " + test + " is " + str(perplexity)


def smooth_tri(phonDict, test):
    #get smoothed model
    triGram = train_trigram(phonDict, 1)

    #for each word, print word and probability
    #to find probability, each word is split into separate phonemes with '#' added as the two first and
    #  the last elements, and the probability of each trigram consisting of the bigram before + current
    #  is transformed into a log probability and added together
    #log_sum is the sum of all log probabilities, N is number of phonemes plus number of words
    testf = open(test)
    log_sum = 0.0
    N = 0
    for word in testf:
        word = word.strip()
        sentence = word + "\t"
        word = "# # " + word + " #"
        phons = re.split(' ', word)
        N += len(phons) - 2
        probability = 0.0
        for i in range(2, len(phons)):
            probability += math.log(triGram[(phons[i-2], phons[i-1])][phons[i]], 2)
        log_sum += probability
        sentence += str(2**(probability))
        print sentence
    testf.close()

    #print perplexity
    perplexity = 2**(log_sum*(float(-1)/N))
    print "The perplexity of " + test + " is " + str(perplexity)


def main():
    phonDict = sys.argv[1]
    N = sys.argv[2]
    #if there is a third argument, build a smoothed model and find perplexity
    #if not, build a default model and print 25 random words
    if (len(sys.argv) == 4):
        test = sys.argv[3]
        if (N == '2'):
            smooth_bi(phonDict, test)
        else:
            smooth_tri(phonDict, test)
    elif (N == '2'):
        make_bigrams(phonDict)
    else:
        make_trigrams(phonDict)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy as sp
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA

#sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join(r'C:\Users\msingleton\Documents\GitHub\XCS224N-A1')))
from utils.sanity_checks import *

def distinctWords(corpus):
    """ Determine a list of distinct words for the corpus.
        Params:
            corpus (list of list of strings): corpus of documents
        Return:
            corpus_words (list of strings): list of distinct words across the corpus, sorted (using python 'sorted' function)
            num_corpus_words (integer): number of distinct words across the corpus
    """
    corpus_words = []
    num_corpus_words = -1

    ### SOLUTION BEGIN
    
    # Merge the lists of strings into a single list
    concat_list = [j for i in corpus for j in i]
      
    # Stuff the merged list into a set to unduplicate the words; convert de-duped set back to a sorted list
    corpus_words = sorted(list(set(concat_list)))
   
    # Count distinct words in de-duped list
    num_corpus_words = len(corpus_words)       
    
    ### SOLUTION END

    return corpus_words, num_corpus_words


def computeCoOccurrenceMatrix(corpus, window_size=4):
    """ Compute co-occurrence matrix for the given corpus and window_size (default of 4).
    
        Note: Each word in a document should be at the center of a window. Words near edges will have a smaller
              number of co-occurring words.
              
              For example, if we take the document "START All that glitters is not gold END" with window size of 4,
              "All" will co-occur with "START", "that", "glitters", "is", and "not".
    
        Params:
            corpus (list of list of strings): corpus of documents
            window_size (int): size of context window
        Return:
            M (numpy matrix of shape (number of unique words in the corpus , number of unique words in the corpus)):
                Co-occurence matrix of word counts. 
                The ordering of the words in the rows/columns should be the same as the ordering of the words given by the distinct_words function.
            word2Ind (dict): dictionary that maps word to index (i.e. row/column number) for matrix M.
    """
    words, num_words = distinctWords(corpus)
    #M = None
    #word2Ind = {}

    ### SOLUTION BEGIN
    
    M = np.zeros((num_words,num_words), dtype=np.int8)
    word_idx = list(range(0,num_words))
    word2Ind = {k:v for k,v in zip(words,word_idx)} # Dict to link words with their row/col in M
    
    #[getContextWordCounts(doc, cw_idx, window_size) for doc in corpus for cw_idx in range(len(doc))]
    for doc in corpus:
        for cw_idx in range(len(doc)):
            # Initialize word counts row vector (v)
            v = np.zeros(shape=num_words, dtype=np.int8)
            
            # List (window) of words around the center word
            left = max(cw_idx-window_size,0)
            #right = min(num_words,cw_idx+window_size)
            right = min(len(doc),cw_idx+window_size)
            window = doc[left:right+1]
                         
            # Unique words in the window
            window_unique = list(set(window))
            
            for w in window_unique:
                v_idx = word2Ind[w]
                M_idx = word2Ind[doc[cw_idx]]
                if w == doc[cw_idx]:     # Don't count the center word itself
                    word_freq = window.count(w) - 1 
                else: 
                    word_freq = window.count(w) # times w appears in window
                v[v_idx] = word_freq
            
            # Update row of M corr to w with word counts in v
            M[M_idx] = M[M_idx] + v
            print(doc[cw_idx], M_idx, v, left, right, window)
    
    ### SOLUTION END

    return M, word2Ind

def reduceToKDim(M, k=2):
    """ Reduce a co-occurence count matrix of dimensionality (num_corpus_words, num_corpus_words)
        to a matrix of dimensionality (num_corpus_words, k) using the following SVD function from Scikit-Learn:
            - http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html
    
        Params:
            M (numpy matrix of shape (number of unique words in the corpus , number of number of corpus words)): co-occurence matrix of word counts
            k (int): embedding size of each word after dimension reduction
        Return:
            M_reduced (numpy matrix of shape (number of corpus words, k)): matrix of k-dimensioal word embeddings.
                    In terms of the SVD from math class, this actually returns U * S
    """
    np.random.seed(4355)
    n_iters = 10  # Use this parameter in your call to `TruncatedSVD`
    M_reduced = None
    print("Running Truncated SVD over %i words..." % (M.shape[0]))

    ### SOLUTION BEGIN
    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=k, n_iter=n_iters)
    M_reduced = svd.fit_transform(M)  
    ### SOLUTION END

    print("Done.")
    return M_reduced


#############################################
# Testing functions below. DO NOT MODIFY!   #
#############################################

def test_distinctWords():
    print("\n\t\t\t Testing distinctWords \t\t\t")

    test_corpus = toyCorpus()
    test_corpus_words, num_corpus_words = distinctWords(test_corpus)

    ans_test_corpus_words = sorted(
        list(set(["START", "All", "ends", "that", "gold", "All's", "glitters", "isn't", "well", "END"])))
    ans_num_corpus_words = len(ans_test_corpus_words)

    print("\nYour Result:")
    print(
        "Words in corpus: {}\n Number of words in corpus: {}\n".format(test_corpus_words,
                                                                       num_corpus_words
                                                                       )
    )

    print("Expected Result:")
    print(
        "Words in corpus: {}\n Number of words in corpus: {}\n".format(ans_test_corpus_words,
                                                                       ans_num_corpus_words
                                                                       )
    )


def test_computeCoOccurenceMatrix():
    print("\n\t\t\t Testing computeCoOccurrenceMatrix \t\t\t")

    test_corpus = toyCorpus()
    M_test, word2Ind_test = computeCoOccurrenceMatrix(test_corpus, window_size=2)

    M_test_ans, word2Ind_test_ans = toyCorpusCoOccurence()

    for w1 in word2Ind_test_ans.keys():
        idx1 = word2Ind_test_ans[w1]
        for w2 in word2Ind_test_ans.keys():
            idx2 = word2Ind_test_ans[w2]
            student = M_test[idx1, idx2]
            correct = M_test_ans[idx1, idx2]
            if student != correct:
                print("Correct M:")
                print(M_test_ans)
                print("Your M: ")
                print(M_test)
                raise AssertionError(
                    "Incorrect count at index ({}, {})=({}, {}) in matrix M. Yours has {} but should have {}.".format(
                        idx1, idx2, w1, w2, student, correct))

    print("\nYour Result:")
    print(
        "Shape of co-occurence matrix: {}\n Word to index map: {}\n".format(M_test.shape,
                                                                            word2Ind_test
                                                                            )
    )

    print("\nExpected Result:")
    print(
        "Shape of co-occurence matrix: {}\n Word to index map: {}\n".format(M_test_ans.shape,
                                                                            word2Ind_test_ans
                                                                            )
    )


def test_reduceToKDim():
    print("\n\t\t\t Testing reduceToKDim \t\t\t")

    M_test_ans, word2Ind_test_ans = toyCorpusCoOccurence()
    M_test_reduced = reduceToKDim(M_test_ans, k=2)

    print("\nYour Result:")
    print(
        "Shape of reduced dim co-occurence matrix: {}\n".format(M_test_reduced.shape
                                                                )
    )

    print("\nExpected Result:")
    print(
        "Shape of reduced dim co-occurence matrix: {}\n".format((10, 2)
                                                                )
    )


if __name__ == "__main__":
    test_distinctWords()
    test_computeCoOccurenceMatrix()
    test_reduceToKDim()

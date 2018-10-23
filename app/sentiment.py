# -*- coding: UTF-8 -*-

from collections import defaultdict
import os
import re
import codecs
import sys

import jieba
import chardet

class SentimentAnalyzer:
    stopwords = []
    notwords = []
    sentiment_score_dict = defaultdict()
    degree_dict = defaultdict()


    def __init__(self, stopwords_path, notwords_path, sen_sore_path, degree_path):
        with open(stopwords_path, 'r') as f:
            for line in f.readlines():
                line = line.strip('\n')
                self.stopwords.append(line)

        with open(notwords_path, 'r') as f:
            for line in f.readlines():
                line = line.strip('\n')
                self.notwords.append(line)

        with open(sen_sore_path, 'r') as f:
            for line in f.readlines():
                line = line.strip('\n')
                senscore = line.split(' ')
                self.sentiment_score_dict[senscore[0]] = senscore[1]

        with open(degree_path, 'r') as f:
            for line in f.readlines():
                line = line.strip('\n')
                degree = line.split(' ')
                self.degree_dict[degree[0]] = degree[1]


    def _list_to_dict(self, wordlist):
        data = {}
        
        for idx in range(0, len(wordlist)):
            data[wordlist[idx]] = idx
        
        return data


    def _cut_sentence(self, sentence):
        seg_list = jieba.cut(sentence)
        result = []
        for word in seg_list:
            if word in self.stopwords:
                continue
            else:
                result.append(word)
        
        return self._list_to_dict(result)


    def _classify_words(self, words):
        sen_words = defaultdict()
        not_words = defaultdict()
        degree_words = defaultdict()
        for word in words.keys():
            if word in self.sentiment_score_dict.keys() and word not in self.notwords and word not in self.degree_dict.keys():
                sen_words[words[word]] = self.sentiment_score_dict[word]
            elif word in self.notwords and word not in self.degree_dict.keys():
                not_words[words[word]] = -1
            elif word in self.degree_dict.keys():
                degree_words[words[word]] = self.degree_dict[word]
        
        return sen_words, not_words, degree_words


    def _evaluate_sentence(self, sen_words, not_words, degree_words, word_list):
        weight = 1
        score = 0

        sen_idx = -1
        sen_idx_list = list(sen_words.keys())

        for i in range(0, len(word_list)):
            if i in sen_words.keys():
                score += weight * float(sen_words[i])
                sen_idx += 1
            
            if sen_idx < len(sen_idx_list) - 1:
                for j in range(sen_idx_list[sen_idx], sen_idx_list[sen_idx + 1]):
                    if j in not_words.keys():
                        weight *= -1
                    elif j in degree_words.keys():
                        weight *= float(degree_words[j])

            if sen_idx < len(sen_idx_list) - 1:
                i = sen_idx_list[sen_idx + 1]
        
        return score


    def calcuate_score(self, sentence):
        word_dict = self._cut_sentence(sentence)
        sen_words, not_words, degree_words = self._classify_words(word_dict)
        score = self._evaluate_sentence(sen_words, not_words, degree_words, word_dict.keys())

        return score


if __name__ == '__main__':
    analyzer = SentimentAnalyzer('../data_set/stopwords.txt', '../data_set/notdict.txt',
        '../data_set/BosonNLP_sentiment_score.txt', '../data_set/degreedict.txt')
    print(analyzer.calcuate_score("你好，世界"))

"""Small statistical benchmark: class-balanced multinomial naive Bayes.

Unigram/bigram capped counts; fit on train only. Scores are not calibrated legal
confidence. Kept in the research pipeline, not the interactive review tool.
"""
import math
import re
from collections import Counter

def tokens(text):
    words=re.findall(r"[a-z]+",text.lower())
    return Counter(words+[a+'_'+b for a,b in zip(words,words[1:])])

class NaiveBayes:
    def __init__(self, alpha=1.0):
        self.alpha=alpha

    def fit(self, texts, labels):
        self.counts=[Counter(),Counter()]
        self.docs=Counter(labels)
        for text,label in zip(texts,labels):
            self.counts[label].update({t:min(n,3) for t,n in tokens(text).items()})
        self.vocabulary=set(self.counts[0])|set(self.counts[1])
        v=len(self.vocabulary)
        self.weights={}
        totals=[sum(c.values())+self.alpha*v for c in self.counts]
        for token in self.vocabulary:
            self.weights[token]=math.log((self.counts[1][token]+self.alpha)/totals[1])-math.log((self.counts[0][token]+self.alpha)/totals[0])
        return self

    def score(self,text):
        # Equal class priors to resist majority-only predictions.
        return sum(min(n,3)*self.weights.get(t,0.0) for t,n in tokens(text).items())

    def predict(self,text):
        return int(self.score(text)>=0)

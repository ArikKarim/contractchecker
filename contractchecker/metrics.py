"""Explicit binary metrics and uncertainty; contract is the resampling unit."""
import math
import random

def binary_metrics(truth,pred):
    tp=sum(y==1 and p==1 for y,p in zip(truth,pred))
    tn=sum(y==0 and p==0 for y,p in zip(truth,pred))
    fp=sum(y==0 and p==1 for y,p in zip(truth,pred))
    fn=sum(y==1 and p==0 for y,p in zip(truth,pred))
    def div(a,b):return a/b if b else 0.0
    f1pos=div(2*tp,2*tp+fp+fn)
    f1neg=div(2*tn,2*tn+fp+fn)
    return {'n':len(truth),'tp':tp,'tn':tn,'fp':fp,'fn':fn,
            'precision_yes':div(tp,tp+fp),'recall_yes':div(tp,tp+fn),
            'f1_yes':f1pos,'f1_no':f1neg,'macro_f1':(f1pos+f1neg)/2,
            'accuracy':div(tp+tn,len(truth)),
            'balanced_accuracy':(div(tp,tp+fn)+div(tn,tn+fp))/2}

def wilson(successes,n):
    z=1.959963984540054
    p=successes/n
    d=1+z*z/n
    c=(p+z*z/(2*n))/d
    e=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-e),min(1,c+e)]

def quantile(xs,p):
    xs=sorted(xs)
    i=(len(xs)-1)*p
    lo=int(i);hi=min(lo+1,len(xs)-1)
    return xs[lo]+(xs[hi]-xs[lo])*(i-lo)

def bootstrap(paired_contract_scores,repetitions=2000,seed=20261102):
    rng=random.Random(seed)
    n=len(paired_contract_scores)
    means=[sum(paired_contract_scores[rng.randrange(n)] for _ in range(n))/n for _ in range(repetitions)]
    return {'mean':sum(paired_contract_scores)/n,'percentile_95_ci':[quantile(means,.025),quantile(means,.975)],
            'replicates':repetitions,'seed':seed,'unit':'contract (four correlated task decisions)'}

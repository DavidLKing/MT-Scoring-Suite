#!/usr/bin/env python3
# meteor - *.jar.. / git / MT - Scoring - Suite / gold.txt.. / git / MT - Scoring - Suite / pred.txt -l en

import sys
import argparse
import pdb
import pickle as pkl
import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import corpus_bleu
import yaml
import subprocess

parser = argparse.ArgumentParser()
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-c', '--config', help='YaML config file', required=True)
requiredNamed.add_argument('-r', '--ref', help='Reference file', required=True)
requiredNamed.add_argument('-p', '--pred', help='Prediction file', required=True)
requiredNamed.add_argument('-o', '--output', help='Output file', required=True)
args = parser.parse_args()

with open(args.config) as f:
    config = yaml.safe_load(f)


class Score:
    def __init__(self):
        """
        I'm not sure if we should use arguments or a configuration file for this
        """
        self.args = args


    def load_file(self, _file):
        """
        I'm not really sure what the best data format for this is yet
        If these files get too long, this may get RAM intensive
        """
        return open(_file, 'r').readlines()

    def bleu_weights(self, maxn):
        weights = []
        for n in range(maxn):
            weights.append([0] * maxn)
        for n in range(maxn):
            weights[n][n] = 1
        return [tuple(x) for x in weights]

    def get_bleus(self, ref, pred, weights):
        scores = []
        for w in weights:
            scores.append(sentence_bleu([ref], pred, w))
        assert(len(scores) == len(weights))
        return scores

    def main(self, reffile, predfile, maxn):
        refs = s.load_file(reffile)
        preds = s.load_file(predfile)
        assert(len(refs) == len(preds)), "Reference and prediciton files must be of the same length"
        weight_tuples = self.bleu_weights(maxn)
        print("Getting coprus level scores")
        # Get everything
        corp_scores = [corpus_bleu(refs, preds, weights=w) for w in weight_tuples]
        # Meteor also has line by line results
        cmd = [
            "java",
            "-jar",
            config['METEOR'],
            reffile,
            predfile,
            "-l",
            "en"
        ]
        print("Starting meteor")
        meteor = subprocess.run(cmd, stdout=subprocess.PIPE)
        sent_scores = []
        for ref, pred in zip(refs, preds):
            scores = self.get_bleus(ref, pred, weight_tuples)
            sent_scores.append(scores)
        pdb.set_trace()




if __name__ == '__main__':
    s = Score()
    ref = s.args.ref
    pred = s.args.pred
    s.main(ref, pred, config['BLEU n-gram'])


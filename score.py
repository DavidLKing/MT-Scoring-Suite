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
requiredNamed.add_argument('-s', '--src', help='Source file', required=True)
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
        # Gross one-liner. I'm so sorry!
        self.ter2txt = lambda x: x.stdout.decode().split('\n')[4].replace("Total TER: ", "").split(' ')[0]


    def load_file(self, _file):
        """
        I'm not really sure what the best data format for this is yet
        If these files get too long, this may get RAM intensive
        """
        return open(_file, 'r').readlines()

    def prepTER(self, predfile, reffile):
        preds = open(predfile, 'r').readlines()
        refs = open(reffile, 'r').readlines()
        predTER = predfile + "TER"
        refTER = reffile + "TER"
        self.ter_write(predTER, preds)
        self.ter_write(refTER, refs)

    def ter_write(self, _file, lines):
        i = 0
        with open(_file, 'w') as f:
            for l in lines:
                l = l.strip()
                l += ' ('
                l += str(i)
                l += ')\n'
                i += 1
            f.write(l)

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

    def lineTER(self, pred, ref):
        p = open('temp.pred', 'w')
        r = open('temp.ref', 'w')
        predLine = pred.strip() + ' ' + "(1)"
        refLine = ref.strip() + ' ' + "(1)"
        p.write(predLine)
        r.write(refLine)
        p.close()
        r.close()
        tercmd = [
            'java',
            '-jar',
            config['TER'],
            '-h',
            "temp.pred",
            '-r',
            "temp.ref"
        ]
        ter_out = subprocess.run(tercmd, stdout=subprocess.PIPE)
        return self.ter2txt(ter_out)

    def get_met_sent(self, meteor):
        meteor = meteor.stdout.decode().split("\n")
        # List comprehension isn't working
        # test = [x.startswith("Segment") for x in meteor]
        scores = []
        for met in meteor:
            if met.startswith("Segment"):
                met = met.split("\t")[1]
                scores.append(met)
        return scores

    def get_met_corp(self, meteor):
        meteor = meteor.stdout.decode().split("\n")
        # List comprehension isn't working
        # test = [x.startswith("Segment") for x in meteor]
        return meteor[-2].split(' ')[-1]

    def main(self, srcfile, reffile, predfile, maxn, out):
        self.prepTER(predfile, reffile)
        srcs = s.load_file(srcfile)
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
            config['METLANG']
        ]
        print("Starting METEOR")
        meteor = subprocess.run(cmd, stdout=subprocess.PIPE)
        met_corp = self.get_met_corp(meteor)
        met_sent = self.get_met_sent(meteor)
        print("Starting TER")
        tercmd = [
            'java',
            '-jar',
            config['TER'],
            '-h',
            predfile + 'TER',
            '-r',
            reffile + 'TER'
        ]
        ter_corp = subprocess.run(tercmd, stdout=subprocess.PIPE)
        ter_corp = self.ter2txt(ter_corp)
        sent_scores = []
        ter_scores = []
        print("Getting individual TER and BLEU scores")
        for ref, pred in zip(refs, preds):
            scores = self.get_bleus(ref, pred, weight_tuples)
            sent_scores.append(scores)
            ter_out = self.lineTER(pred, ref)
            ter_scores.append(ter_out)
        # Sanity check:
        assert(len(ter_scores) == len(sent_scores))
        assert(len(met_sent) == len(sent_scores))
        header = [
            "Source",
            "Human",
            "Machine",
            "TER",
            "METEOR",
            "BLEU 1",
            "BLEU 2",
            "BLEU 3",
            "BLEU 4"
        ]
        outfile = open(out, 'w')
        outfile.write('\t'.join(header) + '\n')
        for src, ref, pred, ter, met, bleu in zip(srcs, refs, preds, ter_scores, met_sent, sent_scores):
            outline = [src, ref, pred, ter, met]
            # pdb.set_trace()
            outline += bleu
            # pdb.set_trace()
            outline = [str(x) for x in outline]
            # pdb.set_trace()
            outline = [x.strip() for x in outline]
            # pdb.set_trace()
            outline = '\t'.join(outline)
            # pdb.set_trace()
            outline += '\n'
            # pdb.set_trace()
            outfile.write(outline)
        outfile.write("\nCorpus level scores\n")
        outfile.write('\t'.join([
            "TER", "METEOR", "BLEU 1",
            "BLEU 2", "BLEU 3", "BLEU 4\n"
        ]))
        outgroup = [ter_corp, met_corp] + [str(x) for x in corp_scores]
        outgroup = '\t'.join(outgroup)
        outfile.write(outgroup)



if __name__ == '__main__':
    s = Score()
    src = s.args.src
    ref = s.args.ref
    pred = s.args.pred
    out = s.args.output
    s.main(src, ref, pred, config['BLEU n-gram'], out)


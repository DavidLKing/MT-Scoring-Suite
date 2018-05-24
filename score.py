#!/usr/bin/env python3

import sys
import argparse
import pdb
import pickle as pkl
import yaml

parser = argparse.ArgumentParser()
# requiredNamed = parser.add_argument_group('required named arguments')
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




if __name__ == '__main__':
    s = Score()
    p.load_file(p.args.input)
    p.main(p.args.output)

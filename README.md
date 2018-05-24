# MT-Scoring-Suite
A suite of scoring metrics that I got tired of waiting for other people to implement

To import the environment:

`conda env create -f scoring.yml`

Set `config.yml` to have the location of your METEOR installation.

Get scores with:

`./score.py -c config.yml -s src.txt -r gold.txt -p pred.txt -o test.tsv`

Be sure to configure config.yml to reflect the ABSOLUTE paths of where you 
downloaded [METEOR](http://www.cs.cmu.edu/~alavie/METEOR/) and 
[TER](http://www.cs.umd.edu/~snover/tercom/). Also be sure to set the language
for METEOR.
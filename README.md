# MT-Scoring-Suite
A suite of scoring metrics that I got tired of waiting for other people to implement

To import the environment:

`conda env create -f scoring.yml`

Set `config.yml` to have the location of your METEOR installation.

Get scores with:

`./score.py -c config.yml -r gold.txt -p pred.txt -o test.txt`
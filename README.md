# PassAna

## Requirements
System: tested on Ubuntu 18.04 and 20.04，
Lib: CodeQL-CLI

## LGTM DataSet
Download LGTM data to local `$project-home$`

In `$project-home$`, use this script `for z in *.zip; do unzip $z && rm $z; done` to unzip files.

## Structure
`context`: Flow Context Classifier

`pwd`: Credential Classifier

`ql`: Ql Scripts

`tokenizer`: NLP tokenizer


## Running Introduction

`1.anaStringLiterals`: find all string，输出为`pass.csv`

`2.3.trainModel`: train credential classifier 

`4.1trainContextClassifier`: train flow context classifier 



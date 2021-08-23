#!/bin/bash

sphinx-build -b latex . latex

cd latex

pdflatex swprepost.tex

pdflatex swprepost.tex

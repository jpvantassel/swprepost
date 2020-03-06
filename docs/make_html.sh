#!/bin/bash

sphinx-build -a -E -b html . html
cd html
ls
/c/Program\ Files/Mozilla\ Firefox/firefox index.html

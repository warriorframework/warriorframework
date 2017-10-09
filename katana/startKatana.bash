#!/bin/bash

set +x
python -c 'import django'
result="$?"
if [ "$result" -ne 0 ]; then 
	echo "Please install django for katana to work"
	echo "Try sudo pip install Django"
else 
	python ./katana.py $*
fi

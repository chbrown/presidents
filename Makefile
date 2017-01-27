all: data/millercenter/speeches.json data/tapp/election2016.json data/tapp/inaugurals.json

# pre-requisite for all of these commands:
# pip install -r requirements.txt

data/millercenter/speeches.json:
	python src/cli.py millercenter > $@

# this takes ~20 minutes even with all the pages already cached
data/tapp/election2016.json:
	python src/cli.py tapp-election2016 > $@

data/tapp/inaugurals.json:
	python src/cli.py tapp-inaugurals > $@

all: data/millercenter/speeches.json data/tapp/election2016.json data/tapp/inaugurals.json

# pre-requisite for all of these commands:
# pip install -r requirements.txt

data/millercenter/speeches.json:
	python src/cli.py millercenter > $@

# this takes ~20 minutes even with all the pages already cached
data/tapp/election2016.json:
	python src/cli.py tapp-election2016 > $@

# this takes ~22 minutes, including fetching the pages
data/tapp/election2012.json:
	python src/cli.py tapp-election2012 > $@

# this takes ~23 minutes, including fetching the pages
data/tapp/election2008.json:
	python src/cli.py tapp-election2008 > $@

data/tapp/election2004.json:
	python src/cli.py tapp-election2004 > $@

data/tapp/election1960.json:
	python src/cli.py tapp-election1960 > $@

data/tapp/inaugurals.json:
	python src/cli.py tapp-inaugurals > $@

data/tapp/transition2017.json:
	python src/cli.py tapp-transition2017 > $@

data/tapp/transition2009.json:
	python src/cli.py tapp-transition2009 > $@

data/tapp/transition2001.json:
	python src/cli.py tapp-transition2001 > $@


data/trump.json:
	: > $@
	python src/cli.py abcnews Politics/transcript-abc-news-anchor-david-muir-interviews-president/story?id=45047602 >> $@
	python src/cli.py cspan 422829-1 >> $@
	python src/cli.py cbsnews news/trump-cia-speech-transcript >> $@

all: data/millercenter/speeches.json data/tapp/election2016.json data/tapp/inaugurals.json

# pre-requisite for all of these commands:
# pip install -r requirements.txt

data/millercenter/speeches.json:
	python src/cli.py millercenter > $@

# this takes ~20 minutes even with all the pages already cached
data/tapp/election2016.json:
	python src/cli.py tapp-election2016 > $@

data/tapp/election2012.json:
	python src/cli.py tapp-election2012 > $@

data/tapp/election2008.json:
	python src/cli.py tapp-election2008 > $@

data/tapp/inaugurals.json:
	python src/cli.py tapp-inaugurals > $@


data/trump.json:
	: > $@
	python src/cli.py abcnews Politics/transcript-abc-news-anchor-david-muir-interviews-president/story?id=45047602 >> $@
	python src/cli.py cspan 422829-1 >> $@
	python src/cli.py cbsnews news/trump-cia-speech-transcript >> $@

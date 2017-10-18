all: data/millercenter/speeches.json data/tapp/election2016.json data/tapp/inaugurals.json

SCRAPE := python -m presidents.scraping.cli

.PHONY: install clean check
install:
	pwd > /usr/local/lib/python2.7/site-packages/presidents.pth

clean:
	rm presidents/**/*.pyc

check:
	pep8 presidents/**/*.py

data/millercenter/speeches.json:
	$(SCRAPE) millercenter > $@

# this takes ~20 minutes even with all the pages already cached
data/tapp/election2016.json:
	$(SCRAPE) tapp-election2016 > $@

# this takes ~22 minutes, including fetching the pages
data/tapp/election2012.json:
	$(SCRAPE) tapp-election2012 > $@

data/tapp/election2008.json:
	$(SCRAPE) tapp-election2008 > $@

data/tapp/election2004.json:
	$(SCRAPE) tapp-election2004 > $@

data/tapp/election1960.json:
	$(SCRAPE) tapp-election1960 > $@

data/tapp/inaugurals.json:
	$(SCRAPE) tapp-inaugurals > $@

data/tapp/transition2017.json:
	$(SCRAPE) tapp-transition2017 > $@

data/tapp/transition2009.json:
	$(SCRAPE) tapp-transition2009 > $@

data/tapp/transition2001.json:
	$(SCRAPE) tapp-transition2001 > $@

data/tapp/listing2016-%.json:
	$(SCRAPE) tapp-listing --year 2016 --month $* > $@

data/tapp/listing2017-%.json:
	$(SCRAPE) tapp-listing --year 2017 --month $* > $@

data/whitehouse/all.json:
	$(SCRAPE) whitehouse > $@

# the following is implicitly .INTERMEDIATE
data/twitter/realDonaldTrump-%.json.zip:
	curl -sL https://github.com/bpb27/trump_tweet_data_archive/raw/master/master_$*.json.zip > $@

data/twitter/realDonaldTrump-%.json.gz: data/twitter/realDonaldTrump-%.json.zip
	unzip $< # produces master_$*.json
	# beware: jq munges long integers
	jq -c '.[]' master_$*.json | gzip > $@
	rm master_$*.json

data/trump.json:
	: > $@
	$(SCRAPE) abcnews Politics/transcript-abc-news-anchor-david-muir-interviews-president/story?id=45047602 >> $@
	$(SCRAPE) cspan 422829-1 >> $@
	$(SCRAPE) cbsnews news/trump-cia-speech-transcript >> $@

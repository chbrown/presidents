all: data/millercenter/speeches.json data/tapp/election2016.json data/tapp/inaugurals.json

SCRAPE := python -m presidents.scraping.cli

# Facilities
# ==========

.PHONY: install clean check
install:
	pwd > /usr/local/lib/python2.7/site-packages/presidents.pth

clean:
	rm -f presidents/**/*.pyc
	rm -rf presidents/**/__pycache__/

check:
	pycodestyle presidents/**/*.py

# Miller Center
# =============

data/millercenter/speeches.json:
	$(SCRAPE) millercenter > $@

# The American Presidency Project (TAPP)
# ======================================

data/tapp/all.local-cache.json:
	# decompress all .json.bz2 files to stdout, then append uncompressed .json files
	bunzip2 -k -c data/tapp/papers-*.json.bz2 | cat - data/tapp/papers-*.json > $@

# echo 2016 2012 2008 2004 1960 | xargs -n1 -I % make data/tapp/election/%.pids
data/tapp/election/%.pids:
	@mkdir -p $(@D)
	$(SCRAPE) tapp-election-pids $* > $@

# echo 2017 2009 2001 | xargs -n1 -I % make data/tapp/transition/%.pids
data/tapp/transition/%.pids:
	@mkdir -p $(@D)
	$(SCRAPE) tapp-transition-pids $* > $@

# echo 11{01,02,03,04,05,07,08,10,13,18,19,20,28,33,35,36,37,39,40,41,57,60,61,62} 21{00,10,11,13,14,15,65} 22{00,01,02,10} {23,24,25}00 251{0,1} 26{00,10} 27{10,20} 2800 3001 3500 550{1,2,3} 8000 | xargs -n1 -I % make data/tapp/category/%.pids
data/tapp/category/%.pids:
	@mkdir -p $(@D)
	$(SCRAPE) tapp-pids ty=$* > $@

# seq 1 45 | xargs -n1 -I % make data/tapp/president/%.pids
data/tapp/president/%.pids:
	@mkdir -p $(@D)
	$(SCRAPE) tapp-pids pres=$* > $@

# seq 1789 2017 | xargs -n1 -I % make data/tapp/year/%.pids
data/tapp/year/%.pids:
	@mkdir -p $(@D)
	$(SCRAPE) tapp-pids year=$* > $@

# White House Briefing Room
# =========================

data/whitehouse/all.json:
	$(SCRAPE) whitehouse > $@

# Twitter
# =======

# the following is implicitly .INTERMEDIATE
data/twitter/realDonaldTrump-%.json.zip:
	curl -sL https://github.com/bpb27/trump_tweet_data_archive/raw/master/master_$*.json.zip > $@

data/twitter/realDonaldTrump-%.json.gz: data/twitter/realDonaldTrump-%.json.zip
	unzip $< # produces master_$*.json
	# beware: jq munges long integers
	jq -c '.[]' master_$*.json | gzip > $@
	rm master_$*.json

# Miscellaneous
# =============

data/trump.json:
	: > $@
	$(SCRAPE) abcnews Politics/transcript-abc-news-anchor-david-muir-interviews-president/story?id=45047602 >> $@
	$(SCRAPE) cspan 422829-1 >> $@
	$(SCRAPE) cbsnews news/trump-cia-speech-transcript >> $@

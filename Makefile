all: data/millercenter/speeches.json data/tapp/election2016.json

data/millercenter/speeches.json:
	pip install requests==2.12.5 requests-cache==0.4.13 beautifulsoup4==4.5.3
	python millercenter.py > $@

data/tapp/election2016.json:
	python tapp.py election2016 > $@

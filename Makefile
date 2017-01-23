all: data/millercenter/speeches.json

data/millercenter/speeches.json:
	pip install requests==2.12.5 requests-cache==0.4.13 beautifulsoup4==4.5.3
	python millercenter.py > $@

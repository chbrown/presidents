# Presidential data

## The Miller Center

    make millercenter.json

`millercenter.py` fetches the listing at <http://millercenter.org/president/speeches>, then fetches each of the speeches on that page, printing line-delimited JSON output to `stdout`, one line per speech.
As of 2017-01-22, the result is a 962-line file.

These entries look like the following, when pretty printed:

    {
      "president": "Barack Obama",
      "source": "http://millercenter.org/president/obama/speeches/speech-4427",
      "text": "To Chairman Dean [...] Bless the United States of America.",
      "timestamp": "2008-08-28",
      "title": "Acceptance Speech at the Democratic National Convention"
    }

The `text` field separates paragraphs with newlines.

There are two speeches on the speeches listing that lead to empty pages, and which are excluded from `millercenter.json`:

* Barack Obama's "Remarks on the Afghanistan Pullout (June 22, 2011)"
* Barack Obama's "Address to Congress on the American Jobs Act (September 8, 2011)"

Another that has a copy-and-paste issue, which the Python script mostly fixes, so it is included.

* Abraham Lincoln's "Cooper Union Address (February 27, 1860)"

Some speeches are dialogues. Potentially useful formatting, like bold-face, has been stripped from these. E.g.,

* Bill Clinton's "Presidential Debate with Senator Bob Dole (October 6, 1996)"
* George H. W. Bush's "Debate with Michael Dukakis (September 25, 1988)"

### Sample filters / analyses

Use [`jq`](https://stedolan.github.io/jq/) to get word counts for each speech (this isn't `jq`'s forte, so it's a bit slow), along with the president's name:

    printf "%s\t%s\n" president words
    <millercenter.json jq -r '[.president, (.text | [scan("\\s+")] | length + 1)] | @tsv'

Select only the inaugural speeches:

    <millercenter.json jq -c 'select(.title | test("Inaugural"))'

Print just the text of William Henry Harrison's record-setting and -holding inaugural speech:

    <millercenter.json jq -r 'select(.president=="William Harrison" and (.title | test("Inaugural"))) | .text'

Tokenize, count, and rank the top 1000 words used in inaugural addresses:

    <millercenter.json jq -r 'select(.title | test("Inaugural")) | .text' |\
      tr [:upper:] [:lower:] |\
      tr -C -s "[:alnum:]'" [:space:] | tr -s [:space:] '\n' |\
      sort | uniq -c | sort -gr |\
      cat -n | head -1000

Explanation:

| command | explanation |
|---------|-------------|
| `tr [:upper:] [:lower:]` | lowercase everything
| `tr -C -s "[:alnum:]'" [:space:]` | replace every sequence of non-alphanumeric/single-quote with a single space
| `tr -s [:space:] '\n'` | replace every space with a newline
| `sort` | sort by word so that `uniq -c` works
| `uniq -c` | replace repeated lines with a single line of the count + content (streaming, so lines must be sorted beforehand)
| `sort -gr` | re-sort by count prefix, highest to lowest
| `cat -n` | number each line
| `head -1000` | show only the top 1000 words


## The American Presidency Project

### Election 2016

`data/tapp/election2016.json` stats:

Categories:

| count |     category      |
|------:|:------------------|
|   383 | campaign speeches |
|   834 | statements        |
|  6279 | press releases    |

Authors:

| count |      author     |
|------:|:----------------|
|     1 | Carly Fiorina   |
|    10 | Lincoln Chafee  |
|    36 | Martin O'Malley |
|    51 | George Pataki   |
|    65 | Rand Paul       |
|    65 | Jim Webb        |
|    93 | Scott Walker    |
|   116 | Bobby Jindal    |
|   122 | Ben Carson      |
|   124 | Chris Christie  |
|   171 | Lindsey Graham  |
|   214 | Mike Huckabee   |
|   311 | Rick Perry      |
|   314 | Jeb Bush        |
|   340 | Donald J. Trump |
|   427 | Rick Santorum   |
|   498 | John Kasich     |
|   602 | Ted Cruz        |
|   694 | Bernie Sanders  |
|   738 | Marco Rubio     |
|  2504 | Hillary Clinton |


# Data sources

* [The American Presidency Project](http://www.presidency.ucsb.edu/)

  > [...] non-profit and non-partisan, the leading source of presidential documents on the internet. Our archives contain 122,485 documents and are growing rapidly.
  - Affiliated with the University of California, Santa Barbara.
  - Started in 1999
  - Seems to be an impressive collection of material, but only small portions are available as clean, structured data

* [The Miller Center](http://millercenter.org/)

  > [...] is a nonpartisan institute that seeks to expand understanding of the presidency, policy, and political history, providing critical insights for the nation's governance challenges.
  - Affiliated with the University of Virginia
  - On GitHub at <https://github.com/miller-center>
    - Appendices for `millercenter.org`, not source files
    - The [First Year 2017](http://firstyear2017.org/) site seems to be sourced from [@miller-center/first-year](https://github.com/miller-center/first-year)
    - And [Connecting Presidential Collections](http://presidentialcollections.org/) seems to be sourced from [@miller-center/cpc](https://github.com/miller-center/cpc) (which refers to some apparently private repos)
    - [@miller-center/presidential-speeches](https://github.com/miller-center/presidential-speeches)
      + Rag-tag bunch of files with unknown origins

  - <https://github.com/jake-mason/Presidential-Speeches>
    + Python web scraper for `millercenter.org` speeches. One text file per speech, down-cased and de-punctuated, no titles or dates. 962 files total.
    + Some K-Means clustering analysis in separate script.

* https://github.com/prateekpg2455/U.S-Presidential-Speeches
  - Analysis of only State of the Union addresses from 1790-2006 using Gensim's Word2Vec.
  - Mostly dimension reduction for visualization / clustering in embedded space (unclear why bag-of-words is insufficient)

* <http://www.bartleby.com/124/index.html>

  > Inaugural Addresses of the Presidents of the United States
  > George Washington to Donald J. Trump

* <https://www.archives.gov/presidential-libraries/research/alic/presidents.html>

  > Use these links to find information about presidential documents, the U.S. Presidents, and Presidential Libraries.
  - Miscellaneous links to presidential anecdotes
  - ([NARA](http://nara.gov/) = National Archives and Records Administration was moved to archives.gov in 2002)

* [Public Papers of the Presidents](https://www.gpo.gov/fdsys/browse/collection.action?collectionCode=PPP)

  > [...] which is compiled and published by the Office of the Federal Register, National Archives and Records Administration, began in 1957 in response to a recommendation of the National Historical Publications Commission. Noting the lack of uniform compilations of messages and papers of the Presidents before this time, the Commission recommended the establishment of an official series in which Presidential writings, addresses, and remarks of a public nature could be made available.
  - The website only lists:
    + Barack H. Obama
    + George W. Bush
    + William J. Clinton
    + George H. W. Bush
  - But in theory the papers feature the following presidents:
    + Hoover
    + Truman
    + Eisenhower
    + Kennedy
    + Johnson
    + Nixon
    + Ford
    + Carter
    + Reagan
    + George H.W. Bush
    + Clinton
    + George W. Bush

* [PresidentsUSA.net](http://www.presidentsusa.net/speeches.html)

  > The purpose of this site is to provide researchers, students, teachers, politicians, journalists, and citizens a complete resource guide to the US Presidents.
  - Affiliated with Yale
  - Hodgepodge of links to other sites, no original data.

* [PresidentialRhetoric.com](http://www.presidentialrhetoric.com/index.html)

  > This site is devoted to bringing you contemporary information and resources concerning the study of presidential rhetoric.
  - Extensive collection of Inaugural Address(es), State of the Union Addresses, and "Other Important Addresses"

* [Joint Congressional Committee on Inaugural Ceremonies](https://web.archive.org/web/20141104100712/http://www.inaugural.senate.gov/)
  - Went offline sometime in 2014, but the Wayback Machine has a decent archive


## By president

* Obama:
  - [473 Speeches and Remarks](https://obamawhitehouse.archives.gov/briefing-room/speeches-and-remarks)
  - <http://obamaspeeches.com/>
    + "Best Speeches of Barack Obama through his 2009 Inauguration"
    + Fan site (?)

* Trump:
  - <https://github.com/ryanmcdermott/trump-speeches>
    + "1mb of text data taken from speeches made by Donald Trump at various points in his 2016 campaign for President of the United States."
    + Unclear what his sources are. No metadata. No distinction between documents.
    + Includes script to generate word cloud with Python
  - <https://github.com/PedramNavid/trump_speeches>
    + "All of Trump's Speeches from June 2015 to November 9, 2016"
    + Scraped from "The American Presidency Project" with Python.
  - <http://archive.org/details/trumparchive>

    > The Trump Archive collects TV news shows containing debates, speeches, rallies, and other broadcasts related to President-elect Donald Trump. This evolving non-commercial, searchable collection is designed to preserve the historical record for posterity.
    + Primarily a source of video, but most (all?) has the (messy) closed captions for the footage.
    + These are timestamped, which is potentially useful for determining rate of speech, or for proportion of airtime claimed in a debate.
  - <https://www.whitehouse.gov/briefing-room/presidential-actions/executive-orders>

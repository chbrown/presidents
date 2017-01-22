# Presidential data

* [`speeches/`](speeches/)


## Data sources

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

## Scrapers

* [The Miller Center](Miller_Center.md)
* [The American Presidency Project](TAPP.md)


# Other Data sources

## By site

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

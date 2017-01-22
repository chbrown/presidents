# speeches

## The Miller Center

    make millercenter.json

`millercenter.py` fetches the listing at <http://millercenter.org/president/speeches>, then fetches each of the speeches on that page, printing line-delimited JSON output to `stdout`, one line per speech.
As of 2017-01-22, the result is a 962-line file.

These entries look like the following, when pretty printed:

    {
      "president": "Barack Obama",
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

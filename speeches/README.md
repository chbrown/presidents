# speeches

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

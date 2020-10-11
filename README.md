# rplint
rplint is a linter for Real Python article writers and editors.  It performs a number of checks on a markdown document reporting errors to standard out.

## Usage

The command line help is:

```bash
Usage: rplint.py [OPTIONS] FILENAME

Options:
  -l, --line-length INTEGER
  -j, --jima                 use extra bad word list
  -h, --help                 Show this message and exit.
```

Here `--line-length` is used to specify the length of line which generates an error and `--jima` adds extra words to the "Bad Word" test which the author finds useful but others may not.

## Tests

Here are the tests it performs:

* **Line Length**: Tests if any single line is longer than a limit (500 characters by default). Take links into account.
* **Bad Words**: Tests for any of a list of words which shouldn't be used in a Real Python article. This includes words like "OK", "aka", and "very".
* **Phrases**: Tests for a list of multi-word phrases which are errors.  This includes "built in", and "same exact", a personal favorite.
* **Contractions**: Searches for two-word phrases which could be contractions
* **Code Formatter**: Tests that each code block has a code formatter specified and, as a bonus, makes sure `cpp` is used instead of `c++`.
* **Leading Colon**: Tests that the final sentence before each code block ends with a colon followed by a blank line.

## Future Tests

There are several features that could be added, but the next on my list is probably:

* **URL Alive**: Attempt an HTTP GET from all links

I welcome more ideas, either as a simple message, an issue, or a PR here.

## Helping Out

I'm not sure if this will be useful to others, so until I see signs of life, I'm not going to bother with a full code of conduct and rules/guidelines for adding to the project.  Right now the rules are basically: 

* Be Nice
* Contact me (jima) if you've got questions/comments/suggestions.

This project is in very early stages and I'm not certain it will continue as a stand alone project. Watch this space!


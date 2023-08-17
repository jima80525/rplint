# rplint

`rplint` is a linter for Real Python tutorial writers and editors. It performs a number of checks on a markdown document reporting errors to standard out.

It can be install from PyPI:

```sh
$ python -m pip install rplint
```

This command will install the latest version of `rplint` form PyPI.

## Usage

The command line help is:

```sh
$ rplint --help
Usage: rplint [OPTIONS] INPUT_FILE

  Checks a Markdown file for common writing issues.

  INPUT_FILE The Markdown file to check.

Options:
  -l, --line-length INTEGER  Line length to check for [500].
  --version                  Show the version and exit.
  --help                     Show this message and exit.
```

It takes a Markdown file as a command-line argument. The `--line-length` option is used to specify the length of line which generates an error.

## Checks

Here are the check that `rplint` currently performs:

* **Line Length**: Checks if any single line is longer than a limit (500 characters by default). Take links into account.
* **Bad Words**: Checks for any of a list of words which shouldn't be used in a Real Python tutorial. This includes words like "OK", "aka", and "very".
* **Weak URLs:** Checks for poorly phrase URL text
* **Bad Phrases**: Checks for a list of multi-word phrases which are errors. This includes "built in", and "same exact", a personal favorite.
* **Section End:** Checks for sections ending in a code block or an alert block
* **Contractions**: Searches for two-word phrases which could be contractions
* **Code Formatter**: Checks that each code block has a code formatter specified and, as a bonus, makes sure `cpp` is used instead of `c++`.
* **Leading Colon**: Checks that the final sentence before each code block ends with a colon followed by a blank line.
* **Spaces in Line**: Checks for trailing and extra whitespaces in a line.

## Future Checks

There are several features that could be added, but the next on the list is probably:

* **URL Alive**: Attempt an HTTP GET from all links

I welcome more ideas, either as a simple message, an issue, or a PR here.

## Building

The project uses what is likely an odd mixture of **poetry** and **invoke**. Poetry is used to manage dependencies and invoke is used like make, running the tests and doing releases.

Installing Poetry caused me some issues. First following the [instructions](https://python-poetry.org/docs/) and then copy the PATH export that the installer put into .profile into .bashrc. This part is for linux (and possibly macOS) users.

Once that's installed (and you have a virtualenv setup!) use `poetry install` to get all the required dependencies set up.

The invoke tool uses `tasks.py` to provide commands to build and test the code. The most frequent ones to use are: `invoke --list`, which shows the list of possible commands, and `invoke test` which runs the unit tests.

## Helping Out

I'm not sure if this will be useful to others, so until I see signs of life, I'm not going to bother with a full code of conduct and rules/guidelines for adding to the project. Right now the rules are basically:

* Be Nice
* Contact me (jima) if you've got questions/comments/suggestions.

This project is in very early stages and I'm not certain it'll continue as a stand alone project. Watch this space!

## Authors

I'd like to thank Brad Solomon for offering some excellent PRs on this and really moving it forward!

## Release Notes

### 0.8.0

* Some deep structural refactors to the code provided by Leodanis Pozo Ramos.

### 0.7.1

* Fix for false positive matches when checking for phrases. For example "edit is" was triggering a contraction check for "it it".

### 0.6.0 -> 0.7.0 - 14 Feb 2021

* Fixed link-removal regex so it removes links with bolded and mono-spaced text
* Added link-removal to all line and word tester tests. This remove false positives on links from python.org among other things
* Added many of the words from the RP spelling recommendation pages.
* Fixed a couple of missing contractions, along with checks for "we" and "our"
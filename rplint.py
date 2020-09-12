#!/usr/bin/env python3
import re
import sys


class Tester:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def __str__(self):
        str = ""
        if self.errors:
            str += f"{self.title} Errors\n"
            for item in self.errors:
                str += f"\t{item}\n"
        # JHA TODO add flag for showing/hiding warnings
        if self.warnings:
            str += f"{self.title} Warnings\n"
            for item in self.warnings:
                str += f"\t{item}\n"

        return str


class LineTester(Tester):
    def __init__(self):
        super().__init__()
        self.title = "Base Class Only"

    def test_lines(self, lines):
        for index, line in enumerate(lines, start=1):
            line = line.strip()
            self.test_line(index, line)


class WordTester(Tester):
    def __init__(self):
        super().__init__()
        self.title = "Base Class Only"

    def test_lines(self, lines):
        for index, line in enumerate(lines, start=1):
            line = line.strip()
            for word in self.extract(line):
                self.test_word(index, word, line)

    def extract(self, text):
        word_regex = re.compile(
            u"([\\w\\-'’`]+)([.,?!-:;><@#$%^&*()_+=/\]\\[])?")  # noqa W605
        previous = None
        final_word = None
        for match in word_regex.finditer(text):
            try:
                word = match.group(1)
                if not word:
                    raise Exception("No word matches found. Bad regex?")
                if previous:
                    yield previous
                    yield previous + " " + word
                if match.group(2):  # hit punctuation, yield word by itself
                    yield word
                    previous = None
                else:
                    previous = word
                final_word = previous
            except IndexError:
                word = match.group(0)
                yield word

        if final_word:
            yield final_word


class TestLineLen(LineTester):
    def __init__(self):
        super().__init__()
        self.title = "Line Length"
        # JHA TODO get these in command line args with defaults
        self.error_len = 500
        self.warn_len = 400

    def test_line(self, index, line):
        if len(line) > self.error_len:
            self.errors.append(f"{index:5}: Line length: {len(line)}")
        elif len(line) > self.warn_len:
            self.warnings.append(f"{index:5}: Line length: {len(line)}")


class TestBadWords(WordTester):
    def __init__(self):
        super().__init__()
        self.title = "Bad Word"
        self.bad_words = [
            "aka",
            "etc",
            "JHA",
            "TODO",
            "built in",
            "very",
            "actually",
            "OK",
            "easy",
            "simple",
            "obvious",
            "trivial",
            "complex",
            "difficult",
            "unsurprising",
        ]

    def test_word(self, index, word, line):
        if word in self.bad_words:
            trail = "..." if len(line) > 40 else ""
            self.errors.append(f"{index}: Found '{word}' in line: "
                               f"{line[:40]}{trail}")


class TestPhrases(Tester):
    def __init__(self):
        super().__init__()
        self.title = "Bad Word"
        self.bad_words = [
            "exact same",
            "built in",
            "those of you",
            "some of you",
            "as you can imagine",
        ]

    def test_line(self, index, line):
        for word in self.bad_words:
            if word in line:
                self.errors.append(f"{index}: Found '{word}' in line: {line}")


class TestCodeFormatter(LineTester):
    def __init__(self):
        super().__init__()
        self.title = "Code Formatter"
        self.in_code_block = False

    def test_line(self, index, line):
        """ Tracks that all code blocks have formatters. Keeps a state machine
        of whether or not we're in a code block as we only want to look for
        formatters on starting lines. """
        lline = line.lower()
        if line.startswith("```"):
            if self.in_code_block:
                self.in_code_block = False  # end of block
            else:
                self.in_code_block = True  # start of block
                if len(line) == 3:
                    self.errors.append(f"{index}: Code block has no formatter")
                if "c++" in line.lower():
                    self.errors.append(f"{index}: Code block has bad formatter"
                                       " (c++ instead of cpp)")
                if 'linenums=' in lline and 'linenums="' not in lline:
                    self.errors.append(f"{index}: Poorly formed linenums spec "
                                       "on formatter")


def main(filename):
    testers = [TestLineLen(), TestBadWords(), TestCodeFormatter(), ]
    # testers = [TestLineLen(), TestCodeFormatter(), ]
    # testers = [TestBadWords(), ]
    with open(filename) as infile:
        lines = infile.readlines()
        for tester in testers:
            tester.test_lines(lines)
            print(tester)


if __name__ == "__main__":
    main(sys.argv[1])

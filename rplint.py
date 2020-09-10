#!/usr/bin/env python3
import sys


class Tester:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def test_line(self, index, line):
        """ A real developer would make this an abstract base class. """
        print("Improperly formed Test class")
        sys.exit(1)

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


class TestLineLen(Tester):
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


class TestBadWords(Tester):
    def __init__(self):
        super().__init__()
        self.title = "Bad Word"
        self.bad_words = [
            "aka",
            "etc",
            "JHA",
            "TODO",
            "very",
            "actually",
            "exact same",
            "built in",
            "those of you",
            "some of you",
            "OK",
            "easy",
            "simple",
            "obvious",
            "trivial",
            "complex",
            "difficult",
            "unsurprising",
            "as you can imagine",
        ]

    def test_line(self, index, line):
        for word in self.bad_words:
            if word in line:
                self.errors.append(f"{index}: Found '{word}' in line: {line}")


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


class TestCodeFormatter(Tester):
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
    with open(filename) as infile:
        for index, line in enumerate(infile, start=1):
            line = line.strip()
            for tester in testers:
                tester.test_line(index, line)
    for tester in testers:
        print(tester)


if __name__ == "__main__":
    # main("PracticeProblems.mdt")
    main(sys.argv[1])

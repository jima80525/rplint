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

    def __bool__(self):
        return bool(self.errors)

    def truncate_line(self, line):
        trail = "..." if len(line) > 40 else ""
        self.trunc = f"{line[:40]}{trail}"

    def add_error(self, index, msg, origLine=None):
        line = ""
        if origLine:
            trail = "..." if len(origLine) > 40 else ""
            line = f": {origLine[:40]}{trail}"

        self.errors.append(f"{index:5}: {msg}{line}")


class LineTester(Tester):
    def __init__(self):
        super().__init__()
        self.title = "Base Class Only"
        self.in_code_block = False

    def test_lines(self, lines):
        """Keeps a state machine of whether or not we're in a code block as
        some tests only want to look outside code blocks."""
        self.lines = [line.strip() for line in lines]
        for index, line in enumerate(lines, start=1):
            self.truncate_line(line)
            if line.startswith("```"):
                self.in_code_block = not self.in_code_block
            self.test_line(index, line)


class WordTester(Tester):
    def __init__(self):
        super().__init__()
        self.title = "Base Class Only"

    def test_lines(self, lines):
        for index, line in enumerate(lines, start=1):
            self.truncate_line(line)
            line = line.strip()
            for word in self.extract(line):
                self.test_word(index, word, line)

    def extract(self, text):
        word_regex = re.compile(
            r"([\w\-'’`]+)([.,?!-:;><@#$%^&*()_+=/\]\[])?"
        )  # noqa W605
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
        url_pat = r"""
                      \[        # literal opening square bracket
                      ([\w\s]*) # the shown text from the line
                      \]        # literal closing square bracket
                       \s*      # optional whitespace (is this needed?)
                       \(       # literal opening paren
                       ([^\)]*) # group the url
                       \)       # literal closing paren
                   """
        line = re.sub(url_pat, r"\g<1>", line, flags=re.VERBOSE)
        if len(line) > self.error_len:
            self.add_error(index, f"Line length: {len(line)}")
        elif len(line) > self.warn_len:
            # JHA TODO do we want this???
            self.warnings.append(f"{index:5}: Line length: {len(line)}")


class TestBadWords(WordTester):
    def __init__(self):
        super().__init__()
        self.title = "Bad Word"
        self.bad_words = [
            "aka",
            "etc",
            "OK",
            "JHA",
            "TODO",
            "very",
            "actually",
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
            self.add_error(index, f"Found '{word}' in line:")


class TestPhrases(LineTester):
    def __init__(self):
        super().__init__()
        self.title = "Bad Phrase"
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
                self.add_error(index, f"Found '{word}' in line:")


class TestCodeFormatter(LineTester):
    def __init__(self):
        super().__init__()
        self.title = "Code Formatter"

    def test_line(self, index, line):
        """Tracks that all code blocks have formatters. Keeps a state machine
        of whether or not we're in a code block as we only want to look for
        formatters on starting lines."""
        lline = line.lower()
        if line.startswith("```") and self.in_code_block:
            if len(line) == 3:
                self.add_error(index, "Code block has no formatter")
            if "c++" in line.lower():
                self.add_error(
                    index,
                    "Code block has bad formatter (c++ " "instead of cpp)",
                )
            if "linenums=" in lline and 'linenums="' not in lline:
                self.add_error(index, "Poorly formed linenums spec")


class TestLeadingColon(LineTester):
    def __init__(self):
        super().__init__()
        self.title = "Colon"
        self.in_code_block = False

    def test_line(self, index, line):
        """ensures that line before a code block is blank and two lines before
        ends with a colon."""
        if line.startswith("```") and self.in_code_block:
            """Because we're using a 1-based index, the actual indices into
            the self.lines array are offset by one."""
            blank = self.lines[index - 2]
            text = self.lines[index - 3]
            # sanity check to avoid issues
            if index < 3:
                self.add_error(index, "code block starts before text!")
            # previous line (n-2) must be blank
            elif len(blank) > 0:
                self.add_error(index, "line preceding code block must be blank")
            # line before that (n-3) must have text ending in colon
            elif len(text) == 0:
                self.add_error(index, "two blank lines before code block")
            elif text[-1] != ":":
                self.add_error(
                    index,
                    "final text preceding code block must end in colon",
                )


# @click.command(context_settings=dict(help_option_names=["-h", "--help"]))
# @click.option("-v", "--verbose", is_flag=True, help="Verbose debugging info")
# @click.argument("doc", type=str, help="Markdown document to process")
def main(filename):
    testers = [
        TestLineLen(),
        TestBadWords(),
        TestPhrases(),
        TestCodeFormatter(),
        TestLeadingColon(),
    ]
    # testers = [TestLeadingColon(), ]
    with open(filename) as infile:
        lines = infile.readlines()
        for tester in testers:
            tester.test_lines(lines)
            if tester:
                print(tester)


if __name__ == "__main__":
    main(sys.argv[1])

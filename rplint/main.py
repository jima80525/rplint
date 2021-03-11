import click
import re

__version__ = "0.7.1"


class Tester:
    def __init__(self):
        self.errors = []

    def __str__(self):
        str = ""
        if self.errors:
            str += f"{self.title} Errors\n"
            for item in self.errors:
                str += f"\t{item}\n"

        return str

    def __bool__(self):
        return bool(self.errors)

    def truncate_line(self, line):
        trail = "..." if len(line) > 40 else ""
        self.trunc = f"{line[:40]}{trail}"

    def remove_links(self, line):
        url_pat = """
                      \[                 # literal opening square bracket
                      ([\`\(\)\*\w\s-]*) # the shown text from the line
                      \]                 # literal closing square bracket
                       \s*               # optional whitespace (is this needed?)
                       \(                # literal opening paren
                       ([^\)]*)          # group the url
                       \)                # literal closing paren
                   """
        return re.sub(url_pat, r"\g<1>", line, flags=re.VERBOSE)

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
            line = self.remove_links(line)
            if line.startswith("```"):
                self.in_code_block = not self.in_code_block
            self.test_line(index, line)


def word_extractor(text):
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


class WordTester(Tester):
    def __init__(self):
        super().__init__()
        self.title = "Base Class Only"
        self.in_code_block = False

    def test_lines(self, lines):
        for index, line in enumerate(lines, start=1):
            self.truncate_line(line)
            line = self.remove_links(line)
            if line.startswith("```"):
                self.in_code_block = not self.in_code_block
            line = line.strip()
            for word in word_extractor(line):
                self.test_word(index, word, line)


class TestLineLen(LineTester):
    def __init__(self, limit):
        super().__init__()
        self.title = "Line Length"
        # JHA TODO get these in command line args with defaults
        self.error_len = limit

    def test_line(self, index, line):
        if len(line) > self.error_len:
            self.add_error(index, f"Line length: {len(line)}")


class TestBadWords(WordTester):
    def __init__(self, use_extra_words):
        super().__init__()
        self.title = "Bad Word"
        self.bad_words = [
            "I",
            "we",
            "our",
            "aka",
            "etc",
            "ok",
            "very",
            "actually",
            "article",
            "utilize",
            "utilise",
            "regarding",
            "thus",
            "upon",
            "caveat",
            "ergo",
            "incognito",
            "quasi",
            "via",
            "3-d",  # 3D
            "boolean",  # Boolean (always cap)
            "celsius",  # Celsius (cap)
            "32 bit",  # always hyphen
            "64 bit",  # always hyphen
            "comma separated",  # comma-separated list
            "cross platform",  # cross-platform (always hyphenate)
            "data set"  # dataset (NOT data set)
            "double check",  # double-check (always hyphenate as a verb)
            "double click",  # double-click (always hyphenate as a verb)
            "double space",  # double-space (always hyphenate as a verb)
            "double-spacing",  # double spacing (noun)
            "e-mail",  # email (not e-mail)
            "file name",
            "file-name",  # filename
            "file-path",  # file path
            "filesystem",
            "file-system",  # file system
            "floating point",  # floating-point number (hyphenate)
            '"for" loop',
            "for-loop",  # for loop (not “for” loop not for-loop)
            "for/else",
            "for-else",  # for … else (not for/else or for-else)
            "front end",  # front-end developer (hyphenate)
            "hard and fast",  # hard-and-fast rule
            "hard code",  # hard-code
            "hard coded",  # hard-coded
            "hard coding",  # # hard-coding
            "head first",  # headfirst (one word)
            "if/else",
            "if-else",  # if … else (not if/else or if-else)
            "indexes",  # indices (not indexes)
            "in-line",  # inline comment (no hyphen)
            "left most",  # leftmost
            "left-most",  # leftmost
            "light weight",  # lightweight
            "light-weight",  # lightweight
            "lower case",
            "lower-case",  # lowercase
            "meta-character",  # metacharacter
            "multi-dimensional",  # multidimensional
            "multi-line",  # multiline
            "new-line",  # newline
            "non empty",  # non-empty
            "nonempty",  # non-empty
            "non existent",  # nonexistent
            "non-existent",  # nonexistent
            "non indented",  # non-indented
            "nonindented",  # non-indented
            "noninteger",  # non-integer
            "object oriented",  # object-oriented
            "on ramp",  # on-ramp (hyphenate)
            "open ended",  # open-ended (aways hyphen)
            "open-source",  # open source (never hyphenate)
            "place-holder",  # placeholder
            "pre-existing",  # preexisting
            "pre-installed",  # preinstalled
            "re-assign",  # reassign
            "recreate",  # re-create (to avoid confusion with recreate, meaning to relax)
            "re-initialize",  # reinitialize
            "re-open",  # reopen
            "re-run",  # rerun
            "right click",  # right-click (always hyphenate)
            "right-most",  # rightmost
            "run-time",  # runtime
            "to-last",  # second to last (never hyphenate; “third to last” etc.)
            "slice-notation",  # slice notation
            "stand alone",  # stand-alone
            "square-bracket",  # square bracket notation (no hyphen)
            "super power",  # superpower (one word)
            "time stamp",  # timestamp (not time stamp)
            "time-stamp",  # timestamp (not time stamp)
            "top-most",  # topmost
            "upper case",  # uppercase
            "upper-case",  # uppercase
            "use-case",  # use case (not usecase not use-case)
            "usecase",  # use case (not usecase not use-case)
            "user friendly",  # user-friendly (always hyphenate)
            "user name",  # username
            "user-name",  # username
            "walk-through",  # walkthrough (not walk-through)
            "webpage",  # web page
            "web site",  # website
            "white space",  # whitespace
            "x axis",  # x-axis
            "x coordinate",  # x-coordinate (always hyphenate)
            "x value",  # x-value
            "y axis",  # y-axis
            "y coordinate",  # y-coordinate (always hyphenate)
            "y value",  # y-value
        ]
        if use_extra_words:
            self.bad_words.extend(
                [
                    "jha",
                    "todo",
                    "easy",
                    "simple",
                    "obvious",
                    "trivial",
                    "complex",
                    "difficult",
                    "unsurprising",
                ]
            )
        self.cap_words = [
            "bokeh",  # Bokeh
            "Numpy",  # NumPy
            "numpy",  # NumPy
            "Pygame",  # PyGame
            "pygame",  # PyGame
            "Pytorch",  # PyTorch
            "pytorch",  # PyTorch
            "Tensorflow",  # TensorFlow
            "tensorflow",  # TensorFlow
            "Conda",  # conda (lowercase, monospace)
            "Computer Science",
            "Computer science",  # computer science (no caps)
            "fahrenheit",  # Fahrenheit (capitalize)
            "f string",
            "F string",
            "F-string",  # f-string (hyphenate, do not capitalize)
            "gherkin",  # Gherkin (uppercase)
            "hello, world",
            "hello world",
            "Hello world",  # Hello, World (monospace, comma, caps)
            "javascript",  # JavaScript
            "Mac OS",  # macOS (not Mac OS or macos)
            "macos",  # macOS (not Mac OS or macos)
            "OSX",  # OS X (NOT OSX)
            "Pandas",  # pandas (always lowercase)
            "pep8",  # PEP 8 (not PEP8)
            "Pep8",  # PEP 8 (not PEP8)
            "PEP8",  # PEP 8 (not PEP8)
            "pep-8",  # PEP 8 (not PEP8)
            "Pep-8",  # PEP 8 (not PEP8)
            "PEP-8",  # PEP 8 (not PEP8)
            "pep 8",  # PEP 8 (not PEP8)
            "Pep 8",  # PEP 8 (not PEP8)
            "pygame",  # Pygame (always capitalize)
            "pypi",  # PyPI
            "Pypi",  # PyPI
            "Pytest",  # pytest
            "python",  # Python (not python)
            "Scikit-Learn",  # scikit-learn
            "Scikit-learn",  # scikit-learn
            "scikit-Learn",  # scikit-learn
            "start menu",  # Start menu (cap)
            "System Python",  # system Python (lowercase)
            "utf-8",  # UTF-8
            "Wi Fi",  # Wi-Fi (not WIFI)
            "WI-FI",  # Wi-Fi (not WIFI)
            "WIFI",  # Wi-Fi (not WIFI)
        ]

    def test_word(self, index, word, line):
        if word.lower() in self.bad_words:
            self.add_error(index, f"Found '{word}' in line")
        elif word in self.cap_words and not self.in_code_block:
            # frequently code blocks must spell things with different case
            self.add_error(index, f"Found '{word}' in line")


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
            "our tutorial",
            "de facto",
        ]
        # To also catch bad phrases at the beginning of a sentence
        self.bad_words.extend([p.capitalize() for p in self.bad_words])
        self.error_format = "Found '%s' in line"

    def test_line(self, index, line):
        for word in self.bad_words:
            if word in line:
                bad_list = [bad for bad in word_extractor(self.bad_words)]
                self.add_error(index, self.error_format % word)


class TestContractions(TestPhrases):
    def __init__(self):
        super().__init__()
        self.error_format = "Found '%s' (should be a contraction) in line"
        self.title = "Contraction"
        self.bad_words = [
            "has not",
            "do not",
            "it is",
            "it will",
            "that is",
            "they are",
            "they will",
            "you will",
            "you are",
        ]
        # To also catch potential contractions at the beginning of a sentence
        self.bad_words.extend([c.capitalize() for c in self.bad_words])


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


class TestCodeBlockOrAlertEndsSection(LineTester):
    ENDALERT = "endalert %}"
    ENDCODE = "```"
    end_block_re = re.compile(rf".*?({ENDALERT}|{ENDCODE})\s*")

    def __init__(self):
        super().__init__()
        self.title = "Dangling Code Block or Alert"

    def test_line(self, index, line):
        match = self.end_block_re.match(line)
        if match and not self.in_code_block:
            # We found a closing marker for a template tag or code
            # block. Now look to see if subsequent lines go straight to
            # introducing a header.
            for next_line in self.lines[index:]:
                if not next_line or next_line.isspace():
                    continue
                if next_line.startswith("#"):
                    g = match.group(1)
                    if g == self.ENDALERT:
                        msg = (
                            "a section should not end abruptly with an endalert"
                        )
                    elif g == self.ENDCODE:
                        msg = "a section should not end with a code block"
                    self.add_error(index, msg)
                else:
                    break


class TestHereLinks(LineTester):
    """Catches links where the link text is a generic term.

    ... 'generic' such as 'here' or 'this link'.
    """

    shoddy_md_link_re = re.compile(
        r"\[(?:here|this (?:article|tutorial|link))\]\([^)]+\)"
    )

    def __init__(self):
        super().__init__()
        self.title = "Bad Link Text"

    def test_line(self, index, line):
        if self.in_code_block:
            return None
        match = self.shoddy_md_link_re.search(line)
        if match:
            self.add_error(
                index, f"links should use descriptive text: {match.group(0)}"
            )


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-l", "--line-length", default=500)
@click.option("-j", "--jima", is_flag=True, help="use extra bad word list")
@click.version_option(version=__version__)
@click.argument("filename", type=str)
def rplint(line_length, jima, filename):
    testers = [
        TestLineLen(line_length),
        TestBadWords(jima),
        TestHereLinks(),
        TestPhrases(),
        TestContractions(),
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

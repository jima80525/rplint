import abc
import re
import string
from pathlib import Path

import click

BAD_WORDS_DIR = Path(__file__).parent.parent / "dicts"
TRUNCATE_LENGTH = 40
RP_SYNTAX_HIGHLIGHTERS = ["cpp"]
END_ALERT = "endalert %}"
CODE_BLOCK_DELIMITER = "```"

__version__ = "0.7.1"


class BaseChecker(abc.ABC):
    # Feature inheritance
    def __init__(self) -> None:
        self.title = "Base Class Only"
        self.in_code_block = False
        self.errors: list[str] = []
        self.error_format = "Found '%s' in line"

    def __str__(self) -> str:
        str_rep = f"{self.title}"
        if len(self.errors) > 0:
            str_rep += " Errors:\n"
            for error in self.errors:
                str_rep += f"{error:>6}\n"
        return str_rep

    def __bool__(self) -> bool:
        return len(self.errors) > 0

    def truncate_line(self, line: str):
        trail = "..." if len(line) > TRUNCATE_LENGTH else ""
        self.trunc = f"{line[:TRUNCATE_LENGTH]}{trail}"

    def remove_links(self, line: str) -> str:
        url_pattern = """
            \[                 # literal opening square bracket
            ([\`\(\)\*\w\s-]*) # the shown text from the line
            \]                 # literal closing square bracket
            \s*               # optional whitespace (is this needed?)
            \(                # literal opening paren
            ([^\)]*)          # group the url
            \)                # literal closing paren
        """
        return re.sub(url_pattern, r"\g<1>", line, flags=re.VERBOSE)

    def register_error(self, lineno: int, msg: str, orig_line=None):
        line = ""
        if orig_line:
            trail = "..." if len(orig_line) > TRUNCATE_LENGTH else ""
            line = f": {orig_line[:TRUNCATE_LENGTH]}{trail}"
        self.errors.append(f"{lineno:5}: {msg}{line}")

    def load_bad_words(self, filename) -> list[str]:
        with open(filename) as file:
            return [line.split("#")[0].strip().rstrip(",") for line in file]

    # Interface inheritance
    @abc.abstractmethod
    def run(self, lines: list[str]):
        pass


class WordsChecker(BaseChecker):
    def run(self, lines):
        for index, line in enumerate(lines, start=1):
            self.truncate_line(line)
            line = self.remove_links(line)
            if line.startswith(CODE_BLOCK_DELIMITER):
                self.in_code_block = not self.in_code_block
            line = line.strip()
            for word in self._extract(line):
                self.check_word(index, word)

    def _extract(self, text):
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

    # Interface inheritance
    def check_word(self, lineno, word):
        raise NotImplementedError


class BadWordsCheck(WordsChecker):
    def __init__(self):
        super().__init__()
        self.title = "Bad Word Test"
        self.bad_words = self.load_bad_words(BAD_WORDS_DIR / "badwords.txt")
        self.cap_words = self.load_bad_words(BAD_WORDS_DIR / "capwords.txt")

    def check_word(self, lineno, word):
        if word.lower() in self.bad_words:
            self.register_error(lineno, self.error_format % word)
        elif word in self.cap_words and not self.in_code_block:
            # Frequently, code blocks spell things in a different way
            self.register_error(lineno, self.error_format % word)


class LineChecker(BaseChecker):
    def run(self, lines):
        """Keeps a state machine of whether or not we're in a code block as
        some tests only want to look outside code blocks."""
        self.lines = [line.strip() for line in lines]
        for index, line in enumerate(lines, start=1):
            self.truncate_line(line)
            line = self.remove_links(line)
            if line.startswith(CODE_BLOCK_DELIMITER):
                self.in_code_block = not self.in_code_block
            self.check_line(index, line)

    def check_line(self, lineno, line):
        raise NotImplementedError


class LineLengthCheck(LineChecker):
    def __init__(self, limit):
        super().__init__()
        self.title = "Line Length Test"
        self.error_len = limit

    def check_line(self, lineno, line):
        if len(line) > self.error_len:
            self.register_error(lineno, f"Line length: {len(line)}")


class BadPhrasesCheck(LineChecker):
    def __init__(self):
        super().__init__()
        self.title = "Bad Phrase Test"
        self.bad_words = self.load_bad_words(BAD_WORDS_DIR / "badphrases.txt")
        # To also catch bad phrases at the beginning of a sentence
        self.bad_words.extend([p.capitalize() for p in self.bad_words])

    def check_line(self, lineno, line):
        for word in self.bad_words:
            if word in line:
                # check to make sure that the found match isn't a false match
                # (like "edit is" matching "it is")
                index = line.find(word)
                if index == 0 or line[index - 1] not in string.ascii_letters:
                    self.register_error(lineno, self.error_format % word)


class ContractionsCheck(BadPhrasesCheck):
    def __init__(self):
        super().__init__()
        self.title = "Contraction Test"
        self.bad_words = self.load_bad_words(
            BAD_WORDS_DIR / "contractions.txt"
        )
        # To also catch potential contractions at the beginning of a sentence
        self.bad_words.extend([c.capitalize() for c in self.bad_words])


class CodeFormatterCheck(LineChecker):
    def __init__(self):
        super().__init__()
        self.title = "Code Formatter Test"
        self.formatters = self.load_bad_words(
            BAD_WORDS_DIR / "syntaxhighlighters.txt"
        )

    def check_line(self, lineno, line):
        """Tracks that all code blocks have formatters."""
        if line.startswith(CODE_BLOCK_DELIMITER) and self.in_code_block:
            if len(line.strip()) == 3:
                self.register_error(lineno, "Code block has no formatter")
                return
            formatter = line[3:].split()[0]
            if formatter not in self.formatters:
                self.register_error(
                    lineno,
                    f"Code block has bad formatter '{formatter}'",
                )


class EndingColonCheck(LineChecker):
    def __init__(self):
        super().__init__()
        self.title = "Ending Colon Test"
        self.in_code_block = False

    def check_line(self, lineno, line):
        if line.startswith(CODE_BLOCK_DELIMITER) and self.in_code_block:
            """Because we're using a 1-based index, the actual indices into
            the self.lines array are offset by one."""
            previous_line = self.lines[lineno - 2]
            text_line = self.lines[lineno - 3]
            # sanity check to avoid issues
            if lineno < 3:
                self.register_error(lineno, "Code block starts before text")
            # previous line (n-2) must be blank
            elif len(previous_line) > 0:
                self.register_error(
                    lineno, "Line preceding code block must be blank"
                )
            # line before that (n-3) must have text ending in colon
            elif len(text_line) == 0:
                self.register_error(
                    lineno, "Two blank lines before code block"
                )
            elif text_line.strip()[-1] != ":":
                self.register_error(
                    lineno,
                    "Text preceding code block must end in a colon",
                )


class CodeBlockOrAlertEndsSectionCheck(LineChecker):
    end_block_re = re.compile(rf".*?({END_ALERT}|{CODE_BLOCK_DELIMITER})\s*")

    def __init__(self):
        super().__init__()
        self.title = "Dangling Code Block or Alert Test"

    def check_line(self, lineno, line):
        match = self.end_block_re.match(line)
        if match and not self.in_code_block:
            for next_line in self.lines[lineno:]:
                if not next_line or next_line.isspace():
                    continue
                if next_line.startswith("#"):
                    g = match.group(1)
                    msg = "Unkown error"
                    if g == END_ALERT:
                        msg = "Section should not end with an alert block"
                    elif g == CODE_BLOCK_DELIMITER:
                        msg = "Section should not end with a code block"
                    self.register_error(lineno, msg)
                else:
                    break


class BadLinkAnchorCheck(LineChecker):
    """Catches links where the link text is a generic term.

    ... 'generic' such as 'here' or 'this link'.
    """

    # TODO: This regex isn't working as expected
    shoddy_md_link_re = re.compile(
        r"\[(?:here|this (?:article|tutorial|link))\]\([^)]+\)"
    )

    def __init__(self):
        super().__init__()
        self.title = "Bad Link Anchor Test"

    def check_line(self, lineno, line):
        if self.in_code_block:
            return
        match = self.shoddy_md_link_re.search(line)
        if match is not None:
            self.register_error(
                lineno,
                f"Links anchored to generic term '{match.group(0)}'",
            )


@click.command()
@click.option(
    "-l",
    "--line-length",
    type=click.INT,
    default=500,
    help="Line length to check for.",
)
@click.argument(
    "input_file",
    type=click.File(mode="r"),
    required=True,
)
def rplint(input_file, line_length):
    """Checks a Markdown file for common writing errors."""
    checks = [
        BadWordsCheck(),
        LineLengthCheck(line_length),
        BadPhrasesCheck(),
        ContractionsCheck(),
        CodeFormatterCheck(),
        EndingColonCheck(),
        CodeBlockOrAlertEndsSectionCheck(),
        BadLinkAnchorCheck(),
    ]
    lines = input_file.readlines()
    for check in checks:
        check.run(lines)
        if check:
            click.secho(check, fg="red")
        else:
            click.secho(f"{check}... Passes!", fg="green")

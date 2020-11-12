import pytest

import rplint


def test_line_length():
    """ Test producing errors on long lines. """
    dut = rplint.TestLineLen(500)
    dut.test_line(1, "short")
    dut.test_line(2, "")
    dut.test_line(3, " ")
    dut.test_line(4, "l" * 500)
    assert not bool(dut)
    dut.test_line(5, "l" * 501)
    assert bool(dut)


@pytest.mark.parametrize("line", [
    "Just visit [this link](https://realpython.com/) and you'll get rich!",
    "You can find more on that [here](https://github.com/jima80525/rplint)",
])
def test_here_links(line):
    dut = rplint.TestHereLinks()
    dut.test_line(-1, line)
    assert bool(dut)


def test_bad_words():
    dut = rplint.TestBadWords(True)
    dut.test_lines(["short"])
    dut.test_lines([""])
    dut.test_lines([" "])
    dut.test_lines(["no bad words here"])
    dut.test_lines(["no bad words here" * 501])
    assert not bool(dut)

    # first word is bad
    dut = rplint.TestBadWords(True)
    dut.test_lines(["OK this is short", "that is not"])
    assert bool(dut)

    # middle word is bad
    dut = rplint.TestBadWords(True)
    dut.test_lines(["this is OK short", "that is not"])
    assert bool(dut)

    # last word is bad
    dut = rplint.TestBadWords(True)
    dut.test_lines(["this is short OK", "that is not"])
    assert bool(dut)

    # middle sentence is bad
    dut = rplint.TestBadWords(True)
    dut.test_lines(["first sentence", "this is short OK", "that is not"])
    assert bool(dut)

    # last sentence is bad
    dut = rplint.TestBadWords(True)
    dut.test_lines(
        [
            "first sentence",
            "that is not",
            "this is short OK? or not Okay",
        ]
    )
    assert bool(dut)


def test_bad_phrases():
    dut = rplint.TestPhrases()
    dut.test_lines(["short"])
    dut.test_lines([""])
    dut.test_lines([" "])
    dut.test_lines(["no bad words here"])
    dut.test_lines(["no bad words here" * 501])
    assert not bool(dut)

    # first word is bad
    dut = rplint.TestPhrases()
    dut.test_lines(["exact same this is short", "that is not"])
    assert bool(dut)

    # middle word is bad
    dut = rplint.TestPhrases()
    dut.test_lines(["this is exact same short", "that is not"])
    assert bool(dut)

    # last word is bad
    dut = rplint.TestPhrases()
    dut.test_lines(["this is short exact same", "that is not"])
    assert bool(dut)

    # middle sentence is bad
    dut = rplint.TestPhrases()
    dut.test_lines(
        ["first sentence", "this is short exact same", "that is not"]
    )
    assert bool(dut)

    # last sentence is bad
    dut = rplint.TestPhrases()
    dut.test_lines(
        [
            "first sentence",
            "that is not",
            "this is short exact same",
        ]
    )
    assert bool(dut)


def test_contractions():
    dut = rplint.TestContractions()
    dut.test_lines(["short"])
    dut.test_lines([""])
    dut.test_lines([" "])
    dut.test_lines(["no bad words here"])
    dut.test_lines(["no bad words here" * 501])
    assert not bool(dut)

    # first word is bad
    dut = rplint.TestContractions()
    dut.test_lines(["that is exact same this is short", "this is not"])
    assert bool(dut)

    # middle word is bad
    dut = rplint.TestContractions()
    dut.test_lines(["words here that is short", "this is not"])
    assert bool(dut)

    # last word is bad
    dut = rplint.TestContractions()
    dut.test_lines(["this is short that is", "this is not"])
    assert bool(dut)

    # middle sentence is bad
    dut = rplint.TestContractions()
    dut.test_lines(
        ["first sentence", "that is short exact same", "this is not"]
    )
    assert bool(dut)

    # last sentence is bad
    dut = rplint.TestContractions()
    dut.test_lines(
        [
            "first sentence",
            "this is not",
            "that is short exact same",
        ]
    )
    assert bool(dut)


def test_two_word_detect():
    valid_sentences = [
        " not exact. same be corrected!\n",
        " not exact, same be corrected!\n",
        " not exact? same be corrected!\n",
        " not exact! same be corrected!\n",
        " not exact- same be corrected!\n",
        " not exact: same be corrected!\n",
        " not exact; same be corrected!\n",
        " not exact> same be corrected!\n",
        " not exact< same be corrected!\n",
        " not exact@ same be corrected!\n",
        " not exact# same be corrected!\n",
        " not exact$ same be corrected!\n",
        " not exact% same be corrected!\n",
        " not exact^ same be corrected!\n",
        " not exact& same be corrected!\n",
        " not exact* same be corrected!\n",
        " not exact( same be corrected!\n",
        " not exact, same be corrected!\n",
        " not exact_ same be corrected!\n",
        " not exact+ same be corrected!\n",
        " not exact= same be corrected!\n",
        " not exact/ same be corrected!\n",
        " not exact[ same be corrected!\n",
        " not exact] same be corrected!\n",
    ]
    # punctuation between words means they're OK
    dut = rplint.TestPhrases()
    dut.test_lines(valid_sentences)
    assert not bool(dut)

    # fail on same phrase without punctuation
    dut = rplint.TestPhrases()
    dut.test_lines([" not exact same be corrected!\n"])
    assert bool(dut)


def test_code_formatter():
    dut = rplint.TestCodeFormatter()
    dut.test_lines(["short"])
    dut.test_lines([""])
    dut.test_lines([" "])
    dut.test_lines(["no bad words here"])
    dut.test_lines(["no bad words here" * 501])
    dut.test_lines(["```python "])
    dut.test_lines(["```cpp "])
    dut.test_lines(['```cpp linenums="1"'])
    assert not bool(dut)

    dut = rplint.TestCodeFormatter()
    dut.test_lines(["```", "```python "])
    assert bool(dut)

    dut = rplint.TestCodeFormatter()
    dut.test_lines(["```c++ "])
    assert bool(dut)

    dut = rplint.TestCodeFormatter()
    dut.test_lines(["```cpp linenums=1"])
    assert bool(dut)


def test_leading_colon():
    dut = rplint.TestLeadingColon()
    dut.test_lines(["short"])
    dut.test_lines([""])
    dut.test_lines([" "])
    dut.test_lines(["no bad words here"])
    dut.test_lines(["no bad words here" * 501])
    dut.test_lines(
        [
            "One line",
            "another line:",
            "\n",
            "```python ",
        ]
    )
    print(dut)
    assert not bool(dut)

    dut = rplint.TestLeadingColon()
    dut.test_lines(
        [
            "One line",
            "another line",
            "\n",
            "```python ",
        ]
    )
    print(dut)
    assert bool(dut)

    dut = rplint.TestLeadingColon()
    dut.test_lines(
        [
            "One line",
            "another line:",
            "```python ",
        ]
    )
    print(dut)
    assert bool(dut)


@pytest.mark.parametrize("text", [
    """\
This is a sentence. Alright, I'm introducing a code block now:

```python
f = "do the foo"
print(f)
```

## Next Section

Gee, hope you caught that, cause we're moving right on without you.
""",
    """\
This is a sentence. Alright, I'm introducing a code block now:

```python
f = "do the foo"
print(f)
```
## Next Section, But No Whitespace

Gee, hope you caught that, cause we're moving right on without you.""",
    r"""\
This is a sentence. Alright, I'm introducing a code block now:

{% alert %}
You've been alerted
{% endalert %}

## Next Section

Gee, hope you caught that, cause we're moving right on without you.
"""
])
def test_dangling_cb_alert(text):
    dut = rplint.TestCodeBlockOrAlertEndsSection()
    dut.test_lines(text.splitlines())
    print(dut)
    assert bool(dut)


def test_url_line_length():
    """ Test line length with embedded links. """
    shown = "shown_text"
    url = f"[{shown}](long url here)"
    too_short = "a" * (500 - len(url)) + url
    just_right = "a" * (500 - len(shown)) + url
    too_long = just_right + "z"

    # too_short and just_right should not raise an error
    dut = rplint.TestLineLen(500)
    dut.test_lines([too_short])
    dut.test_lines([just_right])
    assert not bool(dut)

    # too_long should fail
    dut = rplint.TestLineLen(500)
    dut.test_lines([too_long])
    assert bool(dut)

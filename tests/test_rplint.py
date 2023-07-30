import pytest

import rplint


def test_contraction():
    """Test producing errors on long lines."""
    dut = rplint.ContractionsCheck()
    dut.check_line(1, "edit is aaa")
    dut.check_line(2, "not a problem edit is")
    dut.check_line(3, "aaa edit is bbb")
    dut.check_line(4, "aaa ?edit is bbb")
    dut.check_line(5, "aaa edit is? bbb")
    assert not bool(dut)

    dut = rplint.ContractionsCheck()
    dut.check_line(1, "it is bbb")
    assert bool(dut)
    dut = rplint.ContractionsCheck()
    dut.check_line(5, "aaa it is")
    assert bool(dut)
    dut = rplint.ContractionsCheck()
    dut.check_line(5, "aaa it is bbb")
    assert bool(dut)
    dut = rplint.ContractionsCheck()
    dut.check_line(5, "aaa !!it is bbb")
    assert bool(dut)
    dut = rplint.ContractionsCheck()
    dut.check_line(5, "aaa it is!! bbb")
    assert bool(dut)


def check_line_length():
    """Test producing errors on long lines."""
    dut = rplint.LineLengthCheck(500)
    dut.check_line(1, "short")
    dut.check_line(2, "")
    dut.check_line(3, " ")
    dut.check_line(4, "l" * 500)
    fred = (
        "visit [`**this -link`](https://realpython.com/) and you'll get rich"
    )
    fred = fred + "l" * 460
    dut.run([fred])
    assert not bool(dut)
    dut.check_line(5, "l" * 501)
    assert bool(dut)

    # repeat test with link but in failing case
    dut = rplint.LineLengthCheck(500)
    fred = (
        "visit [`**this -link`](https://realpython.com/) and you'll get rich"
    )
    fred = fred + "l" * 461
    dut.run([fred])
    assert bool(dut)


@pytest.mark.parametrize(
    "line",
    [
        "Just visit [this link](https://realpython.com/) and you'll get rich!",
        "You can find more on that [here](https://github.com/jima80525/rplint)",
    ],
)
def test_here_links(line):
    dut = rplint.BadLinkAnchorCheck()
    dut.check_line(-1, line)
    assert bool(dut)


def test_bad_words():
    dut = rplint.BadWordsCheck()
    dut.run(["short"])
    dut.run([""])
    dut.run([" "])
    dut.run(["no bad words here"])
    dut.run(["no bad words here" * 501])
    assert not bool(dut)

    # first word is bad
    dut = rplint.BadWordsCheck()
    dut.run(["OK this is short", "that is not"])
    assert bool(dut)

    # middle word is bad
    dut = rplint.BadWordsCheck()
    dut.run(["this is OK short", "that is not"])
    assert bool(dut)

    # last word is bad
    dut = rplint.BadWordsCheck()
    dut.run(["this is short OK", "that is not"])
    assert bool(dut)

    # middle sentence is bad
    dut = rplint.BadWordsCheck()
    dut.run(["first sentence", "this is short OK", "that is not"])
    assert bool(dut)

    # last sentence is bad
    dut = rplint.BadWordsCheck()
    dut.run(
        [
            "first sentence",
            "that is not",
            "this is short OK? or not Okay",
        ]
    )
    assert bool(dut)


def test_bad_phrases():
    dut = rplint.BadPhrasesCheck()
    dut.run(["short"])
    dut.run([""])
    dut.run([" "])
    dut.run(["no bad words here"])
    dut.run(["no bad words here" * 501])
    assert not bool(dut)

    # first word is bad
    dut = rplint.BadPhrasesCheck()
    dut.run(["exact same this is short", "that is not"])
    assert bool(dut)

    # middle word is bad
    dut = rplint.BadPhrasesCheck()
    dut.run(["this is exact same short", "that is not"])
    assert bool(dut)

    # last word is bad
    dut = rplint.BadPhrasesCheck()
    dut.run(["this is short exact same", "that is not"])
    assert bool(dut)

    # middle sentence is bad
    dut = rplint.BadPhrasesCheck()
    dut.run(["first sentence", "this is short exact same", "that is not"])
    assert bool(dut)

    # last sentence is bad
    dut = rplint.BadPhrasesCheck()
    dut.run(
        [
            "first sentence",
            "that is not",
            "this is short exact same",
        ]
    )
    assert bool(dut)


def test_contractions():
    dut = rplint.ContractionsCheck()
    dut.run(["short"])
    dut.run([""])
    dut.run([" "])
    dut.run(["no bad words here"])
    dut.run(["no bad words here" * 501])
    assert not bool(dut)

    # first word is bad
    dut = rplint.ContractionsCheck()
    dut.run(["that is exact same this is short", "this is not"])
    assert bool(dut)

    # middle word is bad
    dut = rplint.ContractionsCheck()
    dut.run(["words here that is short", "this is not"])
    assert bool(dut)

    # last word is bad
    dut = rplint.ContractionsCheck()
    dut.run(["this is short that is", "this is not"])
    assert bool(dut)

    # middle sentence is bad
    dut = rplint.ContractionsCheck()
    dut.run(["first sentence", "that is short exact same", "this is not"])
    assert bool(dut)

    # last sentence is bad
    dut = rplint.ContractionsCheck()
    dut.run(
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
    dut = rplint.BadPhrasesCheck()
    dut.run(valid_sentences)
    assert not bool(dut)

    # fail on same phrase without punctuation
    dut = rplint.BadPhrasesCheck()
    dut.run([" not exact same be corrected!\n"])
    assert bool(dut)


def test_code_formatter():
    dut = rplint.CodeFormatterCheck()
    dut.run(["short"])
    dut.run([""])
    dut.run([" "])
    dut.run(["no bad words here"])
    dut.run(["no bad words here" * 501])
    dut.run(["```python "])
    assert not bool(dut)

    dut = rplint.CodeFormatterCheck()
    dut.run(["```", "```python "])
    assert bool(dut)


def test_leading_colon():
    dut = rplint.EndingColonCheck()
    dut.run(["short"])
    dut.run([""])
    dut.run([" "])
    dut.run(["no bad words here"])
    dut.run(["no bad words here" * 501])
    dut.run(
        [
            "One line",
            "another line:",
            "\n",
            "```python ",
        ]
    )
    print(dut)
    assert not bool(dut)

    dut = rplint.EndingColonCheck()
    dut.run(
        [
            "One line",
            "another line",
            "\n",
            "```python ",
        ]
    )
    print(dut)
    assert bool(dut)

    dut = rplint.EndingColonCheck()
    dut.run(
        [
            "One line",
            "another line:",
            "```python ",
        ]
    )
    print(dut)
    assert bool(dut)


@pytest.mark.parametrize(
    "text",
    [
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
""",
    ],
)
def test_dangling_cb_alert(text):
    dut = rplint.CodeBlockOrAlertEndsSectionCheck()
    dut.run(text.splitlines())
    print(dut)
    assert bool(dut)


def test_url_line_length():
    """Test line length with embedded links."""
    shown = "shown_text"
    url = f"[{shown}](long url here)"
    too_short = "a" * (500 - len(url)) + url
    just_right = "a" * (500 - len(shown)) + url
    too_long = just_right + "z"

    # too_short and just_right should not raise an error
    dut = rplint.LineLengthCheck(500)
    dut.run([too_short])
    dut.run([just_right])
    assert not bool(dut)

    # too_long should fail
    dut = rplint.LineLengthCheck(500)
    dut.run([too_long])
    assert bool(dut)

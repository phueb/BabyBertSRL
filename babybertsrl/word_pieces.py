"""
obtained from Allen NLP toolkit in September 2019
"""

from typing import List, Tuple

from babybertsrl import configs


def convert_wordpieces_to_words(wordpieces: List[str],
                                ) -> List[str]:
    """

    :param wordpieces:
    :return:

    written by PH in June, 2020

    """

    def convert_sub_text_to_word(pieces: List[str],
                                 remove_garbage: bool = False) -> str:  # works as expected June 25, 2020
        if remove_garbage:
            word = ''.join([p.lstrip('##') for p in pieces])
        else:
            word = ''.join([p for p in pieces])
        return word

    words = []
    for n, wp in enumerate(wordpieces):
        if wp == '[CLS]' and n == 0:
            continue
        if wp == '[SEP]' and n == len(wordpieces) - 1:  # sometimes model predicts [SEP] inside sentence
            continue

        if wp.startswith('##'):
            continue

        chunk = [wp]
        for next_wp in wordpieces[n+1:]:
            if next_wp.startswith('##'):
                chunk.append(next_wp)
            else:
                break
        words.append(convert_sub_text_to_word(chunk))

    if configs.Wordpieces.verbose:
        print('Converting pieces:')
        print(wordpieces)
        print('to words:')
        print(words)

    return words


def convert_words_to_wordpieces(tokens: List[str],
                                wordpiece_tokenizer,
                                ) -> Tuple[List[str], List[int], List[int]]:
    """
    Convert a list of tokens to wordpiece tokens and offsets, as well as adding
    BERT CLS and SEP tokens to the begining and end of the sentence.

    A slight oddity with this function is that it also returns the wordpiece offsets
    corresponding to the _start_ of words as well as the end.

    We need both of these offsets (or at least, it's easiest to use both), because we need
    to convert the labels to tags using the end_offsets. However, when we are decoding a
    BIO sequence inside the SRL model itself, it's important that we use the start_offsets,
    because otherwise we might select an ill-formed BIO sequence from the BIO sequence on top of
    wordpieces (this happens in the case that a word is split into multiple word pieces,
    and then we take the last tag of the word, which might correspond to, e.g, I-V, which
    would not be allowed as it is not preceeded by a B tag).

    For example:

    `annotate` will be bert tokenized as ['anno", "##tate'].
    If this is tagged as [B-V, I-V] as it should be, we need to select the
    _first_ wordpiece label to be the label for the token, because otherwise
    we may end up with invalid tag sequences (we cannot start a new tag with an I).

    Returns
    -------
    wordpieces : List[str]
        The BERT wordpieces from the words in the sentence.
    end_offsets : List[int]
        Indices into wordpieces such that `[wordpieces[i] for i in end_offsets]`
        results in the end wordpiece of each word being chosen.
    start_offsets : List[int]
        Indices into wordpieces such that `[wordpieces[i] for i in start_offsets]`
        results in the start wordpiece of each word being chosen.
    """
    word_piece_tokens: List[str] = []
    end_offsets = []
    start_offsets = []
    cumulative = 0
    for token in tokens:
        word_pieces = wordpiece_tokenizer.tokenize(token)
        start_offsets.append(cumulative + 1)
        cumulative += len(word_pieces)
        end_offsets.append(cumulative)
        word_piece_tokens.extend(word_pieces)

    wordpieces = ['[CLS]'] + word_piece_tokens + ['[SEP]']

    return wordpieces, end_offsets, start_offsets


def convert_verb_indices_to_wordpiece_indices(verb_indices: List[int],
                                              offsets: List[int],
                                              ):
    """
    Converts binary verb indicators to account for a wordpiece tokenizer,
    extending/modifying BIO tags where appropriate to deal with words which
    are split into multiple wordpieces by the tokenizer.

    Parameters
    ----------
    verb_indices : `List[int]`
        The binary verb indicators, 0 for not a verb, 1 for verb.
    offsets : `List[int]`
        The wordpiece offsets.

    Returns
    -------
    The new verb indices.
    """
    j = 0
    new_verb_indices = []
    for i, offset in enumerate(offsets):
        indicator = verb_indices[i]
        while j < offset:
            new_verb_indices.append(indicator)
            j += 1

    # Add 0 indicators for cls and sep tokens.
    return [0] + new_verb_indices + [0]


def convert_bio_tags_to_wordpieces(tags: List[str],
                                   offsets: List[int],
                                   ) -> List[str]:
    """
    Converts a series of BIO tags to account for a wordpiece tokenizer,
    extending/modifying BIO tags where appropriate to deal with words which
    are split into multiple wordpieces by the tokenizer.

    Parameters
    ----------
    tags : `List[str]`
        The BIO formatted tags to convert to BIO tags for wordpieces
    offsets : `List[int]`
        The wordpiece offsets.

    Returns
    -------
    The new BIO tags.
    """
    new_tags = []
    j = 0
    for i, offset in enumerate(offsets):
        tag = tags[i]
        is_o = tag == "O"
        is_start = True
        while j < offset:
            if is_o:
                new_tags.append("O")

            elif tag.startswith("I"):
                new_tags.append(tag)

            elif is_start and tag.startswith("B"):
                new_tags.append(tag)
                is_start = False

            elif tag.startswith("B"):
                _, label = tag.split("-", 1)
                new_tags.append("I-" + label)
            j += 1

    # Add O tags for cls and sep tokens.
    return ['O'] + new_tags + ['O']
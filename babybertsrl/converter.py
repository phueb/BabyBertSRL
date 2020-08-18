from typing import Iterator, List, Tuple, Union
import numpy as np

from transformers import WordpieceTokenizer

from allennlp.data.token_indexers import SingleIdTokenIndexer
from allennlp.data import Instance, Token
from allennlp.data.fields import TextField, SequenceLabelField, MetadataField

from babybertsrl.word_pieces import\
    convert_words_to_wordpieces,\
    convert_bio_tags_to_wordpieces, \
    convert_verb_indices_to_wordpiece_indices
from babybertsrl import configs


class ConverterMLM:

    def __init__(self,
                 num_masked: int,
                 wordpiece_tokenizer: WordpieceTokenizer,
                 ):
        """
        converts utterances into Allen NLP toolkit instances format
        for training with BERT.
        designed to use with CHILDES sentences

        """

        self.num_masked = num_masked
        self.wordpiece_tokenizer = wordpiece_tokenizer
        self.token_indexers = {'tokens': SingleIdTokenIndexer()}  # specifies how a token is indexed

    def _text_to_instance(self,
                          mlm_in: List[str],
                          mlm_in_wp: List[str],
                          mlm_tags: List[str],
                          mlm_tags_wp: Union[List[int], None],  # use int so that auto-indexing by Allen NLP is skipped
                          start_offsets: List[int],
                          indicator_wp: List[int],
                          ) -> Instance:

        # meta data only has whole words
        metadata_dict = dict()
        metadata_dict['start_offsets'] = start_offsets
        metadata_dict['in'] = mlm_in
        metadata_dict['gold_tags'] = mlm_tags  # is just a copy of the input without the mask

        # text-field assigns ID to each input and output token, obtained from word-piece tokenizer vocab
        # note1: BERT's output size is always the size of the word-piece tokenizer vocab
        # note2: BERT's output size need not correspond to number of word-pieces actually used to tokenize corpus,
        # which means that the word-piece tokenizer vocab may be larger than the effective (seen) vocabulary
        tokens = [Token(t, text_id=self.wordpiece_tokenizer.vocab[t]) for t in mlm_in_wp]
        text_field = TextField(tokens, self.token_indexers)

        fields = {'tokens': text_field,
                  'indicator': SequenceLabelField(indicator_wp, text_field),  # probably not needed - specific to SRL
                  'metadata': MetadataField(metadata_dict)}
        if mlm_tags_wp is not None:
            fields['tags'] = SequenceLabelField(mlm_tags_wp, text_field)

        return Instance(fields)

    def make_instances(self,
                       utterances:  List[List[str]],
                       ) -> List[Instance]:
        """
        convert on utterance into possibly multiple Allen NLP instances

        # TODO whole-word masking

        """

        res = []
        for mlm_in in utterances:
            # to word-pieces (do this BEFORE masking) - works as expected June 25, 2020
            mlm_in_wp, end_offsets, start_offsets = convert_words_to_wordpieces(mlm_in, self.wordpiece_tokenizer)
            # collect each multiple times, each time with a different masked word
            choices = np.arange(1, len(mlm_in_wp) - 1)  # prevents masking of [SEP] or [CLS]
            for masked_id in np.random.choice(choices, size=min(len(choices), self.num_masked), replace=False):
                # mask
                mlm_tags = mlm_in.copy()
                mlm_tags_wp = [configs.Training.ignored_index if n != masked_id else self.wordpiece_tokenizer.vocab[w]
                               for n, w in enumerate(mlm_in_wp)]
                mlm_in_wp[masked_id] = '[MASK]'
                indicator_wp = [0] * (len(mlm_in_wp))
                # TODO huggingface doc says indicator is about distinguishing between sentences,
                #  but allen nlp says this should also be used for "mask"

                # to instance
                instance = self._text_to_instance(mlm_in,
                                                  mlm_in_wp,
                                                  mlm_tags,
                                                  mlm_tags_wp,
                                                  start_offsets,
                                                  indicator_wp)
                res.append(instance)

        print(f'With num_masked={self.num_masked}, made {len(res):>9,} MLM instances')

        return res

    def make_probing_instances(self,
                               utterances:  List[List[str]],
                               ) -> List[Instance]:
        """
        convert each utterance into exactly one Allen NLP instance.
        differences compared to training instances:
         1)  masking is assumed to be already done
         2) no gold tags are collected, because they are assumed not to exist

        """

        res = []
        for mlm_in in utterances:
            # to word-pieces (do this BEFORE masking)
            mlm_in_wp, offsets, start_offsets = convert_words_to_wordpieces(mlm_in, self.wordpiece_tokenizer)

            mlm_tags = mlm_in.copy()  # irrelevant for probing
            mlm_tags_wp = [self.wordpiece_tokenizer.vocab[w]
                           for n, w in enumerate(mlm_in_wp)]  # relevant only for forced_choice probing tasks
            indicator_wp = [0] * (len(mlm_in_wp))

            # to instance
            instance = self._text_to_instance(mlm_in,
                                              mlm_in_wp,
                                              mlm_tags,
                                              mlm_tags_wp,
                                              start_offsets,
                                              indicator_wp)
            res.append(instance)

        print(f'Without masking, made {len(res):>9,} probing MLM instances')

        return res


class ConverterSRL:

    def __init__(self,
                 num_masked: int,
                 wordpiece_tokenizer: WordpieceTokenizer,
                 ):
        """
        converts propositions into Allen NLP toolkit instances format
        for training a BERT-based SRL tagger.
        designed to use with conll-05 style formatted SRL data.
        """

        self.num_masked = num_masked
        self.wordpiece_tokenizer = wordpiece_tokenizer
        self.token_indexers = {'tokens': SingleIdTokenIndexer()}

    @staticmethod
    def make_verb_indices(proposition):
        """
        return a one-hot list where hot value marks verb
        :param proposition: a tuple with structure (words, predicate, labels)
        :return: one-hot list, [sentence length]
        """
        num_w_in_proposition = len(proposition[0])
        res = [int(i == proposition[1]) for i in range(num_w_in_proposition)]

        if all([x == 0 for x in res]):
            raise ValueError('Verb indicator contains zeros only. ')

        return res

    def _text_to_instance(self,
                          srl_in: List[str],
                          srl_verb_indices: List[int],
                          srl_tags: List[str],
                          ) -> Instance:

        # to word-pieces
        srl_in_wp, offsets, start_offsets = convert_words_to_wordpieces(srl_in, self.wordpiece_tokenizer)
        srl_tags_wp = convert_bio_tags_to_wordpieces(srl_tags, offsets)
        verb_indices_wp = convert_verb_indices_to_wordpiece_indices(srl_verb_indices, offsets)

        # compute verb
        verb_index = srl_verb_indices.index(1)
        verb = srl_in_wp[verb_index]

        # metadata only has whole words
        metadata_dict = dict()
        metadata_dict['start_offsets'] = start_offsets
        metadata_dict['in'] = srl_in   # previously called "words"
        metadata_dict['verb'] = verb
        metadata_dict['verb_index'] = verb_index  # must be an integer
        metadata_dict['gold_tags'] = srl_tags  # non word-piece tags
        metadata_dict['gold_tags_wp'] = srl_tags_wp

        # fields
        tokens = [Token(t, text_id=self.wordpiece_tokenizer.vocab[t]) for t in srl_in_wp]
        text_field = TextField(tokens, self.token_indexers)

        fields = {'tokens': text_field,
                  'indicator': SequenceLabelField(verb_indices_wp, text_field),
                  'tags': SequenceLabelField(srl_tags_wp, text_field),
                  'metadata': MetadataField(metadata_dict)}

        return Instance(fields)

    def make_instances(self, propositions: List[Tuple[List[str], int, List[str]]],
                       ) -> List[Instance]:
        """
        roughly equivalent to Allen NLP toolkit dataset.read().
        return a list rather than a generator,
         because DataIterator requires being able to iterate multiple times to implement multiple epochs.

        """
        res = []
        for proposition in propositions:
            srl_in = proposition[0]
            srl_verb_indices = self.make_verb_indices(proposition)
            srl_tags = proposition[2]

            # to instance
            instance = self._text_to_instance(srl_in,
                                              srl_verb_indices,
                                              srl_tags)
            res.append(instance)

        print(f'Made {len(res):>9,} SRL instances')

        return res
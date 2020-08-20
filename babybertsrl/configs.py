from pathlib import Path


class Dirs:
    root = Path(__file__).parent.parent
    data = root / 'data'
    data_tools = root / 'data_tools'
    local_probing_path = Path.home() / 'Babeval_phueb' /'sentences'
    # probing data can be found at https://github.com/phueb/Babeval/tree/master/sentences


class Data:
    uncased = True  # make sure the correct Google vocab is loaded, e.g. bert-base-uncased-vocab.txt
    min_seq_length = 3
    max_seq_length = 128
    train_prob = 0.8  # probability that utterance is assigned to train split
    special_symbols = ['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]']  # order matters
    childes_symbols = ['[NAME]', '[PLACE]', '[MISC]']

    mask_vocab_id = special_symbols.index('[MASK]')


class Training:
    feedback_interval = 100
    ignored_index = -1  # any ids in argument "tags" to cross-entropy fn are ignored
    debug = False


class Eval:
    interval = 10_000
    test_sentences = False
    train_split = False
    print_perl_script_output = False  # happens at every batch so not very useful
    probe_at_step_zero = True
    probe_at_end = False

    probing_names = [
        'dummy',
        'agreement_between_neighbors',
        'agreement_across_1_adjective',
        'agreement_across_2_adjectives',
        'agreement_across_PP',
        'agreement_across_RC',
        'agreement_in_1_verb_question',
        'agreement_in_2_verb_question',
    ]


class Wordpieces:
    verbose = False
    warn_on_mismatch = False


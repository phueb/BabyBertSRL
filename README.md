# CHILDES-SRL

A corpus of semantic role labels auto-generated for 5M words of American-English child-directed speech.

## Purpose

The purpose of this repository is to:
  - host the CHILDES-SRL corpus, and code to generate it, and
  - suggest recipes for training BERT on CHILDES-SRL for classifying token spans into semantic role arguments.

Inspiration and code for a BERT-based semantic role labeler comes from the [AllenNLP toolkit](https://demo.allennlp.org).
A SRL demo can be found [here](https://demo.allennlp.org/semantic-role-labeling). 

The code is for research purpose only. 

## History

- 2008: The BabySRL project started as a collaboration between Cynthia Fisher, Dan Roth, Michael Connor and Yael Gertner, 
whose published work is available [here](https://www.aclweb.org/anthology/W08-2111/).

- 2016: The most recent work, prior to this, can be found [here](https://gitlab-beta.engr.illinois.edu/babysrl-group/babysrl)

- 2019: The current work is an extension of the previous, leveraging the powerful deep-learning model BERT. Investigation into the inner workings of the model began in in September 2019 while under the supervision of [Cynthia Fisher](https://psychology.illinois.edu/directory/profile/clfishe)
at the Department of Psychology at [UIUC](https://psychology.illinois.edu/). 

- 2020 (Spring): Experimentation with with joint training BERT on SRL and MLM began. The joint training procedure is similar to what is proposed in [https://arxiv.org/pdf/1901.11504.pdf](https://arxiv.org/pdf/1901.11504.pdf)

- 2020 (Summer): Having found little benefit for joint SRL and MLM training BERT on CHILDES,
 a new line of research comparing BERT trained on CHILDES to BERT trained on billions of words of text was begun. 
 Development moved [here](https://github.com/phueb/BabyBERT/). 
 The purpose of this repository pivoted from providing code to train BERT jointly on SRL and MLM, to 
  - host the CHILDES-SRL corpus, and code to generate it, and
  - suggest recipes for training BERT to classify token spans into semantic role arguments.
  
  
## Generating the CHILDES-SRL corpus

To annotate 5M words of child-directed speech using a semantic role tagger, trained by AllenNLP,
execute `data_tools/make_srl_training_data_from_model.py`

To generate a corpus of human-labeled semantic role labels for a small section of CHILDES, 
execute `data_tools/make_srl_training_data_from_human.py`


## Quality of auto-generated tags

How well does AllenNLP SRL tagger perform on CHILDES 2008 SRL data?
Below is a list of f1 scores, comparing its performance with that of trained human annotators.

          ARG-A1 f1= 0.00
          ARG-A4 f1= 0.00
         ARG-LOC f1= 0.00
            ARG0 f1= 0.95
            ARG1 f1= 0.93
            ARG2 f1= 0.79
            ARG3 f1= 0.44
            ARG4 f1= 0.80
        ARGM-ADV f1= 0.70
        ARGM-CAU f1= 0.84
        ARGM-COM f1= 0.00
        ARGM-DIR f1= 0.48
        ARGM-DIS f1= 0.68
        ARGM-EXT f1= 0.38
        ARGM-GOL f1= 0.00
        ARGM-LOC f1= 0.68
        ARGM-MNR f1= 0.68
        ARGM-MOD f1= 0.78
        ARGM-NEG f1= 0.99
        ARGM-PNC f1= 0.03
        ARGM-PPR f1= 0.00
        ARGM-PRD f1= 0.15
        ARGM-PRP f1= 0.39
        ARGM-RCL f1= 0.00
        ARGM-REC f1= 0.00
        ARGM-TMP f1= 0.84
          ARGRG1 f1= 0.00
          R-ARG0 f1= 0.00
          R-ARG1 f1= 0.00
      R-ARGM-CAU f1= 0.00
      R-ARGM-LOC f1= 0.00
      R-ARGM-TMP f1= 0.00
         overall f1= 0.88

## Compatibility

Tested on Ubuntu 16.04, Python 3.6, and torch==1.2.0

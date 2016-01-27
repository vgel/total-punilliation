#!/usr/bin/env python3

import itertools
import nltk
import operator

import cu_lsa

cmudict = nltk.corpus.cmudict.dict()
lemmaitzer = nltk.stem.wordnet.WordNetLemmatizer()

MATCH_THRESHOLD = 0.6

class SwapWordsException(BaseException):
    pass

def words_syls_match(a_syls, b_syls):
    if len(a_syls) > len(b_syls):
        raise SwapWordsException()
    stressed_seen = 0
    for i in range(len(b_syls) - len(a_syls)):
        if b_syls[i][-1].isdigit():
            stressed_seen += 1
        stressed_within = 0
        syls_match = 0
        for j in range(len(a_syls)):
            if a_syls[j][0] == b_syls[i + j][0]:
                syls_match += 1
            if a_syls[j][-1].isdigit():
                stressed_within += 1
        if syls_match / len(a_syls) > MATCH_THRESHOLD:
            return stressed_seen, stressed_within, 1.0 #(syls_match / len(a_syls))**2
    return None

def words_intersposed(a, b, swapped = False):
    a_phones = cmudict[a][0]
    b_phones = cmudict[b][0]
    try:
        result = words_syls_match(a_phones, b_phones)
    except SwapWordsException as _:
        return words_intersposed(b, a, swapped = True)
    if result is None: # nothing
        return None

    before, within, multiplier = result
    a_parts = cu_lsa.query_syllables(a)
    b_parts = cu_lsa.query_syllables(b)
    if a_parts is None or b_parts is None:
        return None
    if before == 0 and within >= len(b_parts): # only adds plural
        return None

    combined = b_parts[:before] + [p.upper() for p in a_parts] + b_parts[before + within:]
    if before + within >= len(b_parts) and b.endswith('s') and not a.endswith('s'):
        combined += ['s']

    return {
        'result': combined,
        'multiplier': multiplier,
        'was_swapped': swapped,
        'a_info': {
            'phones': a_phones,
            'syllables': a_parts
        },
        'b_info': {
            'phones': b_phones,
            'syllables': b_parts
        }
    }

def find_puns(wordlist_a, wordlist_b):
    for left, right in itertools.product(wordlist_a, wordlist_b):
        left_score, left_word = left
        right_score, right_word = right

        # if left/right is one of the given words, make the score the square of the other score
        # unless both are the given words, but that's just funny
        if left_score == 1.0:
            left_score = right_score
        if right_score == 1.0:
            right_score = left_score

        try:
            result = words_intersposed(left_word, right_word)
            if result is not None:
                yield {
                    'score': left_score * right_score * result['multiplier'],
                    'data': result
                }
            else:
                yield None
        except KeyError as e:
            pass

def total_punhilliation(word_a, word_b):
    word_a_lemma = lemmaitzer.lemmatize(word_a)
    word_a_results = cu_lsa.query([word_a_lemma])
    word_b_lemma = lemmaitzer.lemmatize(word_b)
    word_b_results = cu_lsa.query([word_b_lemma])

    pun_results = []
    count = 0
    for pun in find_puns(word_a_results, word_b_results):
        count += 1
        if pun is not None:
            pun_results.append(pun)
            yield count / len(word_a_results) / len(word_b_results) # progress
    yield 1.0
    yield {
        'word_a_info': {
            'original': word_a,
            'lemma': word_a_lemma
        },
        'word_b_info': {
            'original': word_b,
            'lemma': word_b_lemma
        },
        'results': sorted(pun_results, key = operator.itemgetter('score'), reverse = True)
    }
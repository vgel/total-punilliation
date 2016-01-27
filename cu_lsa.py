#!/usr/bin/env python3

import bs4
import requests

cu_url = 'http://lsa.colorado.edu/cgi-bin/LSA-select-x.html'

corpuses = {
    'bio':            'Biology_HS_betatest (300 factors)',
    'spacex':         'CSCL_spaceX (300 factors)',
    'french1':        'Francais-Contes-Total (300 factors)',
    'french2':        'Francais-Livre (300 factors)',
    'french3':        'Francais-Livres3 (100 factors)',
    'french4':        'Francais-Monde (300 factors)',
    'french5':        'Francais-Monde-Extended (300 factors)',
    'french6':        'Francais-Production-Total (300 factors)',
    'french7':        'Francais-Psychology (300 factors)',
    'french8':        'Francais-Total (300 factors)',
    'genread3':       'General_Reading_up_to_03rd_Grade (300 factors)',
    'genread6':       'General_Reading_up_to_06th_Grade (300 factors)',
    'genread9':       'General_Reading_up_to_09th_Grade (300 factors)',
    'genread12':      'General_Reading_up_to_12th_Grade (300 factors)',
    'genreadcollege': 'General_Reading_up_to_1st_year_college (300 factors)',
    'hsbio':          'HSBio (941 factors)',
    'idioms':         'Literature_with_idioms (528 factors)',
    'meso':           'Mesoamerican (249 factors)',
    'pysch':          'Psychology_Myers_5th_ed (400 factors)',
    'uav':            'UAV_SPACE (308 factors)',
    'cognit':         'cognit (300 factors)',
    'energy':         'energy (255 factors)',
    'heart':          'heart (100 factors)'
}

# LSAspace:General_Reading_up_to_1st_year_college (300 factors)
# LSATermCnt:20
# LSAFactors:
# LSAFrequency:0
# CmpType:term
# txt1:skeleton
# instrument

def query(terms, space = corpuses['genreadcollege'], term_cnt = 500, factors = None, freq = 0, cmp_type = 'term'):
    assert not isinstance(terms, str)
    resp = requests.post(cu_url, data = {
        'LSAspace': space,
        'LSAFactors': factors or '',
        'LSAFrequency': freq,
        'CmpType': cmp_type,
        'txt1': '\n'.join(terms)
    })
    if resp.status_code != 200:
        print(resp)
        raise Exception('Not 200!', resp)
    html = bs4.BeautifulSoup(resp.text)
    # print(html)
    data = html.find('table', border = '')
    rows = data.find_all('tr')[1:]
    def munge_tr(tr):
        score, term = map(lambda td: td.text.strip(), tr.find_all('td'))
        return float(score), term
    cells = [ munge_tr(tr) for tr in rows ]
    return cells

syllable_query_cache = {
    'blouses': ['blouses']
}

syl_url = 'http://www.syllablecount.com/syllables/'

def _sylc_query_syllables(word):
    resp = requests.get(syl_url + word.lower())
    if resp.status_code != 200:
        print(resp)
        raise Exception('Not 200!', resp)
    html = bs4.BeautifulSoup(resp.text)
    sylls = html.find('p', id = 'ctl00_ContentPane_paragraphtext2').find('b').text
    return sylls.split('-')

def _hms_query_syllables(word):
    resp = requests.get('http://www.howmanysyllables.com/words/' + word.lower())
    if resp.status_code != 200:
        print(resp)
        raise Exception('Not 200!', resp)
    html = bs4.BeautifulSoup(resp.text)
    return html.find('p', id = 'SyllableContentContainer').find('span', 'Answer_Red').text.split('-')

def query_syllables(word):
    if word not in syllable_query_cache:
        try:
            syllable_query_cache[word] = _hms_query_syllables(word)
        except Exception as _:
            try:
                syllable_query_cache[word] = _sylc_query_syllables(word)
            except Exception as _:
                print('failed to lookup', word)
                return None
    return syllable_query_cache[word]
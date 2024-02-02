import re
from nltk.corpus import stopwords
 
stop_words = set(stopwords.words('english'))

token_pattern = re.compile(r"\b[a-z0-9]+\b")

def computeWordFrequencies(tokens):
    """Return a dictionary of word frequencies.
    
    Parameters
    ----------
    tokens : list

    Returns
    -------
    A dictionary of word frequencies.
    """

    word_frequencies = {}
    for token in tokens:
        if token not in word_frequencies:
            word_frequencies[token] = 1
        else:
            word_frequencies[token] += 1
    return word_frequencies

def print_sorted(word_frequencies, top_k=None):
    """Returns the word frequencies in descending order.
    
    Parameters
    ----------
    word_frequencies : dict

    Returns
    -------
    A string of top k word frequencies in descending order.
    """

    sorted_word_frequencies = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)
    if not top_k:
        top_k = len(sorted_word_frequencies)

    records = []
    for item in sorted_word_frequencies[:top_k]:
        records.append(item[0] + '\t' + str(item[1]))
    
    return '\n'.join(records)

def tokenize(text:str)->list:
    """Return a list of tokens excluding stop words from a given text.
    
    Parameters
    ----------
    path : str

    Returns
    -------
    A list of tokens.
    """

    tokens = []
    tokens = token_pattern.findall(text.lower())
    tokens = [t for t in tokens if t not in stop_words]
    return tokens
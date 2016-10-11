from itertools import repeat

import pytest
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

from eli5.sklearn.unhashing import InvertableHashingVectorizer


@pytest.mark.parametrize('always_signed', [True, False])
def test_invertable_hashing_vectorizer(always_signed):
    n_features = 8
    n_words = 4 * n_features
    vec = HashingVectorizer(n_features=n_features)
    words = ['word_{}'.format(i) for i in range(n_words)]
    corpus = [w for i, word in enumerate(words, 1) for w in repeat(word, i)]
    split = len(corpus) // 2
    doc1, doc2 = ' '.join(corpus[:split]), ' '.join(corpus[split:])

    ivec = InvertableHashingVectorizer(vec)
    ivec.fit([doc1, doc2])
    check_feature_names(vec, ivec, always_signed, corpus)

    ivec = InvertableHashingVectorizer(vec)
    ivec.partial_fit([doc1])
    ivec.partial_fit([doc2])
    check_feature_names(vec, ivec, always_signed, corpus)

    ivec = InvertableHashingVectorizer(vec)
    for w in corpus:
        ivec.partial_fit([w])
    check_feature_names(vec, ivec, always_signed, corpus)


def check_feature_names(vec, ivec, always_signed, corpus):
    feature_names = ivec.get_feature_names(always_signed=always_signed)
    seen_words = set()
    for idx, feature_name in enumerate(feature_names):
        collisions = feature_name.split(' | ')
        for c in collisions:
            sign = 1
            if c.startswith('(-)'):
                c = c[len('(-)'):]
                sign = -1
            seen_words.add(c)
            if not always_signed and ivec.column_signs_[idx] < 0:
                sign *= -1
            expected = np.zeros(vec.n_features)
            expected[idx] = sign
            assert np.allclose(vec.transform([c]).toarray(), expected)
    assert seen_words == set(corpus)
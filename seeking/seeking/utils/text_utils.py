# -*- coding: utf-8 -*-
import re
from urllib.request import urlopen

import MeCab
import nltk
from sklearn.feature_extraction import stop_words as sk_stop_words


def clean(_text: str) -> str:
    _text = remove_br(_text.expandtabs(1))
    _text = remove_url(_text).strip()
    return _text if _text != '' else None


def remove_br(_text: str) -> str:
    return re.sub(r'\n+', ' ', _text, flags=re.MULTILINE)


def remove_url(_text: str) -> str:
    _text = re.sub(r'https?:\/\/.*[\r\n]*', '', _text, flags=re.MULTILINE)
    _text = re.sub(r'\s+$', '', _text, flags=re.MULTILINE)
    return _text


def custom_contained_stopwords():
    return set([
        # 'http', '学生', 'https', 'co', '好き', '大好き', 'アイコン', 'フォロー', 'ヘッダー', '最近', 'する', 'てる', 'フォロバ',
        # 'やっ', 'なっ', '無言', 'ください', 'くん', 'いる', 'アカウント', 'なり', '失礼',
    ])


def fetch_static_stopwords(en=True, ja=True):
    # english stopwords
    if en:
        stopwords_sklearn = set(sk_stop_words.ENGLISH_STOP_WORDS)
        nltk.download('stopwords')
        stopwords_nltk = set(nltk.corpus.stopwords.words('english'))
    else:
        stopwords_sklearn = set([])
        stopwords_nltk = set([])

    # japanese stopwords
    if ja:
        slothlib_file = urlopen(
            'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt')
        stopwords_slothlib = [line.decode("utf-8").strip() for line in slothlib_file]
        stopwords_slothlib = set([ss for ss in stopwords_slothlib if not ss == u''])
    else:
        stopwords_slothlib = set([])

    return list(stopwords_nltk | stopwords_sklearn | stopwords_slothlib)


class MeCabParser:
    def __init__(self,
                 dic_path='/usr/local/lib/mecab/dic/mecab-ipadic-neologd',
                 target_pos=['名詞', '動詞', '形容詞', '副詞', '連体詞']):
        self.dic_path = dic_path
        self.tagger = MeCab.Tagger('-d {}'.format(dic_path))
        self.stopwords = fetch_static_stopwords(ja=False) + ['*']
        self.stop_contained_words = custom_contained_stopwords()
        self.target_pos = target_pos

    def split(self, text: str, joined=True):
        cleaned_text = clean(text)
        words = []
        if cleaned_text:
            for chunk in self.tagger.parse(cleaned_text).splitlines()[:-1]:
                if chunk != '':
                    (surface, feature) = chunk.split('\t')
                    features = feature.split(',')
                    pos = features[0]
                    if pos in self.target_pos:
                        word = features[6]  # Vocab数を少しでも減らすため原形に変換
                        if word not in self.stopwords and not any([scw in word for scw in self.stop_contained_words]):
                            words.append(word)
        if joined:
            return ' '.join(words)
        else:
            return words


if __name__ == '__main__':
    texts = [
        '名詞抽出 & tfidf top 30をUser親でdatastoreに入れる',
        'w2vも計算してdatastoreに入れる、別テーブルがいいかも',
    ]
    parser = MeCabParser()
    splitted = list(map(parser.split, texts))
    print(splitted)

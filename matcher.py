import re
import pandas as pd
from rapidfuzz import process, fuzz

class PositionMatcher:
    SYNONYMS = {
        r'\bпто\b': 'производственно-технического отдела',
        r'\bэгс\b|эл\.?газосварщик': 'электрогазосварщик',
        r'\bавтокран\w*': 'крана автомобильного',
        r'\bбульдозерист\w*': 'машинист бульдозера',
        r'\bшофер\w*': 'водитель',
        r'\bразнорабочий\w*': 'подсобный рабочий',
        r'производитель работ\b': 'прораб',
        r'специалист по сметам': 'сметчик',
        r'\bкрановщик\b': 'машинист крана',
        r'\bмаш\.|\bмаш\b': 'машинист',
        r'\bнач\.|\bнач\b': 'начальник',
        r'\bстроит\.|\bстроит\b': 'строительных',
        r'\bмех\.|\bмех\b': 'механического',
        r'\bруч\.|\bруч\b': 'ручного'
    }

    def __init__(self, classifier_path='data/classifier.csv', threshold=60):
        self.cls = pd.read_csv(classifier_path, sep=';')
        self.cls['clean'] = self.cls['Наименование должности по классификатору'].apply(self.clean)
        self.threshold = threshold

    @classmethod
    def clean(cls, text):
        t = re.sub(r'\(.*?\)|["«][^"»]+["»]|\b(ооо|ао|зао)\b|\d+\s*(?:разряд\w*|категори\w*|кат\.?|р-да)', '', str(text).lower().replace('ё', 'е'))
        for k, v in cls.SYNONYMS.items():
            t = re.sub(k, v, t)
        return ' '.join(re.findall(r'[а-яa-z]+', t))

    def match(self, raw_title):
        cleaned = self.clean(raw_title)
        res = process.extractOne(cleaned, self.cls['clean'], scorer=fuzz.token_sort_ratio)
        if not res or res[1] < self.threshold:
            return 'НЕТ СООТВЕТСТВИЯ', '', round(1 - (res[1] if res else 0) / 100, 2)
        row = self.cls.iloc[res[2]]
        return row['Код'], row['Наименование должности по классификатору'], round(res[1] / 100, 2)

    def evaluate(self, labeled_path='data/labeled_sample.csv'):
        df = pd.read_csv(labeled_path, sep=';')
        preds = df['Исходное наименование должности'].apply(lambda x: self.match(x)[0])
        return (preds == df['Правильный код']).mean()

    def process_file(self, input_path='data/raw_positions.csv', output_path='results.csv', review_threshold=0.80):
        df = pd.read_csv(input_path, sep=';')
        res = df['Исходное наименование должности'].apply(lambda x: pd.Series(self.match(x)))
        df['код'], df['наименование по классификатору'], df['уверенность'] = res[0], res[1], res[2]
        df['требует проверки да/нет'] = df['уверенность'].apply(lambda x: 'да' if x < review_threshold else 'нет')
        df.rename(columns={'Исходное наименование должности': 'исходное наименование'}, inplace=True)
        df.to_csv(output_path, sep=';', index=False)
        return df


# --- Пример использования ---
# matcher = PositionMatcher()
#
# - Сопоставление одной должности:
# code, name, conf = matcher.match('Плотник 5 разряда')
# print(code, name, conf)  # ('КЛС-006', 'Плотник', 1.0)

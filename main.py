from matcher import PositionMatcher

def main():
    matcher = PositionMatcher()
    
    # 1. Оценка точности на проверочной выборке
    accuracy = matcher.evaluate('data/labeled_sample.csv')
    print(f"Точность (Accuracy) на labeled_sample.csv: {accuracy:.2%}")
    
    # 2. Обработка всех 300 записей и сохранение в results.csv
    results = matcher.process_file('data/raw_positions.csv', 'results.csv', review_threshold=0.80)
    flagged = (results['требует проверки да/нет'] == 'да').sum()
    print(f"Обработано {len(results)} записей. Результаты успешно сохранены в results.csv")
    print(f"Записей, требующих ручной проверки (уверенность < 0.80): {flagged}")

if __name__ == '__main__':
    main()

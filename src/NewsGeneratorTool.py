import csv
import yaml
import random
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict

from pathlib import Path

# -----------------------------
# Load configuration from YAML
# -----------------------------
def load_config(path: Path) -> Dict:
    with path.open('r') as f:
        return yaml.safe_load(f)

# -----------------------------
# Load symbols from CSV files and dates
# -----------------------------
def load_symbols_and_dates(hot_path: Path, other_path: Path, total_symbols: int):
    hot_count = int(total_symbols * 0.6)
    other_count = total_symbols - hot_count

    def read_csv_symbols(file_path: Path, count: int):
        with file_path.open('r', newline='') as f:
            reader = list(csv.DictReader(f))
            return [row['symbol'] for row in reader[:count]], reader[0]['START_DATE'], reader[0]['END_DATE']

    hot_symbols, start_date, end_date = read_csv_symbols(hot_path, hot_count)
    other_symbols, _, _ = read_csv_symbols(other_path, other_count)
    symbols = hot_symbols + other_symbols
    random.shuffle(symbols)
    return symbols, start_date, end_date

# -----------------------------
# Weighted Random Choice
# -----------------------------
def weighted_choice(choices):
    r = random.random()
    cumulative = 0
    for choice in choices:
        cumulative += choice['probability']
        if r < cumulative:
            return choice['sentiment']
    return choices[-1]['sentiment']

# -----------------------------
# Generate Random Time
# -----------------------------
def random_time():
    hour = random.randint(9, 16)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"

# -----------------------------
# Generate News Data
# -----------------------------
def generate_news_data(config_path: Path) -> List[Dict]:
    config = load_config(config_path)

    hot_symbols_path = Path(__file__).parent.parent / 'data' / 'hot_symbols.csv'
    other_symbols_path = Path(__file__).parent.parent / 'data' / 'other_symbols.csv'
    symbols_pool, start_date, end_date = load_symbols_and_dates(hot_symbols_path, other_symbols_path, config['SYMBOLS_RANGE'])

    news_items = []
    headline_counter = 1

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    delta_days = (end_dt - start_dt).days

    for _ in range(config['NUM_NEWS']):
        is_shared = random.random() < config['SHARED_HEADLINE_PROBABILITY']
        headline_id = f"H{headline_counter:04d}"

        if is_shared:
            num_symbols = random.randint(2, config['MAX_SYMBOLS_PER_SHARED_HEADLINE'])
            chosen_symbols = random.sample(symbols_pool, num_symbols)
        else:
            chosen_symbols = [random.choice(symbols_pool)]

        sentiment = weighted_choice(config['NEWS_SENTIMENTS'])
        impact_score = round(random.uniform(*config['IMPACT_SCORE_RANGE']), 3)
        confidence_score = round(random.uniform(*config['CONFIDENCE_SCORE_RANGE']), 2)
        category = random.choice(config['NEWS_CATEGORIES'])
        source = random.choice(config['NEWS_SOURCES'])
        exchange = random.choice(config['REF_EXCHANGES'])['exchange_code']
        sector = random.choice(config['REF_SECTORS'])
        date = (start_dt + timedelta(days=random.randint(0, delta_days))).strftime("%Y-%m-%d")
        time = random_time()

        for symbol in chosen_symbols:
            affected_pool = [s for s in symbols_pool if s != symbol]
            affected_symbols = random.sample(affected_pool, random.randint(0, config['MAX_AFFECTED_SYMBOLS']))
            affected_str = ";".join(affected_symbols)

            row = {
                "date": date,
                "time": time,
                "stock_symbol": symbol,
                "stock_exchange": exchange,
                "sector": sector,
                "headline_id": headline_id,
                "category": category,
                "source": source,
                "sentiment": sentiment,
                "impact_score": impact_score,
                "confidence_score": confidence_score,
                "affected_symbols": affected_str
            }

            news_items.append(row)

        headline_counter += 1

    return news_items

# -----------------------------
# Save Output in Different Formats
# -----------------------------
def save_output(news_items: List[Dict], output_dir: Path, output_format: str, batch_size: int = 500):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_format = output_format.lower()

    for i in range(0, len(news_items), batch_size):
        batch = news_items[i:i + batch_size]
        file_index = i // batch_size + 1

        if output_format == "csv":
            output_path = output_dir / f"news_batch_{file_index}.csv"
            with output_path.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=batch[0].keys())
                writer.writeheader()
                writer.writerows(batch)

        elif output_format == "json":
            output_path = output_dir / f"news_batch_{file_index}.json"
            with output_path.open('w') as f:
                json.dump(batch, f, indent=2)

        elif output_format == "parquet":
            output_path = output_dir / f"news_batch_{file_index}.parquet"
            df = pd.DataFrame(batch)
            df.to_parquet(output_path, index=False)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        print(f"✅ Saved {len(batch)} rows to {output_path}")

# -----------------------------
# Main Entry Point
# -----------------------------
if __name__ == "__main__":
    config_path = Path(__file__).parent.parent / 'config' / 'configuration.yaml'
    output_path = Path(__file__).parent.parent / 'output'

    config = load_config(config_path)
    news_data = generate_news_data(config_path)
    save_output(news_data, output_path, config.get("OUTPUT_FORMAT", "csv"))

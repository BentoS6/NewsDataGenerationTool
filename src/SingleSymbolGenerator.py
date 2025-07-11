import csv
import yaml
import random
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
# Generate News Data for One Symbol
# -----------------------------
def generate_news_data_single(config: Dict) -> List[Dict]:
    symbol_info = config['SINGLE_SYMBOL_DETAILS']
    symbol = symbol_info['symbol']
    exchange = symbol_info['exchange']
    sector = symbol_info['sector']

    base_date = datetime.strptime(config['DATE'], "%Y-%m-%d")
    delta_days = config.get('NO_OF_DAYS', 1)

    news_items = []
    headline_counter = 1

    for _ in range(config['NUM_NEWS']):
        headline_id = f"H{headline_counter:04d}"

        sentiment = weighted_choice(config['NEWS_SENTIMENTS'])
        impact_score = round(random.uniform(*config['IMPACT_SCORE_RANGE']), 3)
        confidence_score = round(random.uniform(*config['CONFIDENCE_SCORE_RANGE']), 2)
        category = random.choice(config['NEWS_CATEGORIES'])
        source = random.choice(config['NEWS_SOURCES'])

        date = (base_date - timedelta(days=random.randint(0, delta_days - 1))).strftime("%Y-%m-%d")
        time = random_time()

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
            "affected_symbols": ""
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

    news_items.sort(key=lambda x: (x['date'], x['time']))

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
    config_path = Path(__file__).parent.parent / 'config' / 'single_symbol_config.yaml'
    output_path = Path(__file__).parent.parent / 'output' / 'single_symbol'

    config = load_config(config_path)
    news_data = generate_news_data_single(config)
    save_output(news_data, output_path, config.get("OUTPUT_FORMAT", "csv"), config.get("INPUT_BATCH_SIZE", 500))

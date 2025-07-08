## 📰 News Data Generation Tool

- A python data genration script to generate **realistic financial news data** that includes columns such as **date, time, stock symbols, stock exchange, sector, headlines (this just contains the headline id for now, eg: H0001, H0002, etc), category, source, sentiment, impact score, confidence score and affected symbols**. 
---

## 📦 Features

- Generates realistic, configurable financial news data
- Robust YAML-based config file
- Outputs to **CSV**, **JSON**, or **Parquet** formats as per config file
- Supports shared headlines across multiple symbols
- Batch-wise output file support

---

## 🛠️ Requirements

Install required dependencies using:

```zsh
pip install -r requirements.txt

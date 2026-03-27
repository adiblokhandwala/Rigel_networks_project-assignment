# 📈 Trading Strategy Backtesting Engine

## 🧠 Overview

A modular Python-based backtesting engine designed to evaluate trading strategies under different market regimes such as **trending** and **ranging** conditions.

The system is built with flexibility in mind — new strategies can be added easily without modifying the core engine by simply updating configuration files and adding strategy classes.

---

## ✨ Features

* 📊 Market regime detection (Trending / Ranging)
* ⚙️ JSON-based configuration system
* 🧩 Plug-and-play strategy architecture
* 📁 Clean project structure for scalability
* 📉 Trade execution using next-day open prices
* 📄 Export of trade logs (`orders.xlsx`)




---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
```

---

### 2️⃣ Navigate to the Project Folder

```bash
cd your-repo-name
```

---

### 3️⃣ Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
```

---

### 4️⃣ Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
source .venv/bin/activate
```

---

### 5️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 6️⃣ Run the Engine

```bash
python run_engine.py --config configs/engine.json
```

---

## ⚙️ Configuration

The engine is controlled using JSON configuration files.

Example:

```json
{
  "strategy": "strategy1",
  "capital": 100000,
  "risk_per_trade": 0.02

}
```

### 📊 Selecting Different Market Data

You can choose different market instruments by modifying the `"data_ticker"` parameter in the configuration file. just add the ticker name according to yfinance. E.g. for NIFTY50 , use "^NSEI", for 

#### Examples

```json
{
  "data_ticker": "SPX"   // S&P 500 Index
}
```

You can add new strategies by:

* Creating a new class inside the `strategies/` directory
* Updating the configuration file

---

## 📊 Output

After execution, the engine generates:

* 📄 `orders.xlsx` → Trade logs


---







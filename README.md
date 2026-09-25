# 🛡️ AI-Based Network IDS/IPS

A machine-learning-powered Intrusion Detection & Prevention System demo with a real-time **Streamlit Live Sentinel Dashboard**. Trains a classifier on the NSL-KDD intrusion detection dataset, simulates live network traffic streams, alerts on suspicious flows, and automatically manages firewall deny-lists.

---

## ✨ Features

- **ML-based Classification**: Random Forest classifier trained to distinguish normal traffic from attacks.
- **Full Preprocessing Pipeline**: Categorical encoding, feature scaling, and train/test alignment.
- **Simulated Real-Time Detection**: Streams test flows with confidence scoring, alerting, and automated IP blocking.
- **🛡️ AI-Based Network IDS/IPS Dashboard (`app.py`)**:
  - **Live KPI Metrics**: Real-time Total Flows, Alerts Raised, Active Blocked IPs, Accuracy, and Threat Density %.
  - **Streamlit Auto-Refresh**: Adjustable auto-refresh intervals (1s to 10s).
  - **Embedded Detector Controller**: Start, stop, and configure `simulateDetector.py` from the sidebar.
  - **Interactive Analytics**: Plotly traffic volume timelines, action breakdown pie charts, and top attack source charts.
  - **Firewall Deny-List Management**: View active blocked IPs with one-click **Unblock IP** rule management.
  - **Real-Time Stream Inspector**: Filter flows by status/action, search by IP address, filter by confidence, and export CSV logs.
  - **Cloud-Ready Demo Mode**: Automatically initializes sample traffic flows on launch if log data is empty.

---

## 🏗️ Architecture & How It Works

```
Network traffic → Feature extraction → ML classifier → Decision engine
                                                             ↓         ↓
                                                         Alert (IDS)  Block (IPS)
                                                             ↓         ↓
                                                    Live Streamlit Dashboard (app.py)
```

---

## 📦 Setup & Installation

```bash
git clone https://github.com/Gayatri123-77/ids-ips.git
cd ids-ips
pip install -r requirements.txt
```

---

## 🚀 Running the Project

### 1. Download Dataset & Train Model
```bash
python data.py
python preprocess.py
python train.py
```

### 2. Launch the Live Sentinel Dashboard
```bash
streamlit run app.py
```

### 3. Stream Traffic Simulation
You can trigger simulation directly from the Dashboard Sidebar UI, or execute via CLI:
```bash
python simulateDetector.py --num-rows 500 --sleep 0.05 --threshold 0.5
```

---

## 📁 Project Structure

```
ids-ips/
├── app.py                 # Streamlit live Sentinel dashboard
├── data.py                # Downloads NSL-KDD dataset
├── preprocess.py          # Preprocesses & scales features
├── train.py               # Trains & evaluates Random Forest classifier
├── simulateDetector.py   # Real-time IDS/IPS flow simulator
├── blocked_ips.txt        # Live firewall deny-list & audit log
├── requirements.txt       # Dependencies (pandas, scikit-learn, streamlit, plotly)
└── README.md              # Project documentation
```

---

## 📊 Dataset

Uses [NSL-KDD](http://nsl.cs.unb.ca/NSL-KDD/), an improved version of the classic KDD Cup 1999 intrusion detection dataset.

---

## ⚠️ Disclaimer

This project is built for educational and demonstration purposes. Only run non-simulated versions on networks you own or have explicit permission to audit.

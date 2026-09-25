
# 🛡️ AI-Based Network IDS/IPS

A machine-learning-powered Intrusion Detection & Prevention System demo, built as a hands-on learning project. Trains a classifier on the NSL-KDD intrusion detection dataset, then simulates a live network traffic stream through it — alerting on suspicious flows and "blocking" repeat offenders.

> 📚 This is a **learning/demo project**: it runs on a labeled dataset rather than live network traffic, and blocking is simulated (logged, not enforced on a real firewall). See [Next Steps](#-next-steps--going-further) for how to extend it toward a real deployment.

# 🛡️ AI-Based Network IDS/IPS with Live Dashboard


# 🛡️ AI-Based Network IDS/IPS with  Live Sentinel Dashboard




## ✨ Features

- **ML-based classification** — Random Forest classifier trained to distinguish normal traffic from attacks
- **Full preprocessing pipeline** — categorical encoding, feature scaling, class imbalance handling
- **Evaluation metrics** — accuracy, precision, recall, F1, confusion matrix (not just raw accuracy, which is misleading on imbalanced traffic data)
- **Simulated real-time detection** — replays test data as a live stream with alerts printed as they happen
- **Simulated IPS blocking** — flags repeat-offending source IPs and "blocks" them, logged to file



## 🏗️ How it works

```
Network traffic → Packet capture → Feature extraction → ML classifier → Decision engine
                                                                              ↓         ↓
                                                                          Alert (IDS)  Block (IPS)
                                                                              ↓         ↓
                                                                          Logging & dashboard
```

This demo starts from a pre-labeled dataset (NSL-KDD) instead of live packet capture, so you can focus on the ML pipeline first before adding real network I/O.

---

## 📦 Setup

```bash
git clone https://github.com/Gayatri123-77/ids-ips.git
cd ids-ips
pip install -r requirements.txt
```

## 🚀 Usage

Run the scripts in order:

```bash
python download_data.py      # fetches NSL-KDD into ./data/
python preprocess.py         # builds model-ready arrays in ./artifacts/
python train.py              # trains + evaluates the Random Forest
python simulate_detector.py  # streams traffic through the model, alerts + "blocks"
```

Optional flags for the simulator:

```bash
python simulate_detector.py --num-rows 500 --sleep 0.05 --threshold 0.6
```

| Flag | Meaning | Default |
|---|---|---|
| `--num-rows` | How many test flows to stream | 300 |
| `--sleep` | Seconds paused between flows (for a "live" feel) | 0.03 |
| `--threshold` | Confidence required to trigger an alert/block | 0.5 |
| `--seed` | Random seed for reproducible runs | 42 |

---

## 📁 Project structure

```
ids-ips/
├── download_data.py       # downloads NSL-KDD dataset
├── preprocess.py           # cleans, encodes, scales the data
├── train.py                 # trains and evaluates the classifier
├── simulate_detector.py    # simulated real-time IDS/IPS demo
├── requirements.txt
└── README.md
```

`data/` and `artifacts/` are generated at runtime and git-ignored (see `.gitignore`) since they contain the raw dataset and trained model files.

---

## 📊 Dataset

Uses [NSL-KDD](http://nsl.cs.unb.ca/NSL-KDD/), an improved, de-duplicated version of the classic KDD Cup 1999 intrusion detection dataset — a standard benchmark for this kind of ML security project.

---

## 🔭 Next steps / going further

- Replace the dataset-driven input with real live packet capture (Scapy/Zeek)
- Try a modern, more realistic dataset like CICIDS2017
- Add multi-class classification (attack *type*, not just attack/normal)
- Wire real blocking into `iptables`/`nftables`
- Build a live dashboard (Flask/Streamlit) for alerts and blocked IPs

---

## ⚠️ Disclaimer

This is an educational project. Only ever point a real (non-simulated) version of this at traffic or networks you own or have explicit permission to test.


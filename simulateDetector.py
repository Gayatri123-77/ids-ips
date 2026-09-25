import os
import time
import random
import argparse
import numpy as np
import joblib
 
ARTIFACT_DIR = "artifacts"
LOG_FILE = "blocked_ips.txt"
 
 
def synthetic_ip(row_index, rng):
    # Deterministic-looking but arbitrary IP per row, drawn from a small
    # pool of 40 "hosts" so a handful of IPs generate repeat traffic and
    # can actually get blocked more than once.
    rng_state = random.Random(row_index % 40)
    return f"10.0.{rng_state.randint(0, 5)}.{rng_state.randint(1, 254)}"
 
 
def load_artifacts():
    model = joblib.load(os.path.join(ARTIFACT_DIR, "model.joblib"))
    X_test = np.load(os.path.join(ARTIFACT_DIR, "X_test.npy"))
    y_test = np.load(os.path.join(ARTIFACT_DIR, "y_test.npy"))
    return model, X_test, y_test
 
 
def run(num_rows, sleep_seconds, threshold, seed):
    model, X_test, y_test = load_artifacts()
 
    rng = random.Random(seed)
    total_rows = X_test.shape[0]
    num_rows = min(num_rows, total_rows)
    indices = list(range(total_rows))
    rng.shuffle(indices)
    indices = indices[:num_rows]
 
    blocked_ips = set()
    alerts = 0
    correct = 0
 
    with open(LOG_FILE, "w") as log:
        log.write("timestamp,src_ip,true_label,predicted,confidence,action\n")
 
        for step, idx in enumerate(indices, start=1):
            row = X_test[idx].reshape(1, -1)
            true_label = int(y_test[idx])
            proba = model.predict_proba(row)[0]
            pred_label = int(model.classes_[np.argmax(proba)])
            confidence = float(np.max(proba))
            src_ip = synthetic_ip(idx, rng)
 
            is_attack_flag = pred_label == 1 and confidence >= threshold
            correct += int(pred_label == true_label)
 
            timestamp = time.strftime("%H:%M:%S")
            action = "none"
 
            if is_attack_flag:
                alerts += 1
                already_blocked = src_ip in blocked_ips
                print(f"[{timestamp}] flow #{step:04d}  src={src_ip:<14} "
                      f"ALERT attack (confidence {confidence:.2f})")
                if not already_blocked:
                    blocked_ips.add(src_ip)
                    action = "blocked"
                    print(f"             -> BLOCKING {src_ip} (added to firewall deny-list)")
                else:
                    action = "already_blocked"
                    print(f"             -> {src_ip} already blocked, skipping")
            else:
                action = "allowed"
 
            log.write(f"{timestamp},{src_ip},{true_label},{pred_label},{confidence:.4f},{action}\n")
            time.sleep(sleep_seconds)
 
    print("\n=== Run summary ===")
    print(f"Flows processed:     {num_rows}")
    print(f"Alerts raised:       {alerts}")
    print(f"Unique IPs blocked:  {len(blocked_ips)}")
    print(f"Prediction accuracy on this sample: {correct / num_rows:.2%}")
    print(f"Full log written to {LOG_FILE}")
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulated real-time IDS/IPS demo")
    parser.add_argument("--num-rows", type=int, default=300, help="How many test flows to stream")
    parser.add_argument("--sleep", type=float, default=0.03, help="Seconds to pause between flows")
    parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold to trigger an alert/block")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible ordering")
    args = parser.parse_args()
 
    run(args.num_rows, args.sleep, args.threshold, args.seed)
 
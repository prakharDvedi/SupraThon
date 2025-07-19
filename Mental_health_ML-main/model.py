import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import os
import pickle



WEIGHTS_FILE = "model_weights.pkl"

# Feature engineering functions

def rolling_entropy(series, bins=10, window=7):
    def entropy(window_data):
        counts, _ = np.histogram(window_data, bins=bins)
        probs = counts / counts.sum() if counts.sum() != 0 else np.ones_like(counts)
        probs = probs[probs > 0]
        return -np.sum(probs * np.log2(probs))
    return series.rolling(window).apply(entropy, raw=True)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Model parameters
def train_and_save_model():
    df = pd.read_csv("Mental_health_ML-main\\wearable_sensor_data.csv")
    df = df.sort_values(by=["user_id", "day_index"]).reset_index(drop=True)
    grouped = df.groupby("user_id")
    df["SRE"] = grouped["sleep_onset_time"].apply(rolling_entropy).reset_index(level=0, drop=True)
    df["PAI"] = grouped["step_count"].apply(
        lambda x: x.rolling(window=5).std() / x.rolling(window=5).mean()
    ).reset_index(level=0, drop=True)
    df["HRSI"] = grouped["resting_heart_rate"].apply(
        lambda x: 1 / x.rolling(window=5).std()
    ).reset_index(level=0, drop=True)
    df["SDAS"] = grouped["sleep_duration"].apply(
        lambda x: np.maximum(0, 7*8 - x.rolling(window=7).sum())
    ).reset_index(level=0, drop=True)
    df["SSR"] = grouped["stress_level"].apply(
        lambda x: x.rolling(window=7).apply(lambda w: np.mean(w > 0.7))
    ).reset_index(level=0, drop=True)
    df["ARI"] = (df["HR_day_avg"] - df["HR_sleep_min"]) / df["HR_day_avg"]
    df_clean = df.dropna().reset_index(drop=True)
    features = [
        'sleep_duration', 'step_count', 'resting_heart_rate',
        'stress_level', 'sleep_onset_time', 'HR_day_avg', 'HR_sleep_min',
        'SRE', 'PAI', 'HRSI', 'SDAS', 'SSR', 'ARI'
    ]
    df_clean["anomaly"] = ((df_clean["stress_level"] > 0.85) |
                           (df_clean["SDAS"] > 10) |
                           (df_clean["ARI"] < 0.1)).astype(int)
    X = df_clean[features].values
    Y = np.array(df_clean["anomaly"].values).reshape(-1, 1)
    Y_labels = np.array(df_clean["anomaly"].values)
    X_train, X_test, Y_train_labels, Y_test_labels = train_test_split(
        X, Y_labels, test_size=0.2, random_state=42, stratify=Y_labels
    )
    encoder = OneHotEncoder(sparse_output=False)
    Y_train = encoder.fit_transform(np.array(Y_train_labels).reshape(-1, 1))
    T = np.array(X_train).shape[0]
    n_features = np.array(X_train).shape[1]
    n_layers = 10
    n_nodes = 2048
    C_inv = 2e-2
    w1 = np.random.rand(n_features, n_nodes)
    w = np.random.rand(n_nodes+n_features, n_nodes, n_layers-1)
    bias = np.random.rand(n_nodes, n_layers)
    H_list = []
    K1 = np.dot(X_train , w1)
    H1 = sigmoid(K1 + bias.T[0:1, :])
    H_list.append(H1)
    for i in range(1, n_layers):
        prev_h = H_list[i-1]
        matrix = np.concatenate((prev_h, X_train), axis=1)
        K = np.dot(matrix, w[: , :, i-1])
        new_h = sigmoid(K + bias.T[i:i+1 , :])
        H_list.append(new_h)
    D_list = []
    D1 = np.concatenate((H_list[0], X_train), axis=1)
    D_list.append(D1)
    for i in range(1, n_layers):
        D_new = np.concatenate((H_list[i],H_list[i-1], X_train), axis=1)
        D_list.append(D_new)
    beta_list = []
    if n_features+n_nodes<T:
        beta1 = np.dot(np.dot(np.linalg.inv(np.dot(D_list[0].T,D_list[0]) + C_inv*(np.eye(n_features+n_nodes))),D_list[0].T),Y_train)
    else :
        beta1 = np.dot(np.dot(D_list[0].T,np.linalg.inv(np.dot(D_list[0],D_list[0].T) + C_inv*(np.eye(T)))),Y_train)
    beta_list.append(beta1)
    for i in range(1,n_layers):
        if n_features+2*n_nodes<T:
            beta = np.dot(np.dot(np.linalg.inv(np.dot(D_list[i].T,D_list[i]) + C_inv*(np.eye(n_features+2*n_nodes))),D_list[i].T),Y_train)
        else:
            beta= np.dot(np.dot(D_list[i].T,np.linalg.inv(np.dot(D_list[i],D_list[i].T) + C_inv*(np.eye(T)))),Y_train)
        beta_list.append(beta)
    # Save weights
    with open(WEIGHTS_FILE, 'wb') as f:
        pickle.dump({
            'w1': w1, 'w': w, 'bias': bias, 'beta_list': beta_list,
            'n_layers': n_layers, 'n_features': n_features, 'n_nodes': n_nodes
        }, f)
    return w1, w, bias, beta_list, n_layers, n_features, n_nodes

# Load or train model
if os.path.exists(WEIGHTS_FILE):
    with open(WEIGHTS_FILE, 'rb') as f:
        weights = pickle.load(f)
    w1 = weights['w1']
    w = weights['w']
    bias = weights['bias']
    beta_list = weights['beta_list']
    n_layers = weights['n_layers']
    n_features = weights['n_features']
    n_nodes = weights['n_nodes']
else:
    w1, w, bias, beta_list, n_layers, n_features, n_nodes = train_and_save_model()

# --- Prediction Function ---
def compute_additional_features(user_input):
    # user_input: [sleep_duration, step_count, resting_heart_rate, stress_level, sleep_onset_time, HR_day_avg, HR_sleep_min]
    sleep_duration, step_count, resting_heart_rate, stress_level, sleep_onset_time, HR_day_avg, HR_sleep_min = user_input
    # For new users, we can't compute rolling features, so set to mean or neutral values
    SRE = 0.0  # Could use dataset mean if desired
    PAI = 0.0
    HRSI = 0.0
    SDAS = max(0, 56 - sleep_duration*7)  # 7*8 - total sleep in a week
    SSR = 1.0 if stress_level > 0.7 else 0.0
    ARI = (HR_day_avg - HR_sleep_min) / HR_day_avg if HR_day_avg != 0 else 0.0
    return [sleep_duration, step_count, resting_heart_rate, stress_level, sleep_onset_time, HR_day_avg, HR_sleep_min, SRE, PAI, HRSI, SDAS, SSR, ARI]

def predict_anomaly(user_input):
    # user_input: list of 7 values in the order above
    x = np.array(compute_additional_features(user_input)).reshape(1, -1)
    # Forward pass through the trained model
    K1 = np.dot(x, w1)
    H1 = sigmoid(K1 + bias.T[0:1, :])
    H_list = [H1]
    for i in range(1, n_layers):
        prev_h = H_list[i-1]
        matrix = np.concatenate((prev_h, x), axis=1)
        K = np.dot(matrix, w[:, :, i-1])
        new_h = sigmoid(K + bias.T[i:i+1 , :])
        H_list.append(new_h)
    D_list = []
    D1 = np.concatenate((H_list[0], x), axis=1)
    D_list.append(D1)
    for i in range(1, n_layers):
        D_new = np.concatenate((H_list[i], H_list[i-1], x), axis=1)
        D_list.append(D_new)
    output_list = []
    for i in range(n_layers):
        output = np.dot(D_list[i], beta_list[i])
        output_list.append(output)
    sum_output = np.sum(output_list, axis=0)
    score = sum_output[0, 1] / n_layers  # Normalized score between 0 and 1
    # Define thresholds for categories
    if score < 0.33:
        return "null"
    elif score < 0.66:
        return "minor"
    else:
        return "major"

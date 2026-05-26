import sqlite3
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)

from helper.helper import mainDB, get_logging

logger = get_logging(Path(__file__).stem)

FEATURE_COLUMNS = [
    '3Day_Return', '10Day_Return', '14Day_Return', 'Momentum_Ratio',
    'MA10_slope_3', 'MA20_slope_5', 'MA_Ratio', 'Price_ROC',
    'RSI14', 'MACD', 'Signal_Line', 'range', 'Volatility_10',
    'ATR', 'ATR_Ratio', 'ATR_Spike',
    'Vol_Trend_5_20', 'Volume_Spike', 'Turnover_Spike', 'Trades_Spike', 'Volume_Price_Trend',
    'Delivery_Ratio', 'Delivery_Spike',
    'Gap', 'Close_Position', 'VWAP_Ratio'
]

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')


def load_dataset():
    with sqlite3.connect(mainDB) as conn:
        df = pd.read_sql_query("SELECT * FROM dataSetTable WHERE Result IS NOT NULL", conn)
    logger.info(f"Loaded {len(df)} rows from dataSetTable")
    return df


def prepare_data(df):
    df = df.sort_values('Date').reset_index(drop=True)

    X = df[FEATURE_COLUMNS].copy()
    y = df['Result'].astype(int)

    # Replace infinities and fill remaining NaNs with 0
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.fillna(0, inplace=True)

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    logger.info(f"Train class distribution: {dict(y_train.value_counts())}")
    logger.info(f"Test class distribution: {dict(y_test.value_counts())}")

    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train):
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1
    logger.info(f"scale_pos_weight: {scale_pos_weight:.4f}")

    base_model = XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1
    )

    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [100, 300, 500],
        'min_child_weight': [1, 3, 5],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
    }

    tscv = TimeSeriesSplit(n_splits=5)

    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=tscv,
        scoring='f1',
        n_jobs=-1,
        verbose=1,
        refit=True
    )

    logger.info("Starting GridSearchCV (this may take a while)...")
    grid_search.fit(X_train, y_train)

    logger.info(f"Best parameters: {grid_search.best_params_}")
    logger.info(f"Best CV F1 score: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_, grid_search.best_params_


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)

    logger.info("=" * 60)
    logger.info("MODEL EVALUATION RESULTS")
    logger.info("=" * 60)
    logger.info(f"Accuracy:  {acc:.4f}")
    logger.info(f"Precision: {prec:.4f}")
    logger.info(f"Recall:    {rec:.4f}")
    logger.info(f"F1 Score:  {f1:.4f}")
    logger.info(f"ROC-AUC:   {roc:.4f}")
    logger.info(f"Confusion Matrix:\n{cm}")
    logger.info(f"Classification Report:\n{report}")

    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1, 'roc_auc': roc}


def log_feature_importance(model):
    importance = model.feature_importances_
    feature_imp = sorted(
        zip(FEATURE_COLUMNS, importance), key=lambda x: x[1], reverse=True
    )
    logger.info("Feature Importance Ranking:")
    for rank, (feat, imp) in enumerate(feature_imp, 1):
        logger.info(f"  {rank:2d}. {feat:<25s} {imp:.4f}")


def save_model(model, best_params, metrics):
    os.makedirs(MODEL_DIR, exist_ok=True)

    model_path = os.path.join(MODEL_DIR, 'xgboost_nifty50.json')
    model.save_model(model_path)
    logger.info(f"Model saved to {model_path}")

    params_path = os.path.join(MODEL_DIR, 'best_params.json')
    output = {
        'best_params': best_params,
        'metrics': {k: round(v, 4) for k, v in metrics.items()}
    }
    with open(params_path, 'w') as f:
        json.dump(output, f, indent=2)
    logger.info(f"Best params and metrics saved to {params_path}")


def main():
    logger.info("=" * 60)
    logger.info("STARTING XGBOOST MODEL TRAINING")
    logger.info("=" * 60)

    df = load_dataset()
    X_train, X_test, y_train, y_test = prepare_data(df)
    model, best_params = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)
    log_feature_importance(model)
    save_model(model, best_params, metrics)

    logger.info("XGBoost training pipeline completed successfully.")



if __name__ == "__main__":
    main()

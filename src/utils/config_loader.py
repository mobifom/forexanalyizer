"""
Configuration Loader
Loads and manages application configuration
"""

import yaml
import os
from typing import Dict


def load_config(config_path: str = 'config/config.yaml') -> Dict:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_default_config() -> Dict:
    """
    Get default configuration if file not available

    Returns:
        Default configuration dictionary
    """
    return {
        'timeframes': ['1d', '4h', '1h', '15m'],
        'timeframe_weights': {
            '1d': 0.4,
            '4h': 0.3,
            '1h': 0.2,
            '15m': 0.1
        },
        'currency_pairs': ['EURUSD=X', 'GBPUSD=X'],
        'indicators': {
            'ma_periods': [20, 50, 200],
            'ema_periods': [12, 26, 50],
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'stochastic_k': 14,
            'stochastic_d': 3,
            'atr_period': 14,
            'bollinger_period': 20,
            'bollinger_std': 2
        },
        'confluence': {
            'min_timeframes_agree': 3,
            'min_confidence': 0.6
        },
        'ml_model': {
            'train_test_split': 0.2,
            'lookback_periods': 5,
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5
        },
        'risk_management': {
            'risk_per_trade': 0.02,
            'atr_multiplier': 2.0,
            'max_drawdown': 0.15,
            'min_risk_reward': 1.5
        },
        'data': {
            'historical_days': 365,
            'cache_enabled': True,
            'cache_duration_minutes': 60
        }
    }

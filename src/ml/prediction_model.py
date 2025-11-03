"""
Machine Learning Prediction Model
Binary/Ternary classification for BUY/SELL/HOLD signals
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging
import joblib
import os

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

logger = logging.getLogger(__name__)


class ForexMLModel:
    """Machine Learning model for forex prediction"""

    def __init__(self, config: Dict):
        """
        Initialize ML model

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.ml_config = config.get('ml_model', {})
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML model

        Args:
            df: DataFrame with technical indicators

        Returns:
            DataFrame with features
        """
        features = pd.DataFrame()

        # Price-based features
        if 'Close' in df.columns:
            features['price_change_pct'] = df['Close'].pct_change()
            features['price_change_5'] = df['Close'].pct_change(5)
            features['price_change_10'] = df['Close'].pct_change(10)

        # RSI
        if 'RSI' in df.columns:
            features['rsi'] = df['RSI']
            features['rsi_normalized'] = (df['RSI'] - 50) / 50  # Normalize around 50

        # MACD
        if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Hist']):
            features['macd'] = df['MACD']
            features['macd_signal'] = df['MACD_Signal']
            features['macd_hist'] = df['MACD_Hist']
            features['macd_cross'] = (df['MACD'] > df['MACD_Signal']).astype(int)

        # Moving Averages
        if all(col in df.columns for col in ['MA_20', 'MA_50']):
            features['ma_20_50_diff'] = (df['MA_20'] - df['MA_50']) / df['Close']
            features['price_above_ma20'] = (df['Close'] > df['MA_20']).astype(int)
            features['price_above_ma50'] = (df['Close'] > df['MA_50']).astype(int)

        if 'MA_200' in df.columns:
            features['price_above_ma200'] = (df['Close'] > df['MA_200']).astype(int)

        # Stochastic
        if all(col in df.columns for col in ['Stoch_K', 'Stoch_D']):
            features['stoch_k'] = df['Stoch_K']
            features['stoch_d'] = df['Stoch_D']
            features['stoch_cross'] = (df['Stoch_K'] > df['Stoch_D']).astype(int)

        # Bollinger Bands
        if all(col in df.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Width']):
            features['bb_position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
            features['bb_width'] = df['BB_Width'] / df['Close']

        # Volume
        if 'Volume' in df.columns and 'Volume_MA' in df.columns:
            features['volume_ratio'] = df['Volume'] / df['Volume_MA']

        # ATR (volatility)
        if 'ATR' in df.columns:
            features['atr_pct'] = df['ATR'] / df['Close']

        # Support/Resistance distance
        if 'Support_Distance' in df.columns:
            features['support_distance'] = df['Support_Distance']
        if 'Resistance_Distance' in df.columns:
            features['resistance_distance'] = df['Resistance_Distance']

        return features.fillna(0)

    def create_labels(self, df: pd.DataFrame, lookback: int = 5, threshold: float = 0.001) -> pd.Series:
        """
        Create labels for training (BUY=1, SELL=-1, HOLD=0)

        Args:
            df: DataFrame with price data
            lookback: Periods to look ahead for profit
            threshold: Minimum price change to classify as BUY/SELL (0.001 = 0.1%)

        Returns:
            Series with labels
        """
        # Look forward to see if price goes up or down
        future_return = df['Close'].shift(-lookback) / df['Close'] - 1

        labels = pd.Series(0, index=df.index)  # Default to HOLD

        # BUY if price goes up significantly
        labels[future_return > threshold] = 1

        # SELL if price goes down significantly
        labels[future_return < -threshold] = -1

        return labels

    def train(
        self,
        df: pd.DataFrame,
        save_path: str = 'models/forex_model.pkl'
    ) -> Dict:
        """
        Train the ML model

        Args:
            df: DataFrame with indicators
            save_path: Path to save the trained model

        Returns:
            Dictionary with training metrics
        """
        logger.info("Preparing training data...")

        # Prepare features and labels
        features = self.prepare_features(df)
        labels = self.create_labels(df, lookback=self.ml_config.get('lookback_periods', 5))

        # Remove rows with NaN
        valid_idx = ~(features.isna().any(axis=1) | labels.isna())
        features = features[valid_idx]
        labels = labels[valid_idx]

        if len(features) < 100:
            logger.error("Insufficient training data")
            return {'error': 'Insufficient training data'}

        # Store feature columns
        self.feature_columns = features.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features,
            labels,
            test_size=self.ml_config.get('train_test_split', 0.2),
            random_state=42,
            stratify=labels if len(np.unique(labels)) > 1 else None
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Handle class imbalance with SMOTE (if we have all 3 classes)
        if len(np.unique(y_train)) > 1:
            try:
                smote = SMOTE(random_state=42)
                X_train_scaled, y_train = smote.fit_resample(X_train_scaled, y_train)
                logger.info(f"Applied SMOTE: {len(y_train)} samples after resampling")
            except Exception as e:
                logger.warning(f"SMOTE failed: {e}, continuing without resampling")

        # Create ensemble model
        logger.info("Training ensemble model...")

        rf = RandomForestClassifier(
            n_estimators=self.ml_config.get('n_estimators', 100),
            max_depth=self.ml_config.get('max_depth', 10),
            min_samples_split=self.ml_config.get('min_samples_split', 5),
            random_state=42,
            n_jobs=-1
        )

        gb = GradientBoostingClassifier(
            n_estimators=self.ml_config.get('n_estimators', 100),
            max_depth=self.ml_config.get('max_depth', 10),
            random_state=42
        )

        # Voting classifier
        self.model = VotingClassifier(
            estimators=[('rf', rf), ('gb', gb)],
            voting='soft'
        )

        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)

        y_pred = self.model.predict(X_test_scaled)

        logger.info(f"Training accuracy: {train_score:.2%}")
        logger.info(f"Test accuracy: {test_score:.2%}")

        # Classification report
        class_names = ['SELL', 'HOLD', 'BUY'] if len(np.unique(y_test)) == 3 else None
        report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)

        # Save model
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, save_path)
        logger.info(f"Model saved to {save_path}")

        return {
            'train_score': train_score,
            'test_score': test_score,
            'classification_report': report,
            'feature_count': len(self.feature_columns)
        }

    def load(self, model_path: str = 'models/forex_model.pkl') -> bool:
        """
        Load a trained model

        Args:
            model_path: Path to the saved model

        Returns:
            True if successful
        """
        try:
            saved_data = joblib.load(model_path)
            self.model = saved_data['model']
            self.scaler = saved_data['scaler']
            self.feature_columns = saved_data['feature_columns']
            logger.info(f"Model loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def predict(self, df: pd.DataFrame) -> Dict:
        """
        Make prediction on new data

        Args:
            df: DataFrame with indicators

        Returns:
            Dictionary with prediction and confidence
        """
        if self.model is None:
            logger.error("Model not trained or loaded")
            return {'signal': 'HOLD', 'confidence': 0.0}

        # Prepare features
        features = self.prepare_features(df)

        # Ensure we have the same features as training
        for col in self.feature_columns:
            if col not in features.columns:
                features[col] = 0

        features = features[self.feature_columns]

        # Use only the last row for prediction
        X = features.iloc[[-1]].fillna(0)
        X_scaled = self.scaler.transform(X)

        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]

        # Map prediction to signal
        signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
        signal = signal_map.get(prediction, 'HOLD')

        # Confidence is the probability of the predicted class
        confidence = probabilities[prediction + 1]  # -1, 0, 1 -> index 0, 1, 2

        return {
            'signal': signal,
            'confidence': float(confidence),
            'probabilities': {
                'SELL': float(probabilities[0]),
                'HOLD': float(probabilities[1]) if len(probabilities) > 2 else 0.0,
                'BUY': float(probabilities[-1])
            }
        }


class EnsembleVoting:
    """Ensemble voting system combining multiple signals"""

    @staticmethod
    def vote(
        technical_signals: Dict[str, str],
        ml_prediction: Dict,
        weights: Dict[str, float] = None
    ) -> Dict:
        """
        Combine signals using weighted voting

        Args:
            technical_signals: Dictionary of technical indicator signals
            ml_prediction: ML model prediction dictionary
            weights: Weights for different signal sources

        Returns:
            Dictionary with final signal and confidence
        """
        if weights is None:
            weights = {
                'ml': 0.5,
                'technical': 0.5
            }

        # Count technical signals
        tech_buy = sum(1 for s in technical_signals.values() if s == 'BUY')
        tech_sell = sum(1 for s in technical_signals.values() if s == 'SELL')
        tech_total = len(technical_signals)

        # Technical consensus
        if tech_buy > tech_sell:
            tech_signal = 'BUY'
            tech_confidence = tech_buy / tech_total
        elif tech_sell > tech_buy:
            tech_signal = 'SELL'
            tech_confidence = tech_sell / tech_total
        else:
            tech_signal = 'HOLD'
            tech_confidence = 0.5

        # Combine with ML
        ml_signal = ml_prediction['signal']
        ml_confidence = ml_prediction['confidence']

        # Weighted voting
        buy_score = 0
        sell_score = 0

        if tech_signal == 'BUY':
            buy_score += weights['technical'] * tech_confidence
        elif tech_signal == 'SELL':
            sell_score += weights['technical'] * tech_confidence

        if ml_signal == 'BUY':
            buy_score += weights['ml'] * ml_confidence
        elif ml_signal == 'SELL':
            sell_score += weights['ml'] * ml_confidence

        # Final decision
        if buy_score > sell_score and buy_score > 0.5:
            final_signal = 'BUY'
            final_confidence = buy_score
        elif sell_score > buy_score and sell_score > 0.5:
            final_signal = 'SELL'
            final_confidence = sell_score
        else:
            final_signal = 'HOLD'
            final_confidence = 0.5

        return {
            'signal': final_signal,
            'confidence': final_confidence,
            'technical_signal': tech_signal,
            'technical_confidence': tech_confidence,
            'ml_signal': ml_signal,
            'ml_confidence': ml_confidence
        }

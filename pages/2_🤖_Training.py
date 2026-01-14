"""
ML Model Training Page
Train machine learning models on historical data
"""

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.forex_analyzer import ForexAnalyzer
from src.auth.authentication_db import AuthenticatorDB, Permissions

st.set_page_config(page_title="Model Training", page_icon="🤖", layout="wide")

# Check authentication with database
if 'auth' not in st.session_state:
    st.session_state.auth = AuthenticatorDB()

auth = st.session_state.auth

if not auth.is_authenticated():
    st.error("🔒 Please login first")
    st.info("Return to the main page to login")
    st.stop()

if not auth.has_permission(Permissions.TRAIN_MODEL):
    st.error("🔒 Model training requires admin privileges")
    st.info("Only administrators can train machine learning models")
    st.stop()

# Render user info in sidebar
auth.render_user_info()

st.title("🤖 ML Model Training")
st.markdown("Train machine learning models on historical forex and metals data")

# Initialize
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ForexAnalyzer()

# Sidebar
with st.sidebar:
    st.header("Training Settings")

    # Asset categories
    asset_category = st.selectbox(
        "Asset Category",
        ['Forex Pairs', 'Indices', 'Crypto', 'Precious Metals']
    )

    if asset_category == 'Forex Pairs':
        symbol = st.selectbox(
            "Select Forex Pair",
            ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X']
        )
    elif asset_category == 'Indices':
        symbol = st.selectbox(
            "Select Index",
            ['US30', 'US100'],
            format_func=lambda x: 'US30 (Dow Jones)' if x == 'US30' else 'US100 (NASDAQ 100)'
        )
    elif asset_category == 'Crypto':
        symbol = st.selectbox(
            "Select Cryptocurrency",
            ['BTC/USD', 'ETH/USD'],
            format_func=lambda x: 'Bitcoin' if x == 'BTC/USD' else 'Ethereum'
        )
    else:  # Precious Metals
        symbol = st.selectbox(
            "Select Metal",
            ['XAU_USD', 'XAG_USD'],
            format_func=lambda x: 'Gold Spot' if x == 'XAU_USD' else 'Silver Spot'
        )

    st.caption(f"Training model for: {symbol}")

    st.divider()

    st.markdown("**Model Parameters**")
    st.info("Using default parameters from config. Advanced settings coming soon!")

    st.divider()

    save_path = st.text_input(
        "Model Save Path",
        "models/forex_model.pkl"
    )

    train_button = st.button("🚀 Start Training", type="primary", use_container_width=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Training Information")

    st.markdown("""
    ### What is ML Training?

    The machine learning model learns from historical price patterns to predict future movements.

    **Training Process:**
    1. Fetches historical data for the selected symbol
    2. Calculates technical indicators
    3. Prepares features from indicators
    4. Creates labels based on future price movements
    5. Trains ensemble model (Random Forest + Gradient Boosting)
    6. Evaluates performance on test data
    7. Saves trained model for future use

    **What You'll Get:**
    - Trained model saved to disk
    - Training and testing accuracy
    - Classification report
    - Feature importance
    """)

with col2:
    st.subheader("Tips")

    st.info("""
    **Best Practices:**

    - Train on the symbol you'll be trading most
    - Retrain weekly for best results
    - Higher accuracy on daily timeframe
    - EURUSD typically has best data
    - Gold/Silver need more training data
    """)

    st.warning("""
    **Note:**

    Training can take 1-5 minutes depending on data size
    """)

# Training section
if train_button:
    st.divider()
    st.subheader(f"Training Model on {symbol}")

    # Create status containers
    status_container = st.container()
    progress_bar = st.progress(0)

    with status_container:
        st.info(f"⏳ Fetching historical data for {symbol}...")
        progress_bar.progress(10)

    try:
        # Train the model
        with st.spinner("Training in progress... This may take a few minutes."):
            results = st.session_state.analyzer.train_model(
                symbol=symbol,
                save_path=save_path
            )

            progress_bar.progress(100)

        if results and 'error' not in results:
            st.success("✅ Training Complete!")

            # Display results
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Training Accuracy",
                    f"{results['train_score']:.2%}",
                    help="Accuracy on training data"
                )

            with col2:
                st.metric(
                    "Test Accuracy",
                    f"{results['test_score']:.2%}",
                    help="Accuracy on held-out test data"
                )

            st.metric("Features Used", results['feature_count'])

            # Classification report
            if 'classification_report' in results:
                st.subheader("Classification Report")

                report = results['classification_report']

                # Create DataFrame from report
                import pandas as pd

                report_data = []
                for class_name, metrics in report.items():
                    if isinstance(metrics, dict):
                        report_data.append({
                            'Class': class_name,
                            'Precision': metrics.get('precision', 0),
                            'Recall': metrics.get('recall', 0),
                            'F1-Score': metrics.get('f1-score', 0),
                            'Support': metrics.get('support', 0)
                        })

                if report_data:
                    df = pd.DataFrame(report_data)
                    st.dataframe(
                        df.style.format({
                            'Precision': '{:.2%}',
                            'Recall': '{:.2%}',
                            'F1-Score': '{:.2%}',
                            'Support': '{:.0f}'
                        }),
                        use_container_width=True
                    )

            st.success(f"Model saved to: `{save_path}`")

            st.markdown("""
            ### Next Steps

            1. ✅ Model is trained and saved
            2. Go back to main page to analyze with ML enabled
            3. The model will be automatically loaded
            4. Retrain periodically for best results
            """)

        else:
            st.error("❌ Training failed. Check the logs for details.")
            if results:
                st.error(f"Error: {results.get('error', 'Unknown error')}")

    except Exception as e:
        st.error(f"❌ Training Error: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())

else:
    st.info("👈 Select a symbol and click **Start Training** to begin")

    # Show current model status
    st.divider()
    st.subheader("Current Model Status")

    model_path = "models/forex_model.pkl"
    if os.path.exists(model_path):
        import datetime
        mod_time = os.path.getmtime(model_path)
        mod_datetime = datetime.datetime.fromtimestamp(mod_time)

        st.success(f"✅ Model exists: `{model_path}`")
        st.info(f"Last trained: {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

        col1, col2 = st.columns(2)
        with col1:
            file_size = os.path.getsize(model_path) / 1024  # KB
            st.metric("Model Size", f"{file_size:.1f} KB")

        with col2:
            days_old = (datetime.datetime.now() - mod_datetime).days
            st.metric("Days Old", days_old)

            if days_old > 7:
                st.warning("⚠️ Model is more than 7 days old. Consider retraining!")
    else:
        st.warning("⚠️ No trained model found")
        st.info("Train a model to enable ML predictions in the main analysis")

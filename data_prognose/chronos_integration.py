"""
Chronos Forecasting Integration for Trading Agent
Amazon's foundation model for time series prediction
"""

import torch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def setup_chronos():
    """
    Complete setup guide for Chronos
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          CHRONOS SETUP GUIDE                              ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Chronos is Amazon's pre-trained foundation model for time series.
    
    Installation:
    
    1. Install package:
       pip install chronos-forecasting
    
    2. Install dependencies:
       pip install torch pandas numpy matplotlib
    
    3. Models available on HuggingFace:
       - chronos-t5-tiny   (8M params, fastest)
       - chronos-t5-mini   (20M params)
       - chronos-t5-small  (46M params)
       - chronos-t5-base   (200M params, RECOMMENDED)
       - chronos-t5-large  (710M params, best accuracy)
    
    4. Hardware Requirements:
       - tiny/mini: CPU only, 4GB RAM
       - small: CPU or GPU, 8GB RAM
       - base: GPU recommended, 16GB RAM
       - large: GPU required, 32GB RAM
    """)


# ===== OPTION 1: LOCAL INFERENCE =====

def forecast_with_chronos_local(
    historical_prices: list,
    prediction_length: int = 24,
    model_size: str = "base"
):
    """
    Run Chronos locally for time series forecasting
    
    Args:
        historical_prices: List of historical closing prices
        prediction_length: How many steps to forecast
        model_size: tiny, mini, small, base, or large
    
    Returns:
        Dict with predictions and confidence intervals
    """
    try:
        from chronos import ChronosPipeline
        
        # Load pre-trained model
        model_name = f"amazon/chronos-t5-{model_size}"
        
        print(f"📥 Loading {model_name}...")
        print("(First run will download model from HuggingFace)")
        
        pipeline = ChronosPipeline.from_pretrained(
            model_name,
            device_map="auto",  # Automatically use GPU if available
            torch_dtype=torch.bfloat16,
        )
        
        # Prepare data
        context = torch.tensor(historical_prices)
        
        print(f"🔮 Generating forecast for {prediction_length} periods...")
        
        # Generate forecast
        forecast = pipeline.predict(
            context,
            prediction_length=prediction_length,
            num_samples=100,  # Generate 100 samples for confidence intervals
        )
        
        # Calculate statistics
        forecast_mean = forecast.mean(dim=0).numpy()
        forecast_median = forecast.median(dim=0).values.numpy()
        forecast_std = forecast.std(dim=0).numpy()
        
        # Confidence intervals (80% and 95%)
        forecast_q10 = forecast.quantile(0.10, dim=0).numpy()
        forecast_q90 = forecast.quantile(0.90, dim=0).numpy()
        forecast_q05 = forecast.quantile(0.05, dim=0).numpy()
        forecast_q95 = forecast.quantile(0.95, dim=0).numpy()
        
        return {
            'mean': forecast_mean.tolist(),
            'median': forecast_median.tolist(),
            'std': forecast_std.tolist(),
            'lower_80': forecast_q10.tolist(),
            'upper_80': forecast_q90.tolist(),
            'lower_95': forecast_q05.tolist(),
            'upper_95': forecast_q95.tolist(),
            'prediction_length': prediction_length,
            'model': model_name
        }
        
    except ImportError:
        print("❌ chronos-forecasting not installed!")
        print("   Install: pip install chronos-forecasting")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ===== OPTION 2: CLOUD-BASED (HuggingFace Inference API) =====

def forecast_with_chronos_cloud(
    historical_prices: list,
    prediction_length: int = 24,
    api_token: str = None,
    model_size: str = "base"
):
    """
    Use HuggingFace Inference API for Chronos (no local GPU needed)
    
    Args:
        historical_prices: Historical data
        prediction_length: Forecast horizon
        api_token: HuggingFace API token
        model_size: Model size
    
    Returns:
        Forecast results
    """
    import requests
    import json
    
    if not api_token:
        print("❌ Need HuggingFace API token!")
        print("   Get it from: https://huggingface.co/settings/tokens")
        return None
    
    model_name = f"amazon/chronos-t5-{model_size}"
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    headers = {"Authorization": f"Bearer {api_token}"}
    
    payload = {
        "inputs": historical_prices,
        "parameters": {
            "prediction_length": prediction_length
        }
    }
    
    print(f"☁️  Calling HuggingFace API for {model_name}...")
    
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        return None


# ===== OPTION 3: AWS SageMaker (Enterprise) =====

def deploy_chronos_sagemaker():
    """
    Guide for deploying Chronos on AWS SageMaker
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║       CHRONOS ON AWS SAGEMAKER                            ║
    ╚═══════════════════════════════════════════════════════════╝
    
    For production-grade deployment:
    
    1. Setup SageMaker:
       - Create SageMaker notebook instance
       - Add HuggingFace Deep Learning Container
    
    2. Deploy model:
       ```python
       from sagemaker.huggingface import HuggingFaceModel
       
       model = HuggingFaceModel(
           model_data="s3://your-bucket/chronos-model/",
           role=role,
           transformers_version="4.26",
           pytorch_version="1.13",
           py_version="py39",
       )
       
       predictor = model.deploy(
           initial_instance_count=1,
           instance_type="ml.g4dn.xlarge"
       )
       ```
    
    3. Cost estimate:
       - ml.g4dn.xlarge: ~$0.70/hour
       - ~$500/month for 24/7 deployment
    
    Benefits:
    - Auto-scaling
    - Managed infrastructure
    - High availability
    - Enterprise support
    """)


# ===== PRACTICAL EXAMPLE FOR TRADING =====

def trading_forecast_chronos(symbol: str, timeframe: str = "1h"):
    """
    Complete example: Forecast crypto prices using Chronos
    """
    print(f"\n{'='*60}")
    print(f"📈 Trading Forecast with Chronos")
    print(f"   Symbol: {symbol}")
    print(f"   Timeframe: {timeframe}")
    print(f"{'='*60}\n")
    
    # 1. Get historical data (mock for demo)
    print("📊 Step 1: Collecting historical data...")
    
    # In production: use CCXT
    # exchange = ccxt.binance()
    # ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=500)
    
    # For demo: generate mock data
    np.random.seed(42)
    base_price = 45000
    num_periods = 168  # 1 week of hourly data
    
    trend = np.linspace(0, 500, num_periods)
    noise = np.random.randn(num_periods) * 500
    seasonal = 300 * np.sin(np.linspace(0, 4*np.pi, num_periods))
    
    prices = base_price + trend + noise + seasonal
    
    print(f"✅ Loaded {len(prices)} historical records")
    print(f"   Latest price: ${prices[-1]:,.2f}")
    
    # 2. Forecast with Chronos
    print("\n🔮 Step 2: Generating forecast...")
    
    forecast = forecast_with_chronos_local(
        historical_prices=prices.tolist(),
        prediction_length=24,  # Next 24 hours
        model_size="base"  # Change to "tiny" for faster testing
    )
    
    if forecast:
        print("\n✅ Forecast generated!")
        
        # 3. Analyze results
        print("\n📊 Step 3: Analysis")
        
        current_price = prices[-1]
        predicted_price_24h = forecast['mean'][-1]
        change_percent = ((predicted_price_24h - current_price) / current_price) * 100
        
        print(f"\n   Current Price: ${current_price:,.2f}")
        print(f"   Predicted (24h): ${predicted_price_24h:,.2f}")
        print(f"   Expected Change: {change_percent:+.2f}%")
        
        print(f"\n   Confidence Intervals (95%):")
        print(f"   Lower Bound: ${forecast['lower_95'][-1]:,.2f}")
        print(f"   Upper Bound: ${forecast['upper_95'][-1]:,.2f}")
        
        # 4. Trading signals
        print("\n🎯 Step 4: Trading Signals")
        
        if change_percent > 2:
            signal = "🟢 BULLISH"
            action = "Consider BUY"
        elif change_percent < -2:
            signal = "🔴 BEARISH"
            action = "Consider SELL"
        else:
            signal = "🟡 NEUTRAL"
            action = "HOLD"
        
        print(f"   Signal: {signal}")
        print(f"   Action: {action}")
        
        # Return structured data
        return {
            'current_price': current_price,
            'forecast_24h': predicted_price_24h,
            'change_percent': change_percent,
            'confidence_95_lower': forecast['lower_95'][-1],
            'confidence_95_upper': forecast['upper_95'][-1],
            'signal': signal,
            'action': action,
            'full_forecast': forecast
        }
    
    return None


# ===== INTEGRATION WITH TRADING AGENT =====

def chronos_prediction_node(state):
    """
    LangGraph node for price prediction using Chronos
    Drop-in replacement for the prediction node in app.py
    """
    print("--- CHRONOS PREDICTION ENGINE ---")
    
    # Get historical data from state
    market_data = state.get('market_data', {})
    symbol = state.get('symbol', 'BTC/USDT')
    
    # In production: get real prices
    # For now: simulate
    from utils import generate_mock_ohlcv
    df = generate_mock_ohlcv(symbol, '1h', num_candles=168)
    prices = df['close'].tolist()
    
    # Run Chronos forecast
    forecast = forecast_with_chronos_local(
        historical_prices=prices,
        prediction_length=24,
        model_size="base"
    )
    
    if forecast:
        current_price = prices[-1]
        predicted_price = forecast['mean'][-1]
        
        # Determine trend
        change_pct = ((predicted_price - current_price) / current_price) * 100
        
        if change_pct > 1:
            trend = "BULLISH"
        elif change_pct < -1:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"
        
        return {
            "price_prediction": {
                "model": "Chronos-T5-Base",
                "current_price": current_price,
                "predicted_price": predicted_price,
                "predicted_change": change_pct,
                "confidence_interval_95": [
                    forecast['lower_95'][-1],
                    forecast['upper_95'][-1]
                ],
                "trend": trend
            },
            "trend_prediction": f"""Chronos Forecast Analysis:

Current Price: ${current_price:,.2f}
Predicted Price (24h): ${predicted_price:,.2f}
Expected Change: {change_pct:+.2f}%

95% Confidence Interval:
${forecast['lower_95'][-1]:,.2f} - ${forecast['upper_95'][-1]:,.2f}

Trend: {trend}

The model analyzed 168 hours of historical data and generated
100 probabilistic scenarios. The prediction suggests a {trend.lower()}
bias for the next 24 hours with {abs(change_pct):.1f}% expected movement.
"""
        }
    
    # Fallback if Chronos fails
    return {
        "price_prediction": {
            "model": "Fallback",
            "predicted_price": market_data.get('current_price', 0),
            "trend": "NEUTRAL"
        },
        "trend_prediction": "Chronos model unavailable, using fallback."
    }


# ===== COMPARISON: Chronos vs Other Models =====

def compare_forecast_models(prices: list):
    """
    Compare Chronos with Prophet and simple baselines
    """
    print("\n" + "="*60)
    print("🏆 MODEL COMPARISON")
    print("="*60)
    
    prediction_horizon = 24
    
    # 1. Chronos
    print("\n1️⃣  Chronos (Amazon Foundation Model)")
    chronos_result = forecast_with_chronos_local(prices, prediction_horizon, "base")
    if chronos_result:
        print(f"   ✅ Predicted: ${chronos_result['mean'][-1]:,.2f}")
        print(f"   📊 Model: Pre-trained foundation model")
    
    # 2. Prophet
    print("\n2️⃣  Prophet (Meta)")
    try:
        from prophet import Prophet
        
        df = pd.DataFrame({
            'ds': pd.date_range(start='2024-01-01', periods=len(prices), freq='H'),
            'y': prices
        })
        
        model = Prophet(daily_seasonality=True)
        model.fit(df)
        
        future = model.make_future_dataframe(periods=prediction_horizon, freq='H')
        forecast = model.predict(future)
        
        prophet_pred = forecast['yhat'].iloc[-1]
        print(f"   ✅ Predicted: ${prophet_pred:,.2f}")
        print(f"   📊 Model: Additive decomposition")
        
    except Exception as e:
        print(f"   ❌ Prophet failed: {e}")
    
    # 3. Simple Moving Average
    print("\n3️⃣  Simple Moving Average (Baseline)")
    sma = np.mean(prices[-24:])
    print(f"   ✅ Predicted: ${sma:,.2f}")
    print(f"   📊 Model: 24-period average")
    
    print("\n" + "="*60)


# ===== MAIN DEMO =====

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║            CHRONOS TRADING FORECASTING DEMO               ║
    ║                                                           ║
    ║  Amazon's Foundation Model for Time Series Prediction     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check installation
    try:
        from chronos import ChronosPipeline
        print("✅ Chronos is installed!\n")
    except ImportError:
        print("⚠️  Chronos not installed.")
        print("\nInstall with: pip install chronos-forecasting\n")
        setup_chronos()
        exit()
    
    # Menu
    print("\nChoose option:")
    print("1. Run local forecast (requires GPU recommended)")
    print("2. Setup guide")
    print("3. Compare models")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        # Run forecast
        result = trading_forecast_chronos("BTC/USDT", "1h")
        
        if result:
            print("\n" + "="*60)
            print("📋 FINAL RECOMMENDATION")
            print("="*60)
            print(f"\n{result['action']}")
            print(f"Confidence interval suggests price range:")
            print(f"${result['confidence_95_lower']:,.2f} - ${result['confidence_95_upper']:,.2f}")
            
    elif choice == "2":
        setup_chronos()
        
    elif choice == "3":
        # Generate sample data
        np.random.seed(42)
        prices = 45000 + np.cumsum(np.random.randn(168) * 100)
        compare_forecast_models(prices.tolist())
    
    print("\n✅ Done!\n")

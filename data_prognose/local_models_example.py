"""
Trading Agent with LOCAL MODELS (Ollama)
Example configuration using Qwen2.5-14B instead of OpenRouter
"""

import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage

load_dotenv()

# --- LOCAL MODEL CONFIGURATION ---

def get_local_llm(temperature: float = 0.3, model: str = "qwen2.5:14b"):
    """
    Get local LLM via Ollama
    
    Models to try:
    - qwen2.5:14b (BEST for trading analysis)
    - qwen2.5:7b (faster, less capable)
    - deepseek-coder:33b (good for technical analysis)
    - llama3.1:8b (lightweight option)
    - mistral:7b (balanced)
    
    Install: ollama pull qwen2.5:14b
    """
    return Ollama(
        model=model,
        temperature=temperature,
        # Ollama-specific parameters
        num_predict=1024,  # max tokens to generate
        top_k=40,
        top_p=0.9,
        repeat_penalty=1.1,
        # Optional: custom base URL if not default
        # base_url="http://localhost:11434"
    )


# --- EXAMPLE NODE WITH LOCAL MODEL ---

def technical_analysis_local(symbol: str, indicators: dict) -> str:
    """
    Technical analysis using local Qwen2.5 model
    """
    llm = get_local_llm(temperature=0.2)
    
    prompt = f"""You are a Professional Technical Analyst.

Asset: {symbol}

Technical Indicators:
- RSI(14): {indicators['RSI_14']}
- MACD: {indicators['MACD']}
- Price: ${indicators['current_price']:,.2f}

Provide technical analysis with:
1. Trend direction
2. Support/Resistance levels
3. Entry/Exit recommendations

Be concise and actionable."""

    response = llm.invoke(prompt)
    return response


# --- FORECASTING WITH LOCAL MODELS ---

def forecast_with_prophet(prices: list, periods: int = 24):
    """
    Local forecasting with Prophet (Meta)
    No API needed - runs completely offline
    """
    from prophet import Prophet
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Prepare data
    dates = [datetime.now() - timedelta(hours=i) for i in range(len(prices)-1, -1, -1)]
    df = pd.DataFrame({
        'ds': dates,
        'y': prices
    })
    
    # Initialize and fit
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        changepoint_prior_scale=0.05,
        interval_width=0.95
    )
    
    model.fit(df)
    
    # Forecast
    future = model.make_future_dataframe(periods=periods, freq='H')
    forecast = model.predict(future)
    
    return {
        'predicted_price': forecast['yhat'].iloc[-1],
        'lower_bound': forecast['yhat_lower'].iloc[-1],
        'upper_bound': forecast['yhat_upper'].iloc[-1],
        'trend': forecast['trend'].iloc[-1]
    }


def forecast_with_nbeats(df: 'pd.DataFrame', horizon: int = 24):
    """
    Advanced neural forecasting with N-BEATS
    Requires: pip install neuralforecast
    """
    from neuralforecast import NeuralForecast
    from neuralforecast.models import NBEATS
    
    # Initialize model
    models = [
        NBEATS(
            input_size=168,  # 1 week of hourly data
            h=horizon,       # forecast horizon
            max_steps=500,   # training steps
            scaler_type='robust',
            random_seed=42
        )
    ]
    
    nf = NeuralForecast(models=models, freq='H')
    
    # Fit and predict
    nf.fit(df=df)
    forecasts = nf.predict()
    
    return forecasts


# --- SENTIMENT WITH LOCAL MODEL ---

def analyze_sentiment_local(news_text: str) -> dict:
    """
    Sentiment analysis using local FinBERT model
    No API calls - 100% offline
    """
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    
    # Load model (cached after first use)
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    
    # Analyze
    inputs = tokenizer(news_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # Extract scores
    scores = predictions[0].tolist()
    labels = ['negative', 'neutral', 'positive']
    
    sentiment_dict = dict(zip(labels, scores))
    dominant = labels[scores.index(max(scores))]
    
    return {
        'sentiment': dominant,
        'confidence': max(scores),
        'scores': sentiment_dict
    }


# --- COMPLETE LOCAL PIPELINE EXAMPLE ---

def run_local_trading_analysis(symbol: str, timeframe: str):
    """
    Complete trading analysis using ONLY local models
    No external API calls (except for market data)
    """
    
    print("🤖 Running FULLY LOCAL Trading Analysis")
    print("=" * 60)
    
    # 1. Get market data (would use CCXT in production)
    from utils import generate_mock_ohlcv
    df = generate_mock_ohlcv(symbol, timeframe, num_candles=200)
    
    prices = df['close'].tolist()
    current_price = prices[-1]
    
    print(f"\n📊 Symbol: {symbol}")
    print(f"💰 Current Price: ${current_price:,.2f}")
    
    # 2. Technical Analysis (Local LLM)
    print("\n🔍 Running Technical Analysis (Qwen2.5-14B)...")
    
    indicators = {
        'RSI_14': 55.3,
        'MACD': 120.5,
        'current_price': current_price
    }
    
    tech_analysis = technical_analysis_local(symbol, indicators)
    print(f"✅ Technical: {tech_analysis[:200]}...")
    
    # 3. Price Forecast (Local Prophet)
    print("\n📈 Forecasting with Prophet (Local)...")
    
    forecast = forecast_with_prophet(prices, periods=24)
    print(f"✅ Predicted Price (24h): ${forecast['predicted_price']:,.2f}")
    print(f"   Range: ${forecast['lower_bound']:,.2f} - ${forecast['upper_bound']:,.2f}")
    
    # 4. Sentiment Analysis (Local FinBERT)
    print("\n📰 Analyzing Sentiment (FinBERT Local)...")
    
    sample_news = "Bitcoin ETF sees strong inflows amid positive market sentiment"
    sentiment = analyze_sentiment_local(sample_news)
    print(f"✅ Sentiment: {sentiment['sentiment'].upper()} (confidence: {sentiment['confidence']:.2%})")
    
    # 5. Final Decision (Local LLM)
    print("\n🎯 Making Decision (Qwen2.5-14B)...")
    
    llm = get_local_llm(temperature=0.0)
    
    decision_prompt = f"""Based on the analysis:
    
Technical: {tech_analysis[:300]}
Predicted Price: ${forecast['predicted_price']:,.2f}
Current Price: ${current_price:,.2f}
Sentiment: {sentiment['sentiment']}

Make a trading decision: BUY, SELL, or HOLD?
Provide brief reasoning.

Format:
DECISION: [choice]
REASONING: [explanation]"""

    decision = llm.invoke(decision_prompt)
    print(f"✅ {decision}")
    
    print("\n" + "=" * 60)
    print("🎉 Analysis Complete - All models ran LOCALLY!")
    print("💡 No API costs incurred")
    print("🔒 All data stayed on your machine")
    
    return {
        'technical': tech_analysis,
        'forecast': forecast,
        'sentiment': sentiment,
        'decision': decision
    }


# --- BENCHMARKING LOCAL VS API ---

def benchmark_local_vs_api():
    """
    Compare local model vs API performance
    """
    import time
    
    test_prompt = "Analyze BTC/USDT with RSI=55, MACD=positive, bullish trend."
    
    # Test Local (Ollama)
    print("Testing LOCAL model (Qwen2.5-14B via Ollama)...")
    start = time.time()
    local_llm = get_local_llm()
    local_response = local_llm.invoke(test_prompt)
    local_time = time.time() - start
    
    print(f"✅ Local: {local_time:.2f}s")
    print(f"   Response: {local_response[:100]}...")
    
    # Test API (if configured)
    if os.getenv("OPENAI_API_KEY"):
        print("\nTesting API model (DeepSeek via OpenRouter)...")
        from langchain_openai import ChatOpenAI
        
        start = time.time()
        api_llm = ChatOpenAI(
            model="deepseek/deepseek-chat",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        api_response = api_llm.invoke(test_prompt)
        api_time = time.time() - start
        
        print(f"✅ API: {api_time:.2f}s")
        print(f"   Response: {api_response.content[:100]}...")
        
        # Compare
        print("\n📊 Comparison:")
        print(f"   Speed difference: {abs(local_time - api_time):.2f}s")
        if local_time < api_time:
            print(f"   ⚡ Local is {((api_time / local_time) - 1) * 100:.1f}% faster!")
        else:
            print(f"   🌐 API is {((local_time / api_time) - 1) * 100:.1f}% faster")


# --- INSTALLATION GUIDE ---

def check_local_setup():
    """
    Check if local models are properly installed
    """
    print("🔍 Checking Local Model Setup...")
    print("=" * 60)
    
    # Check Ollama
    try:
        llm = Ollama(model="qwen2.5:14b")
        llm.invoke("test")
        print("✅ Ollama + Qwen2.5-14B: READY")
    except Exception as e:
        print("❌ Ollama not ready!")
        print("   Install: Download from ollama.ai")
        print("   Then run: ollama pull qwen2.5:14b")
    
    # Check Prophet
    try:
        from prophet import Prophet
        print("✅ Prophet: Installed")
    except ImportError:
        print("❌ Prophet not installed")
        print("   Install: pip install prophet")
    
    # Check NeuralForecast
    try:
        from neuralforecast import NeuralForecast
        print("✅ NeuralForecast: Installed")
    except ImportError:
        print("⚠️  NeuralForecast not installed (optional)")
        print("   Install: pip install neuralforecast")
    
    # Check Transformers (for FinBERT)
    try:
        from transformers import AutoTokenizer
        print("✅ Transformers: Installed")
    except ImportError:
        print("❌ Transformers not installed")
        print("   Install: pip install transformers")
    
    print("=" * 60)


if __name__ == "__main__":
    # Check setup
    check_local_setup()
    
    print("\n" + "=" * 60)
    choice = input("\nRun full local analysis? (y/n): ")
    
    if choice.lower() == 'y':
        # Run complete local analysis
        results = run_local_trading_analysis("BTC/USDT", "4h")
    
    print("\n" + "=" * 60)
    benchmark = input("\nRun speed benchmark? (y/n): ")
    
    if benchmark.lower() == 'y':
        benchmark_local_vs_api()

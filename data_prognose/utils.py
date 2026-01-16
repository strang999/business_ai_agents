"""
Utility functions for Trading Agent
"""

from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, List


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index
    
    Args:
        prices: List of closing prices
        period: RSI period (default 14)
    
    Returns:
        RSI value (0-100)
    """
    if len(prices) < period + 1:
        return 50.0  # Neutral if not enough data
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_macd(prices: List[float], 
                   fast_period: int = 12, 
                   slow_period: int = 26, 
                   signal_period: int = 9) -> Dict[str, float]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: List of closing prices
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
    
    Returns:
        Dict with MACD, signal, and histogram
    """
    if len(prices) < slow_period:
        return {"macd": 0, "signal": 0, "histogram": 0}
    
    # Simple implementation - use ta-lib or pandas for production
    ema_fast = sum(prices[-fast_period:]) / fast_period
    ema_slow = sum(prices[-slow_period:]) / slow_period
    
    macd = ema_fast - ema_slow
    signal = macd * 0.9  # Simplified
    histogram = macd - signal
    
    return {
        "macd": round(macd, 2),
        "signal": round(signal, 2),
        "histogram": round(histogram, 2)
    }


def calculate_bollinger_bands(prices: List[float], 
                               period: int = 20, 
                               std_dev: int = 2) -> Dict[str, float]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: List of closing prices
        period: Moving average period
        std_dev: Number of standard deviations
    
    Returns:
        Dict with upper, middle, and lower bands
    """
    if len(prices) < period:
        return {"upper": 0, "middle": 0, "lower": 0}
    
    recent_prices = prices[-period:]
    middle = sum(recent_prices) / period
    
    variance = sum((p - middle) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    return {
        "upper": round(upper, 2),
        "middle": round(middle, 2),
        "lower": round(lower, 2)
    }


def detect_support_resistance(prices: List[float], 
                               highs: List[float], 
                               lows: List[float]) -> Dict[str, float]:
    """
    Simple support and resistance detection
    
    Args:
        prices: List of closing prices
        highs: List of high prices
        lows: List of low prices
    
    Returns:
        Dict with support and resistance levels
    """
    if len(prices) < 20:
        current = prices[-1] if prices else 0
        return {
            "support": current * 0.95,
            "resistance": current * 1.05
        }
    
    # Simple approach: recent highs and lows
    recent_highs = highs[-50:] if len(highs) >= 50 else highs
    recent_lows = lows[-50:] if len(lows) >= 50 else lows
    
    resistance = max(recent_highs)
    support = min(recent_lows)
    
    return {
        "support": round(support, 2),
        "resistance": round(resistance, 2)
    }


def calculate_position_size(account_balance: float,
                            risk_percentage: float,
                            entry_price: float,
                            stop_loss: float) -> Dict[str, Any]:
    """
    Calculate position size based on risk management
    
    Args:
        account_balance: Total account balance
        risk_percentage: Risk per trade (e.g., 2 for 2%)
        entry_price: Entry price
        stop_loss: Stop loss price
    
    Returns:
        Dict with position size and risk details
    """
    risk_amount = account_balance * (risk_percentage / 100)
    risk_per_unit = abs(entry_price - stop_loss)
    
    if risk_per_unit == 0:
        return {
            "position_size": 0,
            "units": 0,
            "risk_amount": 0
        }
    
    units = risk_amount / risk_per_unit
    position_value = units * entry_price
    
    return {
        "position_size": round(position_value, 2),
        "units": round(units, 4),
        "risk_amount": round(risk_amount, 2),
        "risk_percentage": risk_percentage
    }


def calculate_risk_reward_ratio(entry_price: float,
                                 stop_loss: float,
                                 take_profit: float) -> float:
    """
    Calculate risk/reward ratio
    
    Args:
        entry_price: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
    
    Returns:
        Risk/reward ratio
    """
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    
    if risk == 0:
        return 0
    
    return round(reward / risk, 2)


def format_price(price: float, decimals: int = 2) -> str:
    """Format price with appropriate decimals and commas"""
    return f"${price:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage with sign"""
    return f"{value:+.{decimals}f}%"


def get_timeframe_minutes(timeframe: str) -> int:
    """Convert timeframe string to minutes"""
    multipliers = {
        'm': 1,
        'h': 60,
        'd': 1440,
        'w': 10080
    }
    
    try:
        value = int(timeframe[:-1])
        unit = timeframe[-1]
        return value * multipliers.get(unit, 1)
    except:
        return 60  # Default to 1 hour


def generate_timestamp() -> str:
    """Generate ISO format timestamp"""
    return datetime.now().isoformat()


def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    return '/' in symbol and len(symbol.split('/')) == 2


def validate_timeframe(timeframe: str) -> bool:
    """Validate timeframe format"""
    valid_units = ['m', 'h', 'd', 'w']
    if not timeframe or len(timeframe) < 2:
        return False
    
    try:
        value = int(timeframe[:-1])
        unit = timeframe[-1]
        return unit in valid_units and value > 0
    except:
        return False


# Mock data generators (for MVP testing)

def generate_mock_ohlcv(symbol: str, 
                        timeframe: str, 
                        num_candles: int = 100) -> pd.DataFrame:
    """
    Generate mock OHLCV data for testing
    In production: Replace with actual CCXT calls
    """
    import numpy as np
    
    # Base price
    base_price = {
        'BTC/USDT': 45000,
        'ETH/USDT': 2500,
        'SOL/USDT': 100,
        'BNB/USDT': 350
    }.get(symbol, 1000)
    
    # Generate random walk
    np.random.seed(42)
    returns = np.random.randn(num_candles) * 0.02  # 2% volatility
    prices = base_price * (1 + returns).cumprod()
    
    data = {
        'timestamp': [datetime.now() - timedelta(minutes=i*get_timeframe_minutes(timeframe)) 
                      for i in range(num_candles-1, -1, -1)],
        'open': prices,
        'high': prices * (1 + abs(np.random.randn(num_candles) * 0.01)),
        'low': prices * (1 - abs(np.random.randn(num_candles) * 0.01)),
        'close': prices,
        'volume': np.random.randint(1000000, 50000000, num_candles)
    }
    
    return pd.DataFrame(data)


def generate_mock_sentiment() -> Dict[str, Any]:
    """Generate mock sentiment data"""
    return {
        "news_sentiment": "neutral",
        "social_sentiment": "bullish",
        "fear_greed_index": 65,
        "sentiment_score": 0.15,
        "sources": ["Twitter", "Reddit", "News"]
    }


if __name__ == "__main__":
    # Test utilities
    test_prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
    
    print("RSI:", calculate_rsi(test_prices))
    print("MACD:", calculate_macd(test_prices))
    print("Bollinger Bands:", calculate_bollinger_bands(test_prices))
    
    print("\nPosition Size:", calculate_position_size(10000, 2, 45000, 44000))
    print("Risk/Reward:", calculate_risk_reward_ratio(45000, 44000, 47000))

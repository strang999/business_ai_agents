"""
Trading Prediction Agent with LangGraph
Professional multi-step pipeline for market analysis and trade predictions
"""

import os
import streamlit as st
from typing import TypedDict, List, Dict, Any, Literal
import operator
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# --- State Definition ---
class TradingState(TypedDict):
    """State that flows through the trading agent pipeline"""
    symbol: str  # e.g., "BTC/USDT"
    timeframe: str  # e.g., "1h", "4h", "1d"
    
    # Data Collection
    market_data: Dict[str, Any]  # OHLCV data
    indicators: Dict[str, float]  # Technical indicators
    sentiment: Dict[str, Any]  # News and social sentiment
    
    # Analysis
    technical_analysis: str  # LLM technical analysis
    fundamental_analysis: str  # LLM fundamental view
    market_context: str  # Overall market conditions
    
    # Prediction
    price_prediction: Dict[str, Any]  # Predicted prices and confidence
    trend_prediction: str  # Predicted trend direction
    
    # Risk & Decision
    risk_assessment: Dict[str, Any]  # Risk metrics
    position_sizing: Dict[str, Any]  # Recommended position size
    
    # Final Output
    decision: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    reasoning: str  # Detailed reasoning
    stop_loss: float  # Recommended stop loss
    take_profit: float  # Recommended take profit
    
    # Metadata
    timestamp: str
    error_log: List[str]


# --- Helper Functions ---

def get_llm(temperature: float = 0.3):
    """Get configured LLM instance"""
    return ChatOpenAI(
        model="deepseek/deepseek-chat",
        temperature=temperature,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )


# --- Node 1: Data Collection ---

def collect_data_node(state: TradingState) -> Dict:
    """
    Collect market data, technical indicators, and sentiment
    In production: Connect to CCXT, yfinance, TradingView, etc.
    For MVP: Simulate with mock data
    """
    print("--- DATA COLLECTOR ---")
    
    symbol = state['symbol']
    timeframe = state['timeframe']
    
    # TODO: Replace with real API calls
    # For now, simulate data collection
    mock_market_data = {
        "current_price": 45000.00,
        "open": 44500.00,
        "high": 45500.00,
        "low": 44200.00,
        "volume": 25000000,
        "change_24h": 1.12,
        "timestamp": datetime.now().isoformat()
    }
    
    mock_indicators = {
        "RSI_14": 55.3,
        "MACD": 120.5,
        "MACD_signal": 110.2,
        "BB_upper": 46000,
        "BB_lower": 44000,
        "EMA_20": 44800,
        "EMA_50": 44200,
        "volume_sma_20": 22000000,
        "support": 44000,
        "resistance": 46000
    }
    
    mock_sentiment = {
        "news_sentiment": "neutral",
        "social_sentiment": "bullish",
        "fear_greed_index": 65,
        "recent_news": [
            "Bitcoin ETF sees strong inflows",
            "Fed signals rate cut possibility"
        ]
    }
    
    return {
        "market_data": mock_market_data,
        "indicators": mock_indicators,
        "sentiment": mock_sentiment,
        "timestamp": datetime.now().isoformat(),
        "error_log": state.get("error_log", [])
    }


# --- Node 2: Technical Analysis (LLM) ---

def technical_analysis_node(state: TradingState) -> Dict:
    """
    LLM analyzes technical indicators and chart patterns
    """
    print("--- TECHNICAL ANALYST ---")
    
    llm = get_llm(temperature=0.2)
    
    market_data = state['market_data']
    indicators = state['indicators']
    
    prompt = f"""You are a Professional Technical Analyst specializing in cryptocurrency trading.

Asset: {state['symbol']}
Timeframe: {state['timeframe']}

Current Market Data:
- Price: ${market_data['current_price']:,.2f}
- 24h Change: {market_data['change_24h']}%
- Volume: ${market_data['volume']:,.0f}

Technical Indicators:
- RSI(14): {indicators['RSI_14']}
- MACD: {indicators['MACD']} (Signal: {indicators['MACD_signal']})
- Bollinger Bands: ${indicators['BB_lower']:,.0f} - ${indicators['BB_upper']:,.0f}
- EMA(20): ${indicators['EMA_20']:,.0f}
- EMA(50): ${indicators['EMA_50']:,.0f}
- Support: ${indicators['support']:,.0f}
- Resistance: ${indicators['resistance']:,.0f}

Provide a detailed technical analysis including:
1. Current trend (bullish/bearish/neutral)
2. Key support and resistance levels
3. Momentum indicators interpretation
4. Volume analysis
5. Potential chart patterns
6. Short-term price targets

Be objective and data-driven in your analysis."""

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    return {"technical_analysis": response.content}


# --- Node 3: Fundamental & Sentiment Analysis ---

def fundamental_analysis_node(state: TradingState) -> Dict:
    """
    LLM analyzes fundamental factors and market sentiment
    """
    print("--- FUNDAMENTAL ANALYST ---")
    
    llm = get_llm(temperature=0.3)
    
    sentiment = state['sentiment']
    
    prompt = f"""You are a Senior Market Analyst specializing in cryptocurrency fundamentals and market psychology.

Asset: {state['symbol']}

Market Sentiment Data:
- News Sentiment: {sentiment['news_sentiment']}
- Social Media Sentiment: {sentiment['social_sentiment']}
- Fear & Greed Index: {sentiment['fear_greed_index']}/100
- Recent Headlines: {', '.join(sentiment['recent_news'])}

Provide analysis on:
1. Overall market sentiment interpretation
2. Impact of recent news on price action
3. Fear & Greed index implications
4. Potential catalysts (positive/negative)
5. Macro factors affecting the market
6. Risk factors to consider

Keep your analysis objective and consider both bullish and bearish scenarios."""

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    return {"fundamental_analysis": response.content}


# --- Node 4: Market Context Analysis ---

def market_context_node(state: TradingState) -> Dict:
    """
    LLM synthesizes overall market conditions
    """
    print("--- MARKET CONTEXT ANALYZER ---")
    
    llm = get_llm(temperature=0.2)
    
    prompt = f"""You are a Market Strategist providing context for trading decisions.

Asset: {state['symbol']}
Timeframe: {state['timeframe']}

Based on current market conditions, describe:
1. Overall market phase (accumulation, markup, distribution, markdown)
2. Market volatility level (low/medium/high)
3. Liquidity conditions
4. Correlation with major indices
5. Best trading strategy for current conditions (trend-following, mean-reversion, etc.)

Be concise but thorough."""

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    return {"market_context": response.content}


# --- Node 5: Price Prediction ---

def prediction_node(state: TradingState) -> Dict:
    """
    Generate price predictions based on all previous analysis
    In production: Use TimeGPT, N-BEATS, or custom ML model
    For MVP: LLM-based prediction with confidence
    """
    print("--- PREDICTION ENGINE ---")
    
    llm = get_llm(temperature=0.1)
    
    market_data = state['market_data']
    technical = state['technical_analysis']
    fundamental = state['fundamental_analysis']
    context = state['market_context']
    
    prompt = f"""You are a Quantitative Analyst making price predictions.

Asset: {state['symbol']}
Current Price: ${market_data['current_price']:,.2f}
Timeframe: {state['timeframe']}

Technical Analysis Summary:
{technical[:500]}...

Fundamental Analysis Summary:
{fundamental[:500]}...

Market Context:
{context[:300]}...

Based on all available information, provide:
1. Price prediction for next {state['timeframe']} (specific number)
2. Trend direction (BULLISH/BEARISH/NEUTRAL)
3. Confidence level (0-100%)
4. Key factors supporting the prediction
5. Potential invalidation levels

Format your response as:
PREDICTION: [price]
TREND: [direction]
CONFIDENCE: [0-100]
REASONING: [explanation]"""

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    # Parse the response
    content = response.content
    
    # Extract prediction (simple parsing, can be improved)
    try:
        lines = content.split('\n')
        prediction_data = {}
        
        for line in lines:
            if 'PREDICTION:' in line:
                prediction_data['predicted_price'] = line.split(':')[1].strip()
            elif 'TREND:' in line:
                prediction_data['trend'] = line.split(':')[1].strip()
            elif 'CONFIDENCE:' in line:
                conf_str = line.split(':')[1].strip().replace('%', '')
                prediction_data['confidence'] = float(conf_str) if conf_str.replace('.', '').isdigit() else 50.0
        
        if not prediction_data:
            prediction_data = {
                'predicted_price': market_data['current_price'],
                'trend': 'NEUTRAL',
                'confidence': 50.0
            }
            
    except Exception as e:
        prediction_data = {
            'predicted_price': market_data['current_price'],
            'trend': 'NEUTRAL',
            'confidence': 50.0
        }
    
    return {
        "price_prediction": prediction_data,
        "trend_prediction": content
    }


# --- Node 6: Risk Assessment ---

def risk_assessment_node(state: TradingState) -> Dict:
    """
    Assess risk and calculate position sizing
    """
    print("--- RISK ASSESSOR ---")
    
    llm = get_llm(temperature=0.1)
    
    market_data = state['market_data']
    indicators = state['indicators']
    prediction = state['price_prediction']
    
    current_price = market_data['current_price']
    
    prompt = f"""You are a Professional Risk Manager.

Asset: {state['symbol']}
Current Price: ${current_price:,.2f}
Predicted Trend: {prediction.get('trend', 'NEUTRAL')}
Confidence: {prediction.get('confidence', 50)}%

Technical Levels:
- Support: ${indicators['support']:,.0f}
- Resistance: ${indicators['resistance']:,.0f}
- RSI: {indicators['RSI_14']}

Calculate and recommend:
1. Risk/Reward Ratio
2. Stop Loss Level (specific price)
3. Take Profit Levels (TP1, TP2, TP3)
4. Maximum Position Size (% of portfolio)
5. Risk Level (LOW/MEDIUM/HIGH)

Format:
RISK_LEVEL: [level]
STOP_LOSS: [price]
TAKE_PROFIT_1: [price]
TAKE_PROFIT_2: [price]
RISK_REWARD: [ratio]
POSITION_SIZE: [percentage]%"""

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    # Parse response
    content = response.content
    risk_data = {}
    
    try:
        lines = content.split('\n')
        for line in lines:
            if 'STOP_LOSS:' in line:
                risk_data['stop_loss'] = line.split(':')[1].strip()
            elif 'TAKE_PROFIT_1:' in line:
                risk_data['take_profit_1'] = line.split(':')[1].strip()
            elif 'RISK_LEVEL:' in line:
                risk_data['risk_level'] = line.split(':')[1].strip()
            elif 'POSITION_SIZE:' in line:
                risk_data['position_size'] = line.split(':')[1].strip()
    except:
        risk_data = {
            'stop_loss': indicators['support'],
            'take_profit_1': indicators['resistance'],
            'risk_level': 'MEDIUM',
            'position_size': '2%'
        }
    
    return {
        "risk_assessment": risk_data,
        "position_sizing": {'recommended_size': risk_data.get('position_size', '2%')}
    }


# --- Node 7: Final Decision Maker ---

def decision_maker_node(state: TradingState) -> Dict:
    """
    Make final trading decision by synthesizing all analysis
    """
    print("--- DECISION MAKER ---")
    
    llm = get_llm(temperature=0.0)
    
    technical = state['technical_analysis']
    fundamental = state['fundamental_analysis']
    prediction = state['price_prediction']
    risk = state['risk_assessment']
    
    prompt = f"""You are the Chief Trading Officer making the final trading decision.

Asset: {state['symbol']}
Current Price: ${state['market_data']['current_price']:,.2f}

Summary of Analysis:
- Technical Outlook: {technical[:200]}...
- Fundamental Outlook: {fundamental[:200]}...
- Predicted Trend: {prediction.get('trend', 'NEUTRAL')}
- Confidence: {prediction.get('confidence', 50)}%
- Risk Level: {risk.get('risk_level', 'MEDIUM')}

Make a final trading decision:
DECISION: BUY / SELL / HOLD
CONFIDENCE: [0-100]
ENTRY_PRICE: [price]
STOP_LOSS: {risk.get('stop_loss', 'N/A')}
TAKE_PROFIT: {risk.get('take_profit_1', 'N/A')}

REASONING:
[Provide clear, concise reasoning for the decision. Include:
- Key factors supporting the decision
- Main risks
- Expected outcome
- Alternative scenarios]

Make the best risk-adjusted decision."""

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    content = response.content
    
    # Parse decision
    decision = "HOLD"
    confidence = 50.0
    
    try:
        lines = content.split('\n')
        for line in lines:
            if 'DECISION:' in line:
                decision = line.split(':')[1].strip().split()[0]  # Get first word (BUY/SELL/HOLD)
            elif 'CONFIDENCE:' in line:
                conf_str = line.split(':')[1].strip().replace('%', '')
                if conf_str.replace('.', '').isdigit():
                    confidence = float(conf_str)
    except:
        pass
    
    return {
        "decision": decision,
        "confidence": confidence,
        "reasoning": content,
        "stop_loss": risk.get('stop_loss', 0),
        "take_profit": risk.get('take_profit_1', 0)
    }


# --- Graph Construction ---

def build_trading_graph():
    """Build the LangGraph workflow for trading analysis"""
    
    workflow = StateGraph(TradingState)
    
    # Add all nodes
    workflow.add_node("collect_data", collect_data_node)
    workflow.add_node("technical_analysis", technical_analysis_node)
    workflow.add_node("fundamental_analysis", fundamental_analysis_node)
    workflow.add_node("market_context", market_context_node)
    workflow.add_node("prediction", prediction_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("decision_maker", decision_maker_node)
    
    # Define the flow
    workflow.set_entry_point("collect_data")
    
    # Sequential flow
    workflow.add_edge("collect_data", "technical_analysis")
    workflow.add_edge("technical_analysis", "fundamental_analysis")
    workflow.add_edge("fundamental_analysis", "market_context")
    workflow.add_edge("market_context", "prediction")
    workflow.add_edge("prediction", "risk_assessment")
    workflow.add_edge("risk_assessment", "decision_maker")
    workflow.add_edge("decision_maker", END)
    
    return workflow.compile()


# --- Streamlit App ---

def main():
    st.set_page_config(
        page_title="Trading Prediction Agent",
        page_icon="📈",
        layout="wide"
    )
    
    # Header
    st.title("📈 AI Trading Prediction Agent")
    st.markdown("""
    **Professional multi-step trading analysis powered by LangGraph**
    
    This agent performs comprehensive market analysis through 7 specialized steps:
    1. 📊 Data Collection
    2. 📉 Technical Analysis
    3. 📰 Fundamental Analysis
    4. 🌐 Market Context
    5. 🎯 Price Prediction
    6. ⚖️ Risk Assessment
    7. ✅ Final Decision
    """)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY not found in .env file")
        st.stop()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        symbol = st.selectbox(
            "Trading Pair",
            ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"],
            index=0
        )
        
        timeframe = st.selectbox(
            "Timeframe",
            ["15m", "1h", "4h", "1d", "1w"],
            index=2
        )
        
        st.divider()
        
        st.markdown("### 🛠️ Future Features")
        st.markdown("""
        - [ ] Live data from CCXT
        - [ ] TimeGPT integration
        - [ ] Backtesting
        - [ ] Paper trading
        - [ ] Alert system
        """)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            run_trading_analysis(symbol, timeframe)
    
    with col2:
        st.metric("Status", "Ready", delta="Waiting for analysis")


def run_trading_analysis(symbol: str, timeframe: str):
    """Execute the trading agent workflow"""
    
    graph = build_trading_graph()
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize state
    inputs = {
        "symbol": symbol,
        "timeframe": timeframe,
        "error_log": []
    }
    
    # Step tracking
    steps = [
        "collect_data",
        "technical_analysis", 
        "fundamental_analysis",
        "market_context",
        "prediction",
        "risk_assessment",
        "decision_maker"
    ]
    
    step_names = {
        "collect_data": "📊 Collecting Market Data",
        "technical_analysis": "📉 Technical Analysis",
        "fundamental_analysis": "📰 Fundamental Analysis",
        "market_context": "🌐 Market Context",
        "prediction": "🎯 Generating Predictions",
        "risk_assessment": "⚖️ Risk Assessment",
        "decision_maker": "✅ Making Decision"
    }
    
    # Create containers for results
    results_container = st.container()
    
    try:
        current_step = 0
        
        # Stream execution
        for output in graph.stream(inputs):
            for key, value in output.items():
                if key in steps:
                    current_step = steps.index(key) + 1
                    progress = current_step / len(steps)
                    progress_bar.progress(progress)
                    status_text.markdown(f"**{step_names.get(key, key)}**")
                    
                    # Show step details in expander
                    with st.expander(f"✅ {step_names.get(key, key)} - Details"):
                        st.json(value)
        
        # Get final state
        final_state = graph.invoke(inputs)
        
        progress_bar.progress(1.0)
        status_text.markdown("**✅ Analysis Complete!**")
        
        # Display results
        display_results(final_state, results_container)
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.exception(e)


def display_results(state: TradingState, container):
    """Display the final analysis results"""
    
    with container:
        st.divider()
        st.header("📊 Analysis Results")
        
        # Decision summary
        col1, col2, col3, col4 = st.columns(4)
        
        decision = state.get('decision', 'HOLD')
        confidence = state.get('confidence', 0)
        
        # Color coding
        decision_color = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }.get(decision, '⚪')
        
        with col1:
            st.metric("Decision", f"{decision_color} {decision}")
        
        with col2:
            st.metric("Confidence", f"{confidence:.1f}%")
        
        with col3:
            current_price = state.get('market_data', {}).get('current_price', 0)
            st.metric("Current Price", f"${current_price:,.2f}")
        
        with col4:
            change = state.get('market_data', {}).get('change_24h', 0)
            st.metric("24h Change", f"{change:+.2f}%", delta=f"{change:+.2f}%")
        
        # Risk Metrics
        st.divider()
        st.subheader("⚖️ Risk Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sl = state.get('stop_loss', 'N/A')
            st.metric("Stop Loss", sl)
        
        with col2:
            tp = state.get('take_profit', 'N/A')
            st.metric("Take Profit", tp)
        
        with col3:
            pos_size = state.get('position_sizing', {}).get('recommended_size', 'N/A')
            st.metric("Position Size", pos_size)
        
        # Detailed Reasoning
        st.divider()
        st.subheader("📝 Detailed Analysis")
        
        tabs = st.tabs([
            "🎯 Final Reasoning",
            "📉 Technical", 
            "📰 Fundamental",
            "🌐 Market Context",
            "🔮 Prediction"
        ])
        
        with tabs[0]:
            st.markdown(state.get('reasoning', 'No reasoning available'))
        
        with tabs[1]:
            st.markdown(state.get('technical_analysis', 'Not available'))
        
        with tabs[2]:
            st.markdown(state.get('fundamental_analysis', 'Not available'))
        
        with tabs[3]:
            st.markdown(state.get('market_context', 'Not available'))
        
        with tabs[4]:
            st.markdown(state.get('trend_prediction', 'Not available'))
        
        # Download report
        st.divider()
        
        report = generate_report(state)
        
        st.download_button(
            "📥 Download Full Report",
            data=report,
            file_name=f"trading_analysis_{state.get('symbol', 'unknown').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )


def generate_report(state: TradingState) -> str:
    """Generate a markdown report of the analysis"""
    
    report = f"""# Trading Analysis Report

**Asset:** {state.get('symbol', 'N/A')}
**Timeframe:** {state.get('timeframe', 'N/A')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎯 Executive Summary

**Decision:** {state.get('decision', 'N/A')}
**Confidence:** {state.get('confidence', 0):.1f}%
**Current Price:** ${state.get('market_data', {}).get('current_price', 0):,.2f}

### Risk Parameters
- **Stop Loss:** {state.get('stop_loss', 'N/A')}
- **Take Profit:** {state.get('take_profit', 'N/A')}
- **Position Size:** {state.get('position_sizing', {}).get('recommended_size', 'N/A')}

---

## 📊 Market Data

{json.dumps(state.get('market_data', {}), indent=2)}

---

## 📉 Technical Analysis

{state.get('technical_analysis', 'Not available')}

---

## 📰 Fundamental Analysis

{state.get('fundamental_analysis', 'Not available')}

---

## 🌐 Market Context

{state.get('market_context', 'Not available')}

---

## 🔮 Price Prediction

{state.get('trend_prediction', 'Not available')}

---

## ⚖️ Risk Assessment

{json.dumps(state.get('risk_assessment', {}), indent=2)}

---

## 📝 Final Decision Reasoning

{state.get('reasoning', 'Not available')}

---

## ⚠️ Disclaimer

This analysis is generated by an AI system and should not be considered as financial advice. 
Always conduct your own research and consult with qualified financial advisors before making trading decisions.
Past performance does not guarantee future results.

---

*Generated by Trading Prediction Agent v1.0*
"""
    
    return report


if __name__ == "__main__":
    main()

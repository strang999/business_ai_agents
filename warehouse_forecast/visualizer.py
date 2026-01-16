"""
Visualization Dashboard

Creates interactive Plotly charts for:
1. Forecast vs Actual (time series)
2. Warehouse fill rates
3. Alert priority matrix
4. Confidence intervals
5. Top products by risk
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForecastVisualizer:
    """Create interactive visualizations"""
    
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def plot_forecast_with_confidence(
        self,
        historical,
        forecast_mean,
        forecast_q10,
        forecast_q90,
        title="Warehouse Forecast"
    ):
        """
        Plot historical + forecast with confidence bands
        
        Args:
            historical: List of historical values
            forecast_mean: Forecasted mean values
            forecast_q10: 10th percentile
            forecast_q90: 90th percentile
            title: Chart title
        """
        # Create time index
        hist_dates = pd.date_range(
            end=datetime.now(),
            periods=len(historical),
            freq='D'
        )
        
        forecast_dates = pd.date_range(
            start=datetime.now() + timedelta(days=1),
            periods=len(forecast_mean),
            freq='D'
        )
        
        fig = go.Figure()
        
        # Historical
        fig.add_trace(go.Scatter(
            x=hist_dates,
            y=historical,
            mode='lines',
            name='Historical',
            line=dict(color='#2E86AB', width=2)
        ))
        
        # Forecast mean
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_mean,
            mode='lines',
            name='Forecast',
            line=dict(color='#A23B72', width=2, dash='dash')
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_dates.tolist() + forecast_dates.tolist()[::-1],
            y=forecast_q90 + forecast_q10[::-1],
            fill='toself',
            fillcolor='rgba(162, 59, 114, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='80% Confidence',
            showlegend=True
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Inventory Level",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_alert_dashboard(self, alerts, metrics):
        """
        Create dashboard with alerts and metrics
        
        Args:
            alerts: List of alert dicts
            metrics: Dict of metrics per series
        """
        # Count by severity
        severity_counts = {
            'HIGH': len([a for a in alerts if a['severity'] == 'HIGH']),
            'MEDIUM': len([a for a in alerts if a['severity'] == 'MEDIUM']),
            'LOW': len([a for a in alerts if a['severity'] == 'LOW'])
        }
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Alerts by Severity',
                'Top 5 Critical Products',
                'Fill Rate Distribution',
                'Forecast Trend'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'histogram'}, {'type': 'scatter'}]
            ]
        )
        
        # 1. Alerts by severity
        fig.add_trace(
            go.Bar(
                x=list(severity_counts.keys()),
                y=list(severity_counts.values()),
                marker_color=['#E63946', '#F77F00', '#06A77D'],
                name='Alerts'
            ),
            row=1, col=1
        )
        
        # 2. Top critical products (if alerts exist)
        if alerts:
            top_alerts = sorted(alerts, key=lambda x: x['days_remaining'])[:5]
            products = [a['product'][:15] for a in top_alerts]  # Truncate long names
            days = [a['days_remaining'] for a in top_alerts]
            
            fig.add_trace(
                go.Bar(
                    x=products,
                    y=days,
                    marker_color='#E63946',
                    name='Days Remaining'
                ),
                row=1, col=2
            )
        
        # 3. Fill rate distribution
        if metrics:
            fill_rates = [m.get('fill_rate_current', 0) * 100 for m in metrics.values()]
            fig.add_trace(
                go.Histogram(
                    x=fill_rates,
                    nbinsx=20,
                    marker_color='#2E86AB',
                    name='Warehouses'
                ),
                row=2, col=1
            )
        
        # 4. Forecast trend summary
        if metrics:
            increasing = len([m for m in metrics.values() if m.get('trend') == 'increasing'])
            decreasing = len([m for m in metrics.values() if m.get('trend') == 'decreasing'])
            
            fig.add_trace(
                go.Bar(
                    x=['Increasing', 'Decreasing'],
                    y=[increasing, decreasing],
                    marker_color=['#06A77D', '#E63946'],
                    name='Trend'
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Warehouse Forecasting Dashboard",
            showlegend=False,
            height=800,
            template='plotly_white'
        )
        
        return fig
    
    def save_html(self, fig, filename):
        """Save figure as interactive HTML"""
        filepath = self.output_dir / filename
        fig.write_html(str(filepath))
        logger.info(f"📊 Saved dashboard: {filepath}")
        return str(filepath)


def create_sample_dashboard():
    """Create sample dashboard for testing"""
    viz = ForecastVisualizer()
    
    # Sample data
    historical = list(range(100, 150))
    forecast_mean = list(range(150, 180))
    forecast_q10 = [x - 10 for x in forecast_mean]
    forecast_q90 = [x + 10 for x in forecast_mean]
    
    # Create forecast chart
    fig1 = viz.plot_forecast_with_confidence(
        historical,
        forecast_mean,
        forecast_q10,
        forecast_q90,
        title="Sample Warehouse Forecast"
    )
    
    viz.save_html(fig1, "sample_forecast.html")
    
    # Sample alerts
    alerts = [
        {'severity': 'HIGH', 'product': 'Product_A', 'days_remaining': 3},
        {'severity': 'MEDIUM', 'product': 'Product_B', 'days_remaining': 10},
        {'severity': 'LOW', 'product': 'Product_C', 'days_remaining': 20}
    ]
    
    metrics = {
        'WH_01_A': {'fill_rate_current': 0.85, 'trend': 'increasing'},
        'WH_01_B': {'fill_rate_current': 0.60, 'trend': 'decreasing'},
        'WH_02_A': {'fill_rate_current': 0.45, 'trend': 'increasing'}
    }
    
    fig2 = viz.create_alert_dashboard(alerts, metrics)
    viz.save_html(fig2, "sample_dashboard.html")
    
    print("✅ Sample dashboards created in output/")
    print("   - sample_forecast.html")
    print("   - sample_dashboard.html")


if __name__ == "__main__":
    create_sample_dashboard()

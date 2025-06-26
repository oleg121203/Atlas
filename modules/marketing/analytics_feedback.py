"""
Analytics and Feedback Loops Module for Atlas

This module tracks marketing campaign conversions and analyzes channel performance.
"""

import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

class MarketingAnalytics:
    def __init__(self):
        self.campaigns = []
        self.conversion_data = []
        self.channel_metrics = {'Twitter': [], 'Instagram': [], 'LinkedIn': [], 'Email': [], 'Website': []}
        self.data_file = "marketing_analytics.json"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.campaigns = data.get('campaigns', [])
                self.conversion_data = data.get('conversion_data', [])
                self.channel_metrics = data.get('channel_metrics', {'Twitter': [], 'Instagram': [], 'LinkedIn': [], 'Email': [], 'Website': []})

    def save_data(self):
        data = {
            'campaigns': self.campaigns,
            'conversion_data': self.conversion_data,
            'channel_metrics': self.channel_metrics
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_campaign(self, name, start_date, end_date, channels):
        campaign = {
            'id': len(self.campaigns) + 1,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
            'channels': channels,
            'created_at': datetime.now().isoformat()
        }
        self.campaigns.append(campaign)
        self.save_data()
        return campaign

    def record_conversion(self, campaign_id, channel, conversion_type, value=1):
        conversion = {
            'id': len(self.conversion_data) + 1,
            'campaign_id': campaign_id,
            'channel': channel,
            'type': conversion_type,
            'value': value,
            'recorded_at': datetime.now().isoformat()
        }
        self.conversion_data.append(conversion)
        self.save_data()
        return conversion

    def update_channel_metrics(self, channel, impressions, clicks, conversions, cost):
        metric = {
            'id': len(self.channel_metrics[channel]) + 1,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'cost': cost,
            'recorded_at': datetime.now().isoformat()
        }
        self.channel_metrics[channel].append(metric)
        self.save_data()
        return metric

    def get_campaign_performance(self, campaign_id=None):
        if campaign_id:
            campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
            if not campaign:
                return f"Campaign {campaign_id} not found"
            conversions = [c for c in self.conversion_data if c['campaign_id'] == campaign_id]
            df = pd.DataFrame(conversions)
            if not df.empty:
                return df.groupby('channel').agg({'value': 'sum'}).reset_index()
            return f"No conversion data for campaign {campaign_id}"
        else:
            df = pd.DataFrame(self.conversion_data)
            if not df.empty:
                return df.groupby(['campaign_id', 'channel']).agg({'value': 'sum'}).reset_index()
            return "No conversion data available"

    def get_channel_performance(self, channel=None):
        if channel:
            metrics = self.channel_metrics.get(channel, [])
            if not metrics:
                return f"No data for channel {channel}"
            df = pd.DataFrame(metrics)
            if not df.empty:
                df['CTR'] = df['clicks'] / df['impressions'] * 100
                df['CPC'] = df['cost'] / df['clicks']
                df['CPA'] = df['cost'] / df['conversions']
                return df.describe()
        else:
            results = {}
            for ch in self.channel_metrics.keys():
                metrics = self.channel_metrics.get(ch, [])
                if metrics:
                    df = pd.DataFrame(metrics)
                    df['CTR'] = df['clicks'] / df['impressions'] * 100
                    df['CPC'] = df['cost'] / df['clicks']
                    df['CPA'] = df['cost'] / df['conversions']
                    results[ch] = df.describe()
                else:
                    results[ch] = f"No data for channel {ch}"
            return results

    def visualize_channel_performance(self, channel=None):
        if channel:
            metrics = self.channel_metrics.get(channel, [])
            if not metrics:
                print(f"No data to visualize for {channel}")
                return
            df = pd.DataFrame(metrics)
            if not df.empty:
                df['recorded_at'] = pd.to_datetime(df['recorded_at'])
                df.set_index('recorded_at', inplace=True)
                fig, ax = plt.subplots(figsize=(10, 6))
                df[['impressions', 'clicks', 'conversions']].plot(ax=ax)
                ax.set_title(f"Performance Metrics for {channel}")
                ax.set_ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()
        else:
            for ch in self.channel_metrics.keys():
                self.visualize_channel_performance(ch)

    def recommend_strategy_adjustment(self, min_ctr=0.5, max_cpc=2.0, max_cpa=50.0):
        recommendations = []
        for channel in self.channel_metrics.keys():
            metrics = self.channel_metrics.get(channel, [])
            if metrics:
                df = pd.DataFrame(metrics)
                df['CTR'] = df['clicks'] / df['impressions'] * 100
                df['CPC'] = df['cost'] / df['clicks']
                df['CPA'] = df['cost'] / df['conversions']
                latest = df.iloc[-1]
                if latest['CTR'] < min_ctr:
                    recommendations.append(f"Increase ad relevance or targeting for {channel} - CTR {latest['CTR']:.2f}% below threshold {min_ctr}%")
                if latest['CPC'] > max_cpc:
                    recommendations.append(f"Optimize ad copy or landing page for {channel} - CPC ${latest['CPC']:.2f} exceeds threshold ${max_cpc}")
                if latest['CPA'] > max_cpa:
                    recommendations.append(f"Refine audience or conversion funnel for {channel} - CPA ${latest['CPA']:.2f} exceeds threshold ${max_cpa}")
        if not recommendations:
            recommendations.append("All channels performing within acceptable parameters.")
        return recommendations

if __name__ == "__main__":
    analytics = MarketingAnalytics()
    campaign = analytics.add_campaign("SummerLaunch", "2025-06-01", "2025-08-31", ["Twitter", "Instagram", "LinkedIn"])
    analytics.record_conversion(campaign['id'], "Twitter", "SignUp", 10)
    analytics.record_conversion(campaign['id'], "Twitter", "Download", 5)
    analytics.record_conversion(campaign['id'], "Instagram", "SignUp", 8)
    analytics.update_channel_metrics("Twitter", 10000, 500, 15, 750.0)
    analytics.update_channel_metrics("Instagram", 8000, 400, 10, 600.0)
    analytics.update_channel_metrics("LinkedIn", 5000, 300, 20, 900.0)
    print(analytics.get_campaign_performance(campaign['id']))
    print(analytics.get_channel_performance())
    analytics.visualize_channel_performance()
    print(analytics.recommend_strategy_adjustment())

"""
Social Media Campaign Module for Atlas

This module provides functionality for managing social media campaigns, creating content,
scheduling posts, and monitoring engagement metrics.
"""

import json
import os
from datetime import datetime, timedelta
import requests
import pandas as pd
import matplotlib.pyplot as plt

class SocialMediaCampaign:
    def __init__(self, campaign_name, platforms=None):
        self.campaign_name = campaign_name
        self.platforms = platforms if platforms else ['Twitter', 'Instagram', 'LinkedIn']
        self.content_plan = []
        self.scheduled_posts = []
        self.engagement_metrics = {'Twitter': [], 'Instagram': [], 'LinkedIn': []}
        self.data_file = f"social_media_data_{campaign_name}.json"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.content_plan = data.get('content_plan', [])
                self.scheduled_posts = data.get('scheduled_posts', [])
                self.engagement_metrics = data.get('engagement_metrics', {'Twitter': [], 'Instagram': [], 'LinkedIn': []})

    def save_data(self):
        data = {
            'content_plan': self.content_plan,
            'scheduled_posts': self.scheduled_posts,
            'engagement_metrics': self.engagement_metrics
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_content_to_plan(self, content_idea, target_platforms=None, visual_description=None):
        if target_platforms is None:
            target_platforms = self.platforms
        content = {
            'idea': content_idea,
            'platforms': target_platforms,
            'visual_description': visual_description,
            'created_at': datetime.now().isoformat(),
            'status': 'Draft'
        }
        self.content_plan.append(content)
        self.save_data()
        return content

    def schedule_post(self, content_index, post_time=None, platforms=None):
        if content_index >= len(self.content_plan):
            raise ValueError("Invalid content index")
        content = self.content_plan[content_index]
        if platforms is None:
            platforms = content['platforms']
        if post_time is None:
            post_time = datetime.now() + timedelta(days=1)
        scheduled_post = {
            'content_index': content_index,
            'post_time': post_time.isoformat(),
            'platforms': platforms,
            'status': 'Scheduled'
        }
        self.scheduled_posts.append(scheduled_post)
        content['status'] = 'Scheduled'
        self.save_data()
        return scheduled_post

    def simulate_posting(self, post_index):
        if post_index >= len(self.scheduled_posts):
            raise ValueError("Invalid post index")
        post = self.scheduled_posts[post_index]
        content = self.content_plan[post['content_index']]
        post['status'] = 'Posted'
        content['status'] = 'Posted'
        # Simulate engagement metrics
        for platform in post['platforms']:
            engagement = {
                'post_time': post['post_time'],
                'likes': pd.np.random.randint(10, 100),
                'shares': pd.np.random.randint(5, 50),
                'comments': pd.np.random.randint(2, 20),
                'reach': pd.np.random.randint(100, 1000)
            }
            self.engagement_metrics[platform].append(engagement)
        self.save_data()
        return post

    def get_engagement_report(self, platform=None):
        if platform:
            metrics = self.engagement_metrics.get(platform, [])
            if not metrics:
                return f"No engagement data available for {platform}"
            df = pd.DataFrame(metrics)
            if not df.empty:
                df['post_time'] = pd.to_datetime(df['post_time'])
                df.set_index('post_time', inplace=True)
                return df.describe()
            return f"No engagement data available for {platform}"
        else:
            report = {}
            for p in self.platforms:
                metrics = self.engagement_metrics.get(p, [])
                if metrics:
                    df = pd.DataFrame(metrics)
                    df['post_time'] = pd.to_datetime(df['post_time'])
                    df.set_index('post_time', inplace=True)
                    report[p] = df.describe()
                else:
                    report[p] = f"No engagement data available for {p}"
            return report

    def visualize_engagement(self, platform=None):
        if platform:
            metrics = self.engagement_metrics.get(platform, [])
            if not metrics:
                print(f"No engagement data to visualize for {platform}")
                return
            df = pd.DataFrame(metrics)
            if not df.empty:
                df['post_time'] = pd.to_datetime(df['post_time'])
                df.set_index('post_time', inplace=True)
                fig, ax = plt.subplots(figsize=(10, 6))
                df[['likes', 'shares', 'comments']].plot(ax=ax)
                ax.set_title(f"Engagement Metrics for {platform}")
                ax.set_ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()
        else:
            for p in self.platforms:
                self.visualize_engagement(p)

    def get_scheduled_posts(self, upcoming_only=True):
        if upcoming_only:
            now = datetime.now().isoformat()
            return [post for post in self.scheduled_posts if post['post_time'] > now and post['status'] == 'Scheduled']
        return [post for post in self.scheduled_posts if post['status'] == 'Scheduled']

    def get_content_plan(self, status=None):
        if status:
            return [content for content in self.content_plan if content['status'] == status]
        return self.content_plan

# Example usage
if __name__ == "__main__":
    campaign = SocialMediaCampaign("AtlasLaunch")
    # Add some content ideas
    campaign.add_content_to_plan("Introducing Atlas - Your Ultimate Productivity Tool!", ['Twitter', 'LinkedIn'], "Sleek app screenshot")
    campaign.add_content_to_plan("How Atlas transforms your workflow", ['Instagram', 'LinkedIn'], "Infographic")
    campaign.add_content_to_plan("User testimonial: Atlas changed my work life!", ['Twitter', 'Instagram'], "User photo")
    # Schedule posts
    campaign.schedule_post(0, datetime.now() + timedelta(hours=2))
    campaign.schedule_post(1, datetime.now() + timedelta(days=1))
    campaign.schedule_post(2, datetime.now() + timedelta(days=2))
    # Simulate posting
    campaign.simulate_posting(0)
    # View engagement report
    print(campaign.get_engagement_report())
    # Visualize engagement
    campaign.visualize_engagement()

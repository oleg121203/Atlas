"""
User Satisfaction Monitoring System

This module implements a system for monitoring user satisfaction with workflows,
including Net Promoter Score (NPS) calculations, feedback collection, and sentiment analysis.
"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import nltk
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download required NLTK data
nltk.download("vader_lexicon")


class UserSatisfactionMonitor:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.feedback_data = pd.DataFrame(
            columns=[
                "user_id",
                "workflow_id",
                "timestamp",
                "nps_score",
                "feedback_text",
                "sentiment",
            ]
        )
        self.nps_history = pd.DataFrame(columns=["timestamp", "nps_score"])

    def collect_nps_score(self, user_id, workflow_id, score):
        """
        Collect Net Promoter Score from a user for a specific workflow.
        Score should be between 0 and 10.
        """
        if not 0 <= score <= 10:
            raise ValueError("NPS score must be between 0 and 10")

        timestamp = datetime.now()
        new_entry = {
            "user_id": user_id,
            "workflow_id": workflow_id,
            "timestamp": timestamp,
            "nps_score": score,
            "feedback_text": "",
            "sentiment": 0.0,
        }
        self.feedback_data = pd.concat(
            [self.feedback_data, pd.DataFrame([new_entry])], ignore_index=True
        )
        self._update_nps_history(timestamp)

    def collect_feedback(self, user_id, workflow_id, feedback_text):
        """
        Collect textual feedback from a user for a specific workflow and analyze its sentiment.
        """
        timestamp = datetime.now()
        sentiment_scores = self.sid.polarity_scores(feedback_text)
        compound_sentiment = sentiment_scores["compound"]

        new_entry = {
            "user_id": user_id,
            "workflow_id": workflow_id,
            "timestamp": timestamp,
            "nps_score": 0,
            "feedback_text": feedback_text,
            "sentiment": compound_sentiment,
        }
        self.feedback_data = pd.concat(
            [self.feedback_data, pd.DataFrame([new_entry])], ignore_index=True
        )

    def _update_nps_history(self, timestamp):
        """
        Update the historical record of overall NPS scores.
        """
        recent_feedback = self.feedback_data[
            self.feedback_data["timestamp"] > timestamp - timedelta(days=7)
        ]
        promoters = len(recent_feedback[recent_feedback["nps_score"] >= 9])
        detractors = len(recent_feedback[recent_feedback["nps_score"] <= 6])
        total_responses = len(recent_feedback[recent_feedback["nps_score"] > 0])

        nps_score = (
            (promoters - detractors) / total_responses * 100
            if total_responses > 0
            else 0
        )

        new_history_entry = {"timestamp": timestamp, "nps_score": nps_score}
        self.nps_history = pd.concat(
            [self.nps_history, pd.DataFrame([new_history_entry])], ignore_index=True
        )

    def get_current_nps(self):
        """
        Calculate and return the current Net Promoter Score based on recent feedback.
        """
        if not self.nps_history.empty:
            return self.nps_history["nps_score"].iloc[-1]
        return 0

    def get_nps_trend(self, days=30):
        """
        Return NPS trend over the specified number of days.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        trend_data = self.nps_history[self.nps_history["timestamp"] >= cutoff_date]
        return trend_data

    def get_workflow_satisfaction(self, workflow_id):
        """
        Get satisfaction metrics for a specific workflow.
        """
        workflow_feedback = self.feedback_data[
            self.feedback_data["workflow_id"] == workflow_id
        ]
        if workflow_feedback.empty:
            return {
                "average_nps": 0,
                "average_sentiment": 0,
                "feedback_count": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
            }

        sentiment_data = workflow_feedback[workflow_feedback["feedback_text"] != ""]
        positive_count = len(sentiment_data[sentiment_data["sentiment"] > 0.05])
        negative_count = len(sentiment_data[sentiment_data["sentiment"] < -0.05])

        return {
            "average_nps": workflow_feedback[workflow_feedback["nps_score"] > 0][
                "nps_score"
            ].mean(),
            "average_sentiment": sentiment_data["sentiment"].mean()
            if not sentiment_data.empty
            else 0,
            "feedback_count": len(workflow_feedback),
            "positive_feedback": positive_count,
            "negative_feedback": negative_count,
        }

    def visualize_satisfaction_dashboard(self):
        """
        Create a comprehensive visual dashboard of user satisfaction metrics.
        """
        fig = plt.figure(figsize=(15, 10))

        # Plot NPS trend
        ax1 = fig.add_subplot(2, 2, 1)
        if not self.nps_history.empty:
            ax1.plot(
                self.nps_history["timestamp"],
                self.nps_history["nps_score"],
                marker="o",
                color="blue",
            )
            ax1.set_title("NPS Trend Over Time")
            ax1.set_xlabel("Date")
            ax1.set_ylabel("NPS Score")
            ax1.grid(True)
            for tick in ax1.get_xticklabels():
                tick.set_rotation(45)

        # Plot sentiment distribution
        ax2 = fig.add_subplot(2, 2, 2)
        sentiment_data = self.feedback_data[self.feedback_data["feedback_text"] != ""]
        if not sentiment_data.empty:
            ax2.hist(
                sentiment_data["sentiment"], bins=20, edgecolor="black", color="green"
            )
            ax2.set_title("Distribution of Feedback Sentiment")
            ax2.set_xlabel("Sentiment Score")
            ax2.set_ylabel("Frequency")

        # Plot NPS category distribution
        ax3 = fig.add_subplot(2, 2, 3)
        nps_data = self.feedback_data[self.feedback_data["nps_score"] > 0]
        if not nps_data.empty:
            promoters = len(nps_data[nps_data["nps_score"] >= 9])
            passives = len(
                nps_data[(nps_data["nps_score"] >= 7) & (nps_data["nps_score"] < 9)]
            )
            detractors = len(nps_data[nps_data["nps_score"] <= 6])
            ax3.bar(
                ["Promoters (9-10)", "Passives (7-8)", "Detractors (0-6)"],
                [promoters, passives, detractors],
                color=["green", "yellow", "red"],
            )
            ax3.set_title("NPS Score Categories")
            ax3.set_ylabel("Count")

        # Plot workflow comparison (if multiple workflows exist)
        ax4 = fig.add_subplot(2, 2, 4)
        workflows = self.feedback_data["workflow_id"].unique()
        if len(workflows) > 1:
            workflow_nps = []
            workflow_labels = []
            for wf in workflows:
                wf_data = self.feedback_data[
                    (self.feedback_data["workflow_id"] == wf)
                    & (self.feedback_data["nps_score"] > 0)
                ]
                if not wf_data.empty:
                    workflow_nps.append(wf_data["nps_score"].mean())
                    workflow_labels.append(wf)
            if workflow_nps:
                ax4.bar(workflow_labels, workflow_nps, color="purple")
                ax4.set_title("Average NPS by Workflow")
                ax4.set_ylabel("Average NPS")
                for tick in ax4.get_xticklabels():
                    tick.set_rotation(45)

        plt.tight_layout()
        plt.show()

    def get_detailed_feedback_analysis(self, workflow_id=None, days=30):
        """
        Get detailed analysis of feedback including most common words and sentiment breakdown.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        if workflow_id:
            feedback_subset = self.feedback_data[
                (self.feedback_data["workflow_id"] == workflow_id)
                & (self.feedback_data["feedback_text"] != "")
                & (self.feedback_data["timestamp"] >= cutoff_date)
            ]
        else:
            feedback_subset = self.feedback_data[
                (self.feedback_data["feedback_text"] != "")
                & (self.feedback_data["timestamp"] >= cutoff_date)
            ]

        if feedback_subset.empty:
            return {
                "total_feedback": 0,
                "positive_percentage": 0,
                "negative_percentage": 0,
                "neutral_percentage": 0,
                "common_themes": [],
            }

        total_feedback = len(feedback_subset)
        positive_count = len(feedback_subset[feedback_subset["sentiment"] > 0.05])
        negative_count = len(feedback_subset[feedback_subset["sentiment"] < -0.05])
        neutral_count = total_feedback - positive_count - negative_count

        # Basic word frequency analysis (excluding common stop words)
        stop_words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "were",
            "will",
            "with",
        }
        all_text = " ".join(feedback_subset["feedback_text"].str.lower())
        words = all_text.split()
        filtered_words = [
            word for word in words if word not in stop_words and len(word) > 2
        ]
        word_freq = pd.Series(filtered_words).value_counts().head(5).to_dict()

        return {
            "total_feedback": total_feedback,
            "positive_percentage": (positive_count / total_feedback) * 100,
            "negative_percentage": (negative_count / total_feedback) * 100,
            "neutral_percentage": (neutral_count / total_feedback) * 100,
            "common_themes": list(word_freq.keys()),
        }

from app.database import Database
import pandas as pd

class Repository:

    def __init__(self, db_path="data/portfolio.db"):
        self.db = Database(db_path)

    def dashboard_summary(self):
        return {
            "snapshot": self.db.latest_snapshot(),
            "report": self.db.latest_report()
        }

    def equity_curve(self, days=365):
        return pd.DataFrame(
            self.db.get_history(days)
        )

    def holdings(self):
        df = pd.DataFrame(
            self.db.latest_positions()
        )

        if not df.empty:
            df["return_pct"] = (
                df["pnl"] / df["cost"] * 100
            ).round(2)

        return df

    def ai_report(self):
        return self.db.latest_report()

    def news(self):
        return pd.DataFrame(
            self.db.today_news()
        )

    def monthly_returns(self):
        return pd.DataFrame(
            self.db.monthly_returns()
        )
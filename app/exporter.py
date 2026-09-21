from pathlib import Path
import json

from app.repository import Repository


class DashboardExporter:

    def __init__(self, db_path="data/portfolio.db"):
        self.repo = Repository(db_path)

    def export(
        self,
        output="dashboard/public/data/dashboard.json"
    ):

        summary = self.repo.dashboard_summary()

        report = summary["report"]

        data = {
            "generated_at": summary["snapshot"]["snapshot_date"],

            "snapshot": summary["snapshot"],

            "ai_report": (
                report.model_dump(mode="json")
                if report else None
            ),

            "equity_curve": self.repo
                .equity_curve(365)
                .to_dict("records"),

            "holdings": self.repo
                .holdings()
                .to_dict("records"),

            "news": self.repo
                .news()
                .to_dict("records"),

            "monthly_returns": self.repo
                .monthly_returns()
                .to_dict("records")
        }

        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

        return path
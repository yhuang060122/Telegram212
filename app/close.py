from app.pipeline import DailyPipeline

pipeline = DailyPipeline()

portfolio, report = pipeline.run()

print("Market close snapshot saved.")
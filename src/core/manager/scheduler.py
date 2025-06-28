from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from models.learner.trainer import train_model
import time

# === Entry point for manual override ===
def train_now():
    print("[INFO] Manual training triggered...")
    train_model()

# === Scheduler logic ===
def start_scheduler(frequency="daily"):
    scheduler = BackgroundScheduler()

    if frequency == "daily":
        trigger = CronTrigger(hour=2)  # 2 AM daily
    elif frequency == "weekly":
        trigger = CronTrigger(day_of_week='sun', hour=3)  # Sunday 3 AM
    elif frequency == "monthly":
        trigger = CronTrigger(day=1, hour=4)  # 1st of every month, 4 AM
    else:
        print(f"[ERROR] Invalid frequency '{frequency}'")
        return

    scheduler.add_job(train_model, trigger, id="model_training", replace_existing=True)
    scheduler.start()

    print(f"[INFO] Scheduler started with '{frequency}' frequency. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(3600)  # Keeps the script alive
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\n[INFO] Scheduler stopped.")

# === CLI Entry ===
if __name__ == "__main__":
    print("=== Model Training Scheduler ===")
    print("Choose training frequency:")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")

    choice = input("Enter choice (1/2/3): ").strip()

    freq_map = {"1": "daily", "2": "weekly", "3": "monthly"}
    freq = freq_map.get(choice, None)

    if freq:
        start_scheduler(freq)
    else:
        print("[ERROR] Invalid choice. Exiting.")

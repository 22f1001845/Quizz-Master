# backend/tasks.py
import csv
import os
from datetime import datetime, timedelta
from itertools import groupby
from operator import attrgetter

from celery import shared_task
from flask_mail import Message
from models import IST, Score, User, db
from sqlalchemy import func
from sqlalchemy.orm import joinedload


# Task 2: Monthly Report sent via email
@shared_task(ignore_results=False, name="send_monthly_activity_report")
def send_monthly_activity_report():
  
    
    from app import mail

    try:
        # --- 1. Calculate the date range for the previous month ---
        # We use the IST timezone defined in models.py for all date operations.
        today = datetime.now(IST)
        first_day_of_current_month = today.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_day_of_prev_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_prev_month = last_day_of_prev_month.replace(day=1)

        # --- 2. Fetch all scores from the previous month in a single efficient query ---
        all_scores_last_month = (
            Score.query.options(joinedload(Score.user), joinedload(Score.quiz))
            .filter(
                Score.timestamp_of_attempt >= first_day_of_prev_month,
                Score.timestamp_of_attempt < first_day_of_current_month,
            )
            .order_by(Score.user_id)
            .all()
        )

        if not all_scores_last_month:
            return {
                "status": "completed",
                "message": "No user activity in the last month. No reports sent.",
            }

        reports_sent = 0

        # --- 3. Group scores by user ---
        user_scores_grouped = groupby(all_scores_last_month, key=attrgetter("user"))

        # --- 4. Iterate over each user and their scores to build and send the email ---
        for user, scores_iterator in user_scores_grouped:
            scores = list(scores_iterator)

            # Skip only if the user object is missing. The check for user.active has been removed.
            if not user:
                continue

            # Calculate statistics for the user
            valid_scores = [s.total_score for s in scores if s.total_score is not None]
            if not valid_scores:
                continue  # Skip users with no valid scores.

            total_score = sum(valid_scores)
            avg_score = total_score / len(valid_scores)

            # --- 5. Build a rich HTML email body ---
            month_name = first_day_of_prev_month.strftime("%B %Y")
            quiz_details_html = ""
            for score in scores:
                quiz_title = score.quiz.remarks if score.quiz else "Unknown Quiz"
                quiz_details_html += f"<li><strong>{quiz_title}:</strong> {score.total_score or 'N/A'}</li>"

            report_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ padding: 25px; border: 1px solid #e0e0e0; border-radius: 8px; max-width: 600px; margin: 20px auto; background-color: #f9f9f9; }}
                    .header {{ font-size: 24px; color: #2c3e50; margin-bottom: 20px; }}
                    .footer {{ margin-top: 25px; font-size: 12px; color: #888; text-align: center; }}
                    ul {{ list-style-type: none; padding-left: 0; }}
                    li {{ background: #ffffff; margin-bottom: 8px; padding: 12px; border-radius: 5px; border-left: 4px solid #3498db; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <p class="header">Your Monthly Report for {month_name}</p>
                    <p>Hi {user.fullname or "there"},</p>
                    <p>Here is your quiz activity summary from last month:</p>
                    <ul>{quiz_details_html}</ul>
                    <p>Your average score for the month was: <strong>{avg_score:.2f}</strong></p>
                    <p>Keep up the great work!</p>
                    <div class="footer">
                        <p>Regards,<br>The Quiz Master Team</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # --- 6. Create a plain text version for compatibility ---
            plain_text_details = "".join(
                [
                    f"- Quiz: {s.quiz.remarks if s.quiz else 'Unknown Quiz'}, Score: {s.total_score or 'N/A'}\n"
                    for s in scores
                ]
            )
            report_text = f"Hi {user.fullname or 'User'},\n\nHere is your activity report for {month_name}:\n{plain_text_details}\nAverage Score: {avg_score:.2f}\n\nKeep up the great work!\n\nRegards,\nThe Quiz Master Team"

            # --- 7. Send the email ---
            try:
                msg = Message(
                    subject=f"Your Quiz Master Report for {month_name}",
                    recipients=[user.email],
                    body=report_text,
                    html=report_html,
                )
                mail.send(msg)
                reports_sent += 1
            except Exception as mail_error:
                print(f"Failed to send email to {user.email}: {mail_error}")
                pass

        return {
            "status": "completed",
            "message": f"Monthly reports sent to {reports_sent} users.",
        }

    except Exception as e:
        print(f"An error occurred in the send_monthly_activity_report task: {e}")
        return {"status": "failed", "error": str(e)}


# Task:3 - Daily Reminders
@shared_task(ignore_results=False, name="send_daily_reminders")
def send_daily_reminders():
    # Import mail inside the task
    from app import mail

    try:
        inactive_threshold = datetime.now() - timedelta(days=7)

        active_users_in_last_7_days = (
            db.session.query(Score.user_id)
            .filter(Score.timestamp_of_attempt > inactive_threshold)
            .distinct()
        )

        inactive_users = User.query.filter(
            User.id.notin_(active_users_in_last_7_days)
        ).all()

        for user in inactive_users:
            reminder_message = f"""Hi {user.fullname or "User"},

We miss you at Quiz Master! Come back and test your knowledge with our new quizzes.

Regards,
The Quiz Master Team"""

            try:
                msg = Message(
                    subject="We miss you at Quiz Master!",
                    recipients=[user.email],
                    body=reminder_message,
                )
                mail.send(msg)
            except Exception:
                pass

        return {
            "status": "completed",
            "message": f"Reminders sent to {len(inactive_users)} inactive users.",
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}


# Task:1 - Download CSV for Admin
@shared_task(ignore_results=False, name="csv_report")
def csv_report():
    """
    Celery task to generate a CSV report of user performance statistics.

    This task queries the database to get statistics for each user,
    including total attempts, average score, and max score.
    It then generates a CSV file and saves it to the static directory.
    """
    try:
        os.makedirs("exports", exist_ok=True)

        users_stat = (
            db.session.query(
                User.id,
                User.fullname,  # Changed from full_name to fullname
                User.email,
                func.count(Score.id),
                func.avg(Score.total_score),
                func.max(Score.total_score),
            )
            .outerjoin(Score, User.id == Score.user_id)  # Explicit join condition
            .group_by(
                User.id, User.fullname, User.email
            )  # Group by all non-aggregated columns
            .all()
        )

        # Generate a unique filename based on the current timestamp.
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"user_performance_{timestamp}.csv"
        filepath = f"exports/{filename}"

        # Write the data to a CSV file.
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row.
            writer.writerow(
                [
                    "USER ID",
                    "FULL NAME",
                    "EMAIL",
                    "TOTAL ATTEMPTS",
                    "AVG SCORE",
                    "MAX SCORE",
                ]
            )

            # Write data rows for each user.
            for row in users_stat:
                writer.writerow(
                    [
                        row.id,
                        row.fullname,
                        row.email,
                        row[3],
                        float(row[4]) if row[4] is not None else 0,
                        row[5] if row[5] is not None else 0,
                    ]
                )

        return {"status": "completed", "url": f"/exports/{filename}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

"""Export tasks to CSV."""
import csv
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.task import Task
from app.models.user import User


def export_tasks_csv(user_email: str, output_file: str):
    """Export user's tasks to CSV."""
    app = create_app("development")
    
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if not user:
            print(f"❌ User not found: {user_email}")
            return
        
        tasks = Task.query.filter_by(user_id=user.id).all()
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Notes", "Due At", "Priority", "Status", "Created At"])
            
            for task in tasks:
                writer.writerow([
                    task.id,
                    task.title,
                    task.notes or "",
                    task.due_at.isoformat() if task.due_at else "",
                    task.priority,
                    task.status,
                    task.created_at.isoformat() if task.created_at else ""
                ])
        
        print(f"✅ Exported {len(tasks)} tasks to {output_file}")


def import_tasks_csv(user_email: str, input_file: str):
    """Import tasks from CSV."""
    app = create_app("development")
    
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if not user:
            print(f"❌ User not found: {user_email}")
            return
        
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                task = Task(
                    user_id=user.id,
                    title=row["Title"],
                    notes=row.get("Notes", ""),
                    priority=row.get("Priority", "MEDIUM"),
                    status=row.get("Status", "TODO")
                )
                
                if row.get("Due At"):
                    try:
                        task.due_at = datetime.fromisoformat(row["Due At"])
                    except ValueError:
                        pass
                
                db.session.add(task)
                count += 1
            
            db.session.commit()
            print(f"✅ Imported {count} tasks")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:")
        print("  Export: python export_import_csv.py export user@email.com output.csv")
        print("  Import: python export_import_csv.py import user@email.com input.csv")
        sys.exit(1)
    
    action = sys.argv[1]
    user_email = sys.argv[2]
    filename = sys.argv[3]
    
    if action == "export":
        export_tasks_csv(user_email, filename)
    elif action == "import":
        import_tasks_csv(user_email, filename)
    else:
        print(f"❌ Unknown action: {action}")

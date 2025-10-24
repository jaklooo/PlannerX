"""Seed development database with sample data."""
import sys
from pathlib import Path
from datetime import datetime, timedelta, date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.event import Event
from app.models.contact import Contact


def seed_dev_data():
    """Seed database with development data."""
    app = create_app("development")
    
    with app.app_context():
        print("🌱 Seeding development database...")
        
        # Create demo user
        user = User.query.filter_by(uid="demo_user").first()
        if not user:
            user = User(
                uid="demo_user",
                email="demo@plannerx.local",
                email_verified=True,
                digest_enabled=True
            )
            db.session.add(user)
            db.session.commit()
            print(f"✅ Created user: {user.email}")
        else:
            print(f"ℹ️  User already exists: {user.email}")
        
        # Create projects
        projects_data = [
            {"name": "Práca", "color": "#3B82F6"},
            {"name": "Osobné", "color": "#10B981"},
            {"name": "Domácnosť", "color": "#F59E0B"}
        ]
        
        projects = {}
        for proj_data in projects_data:
            project = Project.query.filter_by(
                user_id=user.id,
                name=proj_data["name"]
            ).first()
            
            if not project:
                project = Project(user_id=user.id, **proj_data)
                db.session.add(project)
                db.session.commit()
                print(f"✅ Created project: {project.name}")
            
            projects[proj_data["name"]] = project
        
        # Create tasks
        today = datetime.now()
        tasks_data = [
            {
                "title": "Dokončiť prezentáciu",
                "notes": "Pridať grafy a záver",
                "due_at": today + timedelta(hours=3),
                "priority": "HIGH",
                "status": "TODO",
                "project_id": projects["Práca"].id
            },
            {
                "title": "Nakúpiť potraviny",
                "notes": "Mlieko, chlieb, zelenina",
                "due_at": today + timedelta(hours=5),
                "priority": "MEDIUM",
                "status": "TODO",
                "project_id": projects["Domácnosť"].id
            },
            {
                "title": "Zavolať mamke",
                "notes": "",
                "due_at": today + timedelta(days=1),
                "priority": "MEDIUM",
                "status": "TODO",
                "project_id": projects["Osobné"].id
            },
            {
                "title": "Cvičenie",
                "notes": "30 minút",
                "due_at": today + timedelta(hours=2),
                "priority": "LOW",
                "status": "DOING",
                "project_id": projects["Osobné"].id
            },
            {
                "title": "Preplatený účet",
                "notes": "Urgentné!",
                "due_at": today - timedelta(days=2),
                "priority": "HIGH",
                "status": "TODO",
                "project_id": projects["Práca"].id
            }
        ]
        
        for task_data in tasks_data:
            task = Task(user_id=user.id, **task_data)
            db.session.add(task)
        
        db.session.commit()
        print(f"✅ Created {len(tasks_data)} tasks")
        
        # Create events
        events_data = [
            {
                "title": "Týmový meeting",
                "description": "Týždenný sync",
                "start_at": today + timedelta(hours=1),
                "end_at": today + timedelta(hours=2),
                "repeat_rule": "WEEKLY"
            },
            {
                "title": "Obed s kamarátmi",
                "description": "",
                "location": "Restaurant XYZ",
                "start_at": today + timedelta(hours=4),
                "end_at": today + timedelta(hours=5),
                "repeat_rule": "NONE"
            },
            {
                "title": "Ranná káva",
                "description": "Začiatok dňa",
                "start_at": datetime.combine(today.date(), datetime.min.time()) + timedelta(hours=7),
                "repeat_rule": "DAILY"
            }
        ]
        
        for event_data in events_data:
            event = Event(user_id=user.id, **event_data)
            db.session.add(event)
        
        db.session.commit()
        print(f"✅ Created {len(events_data)} events")
        
        # Create contacts
        contacts_data = [
            {
                "name": "Peter Novák",
                "email": "peter@example.com",
                "phone": "+421901234567",
                "birthday_date": date(1990, 5, 15),
                "name_day_date": date(2025, 6, 29)
            },
            {
                "name": "Mária Kováčová",
                "email": "maria@example.com",
                "birthday_date": date(1985, 8, 22),
                "name_day_date": date(2025, 3, 25)
            },
            {
                "name": "Ján Horváth",
                "phone": "+421907654321",
                "birthday_date": date.today(),  # Today's birthday!
                "name_day_date": date(2025, 6, 24),
                "notes": "Bratranec"
            }
        ]
        
        for contact_data in contacts_data:
            contact = Contact(user_id=user.id, **contact_data)
            db.session.add(contact)
        
        db.session.commit()
        print(f"✅ Created {len(contacts_data)} contacts")
        
        print("\n🎉 Seeding complete!")
        print(f"\n📧 Demo user: {user.email}")
        print(f"🔑 Dev token: dev_demo_user:demo@plannerx.local")


if __name__ == "__main__":
    seed_dev_data()

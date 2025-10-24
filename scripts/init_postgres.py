"""Initialize PostgreSQL database for PlannerX."""
import os
from dotenv import load_dotenv
from app import create_app, db

# Load environment variables
load_dotenv()

def init_postgres():
    """Initialize PostgreSQL database."""
    print("🚀 Initializing PostgreSQL database...")

    # Create app with production config to use PostgreSQL
    app = create_app('production')

    with app.app_context():
        try:
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")

            # Optional: Seed with demo data
            print("🌱 Seeding demo data...")
            seed_demo_data()
            print("✅ Demo data seeded successfully!")

            print("🎉 PostgreSQL database is ready!")

        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            print("💡 Make sure DATABASE_URL is set correctly in .env")
            print("💡 For local development, you can use SQLite by leaving DATABASE_URL empty")
            return False

    return True

def seed_demo_data():
    """Seed database with demo data."""
    from app.models.user import User
    from app.models.task import Task
    from app.models.event import Event
    from app.models.contact import Contact
    from datetime import datetime, timedelta

    # Create demo user if not exists
    demo_user = User.query.filter_by(email='demo@plannerx.local').first()
    if not demo_user:
        demo_user = User(
            email='demo@plannerx.local',
            name='Demo User',
            digest_enabled=True,
            sms_enabled=False
        )
        db.session.add(demo_user)
        db.session.commit()

    # Add some demo tasks
    if not Task.query.filter_by(user_id=demo_user.id).first():
        tasks = [
            Task(
                user_id=demo_user.id,
                title='Dokončiť PlannerX aplikáciu',
                description='Finalizovať všetky features a deploynúť',
                priority='HIGH',
                status='IN_PROGRESS',
                due_at=datetime.now() + timedelta(days=1)
            ),
            Task(
                user_id=demo_user.id,
                title='Prečítať si AI sumarizáciu',
                description='Pozrieť si ako funguje nový AI súhrn noviniek',
                priority='MEDIUM',
                status='TODO',
                due_at=datetime.now() + timedelta(days=2)
            )
        ]
        db.session.add_all(tasks)

    # Add demo contact
    if not Contact.query.filter_by(user_id=demo_user.id).first():
        contact = Contact(
            user_id=demo_user.id,
            name='Ján Novák',
            email='jan.novak@example.com',
            phone='+421 123 456 789',
            birthday=datetime(1990, 5, 15).date()
        )
        db.session.add(contact)

    db.session.commit()

if __name__ == "__main__":
    success = init_postgres()
    if success:
        print("\n🎯 Next steps:")
        print("1. Run: python wsgi.py")
        print("2. Visit: http://localhost:5000")
        print("3. Login with: demo@plannerx.local")
    else:
        print("\n🔧 To use SQLite instead (for development):")
        print("1. Leave DATABASE_URL empty in .env")
        print("2. Run: python wsgi.py")
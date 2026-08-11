"""
Seed script - Creates a demo user for testing
Run: python -m app.seed
OR in Docker: docker exec notes-backend python -m app.seed
"""

from app import create_app
from app.extensions import db
from app.models import User, Folder, Tag, Note

app = create_app()

def seed():
    with app.app_context():
        # Create tables if not exist
        db.create_all()
        
        # Check if demo user exists
        existing = User.query.filter_by(email="demo@textnotes.com").first()
        if existing:
            print("✅ Demo user already exists")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@textnotes.com",
            username="demo"
        )
        demo_user.set_password("password123")
        db.session.add(demo_user)
        db.session.flush()  # Get ID
        
        # Create sample folders
        folders = [
            Folder(name="Personal", owner_id=demo_user.id),
            Folder(name="Work", owner_id=demo_user.id),
            Folder(name="Ideas", owner_id=demo_user.id),
        ]
        db.session.add_all(folders)
        db.session.flush()
        
        # Create sample tags
        tags = [
            Tag(name="important", color="#ef4444", owner_id=demo_user.id),
            Tag(name="work", color="#3b82f6", owner_id=demo_user.id),
            Tag(name="personal", color="#22c55e", owner_id=demo_user.id),
            Tag(name="ideas", color="#eab308", owner_id=demo_user.id),
        ]
        db.session.add_all(tags)
        db.session.flush()
        
        # Create sample notes
        notes = [
            Note(
                title="Welcome to TextNotes! 🎉",
                content="""# Welcome to TextNotes!

This is your **new** notes application. Here's what you can do:

## Features
- ✅ Create and edit notes with Markdown support
- ✅ Organize notes into folders
- ✅ Add tags for easy filtering
- ✅ Pin important notes
- ✅ Archive old notes

## Getting Started
1. Click **"New Note"** to create your first note
2. Use the sidebar to navigate between Folders and Tags
3. Search through all your notes instantly

Happy note-taking! 📝""",
                is_pinned=True,
                owner_id=demo_user.id,
                folder_id=folders[0].id,  # Personal
                tags=[tags[0], tags[2]],  # important, personal
            ),
            Note(
                title="Project Meeting Notes",
                content="""# Project Meeting - Q4 Planning

## Attendees
- Team Lead
- Developer
- Designer

## Action Items
- [ ] Review project timeline
- [ ] Update documentation
- [ ] Schedule follow-up meeting

## Key Decisions
1. Move to microservices architecture
2. Adopt TypeScript for new features
3. Implement CI/CD pipeline""",
                owner_id=demo_user.id,
                folder_id=folders[1].id,  # Work
                tags=[tags[1], tags[0]],  # work, important
            ),
            Note(
                title="App Ideas",
                content="""# App Ideas 💡

## Ideas List
1. AI-powered task manager
2. Social reading app
3. Fitness tracker with gamification
4. Recipe organizer with meal planning

## Next Steps
- Research competitors
- Create MVP roadmap
- Design wireframes""",
                owner_id=demo_user.id,
                folder_id=folders[2].id,  # Ideas
                tags=[tags[3], tags[0]],  # ideas, important
            ),
            Note(
                title="Shopping List",
                content="""# Shopping List 🛒

## Groceries
- [ ] Milk
- [ ] Eggs
- [ ] Bread
- [ ] Coffee
- [ ] Vegetables

## Other Items
- [ ] Paper towels
- [ ] Dish soap""",
                is_archived=True,
                owner_id=demo_user.id,
                folder_id=folders[0].id,  # Personal
                tags=[tags[2]],  # personal
            ),
        ]
        db.session.add_all(notes)
        db.session.commit()
        
        print("✅ Demo data created successfully!")
        print(f"   User: demo@textnotes.com / password123")
        print(f"   Created {len(folders)} folders")
        print(f"   Created {len(tags)} tags")
        print(f"   Created {len(notes)} notes")

if __name__ == "__main__":
    seed()

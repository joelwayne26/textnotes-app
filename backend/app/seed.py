"""
Seed script - Creates a demo user for testing
Run: python -m app.seed
OR in Docker: docker exec notes-backend python -m app.seed
"""

import asyncio
from sqlalchemy import select
from app.extensions import sync_engine, Base
from app.models import User, Folder, Tag, Note, note_tags


def seed():
    """Synchronous seed function for initial data creation"""
    
    # Create tables if not exist (using sync engine for Alembic compatibility)
    Base.metadata.create_all(sync_engine)
    
    from sqlalchemy.orm import Sessionmaker
    session = Sessionmaker(bind=sync_engine)
    db = session()
    
    try:
        # Check if demo user exists
        result = db.execute(
            select(User).where(User.email == "demo@textnotes.com")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✅ Demo user already exists")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@textnotes.com",
            username="demo"
        )
        demo_user.set_password("password123")
        db.add(demo_user)
        db.flush()  # Get ID
        
        # Create sample folders
        folders = [
            Folder(name="Personal", owner_id=demo_user.id),
            Folder(name="Work", owner_id=demo_user.id),
            Folder(name="Ideas", owner_id=demo_user.id),
        ]
        db.add_all(folders)
        db.flush()
        
        # Create sample tags
        tags = [
            Tag(name="important", color="#ef4444", owner_id=demo_user.id),
            Tag(name="work", color="#3b82f6", owner_id=demo_user.id),
            Tag(name="personal", color="#22c55e", owner_id=demo_user.id),
            Tag(name="ideas", color="#eab308", owner_id=demo_user.id),
        ]
        db.add_all(tags)
        db.flush()
        
        # Create sample notes
        notes_data = [
            {
                "title": "Welcome to TextNotes! 🎉",
                "content": """# Welcome to TextNotes!

This is your **new** notes application built with **FastAPI**! Here's what you can do:

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
                "is_pinned": True,
                "folder_idx": 0,
                "tag_indices": [0, 2],
            },
            {
                "title": "Project Meeting Notes",
                "content": """# Project Meeting - Q4 Planning

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
                "is_pinned": False,
                "folder_idx": 1,
                "tag_indices": [1, 0],
            },
            {
                "title": "App Ideas 💡",
                "content": """# App Ideas

## Ideas List
1. AI-powered task manager
2. Social reading app
3. Fitness tracker with gamification
4. Recipe organizer with meal planning

## Next Steps
- Research competitors
- Create MVP roadmap
- Design wireframes""",
                "is_pinned": False,
                "folder_idx": 2,
                "tag_indices": [3, 0],
            },
            {
                "title": "Shopping List 🛒",
                "content": """# Shopping List

## Groceries
- [ ] Milk
- [ ] Eggs
- [ ] Bread
- [ ] Coffee
- [ ] Vegetables

## Other Items
- [ ] Paper towels
- [ ] Dish soap""",
                "is_pinned": False,
                "is_archived": True,
                "folder_idx": 0,
                "tag_indices": [2],
            },
        ]
        
        created_notes = []
        for note_data in notes_data:
            note = Note(
                title=note_data["title"],
                content=note_data["content"],
                is_pinned=note_data.get("is_pinned", False),
                is_archived=note_data.get("is_archived", False),
                owner_id=demo_user.id,
                folder_id=folders[note_data["folder_idx"]].id,
            )
            
            # Add tags
            for tag_idx in note_data.get("tag_indices", []):
                note.tags.append(tags[tag_idx])
            
            db.add(note)
            created_notes.append(note)
        
        db.commit()
        
        print("✅ Demo data created successfully!")
        print(f"   User: demo@textnotes.com / password123")
        print(f"   Created {len(folders)} folders")
        print(f"   Created {len(tags)} tags")
        print(f"   Created {len(created_notes)} notes")
        print("\n🚀 FastAPI is now running at http://localhost:5000")
        print("📚 API Docs available at http://localhost:5000/docs")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating seed data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

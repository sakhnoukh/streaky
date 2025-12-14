#!/usr/bin/env python3
"""
Check Alembic migration status and provide instructions
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from alembic import command
    from alembic.config import Config
    from app.config import settings
    
    print("🔍 Checking migration status...")
    print(f"📊 Database: {settings.database_url_computed.split('@')[-1] if '@' in settings.database_url_computed else settings.database_url_computed}")
    print()
    
    # Load Alembic config
    alembic_cfg = Config("alembic.ini")
    
    # Get current revision
    try:
        from alembic.script import ScriptDirectory
        script = ScriptDirectory.from_config(alembic_cfg)
        head = script.get_current_head()
        
        print(f"✅ Latest migration (head): {head}")
        
        # Try to get current database revision
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.database_url_computed)
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
            if current_rev:
                print(f"📌 Current database revision: {current_rev}")
                if current_rev == head:
                    print("✅ Database is up to date!")
                else:
                    print(f"⚠️  Database is behind. Run: alembic upgrade head")
            else:
                print("⚠️  No migrations applied yet. Run: alembic upgrade head")
                
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        print()
        print("💡 Try running: alembic upgrade head")
        
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("💡 Install with: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("💡 To apply migrations manually:")
    print("   alembic upgrade head")

#!/usr/bin/env python3
"""
Automatic .env file migration script for KNUST Student Registration System
This script will update your .env file with the correct variable names.
"""

import os
import shutil
from datetime import datetime

def migrate_env_file():
    """Migrate .env file from old variable names to new ones."""
    
    env_file = '.env'
    backup_file = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    if not os.path.exists(env_file):
        print("❌ No .env file found. Please create one first.")
        return False
    
    print("🔍 Reading current .env file...")
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Create backup
    shutil.copy2(env_file, backup_file)
    print(f"💾 Backup created: {backup_file}")
    
    # Migration mappings
    migrations = {
        'SUPABASE_KEY': 'SUPABASE_SERVICE_ROLE_KEY',
        'JWT_SECRET': 'SECRET_KEY'
    }
    
    migrated_lines = []
    changes_made = False
    
    # Process each line
    for line in lines:
        original_line = line
        
        # Skip comments and empty lines
        if line.strip().startswith('#') or not line.strip():
            migrated_lines.append(line)
            continue
        
        # Check for variables that need migration
        for old_var, new_var in migrations.items():
            if line.startswith(f'{old_var}='):
                # Extract the value
                value = line.split('=', 1)[1].strip()
                # Create new line with new variable name
                line = f'{new_var}={value}\n'
                changes_made = True
                print(f"🔄 Migrated: {old_var} → {new_var}")
                break
        
        migrated_lines.append(line)
    
    # Check if SUPABASE_ANON_KEY exists
    has_anon_key = any(line.startswith('SUPABASE_ANON_KEY=') for line in migrated_lines)
    
    if not has_anon_key:
        print("⚠️  SUPABASE_ANON_KEY not found. Adding placeholder...")
        migrated_lines.append('\n# TODO: Add your Supabase anon key from Dashboard > Settings > API\n')
        migrated_lines.append('SUPABASE_ANON_KEY=your_anon_key_here\n')
        changes_made = True
    
    # Write the migrated file
    if changes_made:
        with open(env_file, 'w') as f:
            f.writelines(migrated_lines)
        print("✅ Migration completed successfully!")
        print(f"📁 Original file backed up as: {backup_file}")
        
        if not has_anon_key:
            print("\n🔑 IMPORTANT: Please update SUPABASE_ANON_KEY with your actual anon key from Supabase Dashboard")
            
        return True
    else:
        print("✅ No migration needed. Your .env file is already up to date!")
        # Remove unnecessary backup
        os.remove(backup_file)
        return True

def validate_env_file():
    """Validate the migrated .env file."""
    print("\n🔍 Validating .env file...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_ANON_KEY',
        'SECRET_KEY',
        'EMAIL_HOST',
        'EMAIL_USER',
        'EMAIL_PASSWORD'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    with open('.env', 'r') as f:
        content = f.read()
    
    for var in required_vars:
        if f'{var}=' not in content:
            missing_vars.append(var)
        elif f'{var}=your_' in content or f'{var}=your-' in content:
            placeholder_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    if placeholder_vars:
        print(f"⚠️  Placeholder values need to be updated: {', '.join(placeholder_vars)}")
        return False
    
    print("✅ .env file validation passed!")
    return True

def main():
    """Main migration function."""
    print("🚀 KNUST Student Registration System - .env Migration Tool")
    print("=" * 60)
    
    # Perform migration
    if migrate_env_file():
        # Validate the result
        if validate_env_file():
            print("\n🎉 Migration completed successfully!")
            print("You can now start your server with: uvicorn main:app --reload")
        else:
            print("\n⚠️  Migration completed but validation failed.")
            print("Please check the warnings above and update your .env file accordingly.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

if __name__ == '__main__':
    main()
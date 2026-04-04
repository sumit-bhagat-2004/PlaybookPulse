"""Reset demo environment script"""
import os
import shutil


def reset_demo_env():
    """Reset demo environment by clearing temporary files"""
    
    files_to_remove = [
        'playbook_pulse.db',
        'demo_analysis_result.json',
        'logs/app.log'
    ]
    
    print("Resetting demo environment...")
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ Removed: {file}")
            except Exception as e:
                print(f"✗ Failed to remove {file}: {e}")
        else:
            print(f"- Not found: {file}")
    
    print("\nDemo environment reset complete!")


if __name__ == "__main__":
    reset_demo_env()

"""Setup script for loading compliance framework data"""
import json
import os


def setup_compliance_data():
    """Verify compliance data files exist"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'compliance')
    
    frameworks = ['nist_sp_800_61.json', 'soc2_cc7.json', 'iso_27001_a16.json']
    
    print("Checking compliance framework data...")
    for framework in frameworks:
        filepath = os.path.join(data_dir, framework)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                print(f"✓ {framework}: {data.get('name', 'Unknown')} loaded")
        else:
            print(f"✗ {framework}: NOT FOUND")
    
    print("\nCompliance data check complete!")


if __name__ == "__main__":
    setup_compliance_data()

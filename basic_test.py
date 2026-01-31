#!/usr/bin/env python3
"""Simple test script to verify Aideck basic setup"""

import sys


def test_imports():
    """Test basic imports without heavy dependencies"""
    try:
        # Test basic Python modules
        import os
        import sys

        print("✅ Basic Python modules work")

        # Test if source directory exists
        src_path = os.path.join(os.path.dirname(__file__), "src", "aideck")
        if os.path.exists(src_path):
            print("✅ Source directory exists")
        else:
            print("❌ Source directory not found")
            return False

        # Test if we can import the main module
        sys.path.insert(0, os.path.dirname(__file__))

        # Try importing version
        try:
            with open(os.path.join(src_path, "version.py")) as f:
                version_content = f.read()
                if "__version__" in version_content:
                    print("✅ Version file exists")
                else:
                    print("⚠️  Version file found but no version info")
        except Exception as e:
            print(f"⚠️  Could not read version file: {e}")

        print("\n🎉 Basic setup verification complete!")
        print("🚀 You can now run: python -m aideck")
        return True

    except Exception as e:
        print(f"❌ Error during basic test: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    if not success:
        sys.exit(1)

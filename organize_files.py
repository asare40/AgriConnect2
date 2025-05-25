import os
import shutil

# Define where files should go based on their name or type
BACKEND_FILES = ['api.py', 'models.py', 'database.py', 'requirements.txt']
FRONTEND_FILES = ['package.json', 'package-lock.json', 'yarn.lock']

# Create folders if they don't exist
os.makedirs('backend', exist_ok=True)
os.makedirs('frontend/src/components', exist_ok=True)
os.makedirs('frontend/src/api', exist_ok=True)

# Move backend files
for f in BACKEND_FILES:
    if os.path.exists(f):
        shutil.move(f, os.path.join('backend', f))

# Move frontend config files
for f in FRONTEND_FILES:
    if os.path.exists(f):
        shutil.move(f, os.path.join('frontend', f))

# Move React src files
for f in os.listdir('.'):
    if f.endswith('.jsx') or f.endswith('.js'):
        if 'Form' in f:
            shutil.move(f, os.path.join('frontend', 'src', 'components', f))
        elif f == 'api.js':
            shutil.move(f, os.path.join('frontend', 'src', 'api', f))
        elif f in ['App.jsx', 'index.js']:
            shutil.move(f, os.path.join('frontend', 'src', f))

print("Files organized into backend/ and frontend/ structure!")
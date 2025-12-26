# EnvMan - Executable Environment Management CLI

🚀 **A standalone executable for managing project environment files**

## 🎯 Quick Installation

```bash
# Option 1: Download and run installer
./install.sh

# Option 2: Manual installation
cp dist/envman ~/.local/bin/envman
chmod +x ~/.local/bin/envman
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 🚀 Usage

```bash
envman add .env          # Store current .env file
envman get .env          # Retrieve stored .env file
envman update .env       # Update with local changes
envman delete .env       # Delete from storage
envman list              # Show stored files for current project
envman projects          # List all managed projects
```

## 🎯 Key Features

- ✅ **Standalone executable** - No Python environment needed
- ✅ **Automatic project detection** - Git repo or directory name
- ✅ **JSON storage** - Simple, portable format
- ✅ **Zero setup** - Just run and use

## 📁 Storage

All environment files are stored in `~/.envman/data.json`

## 🔧 Building from Source

```bash
git clone <repo>
cd envman
uv install
uv run pyinstaller --onefile envman.py --name envman
```

## 📝 Example

```bash
$ cd my-project
$ echo "API_KEY=secret123" > .env
$ envman add .env
Added '.env' to project 'my-project'.

$ rm .env
$ envman get .env  
Restored '.env' to '.env'.

$ cat .env
API_KEY=secret123
```
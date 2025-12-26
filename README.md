# 🌍 EnvMan - Simple Environment File Manager

[![Executable](https://img.shields.io/badge/-Executable-blue?style=flat-square)](https://github.com/yourusername/envman)
[![No Dependencies](https://img.shields.io/badge/-No%20Dependencies-green?style=flat-square)](https://github.com/yourusername/envman)
[![Python](https://img.shields.io/badge/-Python%203.8+-yellow?style=flat-square)](https://github.com/yourusername/envman)

> **Zero-hassle CLI for managing project environment files with automatic project detection**

---

## ✨ Why EnvMan?

Tired of juggling multiple `.env` files across different projects? Envman makes environment management effortless:

🚀 **Auto-detects your project** from Git repo or folder name
💾 **Simple JSON storage** - portable, human-readable, version-control friendly
⚡ **Zero setup** - download and run, no installation required
🔄 **Whole-file operations** - preserves formatting, comments, and structure
🎯 **Project-aware** - automatically knows which project you're working on

---

## 🚀 Quick Start

### One-command installation:
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/envman/main/install.sh | bash
```

### Or download the executable:
```bash
wget https://github.com/yourusername/envman/releases/latest/download/envman-linux-x64
chmod +x envman-linux-x64
sudo mv envman-linux-x64 /usr/local/bin/envman
```

### Ready to use:
```bash
cd your-project
echo "API_KEY=secret123\nDEBUG=true" > .env
envman add .env        # Store it
rm .env                # Delete local copy
envman get .env        # Retrieve it back
cat .env               # ✅ Perfectly preserved
```

---

## 🎯 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Store environment file | `envman add .env` |
| `get` | Retrieve stored file | `envman get .env --output .env.local` |
| `update` | Update with local changes | `envman update .env` |
| `delete` | Remove from storage | `envman delete .env` |
| `list` | Show project files | `envman list` |
| `projects` | List all projects | `envman projects` |

---

## 🏗️ How It Works

Envman automatically detects your project name using:

1. **Git repository name** (from `git remote get-url origin`)
2. **Current directory name** (fallback)

All your environment files are stored in `~/.envman/data.json`:

```json
{
  "projects": {
    "my-awesome-app": {
      "env_files": {
        ".env": "API_KEY=secret123\nDEBUG=true\nPORT=3000",
        "production.env": "API_KEY=prod-key\nDEBUG=false\nPORT=443"
      }
    }
  }
}
```

---

## 🌟 Perfect For

🔄 **Team collaboration** - Share environment configurations easily
⚙️ **CI/CD pipelines** - Store multiple environment variants
🛠️ **Development workflows** - Switch between staging/production configs
🔐 **Security** - Keep sensitive files out of version control
📦 **Docker/Containers** - Manage environment files for different services

---

## 📦 Downloads

| Platform | Download |
|----------|----------|
| Linux x64 | `envman-linux-x64` |
| macOS x64 | `envman-macos-x64` |
| macOS ARM64 | `envman-macos-arm64` |
| Windows x64 | `envman-win-x64.exe` |

👉 [All Releases](https://github.com/yourusername/envman/releases)

---

## 🛠️ Development

```bash
git clone https://github.com/yourusername/envman
cd envman
uv install
uv run pyinstaller --onefile envman.py --name envman
```

---

## 📄 License

MIT License - feel free to use this in your projects!

---

**⭐ Star this repo if Envman makes your development life easier!**

Made with ❤️ by developers, for developers

</div>

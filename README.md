# 🌍 EnvMan - Environment File Manager

> CLI for managing project environment files with encryption and cross-project access

---

## ✨ Features

- **Auto-detects project** from Git repo or folder name
- **SQLite storage** - fast, reliable, portable
- **Encrypted at rest** - AES-256 via system keychain
- **Cross-project access** - fetch envs from any project
- **Multiple files per project** - `.env`, `.env.local`, `.env.production`, etc.

---

## 🚀 Quick Start

```bash
# Install
cd envman
uv pip install -e .
source .venv/bin/activate
ln -sf .venv/bin/envman ~/.local/bin/envman

# Use
cd your-project
envman add .env        # Store (encrypted)
rm .env                # Delete local copy
envman get             # Retrieve decrypted
envman get -p other-project  # Fetch from another project
```

---

## 📖 Commands

### Files
| Command | Description |
|---------|-------------|
| `envman add [.env]` | Store local env file (encrypts automatically) |
| `envman get [-p project]` | Retrieve decrypted env file |
| `envman update [.env]` | Update with local changes |
| `envman delete [.env]` | Remove from storage |
| `envman list [-p project]` | List stored files |

### Projects
| Command | Description |
|---------|-------------|
| `envman projects list` | List all managed projects |
| `envman projects delete <name>` | Delete a project and all its files |

---

## 🔐 Encryption

EnvMan uses **Fernet encryption** (AES-128-CBC + HMAC-SHA256) with the encryption key stored in your system's keychain:

- **Linux**: Secret Service (GNOME Keyring, KWallet)
- **macOS**: Keychain
- **Windows**: Credential Manager

The key is created automatically on first use. All stored env files are encrypted.

---

## 💾 Storage

Location: `~/.envman/data.db`

Tables:
- `projects` - project names
- `env_files` - encrypted file contents (project_name, filename, content)

---

## 🛠️ Development

```bash
git clone https://github.com/adityamiskin/envman
cd envman
uv pip install -e .
uv run pyinstaller --onefile envman.py --name envman
```

---

## 📄 License

MIT

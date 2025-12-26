#!/bin/bash

# Install envman CLI tool

echo "🚀 Installing envman..."

# Create directories
mkdir -p ~/.local/bin
mkdir -p ~/.envman

# Copy executable
cp dist/envman ~/.local/bin/envman
chmod +x ~/.local/bin/envman

# Add to PATH if not already there
if ! echo $PATH | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
    echo "✅ Added ~/.local/bin to PATH"
fi

echo "✅ envman installed successfully!"
echo "📝 Restart your terminal or run: source ~/.bashrc"
echo "🎯 Usage: envman --help"
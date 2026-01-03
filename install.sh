#!/bin/bash
set -e

REPO="adityamiskin/envman"
INSTALL_DIR="${HOME}/.local/bin"
RELEASE_URL="https://api.github.com/repos/${REPO}/releases/latest"

detect_os() {
    case "$(uname -s)" in
        Linux*)  echo "linux" ;;
        Darwin*) echo "macos" ;;
        *)       echo "unknown" ;;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64)  echo "x86_64" ;;
        aarch64|arm64) echo "arm64" ;;
        *)             echo "x86_64" ;;
    esac
}

get_download_url() {
    local os=$1
    local arch=$2

    local asset_pattern="envman-${os}-${arch}"

    curl -sS "${RELEASE_URL}" | \
        grep -o "\"browser_download_url\": \"[^\"]*${asset_pattern}[^\"]*\"" | \
        cut -d'"' -f4 | \
        head -n1
}

download_and_install() {
    local os=$1
    local arch=$2
    local url

    echo "🚀 Detected: ${os}-${arch}"
    url=$(get_download_url "${os}" "${arch}")

    if [ -z "${url}" ]; then
        echo "❌ No binary found for ${os}-${arch}"
        exit 1
    fi

    echo "⬇️  Downloading from ${url}"

    local temp_dir
    temp_dir=$(mktemp -d)
    local archive_file="${temp_dir}/envman.tar.gz"

    curl -sSL -o "${archive_file}" "${url}"
    tar -xzf "${archive_file}" -C "${temp_dir}"

    mkdir -p "${INSTALL_DIR}"
    cp "${temp_dir}/envman" "${INSTALL_DIR}/envman"
    chmod +x "${INSTALL_DIR}/envman"

    rm -rf "${temp_dir}"

    echo "✅ Installed to ${INSTALL_DIR}/envman"
}

add_to_path() {
    if ! echo "${PATH}" | grep -q "${INSTALL_DIR}"; then
        echo "📝 Adding ${INSTALL_DIR} to PATH..."

        for rcfile in "${HOME}/.bashrc" "${HOME}/.zshrc" "${HOME}/.bash_profile" "${HOME}/.profile"; do
            if [ -f "${rcfile}" ]; then
                if ! grep -q "export PATH=\"${INSTALL_DIR}" "${rcfile}" 2>/dev/null; then
                    echo "export PATH=\"${INSTALL_DIR}:\$PATH\"" >> "${rcfile}"
                fi
            fi
        done

        echo "✅ Added to shell config"
    fi
}

check_dependencies() {
    if ! command -v curl &> /dev/null; then
        echo "❌ curl is required but not installed"
        exit 1
    fi
}

main() {
    check_dependencies

    echo "🌍 Installing envman..."

    local os arch
    os=$(detect_os)
    arch=$(detect_arch)

    if [ "${os}" = "unknown" ]; then
        echo "❌ Unsupported operating system"
        exit 1
    fi

    download_and_install "${os}" "${arch}"
    add_to_path

    echo ""
    echo "✅ envman installed successfully!"
    echo "📝 Restart your terminal or run: source ~/.bashrc"
    echo "🎯 Usage: envman --help"
}

main

#!/usr/bin/env bash
# Instala o bot do Guia de Salas como servico do systemd (Raspberry Pi OS ou outro Linux com systemd).
# Uso, na pasta do projeto: bash deploy/instalar_raspberry.sh
set -euo pipefail

PASTA="$(cd "$(dirname "$0")/.." && pwd)"
USUARIO="$(id -un)"
SERVICO=guia-salas-bot

cd "$PASTA"

echo "Instalando dependencias do sistema"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip

echo "Criando ambiente virtual em $PASTA/.venv"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

if [ ! -f .env ]; then
    cp .env.example .env
fi
if ! grep -q '^TELEGRAM_TOKEN=.\+' .env; then
    read -r -s -p "Token do bot (BotFather): " TOKEN
    echo
    sed -i "s|^TELEGRAM_TOKEN=.*|TELEGRAM_TOKEN=$TOKEN|" .env
fi
chmod 600 .env

echo "Criando o servico $SERVICO"
sudo tee /etc/systemd/system/$SERVICO.service > /dev/null <<UNIT
[Unit]
Description=Guia de Salas (bot do Telegram)
After=network-online.target
Wants=network-online.target

[Service]
User=$USUARIO
WorkingDirectory=$PASTA
EnvironmentFile=$PASTA/.env
ExecStart=$PASTA/.venv/bin/python -m guia_salas --telegram
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now $SERVICO
sleep 3
sudo systemctl --no-pager status $SERVICO | head -n 5
echo "Pronto. Para ver o registro: journalctl -u $SERVICO -f"

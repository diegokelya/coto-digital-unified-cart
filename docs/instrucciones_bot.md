# 🤖 Configuración del Bot Persistente de Coto Digital

## ⚠️ IMPORTANTE: Seguridad

**NO pegues el token del bot en el chat de Hermes** — seguí estos pasos que NO muestran el token en pantalla.

---

## 📋 Paso 1: Crear el bot en Telegram

1. Abrí **Telegram** en tu teléfono o computadora
2. Buscá: `@BotFather`
3. Enviá: `/newbot`
4. **Nombre del bot:** `Coto Digital Bot` (o el que prefieras)
5. **Username del bot:** `diego_coto_bot` (debe terminar en `_bot`)
6. **Copiá el token** que te da BotFather (ejemplo: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## 📋 Paso 2: Guardar el token DE FORMA SEGURA

**Ejecutá esto en la terminal** (el token NO se mostrará en pantalla):

```bash
read -rsp "Pegá el token del bot: " TOKEN
printf '\nCOTO_TELEGRAM_BOT_TOKEN=%s\n' "$TOKEN" >> ~/.hermes/.env
unset TOKEN
chmod 600 ~/.hermes/.env
echo "✓ Token guardado de forma segura"
```

Cuando te pida el token, **pegalo** y presioná Enter.

---

## 📋 Paso 3: Obtener tu Chat ID

1. **Enviá `/start`** al bot nuevo en Telegram
2. **Ejecutá esto en la terminal:**

```bash
set -a
source ~/.hermes/.env
set +a
python3 /home/diego/.hermes/scripts/get_telegram_chat_id.py
```

3. **Copiá el número** de `Chat ID` que te muestre (ejemplo: `406287065`)

---

## 📋 Paso 4: Guardar el Chat ID

```bash
echo 'COTO_TELEGRAM_CHAT_ID=TU_CHAT_ID' >> ~/.hermes/.env
```

Reemplazá `TU_CHAT_ID` por el número que obtuviste en el paso 3.

---

## ✅ Verificar configuración

```bash
source ~/.hermes/.env
echo "Token configurado: ${COTO_TELEGRAM_BOT_TOKEN:0:10}..."
echo "Chat ID configurado: $COTO_TELEGRAM_CHAT_ID"
```

Deberías ver:
```
Token configurado: 1234567890...
Chat ID configurado: 406287065
```

---

## 🚀 Probar el bot manualmente

```bash
python3 /home/diego/.hermes/scripts/coto_telegram_bot.py
```

Luego:
1. Enviá `/ayuda` al bot en Telegram
2. Verificá que responda
3. Presioná `Ctrl+C` en la terminal para detener el bot

---

## 🔧 Instalar como servicio (auto-inicio)

```bash
sudo cp /home/diego/.hermes/scripts/coto-telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable coto-telegram-bot
sudo systemctl start coto-telegram-bot
```

Verificar estado:
```bash
sudo systemctl status coto-telegram-bot
```

Ver logs en tiempo real:
```bash
journalctl -u coto-telegram-bot -f
```

---

## 📊 Comandos de gestión

**Iniciar el bot:**
```bash
sudo systemctl start coto-telegram-bot
```

**Detener el bot:**
```bash
sudo systemctl stop coto-telegram-bot
```

**Reiniciar el bot:**
```bash
sudo systemctl restart coto-telegram-bot
```

**Ver logs:**
```bash
journalctl -u coto-telegram-bot -n 50
```

**Deshabilitar auto-inicio:**
```bash
sudo systemctl disable coto-telegram-bot
```

---

## ✅ ¿Qué hace el bot?

Una vez corriendo, podés usar **directo desde Telegram**:

- 🔍 `/buscar coca cola` — Buscar productos en Coto
- ✏️ `/manual Leche La Serenísima 1L | 2809` — Agregar producto
- 🛒 `/carrito` — Ver tu carrito
- ➖ `/eliminar 5` — Quitar producto
- 🗑️ `/vaciar` — Vaciar carrito
- ✅ `/finalizar` — Generar resumen del pedido

**Cada cambio sincroniza automáticamente el dashboard de Home Assistant:**
→ `http://homeassistant.local:8123/pedido-coto/carrito`

---

## 🔒 Seguridad

✅ Bot dedicado (no interfiere con Hermes)  
✅ Token nunca expuesto en logs  
✅ Solo responde a tu chat_id  
✅ Auto-reinicio si falla  
✅ Límites de recursos (512MB RAM, 50% CPU)  
✅ Sin acceso a contraseñas de Coto Digital

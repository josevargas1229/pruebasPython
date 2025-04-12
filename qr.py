import qrcode

# Información del enlace de WhatsApp
numero = "527712320357"  # Número en formato internacional (Ejemplo: México: +52)
mensaje = "Hola, necesito una impresion."  # Mensaje predeterminado

# Formato del enlace1
url_whatsapp = f"https://wa.me/{numero}?text={mensaje.replace(' ', '%20')}"

# Crear el código QR
qr = qrcode.QRCode(
    version=1,  # Tamaño del QR
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel de corrección
    box_size=10,  # Tamaño de cada caja del QR
    border=4,  # Tamaño del borde
)
qr.add_data(url_whatsapp)
qr.make(fit=True)

# Generar imagen del QR
imagen_qr = qr.make_image(fill_color="black", back_color="white")

# Guardar el QR como archivo
imagen_qr.save("codigo_qr_whatsapp.png")

print("Código QR generado y guardado como 'codigo_qr_whatsapp.png'")

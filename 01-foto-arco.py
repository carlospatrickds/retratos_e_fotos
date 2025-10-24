from PIL import Image

# Caminho da imagem original
input_path = "foto_original.jpg"   # substitua pelo nome do seu arquivo
output_path = "foto_para_porta_retrato.jpg"

# Medidas em cm e conversão para pixels (300 DPI)
cm_to_px = 300 / 2.54
largura_total = int(10 * cm_to_px)   # 10 cm
altura_total = int(15 * cm_to_px)    # 15 cm

# Tamanho da área útil que será recortada depois (10x6 cm)
largura_final = int(10 * cm_to_px)
altura_final = int(6 * cm_to_px)

# Abre e redimensiona a imagem para caber na folha 10x15
img = Image.open(input_path)
img = img.convert("RGB")

# Mantém proporção
img.thumbnail((largura_total, altura_total))

# Cria fundo branco 10x15
fundo = Image.new("RGB", (largura_total, altura_total), (255, 255, 255))

# Centraliza a imagem no fundo
x = (largura_total - img.width) // 2
y = (altura_total - img.height) // 2
fundo.paste(img, (x, y))

# Salva imagem ajustada para impressão
fundo.save(output_path, "JPEG", quality=95, dpi=(300, 300))

print("✅ Imagem salva em formato 10x15 cm (300 DPI).")
print("Agora é só imprimir e recortar a parte de 10x6 cm para o porta-retrato.")

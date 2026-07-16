"""Gera PDFs fictícios e visualmente legíveis para testar o aplicativo."""

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tiktok_pdf_organizer.organizer import organize_pdfs  # noqa: E402


EXAMPLES = ROOT / "examples"

ORDERS = (
    ("A", "3320000000001", "Produto fictício A"),
    ("B", "3320000000002", "Produto fictício B"),
    ("C", "3320000000003", "Produto fictício C"),
)

PURPLE = HexColor("#7C3AC6")
GREEN = HexColor("#278D69")
BACKGROUND = HexColor("#F6F4FA")
TEXT = HexColor("#211B2A")
MUTED = HexColor("#6F6679")
BORDER = HexColor("#D9D3E2")
WARNING = HexColor("#B42348")


def _draw_fake_barcode(pdf: canvas.Canvas, tracking: str, x: float, y: float) -> None:
    cursor = x
    for index, digit in enumerate(tracking * 3):
        width = (1 + int(digit) % 3) * 0.35 * mm
        height = (14 + (index % 4) * 2) * mm
        pdf.setFillColor(TEXT)
        pdf.rect(cursor, y, width, height, stroke=0, fill=1)
        cursor += width + 0.45 * mm


def _draw_page(
    pdf: canvas.Canvas,
    *,
    document_type: str,
    order: tuple[str, str, str],
) -> None:
    page_width, page_height = A4
    letter, tracking, product = order
    accent = PURPLE if document_type == "ETIQUETA" else GREEN

    pdf.setFillColor(BACKGROUND)
    pdf.rect(0, 0, page_width, page_height, stroke=0, fill=1)

    pdf.setFillColor(accent)
    pdf.rect(0, page_height - 42 * mm, page_width, 42 * mm, stroke=0, fill=1)

    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 21)
    pdf.drawString(20 * mm, page_height - 23 * mm, f"{document_type} DE TESTE {letter}")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(20 * mm, page_height - 31 * mm, "ARQUIVO FICTÍCIO PARA VALIDAÇÃO DO PROJETO")

    pdf.setFillColor(white)
    pdf.roundRect(
        page_width - 63 * mm,
        page_height - 28 * mm,
        43 * mm,
        10 * mm,
        5 * mm,
        stroke=0,
        fill=1,
    )
    pdf.setFillColor(accent)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(page_width - 41.5 * mm, page_height - 24.5 * mm, "DADOS FICTÍCIOS")

    card_x = 20 * mm
    card_width = page_width - 40 * mm
    card_top = page_height - 62 * mm

    pdf.setFillColor(white)
    pdf.setStrokeColor(BORDER)
    pdf.roundRect(card_x, card_top - 47 * mm, card_width, 47 * mm, 4 * mm, stroke=1, fill=1)

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(card_x + 8 * mm, card_top - 11 * mm, "CÓDIGO DE RASTREIO")
    pdf.setFillColor(TEXT)
    pdf.setFont("Courier-Bold", 20)
    pdf.drawString(card_x + 8 * mm, card_top - 24 * mm, tracking)
    _draw_fake_barcode(pdf, tracking, card_x + 8 * mm, card_top - 42 * mm)

    details_top = card_top - 60 * mm
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(card_x, details_top, "Informações do pedido")

    pdf.setFillColor(white)
    pdf.setStrokeColor(BORDER)
    pdf.roundRect(card_x, details_top - 61 * mm, card_width, 52 * mm, 4 * mm, stroke=1, fill=1)

    rows = (
        ("Pedido", f"TESTE-{letter}-2026"),
        ("Produto", product),
        ("Quantidade", "1 unidade"),
    )
    row_y = details_top - 22 * mm
    for label, value in rows:
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(card_x + 8 * mm, row_y, label)
        pdf.setFillColor(TEXT)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(card_x + 43 * mm, row_y, value)
        row_y -= 13 * mm

    lower_top = details_top - 77 * mm
    lower_title = "Dados de entrega" if document_type == "ETIQUETA" else "Dados fiscais"
    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(card_x, lower_top, lower_title)

    pdf.setFillColor(white)
    pdf.setStrokeColor(BORDER)
    pdf.roundRect(card_x, lower_top - 58 * mm, card_width, 49 * mm, 4 * mm, stroke=1, fill=1)

    pdf.setFont("Helvetica", 10)
    if document_type == "ETIQUETA":
        pdf.setFillColor(TEXT)
        pdf.drawString(card_x + 8 * mm, lower_top - 23 * mm, "Destinatário: Cliente Fictício")
        pdf.drawString(card_x + 8 * mm, lower_top - 37 * mm, "Endereço: Rua de Teste, 123 - Cidade Exemplo")
    else:
        pdf.setFillColor(WARNING)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(card_x + 8 * mm, lower_top - 23 * mm, "DOCUMENTO SEM VALIDADE FISCAL")
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(card_x + 8 * mm, lower_top - 38 * mm, "Criado exclusivamente para testar o pareamento.")

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(page_width / 2, 17 * mm, "TikTok PDF Organizer - ambiente de teste")
    pdf.showPage()


def _create_pdf(path: Path, document_type: str, orders) -> None:
    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.setTitle(f"{document_type.title()} - dados fictícios")
    pdf.setAuthor("Luiz Othávio - TikTok PDF Organizer")
    for order in orders:
        _draw_page(pdf, document_type=document_type, order=order)
    pdf.save()


def main() -> None:
    EXAMPLES.mkdir(parents=True, exist_ok=True)

    labels = EXAMPLES / "01_etiquetas_teste.pdf"
    danfes = EXAMPLES / "02_danfes_teste_fora_de_ordem.pdf"
    expected = EXAMPLES / "03_resultado_esperado.pdf"

    _create_pdf(labels, "ETIQUETA", ORDERS)
    _create_pdf(danfes, "DANFE", (ORDERS[2], ORDERS[0], ORDERS[1]))
    result = organize_pdfs(labels, danfes, expected)

    print(f"Etiquetas: {labels}")
    print(f"DANFEs fora de ordem: {danfes}")
    print(f"Resultado esperado: {expected}")
    print(f"Pares gerados: {result.pairs}")


if __name__ == "__main__":
    main()

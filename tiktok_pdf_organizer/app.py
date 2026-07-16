"""Interface gráfica do TikTok PDF Organizer."""

from math import pi, sin
from pathlib import Path
from threading import Thread
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter

from .organizer import OrganizationResult, organize_pdfs


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720

BACKGROUND = "#130021"
GLASS = "#1C0C32"
GLASS_LIGHT = "#281244"
GLASS_BORDER = "#8C69D9"
FIELD = "#160826"
FIELD_BORDER = "#7654BD"
TEXT = "#FFF9FF"
MUTED = "#BFAED6"
PURPLE = "#A56AF4"
PURPLE_HOVER = "#8E55DF"
SUCCESS = "#8CF0C2"
ERROR = "#FF8CA7"


def _create_background(width: int, height: int) -> Image.Image:
    """Cria o fundo abstrato roxo usado pela interface."""

    image = Image.new("RGB", (width, height), BACKGROUND)
    pixels = image.load()

    top = (21, 0, 38)
    bottom = (48, 4, 80)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(
            int(start + (end - start) * ratio)
            for start, end in zip(top, bottom)
        )
        for x in range(width):
            pixels[x, y] = color

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (-180, -210, 470, 410),
        fill=(112, 31, 190, 150),
    )
    glow_draw.ellipse(
        (570, 330, 1190, 930),
        fill=(156, 55, 255, 125),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(95))
    image = Image.alpha_composite(image.convert("RGBA"), glow)

    ribbons = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ribbon_draw = ImageDraw.Draw(ribbons)

    upper_points = []
    lower_points = []
    for x in range(-120, width + 121, 8):
        upper_y = 100 + 92 * sin((x / width) * 2.2 * pi)
        lower_y = 590 + 100 * sin((x / width) * 2.0 * pi + 1.1)
        upper_points.append((x, int(upper_y)))
        lower_points.append((x, int(lower_y)))

    ribbon_draw.line(
        upper_points,
        fill=(169, 93, 255, 115),
        width=92,
        joint="curve",
    )
    ribbon_draw.line(
        lower_points,
        fill=(119, 45, 220, 130),
        width=110,
        joint="curve",
    )
    ribbon_draw.line(
        upper_points,
        fill=(225, 185, 255, 175),
        width=4,
        joint="curve",
    )
    ribbon_draw.line(
        lower_points,
        fill=(201, 139, 255, 165),
        width=4,
        joint="curve",
    )
    ribbons = ribbons.filter(ImageFilter.GaussianBlur(14))

    return Image.alpha_composite(image, ribbons).convert("RGB")


class FileSelector(ctk.CTkFrame):
    """Campo estilizado para selecionar e exibir um PDF."""

    def __init__(
        self,
        master,
        *,
        number: str,
        title: str,
        hint: str,
        command,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkFrame(self, fg_color="transparent")
        heading.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        heading.grid_columnconfigure(1, weight=1)

        number_label = ctk.CTkLabel(
            heading,
            text=number,
            width=28,
            height=28,
            corner_radius=14,
            fg_color="#6F3EB3",
            text_color=TEXT,
            font=("Segoe UI", 12, "bold"),
        )
        number_label.grid(row=0, column=0, padx=(0, 10))

        title_label = ctk.CTkLabel(
            heading,
            text=title,
            text_color=TEXT,
            font=("Segoe UI", 15, "bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=1, sticky="w")

        hint_label = ctk.CTkLabel(
            heading,
            text=hint,
            text_color=MUTED,
            font=("Segoe UI", 11),
            anchor="e",
        )
        hint_label.grid(row=0, column=2, sticky="e")

        field = ctk.CTkFrame(
            self,
            height=64,
            fg_color=FIELD,
            border_width=1,
            border_color=FIELD_BORDER,
            corner_radius=15,
        )
        field.grid(row=1, column=0, sticky="ew")
        field.grid_propagate(False)
        field.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(
            field,
            text="Nenhum arquivo selecionado",
            text_color="#8F7DA8",
            font=("Segoe UI", 12),
            anchor="w",
        )
        self.file_label.grid(row=0, column=0, padx=(18, 12), sticky="ew")

        self.button = ctk.CTkButton(
            field,
            text="Selecionar",
            width=122,
            height=40,
            corner_radius=11,
            fg_color=GLASS_LIGHT,
            hover_color="#3D2160",
            border_width=1,
            border_color="#A780EC",
            text_color=TEXT,
            font=("Segoe UI", 12, "bold"),
            command=command,
        )
        self.button.grid(row=0, column=1, padx=(0, 11), pady=11)

    def set_file(self, path: str) -> None:
        file_name = Path(path).name
        if len(file_name) > 48:
            file_name = f"{file_name[:22]}…{file_name[-22:]}"
        self.file_label.configure(text=file_name, text_color=TEXT)
        self.button.configure(text="Alterar")

    def set_enabled(self, enabled: bool) -> None:
        self.button.configure(state="normal" if enabled else "disabled")


class App(ctk.CTk):
    """Janela principal do aplicativo."""

    def __init__(self) -> None:
        super().__init__(fg_color=BACKGROUND)

        self.title("TikTok PDF Organizer")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        self.labels_pdf: str | None = None
        self.danfes_pdf: str | None = None

        background = _create_background(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.background_image = ctk.CTkImage(
            light_image=background,
            dark_image=background,
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        background_label = ctk.CTkLabel(self, text="", image=self.background_image)
        background_label.place(x=0, y=0)

        self._build_glass_panel()

    def _build_glass_panel(self) -> None:
        panel = ctk.CTkFrame(
            self,
            width=720,
            height=610,
            corner_radius=34,
            fg_color=GLASS,
            border_width=1,
            border_color=GLASS_BORDER,
        )
        panel.place(relx=0.5, rely=0.51, anchor="center")
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)

        logo = ctk.CTkLabel(
            panel,
            text="PDF",
            width=58,
            height=58,
            corner_radius=20,
            fg_color="#6D38AC",
            text_color=TEXT,
            font=("Segoe UI", 15, "bold"),
        )
        logo.grid(row=0, column=0, pady=(30, 10))

        title = ctk.CTkLabel(
            panel,
            text="TikTok PDF Organizer",
            text_color=TEXT,
            font=("Segoe UI", 27, "bold"),
        )
        title.grid(row=1, column=0)

        subtitle = ctk.CTkLabel(
            panel,
            text="Etiqueta e DANFE no par certo, em segundos.",
            text_color=MUTED,
            font=("Segoe UI", 13),
        )
        subtitle.grid(row=2, column=0, pady=(4, 24))

        selectors = ctk.CTkFrame(panel, fg_color="transparent")
        selectors.grid(row=3, column=0, padx=54, sticky="ew")
        selectors.grid_columnconfigure(0, weight=1)

        self.labels_selector = FileSelector(
            selectors,
            number="1",
            title="PDF de etiquetas",
            hint="Arquivo exportado do TikTok",
            command=self.select_labels,
        )
        self.labels_selector.grid(row=0, column=0, sticky="ew")

        self.danfes_selector = FileSelector(
            selectors,
            number="2",
            title="PDF de DANFEs",
            hint="A ordem das páginas não importa",
            command=self.select_danfes,
        )
        self.danfes_selector.grid(row=1, column=0, pady=(22, 0), sticky="ew")

        self.generate_button = ctk.CTkButton(
            panel,
            text="ORGANIZAR PDF",
            height=58,
            corner_radius=15,
            fg_color=PURPLE,
            hover_color=PURPLE_HOVER,
            border_width=1,
            border_color="#E0C8FF",
            text_color="#170522",
            font=("Segoe UI", 16, "bold"),
            command=self.generate,
            state="disabled",
        )
        self.generate_button.grid(row=4, column=0, padx=54, pady=(28, 12), sticky="ew")

        self.progress = ctk.CTkProgressBar(
            panel,
            height=6,
            mode="indeterminate",
            fg_color="#332048",
            progress_color="#D5ACFF",
        )
        self.progress.grid(row=5, column=0, padx=54, sticky="ew")
        self.progress.set(0)

        self.status = ctk.CTkLabel(
            panel,
            text="Selecione os dois documentos para começar.",
            text_color=MUTED,
            font=("Segoe UI", 11),
        )
        self.status.grid(row=6, column=0, pady=(10, 4))

        privacy = ctk.CTkLabel(
            panel,
            text="PROCESSAMENTO 100% LOCAL  •  SEUS PDFs NÃO SAEM DO COMPUTADOR",
            text_color="#806B98",
            font=("Segoe UI", 9, "bold"),
        )
        privacy.grid(row=7, column=0, pady=(0, 18))

    def select_labels(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o PDF de etiquetas",
            filetypes=[("Arquivo PDF", "*.pdf")],
        )
        if path:
            self.labels_pdf = path
            self.labels_selector.set_file(path)
            self._refresh_ready_state()

    def select_danfes(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o PDF de DANFEs",
            filetypes=[("Arquivo PDF", "*.pdf")],
        )
        if path:
            self.danfes_pdf = path
            self.danfes_selector.set_file(path)
            self._refresh_ready_state()

    def _refresh_ready_state(self) -> None:
        ready = bool(self.labels_pdf and self.danfes_pdf)
        self.generate_button.configure(state="normal" if ready else "disabled")
        self.status.configure(
            text=(
                "Tudo pronto. Clique em organizar PDF."
                if ready
                else "Selecione os dois documentos para começar."
            ),
            text_color=SUCCESS if ready else MUTED,
        )

    def _set_busy(self, busy: bool) -> None:
        self.labels_selector.set_enabled(not busy)
        self.danfes_selector.set_enabled(not busy)
        self.generate_button.configure(state="disabled" if busy else "normal")

        if busy:
            self.progress.start()
            self.status.configure(
                text="Comparando trackings e montando o documento...",
                text_color="#D9C0F5",
            )
        else:
            self.progress.stop()
            self.progress.set(0)
            self._refresh_ready_state()

    def generate(self) -> None:
        if not self.labels_pdf or not self.danfes_pdf:
            messagebox.showerror("Arquivos ausentes", "Selecione os dois PDFs.")
            return

        output_pdf = filedialog.asksaveasfilename(
            title="Salvar PDF organizado",
            defaultextension=".pdf",
            initialfile="etiquetas_e_danfes_organizados.pdf",
            filetypes=[("Arquivo PDF", "*.pdf")],
        )
        if not output_pdf:
            return

        self._set_busy(True)
        Thread(
            target=self._process_in_background,
            args=(output_pdf,),
            daemon=True,
        ).start()

    def _process_in_background(self, output_pdf: str) -> None:
        try:
            result = organize_pdfs(self.labels_pdf, self.danfes_pdf, output_pdf)
        except Exception as error:
            self.after(0, lambda error=error: self._finish_with_error(error))
        else:
            self.after(0, lambda: self._finish_with_success(result, output_pdf))

    def _finish_with_success(
        self,
        result: OrganizationResult,
        output_pdf: str,
    ) -> None:
        self._set_busy(False)
        self.status.configure(
            text=f"Concluído: {result.pairs} par(es) organizado(s).",
            text_color=SUCCESS,
        )

        details = [
            f"{result.pairs} par(es) encontrados e organizados.",
            "",
            self._format_unmatched("Etiquetas sem DANFE", result.unmatched_labels),
            self._format_unmatched("DANFEs sem etiqueta", result.unmatched_danfes),
            (
                "Páginas de etiquetas sem tracking: "
                f"{len(result.label_pages_without_tracking)}"
            ),
            (
                "Páginas de DANFE sem tracking: "
                f"{len(result.danfe_pages_without_tracking)}"
            ),
            "",
            f"Salvo em: {output_pdf}",
        ]
        messagebox.showinfo("PDF organizado", "\n".join(details))

    @staticmethod
    def _format_unmatched(title: str, trackings: tuple[str, ...]) -> str:
        if not trackings:
            return f"{title}: 0"
        preview = ", ".join(trackings[:5])
        remaining = len(trackings) - 5
        suffix = f" e mais {remaining}" if remaining > 0 else ""
        return f"{title}: {len(trackings)} ({preview}{suffix})"

    def _finish_with_error(self, error: Exception) -> None:
        self._set_busy(False)
        self.status.configure(
            text="Não foi possível organizar os PDFs.",
            text_color=ERROR,
        )
        messagebox.showerror("Erro no processamento", str(error))


def run() -> None:
    """Inicializa a aplicação."""

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    App().mainloop()

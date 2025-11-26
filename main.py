
# organizePY.py - Organizador de Arquivos Ultra Moderno v3.0 - NAVEGAÇÃO POR ETAPAS COMPLETA
import os
import shutil
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import webbrowser
import math

# ==================== CONFIGURAÇÃO ====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ==================== CORES HOLOGRÁFICAS ====================
COLORS = {
    "primary": "#00ff88",
    "secondary": "#0099ff",
    "accent": "#ff0088",
    "bg_dark": "#000000",
    "bg_card": "#111111",
    "text_light": "#ffffff",
    "text_gray": "#888888",
    "glass_bg": "#1a1a1a",
    "success": "#43A047",
    "warning": "#FB8C00",
}

# ==================== TIPOS DE ARQUIVOS - AGORA COM EXTENSÕES INDIVIDUAIS ====================
TIPOS = {
    # Documentos
    "PDF": [".pdf"],
    "Word": [".doc", ".docx", ".docm"],
    "Texto": [".txt", ".rtf", ".md"],
    "Email": [".eml"],
    
    # Planilhas
    "Excel": [".xls", ".xlsx", ".xlsm"],
    "CSV": [".csv"],
    "OpenOffice Calc": [".ods"],
    
    # Apresentações
    "PowerPoint": [".ppt", ".pptx", ".pptm"],
    
    # Bancos de Dados
    "Access": [".accdb", ".mdb"],
    
    # Imagens
    "JPEG": [".jpg", ".jpeg"],
    "PNG": [".png"],
    "GIF": [".gif"],
    "BMP": [".bmp"],
    "WebP": [".webp"],
    "TIFF": [".tif", ".tiff"],
    "CorelDRAW": [".cdr"],
    "Photoshop": [".psd"],
    
    # Vídeos
    "MP4": [".mp4"],
    "MKV": [".mkv"],
    "MOV": [".mov"],
    "AVI": [".avi"],
    "WMV": [".wmv"],
    "FLV": [".flv"],
    
    # Áudio
    "MP3": [".mp3"],
    "WAV": [".wav"],
    "FLAC": [".flac"],
    "OGG": [".ogg"],
    "Opus": [".opus"],
    "M4A": [".m4a"],
    
    # Modelos 3D
    "STL": [".stl"],
    "OBJ": [".obj"],
    "3MF": [".3mf"],
    "G-Code": [".gcode"],
    
    # Web/Código
    "HTML": [".html", ".htm"],
    "CSS": [".css"],
    "JavaScript": [".js"],
    "JSON": [".json"],
    "XML": [".xml"],
    "Python": [".py"],
    "Java": [".java"],
    "PHP": [".php"],
    "Arduino": [".ino"],
    "PowerShell": [".ps1"],
    
    # Compactados
    "ZIP": [".zip"],
    "RAR": [".rar"],
    "7Z": [".7z"],
    "TAR": [".tar"],
    "GZ": [".gz"],
    
    # Fontes
    "TrueType": [".ttf"],
    "OpenType": [".otf"],
    
    # Instaladores
    "Executáveis": [".exe"],
    "MSI": [".msi"],
    "Batch": [".bat", ".cmd"],
    
    # Office Extra
    "Publisher": [".pub"],
    "Visio": [".vsd", ".vsdx"],
    "OneNote": [".one"]
}

# Cache de ícones
_icon_cache = {}

# ==================== FUNÇÕES UTILITÁRIAS ====================
def get_desktop():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def make_unique_path(dest_path):
    """Versão otimizada com menos chamadas ao sistema"""
    if not os.path.exists(dest_path):
        return dest_path
    base, ext = os.path.splitext(dest_path)
    i = 1
    while os.path.exists(f"{base} ({i}){ext}"):
        i += 1
    return f"{base} ({i}){ext}"

def move_with_rename(src_file, dest_dir):
    """Versão otimizada com verificações reduzidas"""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    dest_path = make_unique_path(os.path.join(dest_dir, os.path.basename(src_file)))
    
    if os.path.abspath(src_file) == os.path.abspath(dest_path):
        return None
    
    shutil.move(src_file, dest_path)
    return dest_path

def collect_files_for_patterns(src_path, patterns, recurse=False):
    """Versão otimizada com set para busca mais rápida"""
    found = []
    pattern_set = set(patterns)
    
    try:
        if recurse:
            for root, _, files in os.walk(src_path):
                found.extend(
                    os.path.join(root, f) for f in files 
                    if os.path.splitext(f)[1].lower() in pattern_set
                )
        else:
            for f in os.listdir(src_path):
                full_path = os.path.join(src_path, f)
                if os.path.isfile(full_path) and os.path.splitext(f)[1].lower() in pattern_set:
                    found.append(full_path)
    except (FileNotFoundError, PermissionError):
        pass
    
    return found

def create_icon(icon_type, size=24):
    """Cria ícones com cache para melhor performance"""
    cache_key = f"{icon_type}_{size}"
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    icons = {
        "folder": {"color": "#FFB74D", "shape": "folder"},
        "play": {"color": "#4CAF50", "shape": "play"},
        "preview": {"color": "#FF9800", "shape": "preview"},
        "arrow": {"color": "#00ff88", "shape": "arrow"},
        "back": {"color": "#888888", "shape": "back"},
    }
    
    config = icons.get(icon_type, icons["folder"])
    color = config["color"]
    
    if config["shape"] == "folder":
        draw.rounded_rectangle([2, 6, size-2, size-2], radius=3, fill=color)
        draw.rectangle([2, 4, size//2, 8], fill=color)
    elif config["shape"] == "play":
        points = [(6, 4), (size-6, size//2), (6, size-4)]
        draw.polygon(points, fill=color)
    elif config["shape"] == "arrow":
        points = [(8, size//2), (size-8, size//2-6), (size-8, size//2+6)]
        draw.polygon(points, fill=color)
    elif config["shape"] == "back":
        points = [(size-8, size//2), (8, size//2-6), (8, size//2+6)]
        draw.polygon(points, fill=color)
    else:
        draw.ellipse([4, 4, size-4, size-4], fill=color)
    
    icon = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    _icon_cache[cache_key] = icon
    return icon

# ==================== FUNÇÃO DE ORGANIZAÇÃO OTIMIZADA ====================
def organize(sources, categories, mode, dest_base, dest_name, recurse, progress_callback=None):
    """Versão otimizada com processamento paralelo e pastas por tipo de arquivo"""
    root_dest = os.path.join(dest_base, dest_name)
    os.makedirs(root_dest, exist_ok=True)
    log_lines = []
    moved_count = 0
    
    # Criar todas as pastas de destino antecipadamente
    all_patterns = [p.lower() for cat in categories for p in TIPOS.get(cat, [])]
    
    if progress_callback:
        progress_callback(0, 1, "🔍 Iniciando contagem de arquivos...")
    
    # Contagem total otimizada
    total = 0
    for label, path in sources:
        if os.path.exists(path):
            count = len(collect_files_for_patterns(path, all_patterns, recurse))
            total += count
            if progress_callback:
                progress_callback(0, max(1, total), f"📊 Encontrados {total} arquivos em {label}...")
    
    if progress_callback:
        progress_callback(0, max(1, total), f"✅ Total: {total} arquivos para organizar")
    
    time.sleep(0.5)  # Pequena pausa para visualização
    
    processed = 0
    lock = threading.Lock()
    
    def process_file(file_info):
        nonlocal processed, moved_count
        f, cat_dest, cat = file_info
        
        if not os.path.abspath(f).startswith(os.path.abspath(root_dest)):
            try:
                newp = move_with_rename(f, cat_dest)
                if newp:
                    msg = f"✅ {os.path.basename(f)} → {cat}"
                    with lock:
                        moved_count += 1
                    return msg
                else:
                    return f"⭕ {f}"
            except Exception as e:
                return f"❌ {f} : {e}"
        return f"⭕ {f}"
    
    # Processar arquivos em paralelo
    file_tasks = []
    
    for label, path in sources:
        if not os.path.exists(path):
            log_lines.append(f"⚠️ Origem não encontrada: {path}")
            continue
        
        origin_root = os.path.join(root_dest, label) if mode.upper() == "A" else root_dest
        
        for cat in categories:
            patterns = [p.lower() for p in TIPOS.get(cat, [])]
            cat_dest = os.path.join(origin_root, cat.replace("/", "_").replace(" ", "_"))
            os.makedirs(cat_dest, exist_ok=True)
            
            files = collect_files_for_patterns(path, patterns, recurse)
            file_tasks.extend([(f, cat_dest, cat) for f in files])
    
    # Processar arquivos usando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_file, task): task for task in file_tasks}
        
        for future in as_completed(futures):
            result = future.result()
            log_lines.append(result)
            processed += 1
            
            if progress_callback:
                # Mostrar nome do arquivo sendo processado
                file_name = os.path.basename(futures[future][0])
                status_msg = f"📦 [{processed}/{total}] {file_name[:50]}..."
                progress_callback(processed, total, status_msg)
    
    # Mover pastas (sequencial para evitar conflitos)
    if progress_callback:
        progress_callback(processed, total, "📁 Organizando pastas...")
    
    for label, path in sources:
        if not os.path.exists(path):
            continue
            
        origin_root = os.path.join(root_dest, label) if mode.upper() == "A" else root_dest
        dest_folders = os.path.join(origin_root, "Pastas")
        os.makedirs(dest_folders, exist_ok=True)
        
        try:
            for child in os.listdir(path):
                child_full = os.path.join(path, child)
                if os.path.isdir(child_full) and not os.path.abspath(child_full).startswith(os.path.abspath(root_dest)):
                    target = make_unique_path(os.path.join(dest_folders, child))
                    try:
                        shutil.move(child_full, target)
                        log_lines.append(f"📂 {child} → Pastas")
                        if progress_callback:
                            progress_callback(processed, total, f"📂 Movendo pasta: {child}")
                    except Exception as e:
                        log_lines.append(f"❌ Pasta {child} : {e}")
        except Exception as e:
            log_lines.append(f"⚠️ Erro ao listar {path} : {e}")
    
    # Finalização
    if progress_callback:
        progress_callback(total, total, f"✨ Concluído! {moved_count} arquivos organizados")
    
    # Salvar log
    log_file = os.path.join(root_dest, "log.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n\n===== Execução: {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n")
        f.writelines(f"{L}\n" for L in log_lines)
        f.write(f"✨ Arquivos movidos: {moved_count}\n")
    
    return log_lines, moved_count, log_file

# ==================== CLASSE MARCA D'ÁGUA ANIMADA ====================
class NandevWatermark(ctk.CTkFrame):
    """Marca d'água animada com cubo 3D e link para LinkedIn"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configurações
        self.linkedin_url = "https://www.linkedin.com/in/renan-de-oliveira-farias-66a9b412b/"
        self.rotation_angle = 0
        self.animation_speed = 2
        self.is_hovering = False
        self.pulse_phase = 0
        
        # Cores
        self.primary = "#00ff88"
        self.secondary = "#0099ff"
        self.accent = "#ff0088"
        
        self.configure(
            fg_color="transparent",
            corner_radius=12,
            border_width=2,
            border_color=self.primary
        )
        
        self.create_widgets()
        self.start_animation()
        
    def create_widgets(self):
        """Cria os elementos da marca d'água"""
        # Container principal
        main_container = ctk.CTkFrame(self, fg_color=COLORS["glass_bg"], corner_radius=10)
        main_container.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Frame para conteúdo
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=12, pady=8)
        
        # Container horizontal
        h_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        h_container.pack()
        
        # Canvas para o cubo 3D animado
        self.cube_canvas = ctk.CTkCanvas(
            h_container,
            width=32,
            height=32,
            bg=COLORS["glass_bg"],
            highlightthickness=0
        )
        self.cube_canvas.pack(side="left", padx=(0, 10))
        
        # Texto da marca
        text_frame = ctk.CTkFrame(h_container, fg_color="transparent")
        text_frame.pack(side="left")
        
        # Linha 1: "Desenvolvido por"
        dev_label = ctk.CTkLabel(
            text_frame,
            text="Desenvolvido por",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_gray"]
        )
        dev_label.pack()
    
        
        # Linha 2: "Nandev" com gradiente
        name_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        name_frame.pack()
        
        nan_label = ctk.CTkLabel(
            name_frame,
            text="Nan",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary
        )
        nan_label.pack(side="left")
        
        dev_label2 = ctk.CTkLabel(
            name_frame,
            text="dev",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.secondary
        )
        dev_label2.pack(side="left")
        
        # Linha 3: "</> Python Developer"
        code_label = ctk.CTkLabel(
            text_frame,
            text="</> Python Developer",
            font=ctk.CTkFont(size=9),
            text_color=self.accent
        )
        code_label.pack()
              # ==================== ÁREA CLICÁVEL - LINKEDIN GLOBAL ====================
        widgets_clicaveis = [
            self, main_container, content_frame, h_container,
            self.cube_canvas, text_frame, name_frame,
            dev_label, nan_label, dev_label2, code_label
        ]

        for widget in widgets_clicaveis:
            widget.bind("<Button-1>", self.open_linkedin)
            widget.configure(cursor="hand2")

        
        # Botão LinkedIn
        self.linkedin_btn = ctk.CTkButton(
            content_frame,
            text="🔗 LinkedIn",
            command=self.open_linkedin,
            width=120,
            height=28,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=self.secondary,
            hover_color=self.primary,
            corner_radius=8
        )
        self.linkedin_btn.pack(pady=(8, 0))
        
        # Eventos de hover para todo o frame
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.linkedin_btn.bind("<Enter>", self.on_enter)
        self.linkedin_btn.bind("<Leave>", self.on_leave)
        
    def draw_3d_cube(self):
        """Desenha cubo 3D wireframe animado"""
        self.cube_canvas.delete("all")
        
        # Dimensões do cubo
        size = 12
        center_x = 16
        center_y = 16
        
        # Ângulo de rotação com pulso quando hover
        angle = math.radians(self.rotation_angle)
        pulse = 1.0 + (math.sin(self.pulse_phase) * 0.1 if self.is_hovering else 0)
        
        # Vértices do cubo (8 pontos)
        vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Frente
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]   # Trás
        ]
        
        # Projeção 3D -> 2D
        projected = []
        for vertex in vertices:
            # Rotação em Y e X
            x = vertex[0] * math.cos(angle) - vertex[2] * math.sin(angle)
            z = vertex[0] * math.sin(angle) + vertex[2] * math.cos(angle)
            y = vertex[1] * math.cos(angle * 0.7) - z * math.sin(angle * 0.7)
            z = vertex[1] * math.sin(angle * 0.7) + z * math.cos(angle * 0.7)
            
            # Projeção perspectiva simples
            scale = size * pulse / (z + 3)
            x2d = center_x + x * scale
            y2d = center_y + y * scale
            projected.append((x2d, y2d, z))
        
        # Desenhar arestas do cubo
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Frente
            (4, 5), (5, 6), (6, 7), (7, 4),  # Trás
            (0, 4), (1, 5), (2, 6), (3, 7)   # Conexões
        ]
        
        # Cores por profundidade
        for i, (start, end) in enumerate(edges):
            p1 = projected[start]
            p2 = projected[end]
            
            # Cor baseada na profundidade média
            depth = (p1[2] + p2[2]) / 2
            if depth < 0:
                color = self.primary
                width = 2
            elif depth < 1:
                color = self.secondary
                width = 2
            else:
                color = self.accent
                width = 1
            
            self.cube_canvas.create_line(
                p1[0], p1[1], p2[0], p2[1],
                fill=color,
                width=width,
                smooth=True
            )
        
        # Desenhar vértices como pontos brilhantes
        for point in projected:
            radius = 2 if point[2] < 0 else 1.5
            self.cube_canvas.create_oval(
                point[0] - radius, point[1] - radius,
                point[0] + radius, point[1] + radius,
                fill=self.primary if point[2] < 0 else self.secondary,
                outline=""
            )
    
    def start_animation(self):
        """Inicia a animação contínua"""
        self.animate()
    
    def animate(self):
        """Loop de animação"""
        # Incrementar ângulo de rotação
        speed = self.animation_speed * (2 if self.is_hovering else 1)
        self.rotation_angle = (self.rotation_angle + speed) % 360
        
        # Incrementar fase do pulso
        if self.is_hovering:
            self.pulse_phase += 0.15
        
        # Redesenhar cubo
        self.draw_3d_cube()
        
        # Próximo frame
        self.after(30, self.animate)  # ~33 FPS
    def on_enter(self, event):
        """Mouse entrou na área"""
        self.is_hovering = True
        self.configure(border_color=self.accent)
        self.linkedin_btn.configure(fg_color=self.primary)
    
    def on_leave(self, event):
        """Mouse saiu da área"""
        self.is_hovering = False
        self.pulse_phase = 0
        self.configure(border_color=self.primary)
        self.linkedin_btn.configure(fg_color=self.secondary)
    
    def open_linkedin(self, event=None):
        """Abre o LinkedIn no navegador"""
        try:
            webbrowser.open(self.linkedin_url)
            self.show_success_box("LinkedIn aberto com sucesso!")

            original_color = self.linkedin_btn.cget("fg_color")
            self.linkedin_btn.configure(fg_color=self.accent)
            self.after(200, lambda: self.linkedin_btn.configure(fg_color=original_color))

        except Exception as e:
            print(f"Erro ao abrir LinkedIn: {e}")

# ==================== INTERFACE GRÁFICA COM NAVEGAÇÃO POR ETAPAS ====================
class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🗂️ OrganizePY - Organizador de Arquivos v3.0 - NAVEGAÇÃO POR ETAPAS")
        
        # FORÇAR TELA CHEIA
        self.state('zoomed')
        self.attributes('-fullscreen', False)
        self.bind('<Map>', lambda e: self.state('zoomed'))
        
        # Controle de etapas
        self.current_step = 0
        self.total_steps = 5
        
        # Ícones em cache
        self.icons = {
            "folder": create_icon("folder", 20),
            "play": create_icon("play", 20),
            "preview": create_icon("preview", 20),
            "arrow": create_icon("arrow", 24),
            "back": create_icon("back", 24),
        }
        
        self.create_widgets()
        self.show_step(0)
        
        # Maximizar após criação
        self.after(100, lambda: self.state('zoomed'))
        
    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ===== SIDEBAR =====
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COLORS["bg_card"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")
        
        ctk.CTkLabel(logo_frame, text="🗂️", font=ctk.CTkFont(size=48)).pack()
        ctk.CTkLabel(logo_frame, text="OrganizePY", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(logo_frame, text="v3.0 STEPS ⚡", 
                    font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["primary"]).pack(pady=2)
        ctk.CTkLabel(logo_frame, text="Navegação por\nEtapas Inteligente", 
                    font=ctk.CTkFont(size=11), text_color=COLORS["text_gray"]).pack()
        
        # Separador
        ctk.CTkFrame(self.sidebar, height=2, fg_color=COLORS["primary"]).grid(
            row=1, column=0, padx=20, pady=20, sticky="ew")
        
        # Indicador de Progresso das Etapas
        self.steps_indicator = ctk.CTkFrame(self.sidebar, fg_color=COLORS["glass_bg"])
        self.steps_indicator.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(self.steps_indicator, text="📋 Progresso das Etapas", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.steps_labels = []
        steps_info = [
            ("1️⃣", "Selecionar Origens"),
            ("2️⃣", "Configurar Destino"),
            ("3️⃣", "Escolher Categorias"),
            ("4️⃣", "Revisar e Executar"),
            ("5️⃣", "Resultados")
        ]
        
        for i, (emoji, text) in enumerate(steps_info):
            step_frame = ctk.CTkFrame(self.steps_indicator, fg_color="transparent")
            step_frame.pack(fill="x", padx=15, pady=5)
            
            label = ctk.CTkLabel(step_frame, text=f"{emoji} {text}", 
                               font=ctk.CTkFont(size=12), 
                               text_color=COLORS["text_gray"],
                               anchor="w")
            label.pack(side="left", fill="x", expand=True)
            self.steps_labels.append(label)
        
        # Espaçador que empurra a marca d'água para baixo
        self.sidebar.grid_rowconfigure(3, weight=1)
        
        # ===== MARCA D'ÁGUA NANDEV ANIMADA =====
        watermark_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        watermark_frame.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="sew")
        
        self.nandev_watermark = NandevWatermark(
            watermark_frame,
            width=240,
            height=110
        )
        self.nandev_watermark.pack(fill="x")
        
        # Footer "v3.0 STEPS | 2025"
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.grid(row=5, column=0, padx=20, pady=(5, 15), sticky="s")
        
        ctk.CTkLabel(
            footer_frame, 
            text="v3.0 STEPS | 2025", 
            font=ctk.CTkFont(size=9), 
            text_color=COLORS["text_gray"]
        ).pack()
        # ===== ÁREA DE CONTEÚDO =====
        content_container = ctk.CTkFrame(self, fg_color="transparent")
        content_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        content_container.grid_rowconfigure(0, weight=1)
        content_container.grid_columnconfigure(0, weight=1)
        
        # Container para as etapas (CORRIGIDO - Sem grid inicial)
        self.content = ctk.CTkFrame(content_container, fg_color="transparent")
        self.content.grid(row=0, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        
        # Container para cada etapa (CORRIGIDO)
        self.step_frames = []
        for i in range(self.total_steps):
            frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
            frame.grid_columnconfigure(0, weight=1)
            self.step_frames.append(frame)
        
        # Criar conteúdo de cada etapa
        self.create_step_1()  # Selecionar Origens
        self.create_step_2()  # Configurar Destino
        self.create_step_3()  # Escolher Categorias
        self.create_step_4()  # Revisar e Executar
        self.create_step_5()  # Resultados
        
        # Botões de navegação
        nav_frame = ctk.CTkFrame(content_container, fg_color=COLORS["glass_bg"], height=80, corner_radius=15)
        nav_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        nav_frame.grid_columnconfigure(1, weight=1)
        
        self.back_btn = ctk.CTkButton(
            nav_frame,
            text="⬅️ Voltar",
            command=self.previous_step,
            width=160,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["text_gray"],
            hover_color=COLORS["bg_card"],
            corner_radius=12,
            image=self.icons["back"],
            compound="left"
        )
        self.back_btn.grid(row=0, column=0, padx=20, pady=15)
        
        self.step_counter_label = ctk.CTkLabel(
            nav_frame,
            text="Etapa 1 de 5",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["primary"]
        )
        self.step_counter_label.grid(row=0, column=1)
        
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Próximo ➡️",
            command=self.next_step,
            width=160,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            corner_radius=12,
            image=self.icons["arrow"],
            compound="right"
        )
        self.next_btn.grid(row=0, column=2, padx=20, pady=15)
    
    def show_step(self, step):
        """Mostra apenas a etapa especificada (CORRIGIDO)"""
        # Esconder todas as etapas usando grid_forget
        for i, frame in enumerate(self.step_frames):
            if i == step:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()
            
        # Atualizar indicador visual na sidebar
        for i, label in enumerate(self.steps_labels):
            if i == step:
                label.configure(text_color=COLORS["primary"], font=ctk.CTkFont(size=13, weight="bold"))
            elif i < step:
                label.configure(text_color=COLORS["success"], font=ctk.CTkFont(size=12))
            else:
                label.configure(text_color=COLORS["text_gray"], font=ctk.CTkFont(size=12))
        
        # Atualizar contador
        self.step_counter_label.configure(text=f"Etapa {step + 1} de {self.total_steps}")
        
        # Controlar visibilidade dos botões
        if step == 0:
            self.back_btn.configure(state="disabled")
        else:
            self.back_btn.configure(state="normal")
        
        if step == self.total_steps - 1:
           self.next_btn.configure(text="🏁 Finalizar", state="disabled")

        elif step == 3:
          self.next_btn.configure(text="▶️ Executar", state="normal")

        else:
          self.next_btn.configure(text="Próximo ➡️", state="normal")
        
        # Atualizar revisão se estiver na etapa 4
        if step == 3:
            self.update_review()
        
        self.current_step = step
    
    def next_step(self):
        """Avança para a próxima etapa"""
        if self.current_step < self.total_steps - 1:
            # Validar etapa antes de avançar
            if self.validate_current_step():
                if self.current_step == 3:  # Se estiver na etapa de revisão
                    self.execute_organization()
                else:
                    self.show_step(self.current_step + 1)
    
    def previous_step(self):
        """Volta para a etapa anterior"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def validate_current_step(self):
        """Valida se a etapa atual está completa"""
        if self.current_step == 0:  # Etapa 1: Origens
            sources = self.get_selected_sources()
            if not sources:
                messagebox.showwarning("Atenção", "Selecione pelo menos uma origem de arquivos!")
                return False
        elif self.current_step == 1:  # Etapa 2: Destino
            if not self.dest_entry.get().strip():
                messagebox.showwarning("Atenção", "Selecione a pasta de destino!")
                return False
            if not self.dest_name_entry.get().strip():
                messagebox.showwarning("Atenção", "Digite um nome para a pasta organizada!")
                return False
        elif self.current_step == 2:  # Etapa 3: Categorias
            selected = [cat for cat, var in self.cat_vars.items() if var.get()]
            if not selected:
                messagebox.showwarning("Atenção", "Selecione pelo menos um tipo de arquivo!")
                return False
        
        return True
    
    def create_step_1(self):
        """ETAPA 1: Selecionar Origens"""
        frame = self.step_frames[0]
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        ctk.CTkLabel(header, text="📂 Etapa 1: Selecione as Origens dos Arquivos", 
                    font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        
        # Card
        card = ctk.CTkFrame(frame, corner_radius=15, fg_color=COLORS["glass_bg"])
        card.grid(row=1, column=0, sticky="ew")
        
        card_header = ctk.CTkFrame(card, fg_color=COLORS["primary"], corner_radius=15)
        card_header.pack(fill="x", padx=3, pady=3)
        ctk.CTkLabel(card_header, text="🎯 De onde você deseja organizar os arquivos?", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="black").pack(
                        side="left", padx=20, pady=15)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        self.src_vars = {}
        options = [
            ("💻 Desktop", os.path.join(os.path.expanduser("~"), "Desktop")),
            ("📥 Downloads", os.path.join(os.path.expanduser("~"), "Downloads")),
            ("📄 Documentos", os.path.join(os.path.expanduser("~"), "Documents")),
            ("🖼️ Imagens", os.path.join(os.path.expanduser("~"), "Pictures")),
            ("🎬 Vídeos", os.path.join(os.path.expanduser("~"), "Videos")),
            ("🎵 Música", os.path.join(os.path.expanduser("~"), "Music"))
        ]
        
        grid_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 20))
        
        for i, (label_text, path) in enumerate(options):
            var = ctk.BooleanVar(value=(i==0))
            cb_frame = ctk.CTkFrame(grid_frame, corner_radius=10, fg_color=COLORS["bg_card"])
            cb_frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")
            cb = ctk.CTkCheckBox(cb_frame, text=label_text, variable=var, 
                                font=ctk.CTkFont(size=14), checkbox_width=24, checkbox_height=24)
            cb.pack(padx=15, pady=15)
            self.src_vars[label_text] = (var, path)
        
        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        ctk.CTkLabel(content_frame, text="📁 Ou selecione uma pasta personalizada:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 10))
        
        custom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        custom_frame.pack(fill="x")
        
        self.custom_entry = ctk.CTkEntry(custom_frame, height=40, placeholder_text="Caminho da pasta...", 
                                        font=ctk.CTkFont(size=13), corner_radius=10)
        self.custom_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(custom_frame, text="Procurar", width=140, height=40, command=self.choose_custom, 
                     font=ctk.CTkFont(size=13, weight="bold"), corner_radius=10, 
                     image=self.icons["folder"], compound="left").pack(side="left")
    
    def create_step_2(self):
        """ETAPA 2: Configurar Destino"""
        frame = self.step_frames[1]
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        ctk.CTkLabel(header, text="🎯 Etapa 2: Configure o Destino e Opções", 
                    font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        
        # Card
        card = ctk.CTkFrame(frame, corner_radius=15, fg_color=COLORS["glass_bg"])
        card.grid(row=1, column=0, sticky="ew")
        
        card_header = ctk.CTkFrame(card, fg_color=COLORS["success"], corner_radius=15)
        card_header.pack(fill="x", padx=3, pady=3)
        ctk.CTkLabel(card_header, text="📍 Para onde os arquivos serão organizados?", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(
                        side="left", padx=20, pady=15)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        ctk.CTkLabel(left_col, text="📁 Pasta onde será criada a organização:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        dest_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        dest_frame.pack(fill="x", pady=(0, 20))
        
        self.dest_entry = ctk.CTkEntry(dest_frame, height=40, placeholder_text="Selecione a pasta destino...", 
                                      font=ctk.CTkFont(size=13), corner_radius=10)
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dest_entry.insert(0, get_desktop())
        
        ctk.CTkButton(dest_frame, text="Procurar", width=140, height=40, command=self.choose_dest, 
                     font=ctk.CTkFont(size=13, weight="bold"), corner_radius=10, 
                     image=self.icons["folder"], compound="left").pack(side="left")
        
        ctk.CTkLabel(left_col, text="📝 Nome da pasta organizada:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        self.dest_name_entry = ctk.CTkEntry(left_col, height=40, placeholder_text="Ex: Arquivos_Organizados", 
                                           font=ctk.CTkFont(size=13), corner_radius=10)
        self.dest_name_entry.pack(fill="x", pady=(0, 20))
        self.dest_name_entry.insert(0, f"Organizados_{time.strftime('%Y%m%d_%H%M%S')}")
        
        right_col = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        ctk.CTkLabel(right_col, text="⚙️ Opções de Organização", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 15))
        
        self.mode_var = ctk.StringVar(value="B")
        
        mode_b = ctk.CTkRadioButton(right_col, text="📦 Modo Simples\nTodos os arquivos em uma pasta", 
                                    variable=self.mode_var, value="B", 
                                    font=ctk.CTkFont(size=13), radiobutton_width=20, radiobutton_height=20)
        mode_b.pack(anchor="w", padx=20, pady=10)
        
        mode_a = ctk.CTkRadioButton(right_col, text="📂 Modo Organizado\nSeparar por pasta de origem", 
                                    variable=self.mode_var, value="A", 
                                    font=ctk.CTkFont(size=13), radiobutton_width=20, radiobutton_height=20)
        mode_a.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkFrame(right_col, height=2, fg_color=COLORS["text_gray"]).pack(fill="x", padx=20, pady=15)
        
        self.recurse_var = ctk.BooleanVar(value=False)
        recurse_cb = ctk.CTkCheckBox(right_col, text="📁 Incluir subpastas\n(busca recursiva)", 
                                    variable=self.recurse_var, font=ctk.CTkFont(size=13),
                                    checkbox_width=24, checkbox_height=24)
        recurse_cb.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_step_3(self):
        """ETAPA 3: Escolher Categorias"""
        frame = self.step_frames[2]
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        ctk.CTkLabel(header, text="📑 Etapa 3: Escolha os Tipos de Arquivo", 
                    font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        
        # Card
        card = ctk.CTkFrame(frame, corner_radius=15, fg_color=COLORS["glass_bg"])
        card.grid(row=1, column=0, sticky="ew")
        
        card_header = ctk.CTkFrame(card, fg_color=COLORS["secondary"], corner_radius=15)
        card_header.pack(fill="x", padx=3, pady=3)
        
        header_content = ctk.CTkFrame(card_header, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(header_content, text="🎨 Quais tipos de arquivo você quer organizar?", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(side="left")
        
        btn_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(btn_frame, text="✅ Todos", width=100, height=32, 
                     command=self.select_all_categories, 
                     font=ctk.CTkFont(size=12, weight="bold"), corner_radius=8).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="❌ Nenhum", width=100, height=32, 
                     command=self.deselect_all_categories, 
                     font=ctk.CTkFont(size=12, weight="bold"), corner_radius=8).pack(side="left", padx=5)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Organizar por grupos
        groups = {
            "📄 Documentos": ["PDF", "Word", "Texto", "Email"],
            "📊 Planilhas": ["Excel", "CSV", "OpenOffice Calc"],
            "📽️ Apresentações": ["PowerPoint"],
            "🗄️ Bancos de Dados": ["Access"],
            "🎨 Imagens": ["JPEG", "PNG", "GIF", "BMP", "WebP", "TIFF", "CorelDRAW", "Photoshop"],
            "🎬 Vídeos": ["MP4", "MKV", "MOV", "AVI", "WMV", "FLV"],
            "🎵 Áudio": ["MP3", "WAV", "FLAC", "OGG", "Opus", "M4A"],
            "🎲 Modelos 3D": ["STL", "OBJ", "3MF", "G-Code"],
            "🌐 Web/Código": ["HTML", "CSS", "JavaScript", "JSON", "XML", "Python", "Java", "PHP", "Arduino", "PowerShell"],
            "📦 Compactados": ["ZIP", "RAR", "7Z", "TAR", "GZ"],
            "🔤 Fontes": ["TrueType", "OpenType"],
            "⚙️ Instaladores": ["Executáveis", "MSI", "Batch"],
            "📓 Office Extra": ["Publisher", "Visio", "OneNote"]
        }
        
        self.cat_vars = {}
        
        for group_name, categories in groups.items():
            group_frame = ctk.CTkFrame(content_frame, corner_radius=12, fg_color=COLORS["bg_card"])
            group_frame.pack(fill="x", pady=10)
            
            header_frame = ctk.CTkFrame(group_frame, fg_color=COLORS["glass_bg"], corner_radius=10)
            header_frame.pack(fill="x", padx=3, pady=3)
            
            ctk.CTkLabel(header_frame, text=group_name, 
                        font=ctk.CTkFont(size=15, weight="bold")).pack(side="left", padx=15, pady=10)
            
            cats_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
            cats_frame.pack(fill="x", padx=15, pady=15)
            
            for i, cat in enumerate(categories):
                var = ctk.BooleanVar(value=False)
                extensions = ", ".join(TIPOS[cat])
                cb = ctk.CTkCheckBox(cats_frame, 
                                    text=f"{cat} ({extensions})", 
                                    variable=var, 
                                    font=ctk.CTkFont(size=12),
                                    checkbox_width=20, 
                                    checkbox_height=20)
                cb.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=5)
                self.cat_vars[cat] = var
            
            for i in range(3):
                cats_frame.grid_columnconfigure(i, weight=1)
    
    def create_step_4(self):
        """ETAPA 4: Revisar e Executar"""
        frame = self.step_frames[3]
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        ctk.CTkLabel(header, text="✅ Etapa 4: Revisão Final", 
                    font=ctk.CTkFont(size=32, weight="bold")).pack(side="left")
        
        # Card
        card = ctk.CTkFrame(frame, corner_radius=15, fg_color=COLORS["glass_bg"])
        card.grid(row=1, column=0, sticky="ew")
        
        card_header = ctk.CTkFrame(card, fg_color=COLORS["warning"], corner_radius=15)
        card_header.pack(fill="x", padx=3, pady=3)
        ctk.CTkLabel(card_header, text="📋 Revise suas configurações antes de executar", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(
                        side="left", padx=20, pady=15)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Resumo
        self.review_text = ctk.CTkTextbox(content_frame, height=400, font=ctk.CTkFont(size=13),
                                         corner_radius=10, wrap="word")
        self.review_text.pack(fill="both", expand=True)
    
    def create_step_5(self):
        """ETAPA 5: Resultados"""
        frame = self.step_frames[4]
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        self.result_header = ctk.CTkLabel(header, text="⏳ Executando...", 
                                         font=ctk.CTkFont(size=32, weight="bold"))
        self.result_header.pack(side="left")
        
        # Card de Progresso
        progress_card = ctk.CTkFrame(frame, corner_radius=15, fg_color=COLORS["glass_bg"])
        progress_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        progress_content = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_content.pack(fill="x", padx=25, pady=25)
        
        self.progress_label = ctk.CTkLabel(progress_content, text="Preparando...", 
                                          font=ctk.CTkFont(size=14))
        self.progress_label.pack(pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(progress_content, height=20, corner_radius=10)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        
        self.progress_percent = ctk.CTkLabel(progress_content, text="0%", 
                                            font=ctk.CTkFont(size=16, weight="bold"),
                                            text_color=COLORS["primary"])
        self.progress_percent.pack()
        
        # Card de Log
        log_card = ctk.CTkFrame(frame, corner_radius=15, fg_color=COLORS["glass_bg"])
        log_card.grid(row=2, column=0, sticky="ew")
        
        log_header = ctk.CTkFrame(log_card, fg_color=COLORS["primary"], corner_radius=15)
        log_header.pack(fill="x", padx=3, pady=3)
        ctk.CTkLabel(log_header, text="📋 Log de Execução", 
                    font=ctk.CTkFont(size=16, weight="bold"), text_color="black").pack(
                        side="left", padx=20, pady=12)
        
        log_content = ctk.CTkFrame(log_card, fg_color="transparent")
        log_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        self.log_text = ctk.CTkTextbox(log_content, height=300, font=ctk.CTkFont(size=11),
                                      corner_radius=10, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        
        # Botão de ação final
        self.action_btn = ctk.CTkButton(
            log_content,
            text="📂 Abrir Pasta Organizada",
            command=self.open_result_folder,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color=COLORS["primary"],
            corner_radius=12,
            state="disabled"
        )
        self.action_btn.pack(pady=(20, 0), fill="x")
    
    def update_review(self):
        """Atualiza o texto de revisão"""
        self.review_text.delete("1.0", "end")
        
        review = "╔═══════════════════════════════════════════════════╗\n"
        review += "              📋 RESUMO DA ORGANIZAÇÃO\n"
        review += "╚═══════════════════════════════════════════════════╝\n\n"
        
        # Origens
        review += "📂 ORIGENS SELECIONADAS:\n"
        review += "─" * 50 + "\n"
        sources = self.get_selected_sources()
        if sources:
            for label, path in sources:
                review += f"  • {label}\n    📍 {path}\n"
        else:
            review += "  ⚠️ Nenhuma origem selecionada\n"
        review += "\n"
        
        # Destino
        review += "🎯 CONFIGURAÇÃO DE DESTINO:\n"
        review += "─" * 50 + "\n"
        review += f"  📁 Pasta Base: {self.dest_entry.get()}\n"
        review += f"  📝 Nome da Pasta: {self.dest_name_entry.get()}\n"
        review += f"  📦 Modo: {'Organizado (por origem)' if self.mode_var.get() == 'A' else 'Simples (tudo junto)'}\n"
        review += f"  📁 Subpastas: {'Sim' if self.recurse_var.get() else 'Não'}\n\n"
        
        # Categorias
        review += "📑 TIPOS DE ARQUIVO SELECIONADOS:\n"
        review += "─" * 50 + "\n"
        selected_cats = [cat for cat, var in self.cat_vars.items() if var.get()]
        if selected_cats:
            for cat in selected_cats:
                extensions = ", ".join(TIPOS[cat])
                review += f"  ✅ {cat}: {extensions}\n"
        else:
            review += "  ⚠️ Nenhum tipo de arquivo selecionado\n"
        review += "\n"
        
        review += "╔═══════════════════════════════════════════════════╗\n"
        review += "⚠️  IMPORTANTE: Verifique todas as informações antes de executar!\n"
        review += "╚═══════════════════════════════════════════════════╝\n"
        
        self.review_text.insert("1.0", review)
        self.review_text.configure(state="disabled")
    
    def get_selected_sources(self):
        """Retorna lista de origens selecionadas"""
        sources = []
        for label, (var, path) in self.src_vars.items():
            if var.get():
                sources.append((label, path))
        
        custom = self.custom_entry.get().strip()
        if custom and os.path.exists(custom):
            sources.append(("Personalizado", custom))
        
        return sources
    
    def execute_organization(self):
        """Executa a organização"""
        sources = self.get_selected_sources()
        categories = [cat for cat, var in self.cat_vars.items() if var.get()]
        mode = self.mode_var.get()
        dest_base = self.dest_entry.get()
        dest_name = self.dest_name_entry.get()
        recurse = self.recurse_var.get()

        # Ir para a tela de resultados
        self.show_step(4)

        # Resetar interface
        self.result_header.configure(text="⏳ Executando Organização...")
        self.progress_bar.set(0)
        self.progress_percent.configure(text="0%")
        self.log_text.delete("1.0", "end")
        self.action_btn.configure(state="disabled")

        # Executar em thread separada
        def run():
            def progress_callback(current, total, message):
                percent = (current / total) if total > 0 else 0
                self.after(0, lambda: self.progress_bar.set(percent))
                self.after(0, lambda: self.progress_percent.configure(text=f"{int(percent * 100)}%"))
                self.after(0, lambda: self.progress_label.configure(text=message))
                self.after(0, lambda: self.log_text.insert("end", f"{message}\n"))
                self.after(0, lambda: self.log_text.see("end"))

            try:
                log_lines, moved_count, log_file = organize(
                    sources, categories, mode, dest_base, dest_name, recurse, progress_callback
                )

                self.result_folder = os.path.join(dest_base, dest_name)

                # Atualizar interface final
                self.after(
                    0,
                    lambda: self.result_header.configure(
                        text=f"✅ Organização Concluída! {moved_count} arquivos movidos"
                    )
                )
                self.after(0, lambda: self.action_btn.configure(state="normal"))

                # Caixinha de sucesso
                self.after(0, lambda: self.show_success_dialog(moved_count, log_file))

            except Exception as e:
                self.after(0, lambda: self.result_header.configure(text="❌ Erro na Organização"))
                self.after(0, lambda: self.log_text.insert("end", f"\n❌ ERRO: {str(e)}\n"))
                self.after(0, lambda: messagebox.showerror("Erro", f"Erro durante a organização:\n{str(e)}"))

        threading.Thread(target=run, daemon=True).start()
    def open_result_folder(self):
        """Abre a pasta de resultados"""
        if hasattr(self, 'result_folder') and os.path.exists(self.result_folder):
            os.startfile(self.result_folder)
    
    def choose_custom(self):
        path = filedialog.askdirectory(title="Selecione a pasta de origem")
        if path:
            self.custom_entry.delete(0, "end")
            self.custom_entry.insert(0, path)
    
    def choose_dest(self):
        path = filedialog.askdirectory(title="Selecione a pasta de destino")
        if path:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, path)
    
    def select_all_categories(self):
        for var in self.cat_vars.values():
            var.set(True)
    
    def deselect_all_categories(self):
        for var in self.cat_vars.values():
            var.set(False)
    
    # ======= CAIXA DE SUCESSO ESTILIZADA =======
    def show_success_dialog(self, moved_count, log_file):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sucesso")
        dialog.geometry("520x420")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#0f172a")
        dialog.grab_set()

        container = ctk.CTkFrame(dialog, fg_color="#0b1220", corner_radius=30)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            container,
            text="✅",
            font=ctk.CTkFont(size=70),
            text_color=COLORS["primary"]
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            container,
            text="Processo finalizado\ncom sucesso!",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(pady=(5, 20))

        info = ctk.CTkFrame(container, fg_color="transparent")
        info.pack(pady=10)

        ctk.CTkLabel(
            info,
            text=f"📊 Arquivos organizados: {moved_count}",
            font=ctk.CTkFont(size=16),
            text_color="#e2e8f0"
        ).pack(anchor="w", pady=6)

        ctk.CTkLabel(
            info,
            text=f"📄 Log salvo em:\n{log_file}",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8",
            justify="left"
        ).pack(anchor="w", pady=6)

        btn = ctk.CTkButton(
            container,
            text="OK",
            height=55,
            corner_radius=30,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["secondary"],
            command=dialog.destroy
        )
        btn.pack(pady=25, fill="x", padx=50)
# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
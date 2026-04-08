import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import time

# ==========================
# Tooltip moderno
# ==========================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") or (0,0,0,0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#111111", fg="#00ffff",
                         relief=tk.SOLID, borderwidth=1,
                         font=("Consolas", 9))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# ==========================
# Recursos e variáveis
# ==========================
dinheiro = 1_000_000
recursos = 500
veiculos = []
base = []
bays = []
reputacao = 50
missao_disponivel = True
producao_auto_ativa = True
velocidade_voo = 0.3

upgrades = {"Starship": 1, "Booster": 1, "Base": 1}
mechazilla_disponivel = True
voo_em_andamento = False

# ==========================
# Funções de status
# ==========================
def atualizar_status():
    status_text.set(
        f"💰 Dinheiro: ${dinheiro}   🔧 Recursos: {recursos}   ⭐ Reputação: {reputacao}"
    )

def toggle_producao_auto():
    global producao_auto_ativa
    producao_auto_ativa = not producao_auto_ativa
    estado = "Ativada" if producao_auto_ativa else "Desativada"
    barra_label.config(text=f"⚙️ Produção automática {estado}")

def ajustar_velocidade(delta):
    global velocidade_voo
    velocidade_voo = max(0.1, min(1.0, velocidade_voo + delta))
    barra_label.config(text=f"⏱️ Velocidade do voo: {velocidade_voo:.1f}s por passo")

# ==========================
# Botão modo escuro com hover neon
# ==========================
def criar_botao(parent, text, command=None, bg="#111111", fg="#00ffff", bd=2, hover="#00ff00"):
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     relief="raised", bd=bd, activebackground="#222222",
                     activeforeground="#00ffff", highlightbackground="#555555",
                     font=("Consolas", 10, "bold"))
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

# ==========================
# Construção de veículos e base
# ==========================
def construir_veiculo(tipo):
    global dinheiro, recursos, veiculos
    custos = {"Starship": (200_000, 50), "Super Heavy": (300_000, 70)}
    if dinheiro >= custos[tipo][0] and recursos >= custos[tipo][1]:
        dinheiro -= custos[tipo][0]
        recursos -= custos[tipo][1]
        veiculos.append(tipo)
        barra_label.config(text=f"✅ {tipo} construída!")
        atualizar_status()
    else:
        barra_label.config(text="❌ Recursos insuficientes!")

def construir_base_item(item):
    global dinheiro, recursos, base
    custos = {"Mechazilla": (150_000, 30), "Torre Pad": (100_000, 20), "Pad Orbital": (250_000, 50)}
    c_din, c_rec = custos[item]
    if dinheiro >= c_din and recursos >= c_rec:
        dinheiro -= c_din
        recursos -= c_rec
        base.append(item)
        barra_label.config(text=f"✅ {item} construída!")
        atualizar_status()
    else:
        barra_label.config(text="❌ Recursos insuficientes!")

def armazenar_bay():
    if veiculos:
        veiculo = veiculos.pop(0)
        bays.append(veiculo)
        barra_label.config(text=f"📦 {veiculo} armazenado no Bay")
        atualizar_status()
    else:
        barra_label.config(text="❌ Nenhum veículo disponível")

# ==========================
# Produção automática
# ==========================
def producao_automatica():
    while True:
        if producao_auto_ativa and len(veiculos) < 5:
            tipo = random.choice(["Starship", "Super Heavy"])
            construir_veiculo(tipo)
        time.sleep(10)

# ==========================
# Eventos aleatórios
# ==========================
def evento_aleatorio():
    global recursos, reputacao
    while True:
        time.sleep(random.randint(20, 40))
        evento = random.choice(["tempestade", "problema_mecanico", "atraso_pad", "patrocinio"])
        if evento == "tempestade":
            dano = random.randint(10, 30)
            recursos = max(0, recursos - dano)
            barra_label.config(text=f"🌩️ Tempestade danificou a base! Recursos -{dano}")
        elif evento == "problema_mecanico":
            barra_label.config(text="⚠️ Problema mecânico! Lançamento atrasado")
            time.sleep(5)
        elif evento == "atraso_pad":
            barra_label.config(text="🕒 Problema no Pad Orbital, atraso")
            time.sleep(3)
        elif evento == "patrocinio":
            bonus = random.randint(20,50)
            recursos += bonus
            barra_label.config(text=f"💡 Patrocínio recebido! Recursos +{bonus}")
        atualizar_status()

# ==========================
# Lançamento de veículos
# ==========================
def lancar_veiculo():
    global dinheiro, reputacao, missao_disponivel, recursos, voo_em_andamento

    if not bays:
        barra_label.config(text="❌ Nenhum veículo no Bay")
        return

    veiculo = bays[0]

    if veiculo == "Starship":
        if "Pad Orbital" not in base or "Torre Pad" not in base:
            barra_label.config(text="❌ Precisa de Pad Orbital e Torre Pad para lançar Starship")
            return

    bays.pop(0)
    voo_em_andamento = True
    threading.Thread(target=voo_progresso, args=(veiculo,), daemon=True).start()

def voo_progresso(veiculo):
    global dinheiro, reputacao, missao_disponivel, recursos, voo_em_andamento
    fases = ["Motores ativos", "Separação booster", "Reentrada da Ship", "Pouso do booster", "Pouso da Ship"]
    total_passos = len(fases) * 5
    barra_progresso["maximum"] = total_passos
    progresso = 0
    chance_falha = max(0.15 - 0.03 * (upgrades["Starship"]-1), 0.05)
    sucesso = random.random() > chance_falha

    for i, fase in enumerate(fases):
        fase_label.config(text=f"Fase: {fase}")
        for _ in range(5):
            progresso += 1
            barra_progresso["value"] = progresso
            root.update()
            time.sleep(velocidade_voo)
            if not sucesso and i == 2:
                fase_label.config(text=f"💥 FALHA na fase {fase}!")
                barra_progresso["value"] = 0
                multa = random.randint(50_000, 200_000)
                global dinheiro
                dinheiro -= multa
                reputacao -= 10
                barra_label.config(text=f"💸 Multa da FAA: ${multa}")
                atualizar_status()
                voo_em_andamento = False
                return

    ganho = 400_000 if veiculo=="Super Heavy" else 300_000
    ganho_recursos = 70 if veiculo=="Super Heavy" else 50
    ganho_recursos += 10 * (upgrades["Booster"]-1)
    recursos += ganho_recursos
    if missao_disponivel and random.random() < 0.3:
        ganho *= 1.5
        ganho_recursos *= 2
        barra_label.config(text="🎯 Missão do governo concluída! Bônus aplicado")
        missao_disponivel = False
    dinheiro += ganho
    reputacao += 5
    barra_label.config(text=f"✅ Lançamento bem-sucedido! Dinheiro +${ganho}, Recursos +{ganho_recursos}")
    atualizar_status()
    barra_progresso["value"] = 0
    voo_em_andamento = False

# ==========================
# Upgrades
# ==========================
def melhorar(tipo):
    global dinheiro, recursos
    custo_dinheiro = 100_000 * upgrades[tipo]
    custo_recursos = 50 * upgrades[tipo]
    if dinheiro >= custo_dinheiro and recursos >= custo_recursos:
        dinheiro -= custo_dinheiro
        recursos -= custo_recursos
        upgrades[tipo] += 1
        barra_label.config(text=f"⬆️ Upgrade {tipo} realizado! Nível {upgrades[tipo]}")
        atualizar_status()
    else:
        barra_label.config(text="❌ Recursos insuficientes para upgrade")

# ==========================
# Reset e conserto
# ==========================
def resetar_base():
    global veiculos, base, bays, dinheiro, recursos, reputacao, missao_disponivel, mechazilla_disponivel
    confirm = messagebox.askyesno("Confirmar Reset", "Deseja realmente resetar a base?")
    if confirm:
        veiculos = []
        base = []
        bays = []
        dinheiro = 1_000_000
        recursos = 500
        reputacao = 50
        missao_disponivel = True
        mechazilla_disponivel = True
        barra_label.config(text="♻️ Base resetada!")
        atualizar_status()
        barra_progresso["value"] = 0
        fase_label.config(text="Fase: ---")

def consertar_base():
    global recursos, reputacao
    custo = random.randint(50, 150)
    if recursos >= custo:
        recursos -= custo
        reputacao += 2
        barra_label.config(text=f"🛠️ Base consertada! Recursos -{custo}, Reputação +2")
        atualizar_status()
    else:
        barra_label.config(text="❌ Recursos insuficientes para consertar")

# ==========================
# Mechazilla
# ==========================
def desploquiar_mechazilla():
    global recursos, reputacao, mechazilla_disponivel

    if "Mechazilla" not in base:
        barra_label.config(text="❌ Nenhum Mechazilla disponível")
        return

    if upgrades["Starship"] < 3 or upgrades["Booster"] < 2:
        barra_label.config(text="❌ Precisa Starship nível 3 e Booster nível 2 para recuperar Ship")
        return

    if voo_em_andamento:
        barra_label.config(text="⏳ Aguarde o pouso da Starship para desploquiar Mechazilla")
        return

    mechazilla_disponivel = False
    barra_label.config(text="🚀 Mechazilla desploquiado...")
    root.update()
    
    deslocamento = max(1, 5 - upgrades["Base"])
    for i in range(deslocamento):
        barra_progresso["value"] = (i+1)*20
        root.update()
        time.sleep(1)
    
    chance_sucesso = 0.7 + 0.1 * (upgrades["Base"]-1)
    sucesso = random.random() < chance_sucesso
    if sucesso:
        ganho_recuperacao = 50 * upgrades["Booster"]
        recursos += ganho_recuperacao
        reputacao += 5
        barra_label.config(text=f"✅ Mechazilla recuperou Ship ou Booster! Recursos +{ganho_recuperacao}")
    else:
        perda = 30
        recursos = max(0, recursos-perda)
        reputacao -= 5
        barra_label.config(text=f"⚠️ Falha na recuperação! Recursos -{perda}, Reputação -5")
    
    mechazilla_disponivel = True
    barra_progresso["value"] = 0
    atualizar_status()

# ==========================
# Interface Tkinter
# ==========================
root = tk.Tk()
root.title("Starbase Tycoon Sim")
root.configure(bg="#0a0a0a")

status_text = tk.StringVar()
status_label = tk.Label(root, textvariable=status_text, bg="#0a0a0a", fg="#00ff00", font=("Consolas", 10))
status_label.pack(fill=tk.X)
atualizar_status()

controle_frame = tk.Frame(root, bg="#0a0a0a")
controle_frame.pack(fill=tk.X, padx=5, pady=2)
criar_botao(controle_frame, "Ativar/Desativar Produção Auto", toggle_producao_auto).pack(side=tk.LEFT, padx=5)
criar_botao(controle_frame, "Aumentar velocidade do voo", lambda: ajustar_velocidade(0.1)).pack(side=tk.LEFT, padx=5)
criar_botao(controle_frame, "Diminuir velocidade do voo", lambda: ajustar_velocidade(-0.1)).pack(side=tk.LEFT, padx=5)

# Notebook
notebook = ttk.Notebook(root)
notebook.pack(pady=5, expand=True, fill="both")

# Aba Veículos
aba_veiculos = tk.Frame(notebook, bg="#0a0a0a")
notebook.add(aba_veiculos, text="Veículos")
tk.Label(aba_veiculos, text="Construir Veículos", bg="#0a0a0a", fg="#00ffff", font=("Consolas", 12, "bold")).pack(pady=5)

btn_starship = criar_botao(aba_veiculos, "🚀 Construir Starship", lambda: construir_veiculo("Starship"))
btn_starship.pack(pady=2)
ToolTip(btn_starship, "Custo: $200.000, Recursos: 50")

btn_superheavy = criar_botao(aba_veiculos, "🛰️ Construir Super Heavy", lambda: construir_veiculo("Super Heavy"))
btn_superheavy.pack(pady=2)
ToolTip(btn_superheavy, "Custo: $300.000, Recursos: 70")

btn_up_starship = criar_botao(aba_veiculos, "⬆️ Upgrade Starship", lambda: melhorar("Starship"))
btn_up_starship.pack(pady=2)
ToolTip(btn_up_starship, "Custo: $100.000 + 50 recursos por nível atual")

btn_up_booster = criar_botao(aba_veiculos, "⬆️ Upgrade Booster", lambda: melhorar("Booster"))
btn_up_booster.pack(pady=2)
ToolTip(btn_up_booster, "Custo: $100.000 + 50 recursos por nível atual")

# Aba Base
aba_base = tk.Frame(notebook, bg="#0a0a0a")
notebook.add(aba_base, text="Base")
tk.Label(aba_base, text="Construir Base", bg="#0a0a0a", fg="#00ffff", font=("Consolas", 12, "bold")).pack(pady=5)

btn_mechazilla = criar_botao(aba_base, "🤖 Mechazilla", lambda: construir_base_item("Mechazilla"))
btn_mechazilla.pack(pady=2)
ToolTip(btn_mechazilla, "Custo: $150.000, Recursos: 30")

btn_torrepad = criar_botao(aba_base, "🗼 Torre Pad", lambda: construir_base_item("Torre Pad"))
btn_torrepad.pack(pady=2)
ToolTip(btn_torrepad, "Custo: $100.000, Recursos: 20")

btn_padorbital = criar_botao(aba_base, "🛸 Pad Orbital", lambda: construir_base_item("Pad Orbital"))
btn_padorbital.pack(pady=2)
ToolTip(btn_padorbital, "Custo: $250.000, Recursos: 50")

btn_consertar = criar_botao(aba_base, "🛠️ Consertar Base", consertar_base, bg="#222222", fg="#00ffff", hover="#00ff00")
btn_consertar.pack(pady=2)
ToolTip(btn_consertar, "Custo aleatório em recursos: 50-150")

btn_reset = criar_botao(aba_base, "❌ Resetar Base", resetar_base, bg="red", fg="white", hover="#ff5555")
btn_reset.pack(pady=2)
ToolTip(btn_reset, "Reseta toda a base e recursos")

btn_up_base = criar_botao(aba_base, "⬆️ Upgrade Base", lambda: melhorar("Base"))
btn_up_base.pack(pady=2)
ToolTip(btn_up_base, "Custo: $100.000 + 50 recursos por nível atual")

# Aba Bays
aba_bays = tk.Frame(notebook, bg="#0a0a0a")
notebook.add(aba_bays, text="Bays")
tk.Label(aba_bays, text="Gerenciar Bays", bg="#0a0a0a", fg="#00ffff", font=("Consolas", 12, "bold")).pack(pady=5)

btn_armazenar = criar_botao(aba_bays, "📦 Armazenar Veículo", armazenar_bay)
btn_armazenar.pack(pady=2)
ToolTip(btn_armazenar, "Move o veículo para o Bay")

btn_lancar = criar_botao(aba_bays, "🚀 Lançar Veículo", lancar_veiculo)
btn_lancar.pack(pady=2)
ToolTip(btn_lancar, "Lança o veículo se tiver Pad e Torre")

btn_mechazilla_bay = criar_botao(aba_bays, "🤖 Desploquiar Mechazilla", desploquiar_mechazilla)
btn_mechazilla_bay.pack(pady=2)
ToolTip(btn_mechazilla_bay, "Recupera Ship se Starship>=3 e Booster>=2")

# Barra de progresso
style = ttk.Style()
style.theme_use('clam')
style.configure("green.Horizontal.TProgressbar", foreground="#00ff00", background="#00ff00", troughcolor="#111111")
barra_progresso = ttk.Progressbar(root, style="green.Horizontal.TProgressbar", orient="horizontal", length=400, mode="determinate")
barra_progresso.pack(pady=5)
fase_label = tk.Label(root, text="Fase: ---", bg="#0a0a0a", fg="#00ff00", font=("Consolas", 10))
fase_label.pack(pady=2)
barra_label = tk.Label(root, text="Bem-vindo à Starbase!", bg="#0a0a0a", fg="#00ff00", font=("Consolas", 10))
barra_label.pack(pady=5)

# Threads
threading.Thread(target=producao_automatica, daemon=True).start()
threading.Thread(target=evento_aleatorio, daemon=True).start()

root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import random

# =========================
# CONSTANTES
# =========================
COSTS = {
    "SuperHeavy": 300_000_000,
    "Starship Crew": 250_000_000,
    "Starship Cargo": 250_000_000,
    "HLS": 500_000_000,
    "Pad Upgrade": 500_000_000,
    "Tech Upgrade": 400_000_000,
    "Raptor3": 50_000_000,
    "Raptor4": 60_000_000,
    "RaptorVac": 70_000_000
}

MISSION_LIST = [
    {"name": "Órbita Baixa", "base_success": 0.6, "reward": 1_000_000_000, "requires": ["Starship Crew"]},
    {"name": "Satélite", "base_success": 0.65, "reward": 1_500_000_000, "requires": ["Starship Cargo"]},
    {"name": "Lua", "base_success": 0.55, "reward": 3_000_000_000, "requires": ["Starship Cargo","RaptorVac"]},
    {"name": "Marte", "base_success": 0.5, "reward": 5_000_000_000, "requires": ["Starship Crew","RaptorVac"]}
]

CONTRACTS = [
    {"name": "Lançamento de Satélite Civil", "reward": 800_000_000, "requires": ["Starship Cargo"], "completed": False, "remaining_turns":5},
    {"name": "Missão de Observação Lunar", "reward": 2_000_000_000, "requires": ["Starship Crew", "RaptorVac"], "completed": False, "remaining_turns":7},
    {"name": "Transporte de Carga Militar", "reward": 3_000_000_000, "requires": ["Starship Cargo","SuperHeavy"], "completed": False, "remaining_turns":10}
]

# =========================
# TOOLTIP
# =========================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

# =========================
# CLASSES
# =========================
class Company:
    def __init__(self):
        self.cash = 1_500_000_000
        self.tech_level = 1
        self.pad_level = 1
        self.launch_pads = 2
        self.naves = {"SuperHeavy": 0,"Starship Crew": 0,"Starship Cargo": 0,"HLS": 0}
        self.motores = {"Raptor3":0,"Raptor4":0,"RaptorVac":0}
        self.stack_ready = 0
        self.company_value = 5_000_000_000
        self.total_shares = 1_000_000
        self.player_shares = 1_000_000
        self.share_price = self.company_value / self.total_shares
        self.mission_index = 0
        self.last_launch_success = None
        self.contracts = [c.copy() for c in CONTRACTS]

    def update_share_price(self):
        value = self.cash + sum(self.naves.values())*250_000_000 + self.tech_level*100_000_000
        value += sum([c['reward'] for c in self.contracts if c['completed']])
        self.company_value = value
        self.share_price = self.company_value / self.total_shares

    def build_vehicle(self, vehicle_type):
        cost = COSTS[vehicle_type]
        if self.cash>=cost:
            self.cash-=cost
            self.naves[vehicle_type]+=1
            self.update_share_price()
            return f"🔩 {vehicle_type} construída!"
        return f"❌ Dinheiro insuficiente para {vehicle_type}!"

    def build_engine(self, engine_type):
        cost = COSTS[engine_type]
        if self.cash>=cost:
            self.cash-=cost
            self.motores[engine_type]+=1
            self.update_share_price()
            return f"⚙️ {engine_type} construída!"
        return f"❌ Dinheiro insuficiente para {engine_type}!"

    def stack_starship(self):
        if self.naves["SuperHeavy"]>0 and (self.naves["Starship Crew"]>0 or self.naves["Starship Cargo"]>0):
            self.naves["SuperHeavy"]-=1
            if self.naves["Starship Crew"]>0:
                self.naves["Starship Crew"]-=1
            else:
                self.naves["Starship Cargo"]-=1
            self.stack_ready+=1
            return "🏗️ Starship empilhada!"
        return "⚠️ Precisa de booster e nave!"

    def upgrade_tech(self):
        if self.cash>=COSTS["Tech Upgrade"]:
            self.cash-=COSTS["Tech Upgrade"]
            self.tech_level+=1
            self.update_share_price()
            return f"🔧 Tecnologia atualizada para nível {self.tech_level}!"
        return "❌ Dinheiro insuficiente para upgrade de tecnologia!"

    def upgrade_pad(self):
        cost = COSTS["Pad Upgrade"]*self.pad_level
        if self.cash>=cost:
            self.cash-=cost
            self.pad_level+=1
            self.launch_pads+=1
            self.update_share_price()
            return f"🏗️ Plataforma atualizada para nível {self.pad_level}!"
        return "❌ Dinheiro insuficiente para upgrade da plataforma!"

    def launch_mission(self):
        if self.stack_ready==0:
            return "⚠️ Empilhe primeiro!"
        if self.mission_index>=len(MISSION_LIST):
            return "Todas as missões concluídas!"
        launches = min(self.stack_ready,self.launch_pads)
        results = []
        for _ in range(launches):
            mission = MISSION_LIST[self.mission_index]
            for req in mission["requires"]:
                if self.naves.get(req,0)==0 and self.motores.get(req,0)==0:
                    results.append(f"⚠️ Missão exige {', '.join(mission['requires'])}!")
                    continue
            base = mission["base_success"] + self.tech_level*0.05
            success = random.random()<min(base,0.95)
            self.stack_ready-=1
            if success:
                self.cash+=mission["reward"]
                self.last_launch_success=True
                results.append(f"🚀 MISSÃO {mission['name']} COMPLETA! 💰 +${mission['reward']:,}")
                self.mission_index+=1
            else:
                self.cash-=mission["reward"]//2
                self.last_launch_success=False
                results.append(f"💥 Missão {mission['name']} falhou...")
        self.update_share_price()
        return "\n".join(results)

    # Contratos
    def complete_contract(self,index):
        if index>=len(self.contracts):
            return "Contrato inválido"
        c=self.contracts[index]
        if c["completed"]:
            return "Contrato já concluído!"
        for req in c["requires"]:
            if self.naves.get(req,0)==0 and self.motores.get(req,0)==0:
                return f"⚠️ Contrato exige {', '.join(c['requires'])}!"
        self.cash+=c["reward"]
        c["completed"]=True
        self.update_share_price()
        return f"🎯 Contrato '{c['name']}' concluído! 💰 +${c['reward']:,}"

    def advance_turn(self):
        for c in self.contracts:
            if not c["completed"]:
                c["remaining_turns"]-=1
                if c["remaining_turns"]<=0:
                    c["completed"]=True
                    self.cash-=c["reward"]//2  # Penalidade
        self.update_share_price()

# =========================
# INTERFACE
# =========================
class StarshipTycoonUI:
    def __init__(self, root, company: Company):
        self.root=root
        self.company=company
        self.bg="#1e1e1e"
        self.fg="#f1f1f1"
        self.btn="#3c3c3c"
        self.root.configure(bg=self.bg)

        self.notebook=ttk.Notebook(root)
        self.notebook.pack(fill='both',expand=True,padx=10,pady=10)

        # Status
        self.status_frame=tk.Frame(self.notebook,bg=self.bg)
        self.notebook.add(self.status_frame,text="Status")
        self.status_var=tk.StringVar()
        self.status_label=tk.Label(self.status_frame,textvariable=self.status_var,font=("Consolas",11),bg=self.bg,fg=self.fg,justify="left")
        self.status_label.pack(padx=10,pady=10)

        # Upgrades
        self.upgrade_frame=tk.Frame(self.notebook,bg=self.bg)
        self.notebook.add(self.upgrade_frame,text="Upgrades")
        self.create_upgrade_buttons()

        # Construção
        self.build_frame=tk.Frame(self.notebook,bg=self.bg)
        self.notebook.add(self.build_frame,text="Construção")
        self.create_build_buttons()

        # Contratos
        self.contract_frame=tk.Frame(self.notebook,bg=self.bg)
        self.notebook.add(self.contract_frame,text="Contratos")
        self.create_contract_buttons()

        # Log
        self.log_frame=tk.Frame(self.notebook,bg=self.bg)
        self.notebook.add(self.log_frame,text="Log")
        self.log_text=tk.Text(self.log_frame,height=15,bg="#2d2d2d",fg=self.fg,insertbackground=self.fg)
        self.log_text.pack(fill='both',expand=True)
        self.log_text.tag_config("success",foreground="lime")
        self.log_text.tag_config("fail",foreground="red")

        # Barra de progresso
        self.progress=ttk.Progressbar(root,orient='horizontal',length=400,mode='determinate')
        self.progress.pack(pady=5)

        self.update_status()

    # =========================
    # Status e Log
    # =========================
    def update_status(self):
        mission_name = MISSION_LIST[self.company.mission_index]["name"] if self.company.mission_index<len(MISSION_LIST) else "Concluídas"
        contracts_status = "\n".join([f"{i+1}. {c['name']} - {'✅' if c['completed'] else f'❌ ({c['remaining_turns']} turnos)'}" for i,c in enumerate(self.company.contracts)])
        status=f"""
💰 Caixa: ${self.company.cash:,}

🏗️ Plataformas: {self.company.launch_pads} (Nível {self.company.pad_level})
🔧 Tecnologia: {self.company.tech_level}

🔩 SuperHeavy: {self.company.naves['SuperHeavy']}
🛸 Starship Crew: {self.company.naves['Starship Crew']}
🛸 Starship Cargo: {self.company.naves['Starship Cargo']}
🚀 HLS: {self.company.naves['HLS']}
🚀 Stacks prontas: {self.company.stack_ready}

⚙️ Raptor3: {self.company.motores['Raptor3']}
⚙️ Raptor4: {self.company.motores['Raptor4']}
⚙️ RaptorVac: {self.company.motores['RaptorVac']}

📈 Valor empresa: ${self.company.company_value:,}
💵 Preço da ação: ${self.company.share_price:,.2f}

🎯 Próxima missão: {mission_name}

📝 Contratos:\n{contracts_status}
"""
        self.status_var.set(status)

    def log_event(self,text,success=False,fail=False):
        tag="success" if success else "fail" if fail else ""
        self.log_text.insert('end',text+'\n',tag)
        self.log_text.see('end')

    # =========================
    # Botões Upgrades
    # =========================
    def create_upgrade_buttons(self):
        btn_pad = tk.Button(self.upgrade_frame,text="Upgrade Plataforma",command=self.upgrade_pad,bg=self.btn,fg=self.fg,width=25)
        btn_pad.pack(pady=5)
        ToolTip(btn_pad, f"Custo: ${COSTS['Pad Upgrade']*self.company.pad_level:,}")

        btn_tech = tk.Button(self.upgrade_frame,text="Upgrade Tecnologia",command=self.upgrade_tech,bg=self.btn,fg=self.fg,width=25)
        btn_tech.pack(pady=5)
        ToolTip(btn_tech, f"Custo: ${COSTS['Tech Upgrade']:,}")

    def upgrade_pad(self):
        msg=self.company.upgrade_pad()
        self.log_event(msg)
        self.company.advance_turn()
        self.update_status()

    def upgrade_tech(self):
        msg=self.company.upgrade_tech()
        self.log_event(msg)
        self.company.advance_turn()
        self.update_status()

    # =========================
    # Botões Construção
    # =========================
    def create_build_buttons(self):
        for n in ["SuperHeavy","Starship Crew","Starship Cargo","HLS"]:
            btn = tk.Button(self.build_frame,text=f"Construir {n}",command=lambda n=n:self.build_vehicle(n),bg=self.btn,fg=self.fg,width=25)
            btn.pack(pady=2)
            ToolTip(btn, f"Custo: ${COSTS[n]:,}")
        for m in ["Raptor3","Raptor4","RaptorVac"]:
            btn = tk.Button(self.build_frame,text=f"Construir {m}",command=lambda m=m:self.build_engine(m),bg=self.btn,fg=self.fg,width=25)
            btn.pack(pady=2)
            ToolTip(btn, f"Custo: ${COSTS[m]:,}")

        btn_stack = tk.Button(self.build_frame,text="Empilhar Starship",command=self.stack_starship,bg=self.btn,fg=self.fg,width=25)
        btn_stack.pack(pady=5)
        ToolTip(btn_stack, "Empilha uma Starship com booster (prepara para lançamento)")

        btn_launch = tk.Button(self.build_frame,text="Lançar Missão",command=self.launch_mission,bg=self.btn,fg=self.fg,width=25)
        btn_launch.pack(pady=5)
        ToolTip(btn_launch, "Lança uma missão com base na stack pronta")

    def build_vehicle(self,vehicle_type):
        msg=self.company.build_vehicle(vehicle_type)
        self.log_event(msg)
        self.company.advance_turn()
        self.update_status()

    def build_engine(self,engine_type):
        msg=self.company.build_engine(engine_type)
        self.log_event(msg)
        self.company.advance_turn()
        self.update_status()

    def stack_starship(self):
        msg=self.company.stack_starship()
        self.log_event(msg)
        self.company.advance_turn()
        self.update_status()

    def launch_mission(self):
        if self.company.stack_ready==0:
            self.log_event("⚠️ Empilhe primeiro!")
            return
        if self.company.mission_index>=len(MISSION_LIST):
            self.log_event("Todas as missões concluídas!")
            return
        launches=min(self.company.stack_ready,self.company.launch_pads)
        for _ in range(launches):
            self.progress["value"]=0
            self.root.update_idletasks()
            for i in range(0,101,20):
                self.progress["value"]=i
                self.root.update_idletasks()
                self.root.after(150)
            msg=self.company.launch_mission()
            self.log_event(msg,success=self.company.last_launch_success,fail=not self.company.last_launch_success)
        self.company.advance_turn()
        self.update_status()
        if self.company.mission_index==len(MISSION_LIST):
            messagebox.showinfo("VITÓRIA","🎉 Todas as missões concluídas!")

    # =========================
    # Contratos
    # =========================
    def create_contract_buttons(self):
        for i,c in enumerate(self.company.contracts):
            btn = tk.Button(self.contract_frame,text=f"Completar '{c['name']}'",command=lambda i=i:self.complete_contract(i),
                      bg=self.btn,fg=self.fg,width=40)
            btn.pack(pady=5)
            ToolTip(btn, f"Requer: {', '.join(c['requires'])} | Recompensa: ${c['reward']:,} | Restam {c['remaining_turns']} turnos")

    def complete_contract(self,index):
        msg=self.company.complete_contract(index)
        self.log_event(msg,success="concluído" in msg)
        self.company.advance_turn()
        self.update_status()

# =========================
# TUTORIAL INTERATIVO
# =========================
def start_tutorial(ui):
    steps = [
        {"widget": ui.status_label, "text": "💰 Aqui você vê seu caixa, plataformas, tecnologia e status das naves."},
        {"widget": ui.build_frame.winfo_children()[0], "text": "🔩 Clique aqui para construir naves como Super Heavy ou Starship."},
        {"widget": ui.upgrade_frame.winfo_children()[0], "text": "🔧 Use os upgrades para melhorar tecnologia e plataformas."},
        {"widget": ui.contract_frame.winfo_children()[0], "text": "📝 Aba de contratos: complete-os antes do prazo."},
        {"widget": ui.log_text, "text": "📰 Aqui aparecem todos os eventos e resultados das missões."},
        {"widget": ui.progress, "text": "📊 Barra de progresso mostra o avanço de cada lançamento."}
    ]

    def show_step(i=0):
        if i>=len(steps):
            return
        step = steps[i]
        x = step["widget"].winfo_rootx() + step["widget"].winfo_width() + 10
        y = step["widget"].winfo_rooty()
        tip = tk.Toplevel(ui.root)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tip, text=step["text"], justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "10", "bold"), wraplength=250)
        label.pack(ipadx=5, ipady=5)
        btn_next = tk.Button(tip, text="Próximo", command=lambda: [tip.destroy(), show_step(i+1)])
        btn_next.pack(pady=5)

    show_step()

# =========================
# INICIALIZAÇÃO
# =========================
if __name__=="__main__":
    root=tk.Tk()
    root.title("🌌 Starship Tycoon")
    company=Company()
    app=StarshipTycoonUI(root,company)
    root.after(500, lambda: start_tutorial(app))  # tutorial inicia 0.5s depois
    root.mainloop()
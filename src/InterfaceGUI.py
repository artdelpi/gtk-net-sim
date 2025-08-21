import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import matplotlib
matplotlib.use("GTK3Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import queue

class Simulador(Gtk.Window):
    def __init__(self, in_queue: queue, out_queue: queue,  gui_rx):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.gui_rx = gui_rx

        Gtk.Window.__init__(self, title="Simulador de Camada Física / Enlace")
        self.set_default_size(1000, 600)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(main_box)

        config_frame = Gtk.Frame(label="Configurações Gerais")
        config_grid = Gtk.Grid(column_spacing=10, row_spacing=5, margin=10)
        config_frame.add(config_grid)

        def add_row(label_text, widget, row):
            config_grid.attach(Gtk.Label(label=label_text), 0, row, 1, 1)
            config_grid.attach(widget, 1, row, 1, 1)

        self.entrada_texto = Gtk.Entry()
        self.edc = Gtk.SpinButton()
        self.enquadramento = Gtk.ComboBoxText()
        self.detecao = Gtk.ComboBoxText()
        self.detecao.connect("changed", self.on_detecao_changed)
        self.mod_digital = Gtk.ComboBoxText()
        self.mod_analogica = Gtk.ComboBoxText()
        self.erros = Gtk.SpinButton()

        widgets = [
            ("Entrada de texto", self.entrada_texto),
            ("Tamanho do EDC", self.edc),
            ("Tipo de enquadramento", self.enquadramento),
            ("Tipo de detecção ou correção", self.detecao),
            ("Tipo de modulação digital", self.mod_digital),
            ("Tipo de modulação analógica", self.mod_analogica),
            ("Nível de ruído (σ)", self.erros)
        ]

        self.simular_btn = Gtk.Button(label="Simular")
        self.simular_btn.connect("clicked", self.on_simular_clicked)
        config_grid.attach(self.simular_btn, 0, len(widgets), 2, 1)

        self.edc.set_adjustment(Gtk.Adjustment(lower=8, upper=256, step_increment=8, page_increment=8))
        self.edc.set_value(8)  # Valor padrão inicial
        self.erros.set_adjustment(Gtk.Adjustment(lower=0, upper=100, step_increment=0.1, page_increment=1))
        self.erros.set_digits(2)

        tipos_enquadramento = [
            "Contagem de caracteres",
            "FLAGS e inserção de bytes ou caracteres",
            "FLAGS Inserção de bits"
        ]
        for tipo_enquadramento in tipos_enquadramento:
            self.enquadramento.append_text(tipo_enquadramento)
        self.enquadramento.set_entry_text_column(0)
        self.enquadramento.set_active(0)

        tipos_detecao = [
            "Bit de paridade par",
            "CRC", 
            "Hamming"
        ]
        for tipo_detecao in tipos_detecao:
            self.detecao.append_text(tipo_detecao)
        self.detecao.set_entry_text_column(0)
        self.detecao.set_active(0)

        tipos_modulacao_analogica = [
            "ASK",
            "FSK",
            "8-QAM"
        ]
        for tipo_modulacao_analogica in tipos_modulacao_analogica:
            self.mod_analogica.append_text(tipo_modulacao_analogica)
        self.mod_analogica.set_entry_text_column(0)
        self.mod_analogica.set_active(0)

        tipos_modulacao_digital = [
            "NRZ-Polar",
            "Manchester",
            "Bipolar"
        ]
        for tipo_modulacao_digital in tipos_modulacao_digital:
            self.mod_digital.append_text(tipo_modulacao_digital)
        self.mod_digital.set_entry_text_column(0)
        self.mod_digital.set_active(0)


        for i, (label, widget) in enumerate(widgets):
            add_row(label, widget, i)

        
        notebook = Gtk.Notebook()

        self.aba_aplicacao = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)
        self.aba_enlace = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)
        self.figuras = [] 
        self.aba_graficos = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)

        notebook.append_page(self.aba_aplicacao, Gtk.Label(label="Camada de Aplicação"))
        notebook.append_page(self.aba_enlace, Gtk.Label(label="Camada Enlace"))
        notebook.append_page(self.aba_graficos, Gtk.Label(label="Camada Física"))
        

        main_box.pack_start(config_frame, False, False, 10)
        main_box.pack_start(notebook, True, True, 10)
        
        GLib.timeout_add(100, self.atualizar_saidas)  # checa fila a cada 100ms

    def on_detecao_changed(self, widget):
        tipo = widget.get_active_text()
        # Só permite escolher o tamanho do EDC se selecionar CRC
        if tipo == "CRC":
            self.edc.set_sensitive(True)  # Ativa o campo EDC
        else:
            self.edc.set_sensitive(False)  # Desativa o campo EDC
    
    def on_simular_clicked(self, widget):
        GLib.idle_add(self.gui_rx.limpar_abas)

        #Limpa os gráficos
        for box in [self.aba_aplicacao, self.aba_enlace]:
            for child in box.get_children():
                box.remove(child)

        for canvas in self.figuras:
            self.aba_graficos.remove(canvas)
        self.figuras = []

        self.out_queue.put({
            "entrada": self.entrada_texto.get_text(),
            "edc": self.edc.get_value_as_int(),
            "enquadramento": self.enquadramento.get_active_text(),
            "detecao": self.detecao.get_active_text(),
            "mod_digital": self.mod_digital.get_active_text(),
            "mod_analogica": self.mod_analogica.get_active_text(),
            "erros": self.erros.get_value()
        })
    
    def atualizar_saidas(self):
        try:
            while True:
                camada, dado = self.in_queue.get_nowait()

                if camada == "aplicacao" and isinstance(dado, str):
                    label = Gtk.Label(label=dado)
                    self.aba_aplicacao.pack_start(label, False, False, 5)
                    label.show_all()

                elif camada == "enlace" and isinstance(dado, str):
                    label = Gtk.Label(label=dado)
                    self.aba_enlace.pack_start(label, False, False, 5)
                    label.show_all()

                elif camada == "fisica" and isinstance(dado, Figure):
                    canvas = FigureCanvas(dado)
                    canvas.set_hexpand(True)
                    canvas.set_size_request(400, 300) 
                    self.figuras.append(canvas)
                    linha = len(self.figuras) - 1  # Uma linha por gráfico
                    coluna = 0  # Sempre começa na primeira coluna
                    self.aba_graficos.attach(canvas, coluna, linha, 2, 1)
                    self.aba_graficos.show_all()
        except queue.Empty:
            pass
        return True 

class GUI_TX:
    def __init__(self, in_queue, out_queue, gui_rx):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.gui_rx = gui_rx

    def create_window(self):
        win = Simulador(self.in_queue, self.out_queue, self.gui_rx)
        return win


class GUI_RX(Gtk.Window):
    def __init__(self, in_queue: queue.Queue):
        super().__init__(title="Receptor")
        self.set_default_size(800, 600)
        self.in_queue = in_queue
        self.figuras = []

        notebook = Gtk.Notebook()
        self.aba_aplicacao = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)
        self.aba_enlace = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)
        self.aba_graficos = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)

        notebook.append_page(self.aba_aplicacao, Gtk.Label(label="Camada de Aplicação"))
        notebook.append_page(self.aba_enlace, Gtk.Label(label="Camada Enlace"))
        notebook.append_page(self.aba_graficos, Gtk.Label(label="Camada Física"))

        self.add(notebook)
        GLib.timeout_add(100, self.atualizar_saidas)

    def atualizar_saidas(self):
        try:
            while True:
                camada, dado = self.in_queue.get_nowait()

                if camada == "aplicacao" and isinstance(dado, str):
                    label = Gtk.Label(label=dado)
                    self.aba_aplicacao.pack_start(label, False, False, 5)
                    label.show_all()

                elif camada == "enlace" and isinstance(dado, str):
                    label = Gtk.Label(label=dado)
                    self.aba_enlace.pack_start(label, False, False, 5)
                    label.show_all()

                elif camada == "fisica" and isinstance(dado, Figure):
                    canvas = FigureCanvas(dado)
                    canvas.set_hexpand(True)
                    canvas.set_size_request(400, 300)
                    self.figuras.append(canvas)
                    linha = len(self.figuras) - 1
                    self.aba_graficos.attach(canvas, 0, linha, 2, 1)
                    self.aba_graficos.show_all()
        except queue.Empty:
            pass
        return True

    def limpar_abas(self):
    # Limpa a aba de aplicação
        for child in self.aba_aplicacao.get_children():
            self.aba_aplicacao.remove(child)
        
        # Limpa a aba de enlace
        for child in self.aba_enlace.get_children():
            self.aba_enlace.remove(child)
        
        # Limpa a aba de física (gráficos)
        for child in self.aba_graficos.get_children():
            self.aba_graficos.remove(child)
        
        self.figuras = []  # Reseta a lista de figuras
        self.aba_graficos.show_all()  # Atualiza a interface

if __name__ == "__main__":
    import queue

    in_queue = queue.Queue()
    out_queue = queue.Queue()

    gui = GUI(in_queue, out_queue)
    gui.start()
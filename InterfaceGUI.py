import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import matplotlib
matplotlib.use("GTK3Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import queue

class Simulador(Gtk.Window):
    def __init__(self, in_queue: queue, out_queue: queue):
        self.in_queue = in_queue
        self.out_queue = out_queue

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
        self.tamanho_quadro = Gtk.SpinButton()
        self.edc = Gtk.SpinButton()
        self.enquadramento = Gtk.ComboBoxText()
        self.detecao = Gtk.ComboBoxText()
        self.mod_digital = Gtk.ComboBoxText()
        self.mod_analogica = Gtk.ComboBoxText()
        self.erros = Gtk.SpinButton()

        widgets = [
            ("Entrada de texto", self.entrada_texto),
            ("Tamanho máximo de quadro", self.tamanho_quadro),
            ("Tamanho do EDC", self.edc),
            ("Tipo de enquadramento", self.enquadramento),
            ("Tipo de detecção ou correção", self.detecao),
            ("Tipo de modulação digital", self.mod_digital),
            ("Tipo de modulação analógica", self.mod_analogica),
            ("Taxa de erros", self.erros)
        ]

        self.simular_btn = Gtk.Button(label="Simular")
        self.simular_btn.connect("clicked", self.on_simular_clicked)
        config_grid.attach(self.simular_btn, 0, len(widgets), 2, 1)

        self.tamanho_quadro.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))
        self.edc.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))
        self.erros.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))

        tipos_enquadramento = [
            "1",
            "2"
        ]
        for tipo_enquadramento in tipos_enquadramento:
            self.enquadramento.append_text(tipo_enquadramento)
        self.enquadramento.set_entry_text_column(0)
        self.enquadramento.set_active(0)

        tipos_detecao = [
            "Tipo 1",
            "Tipo 2"
        ]
        for tipo_detecao in tipos_detecao:
            self.detecao.append_text(tipo_detecao)
        self.detecao.set_entry_text_column(0)
        self.detecao.set_active(0)

        tipos_modulacao_analogica = [
            "Tipo 1",
            "Tipo 2"
        ]
        for tipo_modulacao_analogica in tipos_modulacao_analogica:
            self.mod_analogica.append_text(tipo_modulacao_analogica)
        self.mod_analogica.set_entry_text_column(0)
        self.mod_analogica.set_active(0)

        tipos_modulacao_digital = [
            "A",
            "B"
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

    
    def on_simular_clicked(self, widget):
        #Limpa os gráficos
        for box in [self.aba_aplicacao, self.aba_enlace]:
            for child in box.get_children():
                box.remove(child)
        self.figuras.clear()

        for canvas in self.figuras:
            self.aba_graficos.remove(canvas)

        self.out_queue.put({
            "entrada": self.entrada_texto.get_text(),
            "quadro": self.tamanho_quadro.get_value_as_int(),
            "edc": self.edc.get_value_as_int(),
            "enquadramento": self.enquadramento.get_active_text(),
            "detecao": self.detecao.get_active_text(),
            "mod_digital": self.mod_digital.get_active_text(),
            "mod_analogica": self.mod_analogica.get_active_text(),
            "erros": self.erros.get_value_as_int()
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
                    canvas.set_size_request(400, 300) 
                    self.figuras.append(canvas)
                    linha = len(self.figuras) // 2
                    coluna = len(self.figuras) % 2
                    self.aba_graficos.attach(canvas, coluna, linha, 1, 1)
                    self.aba_graficos.show_all()

        except queue.Empty:
            pass
        return True 

class GUI:
    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue

    def start(self):
        win = Simulador(self.in_queue, self.out_queue)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class Simulador(Gtk.Window):
    def __init__(self):
        
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

        aba_texto = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin=10)

        notebook.append_page(aba_texto, Gtk.Label(label="Resultados Textuais"))

        aba_graficos = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)
        for i in range(2):
            for j in range(2):
                drawing_area = Gtk.DrawingArea()
                drawing_area.set_size_request(200, 150)
                aba_graficos.attach(drawing_area, j, i, 1, 1)
        notebook.append_page(aba_graficos, Gtk.Label(label="Gráficos de Sinal"))

        main_box.pack_start(config_frame, False, False, 10)
        main_box.pack_start(notebook, True, True, 10)
    
    def on_simular_clicked(self, widget):
        print(f'''                Entrada de texto: {self.entrada_texto.get_text()}
                Tamanho máximo de quadro: {self.tamanho_quadro.get_value_as_int()},
                Tamanho do EDC: {self.edc.get_value_as_int()}
                Tipo de enquadramento: {self.enquadramento.get_active_text()}
                Tipo de enquadramento: {self.enquadramento.get_active_text()}
                Tipo de detecção ou correção: {self.detecao.get_active_text()}
                Tipo de modulação digital: {self.mod_digital.get_active_text()}
                Tipo de modulação analógica: {self.mod_analogica.get_active_text()}
                Taxa de erros: {self.erros.get_value_as_int()}
            ''') 

win = Simulador()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
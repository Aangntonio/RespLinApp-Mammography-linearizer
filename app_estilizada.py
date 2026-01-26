
import wx
import wx.grid 
import wx.adv
import numpy as np
import pydicom as dcm
import scipy.io as sio
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from Modulo_FR import ROI_calculadora, ODR_adjust
import matplotlib.pyplot as plt
from scipy.odr import ODR, Model, RealData
from sklearn.metrics import r2_score
###Colores de la GUI###
#Hola, no se quien carajos lea esto, pero este es un programa para linealizar imagenes DICOM
#de MAMOgrafias, originalmente, llamada MILF (Mammografy Image Linealizer FUnction)

COLOR_BACKGROUND = "#DDDBF2"  # Fondo
COLOR_PANEL = "#FFFFFF"       # Contrase
COLOR_BUTTON = "#5D61CD"      # Btonones
COLOR_TEXT_DARK = "#13293D"   # LEtras

# # ---- Función de conversión exponencial ----
#    ___                              _                  
#   / __\___  _ ____   _____ _ __ ___(_) ___  _ __       
#  / /  / _ \| '_ \ \ / / _ \ '__/ __| |/ _ \| '_ \      
# / /__| (_) | | | \ V /  __/ |  \__ \ | (_) | | | |     
# \____/\___/|_| |_|\_/ \___|_|  |___/_|\___/|_| |_|     
                                                       
#                                              _       _ 
#   _____  ___ __   ___  _ __   ___ _ __   ___(_) __ _| |
#  / _ \ \/ / '_ \ / _ \| '_ \ / _ \ '_ \ / __| |/ _` | |
# |  __/>  <| |_) | (_) | | | |  __/ | | | (__| | (_| | |
#  \___/_/\_\ .__/ \___/|_| |_|\___|_| |_|\___|_|\__,_|_|
#           |_|                                          
def Conversion_exponencial(P, B, A):
    """Calcula la conversión exponencial."""
    termino = (P - B) / A
    return np.exp(termino)
##Esat funcion conveirte valores de pixel a valores de kerma o exposicion, dada la forma
#ESAK  = A * ln ( (Pixel Value ) ) + B
                                 
#               ,----..            
# ,-.----.     /   /   \     ,---, 
# \    /  \   /   .     : ,`--.' | 
# ;   :    \ .   /   ;.  \|   :  : 
# |   | .\ :.   ;   /  ` ;:   |  ' 
# .   : |: |;   |  ; \ ; ||   :  | 
# |   |  \ :|   :  | ; | ''   '  ; 
# |   : .  /.   |  ' ' ' :|   |  | 
# ;   | |  \'   ;  \; /  |'   :  ; 
# |   | ;\  \\   \  ',  / |   |  ' 
# :   ' | \.' ;   :    /  '   :  | 
# :   : :-'    \   \ .'   ;   |.'  
# |   |.'       `---`     '---'    
# `---'                            
                                 
def ROI_calculadora(I,x,y,l = 100):
    '''
    ESta funcion obtiene los valores de Mean Pixel Value y la desviacion destandar de una cierta ROI 
    de pixeles
    Argumientos:
    I = imagen 
    x = coordenada del centro en x
    y = coordenada del centro en y
    l = tamaño de la ROI , por defecto 100 pixeles
    Returns
    MPV = valor del pixel promedio
    sd_MPV = desviacoon estdanr de los valores
    '''
    x = int(x)
    y = int(y)
    half_l = int(l // 2)
    x_min = max(0, x - half_l)
    x_max = min(I.shape[0], x + half_l)
    y_min = max(0, y - half_l)
    y_max = min(I.shape[1], y + half_l)

    ROI = I[x_min:x_max, y_min:y_max]
    MPV = np.mean(ROI)
    sd_MPV = np.std(ROI)

    return MPV, sd_MPV
#    _____       __                __          
#   /  _  \     |__|__ __  _______/  |_  ____  
#  /  /_\  \    |  |  |  \/  ___/\   __\/ __ \ 
# /    |    \   |  |  |  /\___ \  |  | \  ___/ 
# \____|__  /\__|  |____//____  > |__|  \___  >
#         \/\______|          \/            \/ 
# ________  ________ __________                
# \_____  \ \______ \\______   \               
#  /   |   \ |    |  \|       _/               
# /    |    \|    `   \    |   \               
# \_______  /_______  /____|_  /               
#         \/        \/       \/                

def ODR_adjust(x,y,sdx,sdy, tipo = 'lineal',xlbel = 'MPV',ylbel = 'Kerma'):
    '''
    Esta funcion calcula el ajuste ODR (lineal) de datos x y y con sus respectivos desviaciones estandar
    '''

    odr_data = RealData(x = x, y = y, sx= sdx, sy =sdy)

    #Modelo del ODR en este caso debe de ser lineal o exponencial

    def lineal(B,x):
        return B[0]*x + B[1]
    
    def exponencial(B,x):
        return B[0]*np.exp(x)**B[1]
    ####Modelo

    if tipo == 'lineal':

        odr_model = Model(lineal)

    elif tipo == 'exponencial':
        odr_model = Model(exponencial)
    ###Momentaneamente, solo se puede convertir en un 


    #Ajuste
    odr_fit = ODR(odr_data,odr_model, beta0= [1,1])
    out = odr_fit.run()
    
    param = out.beta
    incert = out.sd_beta

    m,b = param
    dm, db = incert
    x_fit = np.linspace(x[0],x[-1], 1000)
    y_fit = lineal(param,x_fit)

    y_pred = lineal(param,x)

    R2 = r2_score(y, y_pred)

    return param, incert, R2    
####inicio de la GUI
class RespLinApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="RespLin App", size=(850, 650))

#       ###icono
        self.SetIcon(wx.Icon("icono.ico"))


        # Ba
        self.make_tool_bar()

        # El panel principal ahora ocupa toda la ventana
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(COLOR_BACKGROUND) # Aplicar nuevo color de fondo

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Panel de Trabajo (Workspace) ---
        self.workspace_panel = wx.Panel(self.panel)
        self.workspace_panel.SetBackgroundColour(COLOR_PANEL) # Fondo blanco para las imágenes
        self.ws_sizer = wx.BoxSizer(wx.VERTICAL)
        

        ###3mensaje de bienvenida
        ##iconos
        font_titulo = wx.Font(16, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        font_instruccion = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        color_titulo = wx.Colour("#005A9C") # Un azul profesional
        color_texto = wx.Colour("#333333") # Texto oscuro estándar

        # 2. Creamos una StaticBox para enmarcar todo el mensaje
        welcome_box = wx.StaticBox(self.workspace_panel, label="Inicio Rápido")
        # El sizer principal del bloque será un StaticBoxSizer
        welcome_block_sizer = wx.StaticBoxSizer(welcome_box, wx.VERTICAL)

        # 3. Creamos el título "Bienvenido" por separado para darle un estilo único
        welcome_label = wx.StaticText(self.workspace_panel, label="Bienvenido")
        welcome_label.SetFont(font_titulo)
        welcome_label.SetForegroundColour(color_titulo)

        # Agregamos el título al sizer del bloque, centrado y con espacio debajo
        welcome_block_sizer.Add(welcome_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)

        # 4. Obtenemos los íconos (esto no cambia)
        find_bmp = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_BUTTON, (16,16))
        new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_BUTTON, (16,16))

        # --- PRIMERA LÍNEA DE INSTRUCCIÓN ---
        text1 = wx.StaticText(self.workspace_panel, label="Presiona ")
        icon1 = wx.StaticBitmap(self.workspace_panel, bitmap=find_bmp)
        text2 = wx.StaticText(self.workspace_panel, label=" para encontrar la función de respuesta.")

        # Aplicamos el estilo de instrucción a los textos
        for txt in [text1, text2]:
            txt.SetFont(font_instruccion)
            txt.SetForegroundColour(color_texto)

        line1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line1_sizer.Add(text1, 0, wx.ALIGN_CENTER_VERTICAL)
        line1_sizer.Add(icon1, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        line1_sizer.Add(text2, 0, wx.ALIGN_CENTER_VERTICAL)

        # --- SEGUNDA LÍNEA DE INSTRUCCIÓN ---
        text3 = wx.StaticText(self.workspace_panel, label="O si ya tienes Fr, presiona ")
        icon2 = wx.StaticBitmap(self.workspace_panel, bitmap=new_bmp)
        text4 = wx.StaticText(self.workspace_panel, label=" para linearizar una imagen DICOM.")

        # Aplicamos el estilo de instrucción a los textos
        for txt in [text3, text4]:
            txt.SetFont(font_instruccion)
            txt.SetForegroundColour(color_texto)

        line2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line2_sizer.Add(text3, 0, wx.ALIGN_CENTER_VERTICAL)
        line2_sizer.Add(icon2, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        line2_sizer.Add(text4, 0, wx.ALIGN_CENTER_VERTICAL)


        # 5. Agregamos las líneas de instrucción al sizer del bloque
        #    Usamos wx.ALIGN_LEFT para que el texto se lea naturalmente
        welcome_block_sizer.Add(line1_sizer, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        welcome_block_sizer.Add(line2_sizer, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)


        # 6. Finalmente, agregamos el bloque completo (el StaticBoxSizer) al sizer del panel
        self.ws_sizer.Add(welcome_block_sizer, 0, wx.CENTER | wx.ALL, 20)


        # welcome_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        # self.welcome_text = wx.StaticText(self.workspace_panel, label="\n\nBienvenido.\n\n")
        # self.welcome_text.SetFont(welcome_font)
        # self.welcome_text.SetForegroundColour(COLOR_TEXT_DARK) # Aplicar nuevo color de texto
        
        #self.ws_sizer.Add(self.welcome_text, 1, wx.ALIGN_CENTER)
        ####


        #####NOT TOCUH pleasseee}
        ###Cuando ella baila
        ###Debajo esa mini falda

        self.workspace_panel.SetSizer(self.ws_sizer)
        main_sizer.Add(self.workspace_panel, 1, wx.EXPAND | wx.ALL, 10)

        # --- Panel Inferior para el botón "Acerca de" ---
        bottom_panel = wx.Panel(self.panel)
        # Hacemos que el panel inferior comparta el color de fondo principal
        bottom_panel.SetBackgroundColour(COLOR_BACKGROUND)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        about_btn = wx.Button(bottom_panel, label="Acerca de...")
        about_btn.Bind(wx.EVT_BUTTON, self.show_about_dialog)
        
        bottom_sizer.AddStretchSpacer(prop=1)
        bottom_sizer.Add(about_btn, 0, wx.ALL, 5)
        
        bottom_panel.SetSizer(bottom_sizer)
        main_sizer.Add(bottom_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.panel.SetSizerAndFit(main_sizer)
        
        # Variables de instancia
        self.dicom = None
        self.imagen_linear = None
        self.canvas = None
        self.img_artist_linear = None
        self.Centre()
        self.Show()

    def make_tool_bar(self):
        toolbar = self.CreateToolBar()
        
        lin_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR)
        fr_bmp = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_TOOLBAR)
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR)
        hist_bmp = wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR)
        enhance_bmp = wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_TOOLBAR)
        help_bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_TOOLBAR)
        exit_bmp = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR)
        
        self.tool_fr = toolbar.AddTool(wx.ID_ANY, "FR", fr_bmp, "Calcular la Función de Respuesta (FR)")
        self.tool_lin = toolbar.AddTool(wx.ID_ANY, "Linearizar", lin_bmp, "Linearizar un archivo DICOM")
        self.tool_save = toolbar.AddTool(wx.ID_ANY, "Guardar", save_bmp, "Guardar el DICOM linearizado")
        toolbar.AddSeparator()
        self.tool_hist = toolbar.AddTool(wx.ID_ANY, "Histograma", hist_bmp, "Mostrar histograma de la imagen linealizada")
        self.tool_enhance = toolbar.AddTool(wx.ID_ANY, "Mejorar", enhance_bmp, "Mejorar brillo/contraste de la vista linealizada")
        toolbar.AddStretchableSpace()
        self.tool_help = toolbar.AddTool(wx.ID_HELP, "Ayuda", help_bmp, "Mostrar ayuda")
        self.tool_exit = toolbar.AddTool(wx.ID_EXIT, "Salir", exit_bmp, "Cerrar la aplicación")

        self.Bind(wx.EVT_TOOL, self.linearizar_dicoms, self.tool_lin)
        self.Bind(wx.EVT_TOOL, self.open_fr_window, self.tool_fr)
        self.Bind(wx.EVT_TOOL, self.savedicom, self.tool_save)
        self.Bind(wx.EVT_TOOL, self.show_histogram, self.tool_hist)
        self.Bind(wx.EVT_TOOL, self.enhance_image, self.tool_enhance)
        self.Bind(wx.EVT_TOOL, self.show_help, self.tool_help)
        self.Bind(wx.EVT_TOOL, lambda e: self.Close(), self.tool_exit)

        toolbar.Realize()
        ####### inhabilita los botones
        toolbar.EnableTool(self.tool_hist.GetId(), False)
        toolbar.EnableTool(self.tool_enhance.GetId(), False)
        toolbar.EnableTool(self.tool_save.GetId(), False)

    def show_about_dialog(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("RespLin App")
        info.SetVersion("2.1.0") # Versión actualizada
        info.SetDescription(
            "Una aplicación para la linearización de imágenes radiograficas DICOM "
            "y el cálculo de la función de respuesta del detector."
        )
        info.SetCopyright("(C) 2025 UNAM")
        info.AddDeveloper("Jose Antonio Gonzalez Gonzalez")
        info.SetWebSite("https://github.com/Aangntonio/Linearizer-FunctionResponse-Mammography", "Repositorio de GitHub")
        wx.adv.AboutBox(info)

    def show_help(self, event):
        help_title = "Ayuda de RespLin App"
        help_message = (
            "--- Flujo de Trabajo ---\n\n"
            "1. Calcular Función de Respuesta (FR):\n"
            "   - Haz clic en el botón 'FR'.\n"
            "   - Carga un archivo CSV y los archivos DICOM correspondientes.\n"
            "   - Calcula la FR para generar los parámetros de linealización (A y B).\n\n"
            "2. Linearizar DICOM:\n"
            "   - Haz clic en el botón 'Linearizar'.\n"
            "   - Selecciona el archivo de parámetros (.mat o .txt).\n"
            "   - Selecciona el archivo DICOM que deseas linearizar.\n\n"
            "3. Mejorar y Analizar (Opcional):\n"
            "   - 'Mejorar': Ajusta el brillo/contraste de la vista.\n"
            "   - 'Histograma': Muestra la distribución de valores de píxel.\n\n"
            "4. Guardar DICOM:\n"
            "   - Haz clic en 'Guardar' para almacenar el nuevo archivo DICOM."
        )
        wx.MessageBox(help_message, help_title, wx.OK | wx.ICON_INFORMATION)

    def linearizar_dicoms(self, event):
        with wx.FileDialog(self, "Seleccionar archivo de parámetros (.mat o .txt)",
                           wildcard="Archivos de parámetros (*.mat;*.txt)|*.mat;*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL: return
            file_path = dlg.GetPath()
            try:
                if file_path.endswith('.mat'):
                    data = sio.loadmat(file_path)
                    A = float(data.get('parametros', [[0, 0]])[0][0])
                    B = float(data.get('parametros', [[0, 0]])[0][1])
                elif file_path.endswith('.txt'):
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        A = float(lines[1].strip().strip('[]').split()[0])
                        B = float(lines[1].strip().strip('[]').split()[1])
                else:
                    wx.MessageBox("Formato de archivo no soportado.", "Error", wx.OK | wx.ICON_ERROR)
                    return
            except Exception as e:
                wx.MessageBox(f"Error leyendo los parámetros:\n{e}", "Error", wx.OK | wx.ICON_ERROR)
                return
        with wx.FileDialog(self, "Seleccionar archivo DICOM", wildcard="Archivos DICOM (*.dcm)|*.dcm",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL: return
            dcm_path = dlg.GetPath()
        try:
            ds = dcm.dcmread(dcm_path)
            self.dicom = ds
            img = ds.pixel_array
            max_value = Conversion_exponencial(4095, B, A)
            convertion_factor = 4095 / max_value
            linear_img = Conversion_exponencial(img, B, A) * convertion_factor
            self.imagen_linear = linear_img

            self.ws_sizer.Clear(True)
            fig = Figure(figsize=(6, 4))
            fig.set_facecolor(COLOR_PANEL)
            axes = fig.subplots(1, 2)
            for ax in axes: ax.set_facecolor(COLOR_PANEL)

            im0 = axes[0].imshow(img, cmap='gray')
            axes[0].set_title('Original DICOM')
            axes[0].axis('off')
            fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)

            self.img_artist_linear = axes[1].imshow(linear_img, cmap='gray')
            axes[1].set_title('DICOM Linearizado')
            axes[1].axis('off')
            fig.colorbar(self.img_artist_linear, ax=axes[1], fraction=0.046, pad=0.04)
            fig.tight_layout()

            self.canvas = FigureCanvas(self.workspace_panel, -1, fig)
            self.ws_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
            self.workspace_panel.Layout()

            toolbar = self.GetToolBar()
            ###Habilita los botones
            toolbar.EnableTool(self.tool_hist.GetId(), True)
            toolbar.EnableTool(self.tool_enhance.GetId(), True)
            toolbar.EnableTool(self.tool_save.GetId(),2 ==2)
        except Exception as e:
            wx.MessageBox(f"No se pudo procesar el DICOM:\n{e}", "Error", wx.OK | wx.ICON_ERROR)
            toolbar = self.GetToolBar()
            toolbar.EnableTool(self.tool_hist.GetId(), False)
            toolbar.EnableTool(self.tool_enhance.GetId(), False)

    def open_fr_window(self, event):
        FRWindow(self)

    def savedicom(self, event):
        if self.imagen_linear is None:
            wx.MessageBox("No hay imagen DICOM linearizada para guardar.", "Error", wx.OK | wx.ICON_ERROR)
            return
        with wx.FileDialog(self, "Guardar DICOM linearizado",
                           wildcard="Archivos DICOM (*.dcm)|*.dcm",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL: return
            out_path = dlg.GetPath()
        try:
            new_ds = self.dicom.copy()
            new_ds.PixelData = self.imagen_linear.astype(np.uint16).tobytes()
            new_ds.Rows, new_ds.Columns = self.imagen_linear.shape
            new_ds.BitsAllocated = 16
            new_ds.BitsStored = 16
            new_ds.HighBit = 15
            new_ds.PixelRepresentation = 0
            new_ds.PixelIntensityRelationship = 'LINEAR'
            new_ds.SOPInstanceUID = dcm.uid.generate_uid()
            new_ds.save_as(out_path)
            wx.MessageBox(f"DICOM guardado exitosamente en:\n{out_path}", "Éxito", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"No se pudo guardar el archivo DICOM:\n{e}", "Error", wx.OK | wx.ICON_ERROR)

    def show_histogram(self, event):
        if self.imagen_linear is None:
            wx.MessageBox("Primero debes linearizar una imagen.", "Error", wx.OK | wx.ICON_ERROR)
            return
        hist_frame = wx.Frame(self, title="Histograma de Imagen Linearizada", size=(500, 400))
        panel = wx.Panel(hist_frame)
        panel.SetBackgroundColour(COLOR_PANEL)
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.hist(self.imagen_linear.ravel(), bins=256, color=COLOR_BUTTON, log=False) # Usar nuevo color de botón
        ax.set_title("Distribución de Intensidad de Píxeles")
        ax.set_xlabel("Valor de Píxel")
        ax.set_ylabel("Frecuencia ")
        ax.grid(True, linestyle='--', alpha=0.6)
        canvas = FigureCanvas(panel, -1, fig)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        hist_frame.Centre()
        hist_frame.Show()

    def enhance_image(self, event):
        if self.imagen_linear is None or self.img_artist_linear is None:
            wx.MessageBox("No hay una imagen linealizada para mejorar.", "Error", wx.OK | wx.ICON_ERROR)
            return
        p2, p98 = np.percentile(self.imagen_linear, (2, 98))
        self.img_artist_linear.set_clim(vmin=p2, vmax=p98)
        self.canvas.draw()
        wx.MessageBox("Contraste de la vista mejorado.\nEste cambio es solo visual y no afectará el archivo guardado.", "Info", wx.OK | wx.ICON_INFORMATION)

###Cargar datos csv
class ManualInputDialog(wx.Dialog):
    def __init__(self, parent, num_rows):
        super().__init__(parent, title="Ingresar Datos Manualmente", size=(350, 450))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # --- Selección de tipo de dato ---
        hbox_type = wx.BoxSizer(wx.HORIZONTAL)
        type_label = wx.StaticText(panel, label="Tipo de dato de entrada:")
        self.data_type_choice = wx.ComboBox(panel, choices=["Exposición (mR)", "Kerma (mGy)"],
                                            style=wx.CB_READONLY)
        self.data_type_choice.SetValue("Exposición (mR)") # Opción por defecto
        hbox_type.Add(type_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        hbox_type.Add(self.data_type_choice, 1, wx.EXPAND)
        vbox.Add(hbox_type, 0, wx.EXPAND | wx.ALL, 10)

        # --- Tabla de datos ---
        self.grid = wx.grid.Grid(panel)
        self.grid.CreateGrid(num_rows, 2)
        self.grid.SetColLabelValue(0, "mAs")
        self.grid.SetColLabelValue(1, "Valor") # Etiqueta genérica
        self.grid.AutoSizeColumns()
        vbox.Add(self.grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # --- Botones ---
        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(panel, wx.ID_OK, "Aceptar")
        cancel_button = wx.Button(panel, wx.ID_CANCEL, "Cancelar")
        hbox_btns.Add(ok_button)
        hbox_btns.Add(cancel_button, flag=wx.LEFT, border=5)
        vbox.Add(hbox_btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        panel.SetSizer(vbox)
        self.Centre()

    def get_data_type(self):
        return self.data_type_choice.GetValue()

    def get_data(self):
        try:
            data = []
            for row in range(self.grid.GetNumberRows()):
                mas_val = float(self.grid.GetCellValue(row, 0))
                val = float(self.grid.GetCellValue(row, 1))
                data.append([mas_val, val])
            return pd.DataFrame(data, columns=["mAs", "Valor"])
        except ValueError:
            wx.MessageBox("Por favor, ingresa solo valores numéricos en la tabla.", "Error de Formato", wx.OK | wx.ICON_ERROR)
            return None


######Funcion de Respuesta######
class FRWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Cálculo de Función de Respuesta", size=(800, 600))
        
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour(COLOR_BACKGROUND)
        vbox = wx.BoxSizer(wx.VERTICAL)

        toolbar_panel = wx.Panel(main_panel)
        toolbar_panel.SetBackgroundColour(COLOR_BUTTON)
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        
        self.btn_dcm = self._create_styled_button(toolbar_panel, "Cargar DICOMs", btn_font)
        self.btn_data = self._create_styled_button(toolbar_panel, "Cargar Datos", btn_font)
        self.btn_calc = self._create_styled_button(toolbar_panel, "Calcular FR", btn_font)
        self.btn_save = self._create_styled_button(toolbar_panel, "Guardar Parámetros", btn_font)

        toolbar_sizer.Add(self.btn_dcm, 1, wx.EXPAND | wx.ALL, 1)
        toolbar_sizer.Add(self.btn_data, 1, wx.EXPAND | wx.ALL, 1)
        toolbar_sizer.Add(self.btn_calc, 1, wx.EXPAND | wx.ALL, 1)
        toolbar_sizer.Add(self.btn_save, 1, wx.EXPAND | wx.ALL, 1)
        
        toolbar_panel.SetSizer(toolbar_sizer)
        vbox.Add(toolbar_panel, 0, wx.EXPAND)

        controls_panel = wx.Panel(main_panel)
        controls_panel.SetBackgroundColour(COLOR_PANEL)
        controls_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.correction_panel = wx.StaticBox(controls_panel, label="Factores de Correccion de l" \
        "a Camara de ionzacion")
        correction_sizer = wx.StaticBoxSizer(self.correction_panel, wx.VERTICAL)
        
        nk_sizer_row = wx.BoxSizer(wx.HORIZONTAL)
        self.chk_nk = wx.CheckBox(self.correction_panel, label="Factor de calibración Nk (mGy/mR)")
        nk_label = wx.StaticText(self.correction_panel, label="Factor Nk:")
        self.txt_nk = wx.TextCtrl(self.correction_panel, value="0.00876")
        nk_sizer_row.Add(self.chk_nk, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        nk_sizer_row.Add(nk_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        nk_sizer_row.Add(self.txt_nk, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        other_sizer_row = wx.BoxSizer(wx.HORIZONTAL)
        self.chk_other = wx.CheckBox(self.correction_panel, label="Factor de corrección por distancia")
        other_label = wx.StaticText(self.correction_panel, label="(d/D)²:")
        self.txt_correccion = wx.TextCtrl(self.correction_panel, value="1.0")
        help_button = wx.Button(self.correction_panel, label="?", size=(25, 25))
        other_sizer_row.Add(self.chk_other, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        other_sizer_row.Add(other_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        other_sizer_row.Add(self.txt_correccion, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        other_sizer_row.Add(help_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        correction_sizer.Add(nk_sizer_row, 0, wx.EXPAND | wx.BOTTOM, 5)
        correction_sizer.Add(other_sizer_row, 0, wx.EXPAND)
        controls_sizer.Add(correction_sizer, 0, wx.EXPAND | wx.ALL, 10)

        hbox_checks = wx.BoxSizer(wx.HORIZONTAL)
        self.chk_mat = wx.CheckBox(controls_panel, label="Guardar como .mat")
        self.chk_txt = wx.CheckBox(controls_panel, label="Guardar como .txt")
        self.chk_mat.SetForegroundColour(COLOR_TEXT_DARK)
        self.chk_txt.SetForegroundColour(COLOR_TEXT_DARK)

        # <--- CAMBIO: Deshabilitar checkboxes de guardado al inicio ---
        self.chk_mat.Enable(False)
        self.chk_txt.Enable(False)
        
        hbox_checks.AddStretchSpacer()
        hbox_checks.Add(self.chk_mat, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        hbox_checks.Add(self.chk_txt, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        hbox_checks.AddStretchSpacer()
        controls_sizer.Add(hbox_checks, 0, wx.EXPAND | wx.ALL, 5)
        
        controls_panel.SetSizer(controls_sizer)
        vbox.Add(controls_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        self.figure = Figure(figsize=(5, 4), facecolor=COLOR_PANEL)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(COLOR_PANEL)
        self.ax.set_title("Función de Respuesta")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.canvas = FigureCanvas(main_panel, -1, self.figure)
        vbox.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 10)
        
        main_panel.SetSizer(vbox)
        
        self.csv_data, self.params = None, None
        self.dicom_files, self.incert, self.R2 = [], None, None
        self.Nk, self.Correcion = None, None
        self.data_input_type = "Exposición (mR)"

        help_button.Bind(wx.EVT_BUTTON, self.ayuda_factores)
        self.btn_dcm.Bind(wx.EVT_BUTTON, self.load_dicoms)
        self.btn_data.Bind(wx.EVT_BUTTON, self.load_data)
        self.btn_calc.Bind(wx.EVT_BUTTON, self.calculate_fr)
        self.btn_save.Bind(wx.EVT_BUTTON, self.save_params)
        
        self._update_button_states()
        self._enable_correction_factors(False)

        self.Centre()
        self.Show()

    def _create_styled_button(self, parent, label, font):
        btn = wx.Button(parent, label=label)
        btn.SetFont(font)
        btn.SetBackgroundColour(COLOR_BUTTON)
        btn.SetForegroundColour("#FFFFFF")
        return btn

    def _update_button_states(self):
        can_load_data = bool(self.dicom_files)
        can_calculate = self.csv_data is not None
        can_save = self.params is not None
        
        self.btn_data.Enable(can_load_data)
        self.btn_calc.Enable(can_calculate)
        self.btn_save.Enable(can_save)
        
        # <--- CAMBIO: Ligar el estado de los checkboxes al del botón de guardar ---
        self.chk_mat.Enable(can_save)
        self.chk_txt.Enable(can_save)


    def _enable_correction_factors(self, enable):
        for child in self.correction_panel.GetChildren():
            child.Enable(enable)
        color = wx.BLACK if enable else wx.Colour(160, 160, 160)
        self.correction_panel.SetForegroundColour(color)
        self.correction_panel.Refresh()

    def ayuda_factores(self, event):
        help_title = "Ayuda en factores de corrección"
        help_mensaje = (
            "Este factor de corrección por distancia se utiliza cuando la C.I. no está colocada sobre la superficie del detector.\n\n"
            "Se calcula como (d/D)².\n\n"
            "Donde d = distancia de la cámara al detector.\n"
            "y D = distancia del tubo de RX a la cámara."
        )
        wx.MessageBox(help_mensaje, help_title, wx.OK | wx.ICON_INFORMATION)

    def load_dicoms(self, event):
        with wx.FileDialog(self, "Seleccionar archivos DICOM", wildcard="DICOM (*.dcm)|*.dcm",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL: return
            self.dicom_files = dlg.GetPaths()
            wx.MessageBox(f"{len(self.dicom_files)} archivos DICOM cargados.", "Info", wx.OK | wx.ICON_INFORMATION)
            self.csv_data, self.params = None, None
            self._update_button_states()

    def load_data(self, event):
        choices = ["Cargar desde archivo CSV", "Ingresar datos manualmente"]
        dlg = wx.SingleChoiceDialog(self, "Elige un método para cargar los datos de exposición:", "Cargar Datos", choices)
        if dlg.ShowModal() == wx.ID_OK:
            choice = dlg.GetStringSelection()
            if choice == "Cargar desde archivo CSV":
                self.data_input_type = "Exposición (mR)"
                self._enable_correction_factors(True)
                with wx.FileDialog(self, "Abrir archivo CSV", wildcard="CSV (*.csv)|*.csv",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dlg:
                    if file_dlg.ShowModal() == wx.ID_CANCEL: return
                    self.csv_data = pd.read_csv(file_dlg.GetPath())
                    wx.MessageBox("Archivo CSV cargado exitosamente.", "Info", wx.OK | wx.ICON_INFORMATION)
            elif choice == "Ingresar datos manualmente":
                manual_dlg = ManualInputDialog(self, num_rows=len(self.dicom_files))
                if manual_dlg.ShowModal() == wx.ID_OK:
                    self.data_input_type = manual_dlg.get_data_type()
                    data = manual_dlg.get_data()
                    if data is not None:
                        self.csv_data = data
                        self._enable_correction_factors(self.data_input_type == "Exposición (mR)")
                manual_dlg.Destroy()
            self._update_button_states()
        dlg.Destroy()

    def calculate_fr(self, event):
        if self.csv_data is None or not self.dicom_files:
            wx.MessageBox("Faltan datos para el cálculo.", "Error", wx.OK | wx.ICON_ERROR)
            return
        if len(self.csv_data.index) != len(self.dicom_files):
            wx.MessageBox(f"El número de entradas de datos ({len(self.csv_data.index)}) no coincide con el número de archivos DICOM ({len(self.dicom_files)}).",
                          "Error de Concordancia", wx.OK | wx.ICON_ERROR)
            return
        try:
            input_values = np.array(self.csv_data.iloc[:, 1].astype(float))
            if self.data_input_type == "Exposición (mR)":
                if self.chk_nk.GetValue():
                    try:
                        self.Nk = float(self.txt_nk.GetValue())
                        if self.Nk <= 0: raise ValueError
                    except ValueError:
                        wx.MessageBox("Introduce un valor numérico positivo válido para Nk.", "Error", wx.OK | wx.ICON_ERROR)
                        return
                else: self.Nk = 0.00876
                if self.chk_other.GetValue():
                    try:
                        self.Correcion = float(self.txt_correccion.GetValue())
                        if self.Correcion <= 0: raise ValueError
                    except ValueError:
                        wx.MessageBox("Introduce un valor de corrección válido.")
                        return
                else: self.Correcion = 1.0
                kerma_values = input_values * self.Nk * self.Correcion
            else:
                kerma_values = input_values

            def get_mas(file):
                return float(getattr(dcm.dcmread(file), "Exposure", 0))
            self.dicom_files.sort(key=get_mas)
            
            MPV, sd = [], []
            for file in self.dicom_files:
                pixel_array = dcm.dcmread(file).pixel_array
                x, y = pixel_array.shape[0] // 2, pixel_array.shape[1] // 2
                mean, dsv = ROI_calculadora(pixel_array, x, y, l=100)
                MPV.append(mean)
                sd.append(dsv)
            MPV, sd = np.array(MPV), np.array(sd)
            
            ln_ESAK = np.log(kerma_values)
            sd_ESAK = abs(ln_ESAK * 0.05)
            
            param, incert, R2 = ODR_adjust(ln_ESAK, MPV, sd_ESAK, sd)
            self.params, self.incert, self.R2 = param, incert, R2
            
            self.ax.clear()
            self.ax.errorbar(ln_ESAK, MPV, xerr=sd_ESAK, yerr=sd, fmt='o', label='Datos experimentales', color='crimson', ecolor='lightcoral', capsize=5)
            x_fit = np.linspace(ln_ESAK.min(), ln_ESAK.max(), 100)
            y_fit = param[0] * x_fit + param[1]
            self.ax.plot(x_fit, y_fit, color='royalblue', linestyle='--', label=f'Ajuste lineal (R²={R2:.4f})')
            self.ax.set_xlabel("ln(ESAK) [mGy]")
            self.ax.set_ylabel("Valor Medio del Píxel (MPV)")
            self.ax.set_title("Función de Respuesta del Detector")
            self.ax.grid(True, linestyle='--', alpha=0.6)
            self.ax.legend()
            self.canvas.draw()
            
            wx.MessageBox(f"Cálculo de FR completado.\n\nParámetros:\nA = {self.params[0]:.4f}\nB = {self.params[1]:.4f}\nR² = {self.R2:.4f}", "Éxito", wx.OK | wx.ICON_INFORMATION)
            self._update_button_states()
        except Exception as e:
            wx.MessageBox(f"Ocurrió un error en el cálculo de la FR:\n{e}", "Error", wx.OK | wx.ICON_ERROR)
            self.params = None
            self._update_button_states()

    def save_params(self, event):
        if self.params is None:
            wx.MessageBox("No hay parámetros para guardar.", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not self.chk_mat.GetValue() and not self.chk_txt.GetValue():
            wx.MessageBox("Por favor, selecciona al menos un formato para guardar.", "Error", wx.OK | wx.ICON_ERROR)
            return
        try:
            if self.chk_mat.GetValue():
                with wx.FileDialog(self, "Guardar parámetros como .mat", wildcard="Archivo MAT (*.mat)|*.mat", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
                    if dlg.ShowModal() == wx.ID_OK:
                        sio.savemat(dlg.GetPath(), {"parametros": self.params, "incertidumbre": self.incert, "R2": self.R2})
            if self.chk_txt.GetValue():
                with wx.FileDialog(self, "Guardar parámetros como .txt", wildcard="Archivo de Texto (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
                    if dlg.ShowModal() == wx.ID_OK:
                        with open(dlg.GetPath(), "w") as f:
                            f.write(f"Parámetros (A, B):\n{self.params}\n\n")
                            f.write(f"Incertidumbre:\n{self.incert}\n\n")
                            f.write(f"Coeficiente de determinación (R2):\n{self.R2:.4f}\n")
            wx.MessageBox("Parámetros guardados correctamente.", "Éxito", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"No se pudieron guardar los parámetros:\n{e}", "Error", wx.OK | wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App(False)
    frame = RespLinApp()
    app.MainLoop()


#          ,
#        \`-._           __
#         \\  `-..____,.'  `.
#          :`.         /    \`.
#          :  )       :      : \
#           ;'        '   ;  |  :
#           )..      .. .:.`.;  :
#          /::...  .:::...   ` ;
#          ; _ '    __        /:\
#          `:o>   /\o_>      ;:. `.
#         `-`.__ ;   __..--- /:.   \
#         === \_/   ;=====_.':.     ;
#          ,/'`--'...`--....        ;
#               ;                    ;
#             .'                      ;
#           .'                        ;
#         .'     ..     ,      .       ;
#        :       ::..  /      ;::.     |
#       /      `.;::.  |       ;:..    ;
#      :         |:.   :       ;:.    ;
#      :         ::     ;:..   |.    ;
#       :       :;      :::....|     |
#       /\     ,/ \      ;:::::;     ;
#     .:. \:..|    :     ; '.--|     ;
#    ::.  :''  `-.,,;     ;'   ;     ;
# .-'. _.'\      / `;      \,__:      \
# `---'    `----'   ;      /    \,.,,,/
#                    `----`            
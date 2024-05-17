import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
import io
import os

def centrar_ventana(ventana):
    ventana.update_idletasks()
    ancho_ventana = ventana.winfo_width()
    alto_ventana = ventana.winfo_height()
    x_ventana = (ventana.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_ventana = (ventana.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana.geometry('{}x{}+{}+{}'.format(ancho_ventana, alto_ventana, x_ventana, y_ventana))

# ---------------------------------------------------------->Solicitar Imagen<----------------------------------------------------------------- 
def cargar_imagen():
    global ruta_imagen,imagen,imagen_original
    ruta_imagen = filedialog.askopenfilename(title="Seleccione una imagen", filetypes=tipos_de_archivos)  # Selecciona la imagen desde el sistema de archivos
    if ruta_imagen:
        # Enviar solicitud al servidor para cargar la imagen
        payload = {"action": "load", "imagePath": ruta_imagen}
        response = requests.post("http://localhost:8080/upload", data=payload)
        if response.status_code == 200:
            imagen_bytes = io.BytesIO(response.content)
            imagen = Image.open(imagen_bytes)
            imagen_original= imagen
        else:
            print("Error al cargar la imagen desde el servidor")
            return
        imagen_tk = ImageTk.PhotoImage(imagen)
        panel_imagen.configure(image=imagen_tk)
        panel_imagen.image = imagen_tk
        # Ajustar tamaño de la ventana al de la imagen
        ventana.update_idletasks()  # Actualizar geometría de la ventana antes de obtener sus dimensiones
        ventana.geometry('{}x{}'.format(ventana.winfo_reqwidth(), ventana.winfo_reqheight()))  # Ajustar ventana al tamaño de la imagen
        centrar_ventana(ventana)
    else:
        print("La ruta de la imagen no es válida")

# ---------------------------------------------------------->Redimensionar la Imagen<-----------------------------------------------------------------
def actualizar_imagen(event):
    global imagen
    if ruta_imagen:
        if tamano_variable.get() == "Máximo":
            # Enviar solicitud al servidor para redimensionar la imagen
            payload = {"action": "resize", "imagePath": ruta_imagen, "width": 800, "height": 720}
            response = requests.post("http://localhost:8080/upload", data=payload)
            if response.status_code == 200:
                imagen_bytes = io.BytesIO(response.content)
                imagen = Image.open(imagen_bytes)
            else:
                print("Error al redimensionar la imagen desde el servidor")
                return
        elif tamano_variable.get() == "Mínimo":
            # Enviar solicitud al servidor para redimensionar la imagen
            payload = {"action": "resize", "imagePath": ruta_imagen, "width": 400, "height": 420}
            response = requests.post("http://localhost:8080/upload", data=payload)
            if response.status_code == 200:
                imagen_bytes = io.BytesIO(response.content)
                imagen = Image.open(imagen_bytes)
            else:
                print("Error al redimensionar la imagen desde el servidor")
                return
        else:
            # Mostrar la imagen original
            imagen = imagen_original

        # Convertir la imagen a formato Tkinter
        imagen_tk = ImageTk.PhotoImage(imagen)
        panel_imagen.configure(image=imagen_tk)
        panel_imagen.image = imagen_tk
        # Ajustar tamaño de la ventana al de la imagen
        ventana.update_idletasks()  # Actualizar geometría de la ventana antes de obtener sus dimensiones
        ventana.geometry('{}x{}'.format(ventana.winfo_reqwidth(), ventana.winfo_reqheight()))  # Ajustar ventana al tamaño de la imagen
        centrar_ventana(ventana)
    else:
        print("Por favor, carga una imagen antes de ajustar el tamaño.")

# ---------------------------------------------------------->Editar la Imagen<-----------------------------------------------------------------
def Editar_Seleccion():
    global ventana, imagen,ventana_edicion,texto_entrada,fuente_seleccionada,posicion_texto_seleccionada,imagenAntesEditar,ventana_destruida,entrada_texto_extra
    if ruta_imagen:
        # Cerrar la ventana principal
        if not ventana_destruida:  
            imagenAntesEditar = imagen  # Guardar una copia en caso de rehacer lo editado
            ventana.destroy()
            ventana_destruida=True 
        # Crear la ventana de edicion
        ventana_edicion = tk.Tk()
        ventana_edicion.title("Imagen seleccionada")
        ventana_edicion.resizable(False,False)
        #Frame Principal
        FramePrincipal_E = tk.Frame(ventana_edicion)
        FramePrincipal_E.pack(expand=True, fill="both")
        # Panel para mostrar la imagen
        panel_imagen_Editar = tk.Label(FramePrincipal_E)
        panel_imagen_Editar.pack(expand=True, fill="both", padx=10, pady=10)
        #Mostrar imagen
        imagen_tk = ImageTk.PhotoImage(imagen)
        panel_imagen_Editar.configure(image=imagen_tk)
        panel_imagen_Editar.image = imagen_tk
        
        #Campo de entrada de texto
        texto_entrada = tk.Entry(FramePrincipal_E)
        texto_entrada.pack(side="top",pady=10)
         # Campo de entrada de texto adicional (caso de escribir en ambos lugares arriba y abajo)
        entrada_texto_extra = tk.Entry(FramePrincipal_E)
        entrada_texto_extra.pack(side="top",padx=25, pady=10)
        # Lista de opciones para la fuente de texto
        opciones_fuentes = ["openSans", "Oswald", "BriemHand"]
        fuente_seleccionada = tk.StringVar(FramePrincipal_E)
        fuente_seleccionada.set(opciones_fuentes[0])  # Establecer la opción por defecto

        # OptionMenu para seleccionar la fuente de texto
        menu_fuentes = tk.OptionMenu(FramePrincipal_E, fuente_seleccionada, *opciones_fuentes)
        menu_fuentes.pack(side="left", pady=10)
        
        # Lista de opciones para la posición del texto
        opciones_posicion_texto = ["superior", "inferior","ambos"]
        posicion_texto_seleccionada = tk.StringVar(FramePrincipal_E)
        posicion_texto_seleccionada.set(opciones_posicion_texto[0])  # Establecer la opción por defecto

        # OptionMenu para seleccionar la posición del texto
        menu_posicion_texto = tk.OptionMenu(FramePrincipal_E, posicion_texto_seleccionada, *opciones_posicion_texto,command=mostrar_entrada_extra)
        menu_posicion_texto.pack(side="left", padx=10, pady=10)
        
         # Botón para Aplicar el texto en la imagen
        boton_guardar = tk.Button(FramePrincipal_E, text="Aplicar Cambios", command=Editar_Imagen)
        boton_guardar.pack(side="left", padx=20, pady=10)
        
        ventana_edicion.update_idletasks()  # Actualizar geometría de la ventana antes de obtener sus dimensiones
        ventana_edicion.geometry('{}x{}'.format(ventana_edicion.winfo_reqwidth(), ventana_edicion.winfo_reqheight()))  # Ajustar ventana al tamaño de la imagen
        entrada_texto_extra.config(state="disabled")  # Se inicializa deshabilitado
        centrar_ventana(ventana_edicion)
    else:
        print("Por favor, carga una imagen antes de confirmar.")

# -------------------------------------------------------->Habililtar la entrada de texto adicional<---------------------------------------------------------------
def mostrar_entrada_extra(opcion_seleccionada):
    global entrada_texto_extra
    if opcion_seleccionada == "ambos":
        entrada_texto_extra.config(state="normal")  # Habilitar la entrada de texto
    else:
        entrada_texto_extra.delete(0, "end")  # Limpiar el texto en la entrada extra
        entrada_texto_extra.config(state="disabled")  # Deshabilitar la entrada de texto

def obtener_formato(ruta_imagen):
     _, extension = os.path.splitext(ruta_imagen)
     extension = extension.lower()  # Convertimos a minúsculas para la comparación
     formato = ''
     if extension in (".jpg", ".jpeg"):
            formato= 'jpeg'
     elif extension == ".png":
            formato= 'png'
     elif extension == ".bmp":
            formato= 'bmp'
     elif extension == ".tiff":
            formato= 'tiff'
     return formato

# -------------------------------------------------------->Enviar la informacion a editar a Go<---------------------------------------------------------------
def Editar_Imagen():
    global imagen, ruta_imagen,posicion_texto_seleccionada,ventana_PreviaImagen,ventana_Previa_Estado
    textoAgregar= texto_entrada.get()
    textoAgregar_EntradaDoble = entrada_texto_extra.get()
    formatoLetra= fuente_seleccionada.get()
    ubicarTexto= posicion_texto_seleccionada.get()
    formatoImagen=obtener_formato(ruta_imagen)
    if not textoAgregar and not textoAgregar_EntradaDoble : return Confirmar_Imagen()  # Caso base de que no haya querido agregar texto se pasa a la siguiente ventana
    #Caso base de si uno es vacio para que no de problemas
    if textoAgregar== "": textoAgregar=" "
    if textoAgregar_EntradaDoble== "": textoAgregar_EntradaDoble=" "
    buffer = io.BytesIO()
    imagen.save(buffer, format=formatoImagen)  # Guarda la imagen en el buffer
    imagen_bytes = buffer.getvalue()           # Obtiene los bytes de la imagen
    # Hacer la solicitud HTTP con la imagen en bytes
    files = {"imagen": imagen_bytes}
    payload = {"action": "edit","text1":textoAgregar ,"text2":textoAgregar_EntradaDoble,  "formato":formatoImagen,"ubicacion":ubicarTexto,"font":formatoLetra}
    response = requests.post("http://localhost:8080/upload",files=files, data=payload)
    if response.status_code == 200:
        imagen_bytes = io.BytesIO(response.content)
        imagen = Image.open(imagen_bytes)    
        texto_entrada.delete(0,"end")
        ventana_edicion.destroy()
        ventana_PreviaImagen = tk.Tk()
        ventana_PreviaImagen.title("Imagen previa a guardar")
        ventana_PreviaImagen.resizable(False,False)
        panel_imagen_editada = tk.Label(ventana_PreviaImagen)
        panel_imagen_editada.pack(expand=True, fill="both", padx=10, pady=10)
        ventana_Previa_Estado= True        # Estado para verificar que se haya creado la ventana Previa de la Imagen
        # Mostrar la imagen editada
        imagen_tk = ImageTk.PhotoImage(imagen)
        panel_imagen_editada.configure(image=imagen_tk)
        panel_imagen_editada.image = imagen_tk

        # Botón para rehacer la edición
        boton_rehacer = tk.Button(ventana_PreviaImagen, text="Rehacer", command=rehacer_edicion)
        boton_rehacer.pack(side="left", padx=20, pady=10)
        
         # Botón para guardar la imagen editada
        boton_guardar = tk.Button(ventana_PreviaImagen, text="Guardar", command=Confirmar_Imagen)
        boton_guardar.pack(side="left", padx=20, pady=10)
        
        ventana_PreviaImagen.update_idletasks()  # Actualizar geometría de la ventana antes de obtener sus dimensiones
        ventana_PreviaImagen.geometry('{}x{}'.format(ventana_PreviaImagen.winfo_reqwidth(), ventana_PreviaImagen.winfo_reqheight()))  # Ajustar ventana al tamaño de la imagen
        centrar_ventana(ventana_PreviaImagen)
    else:
        print("Error al editar la imagen desde el servidor: ")
        return
    
# ---------------------------------------------------------->Rehacer la Imagen y volver a Editar<-----------------------------------------------------------------
def rehacer_edicion():
    global imagen, ventana_PreviaImagen, imagenAntesEditar, ventana_Previa_Estado
    imagen = imagenAntesEditar     # Retomar la imagen antes de la edicion
    ventana_PreviaImagen.destroy()
    ventana_Previa_Estado= False   # Estado para verificar que se ha tenido que quitar la ventana Previa de la Imagen
    Editar_Seleccion()

# ---------------------------------------------------------->Ventana para guardar la imagen<-----------------------------------------------------------------
def Confirmar_Imagen():
    global nombre_archivo_entry, formato_variable, nombre_correo_entry,ventana_Previa_Estado,imagen
    if ventana_Previa_Estado == True:  # Estado para verificar que se haya creado la ventana Previa de la Imagen
        ventana_PreviaImagen.destroy()       
    elif ventana_Previa_Estado == False: ventana_edicion.destroy()  # Si está en False entonces quitar la de edicion
    # Crear la ventana de confirmacion donde se va a guardar la imagen
    ventana_Confirmacion = tk.Tk()  # Crear una nueva ventana
    ventana_Confirmacion.title("Imagen a Guardar")
    ventana_Confirmacion.resizable(False,False)
    
    FramePrincipal_C = tk.Frame(ventana_Confirmacion)
    FramePrincipal_C.pack(expand=True, fill="both")
    
    # Crear un marco para el campo de entrada y el botón
    FrameBotones_C= tk.Frame(ventana_Confirmacion)
    FrameBotones_C.pack(side="top", padx=10, pady=10, fill="x")
    # Espacio de texto para ingresar el nombre del archivo
    nombre_archivo_label = tk.Label(FrameBotones_C, text="Nombre del archivo:")
    nombre_archivo_label.pack(pady=(10,0))
    nombre_archivo_entry = tk.Entry(FrameBotones_C)
    nombre_archivo_entry.pack(pady=(0,10))
    # Opciones de formato
    opciones_formato = ["jpeg", "png","tiff","bmp"]
    formato_variable = tk.StringVar(ventana_Confirmacion)
    formato_variable.set(opciones_formato[0])  # Configurar opción por defecto
    formato_label = tk.Label(FrameBotones_C, text="Formato:")
    formato_label.pack(pady=(10,0))
    menu_formato = tk.OptionMenu(FrameBotones_C, formato_variable, *opciones_formato)
    menu_formato.pack(pady=(0,10))
    
    # Botón para guardar la imagen local
    boton_guardar_local = tk.Button(FrameBotones_C, text="Guardar Local", command=guardar_imagen_Local)
    boton_guardar_local.pack(side="left",padx=5,pady=5)
    # Botón para guardar la imagen por correo
    boton_guardar_Correo = tk.Button(FrameBotones_C, text="Enviar al correo", command=enviarImagen_Correo)
    boton_guardar_Correo.pack(side="left",padx=5,pady=5)
    
    nombre_Correo_label = tk.Label(FrameBotones_C, text="Correo:")
    nombre_Correo_label.pack(side="left",padx=5,pady=5)
    nombre_correo_entry = tk.Entry(FrameBotones_C)
    nombre_correo_entry.pack(side="left",padx=5,pady=5)
    
    # Panel para mostrar la imagen
    panel_imagen_Confirmada = tk.Label(FramePrincipal_C)
    panel_imagen_Confirmada.pack(expand=True, fill="both", padx=10, pady=10)
    
    imagen_tk = ImageTk.PhotoImage(imagen)
    panel_imagen_Confirmada.configure(image=imagen_tk)
    panel_imagen_Confirmada.image = imagen_tk
    ventana_Confirmacion.update_idletasks()  # Actualizar geometría de la ventana antes de obtener sus dimensiones
    ventana_Confirmacion.geometry('{}x{}'.format(ventana_Confirmacion.winfo_reqwidth(), ventana_Confirmacion.winfo_reqheight()))  # Ajustar ventana al tamaño de la imagen
    centrar_ventana(ventana_Confirmacion)
  
 # ---------------------------------------------------------->Guardar la imagen de manera local<-----------------------------------------------------------------  
def guardar_imagen_Local():
    formato = formato_variable.get()
    nombre_archivo = nombre_archivo_entry.get()
    if nombre_archivo == "":
        print("Por favor, ingresa un nombre para el archivo.")
        return
    nombre_archivo_entry.delete(0,"end")
    ruta_guardar = "edited/{}.{}".format(nombre_archivo,formato) 
    buffer = io.BytesIO()
    imagen.save(buffer, format=formato)  # Guarda la imagen en el buffer
    imagen_bytes = buffer.getvalue()    # Obtiene los bytes de la imagen
    # Hacer la solicitud HTTP con la imagen en bytes
    files = {"imagen": imagen_bytes}
    payload = {"action": "save","rutaGuardar":ruta_guardar}
    response = requests.post("http://localhost:8080/upload",files=files, data=payload)
    if response.status_code == 200:
        print("Imagen guardada exitosamente como", nombre_archivo+"."+formato)
    else:
        print("Error al guardar la imagen:", response.text)
 
 # ---------------------------------------------------------->Guardar la imagen por correo<-----------------------------------------------------------------
def enviarImagen_Correo():
    if nombre_correo_entry.get() != "":
        nombre_archivo = nombre_archivo_entry.get()
        if nombre_archivo == "":
            print("Por favor, ingresa un nombre para el archivo.")
            return
        correo= nombre_correo_entry.get()
        formato = formato_variable.get()
        nombre_archivo = nombre_archivo_entry.get()
        nombreImagen= "{}.{}".format(nombre_archivo,formato)
        nombre_correo_entry.delete(0,"end")    # borrar los campos de entrada una vez se hace la solicitud
        nombre_archivo_entry.delete(0,"end")
        
        buffer = io.BytesIO()
        imagen.save(buffer, format=formato)  # Guarda la imagen en el buffer en formato JPEG
        imagen_bytes = buffer.getvalue()    # Obtiene los bytes de la imagen
        # Hacer la solicitud HTTP con la imagen en bytes
        files = {"imagen": imagen_bytes}
        payload = {"action": "correo","nombreImagen":nombreImagen,"direccionCorreo":correo}
        response = requests.post("http://localhost:8080/upload",files=files, data=payload)
        if response.status_code == 200:
            print("Imagen enviada exitosamente al correo:", correo)
        else:
            print("Error al enviar la imagen:", response.text)
        
    else:
        print("Por favor ingresa un correo. ")
        return
    
if __name__=='__main__':
    # los tipos de archivos que se pueden seleccionar 
    tipos_de_archivos = [("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")]  # formato de las imagenes de entrada
    ruta_imagen= None
    ventana_destruida= False        # Manejar el estado de si se va a rehacer la imagen para guardar una copia de la imagen
    ventana_Previa_Estado = False   # Manejar el estado de la ventana Previa de la imagen
    
    # Crear la ventana principal
    ventana = tk.Tk()
    ventana.title("Cargar imagen")
    ventana.resizable(False,False)
    FramePrincipal = tk.Frame(ventana)
    FramePrincipal.pack(expand=True, fill="both")
    # Crear un marco para el campo de entrada y el botón
    FrameBotones= tk.Frame(ventana)
    FrameBotones.pack(side="top", padx=10, pady=10, fill="x")

    # Botón para cargar la imagen
    boton_cargar = tk.Button(FrameBotones, text="Cargar imagen", command=cargar_imagen)
    boton_cargar.pack(side="left", padx=5, pady=5)
    # Opciones de tamaño
    opciones_tamano = ["Original", "Máximo", "Mínimo"]
    tamano_variable = tk.StringVar(ventana)
    tamano_variable.set(opciones_tamano[0])  # Configurar opción por defecto

    # Menú desplegable para elegir el tamaño
    menu_tamano = tk.OptionMenu(FrameBotones, tamano_variable, *opciones_tamano, command=actualizar_imagen)
    menu_tamano.pack(side="left", padx=5, pady=5)

    # Botón para confirmar selección
    boton_confirmar = tk.Button(FrameBotones, text="Confirmar", command=Editar_Seleccion)
    boton_confirmar.pack(side="left", padx=5, pady=5)

    # Panel para mostrar la imagen
    panel_imagen = tk.Label(FramePrincipal)
    panel_imagen.pack(expand=True, fill="both", padx=10, pady=10)

    centrar_ventana(ventana)
    ventana.mainloop()
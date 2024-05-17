package main

import (
	"bytes"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/disintegration/imaging"
	"github.com/golang/freetype"
	"github.com/golang/freetype/truetype"
	"golang.org/x/image/math/fixed"
	"gopkg.in/gomail.v2"
)

func cargarImagen(imgPath string) (image.Image, error) {
	// Carga la imagen desde la ruta proporcionada
	imagen, err := imaging.Open(imgPath)
	if err != nil {
		return nil, fmt.Errorf("error al abrir la imagen: %v", err)
	}

	// Obtener dimensiones actuales de la imagen
	width := imagen.Bounds().Dx()
	height := imagen.Bounds().Dy()
	// Verificar si la imagen está dentro de los límites
	if width <= 800 && height <= 720 && width >= 400 && height >= 420 {
		// La imagen ya está dentro de los límites, no se necesita ajuste
		return imagen, nil
	}
	// Calcular las nuevas dimensiones para ajustar la imagen
	newWidth := width
	newHeight := height

	if width > 800 || height > 720 {
		// La imagen es demasiado grande, ajustar al tamaño máximo permitido
		if width > 800 {
			newWidth = 800
		}
		if height > 720 {
			newHeight = 720
		}
	} else {
		// La imagen es demasiado pequeña, ajustar al tamaño mínimo permitido
		if width < 400 {
			newWidth = 400
		}
		if height < 420 {
			newHeight = 420
		}
	}

	// Redimensionar la imagen a las nuevas dimensiones
	resized := imaging.Resize(imagen, newWidth, newHeight, imaging.Lanczos)
	return resized, nil
}

func redimensionarImagen(img image.Image, width, height int) (image.Image, error) {
	// Redimensiona la imagen
	resized := imaging.Resize(img, width, height, imaging.Lanczos)

	return resized, nil
}

func editarImagen(img image.Image, text string, text2 string, fontName string, ubicacion string) (image.Image, error) {
	// Convierte la imagen a RGBA para permitir la operación Paste
	rgbaImg := image.NewRGBA(img.Bounds())
	draw.Draw(rgbaImg, rgbaImg.Bounds(), img, image.Point{}, draw.Src)
	var fontData []byte
	var fontPath string
	switch fontName {
	case "BriemHand":
		fontPath = "FuentesLetras/BriemHand/BriemHand-VariableFont_wght.ttf"
	case "openSans":
		fontPath = "FuentesLetras/OpenSans/OpenSans-VariableFont_wdth,wght.ttf"
	case "Oswald":
		fontPath = "FuentesLetras/Oswald/Oswald-VariableFont_wght.ttf"
	default:
		return nil, fmt.Errorf("tipo de letra no válido: %s", fontName)
	}
	// Cargar el archivo de fuente
	fontData, err := ioutil.ReadFile(fontPath)
	if err != nil {
		return nil, fmt.Errorf("error al cargar el tipo de letra: %v", err)
	}
	// Analizar la fuente TrueType
	font, err := truetype.Parse(fontData)
	if err != nil {
		return nil, fmt.Errorf("error al analizar la fuente TrueType: %v", err)
	}
	// Tamaño de fuente predeterminado
	fontSize := 24
	// Crear el contexto de dibujo
	drawContext := freetype.NewContext()
	drawContext.SetDst(rgbaImg)
	drawContext.SetClip(rgbaImg.Bounds())
	drawContext.SetSrc(image.NewUniform(color.Black))
	drawContext.SetFont(font)
	drawContext.SetFontSize(float64(fontSize)) // Tamaño de fuente predeterminado
	// Estimar el ancho total del texto1
	var text1Width fixed.Int26_6
	for _, char := range text {
		// Obtener la métrica de avance del carácter
		advanceWidth := font.HMetric(0, font.Index(char)).AdvanceWidth
		// Multiplicar por la escala adecuada
		awidth := drawContext.PointToFixed(float64(fontSize)).Mul(advanceWidth)
		text1Width += awidth
	}
	// Calcular el espacio adicional entre letras para texto1
	spacing := drawContext.PointToFixed(float64(fontSize) * 0.5) // Espacio entre letras
	spacing *= fixed.Int26_6(len(text) - 1)
	// Estimar el ancho total del texto2
	var text2Width fixed.Int26_6
	for _, char := range text2 {
		// Obtener la métrica de avance del carácter
		advanceWidth := font.HMetric(0, font.Index(char)).AdvanceWidth
		// Multiplicar por la escala adecuada
		awidth := drawContext.PointToFixed(float64(fontSize)).Mul(advanceWidth)
		text2Width += awidth
	}
	// Calcular el espacio adicional entre letras para texto2
	spacing2 := drawContext.PointToFixed(float64(fontSize) * 0.5) // Espacio entre letras
	spacing2 *= fixed.Int26_6(len(text2) - 1)
	// Obtener el ancho de la imagen
	imgWidth := rgbaImg.Bounds().Dx()
	// Calcular la posición x para centrar el texto1
	x := (imgWidth - (int(text1Width>>6) + int(spacing>>6))) / 2
	// Calcular la posición x para centrar el texto2
	x2 := (imgWidth - (int(text2Width>>6) + int(spacing2>>6))) / 2

	// Calcular la posición y basada en la ubicación deseada
	var ys []int
	switch ubicacion {
	case "superior":
		ys = append(ys, rgbaImg.Bounds().Dy()/8)
	case "inferior":
		ys = append(ys, (7*rgbaImg.Bounds().Dy())/8)
	case "ambos":
		ys = append(ys, rgbaImg.Bounds().Dy()/8)
		ys = append(ys, (7*rgbaImg.Bounds().Dy())/8)
	default:
		return nil, fmt.Errorf("ubicación no válida: %s", ubicacion)
	}
	// Agrega el texto1 y texto2 a la imagen
	for i, y := range ys {
		pt := freetype.Pt(x, y)
		pt2 := freetype.Pt(x2, y) // Espacio entre texto1 y texto2
		if i == 0 {
			_, err = drawContext.DrawString(text, pt)
			if err != nil {
				return nil, fmt.Errorf("error al agregar texto a la imagen: %v", err)
			}
		} else {
			_, err = drawContext.DrawString(text2, pt2)
			if err != nil {
				return nil, fmt.Errorf("error al agregar texto a la imagen: %v", err)
			}
		}
	}

	return rgbaImg, nil
}

func enviarCorreo(nombreArch string, destino string, imagenBytes []byte) error {
	/// Datos de autenticación
	user := " "
	password := " "
	// Configuración del servidor SMTP de Gmail
	smtpHost := "smtp.gmail.com"
	smtpPort := 587
	msg := gomail.NewMessage()
	msg.SetHeader("From", user)
	msg.SetHeader("To", destino)
	msg.SetHeader("Subject", "Imagen editada.")
	// Adjunta la imagen al mensaje con el tipo MIME genérico para imágenes
	msg.Attach(nombreArch, gomail.SetCopyFunc(func(w io.Writer) error {
		_, err := w.Write(imagenBytes)
		return err
	}), gomail.SetHeader(map[string][]string{
		"Content-Type": {"image/*"},
	}))

	dialer := gomail.NewDialer(smtpHost, smtpPort, user, password)
	if err := dialer.DialAndSend(msg); err != nil {
		return fmt.Errorf("error al enviar el correo electrónico: %v", err)

	}
	return nil
}
func handleImageUpload(w http.ResponseWriter, r *http.Request) {
	// Procesa la solicitud para cargar y redimensionar la imagen
	if r.Method != http.MethodPost {
		http.Error(w, "Método no permitido", http.StatusMethodNotAllowed)
		return
	}

	action := r.FormValue("action")
	switch action {
	case "load":
		CargarImagenSolicitada(w, r)
	case "resize":
		redimensionarImagenSolicitada(w, r)
	case "edit":
		editarImagenSolicitada(w, r)
	case "save":
		guardarImagenSolicitada(w, r)
	case "correo":
		guardarImagenCorreo(w, r)
	default:
		http.Error(w, "Acción no válida", http.StatusBadRequest)
		return
	}
}
func CargarImagenSolicitada(w http.ResponseWriter, r *http.Request) {
	// Obtiene los parámetros de la solicitud
	imgPath := r.FormValue("imagePath")

	// Carga la imagen
	img, err := cargarImagen(imgPath)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al cargar la imagen: %v", err), http.StatusInternalServerError)
		return
	}

	// Escribe los bytes de la imagen en la respuesta HTTP
	err = imaging.Encode(w, img, imaging.JPEG)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al escribir la imagen en la respuesta: %v", err), http.StatusInternalServerError)
		return
	}
}
func redimensionarImagenSolicitada(w http.ResponseWriter, r *http.Request) {
	// Obtiene los parámetros de la solicitud
	imgPath := r.FormValue("imagePath")
	width := parseInt(r.FormValue("width"))
	height := parseInt(r.FormValue("height"))

	// Carga la imagen
	img, err := cargarImagen(imgPath)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al cargar la imagen: %v", err), http.StatusInternalServerError)
		return
	}

	// Redimensiona la imagen
	resizedImage, err := redimensionarImagen(img, width, height)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al redimensionar la imagen: %v", err), http.StatusInternalServerError)
		return
	}

	// Escribe los bytes de la imagen redimensionada en la respuesta HTTP
	err = imaging.Encode(w, resizedImage, imaging.JPEG)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al escribir la imagen redimensionada en la respuesta: %v", err), http.StatusInternalServerError)
		return
	}
}
func editarImagenSolicitada(w http.ResponseWriter, r *http.Request) {
	// Obtiene los parámetros de la solicitud
	text := r.FormValue("text1")
	text2 := r.FormValue("text2")
	ubicacion := strings.ToLower(r.FormValue("ubicacion"))
	formato := r.FormValue("formato")
	fuenteLetra := r.FormValue("font")

	// Obtener la imagen del cuerpo de la solicitud
	file, _, err := r.FormFile("imagen")
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al obtener la imagen de la solicitud: %v", err), http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Leer los bytes de la imagen
	imageBytes, err := ioutil.ReadAll(file)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al leer los bytes de la imagen: %v", err), http.StatusInternalServerError)
		return
	}

	// Convertir los bytes de la imagen en una imagen
	img, _, err := image.Decode(bytes.NewReader(imageBytes))
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al decodificar la imagen: %v", err), http.StatusInternalServerError)
		return
	}

	// Edita la imagen
	editedImage, err := editarImagen(img, text, text2, fuenteLetra, ubicacion)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al editar la imagen: %v", err), http.StatusInternalServerError)
		return
	}

	// Determinar el formato de imagen
	var formatoImaging imaging.Format
	switch strings.ToLower(formato) {
	case "jpeg", "jpg":
		formatoImaging = imaging.JPEG
	case "png":
		formatoImaging = imaging.PNG
	case "bmp":
		formatoImaging = imaging.BMP
	case "tiff":
		formatoImaging = imaging.TIFF
	default:
		http.Error(w, fmt.Sprintf("Formato de imagen no válido: %s", formato), http.StatusBadRequest)
		return
	}

	// Codificar la imagen editada en el formato adecuado y escribir los bytes en la respuesta HTTP
	err = imaging.Encode(w, editedImage, formatoImaging)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error al escribir la imagen editada en la respuesta: %v", err), http.StatusInternalServerError)
		return
	}
}

func guardarImagenSolicitada(w http.ResponseWriter, r *http.Request) {
	// Obtener los parámetros de la solicitud
	nombreImagen := r.FormValue("rutaGuardar")
	// Obtiene la imagen del formulario
	file, _, err := r.FormFile("imagen")
	if err != nil {
		http.Error(w, "Error al obtener el archivo de imagen", http.StatusBadRequest)
		return
	}
	defer file.Close()
	// Crea un nuevo archivo en la ruta especificada
	f, err := os.Create(nombreImagen)
	if err != nil {
		http.Error(w, "Error al crear el archivo", http.StatusInternalServerError)
		return
	}
	defer f.Close()
	// Copia los datos de la imagen al archivo creado
	_, err = io.Copy(f, file)
	if err != nil {
		http.Error(w, "Error al guardar la imagen", http.StatusInternalServerError)
		return
	}

}
func guardarImagenCorreo(w http.ResponseWriter, r *http.Request) {
	// Obtener los parámetros de la solicitud
	nombreImagen := r.FormValue("nombreImagen")
	correoAdjunto := r.FormValue("direccionCorreo")
	// Obtiene la imagen del formulario
	file, _, err := r.FormFile("imagen")
	if err != nil {
		http.Error(w, "Error al obtener el archivo de imagen", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Lee los bytes de la imagen
	imagenBytes, err := ioutil.ReadAll(file)
	if err != nil {
		http.Error(w, "Error al leer los bytes de la imagen", http.StatusInternalServerError)
		return
	}
	if err := enviarCorreo(nombreImagen, correoAdjunto, imagenBytes); err != nil {
		http.Error(w, fmt.Sprintf("Error al enviar el correo electrónico: %v", err), http.StatusInternalServerError)
		return
	}

	// Responde al cliente con un mensaje de éxito
	fmt.Fprintf(w, "Imagen guardada exitosamente como %s", nombreImagen)
}
func parseInt(s string) int {
	// Convierte una cadena a un entero
	// Retorna 0 si hay un error al analizar la cadena
	i, _ := strconv.Atoi(s)
	return i
}
func main() {
	http.HandleFunc("/upload", handleImageUpload)
	fmt.Println("Servidor en ejecución en http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}

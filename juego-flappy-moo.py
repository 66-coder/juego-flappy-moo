import pygame
import random
import sys

# --- 1. Inicialización y Configuración ---
pygame.init()
pygame.mixer.init() 
sonido_punto = pygame.mixer.Sound('sonidos/punto.wav')
sonido_salto = pygame.mixer.Sound('sonidos/salto.wav')

ANCHO_PANTALLA = 400
ALTO_PANTALLA = 600
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Flappy Moo")

# --- CÓDIGO PARA CAMBIAR EL ICONO ---
try:
    # Carga la imagen del icono (asegúrate de que la ruta sea correcta)
    icono_img = pygame.image.load('imagenes/Flappy Moo.png') 
    # Establece la imagen como el icono de la ventana
    pygame.display.set_icon(icono_img)
except pygame.error as e:
    # Es buena práctica manejar el error si la imagen no se encuentra
    print(f"Error al cargar el icono: {e}") 
# -------------------------------------


reloj = pygame.time.Clock()
FPS = 60

fuente = pygame.font.Font(None, 40)
fuente_pequena = pygame.font.Font(None, 25)

BLANCO = (255, 255, 255)
BLANCO_HUESO = (242, 240, 235)
CELESTE = (16, 44, 84)

# ELIMINADAS: COLOR_BORDE y ALTURA_BORDE

# --- 2. Variables de Juego ---
GRAVEDAD = 0.5
VACA_SALTO = -8
VELOCIDAD_TUBERIA = 3
HUECO_TUBERIA = 150
FRECUENCIA_TUBERIA = 1500
ultimo_tiempo_tuberia = pygame.time.get_ticks() - FRECUENCIA_TUBERIA

puntuacion = 0
estado_juego = "INICIO"
corriendo = True

# --- 3. HIGH SCORE Funciones y Variables ---
PUNTUACION_MAXIMA_ARCHIVO = "highscore.txt"

def cargar_puntuacion_maxima():
    try:
        with open(PUNTUACION_MAXIMA_ARCHIVO, 'r') as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0

def guardar_puntuacion_maxima(puntos):
    with open(PUNTUACION_MAXIMA_ARCHIVO, 'w') as f:
        f.write(str(puntos))

puntuacion_maxima = cargar_puntuacion_maxima()
ha_guardado_record = False 


# --- 4. Clases del Juego ---

class Vaca(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        vaca_original = pygame.image.load('imagenes/vaca.png').convert_alpha()
        self.original_image = pygame.transform.scale(vaca_original, (50, 40))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(100, ALTO_PANTALLA // 2))
        self.velocidad = 0

    def update(self):
        self.velocidad += GRAVEDAD
        self.rect.y += self.velocidad

        angulo = max(-90, min(30, -self.velocidad * 3))
        centro_original = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, angulo)
        self.rect = self.image.get_rect(center=centro_original)
        self.mask = pygame.mask.from_surface(self.image)
        
        # Eliminada la lógica de rebote superior.

    def saltar(self):
        self.velocidad = VACA_SALTO
        sonido_salto.play()

class Tuberia(pygame.sprite.Sprite):
    def __init__(self, x, y, posicion):
        super().__init__()
        self.image = pygame.Surface((60, 400))
        VERDE_TUBERIA = (34, 179, 78) 
        BORDE_TUBERIA = (24, 128, 56) 
        self.image.fill(VERDE_TUBERIA)
        self.mask = pygame.mask.from_surface(self.image)
        pygame.draw.rect(self.image, BORDE_TUBERIA, self.image.get_rect(), 3)

        if posicion == 1: 
            self.image = pygame.transform.flip(self.image, False, True) 
            self.rect = self.image.get_rect(midbottom=(x, y - HUECO_TUBERIA // 2))
        else: 
            self.rect = self.image.get_rect(midtop=(x, y + HUECO_TUBERIA // 2))
        
        self.pasada = False 

    def update(self):
        self.rect.x -= VELOCIDAD_TUBERIA
        if self.rect.right < 0:
            self.kill() 

# ELIMINADA: class FondoMovil(pygame.sprite.Sprite):

# --- 5. Funciones Auxiliares ---

def dibujar_texto(texto, fuente, color, superficie, x, y, color_borde=None, offset=2):
    if color_borde:
        sombra_texto = fuente.render(texto, True, color_borde)
        sombra_rect = sombra_texto.get_rect(center=(x + offset, y + offset))
        superficie.blit(sombra_texto, sombra_rect)
        
    objeto_texto = fuente.render(texto, True, color)
    rect_texto = objeto_texto.get_rect(center=(x, y))
    superficie.blit(objeto_texto, rect_texto) 

def manejar_high_score():
    """Gestiona la actualización y guardado de la puntuación máxima."""
    global puntuacion_maxima, ha_guardado_record
    
    if puntuacion > puntuacion_maxima:
        puntuacion_maxima = puntuacion 
        guardar_puntuacion_maxima(puntuacion_maxima) 
    ha_guardado_record = True


def reiniciar_juego(): 
    global puntuacion, ultimo_tiempo_tuberia, ha_guardado_record
    
    puntuacion = 0  
    ha_guardado_record = False
    ultimo_tiempo_tuberia = pygame.time.get_ticks() - FRECUENCIA_TUBERIA

    tuberias.empty()
    todos_los_sprites.empty()

    vaca.rect.center = (100, ALTO_PANTALLA // 2)
    vaca.velocidad = 0
    todos_los_sprites.add(vaca) # SOLO AÑADIMOS LA VACA
    
# --- 6. Creación de Sprites Iniciales ---
todos_los_sprites = pygame.sprite.Group()
tuberias = pygame.sprite.Group()

vaca = Vaca()
# ELIMINADAS: suelo_movil y techo_movil

todos_los_sprites.add(vaca)

# --- 7. Fondo de Estrellas ---
NUMERO_ESTRELLAS = 100
estrellas = []

COLOR_AZUL_CLARO = (175, 215, 255)
COLOR_MORADO = (180, 160, 200)

for _ in range(NUMERO_ESTRELLAS):
    x = random.randint(0, ANCHO_PANTALLA)
    y = random.randint(0, ALTO_PANTALLA)
    velocidad_estrella = random.uniform(0.2, 1.5)
    radio_estrella = random.randint(1, 3)
    color = random.choice([BLANCO_HUESO, BLANCO, COLOR_AZUL_CLARO, COLOR_MORADO])
    estrellas.append([x, y, velocidad_estrella, radio_estrella, color])


# --- 8. Bucle Principal del Juego ---
while corriendo:
   
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if estado_juego == "INICIO":
                    reiniciar_juego() 
                    estado_juego = "JUGANDO"
                elif estado_juego == "JUGANDO":
                    vaca.saltar() 
                elif estado_juego == "FIN":
                    estado_juego = "INICIO"

    
    # Dibujo de fondo y estrellas
    pantalla.fill(CELESTE)
    for x, y, velocidad, radio, color in estrellas:
        pygame.draw.circle(pantalla,color, (int(x), int(y)), radio)

    
    if estado_juego == "INICIO":
        dibujar_texto("Flappy Moo", fuente, BLANCO, pantalla, ANCHO_PANTALLA // 2, 150, (0,0,0))
        dibujar_texto("Presiona ESPACIO", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, 250)
        dibujar_texto("para empezar", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, 280)
        dibujar_texto(f"Récord: {puntuacion_maxima}", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, 350)
        todos_los_sprites.draw(pantalla) 

    elif estado_juego == "JUGANDO":
        # Lógica de actualización
        todos_los_sprites.update()
        tuberias.update() # Las tuberías no están en todos_los_sprites, se actualizan aparte.
        
        # Mover estrellas
        for i in range(len(estrellas)):
            estrellas[i][0] -= estrellas[i][2]
            if estrellas[i][0] < 0:
                estrellas[i][0] = ANCHO_PANTALLA
                estrellas[i][1] = random.randint(0, ALTO_PANTALLA)
        
        # Generación de tuberías
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - ultimo_tiempo_tuberia > FRECUENCIA_TUBERIA:
            altura_tuberia = random.randint(200, 400)
            tuberia_arriba = Tuberia(ANCHO_PANTALLA + 50, altura_tuberia, 1)
            tuberia_abajo = Tuberia(ANCHO_PANTALLA + 50, altura_tuberia, 0)
            tuberias.add(tuberia_arriba, tuberia_abajo)
            ultimo_tiempo_tuberia = tiempo_actual
            
        # Puntuación
        for tuberia in tuberias:
            if not tuberia.pasada and tuberia.rect.centerx < vaca.rect.centerx:
                if tuberia.rect.top > ALTO_PANTALLA / 2: 
                    tuberia.pasada = True
                    puntuacion += 1
                    sonido_punto.play()

        # Detección de Colisiones
        colision_tuberias = pygame.sprite.spritecollide(vaca, tuberias, False, pygame.sprite.collide_mask)
        
        # La vaca muere si toca una tubería, sale por arriba o sale por abajo
        if vaca.rect.bottom >= ALTO_PANTALLA or vaca.rect.top <= 0 or colision_tuberias:
            estado_juego = "FIN"


        # --- DIBUJADO ---
        tuberias.draw(pantalla) # Dibuja las tuberías primero
        todos_los_sprites.draw(pantalla) # Dibuja la vaca encima
        dibujar_texto(str(puntuacion), fuente, BLANCO, pantalla, ANCHO_PANTALLA // 2, 50, (0,0,0))

    
    # Lógica de High Score: Se ejecuta una sola vez al entrar en FIN
    if estado_juego == "FIN" and not ha_guardado_record:
        manejar_high_score()
    
    elif estado_juego == "FIN":
        # Pantalla de Fin de Juego
        tuberias.draw(pantalla)
        todos_los_sprites.draw(pantalla) # Dibuja la vaca
        
        y_center = ALTO_PANTALLA // 2
        dibujar_texto("¡Has Perdido!", fuente, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, y_center - 100)
        dibujar_texto(f"Puntuación: {puntuacion}", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, y_center - 50)
        dibujar_texto(f"Récord: {puntuacion_maxima}", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, y_center)
        dibujar_texto("Presiona ESPACIO para reiniciar", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, y_center + 50)

    # Actualizar la Pantalla
    pygame.display.flip()
    
    reloj.tick(FPS)

# Salir
pygame.quit()
sys.exit()
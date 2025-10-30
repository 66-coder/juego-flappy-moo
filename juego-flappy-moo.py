import pygame
import random
import sys

# --- Inicialización de Pygame ---
pygame.init()
pygame.mixer.init() # Inicializa el mezclador de sonido
sonido_punto = pygame.mixer.Sound('sonidos/punto.mp3')
# --- Configuración de la Pantalla ---
ANCHO_PANTALLA = 400
ALTO_PANTALLA = 600
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Flappy Moo")

# --- Reloj (para controlar los FPS) ---
reloj = pygame.time.Clock()
FPS = 60

# --- Carga de Fuentes ---
fuente = pygame.font.Font(None, 40)
fuente_pequena = pygame.font.Font(None, 25)

# --- Colores ---
BLANCO = (255, 255, 255)
BLANCO_HUESO = (242, 240, 235)
CELESTE = (16, 44, 84)
VERDE = (0, 200, 0)

# --- Variables del Juego ---
GRAVEDAD = 0.5
VACA_SALTO = -8       # La fuerza del salto de la vaca
VELOCIDAD_TUBERIA = 3
HUECO_TUBERIA = 150   # El espacio entre la tubería de arriba y la de abajo
FRECUENCIA_TUBERIA = 1500 # Tiempo en milisegundos para que aparezca una nueva tubería
ultimo_tiempo_tuberia = pygame.time.get_ticks() - FRECUENCIA_TUBERIA

puntuacion = 0
estado_juego = "INICIO"
corriendo = True

# --- Clases del Juego ---

class Vaca(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        vaca_original = pygame.image.load('imagenes/vaca.png').convert_alpha()
        
        # 1. Guarda la imagen escalada como "original"
        self.original_image = pygame.transform.scale(vaca_original, (50, 40))
        
        # 2. 'self.image' será la que rote
        self.image = self.original_image
        
        self.rect = self.image.get_rect(center=(100, ALTO_PANTALLA // 2))
        self.radius = 14 # Un círculo de 18 píxeles de radio
        self.velocidad = 0

    def update(self):
        # Aplicar la gravedad para que la vaca caiga
        self.velocidad += GRAVEDAD
        self.rect.y += self.velocidad

# --- AÑADIR ESTE BLOQUE DE ROTACIÓN ---
        # Rotamos la vaca basado en su velocidad vertical.
        # (-self.velocidad * 3) la inclina hacia arriba al subir (vel negativa)
        # y hacia abajo al caer (vel positiva).
        # Usamos min() y max() para poner un tope (que no gire 360 grados)
        angulo = max(-90, min(30, -self.velocidad * 3))
        
        # Rotamos la imagen *original* (esto es clave para no perder calidad)
        self.image = pygame.transform.rotate(self.original_image, angulo)
        
        # Pygame cambia el centro del 'rect' al rotar.
        # Lo recentramos en su posición anterior para que no "salte" de lugar.
        centro_original = self.rect.center
        self.rect = self.image.get_rect(center=centro_original)
        # --- FIN DEL BLOQUE DE ROTACIÓN ---

        # Evitar que la vaca se salga por la parte superior de la pantalla
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocidad = 0

    def saltar(self):
        # Aplicar una velocidad hacia arriba para simular un salto
        self.velocidad = VACA_SALTO

class Tuberia(pygame.sprite.Sprite):
    def __init__(self, x, y, posicion):
        super().__init__()
        # Se crea la superficie para la tubería
        self.image = pygame.Surface((60, 400))
       
        VERDE_TUBERIA = (34, 179, 78) # Un verde más brillante
        BORDE_TUBERIA = (24, 128, 56) # Un verde oscuro para el borde

        self.image.fill(VERDE_TUBERIA)
        # Dibujamos un borde de 3 píxeles de ancho
        pygame.draw.rect(self.image, BORDE_TUBERIA, self.image.get_rect(), 3)

        if posicion == 1: # Tubería de arriba
            self.image = pygame.transform.flip(self.image, False, True) # Se invierte la imagen
            self.rect = self.image.get_rect(midbottom=(x, y - HUECO_TUBERIA // 2))
        else: # Tubería de abajo
            self.rect = self.image.get_rect(midtop=(x, y + HUECO_TUBERIA // 2))
        
        self.pasada = False # Variable para saber si la vaca ya pasó esta tubería

    def update(self):
        # Mover la tubería hacia la izquierda
        self.rect.x -= VELOCIDAD_TUBERIA
        if self.rect.right < 0:
            self.kill() # Elimina la tubería cuando sale de la pantalla para ahorrar memoria

# --- Grupos de Sprites (para manejar varios objetos a la vez) ---
todos_los_sprites = pygame.sprite.Group()
tuberias = pygame.sprite.Group()

vaca = Vaca()
todos_los_sprites.add(vaca)

# --- Funciones Auxiliares ---

def dibujar_texto(texto, fuente, color, superficie, x, y):
    objeto_texto = fuente.render(texto, True, color)
    rect_texto = objeto_texto.get_rect(center=(x, y))
    superficie.blit(objeto_texto, rect_texto)

def reiniciar_juego():
    global puntuacion, juego_terminado, ultimo_tiempo_tuberia
    # Reiniciar todas las variables del juego a su estado inicial
    puntuacion = 0  
    ultimo_tiempo_tuberia = pygame.time.get_ticks() - FRECUENCIA_TUBERIA
    
    # Limpiar todas las tuberías de la pantalla
    tuberias.empty()
    todos_los_sprites.empty()
    
    # Volver a colocar la vaca en su posición inicial
    vaca.rect.center = (100, ALTO_PANTALLA // 2)
    vaca.velocidad = 0
    todos_los_sprites.add(vaca)

# --- Creación del Fondo de Estrellas ---
NUMERO_ESTRELLAS = 100
estrellas = []

for _ in range(NUMERO_ESTRELLAS):
    # Posición inicial aleatoria
    x = random.randint(0, ANCHO_PANTALLA)
    y = random.randint(0, ALTO_PANTALLA)
    
    # Velocidad aleatoria (más lenta que las tuberías para el efecto parallax)
    # Un valor entre 0.2 y 1.5
    velocidad_estrella = random.uniform(0.2, 1.5)
    
    # Radio (tamaño) de la estrella
    radio_estrella = random.randint(1, 2)
    
    # Guardamos [x, y, velocidad, radio]
    estrellas.append([x, y, velocidad_estrella, radio_estrella])

# --- Bucle Principal del Juego ---
while corriendo:
   # --- Manejo de Eventos (input del usuario) ---
    for evento in pygame.event.get():
        # Si el usuario cierra la ventana
        if evento.type == pygame.QUIT:
            corriendo = False
        # Si el usuario presiona una tecla
        if evento.type == pygame.KEYDOWN:
            # Si la tecla es ESPACIO
            if evento.key == pygame.K_SPACE:
                if estado_juego == "INICIO":
                    # Si estamos en el inicio, empezamos a JUGAR
                    estado_juego = "JUGANDO"
                    reiniciar_juego() # Preparamos el juego
                
                elif estado_juego == "JUGANDO":
                    # Si estamos jugando, la vaca salta
                    vaca.saltar() 
                    
                elif estado_juego == "FIN":
                    # Si perdimos, volvemos al INICIO
                    estado_juego = "INICIO"
                    reiniciar_juego() # Limpiamos la pantalla

    # --- Lógica del Juego (solo si no ha terminado) ---
   # --- Lógica y Dibujo por Estado ---

    # Primero, dibujamos el fondo y las estrellas (que se ven en todos los estados)
    pantalla.fill(CELESTE)
    for x, y, velocidad, radio in estrellas:
        pygame.draw.circle(pantalla, BLANCO_HUESO, (int(x), int(y)), radio)

    
    if estado_juego == "INICIO":
        # --- Pantalla de Inicio ---
        # No hay lógica, solo dibujamos texto y la vaca quieta
        dibujar_texto("Flappy Moo", fuente, BLANCO, pantalla, ANCHO_PANTALLA // 2, 150)
        dibujar_texto("Presiona ESPACIO", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, 250)
        dibujar_texto("para empezar", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, 280)
        
        # Dibuja la vaca en su posición inicial
        todos_los_sprites.draw(pantalla) 

    elif estado_juego == "JUGANDO":
        # --- Lógica del Juego ---
        todos_los_sprites.update()
        
        # Mover las estrellas
        for i in range(len(estrellas)):
            estrellas[i][0] -= estrellas[i][2]
            if estrellas[i][0] < 0:
                estrellas[i][0] = ANCHO_PANTALLA
                estrellas[i][1] = random.randint(0, ALTO_PANTALLA)
        
        # Generar nuevas tuberías
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - ultimo_tiempo_tuberia > FRECUENCIA_TUBERIA:
            altura_tuberia = random.randint(200, 400)
            tuberia_arriba = Tuberia(ANCHO_PANTALLA + 50, altura_tuberia, 1)
            tuberia_abajo = Tuberia(ANCHO_PANTALLA + 50, altura_tuberia, 0)
            tuberias.add(tuberia_arriba, tuberia_abajo)
            todos_los_sprites.add(tuberia_arriba, tuberia_abajo)
            ultimo_tiempo_tuberia = tiempo_actual
            
        # Comprobar si la vaca ha pasado una tubería
        for tuberia in tuberias:
            if not tuberia.pasada and tuberia.rect.centerx < vaca.rect.left:
                if tuberia.rect.top > ALTO_PANTALLA / 2: 
                    tuberia.pasada = True
                    puntuacion += 1
        
        # --- Detección de Colisiones ---
        colision_tuberias = pygame.sprite.spritecollide(vaca, tuberias, False, pygame.sprite.collide_circle)
        if vaca.rect.bottom >= ALTO_PANTALLA or colision_tuberias:
            estado_juego = "FIN"

        # --- Dibujar en Pantalla (Jugando) ---
        todos_los_sprites.draw(pantalla)
        dibujar_texto(str(puntuacion), fuente, BLANCO, pantalla, ANCHO_PANTALLA // 2, 50)
    
    elif estado_juego == "FIN":
        # --- Pantalla de Juego Terminado ---
        # No hay lógica, solo dibujamos la pantalla final
        
        # Dibuja la escena final (vaca caída, tuberías)
        todos_los_sprites.draw(pantalla) 
        
        # Dibuja el texto de "Game Over"
        dibujar_texto("¡Has Perdido!", fuente, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 50)
        dibujar_texto(f"Puntuación: {puntuacion}", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)
        dibujar_texto("Presiona ESPACIO para reiniciar", fuente_pequena, BLANCO_HUESO, pantalla, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 + 50)

    # --- Actualizar la Pantalla (esto está fuera del if/elif) ---
    pygame.display.flip()
   
   
    # --- Actualizar la Pantalla ---
    pygame.display.flip()

    # --- Controlar los FPS para que el juego corra a una velocidad constante ---
    reloj.tick(FPS)

# --- Salir del Juego ---
pygame.quit()
sys.exit()
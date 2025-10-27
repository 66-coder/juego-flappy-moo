import pygame
import random
import sys

# --- Inicialización de Pygame ---
pygame.init()

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
NEGRO = (0, 0, 0)
CELESTE = (135, 206, 235)
VERDE = (0, 200, 0)

# --- Variables del Juego ---
GRAVEDAD = 0.5
VACA_SALTO = -8       # La fuerza del salto de la vaca
VELOCIDAD_TUBERIA = 3
HUECO_TUBERIA = 150   # El espacio entre la tubería de arriba y la de abajo
FRECUENCIA_TUBERIA = 1500 # Tiempo en milisegundos para que aparezca una nueva tubería
ultimo_tiempo_tuberia = pygame.time.get_ticks() - FRECUENCIA_TUBERIA

puntuacion = 0
juego_terminado = False
corriendo = True

# --- Clases del Juego ---

class Vaca(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Se crea una superficie simple como vaca.
        # Puedes reemplazar esto con una imagen cargada con: pygame.image.load('tu_vaca.png').convert_alpha()
        self.image = pygame.Surface((40, 30))
        self.image.fill(BLANCO) # La vaca será un rectángulo blanco
        self.rect = self.image.get_rect(center=(100, ALTO_PANTALLA // 2))
        self.velocidad = 0

    def update(self):
        # Aplicar la gravedad para que la vaca caiga
        self.velocidad += GRAVEDAD
        self.rect.y += self.velocidad

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
        self.image.fill(VERDE)
        
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
    juego_terminado = False
    ultimo_tiempo_tuberia = pygame.time.get_ticks() - FRECUENCIA_TUBERIA
    
    # Limpiar todas las tuberías de la pantalla
    tuberias.empty()
    todos_los_sprites.empty()
    
    # Volver a colocar la vaca en su posición inicial
    vaca.rect.center = (100, ALTO_PANTALLA // 2)
    vaca.velocidad = 0
    todos_los_sprites.add(vaca)


# --- Bucle Principal del Juego ---
while corriendo:
    # --- Manejo de Eventos (input del usuario) ---
    for evento in pygame.event.get():
        # Si el usuario cierra la ventana
        if evento.type == pygame.QUIT:
            corriendo = False
        # Si el usuario presiona una tecla
        if evento.type == pygame.KEYDOWN:
            # Si la tecla es ESPACIO y el juego no ha terminado, la vaca salta
            if evento.key == pygame.K_SPACE and not juego_terminado:
                vaca.saltar()
            # Si la tecla es ESPACIO y el juego SÍ ha terminado, se reinicia
            if evento.key == pygame.K_SPACE and juego_terminado:
                reiniciar_juego()

    # --- Lógica del Juego (solo si no ha terminado) ---
    if not juego_terminado:
        # Actualizar la posición de todos los sprites (vaca y tuberías)
        todos_los_sprites.update()
        
        # Generar nuevas tuberías periódicamente
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - ultimo_tiempo_tuberia > FRECUENCIA_TUBERIA:
            altura_tuberia = random.randint(200, 400)
            tuberia_arriba = Tuberia(ANCHO_PANTALLA + 50, altura_tuberia, 1)
            tuberia_abajo = Tuberia(ANCHO_PANTALLA + 50, altura_tuberia, 0)
            tuberias.add(tuberia_arriba, tuberia_abajo)
            todos_los_sprites.add(tuberia_arriba, tuberia_abajo)
            ultimo_tiempo_tuberia = tiempo_actual
            
        # Comprobar si la vaca ha pasado una tubería para sumar puntos
        for tuberia in tuberias:
            if not tuberia.pasada and tuberia.rect.centerx < vaca.rect.left:
                # Se comprueba que sea la tubería de abajo para contar el punto una sola vez por par
                if tuberia.rect.top > ALTO_PANTALLA / 2: 
                    tuberia.pasada = True
                    puntuacion += 1
        
        # --- Detección de Colisiones ---
        # Colisión con el suelo
        if vaca.rect.bottom >= ALTO_PANTALLA:
            juego_terminado = True

        # Colisión con las tuberías
        if pygame.sprite.spritecollide(vaca, tuberias, False):
            juego_terminado = True

    # --- Dibujar en la Pantalla ---
    pantalla.fill(CELESTE) # Color de fondo

    # Dibuja todos los sprites (la vaca y las tuberías)
    todos_los_sprites.draw(pantalla)

    # Mostrar la puntuación en la parte superior
    dibujar_texto(str(puntuacion), fuente, BLANCO, pantalla, ANCHO_PANTALLA // 2, 50)
    
    # --- Pantalla de Juego Terminado ---
    if juego_terminado:
        dibujar_texto("¡Has Perdido!", fuente, NEGRO, pantalla, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 50)
        dibujar_texto("Presiona ESPACIO para reiniciar", fuente_pequena, NEGRO, pantalla, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)

    # --- Actualizar la Pantalla ---
    pygame.display.flip()

    # --- Controlar los FPS para que el juego corra a una velocidad constante ---
    reloj.tick(FPS)

# --- Salir del Juego ---
pygame.quit()
sys.exit()
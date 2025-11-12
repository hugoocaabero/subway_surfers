import cv2
import mediapipe as mp
import time
# Nota: Se eliminan imports no utilizados como numpy y datetime para limpiar el código.

# Intentar importar pyautogui
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False
    print("ADVERTENCIA: pyautogui no está disponible. Las acciones solo se simularán en la consola.")

# MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Configuración de teclas (por defecto, para un emulador como BlueStacks)
EMULATOR_CONFIGS = {
    'bluestacks': {
        'up': 'up',     # salto
        'down': 'down', # deslizar
        'left': 'left', # izquierda
        'right': 'right'# derecha
    },
    'nox': {
        'up': 'w',
        'down': 's',
        'left': 'a',
        'right': 'd'
    }
}

# Por defecto usar BlueStacks
CURRENT_CONFIG = EMULATOR_CONFIGS['bluestacks']

class Config:
    """Configuración ajustable del detector"""
    def __init__(self):
        # Umbrales de movimiento (ajustables con +/-). Son valores normalizados (0.0 a 1.0)
        # NOTA: Los cooldowns son eliminados y reemplazados por la lógica de bloqueo/reseteo.
        self.JUMP_THRESHOLD = 0.035     # Mover la cabeza un 3.5% de la pantalla para Saltar
        self.SLIDE_THRESHOLD = 0.04     # Mover la cabeza un 4% de la pantalla para Deslizar
        self.SIDE_THRESHOLD = 0.07      # Mover la cabeza un 7% de la pantalla para Moverse
        
        # Frames necesarios para confirmar un movimiento
        self.DETECTION_FRAMES = 1       # Recomendado: 1-3
        
        # Calibración
        self.CALIBRATED = False
        self.neutral_pose = None
        
        # Sensibilidad global (multiplicador para todos los umbrales)
        self.SENSITIVITY = 1.0          # 1.0 por defecto

# Variables globales
config = Config()
# Diccionario que rastrea si una acción ha sido ejecutada y está esperando el reset a neutral
action_lock = {'up': False, 'down': False, 'left': False, 'right': False}


def get_pose_features(landmarks):
    """Extrae la posición normalizada de la nariz (cabeza)"""
    if landmarks is None:
        return None
    
    try:
        # Solo necesitamos la nariz (landmark 0)
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        # Las coordenadas .x y .y de MediaPipe están normalizadas (0.0 a 1.0)
        return {
            'nose_x': nose.x, 
            'nose_y': nose.y 
        }
    except:
        return None

def calibrate(features):
    """Guarda la posición neutral de la cabeza."""
    if not features or 'nose_x' not in features:
        print("\nError: No se detectó tu cara. Asegúrate de estar bien iluminado.")
        return False
    
    # Guardar la posición neutral
    config.neutral_pose = {
        'neutral_x': features['nose_x'],
        'neutral_y': features['nose_y']
    }
    
    config.CALIBRATED = True
    print("\n\n--- ¡CALIBRACIÓN EXITOSA! ---")
    print("Posición de la cabeza guardada. Intenta moverte.")
    return True

def detect_actions(features):
    """
    Detecta acciones basado en la posición actual de la cabeza vs. la posición neutral.
    Usa la lógica de BLOQUEO para asegurar que cada acción (tap) se envíe solo una vez
    por cada vez que se sale de la zona neutral.
    """
    global action_lock 
    
    if not config.CALIBRATED or not features or not config.neutral_pose:
        return set()
    
    actions = set()
    
    current_x = features['nose_x']
    current_y = features['nose_y']
    neutral_x = config.neutral_pose['neutral_x']
    neutral_y = config.neutral_pose['neutral_y']
    
    # Aplica la sensibilidad a los umbrales
    threshold_jump = config.JUMP_THRESHOLD * config.SENSITIVITY
    threshold_slide = config.SLIDE_THRESHOLD * config.SENSITIVITY
    threshold_side = config.SIDE_THRESHOLD * config.SENSITIVITY

    # Verificar si la cabeza está dentro de la zona neutral (tanto en X como en Y)
    is_in_neutral_x = abs(current_x - neutral_x) < threshold_side
    is_in_neutral_y = (current_y > neutral_y - threshold_jump) and \
                      (current_y < neutral_y + threshold_slide)
    
    # --- RESETEO GLOBAL ---
    # Si la cabeza está en la zona neutral COMPLETA, reseteamos TODOS los bloqueos
    if is_in_neutral_x and is_in_neutral_y:
        action_lock['up'] = False
        action_lock['down'] = False
        action_lock['left'] = False
        action_lock['right'] = False
    
    # --- SALTO (cabeza arriba) ---
    if current_y < neutral_y - threshold_jump and not action_lock['up']:
        actions.add('jump')
        action_lock['up'] = True 
    
    # --- DESLIZAR (cabeza abajo) ---
    if current_y > neutral_y + threshold_slide and not action_lock['down']:
        actions.add('slide')
        action_lock['down'] = True 
    
    # --- IZQUIERDA (cabeza a la izquierda) ---
    if current_x < neutral_x - threshold_side and not action_lock['left']:
        actions.add('left')
        action_lock['left'] = True 
    
    # --- DERECHA (cabeza a la derecha) ---
    if current_x > neutral_x + threshold_side and not action_lock['right']:
        actions.add('right')
        action_lock['right'] = True
    
    return actions

def execute_actions(actions):
    """
    Ejecuta las acciones detectadas enviando teclas al emulador.
    pyautogui.press(key) simula un toque rápido (presionar y soltar) de la tecla.
    """
    action_map = {
        'jump': CURRENT_CONFIG['up'],
        'slide': CURRENT_CONFIG['down'],
        'left': CURRENT_CONFIG['left'],
        'right': CURRENT_CONFIG['right']
    }
    
    for action in actions:
        if PYAUTOGUI_AVAILABLE:
            key = action_map.get(action, '')
            if key:
                pyautogui.press(key)
                print(f"-> TECLA PRESIONADA: {key} (Acción: {action})")
        else:
            print(f"[SIMULACIÓN] Acción: {action} -> Tecla: {action_map.get(action)}")

def draw_neutral_zone(image, neutral_pose):
    """Dibuja la zona neutral y los límites de movimiento en la imagen (overlay)."""
    h, w, _ = image.shape
    
    # Coordenadas neutrales (normalizadas 0.0 a 1.0)
    nx = neutral_pose['neutral_x']
    ny = neutral_pose['neutral_y']
    
    # Umbrales (usando la sensibilidad aplicada)
    dx = config.SIDE_THRESHOLD * config.SENSITIVITY
    dy_up = config.JUMP_THRESHOLD * config.SENSITIVITY
    dy_down = config.SLIDE_THRESHOLD * config.SENSITIVITY
    
    # Convertir a píxeles
    center_x = int(nx * w)
    center_y = int(ny * h)
    
    # Calcular límites de la zona neutral en píxeles
    x_min = int((nx - dx) * w)
    x_max = int((nx + dx) * w)
    y_min_jump = int((ny - dy_up) * h)
    y_max_slide = int((ny + dy_down) * h)
    
    # 1. Dibujar el punto central neutral (Cyan)
    cv2.circle(image, (center_x, center_y), 7, (0, 255, 255), -1) 
    
    # 2. Dibujar la ZONA NEUTRAL (rectángulo) - Gris claro
    cv2.rectangle(image, (x_min, y_min_jump), (x_max, y_max_slide), (180, 180, 180), 2)
    
    # 3. Dibujar las flechas de acción fuera de la zona neutral (para indicar el movimiento)
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # UP (Salto)
    cv2.putText(image, "SALTAR", (center_x - 30, max(20, y_min_jump - 15)), font, 0.6, (0, 0, 255), 2)
    # DOWN (Deslizar)
    cv2.putText(image, "DESLIZAR", (center_x - 40, min(h - 10, y_max_slide + 30)), font, 0.6, (0, 0, 255), 2)

    # LEFT
    cv2.putText(image, "IZQ", (max(10, x_min - 40), center_y + 10), font, 0.6, (255, 0, 0), 2)
    # RIGHT
    cv2.putText(image, "DER", (min(w - 50, x_max + 10), center_y + 10), font, 0.6, (255, 0, 0), 2)


def main():
    # Inicializar MediaPipe Pose
    pose = mp_pose.Pose(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        model_complexity=1 # 0: más rápido, 1: por defecto, 2: más lento/preciso
    )
    
    # Captura de video
    cap = cv2.VideoCapture(0)
    
    print("\n--- Subway Surfers AI Controller - Control con la Cabeza ---")
    print("----------------------------------------------------------------")
    print("Controles:")
    print("- Mueve la cabeza hacia ARRIBA/ABAJO/IZQUIERDA/DERECHA para JUGAR.")
    print("- Mantén tu cabeza dentro del rectángulo gris para la POSICIÓN NEUTRAL.")
    print("\nComandos de Teclado:")
    print("c : Calibrar posición neutral (mira al centro)")
    print("+/- : Aumentar/Disminuir sensibilidad (actual: %.1f)" % config.SENSITIVITY)
    print("r : Restablecer calibración")
    print("q/ESC : Salir")
    print("\nEstado: Esperando calibración (Pulsa 'c')...")
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue
        
        # Voltear imagen horizontalmente (efecto espejo)
        image = cv2.flip(image, 1)
        
        # Procesar imagen
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = pose.process(rgb)
        rgb.flags.writeable = True
        image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        
        current_features = None
        
        if results.pose_landmarks:
            # Dibujar pose
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )
            
            # Extraer features de la cabeza
            current_features = get_pose_features(results.pose_landmarks.landmark)
            
            # Detectar y ejecutar acciones si está calibrado
            if config.CALIBRATED and current_features:
                actions = detect_actions(current_features)
                if actions:
                    execute_actions(actions)
        
        # Overlay de estado y UI
        status_color = (0,255,0) if config.CALIBRATED else (0,128,255)
        status_text = "CALIBRADO" if config.CALIBRATED else "NO CALIBRADO"
        cv2.putText(image, f"Estado: {status_text}", (10,30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        cv2.putText(image, f"Sensibilidad: {config.SENSITIVITY:.1f}", (10,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
        
        cv2.putText(image, "c=calibrar  +/-=sens  r=reset  q=salir", (10,90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)

        # Dibuja la zona neutral si está calibrado
        if config.CALIBRATED and config.neutral_pose:
            draw_neutral_zone(image, config.neutral_pose)
        
        cv2.imshow('Subway Surfers Controller', image)
        
        # Manejo de teclas
        key = cv2.waitKey(5) & 0xFF
        
        if key == ord('c'):
            # Calibrar con pose actual
            if current_features:
                calibrate(current_features)
            else:
                print("No se detecta la pose. Por favor, asegúrate de estar visible.")
        
        elif key == ord('r'):
            # Reset calibración
            config.CALIBRATED = False
            config.neutral_pose = None
            # Resetear también el bloqueo direccional al resetear la calibración
            action_lock['up'] = False
            action_lock['down'] = False
            action_lock['left'] = False
            action_lock['right'] = False
            print("\nCalibración reseteada. Pulsa 'c' para re-calibrar.")
        
        elif key == ord('+') or key == ord('='):
            # Aumentar sensibilidad (Umbrales más pequeños, más fácil de activar)
            config.SENSITIVITY = min(2.5, config.SENSITIVITY + 0.1)
            print(f"\nSensibilidad Aumentada: {config.SENSITIVITY:.1f}")
            
        elif key == ord('-'):
            # Disminuir sensibilidad (Umbrales más grandes, más difícil de activar)
            config.SENSITIVITY = max(0.2, config.SENSITIVITY - 0.1)
            print(f"\nSensibilidad Disminuida: {config.SENSITIVITY:.1f}")
            
        elif key == ord('q') or key == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

import cv2
import mediapipe as mp
import numpy as np
import pygame
from typing import Optional, Tuple, Dict, List
import threading
import time
from libras_model_loader import LibrasModelLoader

class LibrasSignIdentifier:
    def __init__(self):
        self.running = False
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.libras_model_loader = LibrasModelLoader(model_path="libras_dataset.csv")
        self.current_libras_letter = ""
        self.libras_letter_history = []
        self.libras_stability_threshold = 5 # Frames consecutivos para confirmar a letra
        
        self.current_gesture = "none"
        self.gesture_confidence = 0.0
        self.gesture_history = []
        self.gesture_stability_threshold = 3
        
        self.game_commands = {
            'advance_dialogue': False,
            'skip_text': False,
            'menu': False,
            'confirm': False,
            'cancel': False,
            'move_left': False,
            'move_right': False,
            'jump': False,
            'interact': False,
            'libras_letter': ''
        }
        
        self.frame_lock = threading.Lock()
        self.current_frame = None
        
    def _get_hand_landmarks_flat(self, hand_landmarks) -> List[float]:
        landmarks_flat = []
        for landmark in hand_landmarks.landmark:
            landmarks_flat.extend([landmark.x, landmark.y, landmark.z])
        return landmarks_flat

    def detect_libras_letter(self, hand_landmarks) -> str:
        if self.libras_model_loader.model is None:
            return "MODELO_NAO_CARREGADO"
        
        landmarks_flat = self._get_hand_landmarks_flat(hand_landmarks)
        return self.libras_model_loader.predict(landmarks_flat)

    def update_libras_stability(self, letter: str):
        self.libras_letter_history.append(letter)
        
        if len(self.libras_letter_history) > self.libras_stability_threshold:
            self.libras_letter_history.pop(0)
        
        if len(self.libras_letter_history) >= self.libras_stability_threshold:
            recent_letters = self.libras_letter_history
            if all(l == letter for l in recent_letters) and letter not in ["MODELO_NAO_CARREGADO", "FORMATO_INCORRETO"]:
                self.current_libras_letter = letter
            else:
                self.current_libras_letter = ""

    def detect_gesture(self, landmarks) -> Tuple[str, float]:
        if not landmarks:
            return "none", 0.0
        
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        
        thumb_index_distance = np.sqrt(
            (thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2
        )
        
        if thumb_index_distance < 0.05:
            return "ok", 0.9
        
        fingers_up = []
        
        if thumb_tip.x > thumb_ip.x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        
        for tip, pip in [(index_tip, index_pip), (middle_tip, middle_pip), 
                        (ring_tip, ring_pip), (pinky_tip, pinky_pip)]:
            if tip.y < pip.y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        if fingers_up == [0, 1, 0, 0, 0]:
            return "point", 0.8
        
        if fingers_up == [0, 1, 1, 0, 0]:
            return "peace", 0.8
        
        if sum(fingers_up) == 0:
            return "fist", 0.7
        
        if sum(fingers_up) >= 4:
            return "open_hand", 0.7
        
        if fingers_up == [1, 1, 1, 0, 0]:
            return "three", 0.7
        
        return "unknown", 0.5
    
    def update_gesture_stability(self, gesture: str, confidence: float):
        self.gesture_history.append((gesture, confidence))
        
        if len(self.gesture_history) > self.gesture_stability_threshold:
            self.gesture_history.pop(0)
        
        if len(self.gesture_history) >= self.gesture_stability_threshold:
            recent_gestures = [g[0] for g in self.gesture_history]
            if all(g == gesture for g in recent_gestures):
                self.current_gesture = gesture
                self.gesture_confidence = confidence
            else:
                self.current_gesture = "none"
                self.gesture_confidence = 0.0
    
    def process_frame(self, frame):
        if frame is None:
            return
        
        # Espelhar horizontalmente para melhor experiência do usuário
        frame = cv2.flip(frame, 1)
        
        # Converter BGR para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Processar com MediaPipe
        results = self.hands.process(rgb_frame)
        
        gesture = "none"
        confidence = 0.0
        libras_letter = ""
        
        # Desenhar landmarks e detectar gestos
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Desenhar landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
                # Detectar gesto
                gesture, confidence = self.detect_gesture(hand_landmarks.landmark)
                
                # Detectar letra de Libras
                libras_letter = self.detect_libras_letter(hand_landmarks)
                self.update_libras_stability(libras_letter)

                # Adicionar texto com o gesto detectado
                cv2.putText(frame, f"Gesto: {gesture} ({confidence:.2f})", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Libras: {self.current_libras_letter}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Atualizar estabilidade do gesto
        self.update_gesture_stability(gesture, confidence)
        
        with self.frame_lock:
            self.current_frame = frame
    
    def get_game_commands(self) -> Dict[str, bool]:
        for key in self.game_commands:
            if key != 'libras_letter':
                self.game_commands[key] = False
        
        if self.current_gesture and self.gesture_confidence > 0.6:
            if self.current_gesture == "point":
                self.game_commands["advance_dialogue"] = True
                self.game_commands["interact"] = True
            elif self.current_gesture == "fist":
                self.game_commands["skip_text"] = True
                self.game_commands["jump"] = True
            elif self.current_gesture == "open_hand":
                self.game_commands["menu"] = True
            elif self.current_gesture == "ok":
                self.game_commands["confirm"] = True
            elif self.current_gesture == "peace":
                self.game_commands["cancel"] = True
            elif self.current_gesture == "two":
                pass
        
        self.game_commands["libras_letter"] = self.current_libras_letter
        
        return self.game_commands.copy()
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_gesture_info(self) -> Tuple[str, float]:
        return self.current_gesture, self.gesture_confidence

class LibrasDisplay:
    def __init__(self, controller: LibrasSignIdentifier, position: Tuple[int, int], size: Tuple[int, int]):
        self.controller = controller
        self.position = position
        self.size = size
        self.visible = True
        
    def toggle_visibility(self):
        self.visible = not self.visible
    
    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        frame = self.controller.get_current_frame()
        if frame is None:
            return
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, self.size)
        frame_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))
        
        surface.blit(frame_surface, self.position)
        
        gesture, confidence = self.controller.get_gesture_info()
        libras_letter = self.controller.current_libras_letter

        font = pygame.font.Font(None, 24)
        y_offset = self.position[1] + self.size[1] + 5

        if gesture != "none":
            text = f"Gesto: {gesture} ({confidence:.2f})"
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.position[0], y_offset)
            pygame.draw.rect(surface, (0, 0, 0), text_rect.inflate(10, 5))
            surface.blit(text_surface, text_rect)
            y_offset += text_rect.height + 5
            
        if libras_letter:
            text = f"Libras: {libras_letter}"
            text_surface = font.render(text, True, (255, 255, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.position[0], y_offset)
            pygame.draw.rect(surface, (0, 0, 0), text_rect.inflate(10, 5))
            surface.blit(text_surface, text_rect)

if __name__ == "__main__":
    # Este bloco não será executado diretamente no jogo, mas é útil para testes isolados
    # Para testar, você precisaria de uma câmera real e um ambiente com acesso a ela.
    print("Este script não inicializa a câmera diretamente. Ele espera frames de uma fonte externa.")
    print("Para testar a funcionalidade de reconhecimento, integre-o a um aplicativo que forneça frames de vídeo.")



import pygame
import sys
from typing import Dict, Optional
import cv2
import numpy as np
from libras_sign_identifier import LibrasSignIdentifier, LibrasDisplay

# ============== Placeholder opcional para PlatformGame ==============
# Se você já tem platform_game.py com a classe PlatformGame, pode remover
# esta classe e fazer "from platform_game import PlatformGame".
class PlatformGame:
    def __init__(self, screen=None):
        self.screen = screen
        self.player_x = 100
        self.player_y = 600
        self.player_speed = 5
        self.player_velocity_y = 0
        self.player_jump_power = -12
        self.gravity = 0.6
        self.is_jumping = False

    def handle_input(self, event):
        pass

    def update(self):
        # gravidade básica
        self.player_velocity_y += self.gravity
        self.player_y += self.player_velocity_y
        if self.player_y >= 600:
            self.player_y = 600
            self.player_velocity_y = 0
            self.is_jumping = False

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill((30, 30, 40))
        pygame.draw.rect(screen, (80, 180, 255), (0, 650, 1024, 50))
        pygame.draw.rect(screen, (255, 220, 50), (self.player_x, int(self.player_y) - 40, 40, 40))
        font = pygame.font.Font(None, 28)
        info = font.render("Plataforma (ESC volta ao menu)", True, (255, 255, 255))
        screen.blit(info, (20, 20))
# ====================================================================

# Inicializa o Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Candango: Neural Ascension")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Fontes
try:
    FONT_DIALOGUE = pygame.font.Font(None, 24)
    FONT_NAME = pygame.font.Font(None, 28)
    FONT_UI = pygame.font.Font(None, 20)
    FONT_LARGE = pygame.font.Font(None, 64)
except Exception:
    FONT_DIALOGUE = pygame.font.Font(pygame.font.get_default_font(), 24)
    FONT_NAME = pygame.font.Font(pygame.font.get_default_font(), 28)
    FONT_UI = pygame.font.Font(pygame.font.get_default_font(), 20)
    FONT_LARGE = pygame.font.Font(pygame.font.get_default_font(), 64)

# Estados do jogo
class GameState:
    MENU = "menu"
    SPELL_NAME = "spell_name"
    VISUAL_NOVEL = "visual_novel"
    PLATFORM = "platform"
    THANK_YOU = "thank_you"

class CandangoGame:
    """Classe principal do jogo Candango: Neural Ascension"""

    def __init__(self):
        self.state = GameState.MENU
        self.clock = pygame.time.Clock()
        self.running = True

        # Libras Sign Identifier
        self.libras_enabled = True
        self.libras_sign_identifier: Optional[LibrasSignIdentifier] = None
        self.libras_display: Optional[LibrasDisplay] = None
        self.cap = None # Webcam capture

        # Visual Novel
        self.story_index = 0
        self.dialogue_text = ""
        self.dialogue_speaker = ""
        self.dialogue_typing = False
        self.dialogue_char_index = 0
        self.typing_speed = 2

        # Configurações
        self.gesture_sensitivity = 0.6

        # Story script
        self.story_script = [
            {"speaker": "Narrador", "text": "Em um escritório cinzento de Brasília, um estagiário enfrenta mais um dia de rotina opressiva...", "background": "office"},
            {"speaker": "Estagiário", "text": "Mais um dia... a mesma rotina esmagadora. Mas hoje... hoje algo parece diferente. Uma faísca?", "background": "office"},
            {"speaker": "Chefe", "text": "Estagiário, este relatório está inaceitável! Esperava mais de você!", "background": "office"},
            {"speaker": "Estagiário", "text": "(Engolindo em seco) Sim, senhor. Vou revisar imediatamente.", "background": "office"},
            {"speaker": "Narrador", "text": "Mas algo extraordinário estava prestes a acontecer. O Cerrado chamava...", "background": "transition"},
            {"speaker": "Macaco-Prego", "text": "Ei, Candango! O Cerrado precisa de nós! As queimadas estão destruindo nossa casa!", "background": "cerrado"},
            {"speaker": "Coruja Sábia", "text": "A sabedoria ancestral reside na harmonia com a natureza. Ouça o vento, jovem Candango.", "background": "cerrado"},
            {"speaker": "Estagiário", "text": "Eu... eu posso sentir algo crescendo dentro de mim. Um poder que nunca soube que existia!", "background": "cerrado"},
            {"speaker": "Super Neural", "text": "Estou pronto para ascender! O Cerrado será protegido!", "background": "cerrado"},
        ]

        # Plataforma
        self.platform_game = PlatformGame(SCREEN)

        # Soletração do nome
        self.player_name = ""
        self.last_recognized_letter = ""
        self.letter_add_timer = 0
        self.LETTER_ADD_DELAY = 30 # Frames para adicionar a próxima letra (aprox. 0.5 segundos a 60 FPS)
        self.name_spelled = False

        # Tela de agradecimento
        self.thank_you_message = ""

        self._initialize_libras_identifier()
        self._load_assets()

    def _initialize_libras_identifier(self):
        """Inicializa o identificador de sinais de Libras"""
        if self.libras_enabled:
            self.cap = cv2.VideoCapture(0) # Inicializa a webcam
            if not self.cap.isOpened():
                print("Erro: Não foi possível abrir a câmera 0. Verifique se ela está conectada e não está em uso.")
                self.libras_enabled = False
                return

            self.libras_sign_identifier = LibrasSignIdentifier()
            camera_size = (220, 165)
            camera_pos = (SCREEN_WIDTH - camera_size[0] - 10, 10)
            self.libras_display = LibrasDisplay(self.libras_sign_identifier, camera_pos, camera_size)
            print("Identificador de Libras inicializado com sucesso!")

    def _load_assets(self):
        """Carrega assets (cores de fundo como placeholder)"""
        self.backgrounds = {
            "office": (100, 100, 100),
            "cerrado": (34, 139, 34),
            "transition": (25, 25, 112),
        }

    def handle_input(self, event):
        """Entrada do usuário"""
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.VISUAL_NOVEL or self.state == GameState.PLATFORM or self.state == GameState.SPELL_NAME or self.state == GameState.THANK_YOU:
                    self.state = GameState.MENU
                elif self.state == GameState.MENU:
                    self.running = False

            elif event.key == pygame.K_c and self.libras_display:
                self.libras_display.toggle_visibility()

            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == GameState.MENU:
                    self.state = GameState.SPELL_NAME # Transição para a tela de soletração
                    self.player_name = "" # Resetar nome
                    self.last_recognized_letter = ""
                    self.name_spelled = False
                elif self.state == GameState.VISUAL_NOVEL:
                    self._advance_dialogue()
                elif self.state == GameState.SPELL_NAME:
                    # Ao pressionar ENTER/ESPAÇO na tela de soletração, avança para a tela de agradecimento
                    if self.player_name:
                        self.thank_you_message = f"Obrigado por jogar {self.player_name.upper()}!"
                        self.state = GameState.THANK_YOU
                    else:
                        # Se o nome estiver vazio, pode-se adicionar uma mensagem de erro ou ignorar
                        print("Nome não soletrado. Por favor, soletre seu nome.")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == GameState.MENU:
                self.state = GameState.SPELL_NAME # Transição para a tela de soletração
                self.player_name = "" # Resetar nome
                self.last_recognized_letter = ""
                self.name_spelled = False
            elif self.state == GameState.VISUAL_NOVEL:
                self._advance_dialogue()
            elif self.state == GameState.SPELL_NAME:
                # Ao clicar na tela de soletração, avança para a tela de agradecimento
                if self.player_name:
                    self.thank_you_message = f"Obrigado por jogar {self.player_name.upper()}!"
                    self.state = GameState.THANK_YOU
                else:
                    print("Nome não soletrado. Por favor, soletre seu nome.")

        if self.state == GameState.PLATFORM:
            self.platform_game.handle_input(event)

    def handle_libras_input(self):
        """Entrada por sinais de Libras"""
        if not self.libras_enabled or not self.libras_sign_identifier:
            return

        # Captura o frame da webcam e processa com o identificador de Libras
        ret, frame = self.cap.read()
        if not ret:
            print("Erro ao capturar frame da webcam.")
            return
        
        self.libras_sign_identifier.process_frame(frame)

        commands = self.libras_sign_identifier.get_game_commands()
        libras_letter = commands.get("libras_letter", "")

        # Lógica para soletração do nome
        if self.state == GameState.SPELL_NAME and not self.name_spelled:
            if libras_letter and libras_letter != "MODELO_NAO_CARREGADO" and libras_letter != "FORMATO_INCORRETO":
                if libras_letter != self.last_recognized_letter:
                    self.last_recognized_letter = libras_letter
                    self.letter_add_timer = self.LETTER_ADD_DELAY # Reinicia o timer
                elif self.letter_add_timer <= 0:
                    self.player_name += libras_letter
                    self.letter_add_timer = self.LETTER_ADD_DELAY # Reinicia o timer
            
            # A confirmação agora é feita apenas por teclado (ESPAÇO/ENTER)
            # O gesto de 'OK' foi removido do LibrasSignIdentifier e, portanto, não é mais verificado aqui.

    def _start_story(self):
        self.story_index = 0
        self._load_current_dialogue()

    def _load_current_dialogue(self):
        if self.story_index < len(self.story_script):
            current = self.story_script[self.story_index]
            self.dialogue_speaker = current["speaker"]
            self.dialogue_text = current["text"]
            self.dialogue_char_index = 0
            self.dialogue_typing = True

    def _advance_dialogue(self):
        if self.dialogue_typing:
            self.dialogue_char_index = len(self.dialogue_text)
            self.dialogue_typing = False
        else:
            self.story_index += 1
            if self.story_index < len(self.story_script):
                self._load_current_dialogue()
            else:
                self.state = GameState.PLATFORM

    def update(self):
        if self.state == GameState.VISUAL_NOVEL:
            if self.dialogue_typing:
                self.dialogue_char_index += self.typing_speed
                if self.dialogue_char_index >= len(self.dialogue_text):
                    self.dialogue_char_index = len(self.dialogue_text)
                    self.dialogue_typing = False
        elif self.state == GameState.PLATFORM:
            self.platform_game.update()
        elif self.state == GameState.SPELL_NAME:
            if self.letter_add_timer > 0:
                self.letter_add_timer -= 1

        self.handle_libras_input()

    def draw_menu(self):
        SCREEN.fill(BLACK)
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Candango: Neural Ascension", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        SCREEN.blit(title_text, title_rect)

        subtitle_text = FONT_NAME.render("Uma Jornada Épica de Inclusão e Heroísmo", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        SCREEN.blit(subtitle_text, subtitle_rect)

        instructions = [
            "Clique ou use ESPAÇO/ENTER para começar",
            "ESC - Menu/Sair",
            "C (teclado) - Mostrar/ocultar câmera",
            "",
            "Reconhecimento de Libras: (Veja a câmera para a letra)"
        ]

        y_offset = 350
        for instruction in instructions:
            text = FONT_UI.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            SCREEN.blit(text, text_rect)
            y_offset += 25

        status_text = FONT_UI.render("✓ Libras Ativo" if self.libras_enabled else "✗ Libras Inativo", True, GREEN if self.libras_enabled else RED)
        SCREEN.blit(status_text, (10, SCREEN_HEIGHT - 30))

        # Exibir a letra de Libras reconhecida no menu
        if self.libras_enabled and self.libras_sign_identifier:
            commands = self.libras_sign_identifier.get_game_commands()
            libras_letter = commands.get("libras_letter", "")
            if libras_letter:
                libras_text = FONT_UI.render(f"Libras: {libras_letter}", True, YELLOW)
                SCREEN.blit(libras_text, (SCREEN_WIDTH // 2 - libras_text.get_width() // 2, y_offset + 25))

    def draw_spell_name_screen(self):
        SCREEN.fill(BLACK)

        title_text = FONT_LARGE.render("Soletrando seu Nome em Libras", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        SCREEN.blit(title_text, title_rect)

        instructions = [
            "Use os gestos de Libras para soletrar seu nome.",
            "Mantenha o gesto da letra por um momento para que ela seja adicionada.",
            "Pressione ESPAÇO/ENTER para confirmar seu nome."
        ]

        y_offset = 200
        for instruction in instructions:
            text = FONT_UI.render(instruction, True, GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            SCREEN.blit(text, text_rect)
            y_offset += 30

        # Nome soletrado em tempo real
        name_display_text = FONT_LARGE.render(self.player_name.upper(), True, YELLOW)
        name_display_rect = name_display_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(name_display_text, name_display_rect)

        # Letra de Libras reconhecida atualmente
        if self.libras_enabled and self.libras_sign_identifier:
            commands = self.libras_sign_identifier.get_game_commands()
            libras_letter = commands.get("libras_letter", "")
            if libras_letter and libras_letter not in ["MODELO_NAO_CARREGADO", "FORMATO_INCORRETO"]:
                current_letter_text = FONT_NAME.render(f"Letra atual: {libras_letter}", True, GREEN)
                current_letter_rect = current_letter_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
                SCREEN.blit(current_letter_text, current_letter_rect)
            else:
                current_letter_text = FONT_NAME.render("Aguardando gesto de Libras...", True, RED)
                current_letter_rect = current_letter_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
                SCREEN.blit(current_letter_text, current_letter_rect)

    def draw_thank_you_screen(self):
        SCREEN.fill(BLACK)
        thank_you_text = FONT_LARGE.render(self.thank_you_message, True, WHITE)
        thank_you_rect = thank_you_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(thank_you_text, thank_you_rect)

        instructions_text = FONT_UI.render("Pressione ESC para voltar ao menu.", True, GRAY)
        instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        SCREEN.blit(instructions_text, instructions_rect)

    def draw_visual_novel(self):
        # Background
        if self.story_index < len(self.story_script):
            bg_key = self.story_script[self.story_index].get("background", "office")
            bg_color = self.backgrounds.get(bg_key, BLACK)
        else:
            bg_color = BLACK
        SCREEN.fill(bg_color)

        # Área de diálogo
        dialogue_rect = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150)
        pygame.draw.rect(SCREEN, GRAY, dialogue_rect)
        pygame.draw.rect(SCREEN, WHITE, dialogue_rect, 3)

        # Nome do falante
        if self.dialogue_speaker:
            speaker_text = FONT_NAME.render(self.dialogue_speaker, True, YELLOW)
            SCREEN.blit(speaker_text, (dialogue_rect.x + 20, dialogue_rect.y + 10))

        # Texto com "efeito digitação"
        displayed_text = self.dialogue_text[:self.dialogue_char_index]
        words = displayed_text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test = current_line + word + " "
            if FONT_DIALOGUE.size(test)[0] < dialogue_rect.width - 40:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        y = dialogue_rect.y + 50
        for line in lines:
            if y + FONT_DIALOGUE.get_linesize() < dialogue_rect.bottom - 10:
                text = FONT_DIALOGUE.render(line, True, WHITE)
                SCREEN.blit(text, (dialogue_rect.x + 20, y))
                y += FONT_DIALOGUE.get_linesize()

        if not self.dialogue_typing:
            indicator = FONT_UI.render("▼ Clique/tecla para continuar", True, YELLOW)
            indicator_rect = indicator.get_rect(center=(SCREEN_WIDTH // 2, dialogue_rect.bottom + 20))
            SCREEN.blit(indicator, indicator_rect)

        progress = f"Cena {self.story_index + 1} de {len(self.story_script)}"
        SCREEN.blit(FONT_UI.render(progress, True, WHITE), (10, 10))

        if self.libras_enabled and self.libras_sign_identifier:
            commands = self.libras_sign_identifier.get_game_commands()
            libras_letter = commands.get("libras_letter", "")

            y_offset_info = 40
            
            if libras_letter and libras_letter != "MODELO_NAO_CARREGADO" and libras_letter != "FORMATO_INCORRETO":
                ltext = f"Libras: {libras_letter}"
                SCREEN.blit(FONT_UI.render(ltext, True, YELLOW), (10, y_offset_info))

    def draw_platform_game(self):
        self.platform_game.draw()

    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.SPELL_NAME:
            self.draw_spell_name_screen()
        elif self.state == GameState.VISUAL_NOVEL:
            self.draw_visual_novel()
        elif self.state == GameState.PLATFORM:
            self.draw_platform_game()
        elif self.state == GameState.THANK_YOU:
            self.draw_thank_you_screen()

        if self.libras_display:
            self.libras_display.draw(SCREEN)

        pygame.display.flip()

    def run(self):
        print("Iniciando Candango: Neural Ascension...")
        print("Controles: Mouse/ESPAÇO/ENTER para avançar | ESC menu/sair | C alterna câmera")
        print("Libras: O reconhecimento de letras de Libras aparecerá na tela da câmera e no canto superior esquerdo.")

        while self.running:
            for event in pygame.event.get():
                self.handle_input(event)
            self.update()
            self.draw()
            self.clock.tick(60)

        if self.libras_sign_identifier:
            self.libras_sign_identifier.stop()
        if self.cap:
            self.cap.release()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CandangoGame()
    game.run()



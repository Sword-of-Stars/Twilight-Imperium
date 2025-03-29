import pygame

class PlayerTracker:
    def __init__(self, players):
        self.players = players  # List of Player objects

        assert len(self.players) >= 3, "Must have at least 3 players"

        self.current_player = players[0]  # Start by showing the first player

        self.width, self.height = 540, 330
        self.disp = pygame.Surface((self.width, self.height))
        self.rect = self.disp.get_rect(topleft=(1040, 540))
        self.background_color = (17, 21, 36)
        self.text_color = (255, 255, 255)
        self.scrollbar_color = (50, 50, 50)
        self.scrollbar_handle_color = (100, 100, 100)

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)

        # Scrolling
        self.scroll_offset = 0
        self.line_height = 30
        self.visible_lines = (self.height - 80) // self.line_height  # Adjusted for title & tabs
        self.max_scroll = 0  # Updates dynamically

        # Tabs
        self.tab_height = 40
        self.tab_width = self.width // max(1, len(self.players))  # Divide tabs equally
        self.tab_rects = [
            pygame.Rect(i * self.tab_width, 0, self.tab_width, self.tab_height) 
            for i in range(len(self.players))
        ]

    def update(self):
        """Update the display surface with the current player's information."""
        self.disp.fill(self.background_color)

        # Render tabs
        for i, player in enumerate(self.players):
            color = (100, 100, 200) if player == self.current_player else (50, 50, 100)
            pygame.draw.rect(self.disp, color, self.tab_rects[i])
            name_surf = self.font.render(player.name, True, (255, 255, 255))
            self.disp.blit(name_surf, (self.tab_rects[i].x + 10, 10))

        # Render player information
        player_info_lines = self.current_player.info.split("\n")
        self.max_scroll = max(0, len(player_info_lines) - self.visible_lines)

        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_lines, len(player_info_lines))
        
        y_offset = self.tab_height + 10  # Below tabs
        for i, line in enumerate(player_info_lines[start_idx:end_idx]):
            text_surf = self.font.render(line, True, self.text_color)
            self.disp.blit(text_surf, (10, y_offset + i * self.line_height))

        # Draw scrollbar if needed
        if len(player_info_lines) > self.visible_lines:
            self._draw_scrollbar()

    def _draw_scrollbar(self):
        """Draw the scrollbar on the display surface."""
        pygame.draw.rect(self.disp, self.scrollbar_color, (self.width - 10, 0, 10, self.height))

        handle_height = max(30, (self.visible_lines / len(self.current_player.info.split("\n"))) * self.height)
        handle_pos = (self.scroll_offset / self.max_scroll) * (self.height - handle_height)

        pygame.draw.rect(self.disp, self.scrollbar_handle_color, 
                         (self.width - 10, handle_pos, 10, handle_height))

    def handle_mouse_click(self, pos):
        """Check if a tab is clicked and switch players."""
        local_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        for i, tab_rect in enumerate(self.tab_rects):
            if tab_rect.collidepoint(local_pos):
                self.current_player = self.players[i]
                self.scroll_offset = 0  # Reset scroll when switching players
                break

    def handle_mouse_wheel(self, pos, event):
        """Handle mouse wheel scrolling if hovering over the tracker."""
        if self.is_mouse_over(pos):
            self.scroll(-event.y)

    def is_mouse_over(self, mouse_pos):
        """Check if the mouse is over the tracker."""
        return self.rect.collidepoint(mouse_pos)

    def scroll(self, direction):
        """Scroll up (-1) or down (+1)."""
        self.scroll_offset = max(0, min(self.scroll_offset + direction, self.max_scroll))

    def draw(self, screen):
        """Draw the player tracker on the main screen."""
        screen.blit(self.disp, self.rect.topleft)
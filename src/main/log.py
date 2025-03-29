import pygame

class EventLog:
    def __init__(self):
        self.events = []
        self.width, self.height = 540, 500
        self.disp = pygame.Surface((self.width, self.height))
        self.rect = self.disp.get_rect(topleft=(1040, 20))
        self.background_color = (17, 21, 36)
        self.text_color = (255, 255, 255)
        self.scrollbar_color = (50, 50, 50)
        self.scrollbar_handle_color = (100, 100, 100)
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)

        
       # Scrolling
        self.scroll_offset = 0
        self.line_height = 30
        self.visible_lines = (self.height - 40) // self.line_height  # Adjusted for title
        self.max_scroll = 0  # Updates dynamically
        
        # Scrollbar dimensions
        self.scrollbar_width = 10
        self.scrollbar_rect = pygame.Rect(
            self.width - self.scrollbar_width, 
            0, 
            self.scrollbar_width, 
            self.height
        )

    def clear(self):
        self.events.clear()
    
    def add_event(self, text):
        """Add an event to the log."""
        self.events.append(text)
        self.max_scroll = max(0, len(self.events) - self.visible_lines)

    def update(self):
        """Update the display surface."""
        self.disp.fill(self.background_color)

        # Render the title
        title_surf = self.title_font.render("Event Log", True, (255, 215, 0))  # Gold color
        self.disp.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 5))

        # Display event logs below the title
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_lines, len(self.events))
        for i, event in enumerate(self.events[start_idx:end_idx]):
            text_surf = self.font.render(event, True, self.text_color)
            self.disp.blit(text_surf, (10, i * self.line_height + 40))  # Adjusted for title space
        
        # Draw scrollbar if needed
        if len(self.events) > self.visible_lines:
            self._draw_scrollbar()
    
    def _draw_scrollbar(self):
        """Draw the scrollbar on the display surface."""
        # Draw scrollbar background
        pygame.draw.rect(self.disp, self.scrollbar_color, self.scrollbar_rect)
        
        # Calculate scrollbar handle size and position
        handle_height = max(30, (self.visible_lines / len(self.events)) * self.height)
        handle_pos = (self.scroll_offset / self.max_scroll) * (self.height - handle_height)
        
        # Draw scrollbar handle
        handle_rect = pygame.Rect(
            self.width - self.scrollbar_width, 
            handle_pos, 
            self.scrollbar_width, 
            handle_height
        )
        pygame.draw.rect(self.disp, self.scrollbar_handle_color, handle_rect)

    def scroll(self, direction):
        """Scroll up (-1) or down (+1)."""
        self.scroll_offset = max(0, min(self.scroll_offset + direction, self.max_scroll))

    def handle_mouse_wheel(self, pos, event):
        """Handle mouse wheel scrolling."""
        if self.is_mouse_over(pos):
            # Scroll up or down based on mouse wheel direction
            self.scroll(-event.y)

    def is_mouse_over(self, mouse_pos):
        """Check if mouse is over the event log area."""
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Draw the event log on the main screen."""
        screen.blit(self.disp, self.rect.topleft)
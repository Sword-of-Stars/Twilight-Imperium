import os, sys
from ti4_model import TwilightImperiumRL
from datetime import datetime
import pygame
from player import Player
from simulation import Simulation
from units import Carrier, Destroyer, GroundForce, SpaceDock
import random
import json

random.seed(42)

class Trainer:
    def __init__(self, num_players=3, episodes=1000, 
                 headless=True, models_dir="models", logs_dir="logs"):
        self.num_players = num_players
        self.episodes = episodes
        self.headless = headless
        self.models_dir = models_dir
        self.logs_dir = logs_dir
        
        # Create timestamp for this training run
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create directories for this training run
        self.run_dir = os.path.join(logs_dir, f"run_{self.timestamp}")
        self.run_models_dir = os.path.join(models_dir, f"run_{self.timestamp}")
        self.stats_dir = os.path.join(self.run_dir, "stats")
        self.viz_dir = os.path.join(self.run_dir, "visualizations")
        
        os.makedirs(self.run_dir, exist_ok=True)
        os.makedirs(self.run_models_dir, exist_ok=True)
        os.makedirs(self.stats_dir, exist_ok=True)
        os.makedirs(self.viz_dir, exist_ok=True)
        
        # Training stats tracking
        self.training_stats = {
            "episodes": [],
            "winners": [],
            "victory_rounds": [],
            "player_final_points": [],
            "earliest_victory": None,
            "avg_victory_round": 0,
            "epsilon_history": []
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(logs_dir, f"training_{timestamp}.log")

        # Redirect all print() calls to this log file
        sys.stdout = open(self.log_file, 'a')
        print(f"Logging started at {timestamp}\n{'='*40}\n")
        
        # Initialize models for each player
        self.models = [
            TwilightImperiumRL(
                input_feature_dim=19,  # Adjust as needed
                hidden_dims=[64, 128, 64],
                gamma=0.99,
                epsilon=1.0,  # Start with full exploration
                epsilon_decay=0.995,
                epsilon_min=0.1,
                learning_rate=0.001
            )
            for _ in range(num_players)
        ]
    
    def _log(self, message, episode=None):
        """Log message to episode file and console"""
        print(message)
        
        # Determine which log file to write to
        if episode is not None:
            log_file = os.path.join(self.run_dir, f"episode_{episode:04d}.log")
        else:
            log_file = os.path.join(self.run_dir, "training.log")
            
        with open(log_file, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")

    def save_stats(self, episode, players):
        """Save player stats for this episode"""
        episode_stats = {
            f"player_{i}": {
                "name": player.name,
                "final_points": player.points,
            }
            for i, player in enumerate(players)
        }
        
        # Save to JSON
        stats_file = os.path.join(self.stats_dir, f"episode_{episode:04d}_stats.json")
        with open(stats_file, 'w') as f:
            json.dump(episode_stats, f, indent=2)
    
    def initialize_pygame(self):
        """Set up pygame if not headless"""
        if not self.headless:
            pygame.init()
            screen = pygame.display.set_mode((1280, 720))
            clock = pygame.time.Clock()
            return screen, clock
        else:
            # Headless mode
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.init()
            screen = pygame.display.set_mode((1, 1))
            clock = pygame.time.Clock()
            return screen, clock
    
    def create_rl_player(self, name, _id, starting_system, starting_units, model, disposition):
        """Create an RL player with the given model"""
        return Player(name, _id, starting_system, starting_units, model, disposition=disposition)
    
    def save_models(self, episode):
        """Save all models"""
        for i, model in enumerate(self.models):
            model_path = os.path.join(self.models_dir, f"player_{i}_episode_{episode}.h5")
            model.model.save_weights(model_path)
    
    def train(self):
        """Run training loop"""
        for episode in range(self.episodes):
            self._log(f"Starting episode {episode+1}/{self.episodes}")
            
            # Initialize pygame
            screen, clock = self.initialize_pygame()
            
            # Create simulation without initializing players
            sim = Simulation(screen, clock)
            
            # Replace default players with RL players
            sim.players = []
            starting_systems = random.sample(sim.game_map.get_start_tiles(), len(sim.game_map.get_start_tiles()))
            dispositions = ["balanced", "defensive", "despot"]
            
            for i in range(self.num_players):
                # Default units for each player
                starting_units = [
                    Carrier(), Carrier(),
                    GroundForce(), GroundForce(), GroundForce(), GroundForce(),
                    Destroyer(), SpaceDock()
                ]
                
                # Create RL player with corresponding model
                rl_player = self.create_rl_player(
                    f"RLPlayer_{i} ({dispositions[i]})",
                    _id=i,
                    starting_system=starting_systems[i],
                    starting_units=starting_units,
                    model=self.models[i],
                    disposition=dispositions[i]
                )
                
                sim.players.append(rl_player)
            
            # Reset player tracker
            sim.player_tracker = sim.player_tracker.__class__(sim.players)
            
            # Run game for max rounds or until completion
            max_rounds = 10
            sim.game_round = 1
            
            while not sim.game_over and sim.game_round <= max_rounds:
                if sim.phase == "strategy":
                    self._log(f"[Episode {episode+1}] Round {sim.game_round}")
                    for player in sim.players:
                        self._log(f"{player.name} has {player.points} points")
                    
                    sim.strategy_phase()
                elif sim.phase == "action":
                    sim.take_turn()
                elif sim.phase == "status":
                    sim.status_phase()
                    sim.game_round += 1

                # Check for game over
                victors = [p for p in sim.players if p.points >= 50]
                if victors:
                    victor = max(victors, key=lambda x: x.points)
                    self._log(f"[Episode {episode+1}] {victor.name} won in round {sim.game_round}!")
                    sim.game_over = True
            
            # If we reached max rounds without a victor
            if not sim.game_over:
                # Find player with highest points
                best_player = max(sim.players, key=lambda x: x.points)
                self._log(f"[Episode {episode+1}] No winner after {max_rounds} rounds. {best_player.name} leads with {best_player.points} points.")
            
            # Log final points
            self._log(f"[Episode {episode+1}] Final points:")
            for player in sim.players:
                self._log(f"{player.name}: {player.points}")
            
            # Train models on collected experiences
            for model in self.models:
                for _ in range(10):  # Train multiple times on memory
                    model.replay()
            
            # Decay exploration rates
            for model in self.models:
                if model.epsilon > model.epsilon_min:
                    model.epsilon *= model.epsilon_decay
                self._log(f"Model epsilon: {model.epsilon:.4f}")
            
            # Save models every 50 episodes
            if (episode + 1) % 50 == 0:
                self.save_models(episode + 1)
                
            # Update target networks every 10 episodes
            if (episode + 1) % 10 == 0:
                for model in self.models:
                    model.update_target_model()
            
            # Clean up pygame
            pygame.quit()
            
        # Save final models
        self.save_models("final")
        self._log("Training complete!")

def main():
    """Main function to run training"""
    trainer = Trainer(
        num_players=3,
        episodes=500,
        headless=True,  # Set to False to visualize training
        models_dir="models",
        logs_dir="logs"
    )
    
    trainer.train()
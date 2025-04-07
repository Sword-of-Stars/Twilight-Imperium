import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Lambda
from tensorflow.keras import layers, Model, Input
from tensorflow.keras.optimizers import Adam
import random
from collections import deque

class TwilightImperiumRL:
    def __init__(self, input_feature_dim=19, hidden_dims=[64, 128, 64], 
                 gamma=0.99, epsilon=0.0, epsilon_decay=0.995, epsilon_min=0.01,
                 learning_rate=0.001, memory_size=10000, batch_size=32):
        # RL parameters
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        
        # Model parameters
        self.input_feature_dim = input_feature_dim
        self.hidden_dims = hidden_dims
        
        # Action space size (number of possible actions)
        self.action_size = self._get_action_space_size()
        
        # Replay memory
        self.memory = deque(maxlen=memory_size)
        
        # Build model
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        
    def _get_action_space_size(self):
        # Define the number of possible actions in the game
        # This will depend on your action representation
        # Example: tactical actions, strategic actions, etc.
        return len(["attack", "reinforce", "produce"])  # Placeholder - adjust based on your game
        
    def _build_model(self):
        # GCN inputs
        node_features_input = Input(shape=(None, self.input_feature_dim), name='node_features')
        adjacency_input = Input(shape=(None, None), name='adjacency')
        
        # Process board state with GCN
        x = node_features_input
        for i, dim in enumerate(self.hidden_dims):
            x = GraphConvLayer(dim, name=f'gcn_{i}')([x, adjacency_input])
            x = layers.Dropout(0.2)(x)
            if i < len(self.hidden_dims) - 1:
                x = layers.BatchNormalization()(x)
        
        # Attention-based pooling
        attention_scores = layers.Dense(1, activation='tanh')(x)  # Shape: (batch_size, num_nodes, 1)
        attention_weights = layers.Softmax(axis=1)(attention_scores)  # Apply softmax along the node axis
        board_embedding = Lambda(lambda inputs: tf.reduce_sum(inputs[0] * inputs[1], axis=1))([x, attention_weights])
        
        # Player-specific features input
        player_input = Input(shape=(20,), name='player_features')  # Adjust size as needed
        
        # Combine board representation with player features
        combined = layers.Concatenate()([board_embedding, player_input])
        
        # Policy (action probabilities) and value (state evaluation) heads
        x = layers.Dense(128, activation='relu')(combined)
        x = layers.Dropout(0.3)(x)
        
        # Policy head (action selection)
        policy_head = layers.Dense(3, activation='relu')(x)
        policy_output = layers.Dense(self.action_size, activation='softmax', name='policy')(policy_head)
        
        # Value head (state evaluation)
        value_head = layers.Dense(64, activation='relu')(x)
        value_output = layers.Dense(1, activation='tanh', name='value')(value_head)
        
        # Create model
        model = Model(
            inputs=[node_features_input, adjacency_input, player_input],
            outputs=[policy_output, value_output]
        )
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss={'policy': 'categorical_crossentropy', 'value': 'mse'},
            metrics={'policy': 'accuracy', 'value': 'mae'}
        )
        
        #print(model.summary())
    
        return model
    
    def update_target_model(self):
        """Update the target model to match the primary model"""
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def choose_action(self, state, valid_actions=["reinforce", "produce", "attack"]):
        """
        Choose an action using epsilon-greedy policy
        
        Args:
            state: Tuple of (node_features, adjacency_matrix, player_features)
            valid_actions: List of valid action indices
            
        Returns:
            action: Selected action index
        """
        if np.random.rand() <= self.epsilon:
            # Exploration: random action
            return random.sample(valid_actions, len(valid_actions))
        
        # Exploitation: use model to predict best action
        node_features, adjacency, player_features = state
        
        # Preprocess and reshape for model input
        node_features = np.expand_dims(node_features, axis=0)
        adjacency = np.expand_dims(adjacency, axis=0)
        player_features = np.expand_dims(player_features, axis=0)
        
        # Get action probabilities
        action_probs, _ = self.model.predict([node_features, adjacency, player_features],
                                             verbose=0)

        # actions in the following order:
        # "strategic", "reinforce", "produce", "attack"

        # Filter to only valid actions
        valid_probs = [(i, action_probs[0][i]) for i, _ in enumerate(valid_actions)]
        valid_probs.sort(key=lambda x: x[1], reverse=True)

        
        # Return the action with highest probability
        return [valid_actions[valid_probs[i][0]] for i in range(len(valid_actions))]
    
    def replay(self):
        """Train the model on experiences from replay memory"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample a batch of experiences
        minibatch = random.sample(self.memory, self.batch_size)
        
        # Prepare batch data
        node_features = []
        adjacencies = []
        player_features = []
        targets_policy = []
        targets_value = []
        
        for state, action, reward, next_state, done in minibatch:
            # Unpack state components
            nf, adj, pf = state
            
            # Preprocess for model input
            nf = np.expand_dims(nf, axis=0)
            adj = np.expand_dims(adj, axis=0)
            pf = np.expand_dims(pf, axis=0)
            
            # Get current predictions
            policy_pred, value_pred = self.model.predict([nf, adj, pf])
            
            # Get target value
            if done:
                target_value = reward
            else:
                next_nf, next_adj, next_pf = next_state
                next_nf = np.expand_dims(next_nf, axis=0)
                next_adj = np.expand_dims(next_adj, axis=0)
                next_pf = np.expand_dims(next_pf, axis=0)
                
                _, next_value = self.target_model.predict([next_nf, next_adj, next_pf])
                target_value = reward + self.gamma * next_value[0][0]
            
            # Create target policy (one-hot with actual action)
            target_policy = policy_pred[0].copy()
            target_policy[action] = 1.0  # Set chosen action to 1.0
            
            # Store batch data
            node_features.append(nf[0])
            adjacencies.append(adj[0])
            player_features.append(pf[0])
            targets_policy.append(target_policy)
            targets_value.append([target_value])
        
        # Convert lists to arrays
        node_features = np.array(node_features)
        adjacencies = np.array(adjacencies)
        player_features = np.array(player_features)
        targets_policy = np.array(targets_policy)
        targets_value = np.array(targets_value)
        
        # Train model
        self.model.fit(
            [node_features, adjacencies, player_features],
            {'policy': targets_policy, 'value': targets_value},
            epochs=1,
            batch_size=self.batch_size,
            verbose=0
        )
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
    def preprocess_adjacency(self, adjacency_matrix):
        """
        Normalize the adjacency matrix for GCN processing
        """
        # Add self-loops: A_hat = A + I
        adj_hat = adjacency_matrix + np.eye(adjacency_matrix.shape[0])
        
        # Compute degree matrix
        degrees = np.sum(adj_hat, axis=1)
        
        # Compute D^(-1/2)
        d_inv_sqrt = np.power(degrees, -0.5)
        d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.0
        d_mat_inv_sqrt = np.diag(d_inv_sqrt)
        
        # Compute normalized adjacency: D^(-1/2) * A_hat * D^(-1/2)
        return d_mat_inv_sqrt @ adj_hat @ d_mat_inv_sqrt


class GraphConvLayer(layers.Layer):
    """Graph Convolutional Layer"""
    def __init__(self, units, activation='relu', **kwargs):
        super(GraphConvLayer, self).__init__(**kwargs)
        self.units = units
        self.activation = tf.keras.activations.get(activation)
        
    def build(self, input_shape):
        node_features_shape = input_shape[0]
        self.kernel = self.add_weight(
            shape=(node_features_shape[-1], self.units),
            initializer='glorot_uniform',
            name='kernel')
        self.bias = self.add_weight(
            shape=(self.units,),
            initializer='zeros',
            name='bias')
        self.built = True
        
    def call(self, inputs):
        node_features, normalized_adjacency = inputs
        support = tf.matmul(node_features, self.kernel)
        output = tf.matmul(tf.cast(normalized_adjacency, tf.float32), support)
        output = output + self.bias
        if self.activation is not None:
            output = self.activation(output)
        return output
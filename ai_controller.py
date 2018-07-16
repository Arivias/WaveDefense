import tensorflow as tf
from inputmanagers import DummyInputManager


class AINetwork:
    def __init__(self, number_eyes, number_actions=7, hidden_size=16, activation=tf.nn.relu):
        self.number_actions = number_actions
        self.number_eyes = number_eyes
        self.angular_velocity = tf.placeholder(tf.float32, [None])
        self.forward_velocity = tf.placeholder(tf.float32, [None])
        self.strafe_velocity = tf.placeholder(tf.float32, [None])
        self.health = tf.placeholder(tf.float32, [None])
        self.enemy_distances = tf.placeholder(tf.float32, [None, number_eyes])
        self.projectile_distances = tf.placeholder(tf.float32, [None, number_eyes])
        inputs = tf.concat([
            self.angular_velocity, self.forward_velocity, self.strafe_velocity,
            self.health, self.enemy_distances, self.projectile_distances
        ], axis=1)
        hidden_layer_1 = tf.layers.dense(inputs, hidden_size, activation)
        self.value = tf.layers.dense(inputs, 1)
        self.output = tf.layers.dense(hidden_layer_1, number_actions, tf.nn.tanh)


class AINetworkTrainer:
    def __init__(self, ai_network, value_loss_weight=0.5, policy_loss_weight=1,
                 entropy_weight=0.01, optimizer=tf.train.AdamOptimizer(learning_rate=0.001)):
        self.value_target = tf.placeholder(tf.float32, [None])
        self.advantages = tf.placeholder(tf.float32, [None])
        self.chosen_actions = tf.placeholder(tf.float32, [None, ai_network.number_actions])
        responsible_action = tf.multiply(ai_network.output, self.chosen_actions)
        responsible_action = tf.reduce_sum(responsible_action, [1])
        action_loss = -tf.reduce_sum(responsible_action * self.advantages)
        entropy = tf.multiply(ai_network.output, tf.log(ai_network.output))
        entropy = -tf.reduce_sum(entropy)
        value_loss = tf.losses.mean_squared_error(self.value_target, ai_network.value)
        self.loss = (value_loss * value_loss_weight + action_loss * policy_loss_weight - entropy * entropy_weight)
        self.train = optimizer.minimize(self.loss)


class AIController(DummyInputManager):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.number_eyes = 10
        self.ai_network = AINetwork(number_eyes=self.number_eyes)
        self.ai_trainer = AINetworkTrainer(self.ai_network)
        self.sess = tf.Session()

    def getInputArray(self, deltaTime, state, ship):
        #Get output for our action (not training)
        feed_dict = {
            self.ai_network.health: [100],
            self.ai_network.angular_velocity: [30],
            self.ai_network.forward_velocity: [0],
            self.ai_network.strafe_velocity: [0],
            self.ai_network.enemy_distances: [i for i in range(self.number_eyes)],
            self.ai_network.projectile_distances: [i for i in range(self.number_eyes)],
        }

        actions = self.sess.run(self.ai_network.output, feed_dict)
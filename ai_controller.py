import tensorflow as tf
from inputmanagers import DummyInputManager
import math
import wdcore


class AINetwork:
    def __init__(self, number_eyes, number_actions=7, hidden_size=16, activation=tf.nn.relu):
        self.number_actions = number_actions
        self.number_eyes = number_eyes
        self.angular_velocity = tf.placeholder(tf.float32, [None, 1])
        self.forward_velocity = tf.placeholder(tf.float32, [None, 1])
        self.strafe_velocity = tf.placeholder(tf.float32, [None, 1])
        self.health = tf.placeholder(tf.float32, [None, 1])
        self.enemy_distances = tf.placeholder(tf.float32, [None, number_eyes])
        self.projectile_distances = tf.placeholder(tf.float32, [None, number_eyes])
        eyes = tf.concat([self.enemy_distances, self.projectile_distances], axis=1)
        print('Eyes shape:', eyes.shape)
        inputs = tf.concat([
            self.angular_velocity, self.forward_velocity, self.strafe_velocity,
            self.health, eyes
        ], axis=1)
        print('Inputs:',inputs.shape)
        hidden_layer_1 = tf.layers.dense(inputs, hidden_size, activation)
        self.value = tf.layers.dense(inputs, 1)
        self.output = tf.layers.dense(hidden_layer_1, number_actions, tf.nn.tanh)


class AINetworkTrainer:
    def __init__(self, ai_network, value_loss_weight=0.5, policy_loss_weight=1,
                 entropy_weight=0.01, optimizer=tf.train.AdamOptimizer(learning_rate=0.001)):
        self.value_target = tf.placeholder(tf.float32, [None, 1])
        self.advantages = tf.placeholder(tf.float32, [None, 1])
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
        self.sess.run(tf.global_variables_initializer())

    def getInputArray(self, deltaTime, state, ship):
        #Get output for our action (not training)

        inputs_enemies=[]
        inputs_projectiles=[]
        angSeparation=math.pi*2
        angSeparation/=self.number_eyes
        eyeAng=ship.rig.rot
        rayLength=state.world.radius
        for i in range(self.number_eyes):######Look through eyes
            orayEnd=[rayLength,0]
            rayEnd=[0,0]
            rayEnd[0]=orayEnd[0]*math.cos(eyeAng)-orayEnd[1]*math.sin(eyeAng)
            rayEnd[1]=orayEnd[0]*math.sin(eyeAng)+orayEnd[1]*math.cos(eyeAng)
            rayEnd=[rayEnd[0]+ship.rig.x,rayEnd[1]+ship.rig.y]
            closestTarget=ship.world.radius*2
            for s in ship.world.shipList:#search ships
                if s.team!=ship.team:
                    d=s.rig.raycast(((ship.rig.x,ship.rig.y),(rayEnd[0],rayEnd[1])))
                    if d!=None:
                        if d<closestTarget:
                            closestTarget=d
            inputs_enemies.append(rayLength-closestTarget)
            closestTarget=ship.world.radius*2
            for obj in ship.world.tickQueue:#search projectiles
                if isinstance(obj,wdcore.Projectile):
                    d=obj.rig.raycast(((ship.rig.x,ship.rig.y),(rayEnd[0],rayEnd[1])))
                    if d!=None:
                        if d<closestTarget:
                            closestTarget=d
            inputs_projectiles.append(rayLength-closestTarget)
            eyeAng+=angSeparation

        ###other inputs
        #forward and strafe
        i_angle=math.atan2(ship.speed[1],ship.speed[0])+math.pi/2
        i_angle=ship.rig.rot-i_angle
        i_xy=[0,0]
        i_xy[0]=ship.speed[0]*math.cos(i_angle)-ship.speed[1]*math.sin(i_angle)
        i_xy[1]=ship.speed[0]*math.sin(i_angle)+ship.speed[1]*math.cos(i_angle)
        
        feed_dict = {
            self.ai_network.health: [[ship.currentHealth/ship.data[0]]],
            self.ai_network.angular_velocity: [[ship.speed[2]]],
            self.ai_network.forward_velocity: [[i_xy[1]]],
            self.ai_network.strafe_velocity: [[i_xy[0]]],
            self.ai_network.enemy_distances: [inputs_enemies],
            self.ai_network.projectile_distances: [inputs_projectiles],
        }

        outputs = self.sess.run(self.ai_network.output, feed_dict).tolist()[0]
        newMovement=[0,0]
        newMovement[0]=outputs[0]*math.cos(-1*i_angle)-outputs[1]*math.sin(-1*i_angle)
        newMovement[1]=outputs[0]*math.sin(-1*i_angle)+outputs[1]*math.cos(-1*i_angle)
        outputs[0]=newMovement[0]
        outputs[1]=newMovement[1]

        return outputs

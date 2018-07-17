import tensorflow as tf
from inputmanagers import DummyInputManager
import math
import wdcore


class AINetwork:
    globalNet=None

    def __init__(self, scope, number_eyes, number_actions=7, hidden_size=16, activation=tf.nn.relu):
        if not AINetwork.globalNet and scope!='global':
            AINetwork.globalNet = AINetwork("global",number_eyes)

        with tf.variable_scope(scope):
            self.number_actions = number_actions
            self.number_eyes = number_eyes
            self.angular_velocity = tf.placeholder(tf.float32, [None, 1])
            self.forward_velocity = tf.placeholder(tf.float32, [None, 1])
            self.strafe_velocity = tf.placeholder(tf.float32, [None, 1])
            self.health = tf.placeholder(tf.float32, [None, 1])
            self.enemy_distances = tf.placeholder(tf.float32, [None, number_eyes])
            self.projectile_distances = tf.placeholder(tf.float32, [None, number_eyes])
            eyes = tf.concat([self.enemy_distances, self.projectile_distances], axis=1)
            inputs = tf.concat([
                self.angular_velocity, self.forward_velocity, self.strafe_velocity,
                self.health, eyes
            ], axis=1)
            hidden_layer_1 = tf.layers.dense(inputs, hidden_size, activation)
            self.value = tf.layers.dense(inputs, 1)
            self.output = tf.layers.dense(hidden_layer_1, number_actions, tf.nn.tanh)


class AINetworkTrainer:
    def __init__(self,scope ,ai_network, value_loss_weight=0.5, policy_loss_weight=1,
                 entropy_weight=0.01, optimizer=tf.train.AdamOptimizer(learning_rate=0.001)):
        assert scope!='global'
        with tf.variable_scope(scope):
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
            # self.train = optimizer.minimize(self.loss)
            local_variables=tf.trainable_variables(scope)
            self.gradients=tf.gradients(self.loss,local_variables)
            global_variables=tf.trainable_variables("global")
            self.apply_gradients=optimizer.apply_gradients(zip(self.gradients,global_variables))
            self.pull_global_variables=[local_variable.assign(global_variable)
                                        for local_variable, global_variable in
                                        zip(local_variables,global_variables)]



class AIController(DummyInputManager):
    def __init__(self, id=1):
        super().__init__()
        self.score = 0
        self.number_eyes = 10
        self.ai_network = AINetwork(scope='worker{}'.format(id), number_eyes=self.number_eyes)
        self.ai_trainer = AINetworkTrainer('worker{}'.format(id), self.ai_network)
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())
        self.prev_state=None
        self.prev_action=None
        self.buffer=[]

    def getInputArray(self, deltaTime, state, ship, stillRunning=True):
        #Get output for our action (not training)

        #buffer:list of lists
        #current state, action taken, reward, next state, is game still running?, value estimate

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

        outputs, value = self.sess.run([self.ai_network.output, self.ai_network.value], feed_dict)
        outputs=outputs.tolist()[0]
        value = value[0][0]
        if self.prev_state:
            self.buffer.append([self.prev_state,self.prev_action,self.score,feed_dict,stillRunning, value])
        self.prev_state=feed_dict
        self.prev_action=outputs

        newMovement=[0,0]
        newMovement[0]=outputs[0]*math.cos(-1*i_angle)-outputs[1]*math.sin(-1*i_angle)
        newMovement[1]=outputs[0]*math.sin(-1*i_angle)+outputs[1]*math.cos(-1*i_angle)
        outputs[0]=newMovement[0]
        outputs[1]=newMovement[1]

        self.score=0
        return outputs

    def train(self):
        # process/format step buffer
        health = []
        angular_velocity = []
        forward_velocity = []
        strafe_velocity = []
        enemy_distances = []
        projectile_distances = []
        actions = []
        rewards = []
        running_list = []
        values=[]
        for state, action, reward, next_state, running, value in self.buffer:
            health.append(state[self.ai_network.health])
            angular_velocity.append(state[self.ai_network.angular_velocity])
            forward_velocity.append(state[self.ai_network.forward_velocity])
            strafe_velocity.append(state[self.ai_network.strafe_velocity])
            enemy_distances.append(state[self.ai_network.enemy_distances])
            projectile_distances.append(state[self.ai_network.projectile_distances])
            ###
            actions.append(action)
            ###
            rewards.append(reward)
            ###
            running_list.append(running)
            ###
            values.append(value)
        # feed buffer into tf session to determine gradients
        # update global  vars
        # clear step buffer
        self.buffer.clear()
import strategy as st

'''
A finite state machine AI with the following transition:
Wander -> Approach: when distance between missle and player <= dis_to_start_attack
Approach -> Wander: when distance between missle and player > dis_to_start_attack
'''
class Transition():
    def __init__(self, toState):
        self.toState = toState

    def Execute(self):
        pass

class State(object):
    def __init__(self, FSM):
        self.FSM = FSM
        
    def Execute(self):
        pass
        
class Wander(State):
    def __init__(self, FSM):
        super(Wander, self).__init__(FSM)
        self.strategy = st.Wander()

    def Execute(self):
        dis = st.Vec2D.sub(self.FSM.missle.kinematic.position, self.FSM.player.kinematic.position)
        if dis.length() <= self.FSM.dis_to_start_attack:
            self.FSM.ToTransition("toApproach")

class Approach(State):
    def __init__(self, FSM):
        super(Approach, self).__init__(FSM)
        self.strategy = st.Seek()

    def Execute(self):
        dis = st.Vec2D.sub(self.FSM.missle.kinematic.position, self.FSM.player.kinematic.position)
        if dis.length() > self.FSM.dis_to_start_attack:
            self.FSM.ToTransition("toWander")

class FSM():
    def __init__(self, missle, player, dis_to_start_attack = 200):
        self.missle = missle
        self.player = player
        self.states = {}
        self.transitions = {}
        self.curState = None
        self.trans = None
        self.dis_to_start_attack = dis_to_start_attack
    
    def AddTransition(self, transName, transition):
        self.transitions[transName] = transition

    def AddState(self, stateName, state):
        self.states[stateName] = state

    def SetState(self, stateName):
        self.curState = self.states[stateName]

    def ToTransition(self, toTrans):
        self.trans = self.transitions[toTrans]

    def Execute(self):
        if (self.trans):
            self.trans.Execute()
            self.SetState(self.trans.toState)
            self.trans = None
        self.curState.Execute()

class FSM_AI():
    def __init__(self, missle, player):
        self.fsm = FSM(missle, player)

        # States 
        self.fsm.AddState("Wander", Wander(self.fsm))
        self.fsm.AddState("Approach", Approach(self.fsm))

        # Transitions 
        self.fsm.AddTransition("toWander", Transition("Wander"))
        self.fsm.AddTransition("toApproach", Transition("Approach"))

        # Set initial state
        self.fsm.SetState("Wander")

    def get_strategy(self):
        # Execute FSM
        self.fsm.Execute()

        # Return the current strategy in FSM
        return self.fsm.curState.strategy
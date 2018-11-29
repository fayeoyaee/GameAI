from kinematics import * 

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
        
class MisselWanderState(State):
    def __init__(self, FSM):
        super(MisselWanderState, self).__init__(FSM)
        self.strategy = Wander()

    def Execute(self):
        dis = Vec2D.sub(self.FSM.missle.kinematic.position, self.FSM.player.kinematic.position)
        if dis.length() <= self.FSM.dis_to_start_attack:
            self.FSM.ToTransition("toApproach")

class ApproachState(State):
    def __init__(self, FSM):
        super(ApproachState, self).__init__(FSM)
        self.strategy = Seek()

    def Execute(self):
        dis = Vec2D.sub(self.FSM.missle.kinematic.position, self.FSM.player.kinematic.position)
        if dis.length() > self.FSM.dis_to_start_attack:
            self.FSM.ToTransition("toMissleWander")

class FSM():
    def __init__(self, missle, player, dis_to_start_attack = 100):
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
        self.MisselFSM = FSM(missle, player)

        # States 
        self.MisselFSM.AddState("MissleWander", MisselWanderState(self.MisselFSM))
        self.MisselFSM.AddState("Approach", ApproachState(self.MisselFSM))

        # Transitions 
        self.MisselFSM.AddTransition("toMissleWander", Transition("MissleWander"))
        self.MisselFSM.AddTransition("toApproach", Transition("Approach"))

        # Set initial state
        self.MisselFSM.SetState("MissleWander")

    def Execute(self):
        self.MisselFSM.Execute()

    def get_strategy (self):
        self.Execute()
        return self.MisselFSM.curState.strategy
        
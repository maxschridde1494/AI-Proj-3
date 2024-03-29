# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        for _ in range(self.iterations): #run value iteration k times
          oldValuesCounter = self.values.copy() #get old values
          states = self.mdp.getStates()
          for state in states:
            possibleActions = self.mdp.getPossibleActions(state)
            if len(possibleActions) == 0:
              continue
            actionValues = []
            for action in possibleActions:
              transitionStates = self.mdp.getTransitionStatesAndProbs(state, action)
              transitions = [t[1]*(self.mdp.getReward(state, action, t[0]) + (self.discount * oldValuesCounter[t[0]])) for t in transitionStates]
              actionValues.append(sum(transitions))
            self.values[state] = max(actionValues)


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        stateRewards = util.Counter()
        transitions = self.mdp.getTransitionStatesAndProbs(state, action)
        for nextState, prob in transitions:
          stateRewards[nextState] = prob * (self.mdp.getReward(state, action, nextState) + (self.discount * self.values[nextState]))
        return stateRewards.totalCount()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
          return None
        actions = self.mdp.getPossibleActions(state)
        actionValues = util.Counter()
        for action in actions:
          actionValues[action] = self.computeQValueFromValues(state, action)
        return actionValues.argMax()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        stateCounter = 0
        index = self.iterations
        while index > 0:
          state = states[stateCounter]
          possibleActions = self.mdp.getPossibleActions(state)
          if len(possibleActions) != 0:
            actionValues = []
            for action in possibleActions:
              transitionStates = self.mdp.getTransitionStatesAndProbs(state, action)
              transitions = [t[1]*(self.mdp.getReward(state, action, t[0]) + (self.discount * self.values[t[0]])) for t in transitionStates]
              actionValues.append(sum(transitions))
            self.values[state] = max(actionValues)
          index -= 1
          stateCounter += 1
          if stateCounter == len(states):
            stateCounter = 0

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        #generate predecessors
        statePredecessors = {}
        states = self.mdp.getStates()
        for state in states:
          statePredecessors[state] = [] #initialize values in predecessors dictionary to empty list 
        for state in states:
          actions = self.mdp.getPossibleActions(state)
          for action in actions:
            transitionStates = self.mdp.getTransitionStatesAndProbs(state, action)
            for nextState, prob in transitionStates:
              #don't know if this is necessary
              #getTransitions...() might only return transitions with nonzero probabilities initially
              if prob > 0:
                if state not in statePredecessors[nextState]:
                  statePredecessors[nextState].append(state)
        
        pQueue = util.PriorityQueue()
        #generate diffs
        for state in states:
          if not self.mdp.isTerminal(state):
            possibleActions = self.mdp.getPossibleActions(state)
            qValues = []
            for action in possibleActions:
              qValues.append(self.computeQValueFromValues(state, action))
            diff = abs(self.values[state] - max(qValues))
            pQueue.push(state, -diff)

        for _ in range(self.iterations):
          if pQueue.isEmpty():
            return
          else:
            curr_state = pQueue.pop()
            if not self.mdp.isTerminal(curr_state):
              pActions = self.mdp.getPossibleActions(curr_state)
              q = []
              for action in pActions:
                q.append(self.getQValue(curr_state, action))
              self.values[curr_state] = max(q)
              for predecessor in statePredecessors[curr_state]:
                predQ = []
                for a in self.mdp.getPossibleActions(predecessor):
                  predQ.append(self.getQValue(predecessor, a))
                diff = abs(self.values[predecessor] - max(predQ))
                if diff > self.theta:
                  pQueue.update(predecessor, -diff)

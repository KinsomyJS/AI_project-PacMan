# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import distanceCalculator
import game



#################
# Team creation #
#################

def createTeam(indexes, num, isRed, names=['DummyAgent','OffensiveAgent']):
    """
    This function should return a list of agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.    isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments, which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(name)(index) for name, index in zip(names, indexes)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """


    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """
        
        
        """
    	you can have your own distanceCalculator. (you can even have multiple distanceCalculators, if you need.)
    	reference the registerInitialState function in captureAgents.py and baselineTeam.py to understand more about the distanceCalculator. 
    	"""

        """
        Each agent has two indexes, one for pacman and the other for ghost.
        self.index[0]: pacman
        self.index[1]: ghost
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''

        """
        overwrite distancer
        only calculate distance positions which are reachable for self team
        """
        self.red = gameState.isOnRedTeam(self.index[0])#0 or 1 doesn't mater
        wallChar = 'r' if self.red else 'b'
        
        layout = gameState.data.layout.deepCopy()
        walls = layout.walls
        for x in range(layout.width):
            for y in range(layout.height):
                if walls[x][y] is wallChar:
                    walls[x][y] = False
        
        self.distancer = distanceCalculator.Distancer(layout)
        

        # comment this out to forgo maze distance computation and use manhattan distances
        self.distancer.getMazeDistances()
        
        
        self.start = [gameState.getAgentPosition(index) for index in self.index]

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index[0])
        
        
        '''
        You should change this in your own agent.
        '''

        
        return self.chooseActionImpl(gameState,self.index[0])

    def getSuccessor(self, gameState, action, index):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        return gameState.generateSuccessor(index, action) 
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action, self.index[0])

        successor = self.getSuccessor(successor, action, self.index[1])

        
        foodList = self.getFood(successor).asListNot()
        features['successorScore'] = -len(foodList)#self.getScore(successor)

        # Compute distance to the nearest food
        myPos = successor.getAgentState(self.index[0]).getPosition()
        if len(foodList) > 0: # This should always be True,    but better safe than sorry
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        
        capsulesList = self.getCapsules(successor)
        features['capsule'] = -len(capsulesList)
#         if len(capsulesList) > 0:
#             minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsulesList])
#             features['distanceToCapsule'] = minDistance
        
        score = (successor.getScore()-gameState.getScore())
        if(not self.red):
            score=-score;
        features['score'] = score
        
        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -5, 'capsule':150, 'score': 200}

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)

        weights = self.getWeights(gameState, action)
        
        return features * weights

    def chooseActionImpl(self, gameState, index):
        """
        Picks among the actions with the highest Q(s,a).
        """
        # isPacman = gameState.getAgentState(index).isPacman
        # time.sleep(2)
        actions = gameState.getLegalActions(index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        #get two enemy ghost
        if(not self.red):
            enemy_gho1 = gameState.getAgentState(4)
            enemy_gho2 = gameState.getAgentState(6)
        else:
            enemy_gho1 = gameState.getAgentState(5)
            enemy_gho2 = gameState.getAgentState(7)
        pacman = gameState.getAgentState(self.index[0])
        dis1 = self.distancer.getDistance(enemy_gho1.getPosition(),pacman.getPosition())
        dis2 = self.distancer.getDistance(enemy_gho2.getPosition(),pacman.getPosition())
        pacman_dir = pacman.getDirection()
        gho1_dir = enemy_gho1.getDirection()
        gho2_dir = enemy_gho2.getDirection()

        # print dis1,"(*(*(*(*(*(*(*(*",dis2
        if(dis1 < 3):
            if(Directions.REVERSE.get(enemy_gho1) in bestActions):
                bestActions.remove(Directions.REVERSE.get(enemy_gho1))
            return random.choice(bestActions)
        if(dis2 < 3):
            if(Directions.REVERSE.get(enemy_gho2) in bestActions):
                bestActions.remove(Directions.REVERSE.get(enemy_gho2))
            return random.choice(bestActions)
        if(gho1_dir == Directions.REVERSE.get(pacman)):
            return random.choice(bestActions.remove(pacman_dir))
        elif(dis2 < 4 and gho2_dir == Directions.REVERSE.get(pacman)):
            return random.choice(bestActions.remove(pacman_dir))

        print Directions.REVERSE.get(pacman.getDirection()),"*****",pacman.getDirection()
        
        # print enemies2.getDirection()
        
        act =  random.choice(bestActions)
        return act


class OffensiveAgent(DummyAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """
    
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action, self.index[0])
        successor = self.getSuccessor(successor, action, self.index[1])
        
        foodList = self.getFood(successor).asListNot()
        features['successorScore'] = -len(foodList)#self.getScore(successor)

        # Compute distance to the nearest food
        myPos = successor.getAgentState(self.index[0]).getPosition()
        if len(foodList) > 0: # This should always be True,    but better safe than sorry
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        
        capsulesList = self.getCapsules(successor)
        #print capsulesList
        #features['capsule'] = len(capsulesList)
        if len(capsulesList) > 0:
            minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsulesList])
            features['capsule'] = minDistance
        
        score = (successor.getScore()-gameState.getScore())
        if(not self.red):
            score=-score;
        features['score'] = score
        
        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -10, 'capsule':-5, 'score': 200}
    
    
    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        successor = self.getSuccessor(gameState, action, self.index[0])
        successor = self.getSuccessor(successor, action, self.index[1])
        score = (successor.getScore()-gameState.getScore())
        if(not self.red):
            score=-score;
        if action == Directions.STOP:
            score -= 100;
        foodList = self.getFood(successor).asListNot()        
        if ( len(self.getFood(gameState).asListNot()) > len(foodList)):
            score += 100;
        # Compute distance to the nearest food
        myPos = successor.getAgentState(self.index[0]).getPosition()
        if len(foodList) > 0: # This should always be True,    but better safe than sorry
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        score-= 3* minDistance
        
        capsulesList = self.getCapsules(successor)
        if len(capsulesList) > 0:
            minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsulesList])
        score -= minDistance
        
        return score
    
    def chooseActionImpl(self, gameState, index):
        """
        Picks among the actions with the highest Q(s,a).
        """
        # isPacman = gameState.getAgentState(index).isPacman
        # time.sleep(2)
        actions = gameState.getLegalActions(index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        #get two enemy ghost
        if(not self.red):
            enemy_gho1 = gameState.getAgentState(4)
            enemy_gho2 = gameState.getAgentState(6)
        else:
            enemy_gho1 = gameState.getAgentState(5)
            enemy_gho2 = gameState.getAgentState(7)
        pacman = gameState.getAgentState(self.index[0])
        dis1 = self.distancer.getDistance(enemy_gho1.getPosition(),pacman.getPosition())
        dis2 = self.distancer.getDistance(enemy_gho2.getPosition(),pacman.getPosition())
        pacman_dir = pacman.getDirection()
        gho1_dir = enemy_gho1.getDirection()
        gho2_dir = enemy_gho2.getDirection()
        g1x,g1y = enemy_gho1.getPosition()
        g2x,g2y = enemy_gho2.getPosition()
        px,py = pacman.getPosition()
        # print g1x,px

        #eat cap
        capsulesList = self.getCapsules(gameState)
        if len(capsulesList) > 0:
            minDistance = min([self.getMazeDistance(pacman.getPosition(), capsule) for capsule in capsulesList])
            if minDistance < 3:
                ax,ay=pacman.getPosition()
                fx,fy=capsule
                if fx>ax and Directions.EAST in actions:
                    act= Directions.EAST
                elif fx<ax and Directions.WEST in actions:
                    act= Directions.WEST
                elif fy>ay and Directions.NORTH in actions:
                    act= Directions.NORTH
                elif fy<ay and Directions.SOUTH in actions:
                    act= Directions.SOUTH
                return act
        #print dis1,"(*(*(*(*(*(*(*(*",dis2
        # if(dis1 < 3):
        #     if(Directions.REVERSE.get(enemy_gho1) in bestActions):
        #         bestActions.remove(Directions.REVERSE.get(enemy_gho1))
        #     return random.choice(bestActions)
        # if(dis2 < 3):
        #     if(Directions.REVERSE.get(enemy_gho2) in bestActions):
        #         bestActions.remove(Directions.REVERSE.get(enemy_gho2))
        #     return random.choice(bestActions)
        if((g1x == px or g1y == py) and Directions.REVERSE.get(enemy_gho1) in bestActions):
            if(gho1_dir in bestActions):
                return gho1_dir
            else:
                return random.choice(bestActions.remove(Directions.REVERSE.get(enemy_gho1)))

        if((g2x == px or g2y == py) and Directions.REVERSE.get(enemy_gho2) in bestActions):
            if(gho2_dir in bestActions):
                return gho2_dir
            else:
                return random.choice(bestActions.remove(Directions.REVERSE.get(enemy_gho2) ))

        # print Directions.REVERSE.get(pacman.getDirection()),"*****",pacman.getDirection()
        
        # print enemies2.getDirection()
        
        act =  random.choice(bestActions)

        return act
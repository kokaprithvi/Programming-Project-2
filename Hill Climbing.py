'''
By Prithvi Koka and Krishna Patel
ITCS 6150-091
'''

from random import randint, choice
import sys 

#Board Size
N = 8

# Maximum number of sideways moves allowed
MAX_SIDEWAYS = 100

# Number of runs for each hill climbing experiment
RUN_COUNTS = [50, 100, 200, 500, 1000, 1500]

# Number of trials for each random-restart hill climbing experiment
RESTART_TRIALS = 500

#Sequences to print for hill climbing and hill climbing with sideways move
NUM_SEQUENCES = 4

# Place a queen in each column of the board at a random row
def configureRandomly(board, state):
    for i in range(N):
        state[i] = randint(0, 100000) % N
        board[state[i]][i] = 1
   
#Print the board in a readable format, 0 for empty square, 1 for queen
def printBoard(board):
    for i in range(N):
        print(*board[i])

#Print the state of the board array, which is a list of row indices for each column
def printState(state):
    print(*state)
    
#Return True if two states are the same, False otherwise
def compareStates(state1, state2):
    for i in range(N):
        if (state1[i] != state2[i]):
            return False;
    return True

#Fill the board with a given value, either 0 or 1
def fill(board, value):
    for i in range(N):
        for j in range(N):
            board[i][j] = value

#Generate the board array from the state array, which is a list of row indices for each column
def generateBoard(board, state):
    fill(board, 0)
    for i in range(N):
        board[state[i]][i] = 1

#Copy the contents of state2 into state1
def copyState(state1, state2):
    for i in range(N):
        state1[i] = state2[i]

#Create a new board array, which is a 2D list of size N x N filled with 0s
def newBoard():
    return [[0 for _ in range(N)] for _ in range(N)]

#Returns the number of queens that are attacking each other in the given state.
#Two queens attack each other if they are in the same row or on the same diagonal.
def calculateObjective( board, state):
    attacking = 0
    for i in range(N):
        for j in range(i + 1, N):
            if state[i] == state[j] or abs(state[i] - state[j]) == j - i:
                attacking += 1
    return attacking

#Get the best neighbor state of the current state by moving one queen to a different row in its column.
# Returns the best objective value and a list of moves that achieve that objective.
def getNeighbor(board, state):
    bestObjective = None
    bestMoves = []

    neighborState = [0] * N
    copyState(neighborState, state)

    for i in range(N):
        original = state[i]
        for j in range(N):

            if j != original:
                neighborState[i] = j
                temp = calculateObjective(board, neighborState)

                if bestObjective is None or temp < bestObjective:
                    bestObjective = temp
                    bestMoves = [(i,j)]
                elif temp == bestObjective:
                    bestMoves.append((i,j))

        neighborState[i] = original

    return bestObjective, bestMoves
    
# Perform hill climbing search to find a solution to the N-Queens problem.
def hillClimbing(allowSideways = False, maxSideways = MAX_SIDEWAYS, initialState = None, record = False):
    state = [0] * N
    board = newBoard()

    if initialState is None:
        configureRandomly(board, state)
    else:
        copyState(state, initialState)
        generateBoard(board, state)

    steps = 0
    sidewaysUsed = 0
    objective = calculateObjective(board, state)
    sequence = [(list(state), objective)] if record else None

    while True:
        if objective == 0:
            break

        bestObjective, bestMoves = getNeighbor(board, state)

        if bestObjective > objective:
            break

        if bestObjective == objective:
            if not allowSideways or sidewaysUsed >= maxSideways:
                break
            sidewaysUsed += 1
        else: 
            sidewaysUsed = 0

        column, row = choice(bestMoves)
        state[column] = row
        generateBoard(board, state)
        objective = bestObjective
        steps += 1

        if record:
            sequence.append((list(state), objective))

    return {"success": objective == 0, "steps": steps, "state": state, 
            "objective": objective, "board": board, "sequence": sequence}

# Perform random-restart hill climbing search to find a solution to the N-Queens problem.
def randomRestartHillClimbing(allowSideways = False, maxSideways = MAX_SIDEWAYS, maxRestarts = 100000):
    totalSteps = 0
    for attempt in range(maxRestarts + 1):
        result = hillClimbing(allowSideways, maxSideways)
        totalSteps += result["steps"]
        if result["success"]:
            return {"success": True, "restarts": attempt,
                    "steps": totalSteps, "state": result["state"],
                    "board": result["board"]}
    
    return {"success": False, "restarts": maxRestarts, 
            "steps": totalSteps, "state": None, "board": None}

# Calculate the average of a list of values, returning 0.0 if the list is empty.
def average(values):
    return sum(values) /  len(values) if values else 0.0

# Run multiple hill climbing experiments and collect statistics on successes, failures, and steps taken.
def runHillClimbingExperiment(runs, allowSideways):
    successSteps = []
    failureSteps = []
    for _ in range(runs):
        result = hillClimbing(allowSideways = allowSideways)
        if result["success"]:
            successSteps.append(result["steps"])
        else: 
            failureSteps.append(result["steps"])

    return {"runs": runs,
            "successes": len(successSteps),
            "failures": len(failureSteps),
            "successRate": len(successSteps) / runs * 100,
            "failureRate": len(failureSteps) / runs * 100,
            "avgStepsSuccess": average(successSteps),
            "avgStepsFailure": average(failureSteps)}

# Run multiple random-restart hill climbing experiments and collect statistics on average restarts and steps taken.
def runRandomRestartExperiment(trials, allowSideways):
    restarts = []
    steps = []
    for _ in range(trials):
        result = randomRestartHillClimbing(allowSideways = allowSideways)
        restarts.append(result["restarts"])
        steps.append(result["steps"])
    return {"trials": trials,
            "avgRestarts": average(restarts),
            "avgSteps": average(steps),
            "maxRestarts": max(restarts)}

# Print a formatted table of experiment results, including the number of runs, successes, failures, success and failure rates, and average steps for successful and failed runs.
def printExperimentTable(title, rows):
    print("\n" + title)
    print("%6s %10s %9s %12s %11s %16s %16s"
          % ("Runs", "Successes", "Failures", "Success %", "Failure %",
             "Avg steps (S)", "Avg steps (F)"))
    for r in rows:
        print("%6d %10d %9d %11.2f%% %10.2f%% %16.2f %16.2f"
              % (r["runs"], r["successes"], r["failures"], r["successRate"],
                 r["failureRate"], r["avgStepsSuccess"], r["avgStepsFailure"]))

# Print the sequences of states and objective values for a specified number of hill climbing runs, showing the steps taken and whether each run was successful or not.
def printSequences(title, allowSideways, count = NUM_SEQUENCES):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    for k in range(1, count + 1):
        result = hillClimbing(allowSideways=allowSideways, record=True)
        status = "SUCCESS" if result["success"] else "FAILURE"
        print("\n--- Sequence %d: %s after %d steps ---"
              % (k, status, result["steps"]))
        board = newBoard()
        for step, (state, objective) in enumerate(result["sequence"]):
            print("\nStep %d: state =" % step, state, " h =", objective)
            generateBoard(board, state)
            printBoard(board)

# Read the number of queens n from user input, ensuring that n is at least 4.
def readN():
     while True:
        try:
            value = int(input("Enter the number of queens n (n >= 4): "))
            if value >= 4:
                return value
        except ValueError:
            pass
        print("Please enter an integer >= 4 "
              "(n = 2 and n = 3 have no solution).")

# Main function to run the N-Queens problem solver with hill climbing and random-restart hill climbing experiments.
def main():
    global N
 
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
        if N < 4:
            sys.exit("n must be at least 4.")
    else:
        N = readN()
 
    # A single demonstration solution for the chosen n
    print("\nSolving the %d-queens problem..." % N)
    demo = randomRestartHillClimbing(allowSideways=True)
    print("Solution found with %d restart(s) and %d total step(s): %s"
          % (demo["restarts"], demo["steps"], demo["state"]))
    printBoard(demo["board"])
 
    # A. Hill climbing search
    resultsA = [runHillClimbingExperiment(runs, False) for runs in RUN_COUNTS]
    printExperimentTable("A. Hill climbing search (n = %d)" % N, resultsA)
 
    # B. Hill-climbing search with sideways move
    resultsB = [runHillClimbingExperiment(runs, True) for runs in RUN_COUNTS]
    printExperimentTable("B. Hill-climbing search with sideways move "
                         "(n = %d, limit %d)" % (N, MAX_SIDEWAYS), resultsB)
 
    # C. Random-restart hill-climbing search
    print("\nC. Random-restart hill-climbing search "
          "(n = %d, %d trials each)" % (N, RESTART_TRIALS))
    without = runRandomRestartExperiment(RESTART_TRIALS, False)
    withSide = runRandomRestartExperiment(RESTART_TRIALS, True)
    print("   Without sideways move: average restarts = %.2f, "
          "average steps = %.2f" % (without["avgRestarts"], without["avgSteps"]))
    print("   With sideways move   : average restarts = %.2f, "
          "average steps = %.2f" % (withSide["avgRestarts"], withSide["avgSteps"]))
 
    # Search sequences from four random initial configurations
    printSequences("A. Search sequences: hill climbing", False)
    printSequences("B. Search sequences: hill climbing with sideways move", True)
 

if __name__ == "__main__":
    main()

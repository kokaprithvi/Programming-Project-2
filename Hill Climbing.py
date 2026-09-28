from random import randint, choice
import sys 

N = 8

MAX_SIDEWAYS = 100

RUN_COUNTS = [50, 100, 200, 500, 1000, 1500]

RESTART_TRIALS = 500

NUM_SEQUENCES = 4


def configureRandomly(board, state):
    for i in range(N):
        state[i] = randint(0, 100000) % N
        board[state[i]][i] = 1
   

def printBoard(board):
    for i in range(N):
        print(*board[i])

def printState( state):
    print(*state)
    

def compareStates(state1, state2):
    for i in range(N):
        if (state1[i] != state2[i]):
            return False;
    return True

def fill(board, value):
    for i in range(N):
        for j in range(N):
            board[i][j] = value

def generateBoard(board, state):
    fill(board, 0)
    for i in range(N):
        board[state[i]][i] = 1

def copyState(state1, state2):
    for i in range(N):
        state1[i] = state2[i]

def newBoard():
    return [[0 for _ in range(N)] for _ in range(N)]


def calculateObjective( board, state):
    attacking = 0
    for i in range(N):
        for j in range(i + 1, N):
            if state[i] == state[j] or abs(state[i] - state[j]) == j - i:
                attacking += 1
    return attacking
        
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

def average(values):
    return sum(values) /  len(values) if values else 0.0

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

def printExperimentTable(title, rows):
    print("\n" + title)
    print("%6s %10s %9s %12s %11s %16s %16s"
          % ("Runs", "Successes", "Failures", "Success %", "Failure %",
             "Avg steps (S)", "Avg steps (F)"))
    for r in rows:
        print("%6d %10d %9d %11.2f%% %10.2f%% %16.2f %16.2f"
              % (r["runs"], r["successes"], r["failures"], r["successRate"],
                 r["failureRate"], r["avgStepsSuccess"], r["avgStepsFailure"]))

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

from flask import Flask
from flask import render_template
from models import dbCon, main, paillierObj, paillerKeys





from flask import Flask, jsonify, request
keys = paillerKeys.paillerKeys() # Update this
db = dbCon.DBCon() # Connect to the database
app = Flask(__name__)


# @app.route('/home')
# def Welcome(name = None):
#     return render_template('index.html', person=name)

@app.route('/')
@app.route('/home')
def Welcome():
    return render_template('home.html')

"""
Directing to this page will update the keys and start the simulation
"""
@app.route('/start', methods=['GET'])
def start():
    db.clean() # Clean out old results if any
    args = [] # Simulation args
    pop = request.args.get('pop', "10000")
    p = request.args.get('p', "1")
    q = request.args.get('q', "1")
    g = request.args.get('g', "1")
    delay = request.args.get('delay', "1")
    if pop != "":
        pop = int(pop)
        if pop != 10000:
            args.append("-pop")
            args.append(pop)
    if p != "" and q != "":
        p = int(p)
        q = int(q)
        if p > 1 and q > 1:
            args.append("-private")
            args.append(p)
            args.append(q)
            if g != "":
                g = int(g)
                if g > 1:
                    args.append("-public")
                    args.append(g)    
    if delay != "":
        delay = int(delay)
        if delay > 1:
            args.append("-d")
            args.append(delay)
    
    global keys 
    keys = main.startSimulation(args) # Load arguments as if cmd line args
    print(f"Public key g: {keys.g}, public key n: {keys.n}, p: {keys.p}, q: {keys.q}")
    return render_template('start.html') # Forward to new page

@app.route('/voteLog')
def vLog(tacoVote = None, firstTaco = None, tacoPT = None, nsq = None, pizzaVote = None, firstPizza = None, pizzaPT = None):
    db.flushTables()
    data = db.fetchVotesEnc()
    # Apply the homomorphic calculations
    firstTaco = -1
    firstPizza = -1
    tacoVote = []
    pizzaVote = []
    nsq = keys.n ** 2
    for j in data:
        if j.canidate == "Taco":
            if firstTaco == -1:
                firstTaco = j.count
            else:
                tacoVote.append(j.count)
        if j.canidate == "Pizza":
            if firstPizza == -1:
                firstPizza = j.count
            else:
                pizzaVote.append(j.count)
    
    temp = paillierObj.paillerObj(keys.n, keys.g)
    temp.p = keys.p
    temp.q = keys.q
    temp.cipherText = firstTaco
    # Sum up values then decrypt
    for i in tacoVote:
        temp.add(i)
    tacoPT = temp.decrypt()
    temp = paillierObj.paillerObj(keys.n, keys.g)
    temp.p = keys.p
    temp.q = keys.q
    temp.cipherText = firstPizza
    for i in pizzaVote:
        temp.add(i)
    pizzaPT = temp.decrypt()

    return render_template('TotalVoteLog.html', tacoVote=tacoVote, firstTaco=firstTaco, tacoPT=tacoPT, nsq=nsq, pizzaVote=pizzaVote, firstPizza=firstPizza,pizzaPT=pizzaPT)

@app.route('/examplePailler')
def pa():
    return render_template('UsingPaillier.html')

@app.route('/voting')
def vote(vote = None, sum = None, win = None, winP = 50):
    names = ["Cramer", "Jones", "Jonesa", "Fidel", "Speare", "Wier", "Workman"]
    votes = []
    total = [0,0]
    win = ""
    for i in names:
        # location, taco, pizza, percent
        votes.append([i, -1, -1, 50, "Neither"])
    db.flushTables()
    data = db.fetchVotesEnc()
    # Apply the homomorphic calculations
    for j in data:
        for i in votes:
            if i[0] == j.location:
                if j.canidate == "Taco":
                    if i[1] == -1:
                        i[1] = j.count
                    else:
                        i[1] = (i[1] * j.count) % keys.n**2
                elif j.canidate == "Pizza":
                    if i[2] == -1:
                        i[2] = j.count
                    else:
                        i[2] = (i[2] * j.count) % keys.n**2
                break
    # Decrypt
    temp = paillierObj.paillerObj(keys.n, keys.g)
    temp.p = keys.p
    temp.q = keys.q
    for j in votes:
        # CLear
        print("Unencrypted values",j)
        if j[1] != -1:
            temp.cipherText = j[1]
            j[1] = temp.decrypt()
        else:
            j[1] = 0

        if j[2] != -1:
            temp.cipherText = j[2]
            j[2] = temp.decrypt()
        else:
            j[2] = 0
        
    
    for j in votes:
        total = j[1] + j[2]
        if total != 0:
            # Determines taco percentage
            percent = j[1] / total
            percent *= 100
            percent = round(percent)
            j[3] = percent
            if j[1] > j[2]:
                j[4] = "Taco"
            elif j[2] > j[1]:
                j[4] = "Pizza"
    print(votes)
    total = [0,0]
    for j in votes:
        total[0] += j[1]
        total[1] += j[2]                        
    
    pizza = 0
    taco = 0
    for j in votes:
        if j[4] == "Taco":
            taco += 1
        else:
            pizza += 1

    if taco > pizza:
        winner = "Taco"
    else:
        winner = "Pizza"

    totalVotes = total[1] + total[0]
    if totalVotes != 0:
        per = total[0] / totalVotes
        per *= 100
        per = round(per)
    return render_template('votePannel.html', vote = votes, sum = total, win = winner, winP = per)


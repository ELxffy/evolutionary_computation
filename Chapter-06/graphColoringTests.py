import csv
import unittest 
import datetime 
import genetic


def load_data(localFileName):
    '''
    expects: T D1 [D2 ... DN]
    where T is the record type
    and D1 .. DN are record-type appropriate data elements
    '''
    rules = set()
    nodes = set()
    with open(localFileName, mode='r') as infile:
        content = infile.read().splitlines()

    for row in content:
        if row[0] == 'e': # e aa bb, aa and bb are node ids 
            nodeIds = row.split(' ')[1:3] 
            rules.add(Rule(nodeIds[0], nodeIds[1])) 
            nodes.add(nodeIds[0])
            nodes.add(nodeIds[1])
            continue

        if row[0] == 'n': # n aa ww, aa is a node id, ww is a weight
            nodeIds = row.split(' ')
            nodes.add(nodeIds[1]) 
    
    return rules, nodes


class Rule:
    def __init__(self, node, adjacent):
        if node < adjacent:
            node, adjacent = adjacent, node
        self.Node = node
        self.Adjacent = adjacent

    def __eq__(self, other):
        return self.Node == other.Node and \
        self.Adjacent == other.Adjacent 
    
    def __hash__(self):
        return hash(self.Node) * 397 ^ hash(self.Adjacent)
    
    def __str__(self):
        return self.Node + "->" + self.Adjacent

    def IsValid(self, genes, nodeIndexLookup):
        index = nodeIndexLookup[self.Node] 
        adjacentStateIndex = nodeIndexLookup[self.Adjacent] 
        return genes[index] != genes[adjacentStateIndex]

def build_rules(items): 
    rulesAdded = {}

    for state, adjacent in items.items(): 
        for adjacentState in adjacent:
            if adjacentState == '': 
                continue
            rule = Rule(state, adjacentState) 
            if rule in rulesAdded:
                rulesAdded[rule] += 1 
            else:
                rulesAdded[rule] = 1
    for k, v in rulesAdded.items(): 
        if v != 2:
            print("rule {} is not bidirectional".format(k)) 
    
    return rulesAdded.keys()

def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime 
    print("{}\t{}\t{}".format(
          ''.join(map(str, candidate.Genes)),
          candidate.Fitness,
          timeDiff))


def get_fitness(genes, rules, stateIndexLookup): 
    rulesThatPass = sum(1 for rule in rules 
                        if rule.IsValid(genes, stateIndexLookup)) 
    return rulesThatPass

@staticmethod
def test_convert_file():
    states = load_data("adjacent_states.csv") 
    output = []
    nodeCount = edgeCount = 0
    for state, adjacents in states.items():
        nodeCount += 1
        for adjacent in adjacents:
            if adjacent == '':
                output.append("n {} 0".format(state))
        else:
            output.append("e {} {}".format(state, adjacent)) 
            edgeCount += 1
    
    with open('./adjacent_states.col', mode='w+') as outfile:
        print("p edge {} {}".format(nodeCount, edgeCount), file=outfile) 
        for line in sorted(output):
            print(line, file=outfile)

class GraphColoringTests(unittest.TestCase): 
    
    def color(self,file,colors): 
        rules, nodes = load_data(file)

        #Define geneSet
        colors = ["Orange", "Yellow", "Green", "Blue"] 
        colorLookup = {color[0]: color for color in colors} 
        geneset = list(colorLookup.keys())

        optimalValue = len(rules) #all adjacent states have different color

        #Chromosome will have 50 genes, one for each state in alphabatical order
        nodeIndexLookup = { key: index for index, key in enumerate(sorted(nodes))}

        #Call get_best
        startTime = datetime.datetime.now()
        
        def fnDisplay(candidate): 
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes, rules, nodeIndexLookup)
      
        best = genetic.get_best(fnGetFitness, len(nodes), optimalValue, geneset, fnDisplay)

        self.assertTrue(not optimalValue > best.Fitness)

        keys = sorted(nodes)
        for index in range(len(nodes)):
            print(keys[index] + " is " + colorLookup[best.Genes[index]])


    def test_states(self):
        self.color("adjacent_states.col",
                    ["Orange", "Yellow","Green","Blue"])

    def test_R100_1gb(self): 
        self.color("R100_1gb.col",
                    ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo"])
    
    def test_benchmark(self):
        genetic.Benchmark.run(lambda: self.test_R100_1gb())
    

if __name__ == '__main__':   
    unittest.main()
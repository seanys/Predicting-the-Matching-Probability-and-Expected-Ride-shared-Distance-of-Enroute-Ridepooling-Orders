def getID(i,j):
    return ("%05d%05d")%(i,j)

def getIDL(i,j):
    return ("%08d%08d")%(i,j)

def getIDFour(i,j,m,n):
    return ("%05d%05d%05d%05d")%(i,j,m,n)

def getPairs(self):
    '''加载一下对应的情况'''
    pairs_df = pd.read_csv("Simulation/data/pairs.csv")
    pairs = {}
    for i in range(pairs_df.shape[0]):
        pairs[pairs_df["original"][i]] = pairs_df["final"][i]
    vertexes_df = pd.read_csv("Simulation/data/vertexes.csv")
    for i in range(vertexes_df.shape[0]):
        if vertexes_df["ver_id"][i] not in pairs:
            pairs[vertexes_df["ver_id"][i]] = vertexes_df["ver_id"][i]
    return pairs

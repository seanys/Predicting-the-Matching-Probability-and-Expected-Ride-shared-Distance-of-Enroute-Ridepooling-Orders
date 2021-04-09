import pandas as pd

def getConnection():
    '''增加相近结点之间的衔接'''
    vertexes_df = pd.read_csv("HaiKou/network/all_vertexes.csv")
    vertexes = [json.loads(vertexes_df["coor"][i]) for i in range(vertexes_df.shape[0])]
    all_connection = [[i] for i in range(len(vertexes))]
    for i in range(249-1):
        for j in range(i+1,249):
            dis = Point(vertexes[i]).distance(Point(vertexes[j]))
            if dis > 0.000001 and dis < 0.0005:
                all_connection[i].append(j),all_connection[j].append(i)
    # for connection in all_connection:
    #     if len(connection) > 1: print(connection)
    return all_connection

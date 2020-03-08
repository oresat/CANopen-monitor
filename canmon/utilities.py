import os.path, json

def load_config(window, filename):
    file = open(os.path.expanduser(filename))
    raw_data = file.read()
    file.close()
    return json.loads(raw_data)

def find_n(data, delim, n=0):
    pieces = data.split(delim, n + 1)
    if(len(pieces) <= (n + 1)): return -1
    return len(data) - len(pieces[-1]) - len(delim)

def delims(data, start, end='\0', n=0):
    return [ find_n(data, start, n) + 1,
             len(data) - find_n(data[::-1], end, n) - 1 ]

# Generate the default configs
def config_factory(filename):
    if(not os.path.exists(os.path.expanduser("~/.canmon"))): os.mkdir(os.path.expanduser("~/.canmon"))
    if("devices" in filename): data = ["can0"]
    elif("tables" in filename): data = [{ 'name': "Hearbeats",
                                          'capacity': 16,
                                          'stale_node_timeout': 60,
                                          'dead_node_timeout': 600 },
                                       { 'name': "Hearbeats",
                                         'capacity': 64,
                                         'stale_node_timeout': None,
                                         'dead_node_timeout': None }]
    else: data = {}

    file = open(os.path.expanduser(filename), "w+")
    file.write(json.dumps(data, sort_keys=True, indent=4) + "\n")
    file.close()

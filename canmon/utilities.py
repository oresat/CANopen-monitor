import os.path, json

# Load a pre-existing json config
def load_config(filename):
    file = open(os.path.expanduser(filename))
    raw_data = file.read()
    file.close()
    return json.loads(raw_data)

# Generate default configs
def config_factory(filename):
    if(not os.path.exists(os.path.expanduser("~/.canmon"))): os.mkdir(os.path.expanduser("~/.canmon"))
    if("devices" in filename): data = ["can0"]
    elif("tables" in filename): data = [{ 'name': "Hearbeat",
                                          'capacity': 16,
                                          'stale_node_timeout': 60,
                                          'dead_node_timeout': 600 },
                                        { 'name': "PDO's",
                                          'capacity': 64,
                                          'stale_node_timeout': None,
                                          'dead_node_timeout': None },
                                        { 'name': "Misc",
                                          'capacity': 64,
                                          'stale_node_timeout': None,
                                          'dead_node_timeout': None }]
    else: data = {}

    file = open(os.path.expanduser(filename), "w+")
    file.write(json.dumps(data, sort_keys=True, indent=4) + "\n")
    file.close()

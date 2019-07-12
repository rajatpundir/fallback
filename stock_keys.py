import os

def api_key(filename = 'keys'):
    filename = './config/' + filename + '.txt'
    if not os.path.exists('config'):
        os.mkdir('config')
    if not os.path.exists(filename):
        open(filename, 'w').close()
    handle = open(filename, 'r')
    keys = []
    for key in handle:
        keys.append(key.strip())
    handle.close()
    handle = open(filename, 'w')
    for key in keys[1:]:
        handle.write(key + '\n')
    if len(keys) > 0:
        handle.write(keys[0] + '\n')
    handle.close()
    if len(keys) > 0:
        return(keys[0])
    else:
        return(None)

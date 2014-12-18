#!/usr/bin/evn python
# uskee.org


def parse_word(line):
    mark = ""
    word = ""
    idx = 0
    cnt = 0
    for ch in line:
        idx += 1
        if ch == " ":
            pass
        elif ch == "=":
            mark = ch
        elif ch == "\r" or ch == "\n":
            pass
        elif ch == ",":
            pass
        elif ch == ":":
            if cnt >= 2: mark = ":"
        elif ch == "{" or ch == "}":
            pass
        elif ch == "'" or ch == "'":
            cnt += 1
        else:
            word += ch 
    return word, idx, mark

def parse_line(line):
    word, idx, mark = parse_word(line)
    if mark == "=" and word:
        return 1, word
    elif mark == ":" and word:
        return 2, word
    elif word:
        return 3, word
    else:
        return 4, ""


def parse_lines(data, keys, lines, done):
    if not lines: return

    line = lines[0]
    kind, word, word2, = parse_line(line)
    print kind, keys[1:], word, done
    if kind == 1:           # key 1  
        data[keys[1]][word]={}
        data = data[keys[1]]
        keys.append(word)
    elif kind == 2:
        if not done:
            data[keys[-1]][word] = {}
            data = data[keys[-1]]
            keys.append(word)
        else:
            if word == "mac": print data
            data[word] = {}
            keys[-1] = word
        done = 0
    elif kind == 3:                     # val
        data[keys[-1]] = word
        done = 1
    elif kind == 4:                     # end of k:v
        if done: 
            keys.pop()
            data = keys[0]
            for item in keys[1:-1]:
                data = data[item]
            print data
        print keys[1:], word
    parse_lines(data, keys, lines[1:], done)
        

def loadeps(fname):
    data = {}
    data["DEPS"] = {}
    lines = file(fname).readlines()
    parse_lines(data, [data, "DEPS"], lines, 0)
    print data
    return None


data = loadeps("DEPS.1")
#data = loadeps("src/DEPS")


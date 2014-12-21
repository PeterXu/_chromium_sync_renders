#!/usr/bin/evn python
# uskee.org

import os
import sys
import getopt

# item in wlist: [word, weight]
def parse_line(wlist, line):
    word = ""
    strmark = 0
    for ch in line:
        if ch == " ":       
            pass
        elif ch == "," or ch == "\r" or ch == "\n":
            if word: 
                #print word
                wlist.append([word, wlist[0]])
                word = ""
        elif ch == "'":     
            if word.find("Var(") != -1:
                continue
            strmark += 1
            if strmark >= 2 and word:
                #print word
                wlist.append([word, wlist[0]])
                strmark = 0
                word = ""
        elif ch == "=":     
            strmark = 0
            if word: 
                #print word
                wlist.append([word, wlist[0]])
                word = ""
        elif ch == ":":
            if strmark == 1:    
                #print word
                word += ch
            strmark = 0
        elif ch == "{":
            wlist[0] += 1
        elif ch == "}":
            wlist[0] -= 1
        else:
            word += ch
    return None


def str2dict(data, wlist):
    wlist[0] = 0
    klist = []
    done = False
    for item in wlist[1:]:
        pre = wlist[0]
        word = item[0]
        cur = item[1]
        wlist[0] = cur
        if cur == 0:
            klist.append(word)
            data[klist[0]] = {}
        elif cur == 1:
            if pre < cur:
                klist.append(word)
                data[klist[0]][klist[1]] = {}
                done = False
            elif pre == cur and not done: # 1 - 1
                data[klist[0]][klist[1]] = word
                done = True
            else:
                if pre > cur: klist.pop()
                klist[1] = word
                #print klist, word
                data[klist[0]][klist[1]] = {}
                done = False
        elif cur == 2:
            if pre < cur:
                klist.append(word)
                #print klist
                data[klist[0]][klist[1]][klist[2]] = {}
                done = False
            elif pre == cur and not done: # 2 - 2
                data[klist[0]][klist[1]][klist[2]] = word
                done = True
            else: # done = True, no pre > cur
                if pre > cur: klist.pop()
                klist[2] = word
                data[klist[0]][klist[1]][klist[2]] = {}
                done = False

def check_dict(line):
    start = False
    for ch in line:
        if start:
            if ch == " " or ch == "\t": continue
            elif ch == "{": return 0
            elif ch == "[": return 1
            else: return -1
        if ch == "=":
            start = True
    return -1

def parse_lines(data, lines):
    wlist = [0]
    last = -1
    for line in lines:
        prop = check_dict(line)
        if last == 0 and prop >= 0:
            #print wlist
            str2dict(data, wlist)           
            wlist = [0]
            if prop == 0:
                parse_line(wlist, line)
                last = prop
            else:
                last = -1
        elif last == 0:
            parse_line(wlist, line)
        elif prop == 0:
            wlist = [0]
            parse_line(wlist, line)
            last = prop
        else:
            last = -1
    if len(wlist) > 1:
        #print wlist
        str2dict(data, wlist)           
    #print data

def printdeps(data, ident):
    for key in data.keys():
        if type(data[key]) == dict:
            print "%s%s:" % (ident, key)
            printdeps(data[key], "    %s" % ident)
        else:
            print "%s%s => %s" % (ident, key, data[key])

def loadeps(fname):
    data = {}
    data["DEPS"] = {}
    parse_lines(data["DEPS"], file(fname).readlines())
    #printdeps(data["DEPS"], "")
    return data

def parse_uri(kvar, line):
    if type(line) != type(""): return "",""

    line = line.replace("+@+Var(", "@Var(")
    while True:
        pos1 = line.find("Var(")
        if pos1 == -1: break
        pos2 = line.find(")", pos1)
        if pos2 == -1: break

        vstr = line[pos1+4:pos2]
        sstr = "Var(%s)" % line[pos1+4:pos2]
        while True:
            pos2 += 1
            if pos2 < len(line) and line[pos2] == "+":
                sstr += "+" 
            else:
                break
        if kvar.has_key(vstr):
            line = line.replace(sstr, kvar[vstr])
                
    pos = line.rfind("@")
    if pos != -1:
        uri = line[:pos]
        rev = line[pos+1:]
    else:
        uri = line
        rev = "_"
    return uri, rev
    

def syncx(kvar, data, chrome):
    for key in data.keys():
        root = "%s/%s" % (chrome, key)
        val = data[key]
        rev = ""

        #print val
        uri,rev = parse_uri(kvar, val)
        if not uri or not rev:
            print "\n[ERROR]\t%s => %s" % (key, val)
            continue
        sh = """
        root=%s && uri=%s && rev=%s; 
        [ ! -d "$root" ] && mkdir -p "$root" && cd "$root" && git init && cd -; 
        cd "$root"; 
        git remote rm origin 2>/dev/null;
        git remote add origin "$uri" 2>/dev/null;
        git pull -f origin;
        git checkout --detach HEAD 2>/dev/null;
        git branch -D master 2>/dev/null;
        git checkout -b master $rev 
        git branch -l | grep master 2>/dev/null || git checkout -b master origin/master;
        sleep 3
        """
        print "\n[INFO]\t%s => %s@%s" % (key, uri, rev)
        sh = sh % (root, uri, rev)
        os.system(sh)
    pass

def usage(prog):
    print "usage: %s -h|--help -c|--chrome chrome_src DEPS" % prog
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) <= 1: usage(sys.argv[0])

    shortopts="hc:"
    longopts=["help", "chrome="]
    optlist, args = getopt.gnu_getopt(sys.argv[1:], shortopts, longopts)

    chrome = "."
    for item in optlist:
        if item[0] == "-h" or item[0] == "--help":
            usage(sys.argv[0])
        elif item[0] == "-c" or item[0] == "--chrome":
            chrome = item[1]
    if not args: usage(sys.argv[0])
    if len(args) != 1: usage(sys.argv[0])
    deps = args[0]

    print "[INFO] Parsing %s ..." % deps
    data = loadeps(deps)
    syncx(data["DEPS"]["vars"], data["DEPS"]["deps_os"]["unix"], chrome)
    syncx(data["DEPS"]["vars"], data["DEPS"]["deps"], chrome)



from textual.app import App, ComposeResult, Binding
from textual.containers import Container, Center
from textual.widgets import Button, Header, Footer, Static, TextLog, Input, Label, DirectoryTree, ContentSwitcher
from textual.widget import Widget
from textual import events
from textual.reactive import reactive
from textual.message_pump import MessagePump
from textual.color import Color

import json
import os
import subprocess
from shell import shell
import random
import sys

c_file = open("config.json")
config = json.load(c_file)
c_file.close()

def shell_parse(input):
    if(input == "deadbeef"):
        return "Thanks!"
    elif(input[:2] == "cd"):
        try:
            os.chdir(input[3:])
            return os.getcwd()
        except:
            return "Directory not found."
    else:
        return shell(input)

class Prompt(Widget):
    to_return = reactive(str(os.getcwd()),layout=False)

    def update(self,args):
        self.to_return = shell_parse(args)

    def render(self) -> str:
        return self.to_return

def parse_cpu():
    with open("/proc/cpuinfo") as file:
        data = file.read()
        data = data.split("\n")
        return data[6].replace("	","").replace(" ","")[7:]

def parse_mem():
    with open("/proc/meminfo") as file:
        data = file.read()
        data = data.split("\n")
        total = int(data[0].replace("	","").replace(" ","")[9:-2])
        free = int(data[1].replace("	","").replace(" ","")[8:-2])
        return str(total-free)

def parse_uptime():
    with open("/proc/uptime") as file:
        data = file.read()
        data = data.split(" ")
        uptime = int(float(data[0]))
        cputime = uptime-int(float(data[1]))
        return str(uptime),str(cputime)

def parse_storage():
    proc = subprocess.Popen("df",stdout=subprocess.PIPE)
    output = proc.stdout.read().decode("utf-8").split("\n")
    output = output[2].replace("	","")
    output = output.split(" ")[3]
    return str(output)

class SysInfo(Widget):
    cpu = reactive(parse_cpu())
    memory = reactive(parse_mem())
    uptime = reactive(parse_uptime()[0])
    cputime = reactive(parse_uptime()[1])
    storage = reactive(parse_storage())
    retval = reactive("")

    def fetchinfo(self):
        self.cpu = parse_cpu()
        self.memory = parse_mem()
        self.uptime = parse_uptime()[0]
        self.cputime = parse_uptime()[1]
        self.storage = parse_storage()

    def on_mount(self):
        self.set_interval(1.0,self.fetchinfo)

    def comp(self):
        self.retval = "System info:\n"
        self.retval+=str(self.cpu)+" MHz CPU\n"
        self.retval+=str(self.memory)+" KB memory in use\n"
        self.retval+=str(self.storage)+" KB storage available\n"
        self.retval+="Uptime: "+str(self.uptime)+" s\n"
        self.retval+="CPU time: "+str(self.cputime)+" s\n"

    def render(self) -> str:
        self.comp()
        return self.retval

class Logo(Widget):
    kitty = r"""                         .-.
                          \ \
                           \ \
                            | |
                            | |
          /\---/\   _,---._ | |
         /^   ^  \,'       `. ;
        ( O   O   )  PyTerm   ;
         `.=o=__,'            \
           /         _,--.__   \
          /  _ )   ,'   `-. `-. \
         / ,' /  ,'        \ \ \ \
        / /  / ,'          (,_)(,_)
       (,;  (,,)"""
    def render(self) -> str:
        return self.kitty

class Snow(Widget):
    posx = reactive([])
    posy = reactive([])
    retval = reactive("")

    def update(self):
        try:
            if(random.randint(0,1)):
                if(len(self.posx) < 15):
                    self.posx.append(random.randint(0,self.container_size[0]-1))
                    self.posy.append(0)
            i = 0
            while(i < len(self.posx)):
                self.posy[i]+=1
                if(self.posy[i] == self.container_size[1]):
                    self.posx.pop(i)
                    self.posy.pop(i)
                    i-=1
                i+=1

            self.retval = ""
            for i in range(self.container_size[1]):
                tmp = " "*(self.container_size[0])
                if(i in self.posy):
                    xind = self.posx[self.posy.index(i)]
                    tmp = [x for x in tmp]
                    tmp[xind] = "*"
                    tmp = "".join(tmp)
                tmp+="\n"
                self.retval+=tmp
        except:
            pass

    def on_mount(self):
        self.set_interval(.25,self.update)

    def render(self) -> str:
        return self.retval


class Rain(Widget):
    posx = reactive([])
    posy = reactive([])
    retval = reactive("")

    def update(self):
        try:
            if(1):
                if(len(self.posx) < 300):
                    self.posx.append(random.randint(0,self.container_size[0]-1))
                    self.posy.append(0)
            i = 0
            while(i < len(self.posx)):
                self.posy[i]+=1
                if(self.posy[i] == self.container_size[1]):
                    self.posx.pop(i)
                    self.posy.pop(i)
                    i-=1
                i+=1

            self.retval = ""
            for i in range(self.container_size[1]):
                tmp = " "*(self.container_size[0])
                if(i in self.posy):
                    xind = self.posx[self.posy.index(i)]
                    tmp = [x for x in tmp]
                    tmp[xind] = "."
                    tmp = "".join(tmp)
                tmp+="\n"
                self.retval+=tmp
        except:
            pass

    def on_mount(self):
        self.set_interval(.04,self.update)

    def render(self) -> str:
        return self.retval

class FileTree(Widget):
    filetree = reactive(DirectoryTree(os.getcwd()))

    def compose(self) -> ComposeResult:
        yield self.filetree

    def update_tree(self):
       self.filetree = reactive(DirectoryTree(os.getcwd()))

class PyTerm(App):
    CSS_PATH="styles.css"

    settings = config
    recent_commands = []

    current = reactive("hello")
    cwd = reactive(os.getcwd())
    _in = Input()
    buffer = ""
    prompt = Prompt(id="prompt")
    sysinfo = SysInfo(id="sys")
    switcher1 = ContentSwitcher(initial=settings["default_widgets"][0])
    switcher2 = ContentSwitcher(initial=settings["default_widgets"][1])
    tree = Container(DirectoryTree(os.getcwd()),id="filetree")
    snow = Snow(id="snow")
    rain = Rain(id="rain")
    kitty = Logo(id="kitty")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with self.switcher1:
            yield self.snow
            yield self.rain
            yield self.sysinfo
        with self.switcher2:
            yield self.tree
            yield self.kitty
        yield self.prompt
        yield self._in

    def update_s(self):
        self.switcher1.styles.border = (self.settings["border"],self.settings["theme"])
        self.prompt.styles.border = (self.settings["border"],self.settings["theme"])
        self._in.styles.border = (self.settings["border"],self.settings["theme"])
        self.switcher2.styles.border = (self.settings["border"],self.settings["theme"])

    def update_tree(self):
        self.query_one("#filetree > DirectoryTree").remove()
        self.query_one("#filetree").mount(DirectoryTree(os.getcwd()))

    def export_settings(self,filename):
        j = json.dumps(self.settings)
        file = open(filename,"w")
        file.write(j)
        file.close()

    def on_input_changed(self,event:Input.Changed):
        self.buffer = event.value

    def on_input_submitted(self,event:Input.Submitted) -> None:
        e_arr = event.value.split(" ")
        e_arr.append("")
        if(event.value == ":q" or event.value == "exit"):
                self.exit()
        elif(e_arr[0] == "theme"):
            try:
                Color.parse(e_arr[1])
                self.settings["theme"] = event.value[6:]
                self.prompt.to_return = "Successfully updated settings."
            except:
                self.prompt.to_return = "Error: color not found."
        elif(e_arr[0] == "content"):
            contents = ["filetree","snow","rain","sys","kitty"]
            try:
                if(e_arr[2] in contents):
                    num = int(e_arr[1])
                    if(num == 1):
                        self.switcher1.current = e_arr[2]
                        self.settings["default_widgets"][0] = e_arr[2]
                    else:
                        self.switcher2.current = e_arr[2]
                        self.settings["default_widgets"][1] = e_arr[2]
                    self.prompt.to_return = "Successfully updated settings."
                else:
                    self.prompt.to_return = "Error: content not found. Select content from the following:\n"+",".join(contents)
            except:
                self.prompt.to_return = "Error: select a valid pane/content combo.\nFormat: content [content pane number] [content name]"
        elif(e_arr[0] == "border"):
            options = ["ascii","blank","dashed","double","heavy","hidden", "none","hkey",
                "inner","outer","round","solid","tall","thick","vkey","wide"]
            if(e_arr[1] == ""):
                self.prompt.to_return = "Available borders styles: "+", ".join(options)+"."
            else:
                if(e_arr[1] in options):
                    self.settings["border"] = e_arr[1]
                    self.prompt.to_return = "Successfully updated settings."
                else:
                    self.prompt.to_return = "Error: border style not found."
        elif(e_arr[0] == "export"):
            if(len(event.value) <= 7):
                self.prompt.to_return = "Error: please specify an output file."
            else:
                self.export_settings(event.value[7:])
                self.prompt.to_return = "Successfully wrote settings to \""+event.value[7:]+"\"."
        elif(e_arr[0] == "autofill"):
            if(e_arr[1].lower() not in ["true","false"]):
                self.prompt.to_return = "Error: invalid value."
            else:
                if(e_arr[1].lower() == "true"):
                    self.settings["autofill"] = True
                else:
                    self.settings["autofill"] = False
                self.prompt.to_return = "Successfully updated settings."
        # if(event.value[:2] == "ls"):
        #     self.cwd = os.getcwd()
        #     self.query_one(ContentSwitcher).current = "filetree"
        else:
            #self.query_one(ContentSwitcher).current = "prompt"
            self.prompt.update(event.value)
        event.input.action_delete_left_all()
        self.update_s()
        self.update_tree()

    def on_mount(self):
        self._in.focus()
        self.update_s()

    def on_key(self, event:events.Key):
        if(self.settings["autofill"]):
            if(event.key=="tab"):
                fname = self.buffer.split(" ")
                fname = fname[len(fname)-1]
                filenames = os.listdir(os.getcwd())
                valid = []
                for file in filenames:
                    if(file[:len(fname)] == fname):
                        valid.append(file)
                if(len(valid) == 1):
                    self.query_one(Input).insert_text_at_cursor(valid[0][len(fname):])
                elif(len(valid) > 0):
                    looping = 1
                    i = len(fname)
                    while(looping):
                        cur_letter = valid[0][i]
                        for j in range(1,len(valid)):
                            if(valid[j][i] != cur_letter):
                                looping = 0
                                break
                        i+=1
                    self.query_one(Input).insert_text_at_cursor(valid[0][len(fname):i-1])
            else:
                pass
            self._in.focus()

app = PyTerm()
app.run()
#os.system("clear")

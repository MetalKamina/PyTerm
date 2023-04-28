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
from shell import shell

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

class SysInfo(Widget):
    cpu = reactive(parse_cpu())
    memory = reactive(parse_mem())
    uptime = reactive(parse_uptime()[0])
    cputime = reactive(parse_uptime()[1])

    retval = reactive("")

    def fetchinfo(self):
        self.cpu = parse_cpu()
        self.memory = parse_mem()
        self.uptime = parse_uptime()[0]
        self.cputime = parse_uptime()[1]

    def on_mount(self):
        self.set_interval(1.0,self.fetchinfo)

    def comp(self):
        self.retval = "System info:\n"
        self.retval+=str(self.cpu)+" MHz CPU\n"
        self.retval+=str(self.memory)+" KB in use\n"
        self.retval+="Uptime: "+str(self.uptime)+" s\n"
        self.retval+="CPU time: "+str(self.cputime)+" s\n"

    def render(self) -> str:
        self.comp()
        return self.retval

class FileTree(Widget):
    dtree = reactive(DirectoryTree(os.getcwd()))

    def compose(self) -> ComposeResult:
        yield self.dtree

    def update_tree(self):
       self.dtree = reactive(DirectoryTree(os.getcwd()))

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
    switcher2 = ContentSwitcher(initial="dtree")
    tree = Container(DirectoryTree(os.getcwd()),id="dtree")


    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.sysinfo
        with self.switcher2:
            yield self.tree
            #yield Static()
        yield self.prompt
        yield self._in

    def update_s(self):
        self.sysinfo.styles.border = (self.settings["border"],self.settings["theme"])
        self.prompt.styles.border = (self.settings["border"],self.settings["theme"])
        self._in.styles.border = (self.settings["border"],self.settings["theme"])
        self.switcher2.styles.border = (self.settings["border"],self.settings["theme"])

    def update_tree(self):
        self.query_one("#dtree > DirectoryTree").remove()
        self.query_one("#dtree").mount(DirectoryTree(os.getcwd()))

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
                Color.parse(event.value[6:])
                self.settings["theme"] = event.value[6:]
            except:
                self.prompt.to_return = "Error: color not found."
        elif(e_arr[0] == "border"):
            options = ["ascii","blank","dashed","double","heavy","hidden/none","hkey",
                "inner","outer","round","solid","tall","thick","vkey","wide"]
            if(e_arr[1] == ""):
               self.prompt.to_return = "Available borders styles: "+", ".join(options)+"."
            else:
                if(e_arr[1] in options):
                    self.settings["border"] = e_arr[1]
                else:
                    self.prompt.to_return = "Error: border style not found."
        elif(e_arr[0] == "export"):
            if(len(event.value) <= 7):
                self.prompt.to_return = "Error: please specify an output file."
            else:
                self.export_settings(event.value[7:])
                self.prompt.to_return = "Succesfully wrote settings to \""+event.value[7:]+"\"."
        # if(event.value[:2] == "ls"):
        #     self.cwd = os.getcwd()
        #     self.query_one(ContentSwitcher).current = "dtree"
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

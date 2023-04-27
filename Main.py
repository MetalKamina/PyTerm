from textual.app import App, ComposeResult, Binding
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, TextLog, Input, Label, DirectoryTree, ContentSwitcher
from textual.widget import Widget
from textual import events
from textual.reactive import reactive

import os
from shell import shell

def shell_parse(input):
    if(input == "deadbeef"):
        return "Thanks!"
    elif(input[:2] == "ls"):
        return shell(input)
    else:
        return shell(input)

class Prompt(Widget):
    _input = reactive("")
    to_return = reactive("asdf",layout=False) 

    def render(self) -> str:
        self.to_return = shell_parse(self._input)
        return self.to_return

class SysInfo(Widget):
    cpu = reactive(1.0)

    def fetchinfo(self):
        self.cpu+=1.0

    def compose(self):
        retval = ""
        retval+=str(self.cpu)+" gHz\n"

        return "hihihi"

    def render(self) -> str:
        self.fetchinfo()
        return str(self.compose())

class PyTerm(App):
    CSS_PATH="styles.css"
    current = reactive("hello")
    cwd = reactive(os.getcwd())
    _in = Input()
    sysinfo = SysInfo()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield self.sysinfo
        with ContentSwitcher(initial="prompt"):
            yield Prompt(id="prompt")
            yield DirectoryTree(path=self.cwd,id="dtree")
        yield self._in

    def on_input_submitted(self,event:Input.Submitted) -> None:
        if(event.value == ":q" or event.value == "exit"):
                self.exit()
        # if(event.value[:2] == "ls"):
        #     self.cwd = os.getcwd()
        #     self.query_one(ContentSwitcher).current = "dtree"
        else:
            self.query_one(ContentSwitcher).current = "prompt"
            self.query_one(Prompt)._input = event.value
        event.input.action_delete_left_all()

    def on_mount(self):
        self._in.focus()

app = PyTerm()
app.run()
#os.system("clear")

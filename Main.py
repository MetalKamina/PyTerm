from textual.app import App, ComposeResult
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
    
class PyTerm(App):
    CSS_PATH="styles.css"
    current = reactive("hello")
    in_w = Input()
    cwd = reactive(os.getcwd())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with ContentSwitcher(initial="prompt"):
            yield Prompt(id="prompt")
            yield DirectoryTree(self.cwd,id="dtree")
        yield Input()

    def on_input_submitted(self,event:Input.Submitted) -> None:
        if(event.value == ":q"):
                self.exit()
        if(event.value[:2] == "ls"):
            self.cwd = os.getcwd()
            self.query_one(ContentSwitcher).current = "dtree"
        else:
            self.query_one(ContentSwitcher).current = "prompt"
        event.input.action_delete_left_all()
        self.query_one(Prompt)._input = event.value
    #def on_key(self, event: events.Key) -> None:
    #    self.query_one(TextLog).write(event)

app = PyTerm()
app.run()
#os.system("clear")

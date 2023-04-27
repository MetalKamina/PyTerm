from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, TextLog, Input, Label
from textual.widget import Widget
from textual import events
from textual.reactive import reactive

def shell(input):
    if(input == "deadbeef"):
        return "Thanks!"
    else:
        return "Please input the word deadbeef:"

class Prompt(Widget):
    _input = reactive("")
    to_return = reactive("asdf",layout=False) 

    def render(self) -> str:
        self.to_return = shell(self._input)
        return self.to_return
    
class PyTerm(App):
    CSS_PATH="styles.css"
    current = reactive("hello")
    in_w = Input()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield Prompt()
        yield self.in_w

    def on_input_submitted(self,event:Input.Submitted) -> None:
        event.input.action_delete_left_all()
        self.query_one(Prompt)._input = event.value
    #def on_key(self, event: events.Key) -> None:
    #    self.query_one(TextLog).write(event)

app = PyTerm()
app.run()
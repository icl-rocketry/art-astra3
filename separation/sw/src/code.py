from typing import Optional
from statemachine import diagnostic, state

curr_state: Optional[state] = diagnostic()
while curr_state is not None:
    curr_state = curr_state.run()
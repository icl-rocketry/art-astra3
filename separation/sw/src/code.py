from statemachine import diagnostic, state

curr_state: state | None = diagnostic()
while curr_state is not None:
    curr_state = curr_state.run()
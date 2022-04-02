from statemachine import diagnostic

state = diagnostic()
while state is not None:
    state = state.run()
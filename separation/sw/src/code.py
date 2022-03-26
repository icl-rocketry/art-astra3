from statemachine import diagnostic, flight, preflight

state = diagnostic()
while state is not None:
    state = state.run()
from talon import app, actions

def on_ready():
    actions.user.send_gaze_point()

app.register("ready", on_ready)

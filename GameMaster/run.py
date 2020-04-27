from app import app, deviceServer
if __name__ == "__main__":
    deviceServer.runThreaded()
    app.run()
from app import app, deviceServer
CK_DEVICE_SERVER = 'DEVICE_SERVER'
if __name__ == "__main__":
    deviceServer.runThreaded()
    app.config[CK_DEVICE_SERVER] = deviceServer
    app.run()
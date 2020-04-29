from app import app, deviceServer
if __name__ == "__main__":
    deviceServer.runThreaded()
    app.config['DEVICE_LIST'] = deviceServer.detectedDevices 
    app.run()
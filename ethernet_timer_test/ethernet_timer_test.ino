#include <SPI.h>
#include <Ethernet.h>
#include <ctype.h>

// MAC address from Ethernet shield sticker under board
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xBA, 0x00 };
char MODEL_ARDUINO[] = "\"arduino\"";
char ROOM_ID[] = "\"ARDUINO ROOM #1\"";
IPAddress ip(192,168,0,177); // IP address, may need to change depending on network
EthernetServer server(8080);  // create a server at port 8080
unsigned long secondsLeft = 3600;
unsigned long lastTick = 0;
boolean countDown = false;
void timer_status();

void setup()
{
   Ethernet.begin(mac, ip);  // initialize Ethernet device
   server.begin();           // start to listen for clients
   Serial.begin(9600);       // for diagnostics
   Serial.println(Ethernet.localIP());
}
void loop(void) 
{
  if(countDown)
  {
    unsigned long lastTickDiff = millis()-lastTick;
    if(lastTickDiff >= 1000)
    {
      lastTick = millis();
      secondsLeft = secondsLeft - 1;
    }
  }
  EthernetClient client = server.available();
  if (client) 
  {
    Serial.println("New connection:");
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) 
    {
      if (client.available()) 
      {
        client.readStringUntil('/'); // get rid of everything before http request
        String url = "";
        char c = client.read();
        while(c != '?' && !isspace(c))
        {
          url += c;
          c = client.read();
        }
        Serial.println(url);
        if(url == "timer/status")
        {
          client.println("HTTP/1.1 200 OK"); // send a standard http response header
          client.println("Access-Control-Allow-Origin: *"); // send CORS
          client.println("");
          client.print("[");client.print(secondsLeft);client.print(",");client.print(countDown?"true":"false");client.print("]");
        }
        else if(url == "timer/resume")
        {
          lastTick = millis();
          countDown = true;
          client.println("HTTP/1.1 200 OK"); // send a standard http response header
          client.println("Access-Control-Allow-Origin: *"); // send CORS
          client.println("");
          client.print("[");client.print(secondsLeft);client.print(",");client.print(countDown?"true":"false");client.print("]");
        }
        else if(url == "timer/pause")
        {
          countDown = false;
          client.println("HTTP/1.1 200 OK"); // send a standard http response header
          client.println("Access-Control-Allow-Origin: *"); // send CORS
          client.println("");
          client.print("[");client.print(secondsLeft);client.print(",");client.print(countDown?"true":"false");client.print("]");
        }
        else if(url == "who")
        {
          client.println("HTTP/1.1 200 OK"); // send a standard http response header
          client.println("Access-Control-Allow-Origin: *"); // send CORS
          client.println("");
          client.print("[");client.print(MODEL_ARDUINO);client.print(",[");client.print("\"timer\"],");client.print(ROOM_ID);client.print("]");
        }
        break;
      }
    }
    // give the web browser time to receive the data
    delay(1);
    // close the connection:
    client.stop();
    Serial.println("client disonnected");
  }
}


void timer_status(EthernetClient& client)
{
  client.print("[");client.print(millis());client.print(", true]");
}

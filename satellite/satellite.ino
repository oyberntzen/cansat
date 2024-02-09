#include <Arduino_MKRENV.h>
#include "libraries/radio.cpp"

int counter = 0;
int session_id = 0;
Packet packet;

void setup() {
    Serial.begin(9600);
    //while (!Serial);

    randomSeed(analogRead(0));
    session_id = random(1<<31);

    if (!ENV.begin()) {
        Serial.println("Failed to initialize MKR ENV shield!");
        while (1);
    }

    radio::init();

}

void loop() {
    Serial.print("Sending packet: ");
    Serial.println(counter);

    float temperature = ENV.readTemperature();
    float humidity = ENV.readHumidity();
    float pressure = ENV.readPressure();
    float light = ENV.readIlluminance();

    packet.has_header = true;
    packet.header.index = counter;
    packet.header.time = millis();
    packet.header.session_id = session_id;

    packet.has_telemetry = true;
    packet.telemetry.has_env = true;
    packet.telemetry.env.temperature = temperature;
    packet.telemetry.env.humidity = humidity;
    packet.telemetry.env.pressure = pressure;
    packet.telemetry.env.light = light;
    
    radio::encode(packet);
    radio::send();

    // send packet
    /*
    LoRa.beginPacket();
    LoRa.print("SI temperatur: ");
    LoRa.print(temperature);
    LoRa.endPacket();*/

    counter++;

    delay(1000);
}

#include "libraries/radio.cpp"

Packet packet;

void setup() {
    Serial.begin(9600);

    while (!Serial);

    radio::init();
}

void loop() {
    radio::recieve();
    packet = radio::decode();
    // TODO: check if valid packet
    radio::sendSerial();

    /*Serial.print("Temperature: ");
    Serial.println(packet.telemetry.env.temperature);
    Serial.print("Humidity: ");
    Serial.println(packet.telemetry.env.humidity);
    Serial.print("Pressure: ");
    Serial.println(packet.telemetry.env.pressure);
    Serial.print("Light: ");
    Serial.println(packet.telemetry.env.light);
    Serial.println();*/
}

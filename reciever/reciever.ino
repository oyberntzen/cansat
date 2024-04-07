//#define DEBUG
#include "libraries/radio.cpp"


Packet packet;

void setup() {
    Serial.begin(9600);

    while (!Serial);

    radio::init(false);
}

void loop() {
    radio::recieve();
    packet = radio::decode();

    if (!radio::decoded) {
        return;
    }

    packet.telemetry.has_radio = true;
    packet.telemetry.radio.RSSI = radio::RSSI();
    packet.telemetry.radio.SNR = radio::SNR();

    radio::encode(packet);
    radio::sendSerial();
}

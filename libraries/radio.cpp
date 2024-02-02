#include <pb_common.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include "packet.pb.c"
#include "Arduino.h"
#include <LoRa.h>
#include <SPI.h>

namespace radio {
    uint8_t packet_id[] = {1, 2, 3};
    const uint8_t packet_id_size = sizeof(packet_id);
    uint8_t buffer[Packet_size + sizeof(packet_id)];
    uint8_t buffer_size = 0;

    void init() {
        if (!LoRa.begin(868E6)) {
            Serial.println("Starting LoRa failed!");
            while (1);
        }
    }

    void printBuffer() {
        for (int i = 0; i < buffer_size; i++) {
            Serial.print(buffer[i]);
            Serial.print(" ");
        }
        Serial.println();
    }

    void encode(Packet packet) {
        memcpy(buffer, packet_id, packet_id_size);
        pb_ostream_t stream = pb_ostream_from_buffer(buffer+packet_id_size, Packet_size);
        pb_encode(&stream, Packet_fields, &packet);
        buffer_size = stream.bytes_written + packet_id_size;
    }

    Packet decode() {
        Packet packet = Packet_init_zero;
        pb_istream_t stream = pb_istream_from_buffer(buffer+packet_id_size, buffer_size-packet_id_size);
        bool status = pb_decode(&stream, Packet_fields, &packet);

        if (!status) {
            Serial.println("Failed to parse packet");
            return Packet_init_zero;
        }

        return packet;
    }

    void send() {
        if (LoRa.beginPacket() == 0) {
            Serial.println("beginPacket failed");
        }
        LoRa.write(buffer, buffer_size);
        if (LoRa.endPacket() == 0) {
            Serial.println("endPacket failed");
        }
    }

    void recieve() {
        buffer_size = 0;
        while (buffer_size == 0) {
            buffer_size = LoRa.parsePacket();
            //Serial.println(packet_size);
        }

        if (buffer_size > packet_id_size + Packet_size) {
            for (int i = 0; i < buffer_size; i++) {
                LoRa.read();
            }
        }

        //int packet_size = LoRa.parsePacket();
        for (int i = 0; i < buffer_size; i++) {
            buffer[i] = LoRa.read();
        }
        
        if (memcmp(buffer, packet_id, packet_id_size) != 0) {
            Serial.println("Wrong packet id");
            recieve();
        }
    }

    void sendSerial() {
        Serial.write(buffer_size - packet_id_size);
        for (int i = 0; i < buffer_size-packet_id_size; i++) {
            Serial.write(buffer[i + packet_id_size]);
        }
    }
}


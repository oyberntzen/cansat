#include <pb_common.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include "packet.pb.c"
#include "Arduino.h"
#include <LoRa.h>
#include <SPI.h>

#ifdef DEBUG
#define PRINT(content) Serial.println(content)
#define PRINT_INLINE(content) Serial.print(content)
#else
#define PRINT(content)
#define PRINT_INLINE(content)
#endif

namespace radio {
    uint8_t packet_id[] = {'I', 'N', 'V'};
    const uint8_t packet_id_size = sizeof(packet_id);
    uint8_t buffer[Packet_size + sizeof(packet_id)];
    uint8_t buffer_size = 0;
    bool packet_sent = true;

    void onPacketSent() {
        packet_sent = true;
        PRINT("Packet sent");
    }

    void init() {
        if (!LoRa.begin(868E6)) {
            PRINT("Failed to initialize radio!");
            while (1);
        }

        LoRa.setSpreadingFactor(11);
        LoRa.setSignalBandwidth(125e3);

        LoRa.onTxDone(onPacketSent);

        PRINT("Radio initialized");
    }

    void printBuffer() {
        for (int i = 0; i < buffer_size; i++) {
            PRINT_INLINE(buffer[i]);
            PRINT_INLINE(" ");
        }
        PRINT();
    }

    uint64_t random2() {
        uint64_t num = 0;
        for (int i = 0; i < 8; i++) {
            num |= uint64_t(LoRa.random()) << i*8;
            delay(100);
        }
        return num;
    }

    void encode(Packet packet) {
        memcpy(buffer, packet_id, packet_id_size);
        pb_ostream_t stream = pb_ostream_from_buffer(buffer+packet_id_size, Packet_size);
        pb_encode(&stream, Packet_fields, &packet);
        buffer_size = stream.bytes_written + packet_id_size;
    }

    Packet decode() {
        Packet packet;
        pb_istream_t stream = pb_istream_from_buffer(buffer+packet_id_size, buffer_size-packet_id_size);
        bool status = pb_decode(&stream, Packet_fields, &packet);

        if (!status) {
            PRINT("Failed to parse packet");
            return Packet_init_zero;
        }

        return packet;
    }

    void send() {
        if (packet_sent) {
            if (LoRa.beginPacket() == 0) {
                PRINT("beginPacket failed");
            }
            LoRa.write(buffer, buffer_size);
            if (LoRa.endPacket(true) == 0) {
                PRINT("endPacket failed");
            }
            packet_sent = false;
            PRINT("Sending packet");
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
            //Serial.println("Wrong packet id");
            recieve();
        }
    }

    void sendSerial() {
        Serial.write(buffer_size - packet_id_size);
        for (int i = 0; i < buffer_size-packet_id_size; i++) {
            Serial.write(buffer[i + packet_id_size]);
        }
    }

    void saveToFile(File file) {
        file.write(buffer_size - packet_id_size);
        file.write(buffer+packet_id_size, buffer_size-packet_id_size);
    }
}


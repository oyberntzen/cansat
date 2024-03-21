#include <Arduino_MKRENV.h>
#include <Arduino_MKRGPS.h>
#include <BMI160Gen.h>
#include <SD.h>

#include <math.h>

#define DEBUG
#include "libraries/radio.cpp"

int counter = 0;
uint64_t session_id = 0;
Packet packet;

int accelerometerRange = 8;
int gyroRange = 250;
float convertBMIData(int16_t data, int max) {
    return (data * max) / 32768.0;
}

File file;

void setup() {
    Serial.begin(9600);
    while (!Serial);

    if (!ENV.begin()) {
        PRINT("Failed to initialize MKR ENV shield!");
        while (1);
    }
    PRINT("MKR ENV shield initialized");

    if (!GPS.begin()) {
        PRINT("Failed to initialize MKR GPS shield!");
        while (1);
    }
    PRINT("MKR GPS shield initialized");

    if (!BMI160.begin(BMI160GenClass::I2C_MODE, 0x69)) {
        PRINT("Failed to initialize BMI160!");
        while (1);
    }
    BMI160.setAccelerometerRange(accelerometerRange);
    BMI160.setGyroRange(gyroRange);
    PRINT("BMI160 initialized");

    if (!SD.begin(4)) {
        PRINT("Failed to initialize SD card!");
        while (1);
    }
    PRINT("SD card initialized");

    radio::init();

    PRINT("Waiting for GPS");
    //while (!GPS.available()) {}

    session_id = GPS.getTime();
    PRINT_INLINE("Session ID: ");
    PRINT(session_id);

    char filename[32];
    sprintf(filename, "%llu.txt", session_id);
    file = SD.open(filename, FILE_WRITE);
}

void loop() {
    PRINT_INLINE("\nSending packet: ");
    PRINT(counter);

    packet.has_header = true;
    packet.header.index = counter;
    packet.header.time = millis();
    packet.header.session_id = session_id;

    packet.has_telemetry = true;

    float temperature = ENV.readTemperature();
    float humidity = ENV.readHumidity();
    float pressure = ENV.readPressure();
    float light = ENV.readIlluminance();

    PRINT("ENV data");
    PRINT_INLINE("Temperature: ");
    PRINT(temperature);
    PRINT_INLINE("Humidity: ");
    PRINT(humidity);
    PRINT_INLINE("Pressure: ");
    PRINT(pressure);
    PRINT_INLINE("Light: ");
    PRINT(light);

    packet.telemetry.has_env = true;
    packet.telemetry.env.temperature = temperature;
    packet.telemetry.env.humidity = humidity;
    packet.telemetry.env.pressure = pressure;
    packet.telemetry.env.light = light;

    if (GPS.available()) {
        float latitude = GPS.latitude();
        float longitude = GPS.longitude();
        float altitude = GPS.altitude();
        float speed = GPS.speed();
        int satellites = GPS.satellites();
        uint64_t epoch_time = GPS.getTime();

        PRINT("GPS data");
        PRINT_INLINE("Latitude: ");
        PRINT(latitude);
        PRINT_INLINE("Longitude: ");
        PRINT(longitude);
        PRINT_INLINE("Altitude: ");
        PRINT(altitude);
        PRINT_INLINE("Speed: ");
        PRINT(speed);
        PRINT_INLINE("Satellites: ");
        PRINT(satellites);
        PRINT_INLINE("Epoch time: ");
        PRINT(epoch_time);

        packet.telemetry.has_gps = true;
        packet.telemetry.gps.latitude = latitude;
        packet.telemetry.gps.longitude = longitude;
        packet.telemetry.gps.altitude = altitude;
        packet.telemetry.gps.speed = speed;
        packet.telemetry.gps.satellites = satellites;
        packet.telemetry.gps.epoch_time = epoch_time;        
    }
    
    int16_t rawAccX, rawAccY, rawAccZ;
    BMI160.getAcceleration(&rawAccX, &rawAccY, &rawAccZ);
    float accX = convertBMIData(rawAccX, accelerometerRange);
    float accY = convertBMIData(rawAccY, accelerometerRange);
    float accZ = convertBMIData(rawAccZ, accelerometerRange);
    float accAbs = sqrt(accX*accX + accY*accY + accZ*accZ);

    int rawGyroX, rawGyroY, rawGyroZ;
    BMI160.readGyro(rawGyroX, rawGyroY, rawGyroY);
    float gyroX = convertBMIData(rawGyroX, gyroRange);
    float gyroY = convertBMIData(rawGyroY, gyroRange);
    float gyroZ = convertBMIData(rawGyroY, gyroRange);

    PRINT("BMI160 data");
    PRINT_INLINE("Accelerometer X: ");
    PRINT(accX);
    PRINT_INLINE("Accelerometer Y: ");
    PRINT(accY);
    PRINT_INLINE("Accelerometer Z: ");
    PRINT(accZ);
    PRINT_INLINE("Accelerometer abs: ");
    PRINT(accAbs);
    PRINT_INLINE("Gyroscope X: ");
    PRINT(gyroX);
    PRINT_INLINE("Gyroscope Y: ");
    PRINT(gyroY);
    PRINT_INLINE("Gyroscope Z: ");
    PRINT(gyroZ);

    packet.telemetry.has_bmi160 = true;
    packet.telemetry.bmi160.accX = accX;
    packet.telemetry.bmi160.accY = accY;
    packet.telemetry.bmi160.accZ = accZ;
    packet.telemetry.bmi160.gyroX = gyroX;
    packet.telemetry.bmi160.gyroY = gyroY;
    packet.telemetry.bmi160.gyroZ = gyroZ;
    
    radio::encode(packet);
    radio::saveToFile(file);
    radio::send();
    file.flush();

    counter++;

    delay(1000);
}

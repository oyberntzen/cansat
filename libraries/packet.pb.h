/* Automatically generated nanopb header */
/* Generated by nanopb-0.4.9-dev */

#ifndef PB_PACKET_PB_H_INCLUDED
#define PB_PACKET_PB_H_INCLUDED
#include <pb.h>

#if PB_PROTO_HEADER_VERSION != 40
#error Regenerate this file with the current version of nanopb generator.
#endif

/* Struct definitions */
typedef struct _Header {
    uint32_t index;
    uint64_t time;
    uint64_t session_id;
} Header;

typedef struct _Telemetry_ENV {
    float temperature;
    float humidity;
    float pressure;
    float light;
} Telemetry_ENV;

typedef struct _Telemetry_GPS {
    float latitude;
    float longitude;
    float altitude;
    float speed;
    uint32_t satellites;
    uint64_t epoch_time;
} Telemetry_GPS;

typedef struct _Telemetry_BMI160 {
    float accX;
    float accY;
    float accZ;
    float gyroX;
    float gyroY;
    float gyroZ;
} Telemetry_BMI160;

typedef struct _Telemetry_Radio {
    int32_t RSSI;
    float SNR;
} Telemetry_Radio;

typedef struct _Telemetry {
    bool has_env;
    Telemetry_ENV env;
    bool has_gps;
    Telemetry_GPS gps;
    bool has_bmi160;
    Telemetry_BMI160 bmi160;
    bool has_radio;
    Telemetry_Radio radio;
} Telemetry;

typedef struct _Packet {
    bool has_header;
    Header header;
    bool has_telemetry;
    Telemetry telemetry;
} Packet;


#ifdef __cplusplus
extern "C" {
#endif

/* Initializer values for message structs */
#define Packet_init_default                      {false, Header_init_default, false, Telemetry_init_default}
#define Header_init_default                      {0, 0, 0}
#define Telemetry_init_default                   {false, Telemetry_ENV_init_default, false, Telemetry_GPS_init_default, false, Telemetry_BMI160_init_default, false, Telemetry_Radio_init_default}
#define Telemetry_ENV_init_default               {0, 0, 0, 0}
#define Telemetry_GPS_init_default               {0, 0, 0, 0, 0, 0}
#define Telemetry_BMI160_init_default            {0, 0, 0, 0, 0, 0}
#define Telemetry_Radio_init_default             {0, 0}
#define Packet_init_zero                         {false, Header_init_zero, false, Telemetry_init_zero}
#define Header_init_zero                         {0, 0, 0}
#define Telemetry_init_zero                      {false, Telemetry_ENV_init_zero, false, Telemetry_GPS_init_zero, false, Telemetry_BMI160_init_zero, false, Telemetry_Radio_init_zero}
#define Telemetry_ENV_init_zero                  {0, 0, 0, 0}
#define Telemetry_GPS_init_zero                  {0, 0, 0, 0, 0, 0}
#define Telemetry_BMI160_init_zero               {0, 0, 0, 0, 0, 0}
#define Telemetry_Radio_init_zero                {0, 0}

/* Field tags (for use in manual encoding/decoding) */
#define Header_index_tag                         1
#define Header_time_tag                          2
#define Header_session_id_tag                    3
#define Telemetry_ENV_temperature_tag            1
#define Telemetry_ENV_humidity_tag               2
#define Telemetry_ENV_pressure_tag               3
#define Telemetry_ENV_light_tag                  4
#define Telemetry_GPS_latitude_tag               1
#define Telemetry_GPS_longitude_tag              2
#define Telemetry_GPS_altitude_tag               3
#define Telemetry_GPS_speed_tag                  4
#define Telemetry_GPS_satellites_tag             5
#define Telemetry_GPS_epoch_time_tag             6
#define Telemetry_BMI160_accX_tag                1
#define Telemetry_BMI160_accY_tag                2
#define Telemetry_BMI160_accZ_tag                3
#define Telemetry_BMI160_gyroX_tag               4
#define Telemetry_BMI160_gyroY_tag               5
#define Telemetry_BMI160_gyroZ_tag               6
#define Telemetry_Radio_RSSI_tag                 1
#define Telemetry_Radio_SNR_tag                  2
#define Telemetry_env_tag                        1
#define Telemetry_gps_tag                        2
#define Telemetry_bmi160_tag                     3
#define Telemetry_radio_tag                      4
#define Packet_header_tag                        1
#define Packet_telemetry_tag                     2

/* Struct field encoding specification for nanopb */
#define Packet_FIELDLIST(X, a) \
X(a, STATIC,   OPTIONAL, MESSAGE,  header,            1) \
X(a, STATIC,   OPTIONAL, MESSAGE,  telemetry,         2)
#define Packet_CALLBACK NULL
#define Packet_DEFAULT NULL
#define Packet_header_MSGTYPE Header
#define Packet_telemetry_MSGTYPE Telemetry

#define Header_FIELDLIST(X, a) \
X(a, STATIC,   SINGULAR, UINT32,   index,             1) \
X(a, STATIC,   SINGULAR, UINT64,   time,              2) \
X(a, STATIC,   SINGULAR, UINT64,   session_id,        3)
#define Header_CALLBACK NULL
#define Header_DEFAULT NULL

#define Telemetry_FIELDLIST(X, a) \
X(a, STATIC,   OPTIONAL, MESSAGE,  env,               1) \
X(a, STATIC,   OPTIONAL, MESSAGE,  gps,               2) \
X(a, STATIC,   OPTIONAL, MESSAGE,  bmi160,            3) \
X(a, STATIC,   OPTIONAL, MESSAGE,  radio,             4)
#define Telemetry_CALLBACK NULL
#define Telemetry_DEFAULT NULL
#define Telemetry_env_MSGTYPE Telemetry_ENV
#define Telemetry_gps_MSGTYPE Telemetry_GPS
#define Telemetry_bmi160_MSGTYPE Telemetry_BMI160
#define Telemetry_radio_MSGTYPE Telemetry_Radio

#define Telemetry_ENV_FIELDLIST(X, a) \
X(a, STATIC,   SINGULAR, FLOAT,    temperature,       1) \
X(a, STATIC,   SINGULAR, FLOAT,    humidity,          2) \
X(a, STATIC,   SINGULAR, FLOAT,    pressure,          3) \
X(a, STATIC,   SINGULAR, FLOAT,    light,             4)
#define Telemetry_ENV_CALLBACK NULL
#define Telemetry_ENV_DEFAULT NULL

#define Telemetry_GPS_FIELDLIST(X, a) \
X(a, STATIC,   SINGULAR, FLOAT,    latitude,          1) \
X(a, STATIC,   SINGULAR, FLOAT,    longitude,         2) \
X(a, STATIC,   SINGULAR, FLOAT,    altitude,          3) \
X(a, STATIC,   SINGULAR, FLOAT,    speed,             4) \
X(a, STATIC,   SINGULAR, UINT32,   satellites,        5) \
X(a, STATIC,   SINGULAR, UINT64,   epoch_time,        6)
#define Telemetry_GPS_CALLBACK NULL
#define Telemetry_GPS_DEFAULT NULL

#define Telemetry_BMI160_FIELDLIST(X, a) \
X(a, STATIC,   SINGULAR, FLOAT,    accX,              1) \
X(a, STATIC,   SINGULAR, FLOAT,    accY,              2) \
X(a, STATIC,   SINGULAR, FLOAT,    accZ,              3) \
X(a, STATIC,   SINGULAR, FLOAT,    gyroX,             4) \
X(a, STATIC,   SINGULAR, FLOAT,    gyroY,             5) \
X(a, STATIC,   SINGULAR, FLOAT,    gyroZ,             6)
#define Telemetry_BMI160_CALLBACK NULL
#define Telemetry_BMI160_DEFAULT NULL

#define Telemetry_Radio_FIELDLIST(X, a) \
X(a, STATIC,   SINGULAR, INT32,    RSSI,              1) \
X(a, STATIC,   SINGULAR, FLOAT,    SNR,               2)
#define Telemetry_Radio_CALLBACK NULL
#define Telemetry_Radio_DEFAULT NULL

extern const pb_msgdesc_t Packet_msg;
extern const pb_msgdesc_t Header_msg;
extern const pb_msgdesc_t Telemetry_msg;
extern const pb_msgdesc_t Telemetry_ENV_msg;
extern const pb_msgdesc_t Telemetry_GPS_msg;
extern const pb_msgdesc_t Telemetry_BMI160_msg;
extern const pb_msgdesc_t Telemetry_Radio_msg;

/* Defines for backwards compatibility with code written before nanopb-0.4.0 */
#define Packet_fields &Packet_msg
#define Header_fields &Header_msg
#define Telemetry_fields &Telemetry_msg
#define Telemetry_ENV_fields &Telemetry_ENV_msg
#define Telemetry_GPS_fields &Telemetry_GPS_msg
#define Telemetry_BMI160_fields &Telemetry_BMI160_msg
#define Telemetry_Radio_fields &Telemetry_Radio_msg

/* Maximum encoded size of messages (where known) */
#define Header_size                              28
#define PACKET_PB_H_MAX_SIZE                     Packet_size
#define Packet_size                              143
#define Telemetry_BMI160_size                    30
#define Telemetry_ENV_size                       20
#define Telemetry_GPS_size                       37
#define Telemetry_Radio_size                     16
#define Telemetry_size                           111

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif

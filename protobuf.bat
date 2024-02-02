protoc -I=protobuf --python_out=python protobuf/packet.proto
cd protobuf
python ../../nanopb-master/generator/nanopb_generator.py -D ../libraries packet.proto
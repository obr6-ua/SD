package main_package;

import java.util.Properties;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

public class productor {
	public static void main(String[] args) {
		//String servidoresBootstrap = "192.168.56.1:9092";
		String servidoresBootstrapMongo = "localhost:27017";
		String topic = "Topic1";

		Properties props = new Properties();
		props.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, servidoresBootstrapMongo);
		props.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		props.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

		KafkaProducer<String, String> productor = new KafkaProducer<>(props);
		try {
			productor.send(new ProducerRecord<>(topic, "Esto"));
			productor.send(new ProducerRecord<>(topic, "Es una"));
			productor.send(new ProducerRecord<>(topic, "Prueba"));
			productor.send(new ProducerRecord<>(topic, "Intento 1"));
		} finally {
			productor.flush();
			productor.close();
		}

	}
}

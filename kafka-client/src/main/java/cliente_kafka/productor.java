package cliente_kafka;

import java.util.Properties;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

public class productor {
	public static void main(String[] args) {
// TODO Auto-generated method stub
		String servidoresBootstrap = "192.168.56.1:9092";
		String topic = "practica2";
		Properties props = new Properties();
		props.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, servidoresBootstrap);
		props.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		props.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		
		KafkaProducer<String, String> productor = new KafkaProducer<>(props);
		try {
			productor.send(new ProducerRecord<String, String>(topic, "mensaje 1 desde java"));
			productor.send(new ProducerRecord<String, String>(topic, "mensaje 2 desde java"));
			productor.send(new ProducerRecord<String, String>(topic, "mensaje 3 desde java"));
		} finally {
			productor.flush();
			productor.close();
		}
	}
}
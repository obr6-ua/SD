package main_package;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

public class consumidor {
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		//String servidoresBootstrap = "192.168.56.1:9092";
		String servidoresBootstrap = "192.168.56.1:27017";
		String topic = "Topic1";
		String grupo = "grupo_9";
		Properties props = new Properties();
		props.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, servidoresBootstrap);
		props.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		props.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		props.setProperty(ConsumerConfig.GROUP_ID_CONFIG, grupo);
		props.setProperty(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "instancia1");
		props.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
		KafkaConsumer<String, String> consumidor = new KafkaConsumer<>(props);
		// consumidor.close();
		consumidor.subscribe(Collections.singleton(topic));
		try {

			while (true) {

				ConsumerRecords<String, String> mensajes = consumidor.poll(Duration.ofMillis(0));
				// System.out.println ("paso por aqui despues de consumir");
				// System.out.println (mensajes.count());
				for (ConsumerRecord<String, String> mensaje : mensajes) {
					System.out.println(mensaje.value());
				}
			}
			// System.out.println ("paso por aqui despues de intro");

		} finally {
			// scanner.close();
			consumidor.close();
			// System.out.println ("paso por aqui despues de cerrar el consumidor");
		}
	}
}

package cliente_kafka;

import java.util.Properties;
import java.time.Duration;
import java.util.ArrayList;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;

public class AD_Engine {
	public void main(String[] args) {
		String servidoresBootstrap = "192.168.56.1:9092";
		
		//AD_Engine modo CONSUMIDOR
		//topic = "productor_consumidor"
		String topic_DE = "drones_engine";
		String grupo = "Engine";
		Properties props_consumidor = new Properties();
		props_consumidor.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, servidoresBootstrap);
		props_consumidor.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		props_consumidor.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		props_consumidor.setProperty(ConsumerConfig.GROUP_ID_CONFIG, grupo);
		props_consumidor.setProperty(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "Engine");
		props_consumidor.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
		KafkaConsumer<String, String> consumidor = new KafkaConsumer<>(props_consumidor);
		
		MongoCollection<Document> coleccion = null;

		MongoClient mongoClient = MongoClients.create("mongodb://localhost:27017");
		ArrayList<Figura> mapa = new ArrayList<Figura>();

		MongoDatabase database = mongoClient.getDatabase("mongo");
		
		//Recepcion de la figura desde Mongo
		do {
			coleccion = database.getCollection("Figura");
		}while(coleccion.countDocuments() == 0);

		try {
			FindIterable<Document> documents = coleccion.find();
			for (Document doc : documents) {
				int id = doc.getInteger("id");
				int coordenadaX = doc.getInteger("coordenada_x");
				int coordenadaY = doc.getInteger("coordenada_y");

				Figura figura = new Figura(id, coordenadaX, coordenadaY);
				mapa.add(figura);
			}
		} catch (Exception e) {
			System.out.println("Error: " + e.toString());
		}
		mongoClient.close();
		
		//recibo mensajes de cada dron para incluirse
		ConsumerRecords<String, String> mensajes = consumidor.poll(Duration.ofMillis(400));
	}
}

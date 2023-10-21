package cliente_kafka;

import java.util.Properties;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.Node;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;

import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import org.xml.sax.InputSource;

class DatosDrones {
	private String idDron;
	private String coordenadaXDestino;
	private String coordenadaYDestino;

	public DatosDrones(String idDron, String coordenadaXDestino, String coordenadaYDestino) {
		this.idDron = idDron;
		this.coordenadaXDestino = coordenadaXDestino;
		this.coordenadaYDestino = coordenadaYDestino;
	}

	public String getId() {
		return idDron;
	}

	public String getX() {
		return coordenadaXDestino;
	}

	public String getY() {
		return coordenadaYDestino;
	}
}

class LeerXML {
	public static ArrayList<DatosDrones> leerXML(String nombreArchivo) {
		try {
			File archivo = new File(nombreArchivo);
			DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			Document doc = dBuilder.parse(archivo);

			doc.getDocumentElement().normalize();
			NodeList listaFiguras = doc.getElementsByTagName("FIGURA");

			ArrayList<DatosDrones> datosDronesList = new ArrayList<>();

			for (int i = 0; i < listaFiguras.getLength(); i++) {
				Element figuraElement = (Element) listaFiguras.item(i);

				String idDron = figuraElement.getElementsByTagName("ID_DRON").item(0).getTextContent();
				String coordenadaXDestino = figuraElement.getElementsByTagName("COORDENADA_X_DESTINO").item(0)
						.getTextContent();
				String coordenadaYDestino = figuraElement.getElementsByTagName("COORDENADA_Y_DESTINO").item(0)
						.getTextContent();

				DatosDrones datosDrones = new DatosDrones(idDron, coordenadaXDestino, coordenadaYDestino);
				datosDronesList.add(datosDrones);
			}

			return datosDronesList;
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
}

class RegistroDrones {
	private int token;

	RegistroDrones(int p_token) {
		token = p_token;
	}

	public int getToken() {
		return token;
	}
}

public class AD_Engine {
	public final int KMAXDRONES = 20;

	private String mapa[][];

	public String leeSocket(Socket p_sk, String p_Datos) {
		try {
			InputStream aux = p_sk.getInputStream();
			DataInputStream flujo = new DataInputStream(aux);
			p_Datos = new String();
			p_Datos = flujo.readUTF();
		} catch (Exception e) {
			System.out.println("Error: " + e.toString());
		}
		return p_Datos;
	}

	public void escribeSocket(Socket p_sk, String p_Datos) {
		try {
			OutputStream aux = p_sk.getOutputStream();
			DataOutputStream flujo = new DataOutputStream(aux);
			flujo.writeUTF(p_Datos);
		} catch (Exception e) {
			System.out.println("Error: " + e.toString());
		}
		return;
	}

	public boolean checkRegistry(int p_token, ArrayList<RegistroDrones> registro) {
		boolean ok = false;

		for (RegistroDrones dr : registro) {
			if (p_token == dr.getToken()) {
				ok = true;
				break;
			}
		}

		return ok;
	}

	public String matrixToStr(String[][] matriz) {
		StringBuilder sb = new StringBuilder();
		for (String[] fila : matriz) {
			for (String cell : fila) {
				sb.append(cell).append("\t");
			}
			sb.append("\n");
		}
		return sb.toString();
	}

	public String[][] strToMatrix(String strMatriz) {
		String[] filas = strMatriz.split("\n");
		String[][] mapa = new String[20][20];

		for (int i = 0; i < 20; i++) {
			String[] columnas = filas[i].split("\t");
			for (int j = 0; j < 20; j++) {
				mapa[i][j] = columnas[j];
			}
		}

		return mapa;
	}

	public void actualizarMapa(String[][] mapa, String mensaje) {
		// mensaje tipo: "id:S"
		String info[] = mensaje.split(":");
		char pos = info[1].charAt(0);

		for (int i = 0; i < 20; i++) {
			for (int j = 0; j < 20; j++) {
				if (mapa[i][j].contains(info[0])) {
					switch (pos) {
					case 'W':
						mapa[i - 1][j] = mapa[i][j];
						mapa[i][j] = "";
						break;
					case 'E':
						mapa[i + 1][j] = mapa[i][j];
						mapa[i][j] = "";
						break;
					case 'N':
						mapa[i][j + 1] = mapa[i][j];
						mapa[i][j] = "";
						break;
					case 'S':
						mapa[i + 1][j - 1] = mapa[i][j];
						mapa[i][j] = "";
						break;
					}
				}
			}
		}

	}

	public void main(String[] args) {
		String servidoresBootstrap = "192.168.56.1:9092";
		ArrayList<RegistroDrones> registro = new ArrayList<RegistroDrones>();
		int dronesRegistrados = 0;
		String mensajeSck = "";
		int maxId = 0;
//		InetAddress direccionIP = null;

		// AD_Engine modo CONSUMIDOR
		// topic = "productor_consumidor"
		String topic_consumidor = "drones_engine";
		String grupo = "Engine";
		Properties props_consumidor = new Properties();
		props_consumidor.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, servidoresBootstrap);
		props_consumidor.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		props_consumidor.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
				StringDeserializer.class.getName());
		props_consumidor.setProperty(ConsumerConfig.GROUP_ID_CONFIG, grupo);
		props_consumidor.setProperty(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "Engine");
		props_consumidor.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
		KafkaConsumer<String, String> consumidor = new KafkaConsumer<>(props_consumidor);
		consumidor.subscribe(Collections.singleton(topic_consumidor));

		// AD_Engine modo PRODUCTOR
		String topic_productor = "engine_drones";
		Properties props_productor = new Properties();
		props_productor.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, servidoresBootstrap);
		props_productor.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		props_productor.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		KafkaProducer<String, String> productor = new KafkaProducer<>(props_productor);

		// Nos conectamos a la BBDD para recibir la informacion guardada del registry
		MongoCollection<org.bson.Document> coleccion = null;
		MongoClient mongoClient = MongoClients.create("mongodb://localhost:27017");
		MongoDatabase database = mongoClient.getDatabase("mongo");

		// 1.LA FIGURA VIENE POR XML

		String nombreArchivo = "drones.xml";
		ArrayList<DatosDrones> datosDronesList = LeerXML.leerXML(nombreArchivo);

		// 2. Sacamos de BBDD información sobre {token} de cada dron y lo guardamos

		// Recepcion de tabla con la informacion de registro de todos los drones
		do {
			coleccion = database.getCollection("Registro");
		} while (coleccion.countDocuments() < KMAXDRONES); // Solo se pueden registrar 20 drones

		try {
			maxId = 0;
			FindIterable<org.bson.Document> documents = coleccion.find();
			for (org.bson.Document doc : documents) {
				int token = doc.getInteger("token");

				RegistroDrones dronDB = new RegistroDrones(token);
				registro.add(dronDB);
				maxId++;
			}
		} catch (Exception e) {
			System.out.println("Error: " + e.toString());
		}
		mongoClient.close();

		// 3. Recibimos {token} de cada dron y contrastamos con el registro de los
		// id-tokens

		try {
			ServerSocket skServidor = new ServerSocket(9999);
			int contador = 0;
			while (dronesRegistrados < maxId && dronesRegistrados < KMAXDRONES) {
				/*
				 * Se espera un cliente que quiera conectarse
				 */
				Socket skCliente = skServidor.accept(); // Crea objeto
				System.out.println("Sirviendo cliente...");

				mensajeSck = leeSocket(skCliente, mensajeSck);

				if (checkRegistry(Integer.parseInt(mensajeSck), registro)) {
					mensajeSck = datosDronesList.get(contador).getId() + "," + datosDronesList.get(contador).getX()
							+ "," + datosDronesList.get(contador).getY();
					escribeSocket(skCliente, mensajeSck);
					mapa[0][0] = datosDronesList.get(contador).getId() + "r";
					dronesRegistrados++;
					contador++;
				} else {
					mensajeSck = "-1";
				}

				skCliente.close();
			}
			skServidor.close();
			System.exit(0);
		} catch (Exception e) {
			System.out.println("Ha fallado el AD_Engine al comunicarse por socket con el dron");
		}

		// mando mapa por kafka

		String mapaStr = matrixToStr(mapa);
		try {
			ProducerRecord<String, String> mensaje = new ProducerRecord<>(topic_productor, mapaStr);
			productor.send(mensaje);
		} catch (Exception e) {
			System.out.println(e.toString());
		} finally {
			productor.close();
		}

		for (;;) {
			ConsumerRecords<String, String> mensajeC = consumidor.poll(Duration.ofMillis(0));
			for (ConsumerRecord<String, String> msj : mensajeC) {
				actualizarMapa(strToMatrix(mapaStr), msj.value());
				mapaStr = matrixToStr(mapa);
				ProducerRecord<String, String> mensajeP = new ProducerRecord<>(topic_productor, mapaStr);
				productor.send(mensajeP);
			}
		}
	}
}

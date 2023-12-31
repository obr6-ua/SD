package main_package;

import java.util.Properties;

import java.io.File;
import java.util.ArrayList;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.time.Duration;
import java.util.Collections;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;

import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;

class DatosDrones {
	private String idDron;
	private String coordenadaXDestino;
	private String coordenadaYDestino;

	public DatosDrones(String idDron, String coordenadaXDestino, String coordenadaYDestino) {
		this.idDron = idDron;
		this.coordenadaXDestino = coordenadaXDestino;
		this.coordenadaYDestino = coordenadaYDestino;
	}

	public DatosDrones() {
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
	
	public void setId(String p_id) {
		idDron = p_id;
	}
	
	public void setX(String p_x) {
		coordenadaXDestino = p_x;
	}
	
	public void setY(String p_y) {
		coordenadaYDestino = p_y;
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
	private static String puertoEscucha;
	private static int numDrones;
	private static String ipBootstrap;
	private static String puertoBootstrap;
	private static String ipWeather;
	private static String puertoWeather;
	private static String ipBBDD;
	private static String puertoBBDD;
	private static Properties props_consumidor;
	private static Properties props_productor;

	private static String mapa[][];

	public static String leeSocket(Socket p_sk, String p_Datos) {
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

	public static void escribeSocket(Socket p_sk, String p_Datos) {
		try {
			OutputStream aux = p_sk.getOutputStream();
			DataOutputStream flujo = new DataOutputStream(aux);
			flujo.writeUTF(p_Datos);
		} catch (Exception e) {
			System.out.println("Error: " + e.toString());
		}
		return;
	}

	public static boolean checkRegistry(int p_token, ArrayList<RegistroDrones> registro) {
		boolean ok = false;

		for (RegistroDrones dr : registro) {
			if (p_token == dr.getToken()) {
				ok = true;
				break;
			}
		}

		return ok;
	}

	public static String matrixToStr(String[][] matriz) {
		StringBuilder sb = new StringBuilder();
		for (String[] fila : matriz) {
			for (String cell : fila) {
				sb.append(cell).append("\t");
			}
			sb.append("\n");
		}
		return sb.toString();
	}

	public static String[][] strToMatrix(String strMatriz) {
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

	public static void actualizarMapa(String[][] mapa, String mensaje) {
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

	public static void configuraConsumidor(Properties p_consumidor, String p_ip, String grupo) {
		p_consumidor.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, p_ip);
		p_consumidor.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		p_consumidor.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		p_consumidor.setProperty(ConsumerConfig.GROUP_ID_CONFIG, grupo);
		p_consumidor.setProperty(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "Engine");
		p_consumidor.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
	}

	public static void configuraProductor(Properties p_productor, String p_ip) {
		p_productor.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, p_ip);
		p_productor.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		p_productor.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
	}

	public static boolean compruebaArgs(String[] args) {
		boolean check = true;
		if (args.length != 6) {
			System.out.println("Error: Se debe ejecutar el servidor de la siguiente forma:");
			System.out.println(
					"./AD_Engine <puerto_escucha> <numero_drones> <IP_server_gestor> <puerto_server_gestor> <IP_AD_Weather> <puerto_AD_Weather>");
			check = false;
		} else {
			puertoEscucha = args[0];
			numDrones = Integer.parseInt(args[1]);
			ipBootstrap = args[2];
			puertoBootstrap = args[3];
			ipWeather = args[4];
			puertoWeather = args[5];
			ipBBDD = args[6];
			puertoBBDD = args[7];
		}
		return check;
	}

	public static void printBanner() {
		System.out.println("*********** ART WITH DRONES ***********");
	}

	public static void printMap(String mapa[][]) {
		for (int i = 1; i <= 20; i++) {
			for (int j = 1; j <= 20; j++) {
				if (i == 1 || j == 1) {
					// Imprimir números de fila y columna en los bordes
					System.out.print(j + i - 1 + "   ");
				} else {
					// Interior del mapa
					System.out.println(mapa[i][j]);
				}
			}
			System.out.println("\n");
		}
	}

	public static void printState(String state) {
		if (state == "OK") {
			System.out.println("	   FIGURA COMPLETADA\n");
		} else if (state == "PROCESO") {
			System.out.println("	   FIGURA EN PROCESO\n");
		} else {
			System.out.println("CONDICIONES CLIMATICAS ADVERSAS ESPECTACULO FINALIZADO\n");
		}
	}
	
	public static void getDataJson(String jsonName, ArrayList<DatosDrones> datosDrones){
		DatosDrones dron = new DatosDrones();
		Gson gson = new Gson();
        JsonObject jsonObject = gson.fromJson(jsonName, JsonObject.class);
        
        JsonArray figurasArray = jsonObject.getAsJsonArray("figuras");
        
        for (int i = 0; i < figurasArray.size(); i++) {
            JsonObject figuraObject = figurasArray.get(i).getAsJsonObject();
            String nombreFigura = figuraObject.get("Nombre").getAsString();
            JsonArray dronesArray = figuraObject.getAsJsonArray("Drones");

            for (int j = 0; j < dronesArray.size(); j++) {
                JsonObject dronObject = dronesArray.get(j).getAsJsonObject();
                int idDron = dronObject.get("ID").getAsInt();
                String coordenadas = dronObject.get("POS").getAsString();

                // Aquí puedes crear objetos de DatosDrones y almacenar los datos
                dron.setId(String.valueOf(idDron));
                String[] coordenadasArray = coordenadas.split(",");
                dron.setX(coordenadasArray[0]);
                dron.setY(coordenadasArray[1]);
                datosDrones.add(dron);
            }
        }
	}

	public static void main(String[] args) {
		// String servidoresBootstrap = "192.168.56.1:9092";
		ArrayList<RegistroDrones> registro = new ArrayList<RegistroDrones>();
		int dronesRegistrados = 0, dronesOK = 0;
		String mensajeSck = "";
		String temperatura = "";
		String jsonName = "AwD_figuras.json";
		ArrayList<DatosDrones> datosDrones = new ArrayList<DatosDrones>();

		mapa = new String[20][20];

		if (!compruebaArgs(args)) {
			System.exit(-1);
		}

		// AD_Engine modo CONSUMIDOR
		// topic = "productor_consumidor"
		String topic_consumidor = "drones_engine";
		String grupo = "Engine";
		props_consumidor = new Properties();
		configuraConsumidor(props_consumidor, ipBootstrap, grupo);
		KafkaConsumer<String, String> consumidor = new KafkaConsumer<>(props_consumidor);
		consumidor.subscribe(Collections.singleton(topic_consumidor));

		// AD_Engine modo PRODUCTOR
		String topic_productor = "engine_drones";
		props_productor = new Properties();
		configuraProductor(props_productor, ipBootstrap);
		KafkaProducer<String, String> productor = new KafkaProducer<>(props_productor);

		// Nos conectamos a la BBDD para recibir la informacion guardada del registry
		String cadenaConexionBBDD = "mongodb://" + ipBBDD + ":" + puertoBBDD;
		MongoCollection<org.bson.Document> coleccion = null;
		MongoClient mongoClient = MongoClients.create(cadenaConexionBBDD); // "mongodb://localhost:27017"
		MongoDatabase database = mongoClient.getDatabase("mongo");

		while (true) {

			// 1.LA FIGURA VIENE POR JSON !!!!!!!!!!!!!!!!
			
			getDataJson(jsonName, datosDrones);

			String nombreArchivo = "drones.xml";
			ArrayList<DatosDrones> datosDronesList = LeerXML.leerXML(nombreArchivo);

			// 2. Sacamos de BBDD información sobre {token} de cada dron y lo guardamos

			// Recepcion de tabla con la informacion de registro de todos los drones
			do {
				coleccion = database.getCollection("Registro");
			} while (coleccion.countDocuments() < numDrones); // Hasta el numerio de drones introducido por parametro

			try {
				FindIterable<org.bson.Document> documents = coleccion.find();
				for (org.bson.Document doc : documents) {
					int token = doc.getInteger("token");

					RegistroDrones dronDB = new RegistroDrones(token);
					registro.add(dronDB);
				}
			} catch (Exception e) {
				System.out.println("Error: " + e.toString());
			}
			mongoClient.close();

			// 3. Recibimos {token} de cada dron del Registry y contrastamos con el registro
			// de los
			// id-tokens

			try {
				ServerSocket skServidor = new ServerSocket(9999);
				int contador = 0;
				while (dronesRegistrados < numDrones) {
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
				// System.exit(0);
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
				System.exit(-1);
			} finally {
				productor.close();
			}

			try {

				// Realizamos la peticion a AD_Weather

				try {
					Socket skCliente = new Socket(ipWeather, Integer.parseInt(puertoWeather));
					leeSocket(skCliente, temperatura);
				} catch (Exception e) {
					System.out.println(e.toString());
					System.exit(-1);
				}

				// Si las condiciones son adversas finalizamos el espectaculo
				if (Integer.parseInt(temperatura) >= 40 || Integer.parseInt(temperatura) <= -1) {
					printBanner();
					printState("-1");
					printMap(mapa);
					System.exit(-1);
				} else {
					ConsumerRecords<String, String> mensajeC = consumidor.poll(Duration.ofMillis(0));
					for (ConsumerRecord<String, String> msj : mensajeC) {
						if (dronesOK == numDrones) {
							printBanner();
							printState("OK");
							printMap(mapa);
							break;
						}
						if (msj.value() == "OK") {
							dronesOK++;
						}
						actualizarMapa(strToMatrix(mapaStr), msj.value());
						printBanner();
						printState("PROCESO");
						printMap(mapa);
						mapaStr = matrixToStr(mapa);
						ProducerRecord<String, String> mensajeP = new ProducerRecord<>(topic_productor, mapaStr);
						productor.send(mensajeP);
					}
				}
			} finally {
				consumidor.close();
			}

		}
	}
}

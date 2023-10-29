import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetResetStrategy;
import org.apache.kafka.common.serialization.StringDeserializer;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

import java.io.*;
import java.net.*;
import java.util.Scanner;

public class Drone {
    private int id;
    private int x;
    private int y;
    private String token;
    private boolean state;

    public Drone(int id) {
        this.id = id;
        this.x = 1;
        this.y = 1;
        this.state = false;
        this.token = null;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token){
        this.token = token;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getX() {
        return x;
    }

    public void setX(int x) {
        this.x = x;
    }

    public int getY() {
        return y;
    }

    public void setY(int y) {
        this.y = y;
    }

    public void setState(boolean state) {
        this.state = state;
    }

}

public class AD_Drone {
    public static void printMenu() {
        System.out.println("*************************************************************");
        System.out.println("*************************************************************");
        System.out.println("******** Menú principal: ********");
        System.out.println("********    1. Dar de alta");
        System.out.println("********    2. Editar perfil");
        System.out.println("********    3. Darse de baja");
        System.out.println("******** 4. Salir");
        System.out.println("*************************************************************");
        System.out.println("*************************************************************");
    }

    public static void printMenu2() {
        System.out.println("*************************************************************");
        System.out.println("*************************************************************");
        System.out.println("******** Menú: ********");
        System.out.println("********    1. Iniciar espectaculo");
        System.out.println("********    2. Volver al menu principal del dron");
        System.out.println("******** 3. Salir");
        System.out.println("*************************************************************");
        System.out.println("*************************************************************");
    }

    public static int getOpcion(Scanner scanner) {
        System.out.print("");
        System.out.print("Seleccione una opción: ");
        return scanner.nextInt();
    }

    public static String getAlias(Scanner scanner) {
        System.out.print("Introduce el alias del dron: ");
        return scanner.next();
    }

    public static void enviarAlias(PrintWriter out, String alias) {
        out.println(alias);
    }

    public static String respuestaServer(BufferedReader in) throws IOException {
        String response = in.readLine();
        System.out.println("Respuesta del servidor: " + response);

        return response;
    }

    public static void closeConnections(BufferedReader in, PrintWriter out, Socket socket) throws IOException {
        in.close();
        out.close();
        socket.close();
    }

    //Configuracion de consumidor
    private static KafkaConsumer<String, String> configurarKafkaConsumer(String bootstrapServers, String groupId, String topic) {
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        consumerProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, OffsetResetStrategy.EARLIEST.toString());

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);
        consumer.subscribe(Collections.singletonList(topic));

        return consumer;
    }

    private static Producer<String, String> configureKafkaProducer(String bootstrapServers) {
        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        return new KafkaProducer<>(producerProps);
    }

    public static String moveDron(int x , int y , Drone dron){
        if (x > dron.getX()){
            dron.setX(dron.getX()+1);
            return dron.getId() + ":W";
        }
        else if (x < dron.getX()){
            dron.setX(dron.getX()-1);
            return dron.getId() + ":E";
        }
        else{
            if (y > dron.getY() ){
                dron.setY(dron.getY()+1);
                return dron.getId() + ":N";
            
            }
            else if (y < dron.getY()){
                dron.setY(dron.getY()-1);
                return dron.getId() + ":S";
            }
            else{
                dron.setState(true);
                return "OK";
            }
        }
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

    public static void unirseAlEspectaculo(String kafkaIp , String kafkaPort , Drone dron , int x , int y){
        // Configuramos consumer
        KafkaConsumer<String, String> recibirDeEngine = configureKafkaConsumer(kafkaIp + ":" + kafkaPort, "groupDrones", "engine_drones");
        Producer<String, String> enviarAEngine = configureKafkaProducer(kafkaIp + ":" + kafkaPort);
        
        // Código para consumir y producir mensajes
        while (true) {
            ConsumerRecords<String, String> records = recibirDeEngine.poll(Duration.ofMillis(100));
            String mensaje = "";
            if(mensaje!="OK"){
                for (ConsumerRecord<String, String> record : records) {
                    // Procesar mensajes del topic de consumo
                    String [][] mapa = strToMatrix(mensaje);

                    // Enviar mensajes al motor "Engine"
                    mensaje = moveDron(x , y , dron);
                    enviarAEngine.send(new ProducerRecord<>("drones_engine", mensaje));
                }
            }
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Uso: java AD_Drone <ip_registry> <puerto_registry> <ip_engine> <puerto_engine> <ip_kafka> <puerto_kafka> ");
            return;
        }
        //Parametros de consola
        String registryIp = args[0] , engineIp = args[2] , kafkaIp = args[4];
        int registryPort = Integer.parseInt(args[1]), enginePort = Integer.parseInt(args[3]) , kafkaPort = Integer.parseInt(args[5]);

        //Variables auxiliares
        String token;
        boolean aux = true;

        try {
            
            //Registry
            Socket registrySocket = new Socket(registryIp, registryPort);
            BufferedReader inRegistry = new BufferedReader(new InputStreamReader(registrySocket.getInputStream()));
            PrintWriter outRegistry = new PrintWriter(registrySocket.getOutputStream(), true);

            //Engine
            Socket registryEngine = new Socket(engineIp, enginePort);
            BufferedReader inEngine = new BufferedReader(new InputStreamReader(registryEngine.getInputStream()));
            PrintWriter outEngine = new PrintWriter(registryEngine.getOutputStream(), true);

            
            //Entrada desde teclado
            Scanner scanner = new Scanner(System.in);

            while (aux) {
                printMenu();
                int opcion = getOpcion(scanner);

                switch (opcion) {
                    case 1:
                        // Dar de alta
                        String alias = getAlias(scanner);
                        outRegistry.println("alta:" + alias);

                        //Guardamos el token
                        token=respuestaServer(inRegistry);
                        break;
                    case 2:
                        // Editar perfil
                        // Implementa la lógica de editar el perfil aquí
                        break;
                    case 3:
                        // Darse de baja
                        // Implementa la lógica de darse de baja aquí
                        aux=false;
                        break;
                    case 4:
                        // Salir del programa
                        closeConnections(inRegistry, outRegistry, registrySocket);
                        return;
                    default:
                        System.out.println("Opción no válida");
                }
            }
            closeConnections(inRegistry, outRegistry, registrySocket);
            aux=true;
            
            while (aux) {
                printMenu2();
                int opcion = getOpcion(scanner);
                String response;
                switch (opcion) {
                    case 1:
                        out.println(token);
                        response=respuestaServer(inRegistry);
                        break;
                    case 2:
                        //Volver al anterior menu
                        break;
                    case 3:
                        // Salir del programa
                        closeConnections(inEngine, outEngine, registryEngine);
                        return;
                    default:
                        System.out.println("Opción no válida");
                }
                if(response != ""){
                    
                    String [] arrayStrings = response.split(":");
                    Drone dron = new Drone(Integer.parseInt(arrayStrings[0]));
                    dron.setToken(token);
                    unirseAlEspectaculo(kafkaIp , kafkaPort , dron , Integer.parseInt(arrayStrings[1]) , Integer.parseInt(arrayStrings[2]));
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

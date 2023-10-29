// import com.mongodb.client.MongoClient;
// import com.mongodb.client.MongoClients;
// import com.mongodb.client.MongoCollection;
// import com.mongodb.client.MongoDatabase;
// import org.bson.Document;
// import org.bson.types.ObjectId;

import java.util.UUID;
import java.awt.*;
import java.awt.datatransfer.*;
import java.io.*;
import java.net.*;

public class AD_Registry {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.out.println("Uso: java AD_Registry <ip_servidor> <puerto_cliente> <puerto_bbdd>");
            return;
        }

        

        String serverIp = args[0];
        int clientPort = Integer.parseInt(args[1]);
        int dbPort = Integer.parseInt(args[2]);

        // // // Conexión a la base de datos MongoDB
        // MongoClient mongoClient = MongoClients.create("mongodb://localhost:27017");
        // MongoDatabase database = mongoClient.getDatabase("drones_db");
        // MongoCollection<Document> dronesCollection = database.getCollection("drones");

        try {
            // Crea un servidor en el puerto de clientes
            ServerSocket serverSocket = new ServerSocket(clientPort);
            String text = "" + serverIp + " " + clientPort;

            // Copiamos en la clipboard
            Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
            StringSelection selection = new StringSelection(text);
            clipboard.setContents(selection, null);

            //Mensajes por consola
            System.out.println("***** Ip -> " + serverIp + ", Port -> " + clientPort + " *****");
            System.out.println("");
            System.out.println("");
            System.out.println("*************************************************************");
            System.out.println("********* IP y PUERTO  COPIADOS EN EL PORTAPAPELES **********");
            System.out.println("*************************************************************");
            System.out.println("");
            System.out.println("");
            System.out.println("*************************************************************");
            System.out.println("***************     Esperando conexiones...   ***************");
            System.out.println("*************************************************************");

            
            while (true) {
                // Espera a que un cliente se conecte
                Socket clientSocket = serverSocket.accept();
                System.out.println("Dron conectado desde: " + clientSocket.getInetAddress());

                // Flujo de entrada desde el cliente
                BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

                // Flujo de salida hacia el cliente
                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

                // Lee mensajes del cliente y los envía de vuelta
                String message;
                message = in.readLine();
                String[] array = message.split(":");
                switch (array[0]) {
                    case "alta":
                        String token = altaDron(dronesCollection , Integer.parseInt(array[1]));
                        out.println("Dron dado de alta con id: " + token);
                        break;
                    case "editar":
                        boolean edited = editarDron(dronesCollection, Integer.parseInt(array[1]), array[2]);
                        if (edited) {
                            out.println("Dron editado correctamente");
                        } else {
                            out.println("No se pudo editar el dron");
                        }
                    break;
                        break;
                    case "baja":
                        // Baja de dron
                        boolean deleted = bajaDron(dronesCollection, Integer.parseInt(array[1]));
                        if (deleted) {
                            out.println("Dron eliminado correctamente");
                        } else {
                            out.println("No se pudo eliminar el dron");
                        }
                        break;
                    case "iniciar":
                        
                        break;
                    default:
                        clientSocket.close();
                        break;
                }

                System.out.println("Fin conexion\n\n");
                clientSocket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
            
        }
    }

    public static String generateRandomToken() {
        UUID uuid = UUID.randomUUID();
        return uuid.toString().replaceAll("-", "");
    }

    // Funciones para interactuar con MongoDB
    private static int altaDron(MongoCollection<Document> collection, String alias) {
        // Obtiene el último ID asignado y asigna el siguiente
        // Document doc = collection.find().sort(new Document("_id", -1)).first();
        // int lastId = doc == null ? 0 : doc.getInteger("_id");
        // int nextId = lastId + 1;
        // Document dron = new Document("_id", nextId);
        // dron.append("alias", alias); // Agrega el alias al documento
        // collection.insertOne(dron);
        String randomToken = generateRandomToken();

        return generateRandomToken;
    }

    private static boolean editarDron(MongoCollection<Document> collection, int id, String alias) {
        // try {
        //     Document filter = new Document("_id", id);
        //     Document update = new Document("$set", new Document("alias", alias));

        //     collection.updateOne(filter, update);
    
        //     return true;
        // } catch (Exception e) {
        //     e.printStackTrace();
        //     return false; 
        // }
        return true;
    }
    
    private static boolean bajaDron(MongoCollection<Document> collection, int id) {
        // try {

        //     Document filter = new Document("_id", id);

        //     collection.deleteOne(filter);
    
        //     return true; 
        // } catch (Exception e) {
        //     e.printStackTrace();
        //     return false; 
        // }
        return true;
    }

}

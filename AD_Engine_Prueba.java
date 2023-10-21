import java.net.*;
import java.io.*;

public class AD_Engine {
    private char[][] mapa = new char[20][20];
    public static void main(String[] args){
        String puertoEngine = "", ipGestor = "", puertoGestor = "", ipWeather = "", puertoWeather = "", numDrones = "";
        //String ruta = ""
        String nombreArchivo = "drones.txt";
        File fichero = new File(nombreArchivo);

        if(args.length != 4){
            System.out.println("Error: Se debe ejecutar el servidor de la siguiente forma:");
            System.out.println("./Engine <puerto_ecucha> <numero_drones> <IP_server_gestor> <puerto_server_gestor> <IP_AD_Weather> <puerto_AD_Weather>");
            System.exit(1);
        }

        try{
            puertoEngine = args[0];
            numDrones = args[1];
            ipGestor = args[2];
            puertoGestor = args[3];
            ipWeather = args[4];
            puertoWeather = args[5];

            ServerSocket skServidor = new ServerSocket(Integer.parseInt(puertoEngine));
            System.out.println("Escuchando en el puerto: " + puertoEngine);

            //Esperamos a que el fichero (BBDD) se escriba
            for(;;){
                if(fichero.exists() && fichero.length() > 0){
                    System.out.println("Se ha encontrado el fichero con la informacion de los drones.");

                    //Se conectan los drones y comprobamos el token mediante hilos
                    Socket skCliente = skServidor.accept();
                    System.out.println("Se ha conectado un dron.");
                    Thread hilo = new Hilo(skCliente);
                    hilo.start();
                }
            }
        }catch(Exception e){
            System.out.println("Error: " + e.toString());
            System.exit(1);
        }
    }
}
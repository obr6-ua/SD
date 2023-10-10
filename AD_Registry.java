import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

public class AD_Registry{
    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Uso: java Server <puerto>");
            System.exit(1);
        }

        int portNumber = Integer.parseInt(args[0]);

        try {
            // Crear un socket de servidor en el puerto especificado
            ServerSocket serverSocket = new ServerSocket(portNumber);
            System.out.println("El servidor está escuchando en el puerto " + portNumber);

            while (true) {
                // Esperar a que un cliente se conecte
                Socket clientSocket = serverSocket.accept();
                System.out.println("Cliente conectado desde " + clientSocket.getInetAddress());

                // Crear un lector de entrada para recibir datos del cliente
                

                BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

                // Crear un escritor de salida para enviar datos al cliente
                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

                // Leer el mensaje del cliente
                String mensajeCliente = in.readLine();
                System.out.println("Mensaje recibido del cliente: " + mensajeCliente);

                // Responder al cliente con "Hola"
                out.println("Hola");

                // Cerrar la conexión con el cliente
                clientSocket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
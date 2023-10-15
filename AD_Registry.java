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

            // Espera a que un cliente se conecte
            Socket clientSocket = serverSocket.accept();
            System.out.println("Dron conectado desde: " + clientSocket.getInetAddress());

            // Flujo de entrada desde el cliente
            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

            // Flujo de salida hacia el cliente
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

            // Lee mensajes del cliente y los envía de vuelta
            String message;
            while ((message = in.readLine()) != null) {
                if (message.equals("1")) {
                out.println("Dar de alta");
            } else if (message.equals("alta")) {
                // El cliente ha enviado la señal de "alta"
                String alias = in.readLine();
                // Realiza la lógica para dar de alta en la base de datos
                // Luego, responde al cliente con la confirmación
                out.println("Dron dado de alta: " + alias);
            } else {
                // Otros casos (2, 3, 4) pueden manejarse de manera similar
            }
            }

            // Cierra las conexiones
            in.close();
            out.close();
            clientSocket.close();
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

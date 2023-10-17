import java.io.*;
import java.net.*;
import java.util.Scanner;

public class AD_Drone {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Uso: java AD_Drone <ip_servidor> <puerto_servidor>");
            return;
        }

        String serverIp = args[0];
        int serverPort = Integer.parseInt(args[1]);

        try {
            // Conecta el cliente al servidor utilizando la IP y el puerto especificados
            Socket clientSocket = new Socket(serverIp, serverPort);

            // Flujo de entrada desde el servidor
            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

            // Flujo de salida hacia el servidor
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

            // Flujo de entrada desde el teclado
            Scanner scanner = new Scanner(System.in);

            while (true) {
                printMenu();
                int opcion = getOpcion(scanner);

                switch (opcion) {
                    case 1:
                            // Dar de alta
                            String alias = getAlias(scanner);
                            // Envía el alias y la señal de "dar de alta" al servidor
                            out.println("alta"); // Señal para dar de alta
                            out.println(alias);
                            respuestaServer(in);
                        break;
                    case 2:
                        // Editar perfil
                        // Implementa la lógica de editar el perfil aquí
                        break;
                    case 3:
                        // Darse de baja
                        // Implementa la lógica de darse de baja aquí
                        break;
                    case 4:
                        // Salir del programa
                        closeConnections(in, out, clientSocket);
                        return;
                    default:
                        System.out.println("Opción no válida");
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void printMenu() {
        System.out.println("*************************************************************");
        System.out.println("*************************************************************");
        System.out.println("******** Menú: ********");
        System.out.println("********    1. Dar de alta");
        System.out.println("********    2. Editar perfil");
        System.out.println("********    3. Darse de baja");
        System.out.println("******** 4. Salir");
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

    public static void respuestaServer(BufferedReader in) throws IOException {
        String response = in.readLine();
        System.out.println("Respuesta del servidor: " + response);
    }

    public static void closeConnections(BufferedReader in, PrintWriter out, Socket clientSocket) throws IOException {
        in.close();
        out.close();
        clientSocket.close();
    }
}

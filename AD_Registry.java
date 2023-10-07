import java.io.IOException;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.Scanner;

public class AD_Registry {
    private int puertoEscucha;
    private Map<String, DatosDron> registroDrones;

    public AD_Registry(int puertoEscucha) {
        this.puertoEscucha = puertoEscucha;
        this.registroDrones = new HashMap<>();
    }

    public String registrarDron(DatosDron datosDron) {
        String token = generarToken();
        registroDrones.put(token, datosDron);
        return token;
    }

    private String generarToken() {
        return UUID.randomUUID().toString();
    }

    public void iniciarServidor() {
        try (ServerSocket socketServidor = new ServerSocket(puertoEscucha)) {
            System.out.println("AD_Registry está escuchando en el puerto " + puertoEscucha + "...");
            while (true) {
                Socket socketCliente = socketServidor.accept();
                System.out.println("Conexión entrante desde " + socketCliente.getInetAddress());

                Scanner entrada = new Scanner(socketCliente.getInputStream());
                PrintWriter salida = new PrintWriter(socketCliente.getOutputStream(), true);

                String solicitud = entrada.nextLine();
                System.out.println("Solicitud recibida: " + solicitud);

                // Analizar la solicitud como JSON
                // Suponemos que la solicitud tiene el formato {"action": "register", "drone_info": {...}}
                // Debes adaptar este código de análisis según tu protocolo de comunicación real
                Map<String, Object> solicitudMapa = analizarJson(solicitud);

                if (solicitudMapa != null && solicitudMapa.containsKey("action") && solicitudMapa.containsKey("drone_info")) {
                    String accion = (String) solicitudMapa.get("action");
                    if ("register".equals(accion)) {
                        DatosDron datosDron = (DatosDron) solicitudMapa.get("drone_info");
                        String token = registrarDron(datosDron);

                        // Enviar el token de vuelta al dron
                        Map<String, Object> respuestaMapa = new HashMap<>();
                        respuestaMapa.put("estado", "éxito");
                        respuestaMapa.put("token", token);
                        String respuesta = convertirAJson(respuestaMapa);
                        salida.println(respuesta);
                    }
                }

                socketCliente.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Método auxiliar para analizar una cadena JSON en un mapa
    private Map<String, Object> analizarJson(String json) {
        // Puedes utilizar una biblioteca JSON como Jackson o Gson para un análisis más robusto
        // Este es un enfoque simplificado para fines de demostración
        // Adapta este código según el formato JSON que utilices
        try {
            return new ObjectMapper().readValue(json, new TypeReference<Map<String, Object>>() {});
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    // Método auxiliar para convertir un objeto a cadena JSON
    private String convertirAJson(Object obj) {
        // Puedes utilizar una biblioteca JSON como Jackson o Gson para una serialización más robusta
        // Este es un enfoque simplificado para fines de demostración
        // Adapta este código según el formato JSON que utilices
        try {
            return new ObjectMapper().writeValueAsString(obj);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
        return null;
    }

    public static void main(String[] args) {
        int puertoRegistro = 9000;
        AD_Registry adRegistry = new AD_Registry(puertoRegistro);
        adRegistry.iniciarServidor();
    }
}

// Define una clase para representar los datos de un dron
class DatosDron {
    private String id;
    private String alias;

    public DatosDron(String id, String alias) {
        this.id = id;
        this.alias = alias;
    }

    // Getters y setters para id y alias
}
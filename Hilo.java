import java.lang.Exception;
import java.net.Socket;
import java.io.*;

public class Hilo extends Thread {
    private Socket skCliente;
    //Coordenada destino del dron
    private int[] coordFin = new int[2];
    //Coordenada actual del dron
    private int[] coordActual = new int[2];
    private int id, token;

    public Hilo(Socket socket){
        skCliente = socket;
        coordFin[0] = 0;
        coordFin[1] = 0;
        coordActual[0] = 0;
        coordActual[1] = 0;
        id = -1;
        token = -1;
    }

    public String leeSck(Socket sck, String datos){
        try{
			InputStream is = sck.getInputStream();
			DataInputStream flujo = new DataInputStream(is);
			datos = new String();
			datos = flujo.readUTF();
		}catch (Exception e)
		{
			System.out.println("Error: " + e.toString());
		}
      return datos;
    }

    public void escribeSck(Socket sck, String datos){
		try
		{
			OutputStream os = sck.getOutputStream();
			DataOutputStream flujo= new DataOutputStream(os);
			flujo.writeUTF(datos);      
		}
		catch (Exception e)
		{
			System.out.println("Error: " + e.toString());
		}
		return;
	}

    public void setData(String[] aux){
        id = Integer.parseInt(aux[0]);
        coordFin[0] = Integer.parseInt(aux[1]);
        coordFin[1] = Integer.parseInt(aux[2]);
        token = Integer.parseInt(aux[3]);
    }

    public void run(){
        String cadena = "";

        try {
            cadena = leeSck(skCliente, cadena);

            //para string tipo: id,coordX,coordY,token
            String[] aux = cadena.split(",");
            setData(aux);

            if(token == -1){
                System.out.println("El dron no ha pasado el registro correctamente; desconectando...");
                System.exit(1);
            }

            //Recibir instrucciones de movimiento del Engine
        }
        catch (Exception e) {
          System.out.println("Error: " + e.toString());
        }
    }
}

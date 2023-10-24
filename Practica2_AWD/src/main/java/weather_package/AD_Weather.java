package weather_package;

import java.io.*;
import java.net.*;
import java.util.*;

public class AD_Weather {
	private String datos[];

	private boolean checkArgs(String args[]) {
		boolean ok = true;

		if (args.length != 1) {
			System.out.println("Error: Formato erroneo /n Formato correcto ./AD_Weather <puerto_escucha>");
		}

		return ok;
	}

	private void extraerDatos() {
		String nArchivo = "InfoClima";
		List<String> listaAux = new ArrayList<>(); // Lista auxiliar

		try {
			File fich = new File(nArchivo);

			// FileReader lee el archivo
			FileReader fileReader = new FileReader(fich);

			// BufferedReader lee líneas de texto
			BufferedReader bufferedReader = new BufferedReader(fileReader);

			String linea;

			while ((linea = bufferedReader.readLine()) != null) {
				String[] aux = linea.split(":");
				listaAux.add(aux[1]);
			}

			bufferedReader.close();
			fileReader.close();

			datos = listaAux.toArray(new String[0]);

		} catch (Exception e) {
			System.out.println("Error: " + e.toString());
			System.exit(-1);
		}
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

	public void main(String args[]) {
		if (!checkArgs(args)) {
			System.exit(-1);
		}

		this.extraerDatos();

		try {
			ServerSocket skServidor = new ServerSocket(Integer.parseInt(args[0]));

			int indice = 0;
			for (;;) { // Esperamos a la peticion de conexion del AD_Engine
				Socket skCliente = skServidor.accept();
				escribeSocket(skCliente, datos[indice]);
				indice++;
				skCliente.close();
			}
		} catch (Exception e) {
			System.out.println("Error: " + e.toString());
			System.exit(-1);
		}
	}
}

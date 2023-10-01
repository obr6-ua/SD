package cliente_kafka;

public class Dron {
	private int id;
	private int coordActualX;
	private int coordActualY;
	char estado;
	
	Dron(int p_id, int cx, int cy){
		id = p_id;
		coordActualX = cx;
		coordActualY = cy;
		estado = 'r';
	}
}

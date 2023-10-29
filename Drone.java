public class Drone {
    private int Id;
    private int x;
    private int y;
    private String token;
    private boolean state;

    public Drone(int id) {
        this.id = id;
        this.x = 1;
        this.y = 1;
        this.state = null;
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

    public boolean isState() {
        return state;
    }

    public void setState(boolean state) {
        this.state = state;
    }

}


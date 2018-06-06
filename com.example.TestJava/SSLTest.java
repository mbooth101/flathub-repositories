import java.io.IOException;
import java.net.URL;
import java.net.URLConnection;

public class SSLTest {

public static void main(String[] args) throws IOException{
	URL u = new URL("https://www.redhat.com/index.html");
	URLConnection c = u.openConnection();
	c.connect();	        
}

}

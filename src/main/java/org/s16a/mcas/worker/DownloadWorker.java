package org.s16a.mcas.worker;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.sql.Savepoint;

import org.s16a.mcas.Enqueuer;
import org.s16a.mcas.Hasher;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;

public class DownloadWorker {
	private static final String TASK_QUEUE_NAME = "download";

	public static void main(String[] argv) throws Exception {
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost("localhost");
		final Connection connection = factory.newConnection();
		final Channel channel = connection.createChannel();

		channel.queueDeclare(TASK_QUEUE_NAME, true, false, false, null);
		System.out.println(" [*] Waiting for messages. To exit press CTRL+C");

		channel.basicQos(1);

		final Consumer consumer = new DefaultConsumer(channel) {
			@Override
			public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
				String message = new String(body, "UTF-8");

				System.out.println(" [x] Received '" + message + "'");
				try {
					downloadAndUpdateModel(message);
				} finally {
					System.out.println(" [x] Done");
					channel.basicAck(envelope.getDeliveryTag(), false);					
				}
			}
		};
		channel.basicConsume(TASK_QUEUE_NAME, false, consumer);
	}

	private static void downloadAndUpdateModel(String message) {
		// open model
		Model model = ModelFactory.createDefaultModel();
		String modelFileName = Hasher.getCacheFilename(message); 
		File f = new File(modelFileName);
		
		if (f.exists()) {
			model.read(modelFileName);
		}
		
		String dataFileName = Hasher.getCacheFilename(message) + ".data";
		
		try {
			saveUrl(dataFileName, message);
		} catch (MalformedURLException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		try {
			Enqueuer.enqueueAfterDownload(model, message, modelFileName, dataFileName);
		} catch (Exception e) {
			e.printStackTrace();
		}
		
	}
	
	
	public static void saveUrl(final String filename, final String urlString)
	        throws MalformedURLException, IOException {
	    BufferedInputStream in = null;
	    FileOutputStream fout = null;
	    try {
	        in = new BufferedInputStream(new URL(urlString).openStream());
	        fout = new FileOutputStream(filename);

	        final byte data[] = new byte[1024];
	        int count;
	        while ((count = in.read(data, 0, 1024)) != -1) {
	            fout.write(data, 0, count);
	        }
	    } finally {
	        if (in != null) {
	            in.close();
	        }
	        if (fout != null) {
	            fout.close();
	        }
	    }
	}
}
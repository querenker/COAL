package org.s16a.mcas;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.vocabulary.DC;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.MessageProperties;

import org.s16a.mcas.worker.UpdateWorker;

public class Enqueuer {

	public static void enqueueAfterDownload(Model model, String url, String modelFileName, String dataFileName) throws Exception {

		// (1) check mime type, and what analyses should be made

		// for the mime type:
		// (2) check model, what was done already
		// (3) enqueue for the analyses

		Map<String, List<Property>> analyses = new HashMap<String, List<Property>>();
		analyses.put("image/jpeg", Arrays.asList(MCAS.mediainfo, MCAS.vcd));
		analyses.put("image/png", Arrays.asList(MCAS.mediainfo));
		analyses.put("text/plain", Arrays.asList(MCAS.ner));
		analyses.put("application/pdf", Arrays.asList(MCAS.pdfmetadataextraction, MCAS.pdftextextraction, MCAS.pdfimageextraction));//

		final Property mimeType = model.createProperty("http://www.semanticdesktop.org/ontologies/2007/01/19/nie/#mimeType");

		// (1)
		Statement s = model.getResource(url).getProperty(mimeType);
		String wantedMimeType = s.getString().split(";")[0];

		for (Property analysis : analyses.get(wantedMimeType)) {
			if (model.getResource(url).getProperty(analysis) == null) {
				System.out.println("enqueue for " + analysis.toString());

				String QUEUE_NAME = analysis.toString();
				ConnectionFactory factory = new ConnectionFactory();
				factory.setHost("localhost");
				Connection connection = factory.newConnection();
				Channel channel = connection.createChannel();
				channel.queueDeclare(QUEUE_NAME, true, false, false, null);
				String message = url;
				channel.basicPublish("", QUEUE_NAME, MessageProperties.PERSISTENT_TEXT_PLAIN, message.getBytes());
				System.out.println(" [x] Sent '" + message + "'");
				channel.close();
				connection.close();
			}

		}

	}

	public static void enqueueForMerge(String filename) throws Exception {
		String QUEUE_NAME = "update";
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost("localhost");
		Connection connection = factory.newConnection();
		Channel channel = connection.createChannel();
		channel.queueDeclare(QUEUE_NAME, true, false, false, null);
		String message = filename;
		channel.basicPublish("", QUEUE_NAME, MessageProperties.PERSISTENT_TEXT_PLAIN, message.getBytes());
		channel.close();
		connection.close();
	}
}

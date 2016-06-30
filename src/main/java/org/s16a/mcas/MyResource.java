package org.s16a.mcas;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.StringWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.*;
import java.util.concurrent.TimeoutException;

import javax.ws.rs.GET;
import javax.ws.rs.HeaderParam;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.MediaType;

import com.hp.hpl.jena.sparql.vocabulary.FOAF;
import com.hp.hpl.jena.vocabulary.RDF;
import org.apache.commons.validator.routines.UrlValidator;

import com.hp.hpl.jena.datatypes.RDFDatatype;
import com.hp.hpl.jena.graph.Node;
import com.hp.hpl.jena.rdf.model.AnonId;
import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.RDFVisitor;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.vocabulary.DC;
import com.hp.hpl.jena.vocabulary.DCTerms;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.MessageProperties;

/**
 * Root resource (exposed at "resource" path)
 */
@Path("resource")
public class MyResource {


	@GET
	@Produces({ "application/x-turtle" })
	public String getTurtle(@QueryParam("url") String resourceUrl, @HeaderParam("accept") String acceptParam) throws IOException, TimeoutException, MCASException {
		Model model = getModel(resourceUrl, acceptParam);
		StringWriter out = new StringWriter();
		model.write(out, "TURTLE");
		return out.toString();
	}

	@GET
	@Produces({ "application/x-n3", "application/x-ntriples" })
	public String getN3(@QueryParam("url") String resourceUrl, @HeaderParam("accept") String acceptParam) throws IOException, TimeoutException, MCASException {
		Model model = getModel(resourceUrl, acceptParam);
		StringWriter out = new StringWriter();
		model.write(out, "NT");
		return out.toString();
	}

	@GET
	@Produces(MediaType.TEXT_PLAIN)
	public String getIt(@QueryParam("url") String resourceUrl, @HeaderParam("accept") String acceptParam) throws IOException, TimeoutException, MCASException {
		Model model = getModel(resourceUrl, acceptParam);
		StringWriter out = new StringWriter();
		model.write(out, "TURTLE");
		return out.toString();
	}

	private Model getModel(String resourceUrl, String acceptParam) throws MalformedURLException, IOException, MCASException, TimeoutException {
		// (1) check url validity
		// (2) check return format
		// (3) create hash
		// (4) check file resource - if existing load model and return it
		// (5) check url header (size and format)
		// (6) create and store basic model
		// (7) enqueue for download
		// (7b) enqueue resource
		// (8) return model --> send accept

		// (1)
		UrlValidator urlValidator = new UrlValidator();
		if (!urlValidator.isValid(resourceUrl)) {
			throw new MCASException("URL is not valid");
		}

		// (2)
		System.out.println("accept: " + acceptParam);
		if (!checkAcceptParam(acceptParam)) {
			throw new MCASException("invalid accept header");
		}

		// (3)
		String filename = Hasher.getCacheFilename(resourceUrl);

		// (4)
		File f = new File(filename);
		if (f.exists()) {
			Model model = ModelFactory.createDefaultModel();
			model.read(filename);
			return model;
		}

		// (5)
		URL url = new URL(resourceUrl);
		URLConnection conn = url.openConnection();

		// get URLs headers
		Map<String, List<String>> map = conn.getHeaderFields();
		int MAX_CONTENT_LENGTH = 50000000; // ca. 50MB
		Set<String> VALID_CONTENT_TYPES = new HashSet<String>(Arrays.asList("image/jpeg", "image/png", "application/pdf"));

		// TODO: this is just an example to accept jpeg images only
		int contentLength = Integer.parseInt(map.get("Content-Length").get(0));
		String contentType = map.get("Content-Type").get(0).split(";")[0];

		System.out.println(contentType);

		if (contentLength > MAX_CONTENT_LENGTH) {
			throw new MCASException("content length exceeded");
		}
		if (!VALID_CONTENT_TYPES.contains(contentType)) {
			throw new MCASException("content type invalid");
		}

		// (6)
		Model model = createAndStoreBasicModel(url, filename, map);

		// (7)

		String QUEUE_NAME = "download";

		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost("localhost");
		Connection connection = factory.newConnection();
		Channel channel = connection.createChannel();
		channel.queueDeclare(QUEUE_NAME, true, false, false, null);
		String message = resourceUrl;
		channel.basicPublish("", QUEUE_NAME, MessageProperties.PERSISTENT_TEXT_PLAIN, message.getBytes());
		//System.out.println(" [x] Sent '" + message + "'");
		channel.close();
		connection.close();
		
		return model;
	}

	private Model createAndStoreBasicModel(URL url, String filename, Map<String, List<String>> map) throws IOException {
		Model model = ModelFactory.createDefaultModel();

		// TODO constant for server uri
		Resource serverResource = model.createResource("http://aragog.blblblu.de:8080/coal/resource?url=" + url.toString());

		final Property type = model.createProperty("http://xmlns.com/foaf/0.1/");
		final Property topic = model.createProperty("http://xmlns.com/foaf/0.1/");

		serverResource.addLiteral(RDF.type, FOAF.Document);
		serverResource.addProperty(topic, url.toString());
		serverResource.addLiteral(DCTerms.modified, Calendar.getInstance());

		Resource someResource = model.createResource(url.toString());

		int contentLength = Integer.parseInt(map.get("Content-Length").get(0));
		String contentType = map.get("Content-Type").get(0);

		String identifier = filename.substring(filename.lastIndexOf("/") + 1, filename.lastIndexOf("."));

		final Property fileSize = model.createProperty("http://www.semanticdesktop.org/ontologies/2007/03/22/nfo/#fileSize");
		final Property mimeType = model.createProperty("http://www.semanticdesktop.org/ontologies/2007/01/19/nie/#mimeType");
		
		someResource.addProperty(DC.identifier, identifier);
		someResource.addLiteral(mimeType, contentType);
		someResource.addLiteral(fileSize, contentLength);
		// TODO: put more info from Header into RDF
		
		FileWriter out = new FileWriter(filename);
		try {
			model.write(out, "TURTLE");
		} finally {
			try {
				out.close();
			} catch (IOException closeException) {
				// ignore
			}
		}

		return model;
	}

	private boolean checkAcceptParam(String acceptParam) {
		// TODO Auto-generated method stub
		return true;
	}
}